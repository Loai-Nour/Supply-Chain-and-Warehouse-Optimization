from datetime import datetime
import random
import string

# ============================================================
# ROLE 3: ORDER & SHIPMENT PROCESSING
# Handles:
# - Customer orders
# - Order lifecycle (Pending -> Picked -> Shipped -> Delivered)
# - Shipment creation / tracking
# - Logging important operations
# - Extra helpers for debugging, summaries, and validation
# ============================================================


# ------------------------------------------------------------
# TransactionLogger
# Tracks order + shipment activity
# ------------------------------------------------------------
class TransactionLogger:
    """
    Centralized logger used by orders and shipments.
    Keeps a protected list (_records) so logs cannot
    be modified outside this class.
    """

    def __init__(self):
        self._records = []   # hidden list to protect log integrity

    # Internal helper to save logs
    def _add(self, record_type, message):
        self._records.append({
            "type": record_type,
            "message": message,
            "time": datetime.now()
        })

    def log_order_status(self, order_id, status):
        self._add(
            "ORDER_STATUS",
            f"Order {order_id} changed status to {status}"
        )

    def log_shipment_event(self, shipment_id, event):
        self._add(
            "SHIPMENT_EVENT",
            f"Shipment {shipment_id}: {event}"
        )

    def log_warning(self, message):
        self._add("WARNING", message)

    def get_logs(self):
        """Expose logs read-only as a tuple."""
        return tuple(self._records)

    def export_as_text(self):
        """Return formatted logs as multi-line text."""
        lines = []
        for r in self._records:
            lines.append(
                f"[{r['time']}] ({r['type']}) -> {r['message']}"
            )
        return "\n".join(lines)


# ------------------------------------------------------------
# CustomerOrder
# Represents a single order from a customer
# ------------------------------------------------------------
class CustomerOrder:

    VALID_STATUSES = [
        "Pending",
        "Picked",
        "Shipped",
        "Delivered",
        "Cancelled"
    ]

    def __init__(self, order_id, customer_name, items, logger):
        """
        items: list of Product objects (or mock objects)
        logger: TransactionLogger instance
        """
        self._order_id = order_id
        self._customer_name = customer_name
        self._items = items or []
        self._status = "Pending"
        self._created_at = datetime.now()
        self._logger = logger

        self._logger.log_order_status(order_id, self._status)

    @property
    def order_id(self):
        return self._order_id

    @property
    def status(self):
        return self._status

    @property
    def items(self):
        return list(self._items)

    def __repr__(self):
        return f"<Order #{self._order_id} status={self._status}>"

    # Private method to protect status changes
    def _set_status(self, new_status):
        if new_status not in self.VALID_STATUSES:
            raise ValueError("Invalid status update.")

        self._status = new_status
        self._logger.log_order_status(self._order_id, new_status)

    # --------------------------------------------------------
    # Uses InventoryManager from Role 1
    # --------------------------------------------------------
    def check_availability(self, inventory):
        """Ensure all products exist in inventory (ignores quantity)."""
        for p in self._items:
            stored = inventory.get_product(p.product_id)
            if stored is None:
                return False
        return True

    def start_picking(self, inventory):
        if self._status != "Pending":
            raise ValueError("Order can only be picked from Pending state.")

        if not self.check_availability(inventory):
            raise ValueError(
                "One or more products are missing from inventory."
            )

        self._set_status("Picked")
        return True

    def mark_shipped(self):
        if self._status != "Picked":
            raise ValueError("Order must be picked before shipping.")
        self._set_status("Shipped")

    def mark_delivered(self):
        if self._status != "Shipped":
            raise ValueError("Order must be shipped before delivery.")
        self._set_status("Delivered")

    def cancel(self, reason="User requested"):
        """Allows cancelling only when not shipped/delivered."""
        if self._status in ("Shipped", "Delivered"):
            raise ValueError("Cannot cancel after shipping.")

        self._set_status("Cancelled")
        self._logger.log_warning(
            f"Order {self._order_id} cancelled: {reason}"
        )

    def get_summary(self):
        """Return basic order summary as dictionary."""
        return {
            "order_id": self._order_id,
            "customer": self._customer_name,
            "status": self._status,
            "created": self._created_at,
            "items_count": len(self._items),
        }


# ------------------------------------------------------------
# Shipment
# Connects an order to delivery
# ------------------------------------------------------------
class Shipment:

    def __init__(self, shipment_id, order_ref, carrier, logger):
        self._shipment_id = shipment_id
        self._order_ref = order_ref
        self._carrier = carrier
        self._tracking_number = None
        self._created = datetime.now()
        self._delivered = False
        self._events = []
        self._logger = logger

        self._add_event("Shipment created")

    def _add_event(self, text):
        """Internal helper for shipment history."""
        self._events.append(
            (datetime.now(), text)
        )
        self._logger.log_shipment_event(self._shipment_id, text)

    @property
    def tracking_number(self):
        return self._tracking_number

    def generate_tracking(self):
        letters = "".join(random.choices(string.ascii_uppercase, k=3))
        digits = "".join(random.choices(string.digits, k=8))
        self._tracking_number = f"{letters}-{digits}"

        self._add_event(f"Tracking generated: {self._tracking_number}")
        return self._tracking_number

    def get_eta(self):
        return "Estimated delivery: 3–5 business days"

    def mark_delivered(self):
        self._delivered = True
        self._add_event("Shipment delivered")

    def is_delivered(self):
        """Return delivery status as boolean."""
        return self._delivered

    def history(self):
        """Return all shipment events."""
        return list(self._events)

    def __repr__(self):
        return (
            f"<Shipment {self._shipment_id} "
            f"delivered={self._delivered} "
            f"tracking={self._tracking_number}>"
        )
