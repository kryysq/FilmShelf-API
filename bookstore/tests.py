from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Director, Genre, Movie


class FilmShelfAPITests(APITestCase):
    fixtures = ['test_movies.json']

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='StrongPassword123!'
        )
        self.movies_url = reverse('movie-list')
        self.movie_detail_url = reverse('movie-detail', args=[1])
        self.movie_not_found_url = reverse('movie-detail', args=[999])

        self.directors_url = reverse('director-list')
        self.director_detail_url = reverse('director-detail', args=[1])

        self.genres_url = reverse('genre-list')
        self.genre_detail_url = reverse('genre-detail', args=[1])

    #Публічний доступ та фільтрація фільмів (GET)

    def test_get_movies_list_from_fixture(self):
        response = self.client.get(self.movies_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[0]['title'], "Inception")
        self.assertEqual(response.data[0]['director_name'], "Christopher Nolan")
        self.assertEqual(response.data[0]['genre_name'], "Sci-Fi")

    def test_filter_movies_by_query_params(self):
        #Фільтр за назвою
        res_title = self.client.get(self.movies_url, {'title': 'Dune'})
        self.assertEqual(res_title.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_title.data), 1)
        self.assertEqual(res_title.data[0]['title'], "Dune")

        #Фільтр за жанром і тд
        res_combined = self.client.get(self.movies_url, {
            'genre': 1,
            'director': 1,
            'year': 2010,
            'min_rating': 8.5,
        })
        self.assertEqual(res_combined.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_combined.data), 1)
        self.assertEqual(res_combined.data[0]['title'], "Inception")

    def test_get_movie_detail_success_and_not_found(self):
        response = self.client.get(self.movie_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Inception")

        not_found_response = self.client.get(self.movie_not_found_url)
        self.assertEqual(not_found_response.status_code, status.HTTP_404_NOT_FOUND)

    #Перевірка прав доступу без автентифікації (401 / 403)

    def test_movie_mutations_forbidden_for_anonymous_user(self):
        payload = {
            "title": "Tenet",
            "director": 1,
            "genre": 1,
            "year": 2020,
            "rating": "7.3"
        }
        post_res = self.client.post(self.movies_url, payload, format='json')
        self.assertIn(post_res.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

        put_res = self.client.put(self.movie_detail_url, payload, format='json')
        self.assertIn(put_res.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

        patch_res = self.client.patch(self.movie_detail_url, {"rating": "9.0"}, format='json')
        self.assertIn(patch_res.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

        del_res = self.client.delete(self.movie_detail_url)
        self.assertIn(del_res.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

        self.assertEqual(Movie.objects.count(), 3)

    #Авторизовані CRUD-операції та валідація для Movie

    def test_create_movie_authorized_and_invalid(self):
        self.client.force_authenticate(user=self.user)

        valid_data = {
            "title": "Oppenheimer",
            "director": 1,
            "genre": 2,
            "year": 2023,
            "rating": "8.4",
            "description": "Biographical thriller film."
        }
        response = self.client.post(self.movies_url, valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Movie.objects.count(), 4)
        self.assertEqual(response.data['title'], "Oppenheimer")

        #Невалідні дані -> 400
        invalid_response = self.client.post(self.movies_url, {"title": ""}, format='json')
        self.assertEqual(invalid_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_movie_put_and_patch_authorized(self):
        self.client.force_authenticate(user=self.user)

        #Повне оновлення (PUT)
        put_data = {
            "title": "Inception (Director's Cut)",
            "director": 1,
            "genre": 1,
            "year": 2010,
            "rating": "9.0",
            "description": "Updated description."
        }
        put_res = self.client.put(self.movie_detail_url, put_data, format='json')
        self.assertEqual(put_res.status_code, status.HTTP_200_OK)
        self.assertEqual(put_res.data['title'], "Inception (Director's Cut)")

        #Невалідний PUT -> 400
        bad_put = self.client.put(self.movie_detail_url, {"title": ""}, format='json')
        self.assertEqual(bad_put.status_code, status.HTTP_400_BAD_REQUEST)

        #Часткове оновлення (PATCH)
        patch_res = self.client.patch(self.movie_detail_url, {"rating": "9.2"}, format='json')
        self.assertEqual(patch_res.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_res.data['rating'], "9.2")

        #Невалідний PATCH -> 400
        bad_patch = self.client.patch(self.movie_detail_url, {"year": "not-a-year"}, format='json')
        self.assertEqual(bad_patch.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_movie_authorized(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(self.movie_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Movie.objects.filter(pk=1).exists())
        self.assertEqual(Movie.objects.count(), 2)

    #Тести для Director та Genre (CRUD + 409 Conflict)

    def test_directors_crud_and_conflict(self):
        #Публічне читання
        list_res = self.client.get(self.directors_url)
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_res.data), 2)

        detail_res = self.client.get(self.director_detail_url)
        self.assertEqual(detail_res.status_code, status.HTTP_200_OK)

        #Авторизоване створення та оновлення
        self.client.force_authenticate(user=self.user)
        create_res = self.client.post(self.directors_url, {"name": "Quentin Tarantino"}, format='json')
        self.assertEqual(create_res.status_code, status.HTTP_201_CREATED)
        new_id = create_res.data['id']

        new_detail_url = reverse('director-detail', args=[new_id])
        update_res = self.client.put(new_detail_url, {"name": "Q. Tarantino", "bio": "Director"}, format='json')
        self.assertEqual(update_res.status_code, status.HTTP_200_OK)

        #Конфлікт видалення режисера, за яким закріплені фільми -> 409
        conflict_res = self.client.delete(self.director_detail_url)
        self.assertEqual(conflict_res.status_code, status.HTTP_409_CONFLICT)
        self.assertTrue(Director.objects.filter(pk=1).exists())

        #Успішне видалення режисера без фільмів -> 204
        del_res = self.client.delete(new_detail_url)
        self.assertEqual(del_res.status_code, status.HTTP_204_NO_CONTENT)

    def test_genres_crud_and_conflict(self):
        list_res = self.client.get(self.genres_url)
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_res.data), 2)

        detail_res = self.client.get(self.genre_detail_url)
        self.assertEqual(detail_res.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=self.user)
        create_res = self.client.post(self.genres_url, {"name": "Comedy"}, format='json')
        self.assertEqual(create_res.status_code, status.HTTP_201_CREATED)
        new_id = create_res.data['id']

        new_detail_url = reverse('genre-detail', args=[new_id])
        update_res = self.client.put(new_detail_url, {"name": "Dark Comedy"}, format='json')
        self.assertEqual(update_res.status_code, status.HTTP_200_OK)

        #Конфлікт видалення жанру з фільмами -> 409
        conflict_res = self.client.delete(self.genre_detail_url)
        self.assertEqual(conflict_res.status_code, status.HTTP_409_CONFLICT)
        self.assertTrue(Genre.objects.filter(pk=1).exists())

        #Успішне видалення порожнього жанру -> 204
        del_res = self.client.delete(new_detail_url)
        self.assertEqual(del_res.status_code, status.HTTP_204_NO_CONTENT)

    def test_models_string_representation(self):
        director = Director.objects.get(pk=1)
        genre = Genre.objects.get(pk=1)
        movie = Movie.objects.get(pk=1)
        self.assertEqual(str(director), "Christopher Nolan")
        self.assertEqual(str(genre), "Sci-Fi")
        self.assertEqual(str(movie), "Inception")