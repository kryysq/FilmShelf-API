from django.db import models

class Director(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Movie(models.Model):
    title = models.CharField(max_length=255)
    director = models.ForeignKey(Director, related_name='movies', on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, related_name='movies', on_delete=models.CASCADE)
    year = models.IntegerField()
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    description = models.TextField(blank=True, null=True)
    poster_url = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.title
