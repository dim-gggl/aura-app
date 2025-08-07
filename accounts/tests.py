from django.test import TestCase
from django.urls import reverse
from core.models import User, UserProfile

class AccountsViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_profile_view_authenticated(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')

    def test_profile_view_unauthenticated(self):
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302) # Redirects to login
        self.assertRedirects(response, '/accounts/login/?next=/accounts/profile/')

    def test_user_profile_creation(self):
        # A profile should be created automatically by the signal
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, UserProfile)