from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import os

class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    patronymic = models.CharField(max_length=100, blank=True, verbose_name='Отчество')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    
    def __str__(self):
        return f"{self.user.last_name} {self.user.first_name}"
    
    @property
    def full_name(self):
        if self.patronymic:
            return f"{self.user.last_name} {self.user.first_name} {self.patronymic}"
        return f"{self.user.last_name} {self.user.first_name}"

class StudentGroup(models.Model):
    """Группа студентов"""
    name = models.CharField(max_length=100, verbose_name='Название группы')
    code = models.CharField(max_length=20, unique=True, verbose_name='Код группы')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Группа студентов'
        verbose_name_plural = 'Группы студентов'
    
    def __str__(self):
        return self.name

class StudentProfile(models.Model):
    """Профиль студента"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    group = models.ForeignKey(StudentGroup, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Группа')
    student_id = models.CharField(max_length=20, unique=True, verbose_name='Студенческий билет')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    
    class Meta:
        verbose_name = 'Профиль студента'
        verbose_name_plural = 'Профили студентов'
    
    def __str__(self):
        return f"{self.user.last_name} {self.user.first_name}"
    
    @property
    def full_name(self):
        return f"{self.user.last_name} {self.user.first_name}"

class Course(models.Model):
    """Курс обучения"""
    title = models.CharField(max_length=200, verbose_name='Название курса')
    description = models.TextField(verbose_name='Описание курса')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'groups__name': 'Teacher'},verbose_name='Преподаватель')
    students = models.ManyToManyField(StudentProfile, through='CourseEnrollment', verbose_name='Студенты')
    is_active = models.BooleanField(default=True, verbose_name='Активный')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
    
    def __str__(self):
        return self.title
    
    @property
    def active_students_count(self):
        return self.students.filter(courseenrollment__is_active=True).count()

class CourseEnrollment(models.Model):
    """Запись о зачислении студента на курс"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('course', 'student')
        verbose_name = 'Запись о зачислении'
        verbose_name_plural = 'Записи о зачислении'

class Assignment(models.Model):
    """Задание курса"""
    TYPE_CHOICES = [
        ('test', 'Тест'),
        ('homework', 'Домашнее задание'),
        ('project', 'Проект'),
        ('exam', 'Экзамен'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200, verbose_name='Название задания')
    description = models.TextField(verbose_name='Описание задания')
    assignment_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='homework', verbose_name='Тип задания')
    max_points = models.IntegerField(default=100, verbose_name='Максимальный балл')
    due_date = models.DateTimeField(verbose_name='Срок сдачи')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Задание'
        verbose_name_plural = 'Задания'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    @property
    def is_overdue(self):
        return timezone.now() > self.due_date

class Homework(models.Model):
    """Домашняя работа студента"""
    STATUS_CHOICES = [
        ('assigned', 'Назначено'),
        ('submitted', 'Сдано'),
        ('graded', 'Проверено'),
        ('revision', 'На доработке'),
        ('late', 'Сдано с опозданием'),
        ('missed', 'Пропущено'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
    ]
    
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='homeworks')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='homeworks')
    text_content = models.TextField(blank=True, verbose_name='Текстовый ответ')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned', verbose_name='Статус')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES,default='medium', verbose_name='Приоритет')
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата сдачи')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Домашняя работа'
        verbose_name_plural = 'Домашние работы'
        unique_together = ('assignment', 'student')
    
    def __str__(self):
        return f"{self.student} - {self.assignment.title}"
    
    @property
    def is_on_time(self):
        if not self.submitted_at:
            return False
        return self.submitted_at <= self.assignment.due_date
    
    @property
    def submission_status(self):
        if not self.submitted_at:
            return 'Не сдано'
        if self.submitted_at > self.assignment.due_date:
            return 'Сдано с опозданием'
        return 'Сдано вовремя'

def homework_attachment_path(instance, filename):
    """Путь для сохранения файлов домашних заданий"""
    return f'homeworks/{instance.homework.id}/{filename}'

