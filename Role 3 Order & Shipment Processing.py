from datetime import datetime
import random
import string

class TransactionLogger:
    """
    Centralized logger for tracking order and shipment activities.
    
    Attributes:
        _records (list): Protected list of event dictionaries.
    """

    def __init__(self):
        """Initializes a hidden record list to protect log integrity."""
        self._records = []

    def _add(self, record_type, message):
        """Internal helper to append a timestamped log entry."""
        self._records.append({
            "type": record_type,
            "message": message,
            "time": datetime.now()
        })

    def log_order_status(self, order_id, status):
        """Records a status change for a specific order."""
        self._add("ORDER_STATUS", f"Order {order_id} changed status to {status}")

    def log_shipment_event(self, shipment_id, event):
        """Records a logistics event for a shipment."""
        self._add("SHIPMENT_EVENT", f"Shipment {shipment_id}: {event}")

    def log_warning(self, message):
        """Records a warning or error message in the logs."""
        self._add("WARNING", message)

    def get_logs(self):
        """Exposes logs as a read-only tuple to prevent external modification."""
        return tuple(self._records)

    def export_as_text(self):
        """
        Returns all logs as a formatted multi-line string.
        
        Returns:
            str: Newline-separated log entries.
        """
        lines = [f"[{r['time']}] ({r['type']}) -> {r['message']}" for r in self._records]
        return "\n".join(lines)


class CustomerOrder:
    """
    Represents a customer's purchase request and its lifecycle.
    
    VALID_STATUSES: Pending, Picked, Shipped, Delivered, Cancelled.
    
    >>> logger = TransactionLogger()
    >>> order = CustomerOrder("ORD-001", "Alice", [], logger)
    >>> order.status
    'Pending'
    """
    VALID_STATUSES = ["Pending", "Picked", "Shipped", "Delivered", "Cancelled"]

    def __init__(self, order_id, customer_name, items, logger):
        """Initializes order with items and logs the initial status."""
        self._order_id = order_id
        self._customer_name = customer_name
        self._items = items or []
        self._status = "Pending"
        self._created_at = datetime.now()
        self._logger = logger
        self._logger.log_order_status(order_id, self._status)

    @property
    def order_id(self):
        """Returns the unique order identifier."""
        return self._order_id

    @property
    def status(self):
        """Returns the current progress status of the order."""
        return self._status

    @property
    def items(self):
        """Returns a copy of the item list."""
        return list(self._items)

    def _set_status(self, new_status):
        """Internal method to update status with validation and logging."""
        if new_status not in self.VALID_STATUSES:
            raise ValueError("Invalid status update.")
        self._status = new_status
        self._logger.log_order_status(self._order_id, new_status)

    def check_availability(self, inventory):
        """Verifies all ordered items exist in the inventory manager."""
        for p in self._items:
            if inventory.get_product(p.product_id) is None:
                return False
        return True

    def start_picking(self, inventory):
        """Transitions order from Pending to Picked if items are available."""
        if self._status != "Pending":
            raise ValueError("Order can only be picked from Pending state.")
        if not self.check_availability(inventory):
            raise ValueError("One or more products are missing from inventory.")
        self._set_status("Picked")
        return True

    def mark_shipped(self):
        """Transitions order from Picked to Shipped."""
        if self._status != "Picked":
            raise ValueError("Order must be picked before shipping.")
        self._set_status("Shipped")

    def mark_delivered(self):
        """Transitions order from Shipped to Delivered."""
        if self._status != "Shipped":
            raise ValueError("Order must be shipped before delivery.")
        self._set_status("Delivered")

    def cancel(self, reason="User requested"):
        """Cancels order if it has not yet been shipped."""
        if self._status in ("Shipped", "Delivered"):
            raise ValueError("Cannot cancel after shipping.")
        self._set_status("Cancelled")
        self._logger.log_warning(f"Order {self._order_id} cancelled: {reason}")

    def get_summary(self):
        """Returns a dictionary summary of order details."""
        return {
            "order_id": self._order_id,
            "customer": self._customer_name,
            "status": self._status,
            "created": self._created_at,
            "items_count": len(self._items),
        }


class Shipment:
    """
    Manages the physical transit details for an order.
    
    >>> logger = TransactionLogger()
    >>> ship = Shipment("SHP-123", "ORD-001", "FedEx", logger)
    >>> tn = ship.generate_tracking()
    >>> len(tn) == 12  # 3 letters + 1 dash + 8 digits
    True
    """

    def __init__(self, shipment_id, order_ref, carrier, logger):
        """Initializes shipment and logs the creation event."""
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
        """Internal helper to track shipment history and log externally."""
        self._events.append((datetime.now(), text))
        self._logger.log_shipment_event(self._shipment_id, text)

    def generate_tracking(self):
        """Generates a random tracking number in AAA-00000000 format."""
        letters = "".join(random.choices(string.ascii_uppercase, k=3))
        digits = "".join(random.choices(string.digits, k=8))
        self._tracking_number = f"{letters}-{digits}"
        self._add_event(f"Tracking generated: {self._tracking_number}")
        return self._tracking_number

    def mark_delivered(self):
        """Updates shipment status to delivered."""
        self._delivered = True
        self._add_event("Shipment delivered")

    def is_delivered(self):
        """Returns True if the shipment has reached its destination."""
        return self._delivered

    def history(self):
        """Returns a list of all shipment events with timestamps."""
        return list(self._events)