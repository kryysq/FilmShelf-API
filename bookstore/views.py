import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from .models import Director, Genre, Movie
from .serializers import DirectorSerializer, GenreSerializer, MovieSerializer

logger = logging.getLogger(__name__)


class DirectorListCreateAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        directors = Director.objects.all()
        serializer = DirectorSerializer(directors, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DirectorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info("Director created (id=%s) by user=%s", serializer.data.get('id'), request.user.username)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.warning("Invalid director payload: %s", serializer.errors)
        return Response({"error": "Invalid data", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class DirectorDetailAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

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
            logger.info("Director updated (id=%s) by user=%s", pk, request.user.username)
            return Response(serializer.data)
        return Response({"error": "Invalid data", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        director = self.get_object(pk)
        if director.movies.exists():
            logger.warning("Attempt to delete director id=%s with linked movies", pk)
            return Response({
                "error": f"Неможливо видалити режисера '{director.name}', оскільки за ним закріплені фільми."
            }, status=status.HTTP_409_CONFLICT)
        director.delete()
        logger.info("Director deleted (id=%s) by user=%s", pk, request.user.username)
        return Response(status=status.HTTP_204_NO_CONTENT)


class GenreListCreateAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        genres = Genre.objects.all()
        serializer = GenreSerializer(genres, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = GenreSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info("Genre created (id=%s) by user=%s", serializer.data.get('id'), request.user.username)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.warning("Invalid genre payload: %s", serializer.errors)
        return Response({"error": "Invalid data", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class GenreDetailAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

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
            logger.info("Genre updated (id=%s) by user=%s", pk, request.user.username)
            return Response(serializer.data)
        return Response({"error": "Invalid data", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        genre = self.get_object(pk)
        if genre.movies.exists():
            logger.warning("Attempt to delete genre id=%s with linked movies", pk)
            return Response({
                "error": f"Неможливо видалити жанр '{genre.name}', оскільки до нього належать фільми."
            }, status=status.HTTP_409_CONFLICT)
        genre.delete()
        logger.info("Genre deleted (id=%s) by user=%s", pk, request.user.username)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MovieListCreateAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        summary="Отримати список фільмів",
        description="Повертає список усіх фільмів із можливістю фільтрації. Доступно без автентифікації.",
        parameters=[
            OpenApiParameter(name='title', type=str, description='Пошук за частиною назви фільму'),
            OpenApiParameter(name='genre', type=int, description='ID жанру для фільтрації'),
            OpenApiParameter(name='director', type=int, description='ID режисера для фільтрації'),
            OpenApiParameter(name='year', type=int, description='Рік виходу фільму'),
            OpenApiParameter(name='min_rating', type=float, description='Мінімальний рейтинг фільму'),
        ],
        responses={200: MovieSerializer(many=True)},
    )
    def get(self, request):
        movies = Movie.objects.all()

        title = request.query_params.get('title', None)
        genre_id = request.query_params.get('genre', None)
        director_id = request.query_params.get('director', None)
        year = request.query_params.get('year', None)
        min_rating = request.query_params.get('min_rating', None)

        if title:
            movies = movies.filter(title__icontains=title)
        if genre_id:
            movies = movies.filter(genre_id=genre_id)
        if director_id:
            movies = movies.filter(director_id=director_id)
        if year:
            movies = movies.filter(year=year)
        if min_rating:
            movies = movies.filter(rating__gte=min_rating)

        logger.info("Movies list retrieved (count=%d)", movies.count())
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Створити новий фільм",
        description="Створює новий запис фільму. Вимагає JWT-токен (Authorization: Bearer <token>).",
        request=MovieSerializer,
        responses={
            201: MovieSerializer,
            400: OpenApiResponse(description="Невалідні дані запиту"),
            401: OpenApiResponse(description="Не надано або недійсний JWT-токен"),
        },
    )
    def post(self, request):
        serializer = MovieSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info("Movie created (id=%s) by user=%s", serializer.data.get('id'), request.user.username)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.warning("Invalid movie payload from user=%s: %s", request.user.username, serializer.errors)
        return Response({"error": "Invalid data", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class MovieDetailAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(Movie, pk=pk)

    @extend_schema(
        summary="Отримати деталі фільму",
        description="Повертає детальну інформацію про фільм за його ID. Доступно всім.",
        responses={
            200: MovieSerializer,
            404: OpenApiResponse(description="Фільм не знайдено"),
        },
    )
    def get(self, request, pk):
        movie = self.get_object(pk)
        logger.info("Movie detail retrieved (id=%s)", pk)
        serializer = MovieSerializer(movie)
        return Response(serializer.data)

    @extend_schema(
        summary="Повністю оновити фільм",
        description="Повне оновлення полів фільму за ID. Вимагає JWT-автентифікації.",
        request=MovieSerializer,
        responses={
            200: MovieSerializer,
            400: OpenApiResponse(description="Невалідні дані"),
            401: OpenApiResponse(description="Потрібна автентифікація"),
            404: OpenApiResponse(description="Фільм не знайдено"),
        },
    )
    def put(self, request, pk):
        movie = self.get_object(pk)
        serializer = MovieSerializer(movie, data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info("Movie fully updated (id=%s) by user=%s", pk, request.user.username)
            return Response(serializer.data)
        logger.warning("Failed PUT update for movie id=%s: %s", pk, serializer.errors)
        return Response({"error": "Invalid data", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Частково оновити фільм",
        description="Часткове оновлення окремих полів фільму за ID. Вимагає JWT-автентифікації.",
        request=MovieSerializer,
        responses={
            200: MovieSerializer,
            400: OpenApiResponse(description="Невалідні дані"),
            401: OpenApiResponse(description="Потрібна автентифікація"),
            404: OpenApiResponse(description="Фільм не знайдено"),
        },
    )
    def patch(self, request, pk):
        movie = self.get_object(pk)
        serializer = MovieSerializer(movie, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info("Movie partially updated (id=%s) by user=%s", pk, request.user.username)
            return Response(serializer.data)
        logger.warning("Failed PATCH update for movie id=%s: %s", pk, serializer.errors)
        return Response({"error": "Invalid data", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Видалити фільм",
        description="Видаляє фільм за ID. Вимагає JWT-автентифікації.",
        responses={
            204: OpenApiResponse(description="Фільм успішно видалено"),
            401: OpenApiResponse(description="Потрібна автентифікація"),
            404: OpenApiResponse(description="Фільм не знайдено"),
        },
    )
    def delete(self, request, pk):
        movie = self.get_object(pk)
        try:
            movie.delete()
            logger.info("Movie deleted (id=%s) by user=%s", pk, request.user.username)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error("Unexpected error deleting movie id=%s: %s", pk, str(e), exc_info=True)
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)