from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
import httpx
from typing import Optional

app = FastAPI()

# Base URLs for backend services.
# In production, consider using environment variables or a configuration service.
BOOK_SERVICE_URL = "http://book-service:3000"
CUSTOMER_SERVICE_URL = "http://customer-service:3000"

# ---------------------------
# Book Endpoints
# ---------------------------

@app.post("/books")
async def create_book(book: dict):
    """
    Proxy POST request to create a new book.
    This calls the Django BookCreateAPIView at /books.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{BOOK_SERVICE_URL}/books", json=book)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=response.status_code if response is not None else 500,
                detail=f"Error from Book Service: {exc}"
            ) from exc
        # Forward the Location header if provided
        headers = {"Location": response.headers.get("Location")} if "Location" in response.headers else {}
        return JSONResponse(content=response.json(), status_code=response.status_code, headers=headers)

@app.get("/books/{isbn}")
async def get_book(isbn: str):
    """
    Proxy GET request to retrieve a book by its ISBN.
    This calls the Django BookDetailAPIView (GET) at /books/<isbn>.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BOOK_SERVICE_URL}/books/{isbn}")
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=response.status_code if response is not None else 500,
                detail=f"Error from Book Service: {exc}"
            ) from exc
        return response.json()

@app.put("/books/{isbn}")
async def update_book(isbn: str, book: dict):
    """
    Proxy PUT request to update a book.
    This calls the Django BookDetailAPIView (PUT) at /books/<isbn>.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(f"{BOOK_SERVICE_URL}/books/{isbn}", json=book)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=response.status_code if response is not None else 500,
                detail=f"Error from Book Service: {exc}"
            ) from exc
        return response.json()

# ---------------------------
# Customer Endpoints
# ---------------------------

@app.post("/customers")
async def create_customer(customer: dict):
    """
    Proxy POST request to create a new customer.
    This calls the Django CustomerListCreateAPIView (POST) at /customers.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{CUSTOMER_SERVICE_URL}/customers", json=customer)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=response.status_code if response is not None else 500,
                detail=f"Error from Customer Service: {exc}"
            ) from exc
        headers = {"Location": response.headers.get("Location")} if "Location" in response.headers else {}
        return JSONResponse(content=response.json(), status_code=response.status_code, headers=headers)

@app.get("/customers")
async def get_customer(userId: Optional[str] = Query(None)):
    """
    Proxy GET request to look up a customer by userId.
    This calls the Django CustomerListCreateAPIView (GET) at /customers with query parameter userId.
    """
    if not userId:
        raise HTTPException(status_code=400, detail="Missing query parameter 'userId'")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{CUSTOMER_SERVICE_URL}/customers", params={"userId": userId})
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=response.status_code if response is not None else 500,
                detail=f"Error from Customer Service: {exc}"
            ) from exc
        return response.json()

@app.get("/customers/{id}")
async def get_customer_detail(id: str):
    """
    Proxy GET request to retrieve customer details by id.
    This calls the Django CustomerDetailAPIView (GET) at /customers/<id>.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{CUSTOMER_SERVICE_URL}/customers/{id}")
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=response.status_code if response is not None else 500,
                detail=f"Error from Customer Service: {exc}"
            ) from exc
        return response.json()

# ---------------------------
# Health Check Endpoint
# ---------------------------

@app.get("/status")
async def status():
    """
    Health check endpoint.
    Proxies the status call to the Book Service's /status endpoint.
    The Django status endpoint returns a plain text "OK".
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BOOK_SERVICE_URL}/status")
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Backend status check failed: {exc}"
            )
        return {"status": response.text.strip()}

# ---------------------------
# Main entry point
# ---------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)
