from django.db import models
from django.utils.text import slugify
from django.urls import reverse


type_choices = (
    ('New', 'New'),
    ('Bestseller', 'Bestseller'),
    ('Offers', 'On offers'),
)

LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger')
)



class Book(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    author = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    type = models.CharField(max_length=20, choices=type_choices, blank=True)
    label = models.CharField(max_length=1, choices=LABEL_CHOICES, blank=True)
    cover = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('solo_app:solo_book_detail', args=[self.slug])
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
