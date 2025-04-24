from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from solo.models import Book  # the import path based on  project structure
from .models import  CartItem, Order, OrderItem
from .forms import CheckoutForm


@login_required
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user, book=book)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart_app:view_cart')









@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                user=request.user,
                shipping_address=form.cleaned_data['shipping_address'],
                phone_number=form.cleaned_data['phone_number']
            )
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    book=item.book,
                    price=item.book.price,
                    quantity=item.quantity
                )
            cart_items.delete()
            return redirect('order_confirmation', order_id=order.id)
    else:
        form = CheckoutForm()
    return render(request, 'cart/checkout.html', {'form': form, 'cart_items': cart_items})





@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.get_total_price() for item in cart_items)
    return render(request, 'cart/view_cart.html', {'cart_items': cart_items, 'total': total})



@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    return redirect('cart_app:view_cart')


@login_required
def order_confirmation(request, order_id):
      order = get_object_or_404(Order, id=order_id, user=request.user)
      return render(request, 'cart/order_confirmation.html', {'order': order})

@login_required
def order_history(request):
      orders = Order.objects.filter(user=request.user).order_by('-created_at')
      return render(request, 'cart/order_history.html', {'orders': orders})