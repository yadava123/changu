# ChanGu Notifications, Realtime, and Tracking

## Notifications

`Notification` is the single persisted notification model. Each row has a user owner, type, title, message, entity reference, read state, and event key. `NotificationService` applies user preferences and event-key idempotency before inserting. Notification rows are only queried or marked read through the authenticated user's `user_id`.

The existing notification WebSocket is `/ws?token=<JWT>`. After database commit, the notification service publishes only to the intended user's connection. The frontend reconnects with backoff, updates unread counts, shows a toast, and supports deep links for orders, deliveries, parcels, rides, Siren requests, and payments.

## Realtime tracking

Drivers and verified active providers can POST current device coordinates:

- `POST /api/driver/location`
- `POST /api/provider/location`

The backend accepts only validated latitude/longitude values, only while the actor is online, and stores the current coordinate on the driver/provider record. It does not create unlimited location history. Updates are published through the existing WebSocket as `LOCATION_UPDATED` events only to customers associated with the active delivery, parcel, ride, or Siren request.

Customer tracking reads are ownership-scoped:

- `GET /api/tracking/orders/{order_id}`
- `GET /api/tracking/parcel/{parcel_id}`
- `GET /api/tracking/ride/{ride_id}`
- `GET /api/tracking/siren/{request_id}`

An unrelated customer receives `404`; no driver/provider coordinates are exposed outside the relevant active service. Provider tracking reads are scoped to the provider's assigned Siren request.

## Maps and location permissions

The frontend uses Leaflet with OpenStreetMap tiles and attribution. `TrackingMap` renders a real map only when an authorized backend coordinate exists; it never invents a marker. OSRM is configured as the development routing/ETA provider through `VITE_ROUTING_URL` for future route and duration requests.

Environment variables:

- `VITE_MAP_TILE_URL`: OpenStreetMap-compatible tile template.
- `VITE_MAP_ATTRIBUTION`: required tile attribution.
- `VITE_ROUTING_URL`: OSRM-compatible routing endpoint.

`LocationReporter` uses browser geolocation only while the driver/provider is online, reports every 30 seconds, and handles denied or unavailable permissions without crashing.

## Matching and availability

Existing matching already requires active online drivers/providers and service/category eligibility. Location reporting is rejected while offline, and acceptance remains protected by backend ownership checks and row locks.

## Verification

- Tracking ownership and online permission test: `tests/test_tracking.py`.
- Existing notification, transport, and Siren tests continue to cover event creation and status transitions.
- Run `python -m alembic upgrade head` before starting the backend.
- Run `python -m pytest -q -p no:unraisableexception` and `npm run build`.

## Known limitations

The configured OpenStreetMap and public OSRM endpoints are suitable for development, not guaranteed production scale or SLA. A production deployment should use an operationally supported tile/routing provider and respect its usage policy. Location history and browser automation for permission prompts are not configured. The implementation deliberately shows unavailable states rather than inventing live tracking data. Existing Siren `datetime.utcnow()` deprecation warnings remain unrelated to this phase.
