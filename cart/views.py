from .models import Order
from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from solo.models import Book
from .models import Order, OrderItem
from .forms import CheckoutForm
from django.contrib import messages


@login_required
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        order_item_qs = order.items.filter(book=book)
        if order_item_qs.exists():
            order_item = order_item_qs[0]
            order_item.quantity += 1
            order_item.save()
        else:
            order_item = OrderItem.objects.create(
                user=request.user,
                book=book,
                ordered_date=timezone.now(),
                quantity=1
            )
            order.items.add(order_item)
    else:
        order_item = OrderItem.objects.create(
            user=request.user,
            book=book,
            ordered_date=timezone.now(),
            quantity=1
        )
        order = Order.objects.create(
            user=request.user,
            ordered_date=timezone.now()
        )
        order.items.add(order_item)

    return redirect('cart_app:view_cart')


@login_required
def checkout(request):
    # Retrieve the active (not yet ordered) order
    order = Order.objects.filter(user=request.user, ordered=False).first()

    if not order or order.items.count() == 0:
        # No active order to check out
        return redirect('cart_app:view_cart')

    # Calculate subtotals and total
    cart_items = []
    total = 0
    for item in order.items.all():
        subtotal = item.book.price * item.quantity
        cart_items.append({
            'item': item,
            'subtotal': subtotal
        })
        total += subtotal

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Update the existing order with shipping details
            order.shipping_address = form.cleaned_data['shipping_address']
            order.phone_number = form.cleaned_data['phone_number']
            order.ordered = True  # Mark the order as complete
            order.save()

            # Redirect to order confirmation page
            return redirect('order_confirmation', order_id=order.id)
    else:
        form = CheckoutForm()

    return render(request, 'cart/checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'order': order,
        'total': total
    })





@login_required
def view_cart(request):
    order = Order.objects.filter(user=request.user, ordered=False).first()
    order_items = order.items.all() if order else []
    total = sum(item.subtotal for item in order_items) if order_items else 0

    return render(request, 'cart/view_cart.html', {
        'order_items': order_items,
        'total': total,
    })

@login_required
def remove_from_cart(request, item_id):
    # Get the current active order
    order = Order.objects.filter(user=request.user, ordered=False).first()
    if not order:
        messages.warning(request, "You don't have an active order.")
        return redirect('cart_app:view_cart')

    try:
        order_item = OrderItem.objects.get(id=item_id, user=request.user)

        if order.items.filter(id=order_item.id).exists():
            # Remove the item
            order.items.remove(order_item)
            order_item.delete()
            messages.success(
                request, f"Removed '{order_item.book.title}' from your cart.")

            # 🧹 If the cart is now empty, delete the order
            if order.items.count() == 0:
                order.delete()
                messages.info(
                    request, "Your cart is now empty. The order has been removed.")
        else:
            messages.warning(request, "This item is not in your cart.")
    except OrderItem.DoesNotExist:
        messages.error(
            request, "This item does not exist or was already removed.")

    return redirect('cart_app:view_cart')


@login_required
def order_confirmation(request, order_id):
      order = get_object_or_404(Order, id=order_id, user=request.user)
      return render(request, 'cart/order_confirmation.html', {'order': order})

@login_required
def order_history(request):
      orders = Order.objects.filter(user=request.user).order_by('-created_at')
      return render(request, 'cart/order_history.html', {'orders': orders})