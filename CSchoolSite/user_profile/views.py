from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from user_profile.forms import UserForm


# Create your views here.

@login_required
def profile(request):
    #user_form = UserForm(instance=request.user)
    return render(request, 'user_profile/profile.html', {"user": request.user})
