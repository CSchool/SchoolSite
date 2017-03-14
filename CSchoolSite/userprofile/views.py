import json
import traceback

from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from userprofile.forms import User, UserForm
from notifications.signals import notify
from django.utils.translation import ugettext_lazy as _
from userprofile.models import Relationship


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


# temp solution (disbale csfr token checking - need to add token from client side!)
@login_required
@csrf_exempt
def json_relatives_choice(request):
    if request.is_ajax() and request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            relative = User.objects.get(id=data['relative_id'])
            relative_type = data['relative_choice']

            if relative_type in ('parent', 'child',):
                # generate invitation code
                invitation_code = get_random_string(length=8)
                encrypted_code = make_password(invitation_code)

                relative_person_id = relative.id if relative_type == 'parent' else request.user.id
                child_person_id = request.user.id if relative_type == 'parent' else relative.id
                invited_person_id = relative.id if relative_type == 'parent' else request.user.id

                relationship = Relationship(relative=User.objects.get(id=relative_person_id),
                                            child=User.objects.get(id=child_person_id),
                                            invited_user=User.objects.get(id=invited_person_id),
                                            code=encrypted_code)
                relationship.save()

                notify.send(request.user, recipient=relative, verb=_('Relationship request'),
                            template='notifications/templates/relationship_request.html',
                            username=request.user.username, initials=request.user.get_initials(),
                            invitation_code=invitation_code)

                return HttpResponse(json.dumps({'status': 'OK'}), content_type="application/json")
            else:
                raise ValueError(_('Your relative type is incorrect!'))
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return HttpResponse(json.dumps({'status': 'ERR', 'message': str(e)}), content_type="application/json")
