# Ride System

## Architecture and flow

Customers request rides through `/api/rides` and can use `/rides`, `/customer/rides`, or `/customer/rides/book`. The authenticated customer owns the ride record and can read or cancel it only while the backend permits cancellation.

Eligible online active drivers receive requests through `/api/driver/rides/available`. Acceptance uses a row lock and rejects a ride already assigned to another driver. The existing active-job guard prevents a driver from accepting overlapping transport work.

The driver lifecycle is enforced by backend transitions:

`REQUESTED -> DRIVER_ASSIGNED -> DRIVER_ARRIVING -> DRIVER_ARRIVED -> RIDE_STARTED -> RIDE_COMPLETED`

Each transition verifies the assigned driver and expected previous state. Notifications are emitted through the existing notification service.

Customers cannot create a second active ride. Customer cancellation notifies an assigned driver, and an assigned driver can cancel before the ride starts through the authorized driver cancellation endpoint; both actions update the real ride record and notify the customer where applicable.

## Payment and earnings

Ride records now persist `payment_status`. A completed ride remains pending payment until the authenticated owner confirms payment through `/api/payments/services/RIDE/{id}/success`. Repeated successful callbacks return the existing transaction. Ride completion settles the existing driver earning record idempotently; payment records are customer-scoped.

## Tracking and maps

Driver location updates use `/api/driver/location` and the existing tracking/WebSocket event infrastructure. Ride tracking is restricted to the ride owner, and driver coordinates are returned only for the assigned ride. The frontend reuses the existing tracking map and opens the current real location through the configured map link.

## Admin

Admins can inspect rides through `/api/admin/rides` with status, numeric ride ID search, page, and limit parameters. The protected `/admin/rides` page uses the existing admin operations surface.

## Security

Customer ride reads and cancellations are owner-scoped. Driver transitions query by both ride ID and assigned driver ID. Driver acceptance requires an active, online driver account and rejects duplicate assignment. Admin ride monitoring requires the admin role.

## Known limitations

The current ride schema stores pickup and destination text but no geocoded coordinates, distance, duration, or final-fare inputs. The existing fare function remains a backend ride-type lookup, not a distance-aware calculation. There is no ride rating table, receipt model, driver cancellation/rematching workflow, saved-location integration, or refund workflow for rides. These require explicit business rules and migrations before production controls are added. No fake coordinates or frontend-only fare calculations were introduced.

## Testing

Transport tests cover customer ownership, backend fare assignment, ride completion payment, parcel payment, and one-driver acceptance. Run `pytest -q tests/test_transport.py` for focused coverage, `pytest -q` for the backend suite, and `npm run build` for the frontend production build.
