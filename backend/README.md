# ChanGu Backend

FastAPI service for the connected ChanGu platform.

Run from this directory:

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The service uses SQLite by default for local development when `DATABASE_URL` is empty. Set `DATABASE_URL` in `.env` to use PostgreSQL.
