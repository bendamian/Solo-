from .models import Order
from django.http import HttpResponse
import json
import stripe
from django.conf import settings
from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from solo.models import Book
from .models import Order, OrderItem
from .forms import CheckoutForm
from django.contrib import messages
from django.urls import reverse
from django.views import View

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        order_item_qs = order.items.filter(book=book, ordered=False)
        if order_item_qs.exists():
            order_item = order_item_qs[0]
            order_item.quantity += 1
            order_item.save()
        else:
            order_item = OrderItem.objects.create(
                user=request.user,
                book=book,
                ordered_date=timezone.now(),
                quantity=1,
                ordered=False
            )
            order.items.add(order_item)
    else:
        order_item = OrderItem.objects.create(
            user=request.user,
            book=book,
            ordered_date=timezone.now(),
            quantity=1,
            ordered=False
        )
        order = Order.objects.create(
            user=request.user,
            ordered_date=timezone.now()
        )
        order.items.add(order_item)

    return redirect('cart_app:view_cart')


@login_required
def checkout(request):
    order = Order.objects.filter(user=request.user, ordered=False).first()
    if not order or not order.items.exists():
        return redirect('cart_app:view_cart')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order.shipping_address = form.cleaned_data['shipping_address']
            order.phone_number = form.cleaned_data['phone_number']
            order.ordered = False
            order.payment_status = 'PENDING'
            order.save()
            return redirect('order_confirmation', order_id=order.id)
    else:
        form = CheckoutForm()

    cart_items = order.items.all()
    total = sum(item.book.price * item.quantity for item in cart_items)

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


@method_decorator([login_required, csrf_exempt], name='dispatch')
class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        order = request.user.orders.filter(ordered=False).first()
        if not order or not order.items.exists():
            return redirect('cart_app:view_cart')

        line_items = [
            {
                'price_data': {
                    'currency': 'gbp',
                    'unit_amount': int(item.book.price * 100),
                    'product_data': {
                        'name': item.book.title,
                        'description': f'{item.quantity} x {item.book.title}',
                        
                    },
                },
                'quantity': item.quantity,
            }
            for item in order.items.all()
        ]

        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],  # ✅ ensure this is included
                line_items=line_items,
                mode='payment',
                client_reference_id=str(order.id),  # optional
                metadata={  # ✅ must be inside here
                    'order_id': str(order.id),
                },
                payment_intent_data={
                    'metadata': {
                        'order_id': str(order.id),
                    }
                },
                success_url=request.build_absolute_uri(
                    reverse('cart_app:checkout_success')
                ) + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=request.build_absolute_uri(
                    reverse('cart_app:checkout')
                ),
            )

            order.stripe_session_id = checkout_session.id
            order.save()

            return redirect(checkout_session.url, code=303)

        except Exception as e:
            print(f"Stripe Error: {e}")
            return redirect('cart_app:checkout_failure')



'''
def checkout(request):
    order = request.user.orders.filter(ordered=False).first()
    context = {'order': order}
    return render(request, 'cart/checkout.html', context)

'''
#######
'''
def checkout_success(request):
    session_id = request.GET.get('session_id')
    if not session_id:
        return redirect('cart_app:checkout_failure')

    try:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == 'paid':
            order = request.user.orders.filter(ordered=False).first()
            if order:
                order.ordered = True
                order.payment_status = 'PAID'
                order.stripe_session_id = session_id
                order.save()
                for item in order.items.all():
                    item.ordered = True
                    item.ordered_date = timezone.now()           
                    item.save()
                return render(request, 'cart/checkout_success.html', {'order': order})
            else:
                return redirect('solo_app:solo_book_list')
        else:
            return redirect('cart_app:checkout_failure')
    except stripe.error.InvalidRequestError as e:
        print(f"Stripe Invalid Request Error: {e}")
        return redirect('cart_app:checkout_failure')

'''


@login_required
def checkout_success(request):
    session_id = request.GET.get('session_id')
    if not session_id:
        return redirect('cart_app:checkout_failure')

    try:
        # Retrieve the session from Stripe
        session = stripe.checkout.Session.retrieve(session_id)

        if session.payment_status == 'paid':
            # Retrieve the order associated with this session
            order = request.user.orders.filter(ordered=False).first()
            if order:
                # Update order details
                order.ordered = True
                order.payment_status = 'PAID'
                order.stripe_session_id = session_id
                order.save()

                # Update each item in the order
                for item in order.items.all():
                    item.ordered = True
                    item.ordered_date = timezone.now()
                    item.save()

                # Prepare context for the success page
                amount_total = session.amount_total  # Amount in cents
                currency = session.currency.upper()
                amount_display = f"{amount_total / 100:.2f} {currency}"

                context = {
                    'order': order,
                    'amount_display': amount_display,
                }

                return render(request, 'cart/checkout_success.html', context)
            else:
                return redirect('solo_app:solo_book_list')
        else:
            return redirect('cart_app:checkout_failure')
    except stripe.error.InvalidRequestError as e:
        print(f"Stripe Invalid Request Error: {e}")
        return redirect('cart_app:checkout_failure')

def checkout_failure(request):
    return render(request, 'cart/checkout_failure.html')


def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'cart/order_confirmation.html', {'order': order})















@login_required
def order_confirmation(request, order_id):
      order = get_object_or_404(Order, id=order_id, user=request.user)
      return render(request, 'cart/order_confirmation.html', {'order': order})

@login_required
def order_history(request):
      orders = Order.objects.filter(user=request.user).order_by('-created_at')
      return render(request, 'cart/order_history.html', {'orders': orders})


@csrf_exempt
def stripe_webhook(request):
    print("📡 Webhook called")
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        print("❌ Invalid payload:", e)
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        print("❌ Invalid signature:", e)
        return HttpResponse(status=400)

    event_type = event['type']
    session = event['data'].get('object')

    if event_type in ['checkout.session.completed', 'checkout.session.async_payment_succeeded']:
        if session.get('payment_status') == 'paid':
            handle_successful_payment(session)
    elif event_type == 'checkout.session.async_payment_failed':
        handle_failed_payment(session)

    return HttpResponse(status=200)


def handle_successful_payment(session):
    print("🔥 Payment handler called")
    metadata = session.get('metadata', {})
    order_id = metadata.get('order_id')
    print("🧾 order_id in metadata:", order_id)

    if not order_id:
        print("❌ No order_id found in session metadata.")
        return

    try:
        order = Order.objects.get(id=order_id)
        order.payment_status = 'PAID'
        order.ordered = True
        # optional: update if not already saved
        order.stripe_session_id = session.get('id')
        order.save()

        for item in order.items.all():
            item.ordered = True
            item.save()

        print(f"✅ Order {order.id} marked as PAID.")
    except Order.DoesNotExist:
        print(f"❌ Order not found with ID: {order_id}")


def handle_failed_payment(session):
    print("💥 Handling failed payment for session:", session.get("id"))
    try:
        order = Order.objects.get(stripe_session_id=session.get("id"))
        order.payment_status = 'FAILED'
        order.save()
        print(f"❗ Order {order.id} marked as FAILED.")
    except Order.DoesNotExist:
        print(f"⚠️ No order found for session ID: {session.get('id')}")
