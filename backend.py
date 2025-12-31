from abc import ABC, abstractmethod
from datetime import datetime
import random
import string

# ==============================================================================
#                                  SYSTEM OVERVIEW
# ==============================================================================
# This unified system integrates three distinct roles:
# 1. Product & Inventory Management (Defining items and tracking stock)
# 2. Warehouse & Storage Management (Physical slotting and capacity planning)
# 3. Order & Shipment Processing (Customer lifecycle and logistics)
# ==============================================================================


# ==============================================================================
# ROLE 1: PRODUCT & INVENTORY MANAGEMENT
# ==============================================================================
# Responsibilities:
# - Define abstract product structures
# - Implement concrete product types (Perishable, Durable)
# - Manage the central inventory registry
# - Calculate financial values and storage costs
# ==============================================================================

class Product(ABC):
    """
    Abstract Base Class for all products in the warehouse system.
    
    This class enforces the contract that all specific product types must follow,
    ensuring they have ID, name, price, and physical dimensions.
    
    Attributes:
        product_id (str): Unique identifier for the item.
        name (str): Human-readable name of the product.
        base_price (float): Cost of the item before fees.
        volume_m3 (float): Volume occupied in cubic meters.
        weight_kg (float): Weight in kilograms.
    """

    def __init__(self, product_id, name, base_price, volume_m3, weight_kg):
        """
        Initializes the product with validation logic to prevent invalid data.
        
        Args:
            product_id (str): The unique ID.
            name (str): The product name.
            base_price (float): Price (must be >= 0).
            volume_m3 (float): Volume (must be > 0).
            weight_kg (float): Weight (must be > 0).
            
        Raises:
            ValueError: If numeric constraints are violated.
        """
        # Core identifying and physical attributes
        self._product_id = product_id
        self._name = name
        self._base_price = base_price
        self._volume_m3 = volume_m3
        self._weight_kg = weight_kg

        # Basic validation to prevent invalid products
        if self._base_price < 0:
            raise ValueError("Product price cannot be negative.")
        
        if self._volume_m3 <= 0:
            raise ValueError("Volume must be a positive value.")
            
        if self._weight_kg <= 0:
            raise ValueError("Weight must be a positive value.")

    # getters
    @property
    def product_id(self):
        """Returns the unique product identifier."""
        return self._product_id

    # Product name with validation on update
    @property
    def name(self):
        """Returns the product name."""
        return self._name

    @name.setter
    def name(self, new_name):
        """Sets the product name, ensuring it is not empty."""
        if not new_name:
            raise ValueError("Product name cannot be empty.")
        self._name = new_name

    # Base price with protection against invalid values
    @property
    def base_price(self):
        """Returns the base price of the product."""
        return self._base_price

    @base_price.setter
    def base_price(self, new_price):
        """
        Updates the base price.
        
        Raises:
            ValueError: If the new price is negative.
        """
        if new_price < 0:
            print(f"[ERROR]: Attempted to set negative price for {self._product_id}")
            raise ValueError("Price cannot be negative.")
        self._base_price = new_price

    # Physical properties are exposed as read-only
    @property
    def volume_m3(self):
        """Returns volume in cubic meters."""
        return self._volume_m3

    @property
    def weight_kg(self):
        """Returns weight in kilograms."""
        return self._weight_kg

    # Each product must declare its category/type
    @property
    @abstractmethod
    def product_type(self):
        """Abstract property: Returns the string category of the product."""
        pass

    # Polymorphic method: storage cost depends on product type
    @abstractmethod
    def calculate_storage_cost(self, days):
        """Abstract method: Calculates storage cost for a given number of days."""
        pass

    # Returns a formatted string describing the product
    @abstractmethod
    def get_product_info(self):
        """Abstract method: Returns a detailed string summary of the product."""
        pass


