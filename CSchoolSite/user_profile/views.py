from django.http import Http404
from django.shortcuts import render


# Create your views here.

def profile(request):
    user = None
    if request.user.is_authenticated():
        user = request.user
    else:
        raise Http404("User is not authenticated")

    return render(request, 'user_profile/profile.html', {"user": user})
