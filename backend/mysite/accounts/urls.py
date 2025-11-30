from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', LogoutView.as_view(next_page='/accounts/login/'), name='logout'),
    path('dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
] + staticfiles_urlpatterns()