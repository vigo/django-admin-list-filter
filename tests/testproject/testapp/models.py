import uuid

from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class CategoryRenamed(models.Model):
    renamed_id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class AudienceChoices(models.TextChoices):
    BEGINNER = 'beginner', 'Beginer'
    INTERMEDIATE = 'intermediate', 'Intermediate'
    PRO = 'pro', 'Pro'


class Post(models.Model):
    author = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts',
    )
    category = models.ForeignKey(
        to='Category',
        on_delete=models.CASCADE,
        related_name='posts',
    )
    category_renamed = models.ForeignKey(
        to='CategoryRenamed',
        on_delete=models.CASCADE,
        related_name='posts',
    )
    tags = models.ManyToManyField(to='Tag', blank=True)
    audience = models.CharField(
        max_length=100,
        choices=AudienceChoices.choices,
        default=AudienceChoices.BEGINNER,
    )

    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title
