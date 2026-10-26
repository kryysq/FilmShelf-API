from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Director, Genre, Movie

class FilmShelfAPITests(APITestCase):
    def setUp(self):
        #початкові тестові дані
        self.director = Director.objects.create(name="Christopher Nolan", bio="Famous director")
        self.genre = Genre.objects.create(name="Sci-Fi")
        self.movie = Movie.objects.create(
            title="Inception",
            director=self.director,
            genre=self.genre,
            year=2010,
            rating=8.8
        )
        
        self.movies_url = reverse('movie-list')
        self.director_detail_url = reverse('director-detail', args=[self.director.id])

    def test_get_movies_list(self):
    
        response = self.client.get(self.movies_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Inception")

    def test_create_movie(self):
        data = {
            "title": "Interstellar",
            "director": self.director.id,
            "genre": self.genre.id,
            "year": 2014,
            "rating": 8.6
        }
        response = self.client.post(self.movies_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Movie.objects.count(), 2)

    def test_delete_director_with_movies_conflict(self):
        #очікуємо 409
        response = self.client.delete(self.director_detail_url)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        #перевіряєм чи режисер не видалився з бази
        self.assertTrue(Director.objects.filter(id=self.director.id).exists())
