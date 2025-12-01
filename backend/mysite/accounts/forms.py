from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from .models import TeacherProfile, Grade

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
            # Добавляем пользователя в группу преподавателей
            teacher_group, created = Group.objects.get_or_create(name='Teacher')
            user.groups.add(teacher_group)

        return user
    
class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['grade_value', 'points', 'comment']
        widgets = {
            'grade_value': forms.Select(attrs={
                'class': 'form-control',
                'style': 'max-width: 200px;'
            }),
            'points': forms.NumberInput(attrs={
                'class': 'form-control',
                'style': 'max-width: 200px;'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Введите ваш комментарий к работе...'
            }),
        }
        labels = {
            'grade_value': 'Оценка',
            'points': 'Баллы',
            'comment': 'Комментарий преподавателя',
        }
    
    def __init__(self, *args, **kwargs):
        max_points = kwargs.pop('max_points', 100)
        super().__init__(*args, **kwargs)
        self.fields['points'].widget.attrs.update({
            'min': 0,
            'max': max_points
        })
        # Устанавливаем варианты оценок
        self.fields['grade_value'].choices = [
            (5, '5 (Отлично)'),
            (4, '4 (Хорошо)'),
            (3, '3 (Удовлетворительно)'),
            (2, '2 (Неудовлетворительно)'),
            (1, '1 (Не сдано)'),
        ]  
    
