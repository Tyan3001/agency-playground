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


# ----- FIXED #1: Returns 200 (OK) -----
@app.get("/health")
def health():
    from fastapi.responses import JSONResponse
    # Fixed: Returns status_code=200
    return JSONResponse(content={"status": "ok"}, status_code=200)


# ----- FIXED #2: Input validation via Pydantic -----
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


# ----- BUG #3: Off-by-one error in user lookup -----
@app.get("/users/{user_id}")
def get_user(user_id: int):
    # BUG: Looks up (user_id - 1) instead of user_id.
    # So GET /users/1 returns user 0 (doesn't exist) → 404
    # and GET /users/2 returns user 1 (Alice) instead of Bob.
    actual_id = user_id  # <-- fixed off-by-one bug
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
