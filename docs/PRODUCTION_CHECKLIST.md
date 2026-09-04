# Production Launch Checklist

Deployment preparation is complete. ChanGu is not deployed or published from this repository. Hosting, domain, TLS, payment approval, and external credentials remain owner-provided requirements.

## Verified

- [x] Frontend production build succeeds.
- [x] Backend Docker image has a production Uvicorn command.
- [x] Alembic migration chain has one head.
- [x] `/health`, `/health/db`, `/ready`, and `/health/live` exist.
- [x] Frontend API and WebSocket origins are configurable or same-origin.
- [x] Authenticated APIs use server-side role and ownership checks.
- [x] Security headers, request IDs, CORS configuration, and rate limits exist.
- [x] `.env`, databases, virtual environments, and build artifacts are ignored.

## Owner or staging requirements

- [ ] Provision PostgreSQL and set `DATABASE_URL` with SSL where required.
- [ ] Inject a generated `SECRET_KEY` and explicit `CORS_ORIGINS` through a secret manager.
- [ ] Run `alembic upgrade head` as a release step.
- [ ] Configure HTTPS/WSS reverse proxy and SPA fallback.
- [ ] Configure encrypted backups, restore testing, monitoring, and alerting.
- [ ] Configure an approved payment provider, signed webhooks, reconciliation, and refunds.
- [ ] Configure Gemini/Groq keys, maps, email/SMS/push services as required.
- [ ] Run staging smoke tests for all roles and core service flows.
- [ ] Replace process-local rate limiting and socket coordination before horizontal scaling.

## Mobile

- [x] Responsive web build succeeds.
- [ ] Add and test Android packaging; no native project currently exists.
- [ ] Provide package ID, icons, store assets, privacy URL, support contact, and Play account.

## Legal and support

- [ ] Review and publish `PRIVACY.md` and `TERMS.md`.
- [ ] Review Siren safety and AI disclaimer text.
- [ ] Configure a real support contact.

## Commands

```powershell
Push-Location backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000
Pop-Location

Push-Location frontend
npm ci
npm run build
npm run preview
Pop-Location

Push-Location backend
pytest -q tests/test_phase11.py tests/test_phase12.py tests/test_health.py
Pop-Location
```
