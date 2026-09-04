# Troubleshooting

- Database unavailable: verify `DATABASE_URL`, PostgreSQL reachability, credentials, and `/health/db`.
- Migration error: inspect `alembic current`, compare with `alembic heads`, and do not run `drop_all`.
- CORS error: add the exact frontend origin to `CORS_ORIGINS` and restart the backend.
- JWT error: verify `SECRET_KEY` is identical across instances and check token expiry.
- WebSocket error: use `wss://` behind HTTPS, enable proxy upgrade headers, and confirm the authenticated token.
- AI unavailable: use the rules provider or show the existing safe unavailable response; normal commerce APIs do not depend on AI.
- Payment test failure: confirm order ownership and the current payment status before retrying.
- Build failure: run `npm ci` from `frontend/` and `npm run build`; run backend tests from `backend/`.
- Missing environment variable: compare deployment secrets with `docs/ENVIRONMENT_VARIABLES.md` and the relevant example file.
