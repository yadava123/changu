# Production Readiness

## Verified controls

- Passwords are stored as bcrypt hashes; plaintext passwords are not returned.
- Login and registration use the existing in-process rate limiter.
- Role-specific registration and authenticated payment mutation endpoints also use bounded rate-limit buckets.
- AI requests use authenticated users, bounded message size, provider timeouts, and daily limits.
- Admin APIs use server-side role checks.
- Customer, vendor, driver, provider, payment, conversation, parcel, ride, and Siren resources use object-level ownership or assignment checks in their APIs.
- Pricing is calculated by the backend for commerce, parcels, and rides.
- Product stock is checked and decremented inside the order transaction.
- Driver/provider/ride/parcel/Siren acceptance and status transitions use backend state validation and row locks where supported.
- Payment success, failed callbacks, service payments, and refunds are idempotent at the application level for repeated requests.
- Requests receive an `X-Request-ID` response header and production errors do not expose stack traces.
- CORS uses configured origins, and the API sets content-type, frame, referrer, and CSP headers.
- `/health/live` checks process availability, `/health/db` checks database connectivity, and `/ready` reports readiness without returning secrets.

## Environment and secrets

Real secrets belong only in the backend environment. `.env`, databases, virtual environments, and build output are ignored by Git. Use the placeholder files under `backend/.env*.example` as templates. Required production values include a generated `SECRET_KEY`, a PostgreSQL `DATABASE_URL`, explicit `CORS_ORIGINS`, and any provider credentials actually used.

Frontend bundles must not receive database credentials, JWT secrets, payment secrets, Gemini/Groq keys, or admin passwords.

## Payments and financial limitations

The current payment layer is an application-level/manual verification foundation, not a live provider integration. It does not currently include signed external webhooks, provider event replay storage, payment-provider reconciliation, or a production refund provider. These are required before accepting real money.

Commission and provider earnings rules are not fully defined for every service. Do not enable live settlement until business percentages, provider integration, and reconciliation are configured.

## Backups and deployment

No backup provider or disaster-recovery automation is configured in this repository. Production deployment must provide encrypted scheduled database backups, tested restores, migration execution, TLS termination, secret storage, log retention, and alerting. The deployment checklist should be completed against the actual hosting provider.

## Testing commands

```powershell
Push-Location backend
pip install -r requirements.txt
pytest -q tests/test_phase11.py tests/test_phase12.py tests/test_health.py
Pop-Location
Push-Location frontend
npm run build
Pop-Location
```

The focused production/AI/personalization/health tests pass. The broader repository suite has previously emitted all test results but can hang during pytest process shutdown; investigate that test teardown behavior before treating it as a CI gate.

## Remaining high-priority production work

- Replace application-level payment confirmation with the approved payment provider and signed webhooks.
- Add durable idempotency keys and webhook event uniqueness constraints.
- Move rate-limit state from process memory to shared infrastructure for multiple backend instances.
- Add external error/latency monitoring and alerting.
- Configure encrypted backups and restore drills.
- Add TLS, production domain, worker deployment, and secret manager configuration.
