# Environment variables

Copy the appropriate backend example file to a deployment secret store. Do not commit `.env` files.

| Variable | Required | Purpose |
|---|---:|---|
| `APP_ENV` | Yes | `development` or `production` |
| `DEBUG` | Yes | Must be `false` in production |
| `DATABASE_URL` | Yes | SQLAlchemy database URL; production must use PostgreSQL |
| `SECRET_KEY` | Yes | Random JWT signing secret; production requires 32+ characters |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Yes | JWT lifetime |
| `CORS_ORIGINS` | Yes | JSON list of explicit frontend origins |
| `AI_PROVIDER` | No | Configured AI provider, default `rules` |
| `GEMINI_API_KEY` | No | Backend-only Gemini credential |
| `LOG_LEVEL` | No | Logging level |
| `RATE_LIMIT_ENABLED` | No | Enables auth rate limits |
| `LOGIN_RATE_LIMIT` | No | Login requests per minute per client |
| `REGISTER_RATE_LIMIT` | No | Registration requests per minute per client |
| `DB_POOL_SIZE` | No | Base production connection pool size |
| `DB_MAX_OVERFLOW` | No | Temporary pool overflow |
| `DB_POOL_TIMEOUT` | No | Pool checkout timeout in seconds |

Frontend only receives public `VITE_API_URL` configuration. Never put JWT secrets, database credentials, or private AI keys in frontend variables.
