# solo/urls.py
from django.urls import path
from . import views

app_name='solo_app'

urlpatterns = [
    path('', views.book_list_view, name='solo_book_list'),
    path('buy/<int:book_id>/', views.book_checkout_view, name='solo_book_checkout'),
    path('success/', views.success_view, name='solo_success'),
    path('<slug:slug>/', views.book_detail_view, name='solo_book_detail'),
]
