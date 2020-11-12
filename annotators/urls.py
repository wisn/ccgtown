from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),

    path('projects/', views.projects, name='projects'),
    path('projects/<uuid:project_uuid>/delete/', views.delete_project),
]
