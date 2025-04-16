from django.db import models

# Create your models here.
from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)  # e.g. 19.99
    cover_image = models.ImageField(
        upload_to='solo_books/', blank=True, null=True)

    def __str__(self):
        return self.title
