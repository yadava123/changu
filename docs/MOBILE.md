# Mobile Readiness

## Current status

ChanGu currently has a responsive React/Vite web frontend. The repository contains no Capacitor, Android, React Native, Flutter, iOS, Gradle, or native project. No mobile release build has been produced or published.

The supported mobile path today is responsive web deployment over HTTPS. The frontend uses the configured `VITE_API_URL` and existing browser WebSocket/location APIs.

## Future packaging

Before creating an Android wrapper, the owner must provide a production HTTPS frontend/API origin, application ID, app name, icon assets, splash assets, privacy policy URL, support contact, and store account. A Capacitor wrapper is the least disruptive option because it can reuse the current Vite build, but it should be added and tested as a separate release task.

Do not embed API keys, database credentials, JWT secrets, payment secrets, or AI provider keys in a mobile bundle. Location and notification permissions should be requested only for flows that need them and documented for store review.

## Mobile checks completed

- Frontend production build succeeds.
- Existing layouts use responsive CSS and mobile route aliases.
- No native packaging or release artifact exists yet.

## Owner requirements

- Android package/application ID
- Google Play developer account
- Store listing, screenshots, privacy policy, terms, support contact
- Production HTTPS API and frontend URLs
- Review of location, notification, and network permissions
