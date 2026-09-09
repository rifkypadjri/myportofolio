from django.shortcuts import render

from main.models import Experience


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
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)