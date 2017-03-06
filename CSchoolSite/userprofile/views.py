import json
import traceback

from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from userprofile.forms import User, UserForm
from notifications.signals import notify
from django.utils.translation import ugettext_lazy as _


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

            notify.send(request.user, recipient=relative, verb=_(
                "{} ({}) has chosen you as your relative!".format(request.user.username,
                                                                   request.user.get_initials())))

            # notification_send([relative], 'relationship_invite',
            #                  {"username": request.user.username, "initials": request.user.get_initials()})

            return HttpResponse(json.dumps({'status': 'OK'}), content_type="application/json")
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return HttpResponse(json.dumps({'status': 'ERR', 'message': str(e)}), content_type="application/json")
