from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', LogoutView.as_view(next_page='/accounts/login/'), name='logout'),
    path('dashboard/', views.teacher_dashboard, name='teacher_dashboard'),

    # Домашние задания
    path('homeworks/', views.homework_list, name='homework_list'),  # ОБРАТИТЕ ВНИМАНИЕ: 'homework_list'
    path('homework/<int:homework_id>/', views.homework_detail, name='homework_detail'),
    path('homework/<int:homework_id>/grade/', views.grade_homework, name='grade_homework'),
    path('homework/<int:homework_id>/request-revision/', views.request_revision, name='request_revision'),
    path('homework/<int:homework_id>/download/', views.download_homework_zip, name='download_homework_zip'),
    path('attachment/<int:attachment_id>/download/', views.download_attachment, name='download_attachment'),
    
    # Курсы и задания
    path('course/<int:course_id>/assignments/', views.course_assignments, name='course_assignments'),
    path('assignment/<int:assignment_id>/', views.assignment_detail, name='assignment_detail'),
    
    # Журнал успеваемости
    path('gradebook/', views.gradebook, name='gradebook'),
    path('gradebook/course/<int:course_id>/', views.gradebook, name='gradebook_course'),
    
    # Прогресс студента
    path('student/<int:student_id>/progress/', views.student_progress, name='student_progress'),
] + staticfiles_urlpatterns()