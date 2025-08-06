from django.test import TestCase
from django.urls import reverse
from core.models import User
from .models import Artwork, Artist, Collection

class ArtworksViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.artist = Artist.objects.create(name='Test Artist')
        self.collection = Collection.objects.create(user=self.user, name='Ma Collection')
        self.artwork = Artwork.objects.create(title='Mona Lisa', user=self.user)
        self.artwork.artists.add(self.artist)
        self.artwork.collections.add(self.collection)

    def test_artwork_list_view(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('artworks:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mona Lisa')
        self.assertTemplateUsed(response, 'artworks/artwork_list.html')

    def test_artwork_detail_view(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('artworks:detail', args=[self.artwork.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mona Lisa')
        self.assertContains(response, 'Test Artist')

    def test_artwork_create_view(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('artworks:create'), {
            'title': 'La Cène',
            'creation_year': 1498,
            'artists': [self.artist.pk],
            'user': self.user.pk
        })
        # Since we are not passing all required form data, we expect a redirect or error
        # A full test would require mocking the entire formset for photos.
        # Here we just check if a new artwork has been created.
        self.assertTrue(Artwork.objects.filter(title='La Cène').exists())