
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from .forms import TeacherRegistrationForm, GradeForm
from .models import Submission, Grade, Comment, Assignment, Course

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
    # Получаем курсы преподавателя
    courses = Course.objects.filter(teacher=request.user).annotate(
        assignments_count=Count('assignments', distinct=True)
    )
    
    # Получаем отправки для этих заданий
    submissions = Submission.objects.filter(
        assignment__course__teacher=request.user
    ).select_related(
        'student', 'assignment', 'assignment__course', 'grade'
    ).order_by('-submitted_at')
    
    # Получаем проверенные задания
    graded_submissions = submissions.filter(grade__isnull=False)
    
    # Считаем баллы для наград
    total_points = 0
    if courses.count() > 0:
        total_points += 50  # За первый курс
    if graded_submissions.count() >= 10:
        total_points += 30  # За 10 проверенных заданий
    if courses.count() >= 3:
        total_points += 75  # За 3 курса
    
    # Считаем полученные награды
    achieved_rewards = 0
    if courses.count() > 0:
        achieved_rewards += 1
    if graded_submissions.count() >= 10:
        achieved_rewards += 1
    if courses.count() >= 3:
        achieved_rewards += 1
    
    context = {
        'user': request.user,
        'courses': courses,
        'submissions': submissions,
        'graded_submissions': graded_submissions,
        'pending_submissions': submissions.filter(status='pending'),
        'total_points': total_points,
        'achieved_rewards': achieved_rewards,
    }
    return render(request, 'accounts/teacher_dashboard.html', context)

def home(request):
    return redirect('login')

