from datetime import datetime
import random
import string

# ============================================================
# ROLE 3: ORDER & SHIPMENT PROCESSING
# This role handles:
# - Customer orders
# - Order lifecycle (Pending -> Picked -> Shipped -> Delivered)
# - Shipment creation / tracking
# - Logging important operations
# ============================================================


# ------------------------------------------------------------
# TransactionLogger
# Tracks order + shipment activity
# ------------------------------------------------------------
class TransactionLogger:

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

    def get_logs(self):
        # expose logs read-only
        return tuple(self._records)


# ------------------------------------------------------------
# CustomerOrder
# Represents a single order from a customer
# ------------------------------------------------------------
class CustomerOrder:

    VALID_STATUSES = ["Pending", "Picked", "Shipped", "Delivered", "Cancelled"]

    def __init__(self, order_id, customer_name, items, logger):
        """
        items: list of Product objects
        logger: TransactionLogger instance
        """
        self._order_id = order_id
        self._customer_name = customer_name
        self._items = items
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
        return self._items

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
        for p in self._items:
            stored = inventory.get_product(p.product_id)
            if stored is None:
                return False
        return True

    def start_picking(self, inventory):
        if self._status != "Pending":
            raise ValueError("Order can only be picked from Pending state.")

        if not self.check_availability(inventory):
            raise ValueError("One or more products are missing from inventory.")

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
        self._logger = logger

        self._logger.log_shipment_event(
            self._shipment_id,
            "Shipment created"
        )

    @property
    def tracking_number(self):
        return self._tracking_number

    def generate_tracking(self):
        letters = "".join(random.choices(string.ascii_uppercase, k=3))
        digits = "".join(random.choices(string.digits, k=8))
        self._tracking_number = f"{letters}-{digits}"

        self._logger.log_shipment_event(
            self._shipment_id,
            f"Tracking generated: {self._tracking_number}"
        )

        return self._tracking_number

    def get_eta(self):
        return "Estimated delivery: 3–5 business days"

    def mark_delivered(self):
        self._delivered = True
        self._logger.log_shipment_event(
            self._shipment_id,
            "Shipment delivered"
        )

    def is_delivered(self):
        return self._delivered




