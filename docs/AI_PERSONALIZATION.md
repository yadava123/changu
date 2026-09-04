# ChanGu AI Personalization

## Existing architecture

Phase 12 extends the existing `UserPreference`, `UserEvent`, favorites, recommendation rules, and AI conversation systems. No duplicate AI profile table was introduced.

Recommendations are deterministic backend results from currently available Food and Shop records. The LLM is not responsible for inventing candidates, prices, stock, vendors, or availability.

## Privacy controls

`UserPreference` now stores:

- `personalization_enabled`: permits preference-aware personalization.
- `memory_enabled`: permits new activity events to be recorded for personalization.
- `recommendations_enabled`: permits personalized recommendation responses.

Authenticated endpoints:

- `GET /api/preferences`
- `PATCH /api/preferences`
- `DELETE /api/preferences`
- `GET /api/recommendations/home`
- `GET /api/recommendations/food`
- `GET /api/recommendations/products`
- `POST /api/events`
- `POST /api/recommendations/feedback`

When memory is disabled, new activity events are not recorded. When recommendations are disabled, recommendation endpoints return empty item sets. Clear removes the authenticated user’s preference row and activity events only. No frontend-provided user ID is trusted.

## Ranking

The existing rule engine ranks real available food and products using explicit category preferences and recent user events. Empty histories remain honest and do not create fake recommendations. Existing favorites and feedback remain user-scoped.

## Database

Migration `20260905_26_ai_preference_controls` adds `memory_enabled` and `recommendations_enabled` to `user_preferences`, defaulting to enabled for existing users.

## Testing

`tests/test_phase12.py` verifies preference updates, memory-disabled event suppression, recommendation suppression, and authenticated clear behavior. Run:

```powershell
Push-Location backend
pytest -q tests/test_phase12.py
Pop-Location
Push-Location frontend
npm run build
Pop-Location
```

## Known limitations

The current implementation does not add automatic LLM preference extraction, rating/favorite-specific ranking, recommendation impression analytics, activity summaries, natural-language structured filters, or write actions from chat. Those features require additional explicit schemas and confirmation flows; no sensitive inference or fake personalization was added.
