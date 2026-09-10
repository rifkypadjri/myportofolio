from django.shortcuts import render

from main.models import Experience, Achievement, Project


def show_main(request):
    context = {
        "name": "Muhammad Rifky Padjri",
        "npm": "2506585800",
        "study_program": "Bachelor of Computer Science",
        "bio": (
            "Undergraduate Computer Science Student at Universitas Indonesia -"
            "Machine Learning & Artificial Intelligence Enthusiast"
        ),
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "name": "Muhammad Rifky Padjri",
        "npm": "2506585800",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)

def show_project(request):
    context = {
        "name": "Muhammad Rifky Padjri",
        "npm": "2506585800",
        "project_list": Project.objects.all(),
    }
    return render(request, "project.html", context)


def show_achievement(request):
    context = {
        "name": "Muhammad Rifky Padjri",
        "npm": "2506585800",
        "achievement_list": Achievement.objects.all(),
    }
    return render(request, "achievement.html", context)