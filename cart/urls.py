from django.urls import path

from . import views
from .views import CreateCheckoutSessionView

app_name = 'cart_app'

urlpatterns = [
    path('cart/', views.view_cart, name='view_cart'),
    path('add/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-history/', views.order_history, name='order_history'),
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(),
         name='create_checkout_session'),
    path('checkout/success/', views.checkout_success, name='checkout_success'),
    path('checkout/failure/', views.checkout_failure, name='checkout_failure'),
    path('order/confirmation/<int:order_id>/',
         views.order_confirmation, name='order_confirmation'),
    path('stripe/webhook/', views.stripe_webhook, name='stripe-webhook'),

]

