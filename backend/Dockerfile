FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1
RUN addgroup --system app && adduser --system --ingroup app app && chown -R app:app /app
USER app
CMD ["sh", "-c", "alembic upgrade head && if [ -n \"$ADMIN_EMAIL\" ] && [ -n \"$ADMIN_PASSWORD\" ]; then python -c 'from app.seed import seed_admin; seed_admin()'; fi && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
