# Agency Playground

A deliberately broken FastAPI app for testing the Phone-to-PR Agency.

## Bugs to Fix

1. ~~**`GET /health` returns 418** — Should return 200~~ (Done)
2. **`POST /users` crashes on missing fields** — Should return 422 with validation errors
3. ~~**`GET /users/{id}` has off-by-one** — Returns wrong user~~ (Done)
4. ~~**`DELETE /users/{id}` is missing** — Tests exist, endpoint doesn't~~ (Done)

## Running Tests

```bash
pip install fastapi uvicorn pytest httpx
pytest tests/ -v
```

Expected: 8 of 14 tests fail until bugs are fixed.
