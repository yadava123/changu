# ChanGu Realtime

## WebSocket

Connect to `/ws?token=<JWT>` after logging in. The backend validates the JWT and limits each user to three connections. Messages are JSON and contain no credentials or private secrets.

The database and REST APIs remain the source of truth. WebSocket delivery is an optimization for UI updates; failed connections do not block normal operations.

## Fallback

The notification bell polls `/api/notifications/unread-count` every 30 seconds. The notification page retrieves paginated notifications, so missed WebSocket events remain available.

## Client messages

The client may send `{ "type": "heartbeat" }`. Unsupported messages receive an error response.

## Security

Connections are user-specific. A token is required, invalid tokens are rejected, and notifications are always filtered by the authenticated user ID.

## Message format

Committed notification events are delivered as:

```json
{"type":"NOTIFICATION","entity_type":"ORDER","entity_id":123,"data":{"id":7,"notification_type":"ORDER_READY","title":"Order ready","message":"Your order is ready.","is_read":false},"timestamp":"2026-09-04T12:00:00+00:00"}
```

The server sends only the minimum notification metadata. It never sends passwords, tokens, payment secrets, or arbitrary URLs. REST actions remain the source of truth; a socket message never changes business state.

## Lifecycle events

Order creation, vendor acceptance/preparation/ready transitions, driver assignment/acceptance/out-for-delivery/delivery completion, order cancellation, payment status changes, and Siren request/provider transitions create database notifications through `NotificationService`. Event keys are scoped to the recipient and deduplicated.

## Fallback and availability

The frontend reconnects with delays of 1, 2, 5, 10, and 30 seconds, then continues retrying at 30 seconds. The bell polls unread count every 30 seconds. Drivers and providers expose `OFFLINE`, `ONLINE`, or `BUSY`; active work prevents accepting another task. GPS tracking is intentionally not implemented in this phase.
