from django.contrib import admin
from django.urls import path, include
from accounts import views  

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', views.user_login, name='home'),  # ГЛАВНАЯ СТРАНИЦА ВЕДЕТ НА ВХОД
]