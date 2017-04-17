from django.shortcuts import render, redirect, reverse
from django.contrib import auth
from django.contrib.admin.views.decorators import staff_member_required
from django.views.static import serve


def index(req):
    return render(req, 'base.html')


def logout(req):
    auth.logout(req)
    return redirect(reverse('index'))

@staff_member_required
def serve_admin_media(*args, **kwargs):
    return serve(*args, **kwargs)