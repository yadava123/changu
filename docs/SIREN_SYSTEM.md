# Siren System

## Customer flow

Customers create authenticated requests through `/api/emergency/requests` and use the protected Siren customer pages. The backend validates service type, priority, description, contact, address, and optional coordinates. Customers can read and cancel only their own requests. A customer cannot create another active request until the current one is resolved or cancelled.

The status flow is:

`SEARCHING -> PROVIDER_ASSIGNED -> ACCEPTED -> ON_THE_WAY -> ARRIVED -> IN_SERVICE -> RESOLVED`

Customer cancellation is allowed before arrival and notifies an assigned provider.

## Provider flow

Approved, verified, active providers control online availability through `/api/provider/status`. Available requests are matched by the backend against the existing emergency type to provider type mapping and online eligibility. Acceptance locks the request row, checks provider type, and prevents concurrent active work for the same provider.

Providers transition assigned requests through on-the-way, arrived, service-started, and resolve endpoints. Assigned providers can cancel before arrival; the customer is notified. Every transition checks provider ownership and the expected previous status.

## Location and real time

Provider GPS updates use `/api/provider/location`. Only active verified online providers can publish location. Events are sent through the existing tracking/WebSocket event infrastructure to the request owner. Customer tracking is owner-scoped and provider tracking is assignment-scoped.

## Admin and security

Provider approval uses the existing application workflow. Admin monitoring uses `/api/admin/siren` with status, request ID search, and bounded pagination. Provider APIs require the emergency-provider role and active verification; admin APIs require the admin role.

## Payments, earnings, and reviews

The current schema does not define Siren pricing, payment status, provider earnings settlement, or a Siren review model. The operational request and tracking flow therefore remains active without invented charges or fake payment success. These financial and review rules require an explicit business decision and migrations before implementation.

## Testing

Siren tests cover provider application approval, online status, customer ownership isolation, provider matching, lifecycle transitions, and duplicate active-request rejection. Run `pytest -q tests/test_siren.py` and `pytest -q` for the full backend suite. Build the frontend with `npm run build`.

## Known limitations

There is no distance-based provider matching, provider rematching after cancellation, saved-address integration, service pricing, refund flow, provider earnings settlement, or Siren rating table. The existing safety notice directs users to official emergency services for immediate life-threatening situations.
