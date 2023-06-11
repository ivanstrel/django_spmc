from django.test import Client, TestCase
from django.urls import reverse

from ..users.models import User
from .models import Project, Scene


class HomeViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(name="testuser", email="testuser@example.com", password="testpass")
        self.project1 = Project.objects.create(name="Project 1", description="This is Project 1")
        self.project2 = Project.objects.create(name="Project 2", description="This is Project 2")
        self.scene1 = Scene.objects.create(
            proj_id=self.project1, name="Scene 1", description="This is Scene 1 of Project 1"
        )
        self.scene2 = Scene.objects.create(
            proj_id=self.project2, name="Scene 2", description="This is Scene 2 of Project 2"
        )

    def test_home_view_for_unauthenticated_users(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/home_non_auth.html")

    def test_home_view_for_authenticated_users(self):
        self.client.login(email="testuser@example.com", password="testpass")
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/home_auth.html")
        self.assertEqual(len(response.context["projects"]), 2)
        self.assertEqual(response.context["projects"][0]["name"], "Project 1")
        self.assertEqual(response.context["projects"][1]["description"], "This is Project 2")


class SelectProjViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(name="testuser", email="testuser@example.com", password="testpass")
        self.project = Project.objects.create(name="Test Project", description="This is a test project")
        self.scene = Scene.objects.create(proj_id=self.project, name="Test Scene", description="This is a test scene")

    def test_select_proj_with_post_request(self):
        # Login client
        self.client.login(email="testuser@example.com", password="testpass")
        # Set up request
        response = self.client.post(reverse("select_project"), {"proj_id": self.project.id})
        # Check that request.session has been updated correctly
        self.assertEqual(self.client.session["proj_id"], str(self.project.id))
        self.assertIsNone(self.client.session.get("scene_id"))
        # Check that the response is a redirect to the correct page
        self.assertRedirects(response, reverse("scene"))

    def test_select_proj_with_get_request(self):
        # Login client
        self.client.login(email="testuser@example.com", password="testpass")
        # Set up request
        response = self.client.get(reverse("select_project"))
        # Check that request.session has not been updated
        self.assertNotIn("proj_id", self.client.session)
        self.assertNotIn("scene_id", self.client.session)
        # Check that the response is a redirect to the correct page
        self.assertRedirects(response, reverse("home"))

    def test_select_proj_with_invalid_post_request(self):
        # Login client
        self.client.login(email="testuser@example.com", password="testpass")
        # Set up request with an invalid project id
        response = self.client.post(reverse("select_project"), {"proj_id": 10})
        # Check that request.session has not been updated
        self.assertNotIn("proj_id", self.client.session)
        self.assertNotIn("scene_id", self.client.session)
        # Check that the response is a redirect to the correct page
        self.assertRedirects(response, reverse("home"))


class SceneViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(name="testuser", email="testuser@example.com", password="testpass")
        self.project = Project.objects.create(name="Test Project", description="Test Description")
        self.scene1 = Scene.objects.create(proj_id=self.project, name="Scene 1", description="Scene 1 Description")
        self.scene2 = Scene.objects.create(proj_id=self.project, name="Scene 2", description="Scene 2 Description")

    def test_scene_view_with_no_proj_id_in_session_data(self):
        # Login client
        self.client.login(email="testuser@example.com", password="testpass")
        response = self.client.get(reverse("scene"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/scene.html")
        self.assertIsNone(response.context["proj"])
        self.assertIsNone(response.context["scenes"])

    def test_scene_view_with_proj_id_in_session_data(self):
        # Login client
        self.client.login(email="testuser@example.com", password="testpass")
        session = self.client.session
        session["proj_id"] = self.project.id
        session.save()
        response = self.client.get(reverse("scene"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/scene.html")
        self.assertEqual(response.context["proj"], self.project)
        self.assertQuerysetEqual(response.context["scenes"], [self.scene1, self.scene2], ordered=True)


class SelectSceneViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(name="testuser", email="testuser@example.com", password="testpass")
        # create a test project
        self.project = Project.objects.create(name="Test Project")
        # create test scenes related to the project
        self.scene1 = Scene.objects.create(proj_id=self.project, name="Test Scene 1")
        self.scene2 = Scene.objects.create(proj_id=self.project, name="Test Scene 2")

    def test_select_scene_with_valid_data(self):
        """
        Test that selecting a scene with valid data sets the session variable and redirects to classification page
        """
        # Login client
        self.client.login(email="testuser@example.com", password="testpass")
        response = self.client.post(reverse("select_scene"), {"proj_id": self.project.id, "scene_id": self.scene1.id})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("classification"))
        self.assertEqual(self.client.session["scene_id"], str(self.scene1.id))

    def test_select_scene_with_invalid_proj_id(self):
        """
        Test that selecting a scene with invalid project id redirects to home page
        """
        # Login client
        self.client.login(email="testuser@example.com", password="testpass")
        response = self.client.post(reverse("select_scene"), {"proj_id": "", "scene_id": self.scene1.id})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("home"))
        self.assertNotIn("scene_id", self.client.session)

    def test_select_scene_with_invalid_scene_id(self):
        """
        Test that selecting a scene with invalid scene id redirects to home page
        """
        # Login client
        self.client.login(email="testuser@example.com", password="testpass")
        response = self.client.post(reverse("select_scene"), {"proj_id": self.project.id, "scene_id": ""})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("home"))
        self.assertNotIn("scene_id", self.client.session)

    def test_select_scene_with_invalid_request_method(self):
        """
        Test that selecting a scene with invalid request method redirects to home page
        """
        # Login client
        self.client.login(email="testuser@example.com", password="testpass")
        response = self.client.get(reverse("select_scene"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("home"))
        self.assertNotIn("scene_id", self.client.session)
