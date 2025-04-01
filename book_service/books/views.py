# Import necessary modules and classes:
from django.http import HttpResponse
from rest_framework.views import APIView             # Base class for our API views
from rest_framework.response import Response         # DRF Response for returning data in JSON format
from rest_framework import status                   # Provides HTTP status code constants (optional use)
from django.shortcuts import get_object_or_404       # Helper to retrieve an object or return 404 if not found
from django.urls import reverse                      # Used to build URLs dynamically based on view names
from .models import Book                  # Import our database models (Book)
from .serializers import BookSerializer  # Import serializers for data validation and transformation

# ------------------------------------------------------------
# API View for creating a new Book (POST /books)
# ------------------------------------------------------------
class BookCreateAPIView(APIView):
    def post(self, request, format=None):
        # Instantiate the serializer with the incoming JSON data.
        serializer = BookSerializer(data=request.data)
        
        # Validate the data against the serializer's rules.
        if serializer.is_valid():
            # Retrieve the ISBN from the validated data.
            isbn = serializer.validated_data.get('ISBN')
            # Check if a book with the same ISBN already exists in the database.
            # If the ISBN is unique, save the new book record to the database.
            book = serializer.save()
            # Build the absolute URL for the newly created book using the reverse lookup.
            location = request.build_absolute_uri(reverse('book_detail', args=[book.ISBN]))
            headers = {'Location': location}  # Set the Location header as required.
            # Return the serialized book data with HTTP status 201 (Created) and the Location header.
            return Response(serializer.data, status=201, headers=headers)
        
        # If validation fails and the error is due to a duplicate ISBN, return a 422 error.
        if serializer.errors.get('ISBN') == ["book with this ISBN already exists."]:
            return Response(
                {"message": "This ISBN already exists in the system."},
                status=422
            )
            
        # If validation fails, return a 400 response with error details.
        return Response(
            {"message": "Illegal, missing, or malformed input", "errors": serializer.errors},
            status=400
        )

# ------------------------------------------------------------
# API View for retrieving and updating a Book (GET and PUT /books/<isbn>)
# ------------------------------------------------------------
class BookDetailAPIView(APIView):
    def get(self, request, isbn, format=None):
        # Retrieve the book object by its ISBN; if not found, a 404 error is automatically returned.
        book = get_object_or_404(Book, ISBN=isbn)
        # Serialize the book object into JSON format.
        serializer = BookSerializer(book)
        # Return the serialized data with a 200 OK status.
        return Response(serializer.data, status=200)
    
    def put(self, request, isbn, format=None):
        # Ensure that the ISBN in the request body matches the ISBN in the URL.
        if request.data.get('ISBN') != isbn:
            return Response(
                {"message": "ISBN in URL and body do not match"},
                status=400
            )
        # Retrieve the book that is going to be updated; return 404 if it doesn't exist.
        book = get_object_or_404(Book, ISBN=isbn)
        # Instantiate the serializer with the existing book instance and new data.
        serializer = BookSerializer(book, data=request.data)
        # Validate the new data.
        if serializer.is_valid():
            # Save the updated book record to the database.
            serializer.save()
            # Return the updated book data with a 200 OK status.
            return Response(serializer.data, status=200)
        # If validation fails, return a 400 response with error details.
        return Response(
            {"message": "Illegal, missing, or malformed input", "errors": serializer.errors},
            status=400
        )

# ------------------------------------------------------------
# API View for the status endpoint (GET /status)
# ------------------------------------------------------------
class StatusAPIView(APIView):
    def get(self, request, format=None):
        # Return a plain text response "OK".
        # Note: content_type is explicitly set to "text/plain" to indicate plain text.
        return Response("OK", status=200, content_type="text/plain")
