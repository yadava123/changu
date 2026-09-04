# ChanGu Admin Control Center

## Verified routes

Admin pages are protected by the frontend `AdminRoute`, and every `/api/admin/*` endpoint requires an authenticated user with the `ADMIN` role.

- `/admin/dashboard`: database-backed user, service, order, delivery, ride, Siren, and AI counts.
- `/admin/users`: paginated user search and role filtering; password hashes are not returned.
- `/admin/approvals`: unified vendor, driver, and emergency-provider application decisions.
- `/admin/vendors`: paginated vendor listing and audited activation changes.
- `/admin/products`: paginated product listing and audited availability changes.
- `/admin/orders`: paginated order inspection and controlled administrative cancellation.
- `/admin/deliveries`: delivery inspection.
- `/admin/siren`: emergency request inspection.
- `/admin/providers`: provider listing and activation controls.
- `/admin/vendor-applications`, `/admin/driver-applications`, `/admin/provider-applications`: approval workflows.
- `/admin/financials`: successful, failed, refunded, commission, earnings, and transaction data.
- `/admin/settings`: persisted operational settings restricted to supported keys.
- `/admin/notifications`: controlled announcements by audience.
- `/admin/audit-logs`: recorded administrative actions.

## Permissions and security

Authorization is enforced in FastAPI with `require_role(UserRole.ADMIN)`. Frontend route protection is only a usability layer. Customer, vendor, driver, and provider requests to admin APIs receive `403` responses.

Administrative state changes use soft status fields where the model supports them. Product and vendor activation changes require browser confirmation and create audit records. Orders cannot be cancelled after delivery or after they have already been cancelled.

## Data and pagination

Dashboard values are calculated from the database. User, vendor, product, order, transaction, and audit-log collections expose bounded page sizes. Financial records are read-only through the current admin API; no historical payment mutation is exposed.

## Testing

The verified admin-related baseline includes role authorization, vendor and driver approvals, financial authorization, and frontend production compilation. Run:

```powershell
Push-Location backend
pytest -q tests/test_auth.py tests/test_driver.py tests/test_financial.py tests/test_vendor.py
Pop-Location
Push-Location frontend
npm run build
Pop-Location
```

The current baseline passes 18 tests. The frontend build passes with an existing Vite chunk-size warning.

## Known limitations

The repository does not yet expose dedicated admin APIs and screens for every requested Phase 6 category, including refunds, configurable commissions, date-range reports, detailed customer activity, ride/parcels management pages, review moderation, and service enablement controls. Those should be implemented only against real models and payment/provider capabilities; no fake dashboard values or no-op controls should be added.
