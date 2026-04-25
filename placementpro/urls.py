from django.contrib import admin
from django.urls import path, include
from .views import login_view, dashboard
from .views import logout_view
from . import views
urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.home),
    path('login/', views.login_view),
    path('dashboard/', dashboard),
    path('logout/', logout_view, name='logout'),

    path('students/', include('students.urls')),
    path('companies/', include('companies.urls')),
]