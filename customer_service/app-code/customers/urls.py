from django.urls import path
from .views import CustomerListCreateAPIView, CustomerDetailAPIView, StatusAPIView

urlpatterns = [
    # Monitoring endpoint
    path('status', StatusAPIView.as_view(), name='status'),
    # Customer endpoints:
    path('', CustomerListCreateAPIView.as_view(), name='customer_collection'),
    path('<str:id>', CustomerDetailAPIView.as_view(), name='customer_detail'),
]