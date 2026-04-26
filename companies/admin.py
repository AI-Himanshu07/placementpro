from django.contrib import admin
from .models import Company, Job, CompanyUser

# COMPANY
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'min_cgpa')


# JOB
@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'min_cgpa', 'status')
    list_filter = ('company',)


# COMPANY USER (FIXED)
@admin.register(CompanyUser)
class CompanyUserAdmin(admin.ModelAdmin):
    list_display = ('user',)   # ✅ ONLY user (safe)