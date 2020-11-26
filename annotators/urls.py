from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),

    path('projects/', views.projects, name='projects'),
    path('projects/<uuid:project_uuid>/', views.editor, name='editor'),
    path('projects/<uuid:project_uuid>/remove/', views.remove_project),

    path('projects/<uuid:project_uuid>/sentences/', views.new_sentences),
    path('projects/<uuid:project_uuid>/changes/', views.add_changes),
    path(
        'projects/<uuid:project_uuid>/sentences/<uuid:sentence_uuid>/remove/',
        views.remove_sentence,
    ),
]
