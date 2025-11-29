from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import TeacherProfile

# Inline для профиля преподавателя
class TeacherProfileInline(admin.StackedInline):
    model = TeacherProfile
    can_delete = False
    verbose_name_plural = 'Профиль преподавателя'
    fields = ('patronymic', 'phone')

# Кастомный админ для User - УПРОЩЕННАЯ ВЕРСИЯ
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    inlines = (TeacherProfileInline,)
    
    # Упрощенные fieldsets без дублирования
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

# Перерегистрируем User
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Админка для TeacherProfile
@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'get_full_name', 'patronymic', 'phone')
    list_filter = ('user__is_active',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone')
    
    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Логин'
    
    def get_full_name(self, obj):
        return f"{obj.user.last_name} {obj.user.first_name}"
    get_full_name.short_description = 'ФИО'