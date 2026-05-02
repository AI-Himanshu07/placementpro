from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.home),
    path('login/', views.login_view),
    path('dashboard/', views.dashboard),
    path('logout/', views.logout_view, name='logout'),

    path('students/', include('students.urls')),
    path('companies/', include('companies.urls')),

    # 🔐 PASSWORD RESET
   # 🔐 PASSWORD RESET
path('password-reset/', 
     auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html'), 
     name='password_reset'),

path('password-reset/done/', 
     auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), 
     name='password_reset_done'),

path('reset/<uidb64>/<token>/', 
     auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), 
     name='password_reset_confirm'),

path('reset/done/', 
     auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), 
     name='password_reset_complete'),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)