class PerishableProduct(Product):
    """
    Represents items with expiration dates and specific temperature requirements.
    
    >>> p = PerishableProduct("P1", "Milk", 2.0, 0.01, 1.0, "2025-12-31", 4)
    >>> p.check_status() # Depends on current date
    'FRESH'
    """

    def __init__(self, product_id, name, base_price, volume_m3, weight_kg, expiry_date, req_temperature_c):
        """
        Initializes a perishable product and parses the expiration date.
        
        Args:
            expiry_date (str): Date in 'YYYY-MM-DD' format.
            req_temperature_c (int): Required storage temperature in Celsius.
        """
        super().__init__(product_id, name, base_price, volume_m3, weight_kg)
        
        try:
            self._expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d") # Use %Y %m %d standard
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format.")

        self._req_temperature_c = req_temperature_c
        self._is_spoiled = False

    @property
    def product_type(self):
        return "Perishable"

    @property
    def expiry_date(self):
        """Returns the expiration datetime object."""
        return self._expiry_date

    # Checks freshness based on current time
    def check_status(self):
        """
        Determines if product is FRESH, CRITICAL (expiring soon), or EXPIRED.
        
        Returns:
            str: Status string.
        """
        current_time = datetime.now()
        if current_time > self._expiry_date:
            self._is_spoiled = True
            return "EXPIRED"
        
        days_left = (self._expiry_date - current_time).days
        if days_left < 3:
            return "CRITICAL"
        return "FRESH"

    def calculate_storage_cost(self, days):
        """
        Calculates cost based on volume and energy usage for cooling.
        Deep freeze items (temp <= 0) cost more.
        """
        base_rate = 5.0
        if self._req_temperature_c > 0:
            energy_factor = 1.5 # Standard Cooling
        else:
            energy_factor = 3.0 # Deep Freeze
        
        volume_cost = self.volume_m3 * base_rate 
        energy_cost = self.weight_kg * 0.1 * energy_factor
        
        return round((volume_cost + energy_cost) * days, 2) # Round to 2 decimals

    def get_product_info(self):
        """Returns detailed info including expiry and temp."""
        status = self.check_status()
        return (
            f"[Perishable] ID: {self.product_id} | Name: {self.name} | "
            f"Expiry: {self._expiry_date.date()} | Temp: {self._req_temperature_c}C | "
            f"Status: {status}"
        )


class DurableProduct(Product):
    """
    Represents long-life items that do not expire but may be fragile.
    
    >>> d = DurableProduct("D1", "Hammer", 15.0, 0.05, 2.0, "Steel", False)
    >>> d.product_type
    'Durable'
    """

    def __init__(self, product_id, name, base_price, volume_m3, weight_kg, material_type, is_fragile):
        """
        Initializes a durable product.
        
        Args:
            material_type (str): Primary material (e.g., 'Wood', 'Steel').
            is_fragile (bool): True if the item requires careful handling.
        """
        super().__init__(product_id, name, base_price, volume_m3, weight_kg)
        self._material_type = material_type
        self._is_fragile = is_fragile

    @property
    def product_type(self):
        return "Durable"

    def calculate_storage_cost(self, days):
        """
        Calculates cost based on volume. Fragile items incur a 20% surcharge.
        """
        base_rate = 2.0
        daily_cost = self.volume_m3 * base_rate
        
        if self._is_fragile: # Fragile product needs a safer environment
            daily_cost *= 1.20 

        return round(daily_cost * days, 2)

    def get_product_info(self):
        """Returns detailed info including material and fragility."""
        fragility = "Fragile" if self._is_fragile else "Robust"
        return (f"[Durable] ID: {self.product_id} | Name: {self.name} | "
            f"Material: {self._material_type} | Type: {fragility}")


