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
        self.assertContains(response, reverse("main:get_experiences_json"))
        self.assertContains(response, "Memuat pengalaman...")
        self.assertContains(response, "experience.js")
        self.assertNotIn("experience_list", response.context)
        self.assertNotContains(response, self.experience.title)
        self.assertNotContains(response, self.experience.description)
        self.assertNotContains(response, self.experience.thumbnail)
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

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
        response = self.client.get(reverse("main:get_experiences_json"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertFalse(response.json()[0]["fields"]["is_ongoing"])

    def test_get_experiences_json(self):
        response = self.client.get(reverse("main:get_experiences_json"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["fields"]["title"], self.experience.title)
        self.assertEqual(
            set(response.json()[0]["fields"]),
            {
                "title",
                "description",
                "category",
                "thumbnail",
                "started_at",
                "ended_at",
                "category_display",
                "is_ongoing",
                "star_count",
                "is_starred",
            },
        )

    def test_projects_json_includes_star_status_without_authentication_data(self):
        user = get_user_model().objects.create_user(
            username="json-user",
            password="secret-test-password",
            email="json-user@example.com",
        )
        self.project.starred_by.add(user)
        self.client.force_login(user)

        response = self.client.get(reverse("main:get_projects_json"))
        payload = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual(len(payload), 1)
        self.assertEqual(
            set(payload[0]["fields"]),
            {
                "title", "description", "thumbnail", "star_count",
                "is_starred", "starred_by_names",
            },
        )
        self.assertEqual(payload[0]["fields"]["star_count"], 1)
        self.assertTrue(payload[0]["fields"]["is_starred"])
        self.assertEqual(payload[0]["fields"]["starred_by_names"], "json-user")
        response_text = response.content.decode("utf-8")
        for sensitive_value in (
            "json-user@example.com",
            "secret-test-password",
            "session",
        ):
            with self.subTest(sensitive_value=sensitive_value):
                self.assertNotIn(sensitive_value, response_text)

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
        self.assertContains(response, reverse("main:get_projects_json"))
        self.assertContains(response, 'id="grid"')
        self.assertContains(response, "fetchProjects(searchInput.value.trim())")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')
        self.assertNotContains(response, "Belum ada project yang ditambahkan.")

    def test_empty_project_page(self):
        Project.objects.all().delete()
        response = self.client.get(reverse("main:show_project"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "project.html")
        self.assertContains(response, "Belum ada proyek yang ditambahkan atau ditemukan.")
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


class ExperienceJsonTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Research Assistant", description="Research work", category="research"
        )
        self.user = get_user_model().objects.create_user(
            username="experience-reader", email="private@example.com"
        )
        self.other_user = get_user_model().objects.create_user(username="other-reader")
        self.experience.starred_by.add(self.other_user)
        self.url = reverse("main:get_experiences_json")

    def get_fields(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        item = response.json()[0]
        self.assertEqual(item["pk"], str(self.experience.pk))
        self.assertEqual(item["model"], "main.experience")
        self.assertNotIn("private@example.com", response.content.decode())
        self.assertNotIn("starred_by", item["fields"])
        return item["fields"]

    def test_anonymous_user_sees_total_without_personal_star(self):
        fields = self.get_fields()
        self.assertEqual(fields["star_count"], 1)
        self.assertFalse(fields["is_starred"])
        self.assertEqual(fields["category_display"], "Research")
        self.assertTrue(fields["is_ongoing"])
        self.assertIsNone(fields["ended_at"])
        self.assertIsNone(fields["thumbnail"])
        self.assertIsInstance(fields["started_at"], str)

    def test_authenticated_user_without_star(self):
        self.client.force_login(self.user)
        fields = self.get_fields()
        self.assertEqual(fields["star_count"], 1)
        self.assertFalse(fields["is_starred"])

    def test_current_user_star_is_specific_to_experience(self):
        self.client.force_login(self.user)
        self.experience.starred_by.add(self.user)
        self.experience.starred_by.add(self.user)
        fields = self.get_fields()
        self.assertEqual(fields["star_count"], 2)
        self.assertTrue(fields["is_starred"])
        self.experience.starred_by.remove(self.user)
        self.assertFalse(self.get_fields()["is_starred"])

    def test_completed_experience_and_existing_title_filter(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        fields = self.get_fields()
        self.assertFalse(fields["is_ongoing"])
        self.assertIsInstance(fields["ended_at"], str)
        self.assertEqual(len(self.client.get(self.url, {"title": " research "}).json()), 1)
        self.assertEqual(self.client.get(self.url, {"title": "missing"}).json(), [])

    def test_empty_list(self):
        Experience.objects.all().delete()
        self.assertEqual(self.client.get(self.url).json(), [])

    def test_anonymous_search_matches_title_or_description(self):
        other = Experience.objects.create(
            title="Intern", description="Operations work"
        )
        Experience.objects.create(title="Volunteer", description="Community event")
        title_matches = self.client.get(self.url, {"q": " RESEARCH "}).json()
        self.assertEqual([item["pk"] for item in title_matches], [str(self.experience.pk)])
        description_matches = self.client.get(self.url, {"q": "operations"}).json()
        self.assertEqual([item["pk"] for item in description_matches], [str(other.pk)])
        both_matches = self.client.get(self.url, {"q": "work"}).json()
        self.assertEqual({item["pk"] for item in both_matches}, {str(other.pk), str(self.experience.pk)})
        self.assertEqual(len(self.client.get(self.url, {"q": "research"}).json()), 1)
        self.assertEqual(self.client.get(self.url, {"q": "missing"}).json(), [])

    def test_empty_search_restores_all_experiences(self):
        Experience.objects.create(title="Intern", description="Operations")
        for query in ("", "   "):
            with self.subTest(query=query):
                self.assertEqual(len(self.client.get(self.url, {"q": query}).json()), 2)

    def test_search_preserves_personal_star_state(self):
        self.client.force_login(self.user)
        self.experience.starred_by.add(self.user)
        fields = self.client.get(self.url, {"q": "Research"}).json()[0]["fields"]
        self.assertEqual(fields["star_count"], 2)
        self.assertTrue(fields["is_starred"])

    def test_prefetch_avoids_per_item_star_queries(self):
        Experience.objects.create(title="Intern", description="Internship")
        with self.assertNumQueries(2):
            self.client.get(self.url)


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
            )

            for response, action_url, should_be_visible in assertions:
                with self.subTest(role=role, url=action_url):
                    if should_be_visible:
                        self.assertContains(response, action_url)
                    else:
                        self.assertNotContains(response, action_url)

            self.assertContains(
                project_response,
                f'const CAN_UPDATE_CONTENT = "{str(can_update).lower()}"',
            )
            self.assertContains(
                project_response,
                f'const IS_SUPERUSER = "{str(can_delete).lower()}"',
            )

            self.assertContains(
                experience_response,
                f'data-can-edit="{str(can_update).lower()}"',
            )
            self.assertContains(
                experience_response,
                f'data-can-delete="{str(can_delete).lower()}"',
            )
            self.assertNotContains(experience_response, self.experience.title)

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

    def test_every_authenticated_role_can_star(self):
        for user in (self.regular_user, self.editor, self.superuser):
            self.client.force_login(user)
            response = self.client.post(
                reverse("main:toggle_star", args=[self.project.id])
            )

            with self.subTest(user=user.username):
                self.assertRedirects(response, reverse("main:show_project"))
                self.assertTrue(
                    self.project.starred_by.filter(pk=user.pk).exists()
                )

        self.assertEqual(self.project.starred_by.count(), 3)

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
        data = self.client.get(reverse("main:get_projects_json")).json()

        self.assertContains(response, 'const IS_AUTHENTICATED = "false"')
        self.assertContains(response, "Login untuk Star")
        self.assertEqual(data[0]["fields"]["star_count"], 1)
        self.assertFalse(data[0]["fields"]["is_starred"])
        self.assertNotContains(response, f'action="{self.toggle_url}"')

    def test_authenticated_user_sees_post_form_csrf_and_star_status(self):
        self.client.force_login(self.user)

        unstarred_response = self.client.get(reverse("main:show_project"))
        unstarred_data = self.client.get(reverse("main:get_projects_json")).json()
        self.assertContains(unstarred_response, 'const IS_AUTHENTICATED = "true"')
        self.assertContains(unstarred_response, 'name="csrfmiddlewaretoken"')
        self.assertFalse(unstarred_data[0]["fields"]["is_starred"])
        self.assertEqual(unstarred_data[0]["fields"]["star_count"], 0)

        self.project.starred_by.add(self.user)
        starred_data = self.client.get(reverse("main:get_projects_json")).json()
        self.assertTrue(starred_data[0]["fields"]["is_starred"])
        self.assertEqual(starred_data[0]["fields"]["star_count"], 1)

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
                self.assertContains(response, 'const IS_AUTHENTICATED = "true"')
                self.assertContains(response, 'name="csrfmiddlewaretoken"')


class ProjectAjaxCreateTest(TestCase):
    def setUp(self):
        self.url = reverse("main:create_project_ajax")
        self.admin = get_user_model().objects.create_superuser(
            username="ajax-admin", password="test-password"
        )

    def test_only_superuser_can_create(self):
        payload = {"title": "New Project", "description": "Description"}
        self.assertEqual(self.client.get(self.url).status_code, 405)
        self.assertEqual(self.client.post(self.url, payload).status_code, 403)
        user = get_user_model().objects.create_user(username="ajax-user")
        self.client.force_login(user)
        self.assertEqual(self.client.post(self.url, payload).status_code, 403)
        self.assertFalse(Project.objects.exists())

    def test_create_validates_and_strips_html(self):
        self.client.force_login(self.admin)
        invalid = self.client.post(
            self.url,
            {"title": '<img src="x">', "description": "Description"},
        )
        self.assertEqual(invalid.status_code, 400)
        self.assertIn("title", invalid.json()["errors"])
        self.assertFalse(Project.objects.exists())

        valid = self.client.post(
            self.url,
            {"title": "Hello <b>world</b>", "description": "A <i>project</i>"},
        )
        self.assertEqual(valid.status_code, 201)
        project = Project.objects.get(pk=valid.json()["pk"])
        self.assertEqual(project.title, "Hello world")
        self.assertEqual(project.description, "A project")

    def test_csrf_is_required(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.admin)
        response = csrf_client.post(
            self.url, {"title": "New Project", "description": "Description"}
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Project.objects.exists())


class ExperienceAjaxCreateTest(TestCase):
    def setUp(self):
        self.url = reverse("main:create_experience_ajax")
        self.admin = get_user_model().objects.create_superuser(username="experience-admin")
        self.payload = {
            "title": "Research Assistant",
            "description": "Research & development",
            "category": "research",
            "thumbnail": "",
            "ended_at": "",
        }

    def test_authorized_valid_request_creates_experience(self):
        self.client.force_login(self.admin)
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response["Content-Type"], "application/json")
        result = response.json()
        self.assertTrue(result["success"])
        self.assertTrue(result["message"])
        self.assertEqual(Experience.objects.count(), 1)
        experience = Experience.objects.get(pk=result["pk"])
        self.assertEqual(experience.title, self.payload["title"])
        self.assertEqual(experience.description, self.payload["description"])
        self.assertEqual(experience.category, "research")
        self.assertTrue(experience.is_ongoing)
        self.assertEqual(experience.starred_by.count(), 0)
        items = self.client.get(reverse("main:get_experiences_json")).json()
        self.assertEqual(items[0]["pk"], result["pk"])

    def test_invalid_request_returns_field_errors_without_saving(self):
        self.client.force_login(self.admin)
        invalid_payloads = (
            ({}, {"title", "description", "category"}),
            ({**self.payload, "title": " "}, {"title"}),
            ({**self.payload, "title": "x" * 256}, {"title"}),
            ({**self.payload, "category": "invalid"}, {"category"}),
            ({**self.payload, "thumbnail": "javascript:alert(1)"}, {"thumbnail"}),
            ({**self.payload, "ended_at": "not-a-date"}, {"ended_at"}),
        )
        for payload, expected_fields in invalid_payloads:
            with self.subTest(fields=expected_fields):
                response = self.client.post(self.url, payload)
                self.assertEqual(response.status_code, 400)
                result = response.json()
                self.assertFalse(result["success"])
                self.assertTrue(expected_fields.issubset(result["errors"]))
                for field in expected_fields:
                    self.assertTrue(result["errors"][field][0]["message"])
                    self.assertTrue(result["errors"][field][0]["code"])
                self.assertFalse(Experience.objects.exists())

    def test_anonymous_and_unauthorized_roles_cannot_create(self):
        regular = get_user_model().objects.create_user(username="experience-regular")
        editor = get_user_model().objects.create_user(username="experience-editor")
        editor.groups.add(Group.objects.create(name="Editor"))
        staff = get_user_model().objects.create_user(username="experience-staff", is_staff=True)
        for user in (None, regular, editor, staff):
            with self.subTest(user=user.username if user else "anonymous"):
                self.client.logout()
                if user:
                    self.client.force_login(user)
                response = self.client.post(self.url, {**self.payload, "is_superuser": "true"})
                self.assertEqual(response.status_code, 403)
                self.assertFalse(response.json()["success"])
                self.assertTrue(response.json()["message"])
                self.assertNotIn("Location", response)
                self.assertFalse(Experience.objects.exists())

    def test_endpoint_is_post_only(self):
        self.client.force_login(self.admin)
        for method in ("get", "put", "patch", "delete"):
            with self.subTest(method=method):
                response = getattr(self.client, method)(self.url)
                self.assertEqual(response.status_code, 405)
                self.assertEqual(response["Allow"], "POST")
                self.assertFalse(Experience.objects.exists())

    def test_csrf_is_required_and_valid_token_allows_creation(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.admin)
        self.assertEqual(csrf_client.post(self.url, self.payload).status_code, 403)
        self.assertFalse(Experience.objects.exists())
        csrf_client.get(reverse("main:show_experience"))
        token = csrf_client.cookies["csrftoken"].value
        response = csrf_client.post(self.url, self.payload, HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json()["success"])


class SessionSecurityTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="session-user", password="test-password"
        )

    def test_logout_is_post_only_and_form_contains_csrf_token(self):
        self.client.force_login(self.user)
        logout_url = reverse("main:logout")

        page_response = self.client.get(reverse("main:show_main"))
        self.assertContains(page_response, 'method="post"')
        self.assertContains(page_response, f'action="{logout_url}"')
        self.assertContains(page_response, 'name="csrfmiddlewaretoken"')

        get_response = self.client.get(logout_url)
        self.assertEqual(get_response.status_code, 405)
        self.assertIn("_auth_user_id", self.client.session)

        post_response = self.client.post(logout_url)
        self.assertRedirects(post_response, reverse("main:show_main"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_rejects_post_without_csrf_token(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.user)

        response = csrf_client.post(reverse("main:logout"))

        self.assertEqual(response.status_code, 403)
        self.assertIn("_auth_user_id", csrf_client.session)
