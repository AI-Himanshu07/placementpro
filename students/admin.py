from django.contrib import admin
from .models import Student, Application

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'cgpa', 'user')
    search_fields = ('name', 'email')
    list_filter = ('cgpa',)

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'company', 'applied_on')