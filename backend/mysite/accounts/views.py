from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.http import require_POST, require_GET
from django.core.paginator import Paginator
from django.utils import timezone
from django.conf import settings
import os
import zipfile
import io
from .forms import TeacherRegistrationForm, GradeForm
from .models import Course, Assignment, Homework, Attachment, Grade, StudentGroup

# домашняя страница
def home(request):
    """Домашняя страница - перенаправляет на вход"""
    return redirect('login')

# Проверка, является ли пользователь преподавателем
def is_teacher(user):
    return user.groups.filter(name='Teacher').exists() or user.is_staff

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
    """Панель управления преподавателя"""
    # Получаем курсы преподавателя
    courses = Course.objects.filter(teacher=request.user).prefetch_related('assignments')
    
    # Добавляем статистику для каждого курса
    for course in courses:
        # Считаем студентов в курсе
        course.students_count = course.students.count()
        # Считаем задания в курсе
        course.assignments_count = course.assignments.count()
        # Считаем задания на проверке для этого курса
        course.pending_count = Homework.objects.filter(
            assignment__course=course,
            status='submitted'
        ).count()
    
    # Получаем домашние задания для таблицы (с пагинацией)
    homeworks = Homework.objects.filter(
        assignment__course__teacher=request.user
    ).select_related(
        'student__user',
        'assignment__course',
        'grade'
    ).order_by('-submitted_at')[:20]  # Показываем последние 20 заданий
    
    # Статистика
    pending_count = Homework.objects.filter(
        assignment__course__teacher=request.user,
        status='submitted'
    ).count()
    
    graded_count = Homework.objects.filter(
        assignment__course__teacher=request.user,
        status='graded'
    ).count()
    
    # Для наград (заглушки)
    total_points = 0  # Можно заменить на реальное значение
    
    context = {
        'user': request.user,
        'courses': courses,
        'homeworks': homeworks,  # Переименовал с submissions на homeworks
        'pending_submissions_count': pending_count,
        'graded_submissions_count': graded_count,
        'total_points': total_points,
    }
    return render(request, 'accounts/teacher_dashboard.html', context)

@login_required
@user_passes_test(is_teacher)
def homework_list(request):
    """Список домашних заданий для проверки"""
    # Фильтрация
    status_filter = request.GET.get('status', 'all')
    course_filter = request.GET.get('course', 'all')
    
    # Получаем задания для курсов преподавателя
    homeworks = Homework.objects.filter(
        assignment__course__teacher=request.user
    ).select_related(
        'student', 'assignment', 'assignment__course'
    ).order_by('-submitted_at')
    
    # Применяем фильтры
    if status_filter != 'all':
        homeworks = homeworks.filter(status=status_filter)
    
    if course_filter != 'all':
        homeworks = homeworks.filter(assignment__course_id=course_filter)
    
    # Пагинация
    paginator = Paginator(homeworks, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Получаем курсы для фильтра
    courses = Course.objects.filter(teacher=request.user)
    
    context = {
        'page_obj': page_obj,
        'courses': courses,
        'status_filter': status_filter,
        'course_filter': course_filter,
        'status_choices': Homework.STATUS_CHOICES,
    }
    return render(request, 'accounts/homework_list.html', context)

@login_required
@user_passes_test(is_teacher)
def homework_detail(request, homework_id):
    """Детальная страница домашнего задания"""
    homework = get_object_or_404(
        Homework.objects.select_related(
            'student__user',
            'assignment__course',
            'assignment__course__teacher'
        ).prefetch_related('attachments'),
        id=homework_id,
        assignment__course__teacher=request.user
    )
    
    # Получаем историю изменений (версионирование)
    # Исправлено: используем changed_at вместо history_date
    history_entries = homework.history.all().order_by('-changed_at')[:10]
    
    # Получаем предыдущие версии, если есть
    previous_versions = Homework.objects.filter(
        student=homework.student,
        assignment=homework.assignment,
        submitted_at__lt=homework.submitted_at
    ).order_by('-submitted_at')
    
    # Форма для оценки
    if request.method == 'POST':
        form = GradeForm(request.POST, max_points=homework.assignment.max_points)
        if form.is_valid():
            grade = form.save(commit=False)
            grade.homework = homework
            grade.teacher = request.user
            grade.save()
            
            # Обновляем статус домашнего задания
            homework.status = 'graded'
            homework.save()
            
            messages.success(request, 'Оценка успешно сохранена!')
            return redirect('homework_detail', homework_id=homework.id)
    else:
        initial_data = {}
        if hasattr(homework, 'grade'):
            initial_data = {
                'grade_value': homework.grade.grade_value,
                'points': homework.grade.points,
                'comment': homework.grade.comment,
            }
        form = GradeForm(initial=initial_data, max_points=homework.assignment.max_points)
    
    context = {
        'homework': homework,
        'form': form,
        'history_entries': history_entries,
        'previous_versions': previous_versions,
        'grade_choices': [
            (5, '5 (Отлично)'),
            (4, '4 (Хорошо)'),
            (3, '3 (Удовлетворительно)'),
            (2, '2 (Неудовлетворительно)'),
            (1, '1 (Не сдано)'),
        ]
    }
    return render(request, 'accounts/homework.html', context)

@login_required
@user_passes_test(is_teacher)
@require_POST
def grade_homework(request, homework_id):
    """API для выставления оценки (AJAX)"""
    homework = get_object_or_404(
        Homework,
        id=homework_id,
        assignment__course__teacher=request.user
    )
    
    try:
        grade_value = int(request.POST.get('grade_value'))
        points = int(request.POST.get('points', 0))
        comment = request.POST.get('comment', '')
        
        # Создаем или обновляем оценку
        grade, created = Grade.objects.update_or_create(
            homework=homework,
            defaults={
                'grade_value': grade_value,
                'points': points,
                'comment': comment,
                'teacher': request.user,
                'graded_at': timezone.now()
            }
        )
        
        # Обновляем статус домашнего задания
        homework.status = 'graded'
        homework.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Оценка успешно сохранена',
            'grade': grade_value,
            'points': points
        })
    except (ValueError, TypeError) as e:
        return JsonResponse({
            'success': False,
            'error': 'Некорректные данные'
        })

