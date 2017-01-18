from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from user_profile.forms import UserForm


# Create your views here.


@login_required
def profile(request):
    return render(request, 'user_profile/user_profile.html', {"user": request.user})


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

    return render(request, 'user_profile/user_profile_edit.html', {"form": form})
