from django.urls import path
from . import views

urlpatterns = [
    path('', views.company_list),
    path('dashboard/', views.company_dashboard),

    path('add/', views.add_company),
    path('edit/<int:id>/', views.edit_company),
    path('delete/<int:id>/', views.delete_company),

    path('jobs/', views.company_jobs),
    path('jobs/<int:id>/', views.view_job, name='view_job'),

    path('add-job/', views.add_job),
    path('edit-job/<int:id>/', views.edit_job),
    path('delete-job/<int:id>/', views.delete_job),

    path('applications/', views.company_applications),
    path('update-status/<int:app_id>/<str:status>/', views.update_status),

    path('<int:id>/', views.company_detail),
]