@login_required
@user_passes_test(is_teacher)
@require_POST
def request_revision(request, homework_id):
    """Запрос доработки домашнего задания"""
    homework = get_object_or_404(
        Homework,
        id=homework_id,
        assignment__course__teacher=request.user
    )
    
    comment = request.POST.get('comment', '')
    if not comment:
        return JsonResponse({
            'success': False,
            'error': 'Укажите комментарий с замечаниями'
        })
    
    # Создаем комментарий преподавателя
    Grade.objects.create(
        homework=homework,
        teacher=request.user,
        comment=comment,
        is_revision_request=True
    )
    
    # Изменяем статус на "на доработке"
    homework.status = 'revision'
    homework.save()
    
    return JsonResponse({
        'success': True,
        'message': 'Запрос на доработку отправлен'
    })

@login_required
@user_passes_test(is_teacher)
def download_attachment(request, attachment_id):
    """Скачивание отдельного файла"""
    attachment = get_object_or_404(
        Attachment,
        id=attachment_id,
        homework__assignment__course__teacher=request.user
    )
    
    file_path = attachment.file.path
    if os.path.exists(file_path):
        response = FileResponse(
            open(file_path, 'rb'),
            content_type='application/octet-stream'
        )
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
        return response
    
    return HttpResponse('Файл не найден', status=404)

@login_required
@user_passes_test(is_teacher)
def download_homework_zip(request, homework_id):
    """Скачивание всех файлов домашнего задания в ZIP"""
    homework = get_object_or_404(
        Homework.objects.prefetch_related('attachments'),
        id=homework_id,
        assignment__course__teacher=request.user
    )
    
    # Создаем ZIP архив в памяти
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Добавляем файлы вложений
        for attachment in homework.attachments.all():
            file_path = attachment.file.path
            if os.path.exists(file_path):
                zip_file.write(
                    file_path,
                    os.path.basename(file_path)
                )
        
        # Добавляем текстовый ответ, если есть
        if homework.text_content:
            zip_file.writestr('text_answer.txt', homework.text_content)
        
        # Добавляем информацию о задании
        info = f"""
        Студент: {homework.student.user.get_full_name()}
        Группа: {homework.student.group.name if homework.student.group else 'Не указана'}
        Задание: {homework.assignment.title}
        Курс: {homework.assignment.course.title}
        Дата сдачи: {homework.submitted_at.strftime('%d.%m.%Y %H:%M')}
        Статус: {homework.get_status_display()}
        """
        zip_file.writestr('info.txt', info)
    
    zip_buffer.seek(0)
    
    response = HttpResponse(
        zip_buffer.getvalue(),
        content_type='application/zip'
    )
    response['Content-Disposition'] = f'attachment; filename="homework_{homework_id}_{homework.student.user.username}.zip"'
    return response

