from django.contrib import admin
from django.urls import path, include
from .views import login_view, dashboard, logout_view
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),

    # 🔹 MAIN ROUTES (same as yours)
    path('', views.home),
    path('login/', login_view),
    path('dashboard/', dashboard),
    path('logout/', logout_view, name='logout'),

    # 🔹 APPS
    path('students/', include('students.urls')),
    path('companies/', include('companies.urls')),
    path(static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)),

    # 🔥 FORGOT PASSWORD FLOW (NEW)
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset.html'
         ),
         name='password_reset'),

    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]