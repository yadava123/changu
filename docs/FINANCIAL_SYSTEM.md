# ChanGu Financial System

## Architecture

ChanGu keeps customer payment transactions in `payment_transactions` and partner settlement in `earning_records`. Partner wallet balances are stored in `wallets`; every balance change has a matching immutable `wallet_transactions` row.

## Payment flow

- Orders are priced and persisted by the backend during checkout.
- Order payment success uses an authenticated, locked order row and creates one verified `PaymentTransaction`.
- Completed parcels and rides use `/api/payments/services/{service_type}/{service_id}/success`; ownership and terminal status are checked on the backend.
- Repeated success requests return the existing transaction and do not create duplicates.
- Frontend amounts and transaction IDs are never trusted.

The current project has no external gateway or webhook credentials configured. These endpoints are internal verified test-mode records, not a claim of card-provider settlement. Provider webhook verification should be added when a real gateway is selected.

## Earnings and commission

Completion events create idempotent `EarningRecord` rows:

- Food delivery: driver delivery earning and vendor order amount.
- Parcel completion: driver earns the backend parcel price.
- Ride completion: driver earns the backend ride fare.

No platform commission percentage exists in the current business configuration, so commission is recorded as zero rather than inventing a percentage. The ledger supports a future commission amount.

## Wallet

Partner wallet balances are updated only by `financial_service.settle_earning`. The source uniqueness constraint and wallet idempotency key prevent duplicate credits. Wallet access is restricted to the authenticated partner account through `/api/earnings/wallet`.

Customer wallet funding, withdrawals, and spending are not enabled because no business rules or payment provider flow exist for them.

## Refunds and cash

Order refunds remain admin-only and create a refund transaction. Cash-on-delivery orders are marked paid when the delivery is completed according to the existing cash rule; no online payment transaction is created for the cash method.

Parcel, ride, and Siren cancellation-fee/refund policies are not defined by the existing product rules, so the system does not silently invent them. Siren has no configured price and therefore has no settlement record.

## Admin finance

- `GET /api/admin/financial-summary` returns database-backed revenue, payment status, commission, and partner earning totals.
- `GET /api/admin/financial-transactions` supports transaction ID, payment status, role, pagination, and admin authorization.
- `/admin/financials` displays the summary and transaction search.

## Customer and partner UI

- `/payments` shows authenticated customer payment history.
- `/earnings` shows partner earnings, daily/weekly totals, wallet balance, and earning records.
- Completed parcel and ride details expose backend-verified payment actions.

## Security and idempotency

All financial APIs require authentication. Customer transactions and service payments are owner-scoped. Admin financial APIs require the admin role. Order/service rows are locked before payment verification. Earning source uniqueness and wallet transaction idempotency constraints prevent duplicate settlement.

## Database

Migration `20260904_22` creates `earning_records`, `wallets`, and `wallet_transactions`. Migration `20260904_21` adds service references to payment transactions.

## Verification

The existing backend suite and focused payment, transport, and Siren tests must pass after migrations. Frontend production build must pass. Remaining known warnings are unrelated Siren `datetime.utcnow()` deprecations and the Starlette multipart compatibility warning.
