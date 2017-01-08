from django.shortcuts import render, redirect, reverse

from django.contrib import auth


def index(req):
    return render(req, 'base.html')


def logout(req):
    auth.logout(req)
    return redirect(reverse('index'))
