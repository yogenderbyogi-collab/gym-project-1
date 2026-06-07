from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

from ..decorators import ratelimited
from ..models import Member


def home(request):
    return render(request, 'home.html')


@ratelimited(rate='5/m')
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        return render(request, 'login.html', {'error': 'Invalid username or password!'})
    return render(request, 'login.html')


@ratelimited(rate='3/m')
def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        errors = []
        if password1 != password2:
            errors.append('Passwords do not match!')
        if len(password1) < 8:
            errors.append('Password must be at least 8 characters.')
        if not any(c.isupper() for c in password1):
            errors.append('Password needs an uppercase letter.')
        if not any(c.isdigit() for c in password1):
            errors.append('Password needs a number.')
        if User.objects.filter(username=username).exists():
            errors.append('Username already taken!')
        if User.objects.filter(email=email).exists():
            errors.append('Email already registered!')

        if errors:
            return render(request, 'signup.html', {'error': ' '.join(errors)})

        user = User.objects.create_user(
            username=username, email=email, password=password1,
            first_name=first_name, last_name=last_name
        )
        Member.objects.create(user=user)
        messages.success(request, 'Account created! You can now login.')
        return redirect('login')
    return render(request, 'signup.html')


def logout_view(request):
    logout(request)
    return redirect('login')