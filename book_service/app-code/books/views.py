import json
import os
import time
from pathlib import Path

import requests
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

# ---------------------------------------------------------------------------
# Circuit‑breaker parameters
# ---------------------------------------------------------------------------
CIRCUIT_FILE       = Path("/tmp/related_books_circuit.json")   # mount an emptyDir here in K8S
RECOMMEND_SERVICE_URL = "localhost:3000"                # external service URL
OPEN_INTERVAL_SECS = 60                                        # stay OPEN for 60 s
REQUEST_TIMEOUT    = 3                                         # external call timeout

# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------
def _load_state():
    """
    Returns {'open': bool, 'opened_at': float}.
    Missing file == CLOSED.
    """
    if not CIRCUIT_FILE.exists():
        return {"open": False, "opened_at": 0.0}

    try:
        with CIRCUIT_FILE.open("r") as fp:
            data = json.load(fp)
        # Coerce types / defaults
        return {
            "open": bool(data.get("open", False)),
            "opened_at": float(data.get("opened_at", 0.0)),
        }
    except Exception:
        # Corrupted file → fail closed
        return {"open": False, "opened_at": 0.0}

def _save_state(open_, opened_at=0.0):
    """Persist breaker state atomically."""
    tmp_path = CIRCUIT_FILE.with_suffix(".tmp")
    with tmp_path.open("w") as fp:
        json.dump({"open": open_, "opened_at": opened_at}, fp)
    os.replace(tmp_path, CIRCUIT_FILE)  # atomic rename


def _should_fast_fail(state):
    """Return True if circuit is OPEN _and_ still inside the 60‑second window."""
    return state["open"] and (time.time() - state["opened_at"] < OPEN_INTERVAL_SECS)

# ------------------------------------------------------------
# API View for retrieving related books from external service (GET /books/<isbn>/)
# ------------------------------------------------------------
class BookRelatedAPIView(APIView):
    def get(self, request, isbn, format=None):
        # Retrieve the book object by its ISBN; if not found, a 404 error is automatically returned.
        print("isbn in request:", isbn)

        # --- circuit‑breaker pre‑check --------------------------------------------------
        state = _load_state()
        if _should_fast_fail(state):
            # Circuit already OPEN → respond immediately
            return Response({"message": "Circuit open — try later"}, status=503)

        # After 60 s we let *one* request probe the downstream service.
        # (If the breaker is CLOSED `state["open"]` is False and we simply continue.)
        url = f"http://{RECOMMEND_SERVICE_URL}/recommended-titles/isbn/{isbn}"

        try:
            ext_resp = requests.get(url, timeout=REQUEST_TIMEOUT)

        except requests.exceptions.Timeout:
            # ---- TIMEOUT → OPEN the circuit & report 504 ------------------------------
            _save_state(open_=True, opened_at=time.time())
            return Response({"message": "External service timeout"}, status=504)

        # ---- External service returned within 3 s --------------------------------------
        status = ext_resp.status_code

        if status == 200:
            # success path ⇒ be sure circuit is CLOSED
            _save_state(open_=False)
            return Response(ext_resp.json(), status=200)

        if status in (204, 404):
            # “no related books”            –> 204 + EMPTY body
            _save_state(open_=False)
            return Response(status=204)

        if status == 503:
            # Downstream signals its own OPEN breaker
            # Treat like a failure, but *keep* our breaker state:
            #   - if it was CLOSED, we OPEN it now
            #   - if it was OPEN and we were probing (first call after 60 s),
            #     we refresh the timer.
            _save_state(open_=True, opened_at=time.time())
            return Response({"message": "Circuit open (downstream unavailable)"}, status=503)

        # Any other code is an unexpected failure – treat like 500 for safety
        _save_state(open_=True, opened_at=time.time())
        return Response({"message": f"Unexpected downstream status {status}"}, status=503)


# ------------------------------------------------------------
# API View for the status endpoint (GET /status)
# ------------------------------------------------------------
class StatusAPIView(APIView):
    def get(self, request, format=None):
        # Return a plain text response "OK".
        # Note: content_type is explicitly set to "text/plain" to indicate plain text.
        return Response("OK", status=200, content_type="text/plain")
