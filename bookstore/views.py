from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Director, Genre, Movie
from .serializers import DirectorSerializer, GenreSerializer, MovieSerializer

class DirectorListCreateAPIView(APIView):
    def get(self, request):
        directors = Director.objects.all()
        serializer = DirectorSerializer(directors, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DirectorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"error": "Invalid data", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class DirectorDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(Director, pk=pk)

    def get(self, request, pk):
        director = self.get_object(pk)
        serializer = DirectorSerializer(director)
        return Response(serializer.data)

    def put(self, request, pk):
        director = self.get_object(pk)
        serializer = DirectorSerializer(director, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({"error": "Invalid data", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        director = self.get_object(pk)
        if director.movies.exists():
            return Response({
                "error": f"Неможливо видалити режисера '{director.name}', оскільки за ним закріплені фільми."
            }, status=status.HTTP_409_CONFLICT)
        director.delete()
        return Response(status=status.HTTP_24_NO_CONTENT)

class GenreListCreateAPIView(APIView):
    def get(self, request):
        genres = Genre.objects.all()
        serializer = GenreSerializer(genres, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = GenreSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"error": "Invalid data", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class GenreDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(Genre, pk=pk)

    def get(self, request, pk):
        genre = self.get_object(pk)
        serializer = GenreSerializer(genre)
        return Response(serializer.data)

    def put(self, request, pk):
        genre = self.get_object(pk)
        serializer = GenreSerializer(genre, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({"error": "Invalid data", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        genre = self.get_object(pk)
        if genre.movies.exists():
            return Response({
                "error": f"Неможливо видалити жанр '{genre.name}', оскільки до нього належать фільми."
            }, status=status.HTTP_409_CONFLICT)
        genre.delete()
        return Response(status=status.HTTP_24_NO_CONTENT)

class MovieListCreateAPIView(APIView):
    def get(self, request):
        movies = Movie.objects.all()

        title = request.query_params.get('title', None)
        genre_id = request.query_params.get('genre', None)
        director_id = request.query_params.get('director', None)
        year = request.query_params.get('year', None)
        min_rating = request.query_params.get('min_rating', None)

        #фільтри
        if title:
            movies = movies.filter(title__icontains=title) #Пошук
        if genre_id:
            movies = movies.filter(genre_id=genre_id)
        if director_id:
            movies = movies.filter(director_id=director_id)
        if year:
            movies = movies.filter(year=year)
        if min_rating:
            movies = movies.filter(rating__gte=min_rating) #мінімальний рейтингом

        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = MovieSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"error": "Invalid data", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class MovieDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(Movie, pk=pk)

    def get(self, request, pk):
        movie = self.get_object(pk)
        serializer = MovieSerializer(movie)
        return Response(serializer.data)

    def put(self, request, pk):
        movie = self.get_object(pk)
        serializer = MovieSerializer(movie, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({"error": "Invalid data", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        movie = self.get_object(pk)
        movie.delete()
        return Response(status=status.HTTP_24_NO_CONTENT)