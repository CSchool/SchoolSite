import datetime
import string
import random

from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import utc
from django.utils.translation import ugettext as _
from django.contrib.auth.views import LoginView

from userprofile.forms import UserForm, ExtendedAuthenticationForm
from userprofile.utils import is_group_member
from userprofile.models import User, Relationship
from main.helpers import get_sapp

class ExtendedLoginView(LoginView):
    authentication_form = ExtendedAuthenticationForm

@login_required
def profile(request):
    if not request.user.personal:
        raise PermissionDenied
    if request.POST.get('delete_relation'):
        relation_id = request.POST.get('delete_relation')
        try:
            rel = Relationship.objects.get(id=relation_id)
        except Relationship.DoesNotExist:
            return redirect(reverse('user_profile'))
        if rel.child == request.user or rel.parent == request.user:
            rel.delete()
        return redirect(reverse('user_profile'))
    if request.POST.get('redeem_relationship_code'):
        code = request.POST.get('code')
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        try:
            rel = Relationship.objects.exclude(invited_user=request.user) \
                .get(confirmation_code=code,
                     valid_until__gt=now,
                     request=Relationship.WAITING)
        except Relationship.DoesNotExist:
            return redirect(reverse('user_profile'))
        if rel.child is None:
            rel.child = request.user
        elif rel.relative is None:
            rel.relative = request.user
            if not request.user.is_parent:
                Group.objects.get(name=_('Parents')).user_set.add(request.user)
            if request.user.is_student:
                Group.objects.get(name=_('Students')).user_set.remove(request.user)
        else:
            return redirect(reverse('user_profile'))
        rel.request = Relationship.APPROVED
        rel.confirmation_code = None
        rel.valid_until = None
        rel.save()
        return redirect(reverse('user_profile'))
    return render(request, 'userprofile/user_profile.html', {"user": request.user, "sapp": get_sapp(request)})


def login(request, *args, **kwargs):
    return ExtendedLoginView.as_view(**kwargs)(request, *args, **kwargs)


def logout(req):
    auth.logout(req)
    return redirect(reverse('index'))


@login_required
def edit_profile(request):
    if not request.user.personal:
        raise PermissionDenied
    form = UserForm(request.POST or None, instance=request.user)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('user_profile'))

    return render(request, 'userprofile/user_profile_edit.html', {"form": form, "sapp": get_sapp(request)})


@csrf_exempt
@login_required
def get_relationship_code(req):
    tp = ''
    if req.POST.get('reltype') == 'child':
        tp = 'child'
    elif req.POST.get('reltype') == 'parent':
        tp = 'parent'
    else:
        raise PermissionDenied
    rel = Relationship.objects.filter(request=Relationship.WAITING, invited_user=req.user)
    if tp == 'child':
        rel = rel.filter(relative=req.user)
    elif tp == 'parent':
        rel = rel.filter(child=req.user)
    rel.order_by('-valid_until')
    now = datetime.datetime.utcnow().replace(tzinfo=utc)
    if not rel.exists():
        if tp == 'child':
            r = Relationship(relative=req.user)
        elif tp == 'parent':
            r = Relationship(child=req.user)
        r.invited_user = req.user
    else:
        r = rel[0]
    if not r.valid_until or (r.valid_until <= now):
        r.valid_until = now + datetime.timedelta(minutes=10)
        while True:
            code = ''.join(random.SystemRandom().choice(
                string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(8))
            if Relationship.objects.filter(request=Relationship.WAITING, valid_until__gt=now, confirmation_code=code).exists():
                continue
            break
        r.confirmation_code = code
    r.save()
    Relationship.objects.filter(request=Relationship.WAITING, valid_until__lt=now).delete() # Clean junk
    return JsonResponse({
        'valid_for': (r.valid_until - now).total_seconds(),
        'code': r.confirmation_code
    })

@csrf_exempt
@login_required
def relationship_code_info(req):
    code = req.POST.get('code')
    now = datetime.datetime.utcnow().replace(tzinfo=utc)
    try:
        rel = Relationship.objects.exclude(invited_user=req.user)\
                                  .get(confirmation_code=code,
                                       valid_until__gt=now,
                                       request=Relationship.WAITING)
    except Relationship.DoesNotExist:
        return JsonResponse({
            'found': False
        })
    if rel.child == rel.invited_user:
        reltype = _('will be your child')
    else:
        reltype = _('will be your parent')
    initials = rel.invited_user.get_full_name()
    return JsonResponse({
        'found': True,
        'name': initials,
        'reltype': reltype
    })