class InventoryManager:
    """
    Manages the collection of products without knowing their specific implementations.
    Acts as the central database for the system.
    """

    def __init__(self):
        self._inventory = {} # Dictionary linking ID to product
        self._category_count = {"Perishable": 0, "Durable": 0}

    # Adds a product if the ID is unique
    def add_product(self, product):
        """
        Registers a product in the system.
        
        Returns:
            bool: True if added successfully, False if ID exists.
        """
        if product.product_id in self._inventory: # Prevent duplicating products
            print(f"[WARNING]: Add Failed: Product ID {product.product_id} already exists.")
            return False
        self._inventory[product.product_id] = product
        self._category_count[product.product_type] += 1 # Increment count
        
        print(f"[INFO]: Product Added: {product.name} (ID: {product.product_id})")
        return True

    # Removes a product safely by ID
    def remove_product(self, product_id):
        """
        Removes a product from the system.
        
        Returns:
            bool: True if removed, False if not found.
        """
        if product_id not in self._inventory:
            print(f"[ERROR]: Remove Failed: Product ID {product_id} not found.")
            return False
        product = self._inventory.pop(product_id) 
        self._category_count[product.product_type] -= 1 # Decrement count
        
        print(f"[INFO]: Product Removed: {product.name} (ID: {product_id})")
        return True

    # Retrieves a product if missing
    def get_product(self, product_id):
        """
        Safe getter for products. Returns None if not found.
        """
        return self._inventory.get(product_id) 

    # Updates price while respecting product validation
    def update_product_price(self, product_id, new_price):
        """
        Updates the price of a specific product via its ID.
        """
        product = self.get_product(product_id)
        if not product:
            print(f"[ERROR]: Product {product_id} not found for price update.")
            return False

        try:
            old_price = product.base_price # Save old price
            product.base_price = new_price # Plug in new price
            print(f"[INFO]: Price updated for {product_id}: {old_price} -> {new_price}")
            return True
        except ValueError as e:
            print(f"[ERROR]: Failed to update price: {e}")
            return False

    # Calculates total value of inventory (base prices)
    def get_total_inventory_value(self):
        """Sum of all base prices in inventory."""
        return round(sum(p.base_price for p in self._inventory.values()), 2)

    # Identifies perishable products close to expiration
    def check_expiring_products(self):
        """Returns a list of warning strings for expired/critical items."""
        warnings = []
        for p in self._inventory.values():
            if p.product_type == "Perishable":
                status = p.check_status()
                if status in {"EXPIRED", "CRITICAL"}:
                    warnings.append(f"WARNING: {p.name} is {status}")
        return warnings

    # Uses polymorphism to calculate storage costs
    def calculate_total_projected_storage_cost(self, days):
        """Calculates total expected cost for all items over X days."""
        total_cost = sum(p.calculate_storage_cost(days) for p in self._inventory.values())
        print(f"[INFO]: Projected storage cost for {days} days: ${total_cost}")
        return total_cost 

    # Generates an inventory summary
    def generate_report(self):
        """Returns a formatted report of all items and counts."""
        lines = []
        lines.append("\n" + "=" * 50)
        lines.append(f"SCWOS INVENTORY REPORT - {datetime.now().date()}")
        lines.append("=" * 50)
        lines.append(f"Total Items: {len(self._inventory)}")
        lines.append(f"Perishables: {self._category_count['Perishable']}")
        lines.append(f"Durables:    {self._category_count['Durable']}")
        lines.append("-" * 50)
        for p in self._inventory.values():
            lines.append(p.get_product_info())
        lines.append("=" * 50 + "\n")
        return "\n".join(lines)


# ==============================================================================
# ROLE 2: WAREHOUSE & STORAGE MANAGEMENT
# ==============================================================================
# Responsibilities:
# - Define physical storage types (Shelf, RefrigeratedUnit)
# - Manage warehouse capacity
# - Optimize product placement logic
# ==============================================================================

class StorageLocation(ABC):
    """
    Abstract Base Class for all storage units (locations) in the warehouse.
    
    Attributes:
        location_id (str): Unique location code.
        capacity (float): Max weight capacity.
        current_load (float): Current weight stored.
    """

    def __init__(self, location_id, capacity, current_load=0):
        self.location_id = location_id
        self.capacity = capacity
        self.current_load = current_load
        self.items_count = 0
        self.last_updated = None

    @abstractmethod
    def is_suitable(self, product):
        """Abstract method: checks if a product type fits this location."""
        pass

    def add_item(self, product):
        """
        Attempts to add an item. Checks suitability and weight capacity.
        """
        suitable = self.is_suitable(product)
        if suitable:
            # Note: Uses 'weight_kg' from Role 1 Product class
            product_weight = product.weight_kg 
            current_load = self.current_load
            new_load = current_load + product_weight
            
            if new_load <= self.capacity: # Capacity check
                self.current_load = new_load
                self.items_count += 1
                self.last_updated = datetime.now()
                return True
        return False

    def remove_item(self, product):
        """Removes an item and updates load calculations."""
        product_weight = product.weight_kg
        current_load = self.current_load
        new_load = current_load - product_weight
        
        if new_load < 0:
            self.current_load = 0
        else:
            self.current_load = new_load
            
        self.items_count -= 1
        if self.items_count < 0:
            self.items_count = 0
        self.last_updated = datetime.now()

    def get_remaining_capacity(self):
        """Returns the free weight capacity available."""
        remaining = self.capacity - self.current_load
        if remaining < 0:
            remaining = 0
        return remaining


