import uuid

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import Client, TestCase
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

        self.assertEqual(response.status_code, 405)
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
        self.experience = Experience.objects.create(
            title="Authorization Experience",
            description="Experience used to test role restrictions.",
            category="full-time",
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

    def test_admin_uses_the_same_role_policy(self):
        model_admin = admin.site._registry[Project]

        for user in (self.regular_user, self.editor, self.superuser):
            request = type("Request", (), {"user": user})()
            with self.subTest(user=user.username):
                self.assertEqual(
                    model_admin.has_add_permission(request),
                    user.is_superuser,
                )
                self.assertEqual(
                    model_admin.has_change_permission(request),
                    user in (self.editor, self.superuser),
                )
                self.assertEqual(
                    model_admin.has_delete_permission(request),
                    user.is_superuser,
                )

    def test_regular_user_and_editor_cannot_create(self):
        for user in (self.regular_user, self.editor):
            self.client.force_login(user)
            for create_url in (
                reverse("main:create_project"),
                reverse("main:create_experience"),
            ):
                with self.subTest(user=user.username, url=create_url):
                    self.assertEqual(self.client.get(create_url).status_code, 403)

    def test_guest_is_redirected_from_all_mutating_views(self):
        protected_requests = (
            ("get", reverse("main:create_project")),
            ("get", reverse("main:create_experience")),
            ("get", reverse("main:update_project", args=[self.project.id])),
            ("get", reverse("main:update_experience", args=[self.experience.id])),
            ("post", reverse("main:delete_project", args=[self.project.id])),
            ("post", reverse("main:delete_experience", args=[self.experience.id])),
        )

        for method, url in protected_requests:
            with self.subTest(method=method, url=url):
                response = getattr(self.client, method)(url)
                self.assertEqual(response.status_code, 302)
                self.assertTrue(response.url.startswith(reverse("main:login")))

    def test_read_views_are_public_for_every_role(self):
        read_urls = (
            reverse("main:show_project"),
            reverse("main:show_experience"),
            reverse("main:show_achievement"),
            reverse("main:get_projects_json"),
            reverse("main:get_experiences_json"),
        )

        for user in (None, self.regular_user, self.editor, self.superuser):
            self.client.logout()
            if user is not None:
                self.client.force_login(user)
            for url in read_urls:
                with self.subTest(
                    user=user.username if user else "guest", url=url
                ):
                    self.assertEqual(self.client.get(url).status_code, 200)

    def test_crud_actions_are_rendered_for_the_correct_roles(self):
        roles = (
            ("guest", None, False, False, False),
            ("regular", self.regular_user, False, False, False),
            ("editor", self.editor, False, True, False),
            ("superuser", self.superuser, True, True, True),
        )

        for role, user, can_create, can_update, can_delete in roles:
            self.client.logout()
            if user is not None:
                self.client.force_login(user)

            project_response = self.client.get(reverse("main:show_project"))
            experience_response = self.client.get(reverse("main:show_experience"))

            assertions = (
                (
                    project_response,
                    reverse("main:create_project"),
                    can_create,
                ),
                (
                    experience_response,
                    reverse("main:create_experience"),
                    can_create,
                ),
                (
                    project_response,
                    reverse("main:update_project", args=[self.project.id]),
                    can_update,
                ),
                (
                    experience_response,
                    reverse(
                        "main:update_experience", args=[self.experience.id]
                    ),
                    can_update,
                ),
                (
                    project_response,
                    reverse("main:delete_project", args=[self.project.id]),
                    can_delete,
                ),
                (
                    experience_response,
                    reverse(
                        "main:delete_experience", args=[self.experience.id]
                    ),
                    can_delete,
                ),
            )

            for response, action_url, should_be_visible in assertions:
                with self.subTest(role=role, url=action_url):
                    if should_be_visible:
                        self.assertContains(response, action_url)
                    else:
                        self.assertNotContains(response, action_url)

            with self.subTest(role=role, container="experience-actions"):
                if can_update or can_delete:
                    self.assertContains(experience_response, "experience-actions")
                else:
                    self.assertNotContains(
                        experience_response, "experience-actions"
                    )

    def test_regular_user_cannot_update(self):
        self.client.force_login(self.regular_user)

        for update_url in (
            reverse("main:update_project", args=[self.project.id]),
            reverse("main:update_experience", args=[self.experience.id]),
        ):
            with self.subTest(url=update_url):
                self.assertEqual(self.client.get(update_url).status_code, 403)

    def test_editor_and_superuser_can_update(self):
        for user in (self.editor, self.superuser):
            self.client.force_login(user)
            project_response = self.client.post(
                reverse("main:update_project", args=[self.project.id]),
                {
                    "title": f"Updated by {user.username}",
                    "description": "Allowed update",
                    "thumbnail": "",
                },
            )
            experience_response = self.client.post(
                reverse("main:update_experience", args=[self.experience.id]),
                {
                    "title": f"Experience updated by {user.username}",
                    "description": "Allowed update",
                    "category": "full-time",
                    "ended_at": "",
                    "thumbnail": "",
                },
            )

            with self.subTest(user=user.username):
                self.assertRedirects(
                    project_response, reverse("main:show_project")
                )
                self.assertRedirects(
                    experience_response, reverse("main:show_experience")
                )
                self.project.refresh_from_db()
                self.experience.refresh_from_db()
                self.assertEqual(self.project.title, f"Updated by {user.username}")
                self.assertEqual(
                    self.experience.title,
                    f"Experience updated by {user.username}",
                )

    def test_regular_user_and_editor_cannot_delete(self):
        for user in (self.regular_user, self.editor):
            self.client.force_login(user)
            for delete_url in (
                reverse("main:delete_project", args=[self.project.id]),
                reverse("main:delete_experience", args=[self.experience.id]),
            ):
                with self.subTest(user=user.username, url=delete_url):
                    self.assertEqual(self.client.post(delete_url).status_code, 403)

        self.assertTrue(Project.objects.filter(pk=self.project.id).exists())
        self.assertTrue(Experience.objects.filter(pk=self.experience.id).exists())

    def test_superuser_can_create_and_delete(self):
        self.client.force_login(self.superuser)

        project_create_response = self.client.post(
            reverse("main:create_project"),
            {
                "title": "Created by admin",
                "description": "Allowed operation",
                "thumbnail": "",
            },
        )
        experience_create_response = self.client.post(
            reverse("main:create_experience"),
            {
                "title": "Created by admin",
                "description": "Allowed operation",
                "category": "full-time",
                "ended_at": "",
                "thumbnail": "",
            },
        )
        self.assertRedirects(
            project_create_response, reverse("main:show_project")
        )
        self.assertRedirects(
            experience_create_response, reverse("main:show_experience")
        )

        project_delete_response = self.client.post(
            reverse("main:delete_project", args=[self.project.id])
        )
        experience_delete_response = self.client.post(
            reverse("main:delete_experience", args=[self.experience.id])
        )
        self.assertRedirects(
            project_delete_response, reverse("main:show_project")
        )
        self.assertRedirects(
            experience_delete_response, reverse("main:show_experience")
        )
        self.assertFalse(Project.objects.filter(pk=self.project.id).exists())
        self.assertFalse(Experience.objects.filter(pk=self.experience.id).exists())

    def test_login_preserves_safe_next_url(self):
        update_url = reverse("main:update_project", args=[self.project.id])
        response = self.client.post(
            reverse("main:login"),
            {
                "username": self.editor.username,
                "password": "test-password",
                "next": update_url,
            },
        )

        self.assertRedirects(response, update_url, fetch_redirect_response=False)
        self.assertEqual(self.client.get(update_url).status_code, 200)

    def test_login_rejects_external_next_url(self):
        response = self.client.post(
            reverse("main:login"),
            {
                "username": self.regular_user.username,
                "password": "test-password",
                "next": "https://example.com/steal-session",
            },
        )

        self.assertRedirects(response, reverse("main:show_main"))


class ProjectStarTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="star-user", password="test-password"
        )
        self.project = Project.objects.create(
            title="Star Test",
            description="Project used to test starring.",
        )
        self.toggle_url = reverse("main:toggle_star", args=[self.project.id])

    def test_authenticated_user_can_toggle_star(self):
        self.client.force_login(self.user)

        add_response = self.client.post(self.toggle_url)
        self.assertRedirects(add_response, reverse("main:show_project"))
        self.assertTrue(self.project.starred_by.filter(pk=self.user.pk).exists())
        self.assertEqual(self.project.starred_by.count(), 1)

        remove_response = self.client.post(self.toggle_url)
        self.assertRedirects(remove_response, reverse("main:show_project"))
        self.assertFalse(self.project.starred_by.filter(pk=self.user.pk).exists())
        self.assertEqual(self.project.starred_by.count(), 0)

    def test_guest_is_redirected_to_login_without_changing_star(self):
        response = self.client.post(self.toggle_url)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("main:login")))
        self.assertFalse(self.project.starred_by.exists())

    def test_get_does_not_change_star(self):
        self.client.force_login(self.user)

        response = self.client.get(self.toggle_url)

        self.assertEqual(response.status_code, 405)
        self.assertFalse(self.project.starred_by.exists())

    def test_nonexistent_project_returns_404(self):
        self.client.force_login(self.user)
        missing_url = reverse("main:toggle_star", args=[uuid.uuid4()])

        response = self.client.post(missing_url)

        self.assertEqual(response.status_code, 404)

    def test_toggle_star_requires_csrf_token(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.user)

        response = csrf_client.post(self.toggle_url)

        self.assertEqual(response.status_code, 403)
        self.assertFalse(self.project.starred_by.exists())

    def test_guest_sees_star_count_and_login_link_instead_of_post_form(self):
        self.project.starred_by.add(self.user)

        response = self.client.get(reverse("main:show_project"))

        self.assertContains(
            response,
            f'href="{reverse("main:login")}?next=',
            html=False,
        )
        self.assertContains(response, "Login untuk Star")
        self.assertContains(response, '<span class="star-count">1</span>')
        self.assertNotContains(response, f'action="{self.toggle_url}"')

    def test_authenticated_user_sees_post_form_csrf_and_star_status(self):
        self.client.force_login(self.user)

        unstarred_response = self.client.get(reverse("main:show_project"))
        self.assertContains(unstarred_response, f'action="{self.toggle_url}"')
        self.assertContains(unstarred_response, 'name="csrfmiddlewaretoken"')
        self.assertContains(unstarred_response, 'aria-pressed="false"')
        self.assertContains(
            unstarred_response, '<span class="star-count">0</span>'
        )

        self.project.starred_by.add(self.user)
        starred_response = self.client.get(reverse("main:show_project"))
        self.assertContains(starred_response, 'aria-pressed="true"')
        self.assertContains(starred_response, "Unstar")
        self.assertContains(starred_response, '<span class="star-count">1</span>')

    def test_regular_editor_and_superuser_all_receive_star_form(self):
        editor = get_user_model().objects.create_user(username="star-editor")
        editor.groups.add(Group.objects.create(name="Editor"))
        superuser = get_user_model().objects.create_superuser(
            username="star-admin", password="test-password"
        )

        for user in (self.user, editor, superuser):
            self.client.force_login(user)
            response = self.client.get(reverse("main:show_project"))

            with self.subTest(user=user.username):
                self.assertContains(response, f'action="{self.toggle_url}"')
                self.assertContains(response, 'name="csrfmiddlewaretoken"')
