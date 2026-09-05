from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.utils.http import url_has_allowed_host_and_scheme
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from flow.models import Workspace

def login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            if not request.POST.get('remember_me'):
                request.session.set_expiry(0)
            next_url = request.POST.get('next')
            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)
            return redirect('flow:home')
    else:
        form = CustomAuthenticationForm()

    context = {
        'title': 'Авторизация',
        'form': form,
        'next': request.GET.get('next', ''),
    }
    return render(request, 'users/login.html', context)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Workspace.objects.get_or_create(owner=user, name='Main')
            auth_login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()

    context = {
        'title': 'Регистрация',
        'form': form
    }
    return render(request, 'users/register.html', context)