class Shelf(StorageLocation):
    """
    Standard dry storage shelf for Durable products.
    """

    def __init__(self, location_id, capacity, current_load, max_height):
        super().__init__(location_id, capacity, current_load)
        self.max_height = max_height

    def is_suitable(self, product):
        """
        Checks if the product is Durable and fits physically.
        """
        # Check type (Role 1 Integration)
        if not isinstance(product, DurableProduct):
            return False

        # Note: Ideally checks height, but here checks weight as proxy in original logic
        total_weight = self.current_load + product.weight_kg
        if total_weight > self.capacity:
            return False

        return True


class RefrigeratedUnit(StorageLocation):
    """
    Temperature-controlled unit for Perishable products.
    """

    def __init__(self, location_id, capacity, min_temp, max_temp):
        super().__init__(location_id, capacity, current_load=0)
        self.min_temp = min_temp
        self.max_temp = max_temp

    def is_suitable(self, product):
        """
        Checks if the product is Perishable and requires this temp range.
        """
        # Check type (Role 1 Integration)
        if not isinstance(product, PerishableProduct):
            return False

        # Check temperature directly (Accessing Role 1 private attribute)
        if product._req_temperature_c < self.min_temp:
            return False
        if product._req_temperature_c > self.max_temp:
            return False

        # Check weight
        total_weight = self.current_load + product.weight_kg
        if total_weight > self.capacity:
            return False

        return True


class Warehouse:
    """
    Represents the entire facility containing multiple storage locations.
    """
    def __init__(self, name):
        self.name = name
        self.locations = [] # List of StorageLocation objects

    def add_location(self, location):
        """Registers a new storage location."""
        self.locations.append(location)

    def get_free_capacity(self):
        """Aggregates free capacity across all locations."""
        total_free = 0
        for loc in self.locations:
            total_free += loc.get_remaining_capacity()
        return total_free

    def list_locations(self):
        """Returns a list of all location IDs."""
        loc_list = []
        for loc in self.locations:
            loc_list.append(loc.location_id)
        return loc_list

    def find_location_by_id(self, location_id):
        """Finds a specific location object by its ID."""
        found = None
        for loc in self.locations:
            if loc.location_id == location_id:
                found = loc
        return found


class OptimizationEngine:
    """
    Logic engine that collaborates with Inventory and Warehouse to find
    the best spot for a product.
    """
    def __init__(self, inventory_manager, warehouse):
        self.inventory_manager = inventory_manager
        self.warehouse = warehouse

    def find_best_location(self, product):
        """
        Iterates through warehouse locations to find the first suitable one.
        Returns the StorageLocation object or None.
        """
        selected_location = None

        for loc in self.warehouse.locations:
            suitable = loc.is_suitable(product)
            if suitable is True:
                selected_location = loc
                break

        return selected_location


# ==============================================================================
# ROLE 3: ORDER & SHIPMENT PROCESSING
# ==============================================================================
# Responsibilities:
# - Handle customer orders (Pending -> Picked -> Shipped -> Delivered)
# - Log transactions
# - Manage shipments and tracking numbers
# ==============================================================================

