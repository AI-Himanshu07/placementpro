from django.contrib import admin
from .models import Company, Job, CompanyUser

# ======================
# COMPANY ADMIN
# ======================
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'min_cgpa')
    search_fields = ('name',)

# ======================
# JOB ADMIN (VERY IMPORTANT)
# ======================
@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'min_cgpa', 'status')
    list_filter = ('company',)
    search_fields = ('title',)

# ======================
# COMPANY USER LINK
# ======================
@admin.register(CompanyUser)
class CompanyUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'company')