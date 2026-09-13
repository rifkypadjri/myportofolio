from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Achievement, Experience, Project


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
        self.assertContains(response, "Belum ada project yang ditambahkan.")
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
