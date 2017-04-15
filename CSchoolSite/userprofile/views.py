import json
import traceback

from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError, PermissionDenied
from django.db.models import Q
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from userprofile.forms import User, UserForm, RelationshipAcceptanceForm
from notifications.signals import notify
from django.utils.translation import ugettext_lazy as _
from userprofile.models import Relationship

from userprofile.utils import is_group_member

from main.enums import APPROVED


@login_required
def profile(request):
    return render(request, 'userprofile/user_profile.html', {"user": request.user})


def logout(req):
    auth.logout(req)
    return redirect(reverse('index'))


@login_required
def edit_profile(request):
    form = UserForm(request.POST or None, instance=request.user)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('user_profile'))

    return render(request, 'userprofile/user_profile_edit.html', {"form": form})


@login_required
def relatives_choice(request):
    return render(request, 'userprofile/relatives_choice.html')


# temp solution (disable csfr token checking - need to add token from client side!)
@login_required
@csrf_exempt
def json_relatives_choice(request):
    if request.is_ajax() and request.method == 'POST':
        try:
            user = request.user
            data = json.loads(request.body.decode('utf-8'))
            relative = User.objects.get(id=data['relative_id'])
            relative_type = ''  # data['relative_choice']

            parents_group = _('Parents')
            is_user_parent = is_group_member(user, parents_group)
            is_relative_parent = is_group_member(relative, parents_group)

            if is_user_parent and is_relative_parent:
                # parents can't have child relationship
                raise ValueError(_("You can't add another parent as child!"))
            elif not is_user_parent and not is_relative_parent:
                # both users are not parents and request.user want to invite relative_user as parent
                relative_type = 'parent'
            elif (is_user_parent and not is_relative_parent) or (is_relative_parent and not is_user_parent):
                # only one of persons is parent
                relative_type = 'child'

            invitation_code = get_random_string(length=8)

            relative_person_id = None
            child_person_id = None
            invited_person_id = relative.id

            if relative_type == 'parent':
                relative_person_id = relative.id
                child_person_id = user.id
            elif relative_type == 'child':
                relative_person_id = relative.id if is_relative_parent else user.id
                child_person_id = user.id if is_relative_parent else relative.id

            relationship = Relationship(relative=User.objects.get(id=relative_person_id),
                                        child=User.objects.get(id=child_person_id),
                                        invited_user=User.objects.get(id=invited_person_id),
                                        code=invitation_code)
            relationship.save()

            notify.send(request.user, recipient=relative, verb=_('Relationship request'),
                        relative_type=relative_type, template='notifications/templates/relationship_request.html',
                        username=request.user.username, initials=request.user.get_initials(),
                        invitation_code=invitation_code)

            return HttpResponse(json.dumps({'status': 'OK'}), content_type="application/json")
        except Exception as e:
            return HttpResponse(json.dumps({'status': 'ERR', 'message': str(e)}), content_type="application/json")


def relationship_acceptance(request, relative):
    form = None
    user = request.user
    relative = get_object_or_404(User, username=relative)

    # try to get relationship between users
    try:
        relationship = Relationship.objects.get(Q(relative=relative, child=user) | Q(relative=user, child=relative))
    except Relationship.DoesNotExist:
        raise PermissionDenied(_('This person didn\'t send you a relationship request!'))

    if relationship.request == APPROVED:
        raise PermissionDenied(_('Request has already approved!'))

    parents_group = _('Parents')

    is_user_parent = is_group_member(user, parents_group)
    is_relative_parent = is_group_member(relative, parents_group)

    # TODO: integrate children query

    # get proper label for relationship field in form
    relationship_label = ''
    if (not is_user_parent and not is_relative_parent) or (is_user_parent and not is_relative_parent):
        # parent give information  about himself
        relationship_label = _('Specify your relationship')
    else:
        relationship_label = _('Specify %(user)s relationship') % {'user': relative.username}

    if request.method == 'POST':
        form = RelationshipAcceptanceForm(request.POST, relationship_label=relationship_label)

        if form.data['password'] == relationship.code:
            relationship.request = APPROVED
            relationship.save()

            if not is_user_parent and not is_relative_parent:
                # relative is new parent
                user.groups.add(Group.objects.get(name=parents_group))

            return HttpResponseRedirect(reverse('user_profile'))
        else:
            form.add_error('password', _('Invitation code are not same!'))
    else:
        form = RelationshipAcceptanceForm(relationship_label=relationship_label)

    return render(request, 'userprofile/relationship_acceptance.html', {'form': form, 'relative': relative})
