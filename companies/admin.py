from django.contrib import admin
from .models import Company, Job

# COMPANY ADMIN
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'min_cgpa')
    search_fields = ('name',)


# JOB ADMIN
@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'min_cgpa', 'status')
    list_filter = ('company',)