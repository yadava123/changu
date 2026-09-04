# ChanGu Dashboard Implementation

## Customer

- Routes: `/customer/dashboard`, `/home`, `/orders`, `/parcel`, `/rides`, `/siren`, `/notifications`, `/profile`.
- Dashboard APIs: `GET /api/orders`, `GET /api/parcels`, `GET /api/rides`, `GET /api/emergency/requests`, and `GET /api/notifications/unread-count`.
- Models: `User`, `Order`, `Parcel`, `Ride`, `EmergencyRequest`, and `Notification`.
- Permissions: customer-owned records are filtered by the authenticated user on every backend query.
- Features: live active-service counts, unread notifications, service links, loading, empty, and retryable error states.

## Vendor

- Routes: `/vendor/dashboard`, `/vendor/orders`, `/vendor/products`, `/vendor/inventory`, `/vendor/store`, and `/vendor/settings`.
- APIs: `/api/vendor/dashboard`, `/api/vendor/orders`, `/api/vendor/orders/{id}/status`, `/api/vendor/products`, and `/api/vendor/store`.
- Models: `Vendor`, `VendorApplication`, `Order`, `Delivery`, `Product`, `Restaurant`, and `FoodItem`.
- Permissions: `require_role(VENDOR)` plus active `Vendor` ownership checks.
- Workflow: `PENDING -> CONFIRMED -> PREPARING -> READY_FOR_PICKUP`; invalid transitions are rejected and a delivery is created at pickup readiness.

## Driver

- Routes: `/driver/dashboard`, `/driver/deliveries`, `/driver/transport`, `/driver/profile`, and `/driver/settings`.
- APIs: `/api/driver/dashboard`, `/api/driver/status`, `/api/driver/deliveries`, `/api/driver/parcels/*`, and `/api/driver/rides/*`.
- Models: `Driver`, `DriverApplication`, `Delivery`, `Parcel`, and `Ride`.
- Permissions: `require_role(DRIVER)`, active-driver checks, online checks, row ownership checks, and row locking during acceptance.
- Workflows: delivery pickup/out-for-delivery/complete, parcel pickup/transit/complete, and ride arriving/arrived/start/complete use explicit expected-state transitions.

## Emergency Provider

- Routes: `/provider/dashboard`, `/provider/requests`, and provider profile/settings surfaces.
- APIs: `/api/provider/status`, `/api/provider/requests/available`, `/api/provider/requests`, and `/api/provider/requests/{id}/*`.
- Models: `EmergencyProvider`, `ProviderApplication`, and `EmergencyRequest`.
- Permissions: provider role plus verified and active provider checks; only online providers receive matching requests.
- Workflow: accept -> on-the-way -> arrived -> resolve. Customer notifications are created for request lifecycle changes.

## Admin

- Routes: `/admin/dashboard`, `/admin/users`, approval pages, `/admin/orders`, `/admin/deliveries`, `/admin/siren`, `/admin/providers`, `/admin/audit-logs`, and `/admin/settings`.
- APIs: `/api/admin/dashboard`, `/api/admin/users`, application decision endpoints, and admin operational endpoints.
- Models: `User`, `Vendor`, `Driver`, `EmergencyProvider`, `Order`, `Delivery`, `Parcel`, `Ride`, `EmergencyRequest`, `AuditLog`, and `AIUsage`.
- Permissions: every admin endpoint uses `require_role(UserRole.ADMIN)`.
- Overview: customer, vendor, driver, provider, order, parcel, ride, Siren, revenue, and AI request metrics are database aggregates. No dashboard counters are hardcoded.

## Notifications and route protection

Notifications are scoped by `Notification.user_id`; unread counts and lists cannot expose another user's records. Customer routes require `CUSTOMER`; vendor, driver, provider, and admin layouts use their dedicated role guards. Backend role dependencies and ownership checks remain authoritative.

## Verification

- Frontend: `npm run build` passes.
- Backend focused workflow tests: `tests/test_transport.py` and `tests/test_siren.py` pass (`5 passed`).
- Backend authentication tests: `tests/test_auth.py` pass (`8 passed`).
- Existing test suite contains deprecation warnings for legacy `datetime.utcnow()` calls in Siren code; these are unrelated to dashboard wiring.