import datetime

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from main.models import Experience, Achievement, Project
from main.forms import ExperienceForm, ProjectForm
from main.permissions import (
    can_create_content,
    editor_or_superuser_required,
    superuser_create_required,
    superuser_delete_required,
)


@superuser_create_required
def create_project(request):
    form = ProjectForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek baru berhasil ditambahkan!")
        return redirect("main:show_project")

    context = {
        "name": "Burhan",
        "form": form,
        "page_title": "Add New Project",
        "submit_label": "Tambah Project",
    }
    return render(request, "projects_form.html", context)


@superuser_create_required
def create_experience(request):
    form = ExperienceForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Pengalaman baru berhasil ditambahkan!")
        return redirect("main:show_experience")

    context = {
        "name": "Muhammad Rifky Padjri",
        "form": form,
        "page_title": "Add New Experience",
        "submit_label": "Tambah Experience",
    }
    return render(request, "experience_form.html", context)


@editor_or_superuser_required
def update_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    form = ProjectForm(request.POST or None, instance=project)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Project berhasil diperbarui!")
        return redirect("main:show_project")

    context = {
        "name": "Muhammad Rifky Padjri",
        "form": form,
        "page_title": "Edit Project",
        "submit_label": "Simpan Perubahan",
    }
    return render(request, "projects_form.html", context)


@editor_or_superuser_required
def update_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    form = ExperienceForm(request.POST or None, instance=experience)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Pengalaman berhasil diperbarui!")
        return redirect("main:show_experience")

    context = {
        "name": "Muhammad Rifky Padjri",
        "form": form,
        "page_title": "Edit Experience",
        "submit_label": "Simpan Perubahan",
    }
    return render(request, "experience_form.html", context)



def show_main(request):
    last_login = request.COOKIES.get('last_login', 'Belum ada sesi login / Cookie tidak ditemukan')
    context = {
        "name": "Muhammad Rifky Padjri",
        "npm": "2506585800",
        "study_program": "Bachelor of Computer Science",
        "bio": (
            "Undergraduate Computer Science Student at Universitas Indonesia -"
            "Machine Learning & Artificial Intelligence Enthusiast"
        ),
        "last_login": last_login,
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "name": "Muhammad Rifky Padjri",
        "npm": "2506585800",
    }
    if can_create_content(request.user):
        context["form"] = ExperienceForm(auto_id="id_add_experience_%s")
    return render(request, "experience.html", context)

def show_project(request):
    title_query = request.GET.get("title", "").strip()
    context = {
        "name": "Muhammad Rifky Padjri",
        "npm": "2506585800",
        "title_query": title_query,
        "form": ProjectForm(),
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
    projects = Project.objects.prefetch_related('starred_by').all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    # Konstruksi data JSON secara manual agar bisa menyisipkan logika Star
    data = []
    for project in projects:
        starred_users = project.starred_by.all()
        is_starred = request.user in starred_users if request.user.is_authenticated else False
        starred_by_names = ", ".join([u.username for u in starred_users])

        data.append({
            "pk": str(project.id),
            "fields": {
                "title": project.title,
                "description": project.description,
                "thumbnail": project.thumbnail,
                "star_count": starred_users.count(),
                "is_starred": is_starred,
                "starred_by_names": starred_by_names,
            }
        })

    return JsonResponse(data, safe=False)


def _get_experiences(query_params):
    experiences = Experience.objects.prefetch_related("starred_by").all()

    if "q" in query_params:
        query = query_params.get("q", "").strip()
        if query:
            experiences = experiences.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )
    else:
        # Preserve the previously supported title-only API filter.
        title_query = query_params.get("title", "").strip()
        if title_query:
            experiences = experiences.filter(title__icontains=title_query)

    return experiences


def _serialize_experience(experience, user):
    starred_users = list(experience.starred_by.all())
    return {
        "model": "main.experience",
        "pk": str(experience.id),
        "fields": {
            "title": experience.title,
            "description": experience.description,
            "category": experience.category,
            "category_display": experience.get_category_display(),
            "thumbnail": experience.thumbnail,
            "started_at": experience.started_at,
            "ended_at": experience.ended_at,
            "is_ongoing": experience.is_ongoing,
            "star_count": len(starred_users),
            "is_starred": user.is_authenticated and user in starred_users,
        },
    }


def get_experiences_json(request):
    experiences = _get_experiences(request.GET)
    data = [_serialize_experience(experience, request.user) for experience in experiences]
    return JsonResponse(data, safe=False)


def show_projects(request):
    title_query = request.GET.get("title", "").strip()

    context = {
        "name": "Muhammad Rifky Padjri",
        "title_query": title_query,
    }
    return render(request, "project.html", context)


@require_POST
def create_experience_ajax(request):
    if not can_create_content(request.user):
        return JsonResponse(
            {
                "success": False,
                "message": "Hanya pemilik portofolio yang dapat menambahkan pengalaman.",
            },
            status=403,
        )

    form = ExperienceForm(request.POST)
    if not form.is_valid():
        return JsonResponse(
            {"success": False, "errors": form.errors.get_json_data()}, status=400
        )

    experience = form.save()
    return JsonResponse(
        {
            "success": True,
            "message": "Pengalaman berhasil ditambahkan.",
            "pk": str(experience.pk),
        },
        status=201,
    )


@require_POST
def create_project_ajax(request):
    if not request.user.is_superuser:
        return JsonResponse(
            {"message": "Hanya pemilik portofolio yang dapat menambahkan proyek."},
            status=403,
        )

    form = ProjectForm(request.POST)
    if form.is_valid():
        project = form.save()
        return JsonResponse(
            {"message": "Proyek berhasil ditambahkan.", "pk": str(project.id)},
            status=201,
        )
    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)

@superuser_delete_required
@require_POST
def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    project.delete()
    messages.success(request, "Project berhasil dihapus!")
    return redirect("main:show_project")


@superuser_delete_required
@require_POST
def delete_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)

    experience.delete()
    messages.success(request, "Pengalaman berhasil dihapus!")
    return redirect("main:show_experience")


def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat. Silakan login.")
        return redirect("main:login")

    context = {
        "name": "Muhammad Rifky Padjri",
        "form": form,
    }
    return render(request, "register.html", context)

def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)
    
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        next_url = request.POST.get("next", "")
        if next_url and url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            response = redirect(next_url)
        else:
            response = redirect("main:show_main")
        response.set_cookie('last_login', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return response

    context = {
        "name": "Muhammad Rifky Padjri",
        "form": form,
        "next": request.POST.get("next", request.GET.get("next", "")),
    }
    return render(request, "login.html", context)

@require_POST
def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie('last_login')
    return response

@login_required(login_url="main:login")
@require_POST
def toggle_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if project.starred_by.filter(pk=request.user.pk).exists():
        project.starred_by.remove(request.user)
    else:
        project.starred_by.add(request.user)

    return redirect("main:show_project")
