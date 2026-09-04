# Deployment

ChanGu is not deployed by this repository. These steps prepare a deployment; the owner must provide hosting, domains, TLS, credentials, and external service accounts.

## Backend

1. Provision PostgreSQL and inject production environment variables from a secret manager.
2. Build the backend image: `docker build -t changu-backend ./backend`.
3. Run migrations as a one-time release step: `alembic upgrade head`.
4. Start without reload: `uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`.
5. Put the service behind an HTTPS reverse proxy. Proxy WebSocket traffic to `/ws` and use `wss://` publicly.
6. Configure health checks against `/health`, `/health/db`, and `/ready`.

The application does not run destructive schema creation on startup. Compose requires `SECRET_KEY` and `POSTGRES_PASSWORD` to be supplied externally.

## Frontend

Run `npm ci`, set the public API URL, run `npm run build`, and serve `frontend/dist` from the HTTPS frontend host. The API origin must be listed in backend `CORS_ORIGINS`.

For same-origin hosting, leave `VITE_API_URL` empty and proxy `/api`, `/health`, and `/ws` to the backend. For separate hosting, set `VITE_API_URL=https://api.example.com` in the frontend build environment. Configure SPA fallback to `index.html` for deep links.

## Database and release

Provision PostgreSQL, inject `DATABASE_URL`, run `alembic upgrade head` once per release, and verify `/health/db` and `/ready`. Do not run destructive schema creation on startup. Configure encrypted backups and test a restore before launch.

## Mobile and legal

The repository currently contains no native mobile project. Responsive web deployment is the supported launch path. See `MOBILE.md` for future Android packaging requirements. Publish legally reviewed `PRIVACY.md` and `TERMS.md` before collecting production user data.

## Troubleshooting

- `DEBUG` or secret startup failure: verify production environment values.
- CORS errors: use the exact frontend origin, including scheme and port.
- WebSocket failures: verify proxy upgrade support, `wss://`, and the JWT token.
- Migration failures: stop the release, inspect the migration revision, and restore the database before retrying.
