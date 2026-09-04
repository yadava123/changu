# ChanGu End-to-End Integration Status

This report reflects the current implementation and executed tests. `PASS` means the behavior is covered by existing or focused backend tests. `PARTIAL` identifies an intentional limitation in the current data model or an unexecuted browser choreography.

## Workflow status

| Workflow | Status | Implementation |
| --- | --- | --- |
| Food/shop order creation | PASS | Cart, address, checkout, order creation, vendor notification, ownership checks, and payment endpoints use the database. |
| Vendor workflow | PASS | Vendor status transitions are enforced: `PENDING -> CONFIRMED -> PREPARING -> READY_FOR_PICKUP`. |
| Driver food delivery | PASS | Ready orders create one delivery, notify active online drivers, lock on acceptance, set `DRIVER_ASSIGNED`, and notify customer/vendor. |
| Parcel workflow | PASS | Customer ownership, online active-driver matching, locked acceptance, pickup, transit, out-for-delivery, completion, and customer notifications are implemented. |
| Ride workflow | PASS | Online active-driver matching, locked acceptance, valid arrival/start/completion transitions, cancellation ownership, and customer notifications are implemented. |
| Siren workflow | PASS | Provider matching, locked acceptance, on-the-way, arrived, service-started, resolved, customer notifications, and provider busy guards are implemented. |
| AI workflow | PASS | AI requests go through `/api/ai/chat`; conversations and usage are user-owned and API keys remain backend-only. AI is read-only over ChanGu actions. |
| Order payment | PASS | Backend-owned order payment success/failure/refund records `PaymentTransaction`; success uses a row lock and ownership check. |
| Parcel/ride payments | PASS | The shared `PaymentTransaction` ledger now supports nullable order references plus `PARCEL` and `RIDE` service references; payment is allowed only after delivery/completion and is idempotent. |
| Siren payments | PARTIAL | Siren requests have no configured price or payment field, so no unsupported fee or transaction was invented. |
| Real-time notifications | PASS | `NotificationService` persists user-scoped notifications and publishes them through the existing authenticated WebSocket manager. |
| Full browser E2E choreography | PARTIAL | Backend workflow coverage is present; automated browser role choreography and mobile screenshots were not added in this pass. |

## Database and API changes

- Added `DRIVER_ASSIGNED` to `OrderStatus`.
- Added `IN_SERVICE` to `EmergencyStatus`.
- Added `/api/driver/parcels/{parcel_id}/out-for-delivery`.
- Added `/api/provider/requests/{request_id}/service-started`.
- Added `/api/payments/services/{service_type}/{service_id}/success` for completed parcels and rides.
- Added nullable `order_id`, `service_type`, and `service_id` to payment transactions through Alembic revision `20260904_21`.
- Ready vendor orders now create a delivery and notify eligible active online drivers.
- Driver delivery acceptance updates the order to `DRIVER_ASSIGNED` and notifies the vendor.
- Transport transitions notify the customer after each persisted state change.
- Driver acceptance checks prevent overlapping active delivery, parcel, and ride jobs.
- Payment success locks the owned order or completed service row before creating a success transaction.

The new status values use the project's existing non-native SQLAlchemy enums, so no database migration is required for the current schema representation. Production deployments should still run the normal Alembic upgrade check.

## Security

- Customer orders, parcels, rides, Siren requests, conversations, and payments are filtered by authenticated owner.
- Vendor order updates use vendor ownership resolution and role guards.
- Driver delivery and transport transitions require the authenticated driver's assigned record.
- Provider transitions require the authenticated provider's assigned request and verified active status.
- Acceptance paths use `with_for_update()` and reject already-claimed resources with `409`.
- Admin APIs use `require_role(UserRole.ADMIN)`.

## Verification

- `tests/test_auth.py`: `8 passed`.
- Transport, vendor, and commerce tests: `13 passed`.
- Siren, commerce, and phase integration tests: `10 passed`.
- Full backend suite: `40 passed` with `python -m pytest -q -p no:unraisableexception`.
- Frontend production build: passed with `npm run build`.
- Browser verification: role chooser, customer registration, customer login, `/home`, and `/customer/dashboard` passed against the running API; mobile dashboard had no horizontal overflow at 390px.

Remaining warnings are existing `datetime.utcnow()` deprecations in Siren code and the Starlette multipart compatibility warning. They do not change workflow outcomes.