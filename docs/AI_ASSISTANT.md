# ChanGu AI Assistant

## Architecture

The frontend uses the authenticated `/api/ai` API. The backend owns conversations, retrieves scoped ChanGu data through `app.ai.tools`, and chooses the configured provider. Rules mode remains the local/default fallback. Optional provider adapters are implemented for Gemini and Groq in `app.ai.provider`.

Provider selection is controlled by `AI_PROVIDER`:

- `rules`: deterministic ChanGu intent/tools, no external key required.
- `gemini`: Gemini HTTP API using `GEMINI_API_KEY`.
- `groq`: Groq OpenAI-compatible HTTP API using `GROQ_API_KEY`.

If the selected provider fails and another configured key is available, the backend tries that provider. If all external providers fail, the verified rules response remains available. Provider failures are not returned to users.

## Configuration

Copy the backend environment example and set secrets only in the server environment:

```text
AI_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=
AI_MODEL=gemini-2.0-flash
AI_MAX_TOKENS=500
AI_TEMPERATURE=0.2
AI_TIMEOUT_SECONDS=20
AI_DAILY_REQUEST_LIMIT=30
```

For Groq, use `AI_PROVIDER=groq`, set `GROQ_API_KEY`, and choose a Groq-supported model such as `llama-3.1-8b-instant`. Never put these values in frontend code, browser storage, or public environment variables.

## API and security

- `POST /api/ai/chat`: authenticated chat with optional owned `conversation_id`.
- `GET /api/ai/conversations`: current user conversations.
- `GET /api/ai/conversations/{id}`: current user's messages only.
- `POST /api/ai/conversations`: create a conversation.
- `DELETE /api/ai/conversations/{id}`: delete an owned conversation.
- `GET /api/ai/health`: admin-only configuration health summary without secrets.
- `GET /api/ai/analytics`: admin-only usage aggregates.

The backend derives identity from the authenticated token. Tools query only data owned by the current user or public catalog records. AI-generated text cannot bypass API authorization, create bookings, cancel services, or mutate transactions; sensitive writes remain explicit API workflows.

## Context and limits

The existing intent/tool layer supplies real Food, Shop, order, cart, parcel, ride, and Siren context. Parcel and ride status lookups are scoped to the authenticated customer, including numeric ID lookups. Conversations and usage are stored in `AIConversation`, `AIMessage`, and `AIUsage`. Messages are limited to 2,000 characters, requests are rate-limited, and daily usage follows `AI_DAILY_REQUEST_LIMIT`.

The assistant does not expose payment credentials, API keys, passwords, tokens, or unrelated users' records. Siren guidance directs users to official emergency services for immediate danger and does not claim emergency dispatch.

## Testing and local commands

```powershell
Push-Location backend
pip install -r requirements.txt
pytest -q tests/test_phase11.py
Pop-Location
Push-Location frontend
npm run build
Pop-Location
```

The provider integrations require a valid server-side key for live external responses. Rules mode can be used for local tests without any provider key.

## Known limitations

The current assistant is read-oriented. It does not execute ride booking, parcel creation, order cancellation, Siren dispatch, refunds, or profile updates through chat. Those workflows require explicit confirmation UX and dedicated backend action contracts before being exposed safely.
