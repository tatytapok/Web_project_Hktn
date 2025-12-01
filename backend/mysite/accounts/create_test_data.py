import os
import django
import sys

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User, Group
from accounts.models import (
    TeacherProfile, StudentProfile, StudentGroup, 
    Course, Assignment, Homework, Attachment, Grade
)
from django.utils import timezone
from datetime import timedelta

def create_test_data():
    print("Создание тестовых данных...")
    
    # Создаем группы пользователей
    teacher_group, _ = Group.objects.get_or_create(name='Teacher')
    student_group, _ = Group.objects.get_or_create(name='Student')
    
    # Создаем преподавателя
    teacher_user = User.objects.create_user(
        username='teacher1',
        email='teacher@example.com',
        password='password123',
        first_name='Иван',
        last_name='Петров'
    )
    teacher_user.groups.add(teacher_group)
    
    teacher_profile = TeacherProfile.objects.create(
        user=teacher_user,
        patronymic='Иванович',
        phone='+7 (999) 123-45-67'
    )
    
    # Создаем группу студентов
    student_group_obj = StudentGroup.objects.create(
        name='МАТ-21-1',
        code='MAT-21-01'
    )
    
    # Создаем студентов
    student_users = []
    student_names = [
        ('Алексей', 'Иванов', 'ivanov_a'),
        ('Мария', 'Петрова', 'petrova_m'),
        ('Иван', 'Сидоров', 'sidorov_i'),
        ('Анна', 'Кузнецова', 'kuznetsova_a'),
    ]
    
    for first_name, last_name, username in student_names:
        user = User.objects.create_user(
            username=username,
            email=f'{username}@example.com',
            password='password123',
            first_name=first_name,
            last_name=last_name
        )
        user.groups.add(student_group)
        student_users.append(user)
        
        StudentProfile.objects.create(
            user=user,
            group=student_group_obj,
            student_id=f'STD{len(student_users):03d}',
            phone=f'+7 (999) 111-{len(student_users):02d}-{len(student_users):02d}'
        )
    
    # Создаем курс
    course = Course.objects.create(
        title='Математика для начинающих',
        description='Курс по основам математики для студентов первого курса',
        teacher=teacher_user,
        is_active=True
    )
    
    # Добавляем студентов на курс
    for student in StudentProfile.objects.all():
        course.students.add(student)
    
    # Создаем задание
    assignment = Assignment.objects.create(
        course=course,
        title='Линейные уравнения',
        description='Решить систему линейных уравнений',
        assignment_type='homework',
        max_points=100,
        due_date=timezone.now() + timedelta(days=7)
    )
    
    # Создаем домашние работы для студентов
    for i, student in enumerate(StudentProfile.objects.all(), 1):
        homework = Homework.objects.create(
            assignment=assignment,
            student=student,
            text_content=f'Решение задач по линейным уравнениям. Вариант {i}',
            status='submitted' if i % 2 == 0 else 'graded',
            priority='medium',
            submitted_at=timezone.now() - timedelta(days=i)
        )
        
        # Для некоторых работ создаем оценки
        if i % 2 == 0:
            Grade.objects.create(
                homework=homework,
                teacher=teacher_user,
                grade_value=5 if i % 3 == 0 else 4,
                points=90 if i % 3 == 0 else 75,
                comment='Отличная работа!' if i % 3 == 0 else 'Хорошо, но есть недочеты'
            )
    
    print("Тестовые данные созданы успешно!")
    print(f"Преподаватель: {teacher_user.username}/password123")
    print(f"Студенты: {', '.join([u.username for u in student_users])}/password123")

if __name__ == '__main__':
    create_test_data()