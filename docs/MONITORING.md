# Monitoring

Monitor these public checks and application signals:

- `/health`: process availability
- `/health/db`: database connectivity
- `/ready`: deployment readiness
- HTTP 4xx/5xx rate and latency, using request IDs for investigation
- WebSocket connection failures and reconnect volume
- Database connection pool exhaustion and migration failures

The application logs request ID, method, path, status, and duration without credentials. Configure the hosting platform or a free uptime checker to poll health endpoints. No paid monitoring service is included.
