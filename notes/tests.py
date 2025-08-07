from django.test import TestCase
from django.urls import reverse
from core.models import User
from .models import Note

class NotesViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.note = Note.objects.create(
            user=self.user,
            title='Idées pour la collection',
            content='Acheter plus de cubistes.'
        )

    def test_note_list_view(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('notes:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Idées pour la collection')
        self.assertTemplateUsed(response, 'notes/note_list.html')

    def test_note_detail_view(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('notes:detail', args=[self.note.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Acheter plus de cubistes.')

