from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Achievement, Experience, Project
from main.permissions import (
    can_create_content,
    can_delete_content,
    can_update_content,
    is_editor,
)


class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="part-time",
            thumbnail="https://example.com/experience.jpg",
        )
        self.project = Project.objects.create(
            title="FoundrOS",
            description="Supplier, inventory, and payment automation.",
            thumbnail="https://example.com/project.png",
        )
        self.achievement = Achievement.objects.create(
            name="Datavidia Finalist",
            description="Built predictive models for air pollution patterns.",
            year=2024,
            level="national",
            thumbnail="https://example.com/achievement.png",
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertContains(response, "Muhammad Rifky Padjri")
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')
        self.assertContains(response, f'href="{reverse("main:show_achievement")}"')
        self.assertContains(response, f'href="{reverse("main:show_project")}"')
        self.assertNotContains(response, self.experience.title)
        self.assertNotContains(response, self.achievement.name)

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Asisten Dosen PBP")
        self.assertEqual(self.experience.category, "part-time")
        self.assertTrue(self.experience.is_ongoing)

    def test_project_model(self):
        self.assertEqual(str(self.project), "FoundrOS")
        self.assertEqual(
            self.project.description,
            "Supplier, inventory, and payment automation.",
        )

    def test_achievement_model(self):
        self.assertEqual(str(self.achievement), "Datavidia Finalist")
        self.assertEqual(self.achievement.year, 2024)
        self.assertEqual(self.achievement.level, "national")
        self.assertTrue(self.achievement.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, "Part-Time")
        self.assertContains(response, "Sedang berlangsung")
        self.assertContains(response, self.experience.thumbnail)
        self.assertContains(response, f'href="{reverse("main:show_main")}"')
        self.assertNotContains(response, "Belum ada pengalaman yang ditambahkan.")

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, "Belum ada pengalaman yang ditambahkan.")
        self.assertNotContains(response, "Asisten Dosen PBP")

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Selesai")
        self.assertNotContains(response, "Sedang berlangsung")

    def test_get_experiences_json(self):
        response = self.client.get(reverse("main:get_experiences_json"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["fields"]["title"], self.experience.title)

    def test_delete_experience_requires_authentication(self):
        response = self.client.post(
            reverse("main:delete_experience", args=[self.experience.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("main:login")))
        self.assertTrue(Experience.objects.filter(pk=self.experience.id).exists())

    def test_delete_experience_requires_post(self):
        superuser = get_user_model().objects.create_superuser(
            username="delete-test-admin", password="test-password"
        )
        self.client.force_login(superuser)
        response = self.client.get(
            reverse("main:delete_experience", args=[self.experience.id])
        )

        self.assertRedirects(response, reverse("main:show_experience"))
        self.assertTrue(Experience.objects.filter(pk=self.experience.id).exists())

    def test_project_page(self):
        response = self.client.get(reverse("main:show_project"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "project.html")
        self.assertContains(response, self.project.title)
        self.assertContains(response, self.project.description)
        self.assertContains(response, self.project.thumbnail)
        self.assertContains(response, f'href="{reverse("main:show_main")}"')
        self.assertNotContains(response, "Belum ada project yang ditambahkan.")

    def test_empty_project_page(self):
        Project.objects.all().delete()
        response = self.client.get(reverse("main:show_project"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "project.html")
        self.assertContains(response, "Belum ada proyek yang ditambahkan.")
        self.assertNotContains(response, "FoundrOS")

    def test_achievement_page(self):
        response = self.client.get(reverse("main:show_achievement"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "achievement.html")
        self.assertContains(response, self.achievement.name)
        self.assertContains(response, self.achievement.description)
        self.assertContains(response, self.achievement.year)
        self.assertContains(response, self.achievement.level)
        self.assertContains(response, self.achievement.thumbnail)
        self.assertContains(response, f'href="{reverse("main:show_main")}"')
        self.assertNotContains(response, "Belum ada prestasi yang ditambahkan.")

    def test_empty_achievement_page(self):
        Achievement.objects.all().delete()
        response = self.client.get(reverse("main:show_achievement"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "achievement.html")
        self.assertContains(response, "Belum ada prestasi yang ditambahkan.")
        self.assertNotContains(response, "Datavidia Finalist")


class AuthorizationTest(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.regular_user = user_model.objects.create_user(
            username="regular", password="test-password"
        )
        self.editor = user_model.objects.create_user(
            username="editor", password="test-password"
        )
        self.editor.groups.add(Group.objects.create(name="Editor"))
        self.superuser = user_model.objects.create_superuser(
            username="admin", password="test-password"
        )
        self.project = Project.objects.create(
            title="Authorization Test",
            description="Project used to test role restrictions.",
        )

    def test_role_helpers(self):
        self.assertFalse(is_editor(self.regular_user))
        self.assertTrue(is_editor(self.editor))

        self.assertFalse(can_create_content(self.regular_user))
        self.assertFalse(can_create_content(self.editor))
        self.assertTrue(can_create_content(self.superuser))

        self.assertFalse(can_update_content(self.regular_user))
        self.assertTrue(can_update_content(self.editor))
        self.assertTrue(can_update_content(self.superuser))

        self.assertFalse(can_delete_content(self.regular_user))
        self.assertFalse(can_delete_content(self.editor))
        self.assertTrue(can_delete_content(self.superuser))

    def test_regular_user_and_editor_cannot_create(self):
        create_url = reverse("main:create_project")

        for user in (self.regular_user, self.editor):
            self.client.force_login(user)
            self.assertEqual(self.client.get(create_url).status_code, 403)

    def test_regular_user_and_editor_cannot_delete(self):
        delete_url = reverse("main:delete_project", args=[self.project.id])

        for user in (self.regular_user, self.editor):
            self.client.force_login(user)
            self.assertEqual(self.client.post(delete_url).status_code, 403)

        self.assertTrue(Project.objects.filter(pk=self.project.id).exists())

    def test_superuser_can_create_and_delete(self):
        self.client.force_login(self.superuser)

        create_response = self.client.post(
            reverse("main:create_project"),
            {
                "title": "Created by admin",
                "description": "Allowed operation",
                "thumbnail": "",
            },
        )
        self.assertRedirects(create_response, reverse("main:show_project"))

        delete_response = self.client.post(
            reverse("main:delete_project", args=[self.project.id])
        )
        self.assertRedirects(delete_response, reverse("main:show_project"))
        self.assertFalse(Project.objects.filter(pk=self.project.id).exists())
