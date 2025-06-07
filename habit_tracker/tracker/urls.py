from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add/', views.add_habit, name='add_habit'),
    path('habit/<int:habit_id>/', views.habit_detail, name='habit_detail'),
    path('habit/<int:habit_id>/delete/', views.delete_habit, name='delete_habit'),
]