class Attachment(models.Model):
    """Вложение к домашней работе"""
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE, 
                                related_name='attachments')
    file = models.FileField(upload_to=homework_attachment_path, verbose_name='Файл')
    file_name = models.CharField(max_length=255, verbose_name='Имя файла')
    file_size = models.IntegerField(verbose_name='Размер файла (байты)')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Вложение'
        verbose_name_plural = 'Вложения'
    
    def __str__(self):
        return self.file_name
    
    def get_file_size(self):
        """Возвращает размер файла в удобном формате"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def get_extension(self):
        """Возвращает расширение файла"""
        return os.path.splitext(self.file_name)[1].lower()

class Grade(models.Model):
    """Оценка за домашнюю работу"""
    homework = models.OneToOneField(Homework, on_delete=models.CASCADE, related_name='grade')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'groups__name': 'Teacher'},verbose_name='Преподаватель')
    grade_value = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Оценка',
        null=True,  # Добавляем
        blank=True  # Добавляем
    )
    points = models.IntegerField(
        verbose_name='Баллы',
        null=True,  # Добавляем
        blank=True  # Добавляем
    )

    comment = models.TextField(blank=True, verbose_name='Комментарий')
    is_revision_request = models.BooleanField(default=False, verbose_name='Запрос доработки')
    graded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Оценка'
        verbose_name_plural = 'Оценки'
    
    def __str__(self):
        if self.grade_value:
            return f"{self.homework} - {self.grade_value}"
        elif self.is_revision_request:
            return f"{self.homework} - Запрос доработки"
        else:
            return f"{self.homework} - Без оценки"
    
    @property
    def grade_with_text(self):
        if self.grade_value:
            grades_text = {
                5: 'Отлично',
                4: 'Хорошо',
                3: 'Удовлетворительно',
                2: 'Неудовлетворительно',
                1: 'Не сдано',
            }
            return f"{self.grade_value} ({grades_text.get(self.grade_value, '')})"
        elif self.is_revision_request:
            return "На доработке"
        else:
            return "Без оценки"

class HomeworkHistory(models.Model):
    """История изменений домашней работы (для версионирования)"""
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE, 
                                related_name='history')
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Изменено пользователем')
    changed_at = models.DateTimeField(auto_now_add=True)
    change_description = models.TextField(verbose_name='Описание изменения')
    
    class Meta:
        verbose_name = 'История изменений'
        verbose_name_plural = 'История изменений'
        ordering = ['-changed_at']
    
    def __str__(self):
        return f"{self.homework} - {self.changed_at}"

class TestQuestion(models.Model):
    """Вопрос теста"""
    TYPE_CHOICES = [
        ('single', 'Один правильный ответ'),
        ('multiple', 'Несколько правильных ответов'),
        ('matching', 'Соответствие'),
        ('text', 'Текстовый ответ'),
    ]
    
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField(verbose_name='Текст вопроса')
    question_type = models.CharField(max_length=20, choices=TYPE_CHOICES, 
                                    default='single', verbose_name='Тип вопроса')
    points = models.IntegerField(default=1, verbose_name='Баллы за вопрос')
    order = models.IntegerField(default=0, verbose_name='Порядок')
    
    class Meta:
        verbose_name = 'Вопрос теста'
        verbose_name_plural = 'Вопросы теста'
        ordering = ['order']
    
    def __str__(self):
        return f"Вопрос {self.order}: {self.question_text[:50]}..."

class TestAnswer(models.Model):
    """Вариант ответа на вопрос теста"""
    question = models.ForeignKey(TestQuestion, on_delete=models.CASCADE, 
                                related_name='answers')
    answer_text = models.TextField(verbose_name='Текст ответа')
    is_correct = models.BooleanField(default=False, verbose_name='Правильный ответ')
    order = models.IntegerField(default=0, verbose_name='Порядок')
    
    class Meta:
        verbose_name = 'Ответ на вопрос'
        verbose_name_plural = 'Ответы на вопросы'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.answer_text[:50]}... ({'✓' if self.is_correct else '✗'})"

class TestSubmission(models.Model):
    """Ответ студента на тест"""
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE, 
                                related_name='test_submissions')
    question = models.ForeignKey(TestQuestion, on_delete=models.CASCADE)
    answer = models.ForeignKey(TestAnswer, on_delete=models.CASCADE, null=True, blank=True)
    answer_text = models.TextField(blank=True, verbose_name='Текстовый ответ')
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Ответ на тест'
        verbose_name_plural = 'Ответы на тесты'
        unique_together = ('homework', 'question')
    
    def __str__(self):
        return f"{self.homework.student} - {self.question}"
    
    @property
    def is_correct(self):
        if self.answer:
            return self.answer.is_correct
        return False

# Модель для SCORM материалов (дополнительная фича)
class SCORMPackage(models.Model):
    """SCORM пакет для курса"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='scorm_packages')
    title = models.CharField(max_length=200, verbose_name='Название пакета')
    package_file = models.FileField(upload_to='scorm_packages/', verbose_name='SCORM пакет')
    version = models.CharField(max_length=50, verbose_name='Версия SCORM')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'groups__name': 'Teacher'})
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'SCORM пакет'
        verbose_name_plural = 'SCORM пакеты'
    
    def __str__(self):
        return self.title

# Модель для чата (дополнительная фича)
class ChatRoom(models.Model):
    """Чат-комната для курса"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='chat_rooms')
    name = models.CharField(max_length=100, verbose_name='Название комнаты')
    topic = models.CharField(max_length=200, blank=True, verbose_name='Тема')
    is_private = models.BooleanField(default=False, verbose_name='Приватная')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Чат-комната'
        verbose_name_plural = 'Чат-комнаты'
    
    def __str__(self):
        return f"{self.course.title} - {self.name}"

class ChatMessage(models.Model):
    """Сообщение в чате"""
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, 
                            related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(verbose_name='Сообщение')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Сообщение чата'
        verbose_name_plural = 'Сообщения чата'
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.sender}: {self.message[:50]}..."