from django.urls import path

from main.views import *
app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("experience/add/", create_experience, name="create_experience"),
    path(
        "experiences/<uuid:experience_id>/edit/",
        update_experience,
        name="update_experience",
    ),
    path(
        "experiences/<uuid:experience_id>/delete/",
        delete_experience,
        name="delete_experience",
    ),
    path("achievement/", show_achievement, name="show_achievement"),
    path('project/', show_project, name="show_project"),
    path('project/add/', create_project, name='create_project'),
    path("projects/<uuid:project_id>/edit/", update_project, name="update_project"),
    path("api/projects/", get_projects_json, name="get_projects_json"),
    path("api/experiences/", get_experiences_json, name="get_experiences_json"),
    path("projects/<uuid:project_id>/delete/",delete_project,name="delete_project"),
    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
    # Tambahkan path ini ke dalam urlpatterns
    path(
        "projects/<uuid:project_id>/star/",
        toggle_star,
        name="toggle_star",
    ),
]
