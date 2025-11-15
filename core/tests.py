from django.test import TestCase
from django.urls import reverse

from .models import User


class CoreViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")

    def test_home_view_unauthenticated(self):
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/home.html")

    def test_home_view_authenticated_redirects(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("core:dashboard"))

    def test_dashboard_view(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(reverse("core:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tableau de bord")
        self.assertTemplateUsed(response, "core/dashboard.html")
