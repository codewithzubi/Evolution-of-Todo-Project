# Backend Guidelines – Phase II

## Stack
- FastAPI 0.128+
- SQLModel + Neon PostgreSQL
- Pydantic v2 models
- JWT middleware for authentication

## Project Structure
- main.py
- models.py
- routes/tasks.py
- dependencies/auth.py
- core/config.py

## Rules
- All routes under /api/tasks
- Every route must validate JWT and filter by user_id
- Use HTTPException for errors
- Return only the authenticated user's data
