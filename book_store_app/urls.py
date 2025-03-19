# urls.py
from django.urls import path
from .views import (
    BookCreateAPIView,
    BookDetailAPIView,
    CustomerListCreateAPIView,
    CustomerDetailAPIView,
    StatusAPIView,
    index,
)

urlpatterns = [
    path("", index, name="index"),
    # Monitoring endpoint
    path('status', StatusAPIView.as_view(), name='status'),
    
    # Book endpoints:
    path('books', BookCreateAPIView.as_view(), name='add_book'),
    path('books/<str:isbn>', BookDetailAPIView.as_view(), name='book_detail'),
    path('books/isbn/<str:isbn>', BookDetailAPIView.as_view(), name='book_detail_alt'),
    
    # Customer endpoints:
    path('customers', CustomerListCreateAPIView.as_view(), name='customer_collection'),
    path('customers/<str:id>', CustomerDetailAPIView.as_view(), name='customer_detail'),
]