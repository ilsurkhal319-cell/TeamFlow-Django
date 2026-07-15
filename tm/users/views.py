from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from .forms import CustomUserCreationForm, CustomAuthenticationForm

def login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('home')
    else:
        form = CustomAuthenticationForm()

    context = {
        'title': 'Авторизация',
        'form': form
    }
    return render(request, 'users/login.html', context)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()

    context = {
        'title': 'Регистрация',
        'form': form
    }
    return render(request, 'users/register.html', context)
