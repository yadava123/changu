# Parcel Delivery

## Current flow

Customers can create and list authenticated parcels through `/api/parcels` and use `/parcel` or `/customer/parcels`. Parcel creation validates addresses, names, package type, and positive weight through `ParcelCreate`; the backend calculates the stored fare. Customers can inspect only their own parcels and cancel only pending or accepted parcels.

Drivers use `/api/driver/parcels/available` and `/api/driver/parcels/{id}/accept`. Acceptance locks the parcel row, checks driver eligibility and active-job rules, assigns one driver, and notifies the customer. Assigned drivers advance parcels through pickup, transit, out-for-delivery, and delivered transitions. Every transition verifies the authenticated driver owns the parcel and matches the expected previous status. Completion creates the existing earning record idempotently through the financial service.

## Status machine

`PENDING -> ACCEPTED -> PICKED_UP -> IN_TRANSIT -> OUT_FOR_DELIVERY -> DELIVERED`

Customer cancellation is allowed only from `PENDING` or `ACCEPTED`. Invalid transitions and second driver acceptance return errors. Customer and driver ownership checks are enforced in the backend.

## Tracking and notifications

The existing tracking endpoint publishes parcel location events for the assigned driver's active parcels. Customer tracking is restricted to the parcel owner. Existing notification services are used for parcel creation, assignment, status changes, and payment events.

## Admin monitoring

Admins can use `/api/admin/parcels` with `status`, numeric parcel ID `search`, `page`, and `limit` filters. The protected `/admin/parcels` page uses this endpoint and the existing admin operations surface.

## Payment and fare limitations

Parcel records now persist `payment_status`. New parcels are pending payment, the existing payment service can confirm payment before dispatch, and driver matching exposes only paid parcels. Paid parcels cannot be cancelled through the customer endpoint because a parcel refund workflow is not yet supported. Fare calculation currently uses the existing weight-based backend function; there is no distance, dimensions, saved-address, prohibited-item, refund, proof-of-delivery, or idempotency-key model for parcels. These require explicit business rules and migrations before production controls are added.

## Testing

Transport tests cover customer creation and ownership isolation, driver eligibility, and single acceptance. Run `pytest -q tests/test_transport.py` for the focused suite and `pytest -q` for the complete backend suite. The frontend production build validates parcel route wiring.