class TransactionLogger:
    """
    Centralized logger used by orders and shipments.
    Keeps a protected list (_records) so logs cannot be modified outside this class.
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
        """Logs a change in order status."""
        self._add(
            "ORDER_STATUS",
            f"Order {order_id} changed status to {status}"
        )

    def log_shipment_event(self, shipment_id, event):
        """Logs an event related to a specific shipment."""
        self._add(
            "SHIPMENT_EVENT",
            f"Shipment {shipment_id}: {event}"
        )

    def log_warning(self, message):
        """Logs a generic warning."""
        self._add("WARNING", message)

    def log_info(self, message):
        """Logs a generic info message."""
        self._add("INFO", message)

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


class CustomerOrder:
    """
    Represents a single order from a customer and manages its lifecycle status.
    """

    VALID_STATUSES = [
        "Pending",
        "Picked",
        "Shipped",
        "Delivered",
        "Cancelled"
    ]

    def __init__(self, order_id, customer_name, items, logger):
        """
        items: list of Product objects (from Role 1)
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
            # Calls Role 1 InventoryManager
            stored = inventory.get_product(p.product_id)
            if stored is None:
                return False
        return True

    def start_picking(self, inventory):
        """Transitions order to Picked status if items are available."""
        if self._status != "Pending":
            raise ValueError("Order can only be picked from Pending state.")

        if not self.check_availability(inventory):
            raise ValueError(
                "One or more products are missing from inventory."
            )

        self._set_status("Picked")
        return True

    def mark_shipped(self):
        """Transitions order to Shipped status."""
        if self._status != "Picked":
            raise ValueError("Order must be picked before shipping.")
        self._set_status("Shipped")

    def mark_delivered(self):
        """Transitions order to Delivered status."""
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


class Shipment:
    """
    Connects an order to delivery logistics and generates tracking info.
    """

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
        """Generates a random tracking code like ABC-12345678."""
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


# ==============================================================================
# MAIN EXECUTION BLOCK (INTEGRATION TEST)
# ==============================================================================
if __name__ == "__main__":
    print("Initializing Unified Warehouse System...")
    
    # 1. Setup Infrastructure (Role 2)
    warehouse = Warehouse("Central Hub")
    shelf_1 = Shelf("Shelf-A", capacity=500, current_load=0, max_height=2.0)
    fridge_1 = RefrigeratedUnit("Fridge-B", capacity=200, min_temp=0, max_temp=5)
    
    warehouse.add_location(shelf_1)
    warehouse.add_location(fridge_1)
    
    # 2. Setup Inventory (Role 1)
    inv_mgr = InventoryManager()
    
    # Create products
    milk = PerishableProduct("P01", "Milk", 2.50, 0.005, 1.1, "2025-12-30", 4)
    table = DurableProduct("D01", "Oak Table", 150.00, 0.5, 20.0, "Wood", False)
    
    # Add to inventory
    inv_mgr.add_product(milk)
    inv_mgr.add_product(table)
    inv_mgr.generate_report()
    
    # 3. Optimize Storage (Role 2 Logic using Role 1 Data)
    engine = OptimizationEngine(inv_mgr, warehouse)
    
    # Place Milk
    loc_milk = engine.find_best_location(milk)
    if loc_milk:
        loc_milk.add_item(milk)
        print(f"Stored {milk.name} in {loc_milk.location_id}")
    else:
        print(f"Could not store {milk.name}")
        
    # Place Table
    loc_table = engine.find_best_location(table)
    if loc_table:
        loc_table.add_item(table)
        print(f"Stored {table.name} in {loc_table.location_id}")
        
    # 4. Process Order (Role 3)
    logger = TransactionLogger()
    order = CustomerOrder("ORD-100", "Alice Smith", [milk, table], logger)
    
    print(f"\nProcessing Order: {order}")
    try:
        # Check stock and pick
        order.start_picking(inv_mgr)
        print("Order Picked.")
        
        # Ship
        order.mark_shipped()
        shipment = Shipment("SHP-500", order.order_id, "FastTrack", logger)
        tracking = shipment.generate_tracking()
        print(f"Shipped with tracking: {tracking}")
        
        # Deliver
        shipment.mark_delivered()
        order.mark_delivered()
        print("Order Delivered.")
        
    except ValueError as e:
        print(f"Order Failed: {e}")

    # 5. Final Logs
    print("\n--- System Logs ---")
    print(logger.export_as_text())