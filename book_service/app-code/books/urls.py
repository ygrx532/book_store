from django.urls import path
from .views import BookCreateAPIView, BookDetailAPIView, BookRelatedAPIView, StatusAPIView

urlpatterns = [
    # Monitoring endpoint
    path('status', StatusAPIView.as_view(), name='status'),
    # Book endpoints:
    path('', BookCreateAPIView.as_view(), name='add_book'),
    path('<str:isbn>', BookDetailAPIView.as_view(), name='book_detail'),
    path('<str:isbn>/related-books', BookRelatedAPIView.as_view(), name='book_detail_alt'),
    path('isbn/<str:isbn>', BookDetailAPIView.as_view(), name='book_detail_alt'),
]