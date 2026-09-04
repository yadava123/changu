def notification_template(name: str, **values) -> tuple[str, str]:
    order_number = values.get("order_number", "your order")
    templates = {
        "order_created": ("Order placed", f"Your order {order_number} has been placed."),
        "vendor_order": ("New order", f"New order {order_number} received."),
        "order_accepted": ("Order accepted", f"Your order {order_number} has been accepted."),
        "order_preparing": ("Order preparing", "Your order is being prepared."),
        "order_ready": ("Order ready", "Your order is ready."),
        "driver_assigned": ("Driver assigned", "A delivery driver has been assigned to your order."),
        "driver_task": ("New delivery", "A new delivery is ready for pickup."),
        "driver_accepted": ("Driver accepted", "Your driver has accepted the delivery."),
        "order_out_for_delivery": ("Out for delivery", "Your order is out for delivery."),
        "order_delivered": ("Order delivered", "Your order has been delivered. Enjoy your meal!"),
        "order_cancelled": ("Order cancelled", f"Your order {order_number} has been cancelled."),
        "vendor_order_cancelled": ("Order cancelled", f"Order {order_number} has been cancelled."),
        "payment_success": ("Payment successful", f"Payment successful for order {order_number}."),
        "payment_failed": ("Payment failed", "Payment failed. Please try again."),
        "refund_completed": ("Refund completed", f"Your refund of ₹{values.get('amount', '')} has been completed."),
        "siren_created": ("Siren request created", "Your Siren request has been created."),
        "siren_provider": ("New Siren request", "New emergency/service request available."),
        "siren_accepted": ("Provider assigned", "A provider has accepted your Siren request."),
        "siren_on_the_way": ("Provider on the way", "Your provider is on the way."),
        "siren_arrived": ("Provider arrived", "Your provider has arrived."),
        "siren_service_started": ("Service started", "Your provider has started the requested service."),
        "siren_resolved": ("Siren request resolved", "Your Siren request has been resolved."),
    }
    try:
        return templates[name]
    except KeyError:
        raise ValueError(f"Unknown notification template: {name}") from None