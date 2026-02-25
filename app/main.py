"""A minimal FastAPI app with deliberate bugs for testing the agency."""

from fastapi import FastAPI

app = FastAPI(title="Agency Playground")

# In-memory "database"
_users: dict[int, dict] = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com"},
    2: {"id": 2, "name": "Bob", "email": "bob@example.com"},
    3: {"id": 3, "name": "Charlie", "email": "charlie@example.com"},
}
_next_id = 4


# ----- BUG #1: Returns 418 (I'm a teapot) instead of 200 -----
@app.get("/health")
def health():
    from fastapi.responses import JSONResponse
    # BUG: Should return status_code=200, not 418
    return JSONResponse(content={"status": "ok"}, status_code=418)


# ----- BUG #2: No input validation — crashes on missing fields -----
@app.post("/users")
def create_user(body: dict):
    global _next_id
    # BUG: Directly accesses body["name"] and body["email"] without validation.
    # If either is missing, this will raise a KeyError and return a 500.
    user = {
        "id": _next_id,
        "name": body["name"],
        "email": body["email"],
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
    actual_id = user_id - 1  # <-- off-by-one bug
    user = _users.get(actual_id)
    if user is None:
        from fastapi.responses import JSONResponse
        return JSONResponse(content={"error": "not found"}, status_code=404)
    return user


# ----- FEATURE #1: DELETE endpoint — tests exist but endpoint is missing -----
# TODO: Implement DELETE /users/{user_id}
# The tests in tests/test_app.py expect this endpoint to:
# 1. Delete the user with the given ID
# 2. Return {"deleted": true, "id": <user_id>} with status 200
# 3. Return 404 if the user doesn't exist
