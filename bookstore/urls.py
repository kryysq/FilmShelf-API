from django.urls import path
from .views import (
    DirectorListCreateAPIView, DirectorDetailAPIView,
    GenreListCreateAPIView, GenreDetailAPIView,
    MovieListCreateAPIView, MovieDetailAPIView
)

urlpatterns = [
    path('directors/', DirectorListCreateAPIView.as_view(), name='director-list'),
    path('directors/<int:pk>/', DirectorDetailAPIView.as_view(), name='director-detail'),
    path('genres/', GenreListCreateAPIView.as_view(), name='genre-list'),
    path('genres/<int:pk>/', GenreDetailAPIView.as_view(), name='genre-detail'),
    path('movies/', MovieListCreateAPIView.as_view(), name='movie-list'),
    path('movies/<int:pk>/', MovieDetailAPIView.as_view(), name='movie-detail'),
]