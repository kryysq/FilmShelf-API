from rest_framework import serializers
from .models import Director, Genre, Movie

class DirectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Director
        fields = '__all__'

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'

class MovieSerializer(serializers.ModelSerializer):
    director_name = serializers.ReadOnlyField(source='director.name')
    genre_name = serializers.ReadOnlyField(source='genre.name')

    class Meta:
        model = Movie
        fields = ['id', 'title', 'director', 'director_name', 'genre', 'genre_name', 'year', 'rating']