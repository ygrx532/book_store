# Import necessary modules and classes:
import json
from confluent_kafka import Producer
from django.conf import settings
from rest_framework.views import APIView             # Base class for our API views
from rest_framework.response import Response         # DRF Response for returning data in JSON format
from rest_framework import status                   # Provides HTTP status code constants (optional use)
from django.shortcuts import get_object_or_404       # Helper to retrieve an object or return 404 if not found
from django.urls import reverse                      # Used to build URLs dynamically based on view names
from .models import Customer                   # Import our database models (Customer)
from .serializers import CustomerSerializer  # Import serializers for data validation and transformation


# ------------------------------------------------------------
# API View for handling customer creation and lookup by userId (POST and GET /customers)
# ------------------------------------------------------------
class CustomerListCreateAPIView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Kafka Producer Configuration
        brokers = '3.129.102.184:9092,18.118.230.221:9093,3.130.6.49:9094'
        self.producer = Producer({
            'bootstrap.servers': brokers,  # Use a placeholder for Kafka brokers
        })

    def _send_customer_event_to_kafka(self, customer):
        # Create the message in JSON format
        customer_data = {
            "userId": customer.userId,
            "name": customer.name,
            "phone": customer.phone,
            "address": customer.address,
            "address2": customer.address2,
            "city": customer.city,
            "state": customer.state,
            "zipcode": customer.zipcode,
        }

        # Serialize the message to JSON
        message = json.dumps(customer_data)

        # Send the message to the Kafka topic
        self.producer.produce('yuyangx2.customer.evt', value=message)
        self.producer.flush()  # Ensure the message is sent
        
    def post(self, request, format=None):
        # Instantiate the serializer with incoming customer data.
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            # Check if a customer with the given userId (email) already exists.
            if Customer.objects.filter(userId=serializer.validated_data.get('userId')).exists():
                return Response(
                    {"message": "This user ID already exists in the system."},
                    status=422
                )
            # Save the new customer to the database.
            customer = serializer.save()
            # Build the URL for retrieving the new customer by their ID.
            location = request.build_absolute_uri(reverse('customer_detail', args=[customer.id]))
            headers = {'Location': location}

            # Send a Kafka message to the customer.evt topic
            self._send_customer_event_to_kafka(customer)

            # Return the serialized customer data with HTTP status 201 and the Location header.
            return Response(serializer.data, status=201, headers=headers)

        return Response(
            {"message": "Illegal, missing, or malformed input", "errors": serializer.errors},
            status=400
        )
    
    def get(self, request, format=None):
        # Retrieve the customer by the userId passed as a query parameter.
        userId = request.query_params.get('userId')
        if not userId:
            return Response({"message": "Illegal, missing, or malformed input"}, status=400)
        try:
            # Try to find the customer with the given email (userId).
            customer = Customer.objects.get(userId=userId)
        except Customer.DoesNotExist:
            # If not found, return a 404 response.
            return Response({"message": "User-ID does not exist in the system"}, status=404)
        # Serialize and return the customer data with a 200 OK status.
        serializer = CustomerSerializer(customer)
        return Response(serializer.data, status=200)

# ------------------------------------------------------------
# API View for retrieving a customer by their numeric ID (GET /customers/<id>)
# ------------------------------------------------------------
class CustomerDetailAPIView(APIView):
    def get(self, request, id, format=None):
        try:
            customer_id = int(id)
        except ValueError:
            return Response({"message": "Illegal, missing, or malformed input"}, status=400)
        # Retrieve the customer by numeric ID; returns 404 if the customer does not exist.
        customer = get_object_or_404(Customer, id=id)
        # Serialize the customer object.
        serializer = CustomerSerializer(customer)
        # Return the serialized data.
        return Response(serializer.data, status=200)

# ------------------------------------------------------------
# API View for the status endpoint (GET /status)
# ------------------------------------------------------------
class StatusAPIView(APIView):
    def get(self, request, format=None):
        # Return a plain text response "OK".
        # Note: content_type is explicitly set to "text/plain" to indicate plain text.
        return Response("OK", status=200, content_type="text/plain")

