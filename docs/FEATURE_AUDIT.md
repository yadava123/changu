# ChanGu Feature Audit

Audit basis: source inspection, backend API tests, migration checks, and frontend production builds on 2026-09-04. `WORKING` means the tested backend path and its connected UI exist; page presence alone is not treated as proof.

| Feature | Frontend | Backend/API | Database | Auth/ownership | Validation/errors | Real data | Tested | Status | Problems / fix |
|---|---|---|---|---|---|---|---|---|---|
| Authentication | Login, register, logout, expiry handling | Register, login, `/me` | `users` | Role checks and active account checks | Pydantic, generic login error, rate limits | Yes | Auth suite | WORKING | Password reset and change-password are not implemented |
| Customer discovery/search | Food, shop, explore, search states | Food, product, restaurant, search APIs | Catalog tables | Authenticated | Query validation and empty states | Yes | Discovery suite | WORKING | Explore query handoff fixed with URL query parsing |
| Products/cart/checkout | Product details, cart, address checkout | Cart totals and order creation | Cart, items, addresses, orders | Customer-owned cart/address/order | Backend prices, stock, quantity checks | Yes | Commerce suite | WORKING | UPI option remains unavailable; COD is the supported checkout method |
| Orders | Orders, details, timeline, tracking refresh | Create, cancel, vendor and delivery transitions | Orders, order items, delivery | Customer/vendor/driver ownership | Status transition validation | Yes | Commerce/driver suites | WORKING | No rejected order status exists |
| Payments/refunds | COD checkout; no external gateway UI | Test success/failure, refund, and transaction history endpoints | Orders plus `payment_transactions` | Customer order ownership; admin refund | Idempotent status checks | Yes | Phase 11/payment tests | PARTIALLY WORKING | No external gateway integration; sandbox provider still required |
| Vendor | Application, profile, catalog, dashboard, orders | Vendor APIs and admin approval | Vendors, applications, products, restaurants | Vendor-owned records | Backend role/ownership checks | Yes | Vendor suite | WORKING | Earnings/commission ledger is not implemented |
| Driver/delivery | Driver workspace and transitions | Online, availability, accept, pickup, delivery | Drivers, deliveries, last_seen | Driver-owned delivery; race validation | State transition and BUSY checks | Yes | Driver suite | WORKING | No GPS tracking; assignment is self-claim |
| Emergency provider/Siren | Customer and provider flows | Request, accept, on-way, arrived, resolve | Emergency requests/providers | Provider-owned requests | State/provider-type checks | Yes | Siren suite | WORKING | Provider earnings/payment/reviews are absent |
| Admin | Dashboard, users, operations, applications, audit, notifications | Protected admin APIs | Audit and platform tables | Admin-only dependencies | Backend enforced | Yes | Existing API suites | PARTIALLY WORKING | Some operation screens are read-only; AI analytics route fixed |
| Notifications/realtime | Bell, center, preferences, toast | CRUD, preferences, authenticated WebSocket | Notifications/preferences | User-scoped | Deduplication, pagination, auth | Yes | Notification/Phase 11 suites | WORKING | Cross-instance socket fanout is not provided |
| Parcel/Rides | Customer forms, history, detail/tracking pages | Create, backend estimates/fares, cancel, driver accept and lifecycle APIs | `parcels`, `rides` | Customer and assigned-driver ownership | Pydantic validation, transitions, row locking | Yes | Transport integration tests | PARTIALLY WORKING | Driver transport UI, automated assignment, payment integration, and realtime lifecycle events remain |
| AI assistant | Chat UI | Rules/provider API, usage limit, analytics | Conversations, messages, usage | Customer-owned conversations/admin analytics | Safe provider failure handling | Yes | Existing AI path | PARTIALLY WORKING | External provider integration depends on configured key |
| Recommendations/favorites | Recommendation strips and preferences | Recommendation service and events | Recommendation/event tables | User-scoped | API-backed | Yes | Partial discovery coverage | PARTIALLY WORKING | Similar-items endpoint and richer catalog metadata are incomplete |
| Profile/settings | Profile editing, password change, preferences, notifications | Authenticated profile/password/preferences APIs | Users and preference tables | User-scoped | Current-password and form validation | Yes | Auth/build tests | WORKING | Address management remains a separate checkout workflow |
| Reviews/ratings | Authenticated review form and route | Create/read review for delivered orders | `reviews`, unique user/order and rating constraint | Customer-owned completed order | Pydantic rating/comment checks, duplicate protection | Yes | Migration and build pass | WORKING | Vendor/product aggregate ratings are not yet implemented |
| Offers/coupons | Coupon entry in checkout | Admin coupon creation and order-time validation | `coupons`, `coupon_usages`, usage indexes/constraints | Admin creation; customer order ownership | Expiry, minimum, limits, non-negative discounts | Yes | Coupon integration test | WORKING | Promotional offers/campaign UI is not implemented |
| Loyalty/referrals/finance | Rewards page with points and referral code | Loyalty balance/transactions, delivered-order awards, referral apply APIs | `loyalty_accounts`, `loyalty_transactions`, `referrals` | User-scoped; self/duplicate referral protection | Idempotent reward events and unique referral constraints | Yes | Growth integration test | PARTIALLY WORKING | Redemption rules, referral rewards, and full financial ledger are not configured |
| Production/deployment | Vite build and error boundary | Health/readiness, migrations, Docker/CI | Alembic migrations | Environment validation | Security headers, rate limits, request IDs | Deployment-managed | Build/tests | PARTIALLY WORKING | HTTPS, managed backups, restore drill, and hosting are operator responsibilities |

## Verified commands

- `python -m pytest -q`: 40 passed
- `alembic upgrade head`: passed through `20260904_20` with reviews, payment transactions, coupons, loyalty, referrals, parcels, and rides
- `npm run build`: passed
- `alembic upgrade head`: passed through `20260904_15`
- Health/security-header smoke check: passed

## Priority follow-up

1. Add a real sandbox payment provider and transaction/refund records before enabling online payment UI.
2. Add review, loyalty, referral, coupon, and earnings domains only when their business rules are defined.
3. Run browser E2E flows at 375px, 768px, and desktop widths.
4. Replace process-local rate limiting and WebSocket coordination before horizontal scaling.
