from django.urls import path

from main.views import *
app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("achievement/", show_achievement, name="show_achievement"),
    path('project/', show_project, name="show_project"),
    path('project/add/', create_project, name='create_project'),
    path("api/projects/", get_projects_json, name="get_projects_json"),
    path("projects/<uuid:project_id>/delete/",delete_project,name="delete_project"),
]