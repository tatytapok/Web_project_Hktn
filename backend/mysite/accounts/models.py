from django.db import models
from django.contrib.auth.models import User

class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    patronymic = models.CharField(max_length=100, blank=True, verbose_name='Отчество')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    
    def __str__(self):
        return f"{self.user.last_name} {self.user.first_name}"
    
