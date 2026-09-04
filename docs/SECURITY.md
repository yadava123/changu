# Security

- Passwords use the existing bcrypt-based password hashing flow and are never returned.
- JWTs are signed with the environment-provided secret and have an expiry.
- Backend dependencies enforce authentication, role authorization, and resource ownership.
- Production rejects debug mode, placeholder secrets, wildcard CORS, and non-PostgreSQL databases.
- Auth endpoints use configurable request limits. The current limiter is process-local and should be replaced with shared Redis or gateway limiting before multi-instance deployment.
- CORS is explicit; HTTPS and WSS must be provided by the deployment reverse proxy.
- Security headers include content type sniffing, frame, referrer, and CSP protections.
- WebSocket connections require JWT authentication, are user-scoped, capped per user, and never change authoritative business state.
- AI credentials remain backend-only and AI is not authoritative for payments, permissions, or business status.
- Payment and refund mutations are backend-controlled and ownership/admin checks are enforced.

Report suspected secrets or security defects privately to the project operator; do not include credentials in issues or logs.
