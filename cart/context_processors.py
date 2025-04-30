# cart/context_processors.py
from .models import Order


def cart_item_count(request):
    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user, ordered=False).first()
        if order:
            return {'cart_item_count': sum(item.quantity for item in order.items.all())}
    return {'cart_item_count': 0}
