from django.test import TestCase
from django.urls import reverse

from core.models import User

from .models import Contact


class ContactsViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.contact = Contact.objects.create(
            user=self.user,
            name="Galerie Durand-Ruel",
            contact_type="galerie",
            email="contact@durand-ruel.fr",
        )

    def test_contact_list_view(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(reverse("contacts:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Galerie Durand-Ruel")
        self.assertTemplateUsed(response, "contacts/contact_list.html")

    def test_contact_detail_view(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(reverse("contacts:detail", args=[self.contact.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "contact@durand-ruel.fr")
