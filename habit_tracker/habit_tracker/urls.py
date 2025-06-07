from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from tracker.views import register
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', LoginView.as_view(template_name='tracker/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', register, name='register'),
    path('', include('tracker.urls')),
]

