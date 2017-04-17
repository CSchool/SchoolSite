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
            data = json.loads(request.body.decode('utf-8'))
            child = None
            parent = None
            other = None
            if data.get('relative_id'):
                relative_id = data.get('relative_id')
                relative_type = "parent"
                child = request.user
                parent = other = User.objects.get(id=relative_id)
            elif data.get('child_id'):
                relative_id = data.get('child_id')
                relative_type = "child"
                parent = request.user
                child = other = User.objects.get(id=relative_id)
            else:
                raise PermissionDenied

            parents_group = _('Parents')

            relationship = Relationship(relative=parent,
                                        child=child,
                                        invited_user=other)
            relationship.save()

            notify.send(request.user, recipient=other, verb=_('Relationship request'),
                        relative_type=relative_type, template='notifications/templates/relationship_request.html',
                        username=request.user.username, initials=request.user.get_initials())

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
        raise PermissionDenied

    if relationship.request == Relationship.APPROVED:
        raise PermissionDenied(_('Request has already been approved'))

    if relationship.invited_user != request.user:
        raise PermissionDenied

    parents_group = _('Parents')
    students_group = _('Students')

    rel_type = _('parent') if relationship.child == user else _('child')

    # TODO: integrate children query

    if request.method == 'POST':
        if request.POST.get('decline'):
            relationship.request = Relationship.DECLINED
            relationship.save()
        else:
            relationship.request = Relationship.APPROVED
            relationship.save()

            if not relationship.relative.is_parent:
                relationship.relative.groups.add(Group.objects.get(name=parents_group))

            if not relationship.child.is_student:
                relationship.child.groups.add(Group.objects.get(name=students_group))
        return HttpResponseRedirect(reverse('user_profile'))
    else:
        form = RelationshipAcceptanceForm()

    return render(request, 'userprofile/relationship_acceptance.html', {'rel_type': rel_type, 'relative': relative})
