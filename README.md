# ChanGu

ChanGu is an AI-powered hyperlocal commerce and emergency assistance platform for India. This repository contains connected Food, Shop, Parcel, Ride, Siren, AI, personalization, vendor, driver, provider, and admin workflows.

## Technology Stack

- Frontend: React + Vite + Tailwind CSS + React Router + Axios
- Backend: FastAPI + Python + Uvicorn + Pydantic + SQLAlchemy
- Database: PostgreSQL-ready, with SQLite as the local fallback

## Project Structure

- `frontend/`: Vite React application, routes, UI, and API client
- `backend/`: FastAPI application, configuration, database foundation, and tests
- `docs/`: product and technical documentation space

## Installation

### Backend

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

After copying `backend/.env.example` to `backend/.env`, set a non-empty `SECRET_KEY`. Apply the database migration before the first auth request:

```powershell
alembic upgrade head
```

Backend runs at `http://localhost:8000`.

### Frontend

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`.

Copy `backend/.env.example` to `backend/.env` and `frontend/.env.example` to `frontend/.env` when you need local overrides. The backend defaults to SQLite if PostgreSQL is not configured. Never commit `.env` files or credentials.

## Testing

Backend tests:

```powershell
cd backend
python -m pytest -q
```

The suite covers validation, password hashing, duplicate registration, login, invalid and expired JWTs, inactive users, role denial, restaurants, food, products, filters, details, search, and empty results.

Backend checks:

- `GET http://localhost:8000/`
- `GET http://localhost:8000/api/health`
- `http://localhost:8000/docs`
- `http://localhost:8000/redoc`

Frontend routes:

- `/` redirects to `/home`; `/home` is protected and requires login
- `/login` and `/register` are public authentication pages
- `/food`, `/shop`, `/parcel`, `/rides`, `/siren`, and `/assistant` use connected backend workflows

The dashboard calls `/api/health` through Axios. Its status pill shows `Backend Status: Connected` only after a successful response, and `Backend Status: Offline` when the request fails.

## Authentication API

- `POST /api/auth/register`: creates a CUSTOMER account with a bcrypt password hash
- `POST /api/auth/login`: verifies credentials and returns a JWT bearer token
- `GET /api/auth/me`: returns the current user and requires `Authorization: Bearer <token>`

JWTs include `user_id`, `email`, `role`, and expiration. The frontend stores the token under `changu_access_token`, restores sessions through `/api/auth/me`, and attaches the token through the Axios interceptor.

## Customer Discovery API

- `GET /api/restaurants?city=Bengaluru&is_active=true`
- `GET /api/restaurants/{restaurant_id}`
- `GET /api/food?restaurant_id=1&category=Indian&search=biryani`
- `GET /api/food/{food_id}`
- `GET /api/products?category=Grocery&search=eggs&seller_id=1`
- `GET /api/products/{product_id}`
- `GET /api/search?q=biryani&type=food&city=Bengaluru`

Discovery data is loaded through Axios service modules, not hard-coded in React. Public catalog endpoints return only active restaurants, food, and products and do not expose private account data.

## Development Admin Seed

There is no public admin registration. For local initialization only, set `ADMIN_EMAIL` and `ADMIN_PASSWORD` in `backend/.env`, run the migration, then execute:

```powershell
python -m app.seed
```

The command is idempotent and creates an `ADMIN` account only when that email does not already exist. Use managed credentials and operational controls in production.

## Database Migrations

Alembic is configured in `backend/alembic.ini`:

```powershell
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

The first migration creates the `users` table and the second creates `restaurants`, `food_items`, and `products`. SQLite is used when `DATABASE_URL` is empty; set a PostgreSQL URL in `backend/.env` for a PostgreSQL deployment.

The migration chain adds the service, commerce, realtime, payment, AI, and personalization tables. The current migration head is `20260905_26`.

## Commerce API

- `GET /api/cart`
- `POST /api/cart/items`
- `PATCH /api/cart/items/{item_id}`
- `DELETE /api/cart/items/{item_id}`
- `DELETE /api/cart`
- `GET /api/addresses`
- `POST /api/addresses`
- `PATCH /api/addresses/{id}`
- `DELETE /api/addresses/{id}`
- `POST /api/orders`
- `GET /api/orders`
- `GET /api/orders/{id}`
- `POST /api/orders/{id}/cancel`

Cart and order endpoints require JWT authentication. The backend re-fetches item prices and calculates subtotal, delivery, tax, discount, and total. Payment status is controlled by backend payment endpoints; live provider settlement still requires production payment configuration.

## Development Catalog Seed

After applying migrations, run:

```powershell
cd backend
python -m app.seed
```

This creates clearly marked development data: three Bengaluru restaurants, five food items, and five local products. The seed is idempotent. It does not represent real vendors or enable checkout.

## Phase 3 Frontend Routes

- `/home`: protected customer dashboard with location, services, search, recommendations, and recent activity
- `/explore`: catalog-wide search
- `/food`: restaurant and food discovery
- `/food/{id}`: food details
- `/restaurants/{id}`: restaurant details and menu
- `/shop`: product discovery
- `/shop/{id}`: product details
- `/profile`: authenticated user details
- `/orders`: empty future orders state
- `/cart`: authenticated cart with quantity controls and authoritative totals
- `/checkout`: address selection, add-address form, COD selection, and place order
- `/orders/:id`: order snapshot, payment state, status timeline, and cancellable-order action
- `/parcel`, `/rides`, `/siren`, `/assistant`: protected service workflows

## Phase 2 Scope

Authentication, users, reusable role authorization, customer home, location selection, catalog discovery, search, detail views, profile, cart, checkout, Cash on Delivery orders, order snapshots, order status, and cancellation rules are implemented. Real payment gateways, delivery assignment, live tracking, parcel workflows, Siren emergency dispatch, AI features, notifications, and vendor/admin dashboards are intentionally not implemented yet.
