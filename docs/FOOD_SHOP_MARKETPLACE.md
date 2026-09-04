# Food + Shop Marketplace

## Customer flow

Customers use `/food` and `/shop` to browse backend-backed restaurants, food items, and products. Search and category parameters are sent to the API. Product and food detail pages link to the real catalog records. `/cart` uses the authenticated customer cart API, and `/checkout` submits only an address, payment method, and optional coupon code. Prices, taxes, delivery fees, discounts, and totals are calculated by the backend.

Customer orders are available at `/orders`, with detail and delivery-tracking routes. Order ownership is enforced by the API.

## Vendor flow

Vendors manage products and food through `/vendor/products`, `/vendor/food`, and the vendor order dashboard. Product ownership is constrained by `seller_id`; food ownership is constrained by the vendor's restaurant. Vendor order transitions are validated by the backend: pending, confirmed, preparing, and ready for pickup.

## Cart and checkout security

The cart is persisted in the database per authenticated user. A cart cannot mix food from different restaurants or products from different sellers. Cart insertion and checkout reject unavailable items and inactive stores. Checkout reloads current catalog prices and uses a database transaction. Product stock is locked where supported, checked against the requested quantity, and decremented only when the order transaction succeeds.

Orders snapshot item names and prices, calculate totals server-side, clear the cart after creation, and notify the customer and vendor. Customer order reads and cancellation are ownership-checked.

## Delivery and notifications

When a vendor marks an order ready, the existing delivery workflow creates an available delivery and notifies eligible online drivers. Driver transitions and customer tracking use the existing delivery and notification APIs.

## Coupons, payments, and reviews

Coupon validation is performed during order creation with expiration, minimum amount, global usage, and per-user usage checks. Payment records and verification use the existing payment APIs. Reviews are limited by the existing completed-order and unique-review rules.

## APIs and data

- `GET /api/food`, `GET /api/food/{id}`
- `GET /api/restaurants`, `GET /api/restaurants/{id}`
- `GET /api/products`, `GET /api/products/{id}`
- `GET/POST /api/cart` and `/api/cart/items`
- `GET/POST /api/orders` and customer order actions
- `/api/vendor/*` for vendor catalog and order actions
- `/api/driver/*` for delivery actions
- `/api/payments/*`, `/api/reviews/*`, and `/api/notifications/*`

The primary database entities are `Restaurant`, `FoodItem`, `Vendor`, `Product`, `Cart`, `CartItem`, `Order`, `OrderItem`, `Delivery`, `Coupon`, `PaymentTransaction`, `Review`, and `Notification`.

## Testing

The full backend suite currently passes 44 tests. Commerce coverage includes cart ownership/isolation, one-source cart enforcement, backend totals, order privacy, cancellation rules, stale inactive-store rejection, and product stock decrement. The frontend production build passes.

## Known limitations

The current schema does not provide a separate category table, product options/add-ons, reserved inventory quantities, distance-based delivery pricing, or a general idempotency-key table. Food items do not have stock fields. These features should be added with migrations and backend contracts before exposing corresponding controls; frontend-only placeholders or fake marketplace data are not acceptable.
