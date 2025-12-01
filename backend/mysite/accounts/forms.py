from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import TeacherProfile

class TeacherRegistrationForm(UserCreationForm):
    last_name = forms.CharField(
        max_length=100, 
        label='Фамилия*',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите фамилию'})
    )
    first_name = forms.CharField(
        max_length=100, 
        label='Имя*',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя'})
    )
    patronymic = forms.CharField(
        max_length=100, 
        required=False,
        label='Отчество',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите отчество'})
    )
    phone = forms.CharField(
        max_length=20, 
        label='Телефон*',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите телефон'})
    )
    email = forms.EmailField(
        label='Email*',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Введите email'})
    )

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'last_name', 'first_name', 'email')
        labels = {
            'username': 'Логин*',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Придумайте логин'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.last_name = self.cleaned_data['last_name']
        user.first_name = self.cleaned_data['first_name']
        user.email = self.cleaned_data['email']
        user.is_active = True  #  Активируем пользователя
        #user.is_staff = True   #  Даем доступ к админке (опционально)
        
        if commit:
            user.save()
            # Создаем профиль преподавателя
            TeacherProfile.objects.create(
                user=user,
                patronymic=self.cleaned_data['patronymic'],
                phone=self.cleaned_data['phone']
            )
        return user
    