@login_required
@user_passes_test(is_teacher)
def course_assignments(request, course_id):
    """Задания курса"""
    course = get_object_or_404(
        Course.objects.prefetch_related('assignments'),
        id=course_id,
        teacher=request.user
    )
    
    assignments = course.assignments.all().order_by('-created_at')
    
    context = {
        'course': course,
        'assignments': assignments,
    }
    return render(request, 'accounts/course_assignments.html', context)

@login_required
@user_passes_test(is_teacher)
def assignment_detail(request, assignment_id):
    """Детали задания и список работ студентов"""
    assignment = get_object_or_404(
        Assignment.objects.select_related('course'),
        id=assignment_id,
        course__teacher=request.user
    )
    
    # Получаем все домашние задания по этому заданию
    homeworks = Homework.objects.filter(
        assignment=assignment
    ).select_related(
        'student__user', 'student__group'
    ).order_by('student__user__last_name', 'student__user__first_name')
    
    # Статистика
    total_students = assignment.course.students.count()
    submitted_count = homeworks.filter(status__in=['submitted', 'graded', 'revision']).count()
    graded_count = homeworks.filter(status='graded').count()
    
    context = {
        'assignment': assignment,
        'homeworks': homeworks,
        'total_students': total_students,
        'submitted_count': submitted_count,
        'graded_count': graded_count,
        'pending_count': submitted_count - graded_count,
    }
    return render(request, 'accounts/assignment_detail.html', context)

@login_required
@user_passes_test(is_teacher)
def student_progress(request, student_id):
    """Прогресс студента по всем курсам"""
    # Здесь должна быть логика получения прогресса студента
    # Для MVP можно вернуть заглушку
    context = {
        'student': {'name': 'Иванов Алексей'},
        'courses': [],
    }
    return render(request, 'accounts/student_progress.html', context)

@login_required
@user_passes_test(is_teacher)
def gradebook(request, course_id=None):
    """Журнал успеваемости"""
    if course_id:
        course = get_object_or_404(Course, id=course_id, teacher=request.user)
        courses = [course]
    else:
        courses = Course.objects.filter(teacher=request.user)
    
    gradebook_data = []
    for course in courses:
        students = course.students.select_related('user').all()
        assignments = course.assignments.all()
        
        for student in students:
            student_grades = []
            total_points = 0
            max_points = 0
            
            for assignment in assignments:
                try:
                    homework = Homework.objects.get(
                        assignment=assignment,
                        student=student
                    )
                    if homework.grade:
                        grade = homework.grade.points
                        total_points += grade
                        max_points += assignment.max_points
                        student_grades.append({
                            'assignment': assignment.title,
                            'grade': grade,
                            'max': assignment.max_points,
                            'status': homework.get_status_display()
                        })
                    else:
                        student_grades.append({
                            'assignment': assignment.title,
                            'grade': None,
                            'max': assignment.max_points,
                            'status': homework.get_status_display()
                        })
                except Homework.DoesNotExist:
                    student_grades.append({
                        'assignment': assignment.title,
                        'grade': None,
                        'max': assignment.max_points,
                        'status': 'Не сдано'
                    })
            
            if max_points > 0:
                progress = (total_points / max_points) * 100
            else:
                progress = 0
            
            gradebook_data.append({
                'student': student.user.get_full_name(),
                'group': student.group.name if student.group else '',
                'grades': student_grades,
                'total_points': total_points,
                'max_points': max_points,
                'progress': progress,
                'final_grade': calculate_final_grade(progress)
            })
    
    context = {
        'courses': courses,
        'gradebook_data': gradebook_data,
        'selected_course_id': course_id,
    }
    return render(request, 'accounts/gradebook.html', context)

def calculate_final_grade(progress):
    """Рассчитывает итоговую оценку на основе прогресса"""
    if progress >= 85:
        return 5
    elif progress >= 70:
        return 4
    elif progress >= 55:
        return 3
    elif progress >= 40:
        return 2
    else:
        return 1

def home(request):
    return redirect('login')

