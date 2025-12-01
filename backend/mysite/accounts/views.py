
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from .forms import TeacherRegistrationForm


# домашняя страница
def home(request):
    """Домашняя страница - перенаправляет на вход"""
    return redirect('login')



# страницы для входа, регистрации
def register(request):
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Регистрация успешна! Теперь вы можете войти.')
            return redirect('login')
    else:
        form = TeacherRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def user_login(request):
    # Показываем сообщение об успешном выходе если есть
    if request.GET.get('logout'):
        messages.success(request, 'Вы успешно вышли из системы.')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('teacher_dashboard')
        else:
            messages.error(request, 'Неверный логин или пароль')
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def teacher_dashboard(request):
    return render(request, 'accounts/teacher_dashboard.html', {'user': request.user})


def home(request):
    return redirect('login')

