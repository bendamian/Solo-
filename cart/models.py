from django.db import models
from django.utils.timezone import datetime
from django.contrib.auth.models import User

from solo.models import Book  # my Book model is in the 'solo' app
import uuid

class OrderItem(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    book = models.ForeignKey(Book,on_delete=models.CASCADE)
    ordered_date = models.DateTimeField('date ordered')
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.quantity} x {self.book.title}'


class Order(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='orders')
    ref_code = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True)
    items = models.ManyToManyField('OrderItem', related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    

    def __str__(self):
        return f'Order {self.ref_code} by {self.user.username}'


'''
# test model
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.book.title}"

    def get_total_price(self):
        return self.quantity * self.book.price

'''
