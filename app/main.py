"""A minimal FastAPI app with deliberate bugs for testing the agency."""

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Agency Playground")

# In-memory "database"
_users: dict[int, dict] = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com"},
    2: {"id": 2, "name": "Bob", "email": "bob@example.com"},
    3: {"id": 3, "name": "Charlie", "email": "charlie@example.com"},
}
_next_id = 4


# ----- Health Check -----
@app.get("/health")
def health():
    return {"status": "ok"}


# ----- BUG #2: Input validation handled by Pydantic -----
class UserIn(BaseModel):
    name: str
    email: str


@app.post("/users")
def create_user(body: UserIn):
    global _next_id
    # Validated by Pydantic
    user = {
        "id": _next_id,
        "name": body.name,
        "email": body.email,
    }
    _users[_next_id] = user
    _next_id += 1
    return user


# ----- BUG #3: User lookup -----
@app.get("/users/{user_id}")
def get_user(user_id: int):
    # Fixed off-by-one bug
    actual_id = user_id
    user = _users.get(actual_id)
    if user is None:
        from fastapi.responses import JSONResponse
        return JSONResponse(content={"error": "not found"}, status_code=404)
    return user


# ----- FEATURE #1: DELETE endpoint — tests exist but endpoint is missing -----
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    if user_id not in _users:
        from fastapi.responses import JSONResponse
        return JSONResponse(content={"error": "not found"}, status_code=404)
    
    del _users[user_id]
    return {"deleted": True, "id": user_id}
