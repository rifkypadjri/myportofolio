from django.shortcuts import render

from main.models import Experience, Achievement, Project
from main.forms import ProjectForm

from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render


def create_project(request):
    form = ProjectForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek baru berhasil ditambahkan!")
        return redirect("main:show_project")

    context = {
        "name": "Burhan",
        "form": form,
    }
    return render(request, "projects_form.html", context)



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

def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    projects_json = serializers.serialize("json", projects)
    return HttpResponse(projects_json, content_type="application/json")

def show_projects(request):
    json_response = get_projects_json(request)

    projects = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    projects = [project.object for project in projects]
    title_query = request.GET.get("title", "").strip()

    context = {
        "name": "Burhan",
        "project_list": projects,
        "title_query": title_query,
    }
    return render(request, "project.html", context)

def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        project.delete()
        messages.success(request, "Project berhasil dihapus!")
        return redirect("main:show_project")

    return redirect("main:show_project")