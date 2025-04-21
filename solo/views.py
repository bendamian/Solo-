from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from .models import Book





def book_checkout_view(request, book_id):
    return render(request, 'solo/book_checkout.html', {'book_id': book_id})


def success_view(request):
    return render(request, 'solo/success.html')


def book_list_view(request):
    books = Book.objects.all()
    return render(request, 'solo/book_list.html', {'books': books})


def book_detail_view(request, slug):
    book = get_object_or_404(Book, slug=slug)
    return render(request, 'solo/book_detail.html', {'book': book})
