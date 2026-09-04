# Database backup and restore

ChanGu does not create automatic backups. Production must use the managed PostgreSQL provider's encrypted backup/export facility or an operator-run `pg_dump` job.

Recommended MVP policy:

- Daily encrypted backups, with provider retention selected by the operator.
- Keep at least one recent backup outside the database host.
- Never place credentials in scripts or repository files.
- Verify a backup by restoring it to a temporary PostgreSQL database and running `alembic upgrade head` plus smoke queries for users, orders, deliveries, notifications, and payment status.

Example operator commands:

```text
pg_dump --format=custom --file=changu.dump "$DATABASE_URL"
pg_restore --clean --if-exists --dbname="$RESTORE_DATABASE_URL" changu.dump
```

Record backup date, schema revision, restore result, and responsible operator for every restore drill. No restore drill has been run by this repository automation; it must be performed against the deployment provider without touching production.
