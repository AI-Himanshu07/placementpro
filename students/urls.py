from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_list, name='student_list'),
    path('add/', views.add_student),
    path('edit/<int:id>/', views.edit_student),
    path('delete/<int:id>/', views.delete_student),

    path('dashboard/', views.student_dashboard),
    path('applications/', views.applications),
    path('apply/<int:company_id>/', views.apply_company),
    path('cancel/<int:id>/', views.cancel_application),

    path('download/', views.download_students),
    path('resume/<int:student_id>/', views.resume_analysis),
    path('admin-apply-job/<int:job_id>/', views.admin_apply_job),
    path('notifications/', views.view_notifications),
    path('add-notification/', views.add_notification),
    path('delete-notification/<int:id>/', views.delete_notification),
    path('apply-job/<int:job_id>/', views.apply_job),
]