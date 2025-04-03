from fastapi import Header, FastAPI, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
import httpx
from jose import jwt
from datetime import datetime, timezone
from typing import Optional

app = FastAPI()

# Base URLs for backend services.
# In production, consider using environment variables or a configuration service.
BASE_URL = "http://internal-bookstore-dev-InternalALB-1681681316.us-east-1.elb.amazonaws.com:3000"

# ---------------------------
# X-Client_Type Header Check
# ---------------------------
def require_client_type(x_client_type: Optional[str] = Header(None)):
    if x_client_type is None:
        raise HTTPException(status_code=400, detail="Missing 'X-Client-Type' header")

# ----------------------------
# JWT Authentication
# ----------------------------

ACCEPTED_USERS = {"starlord", "gamora", "drax", "rocket", "groot"}
REQUIRED_ISSUER = "cmu.edu"
JWT_ALGORITHM = "HS256"

def validate_jwt_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header must start with 'Bearer '")

    token = authorization.removeprefix("Bearer ").strip()

    try:
        # Decode the token without verifying signature
        payload = jwt.get_unverified_claims(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Malformed token")

    # Validate "sub"
    sub = payload.get("sub")
    if sub not in ACCEPTED_USERS:
        raise HTTPException(status_code=401, detail="Invalid user")

    # Validate "iss"
    iss = payload.get("iss")
    if iss != REQUIRED_ISSUER:
        raise HTTPException(status_code=401, detail="Invalid issuer")

    # Validate "exp"
    exp_timestamp = payload.get("exp")
    now = datetime.now(timezone.utc).timestamp()
    if exp_timestamp is None:
        raise HTTPException(status_code=401, detail="Missing 'exp' claim in token")
    if now > exp_timestamp:
        raise HTTPException(status_code=401, detail="Token has expired")

    return payload

    
# ---------------------------
# Book Endpoints
# ---------------------------

@app.post("/books")
async def create_book(book: dict, _=Depends(validate_jwt_token), __=Depends(require_client_type)):
    """
    Proxy POST request to create a new book.
    This calls the Django BookCreateAPIView at /books.
    """
    async with httpx.AsyncClient() as client:
        try:
            print("book request body:", book)
            response = await client.post(f"{BASE_URL}/books/", json=book)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            error_body = exc.response.json()
            raise HTTPException(
                status_code=response.status_code if response is not None else 500,
                detail=error_body
            ) from exc
        # Forward the Location header if provided
        headers = {"Location": response.headers.get("Location")} if "Location" in response.headers else {}
        return JSONResponse(content=response.json(), status_code=response.status_code, headers=headers)
    
@app.get("/books/{isbn}")
async def get_book(isbn: str, _=Depends(validate_jwt_token), __=Depends(require_client_type)):
    """
    Proxy GET request to retrieve a book by its ISBN.
    This calls the Django BookDetailAPIView (GET) at /books/<isbn>.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/books/{isbn}")
            response.raise_for_status()
        except httpx.HTTPError as exc:
            error_body = exc.response.json()
            raise HTTPException(
                status_code=response.status_code if response is not None else 500,
                detail=error_body
            ) from exc
        return response.json()

@app.get("/books/isbn/{isbn}")
async def get_books(isbn: str, _=Depends(validate_jwt_token), __=Depends(require_client_type)):
    """
    Proxy GET request to retrieve books.
    This calls the Django BookListCreateAPIView (GET) at /books.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/books/", params={"isbn": isbn} )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            error_body = exc.response.json()
            raise HTTPException(
                status_code=response.status_code if response is not None else 500,
                detail=error_body
            ) from exc
        return response.json()
    
@app.put("/books/{isbn}")
async def update_book(isbn: str, book: dict, _=Depends(validate_jwt_token), __=Depends(require_client_type)):
    """
    Proxy PUT request to update a book.
    This calls the Django BookDetailAPIView (PUT) at /books/<isbn>.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(f"{BASE_URL}/books/{isbn}", json=book)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            error_body = exc.response.json()
            raise HTTPException(
                status_code=response.status_code if response is not None else 500,
                detail=error_body
            ) from exc
        return response.json()

# ---------------------------
# Customer Endpoints
# ---------------------------

@app.post("/customers")
async def create_customer(customer: dict, _=Depends(validate_jwt_token), __=Depends(require_client_type)):
    """
    Proxy POST request to create a new customer.
    This calls the Django CustomerListCreateAPIView (POST) at /customers.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{BASE_URL}/customers/", json=customer)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            error_body = exc.response.json()
            raise HTTPException(
                status_code=response.status_code if response is not None else 500,
                detail=error_body
            ) from exc
        headers = {"Location": response.headers.get("Location")} if "Location" in response.headers else {}
        return JSONResponse(content=response.json(), status_code=response.status_code, headers=headers)

@app.get("/customers")
async def get_customer(userId: Optional[str] = Query(None), _=Depends(validate_jwt_token), __=Depends(require_client_type)):
    """
    Proxy GET request to look up a customer by userId.
    This calls the Django CustomerListCreateAPIView (GET) at /customers with query parameter userId.
    """
    if not userId:
        raise HTTPException(status_code=400, detail="Missing query parameter 'userId'")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/customers/", params={"userId": userId})
            response.raise_for_status()
        except httpx.HTTPError as exc:
            error_body = exc.response.json()
            raise HTTPException(
                status_code=response.status_code if response is not None else 500,
                detail=error_body
            ) from exc
        return response.json()

@app.get("/customers/{id}")
async def get_customer_detail(id: str, _=Depends(validate_jwt_token), __=Depends(require_client_type)):
    """
    Proxy GET request to retrieve customer details by id.
    This calls the Django CustomerDetailAPIView (GET) at /customers/<id>.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/customers/{id}")
            response.raise_for_status()
        except httpx.HTTPError as exc:
            error_body = exc.response.json()
            raise HTTPException(
                status_code=response.status_code if response is not None else 500,
                detail=error_body
            ) from exc
        return response.json()

# ---------------------------
# Health Check Endpoint
# ---------------------------

@app.get("/status")
async def status(_=Depends(validate_jwt_token), __=Depends(require_client_type)):
    """
    Health check endpoint.
    Proxies the status call to the Book Service's /status endpoint.
    The Django status endpoint returns a plain text "OK".
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/books/status")
            response.raise_for_status()
            response = await client.get(f"{BASE_URL}/customers/status")
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
