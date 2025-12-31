from abc import ABC, abstractmethod
from datetime import datetime

class Product(ABC):
    """
    Abstract Base Class for all products in the warehouse.
    
    Attributes:
        product_id (str): Unique identifier.
        name (str): Product description.
        base_price (float): Cost before storage fees.
        volume_m3 (float): Physical space occupied.
        weight_kg (float): Physical mass.
    """

    def __init__(self, product_id, name, base_price, volume_m3, weight_kg):
        """Initializes product with validation."""
        self._product_id = product_id
        self._name = name
        self._base_price = base_price
        self._volume_m3 = volume_m3
        self._weight_kg = weight_kg

        if self._base_price < 0:
            raise ValueError("Product price cannot be negative.")
        if self._volume_m3 <= 0 or self._weight_kg <= 0:
            raise ValueError("Volume and Weight must be positive values.")

    @property
    def product_id(self):
        """Returns the unique product ID."""
        return self._product_id

    @property
    def name(self):
        """Returns the product name."""
        return self._name

    @name.setter
    def name(self, new_name):
        """Sets a new name with validation."""
        if not new_name:
            raise ValueError("Product name cannot be empty.")
        self._name = new_name

    @property
    def base_price(self):
        """Returns the base price."""
        return self._base_price

    @base_price.setter
    def base_price(self, new_price):
        """Updates price with error logging for negatives."""
        if new_price < 0:
            print(f"[ERROR]: Attempted to set negative price for {self._product_id}")
            raise ValueError("Price cannot be negative.")
        self._base_price = new_price

    @property
    def volume_m3(self):
        """Returns volume in cubic meters."""
        return self._volume_m3

    @property
    def weight_kg(self):
        """Returns weight in kilograms."""
        return self._weight_kg

    @property
    @abstractmethod
    def product_type(self):
        """Abstract property for product category."""
        pass

    @abstractmethod
    def calculate_storage_cost(self, days):
        """Abstract method for polymorphic cost calculation."""
        pass

    @abstractmethod
    def get_product_info(self):
        """Abstract method for formatted product details."""
        pass


class PerishableProduct(Product):
    """
    Items with expiration dates requiring temperature control.
    
    >>> p = PerishableProduct("P01", "Milk", 2.0, 0.01, 1.0, "2025-12-31", 4)
    >>> p.product_type
    'Perishable'
    """

    def __init__(self, product_id, name, base_price, volume_m3, weight_kg, expiry_date, req_temperature_c):
        """Initializes perishable item and parses date."""
        super().__init__(product_id, name, base_price, volume_m3, weight_kg)
        try:
            self._expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format.")
        self._req_temperature_c = req_temperature_c
        self._is_spoiled = False

    @property
    def product_type(self):
        """Returns 'Perishable'."""
        return "Perishable"

    def check_status(self):
        """Determines if product is FRESH, CRITICAL, or EXPIRED."""
        current_time = datetime.now()
        if current_time > self._expiry_date:
            self._is_spoiled = True
            return "EXPIRED"
        days_left = (self._expiry_date - current_time).days
        return "CRITICAL" if days_left < 3 else "FRESH"

    def calculate_storage_cost(self, days):
        """Calculates cost based on volume and cooling factor."""
        energy_factor = 1.5 if self._req_temperature_c > 0 else 3.0
        volume_cost = self.volume_m3 * 5.0
        energy_cost = self.weight_kg * 0.1 * energy_factor
        return round((volume_cost + energy_cost) * days, 2)

    def get_product_info(self):
        """Returns detailed perishable info string."""
        return (f"[Perishable] ID: {self.product_id} | Name: {self.name} | "
                f"Expiry: {self._expiry_date.date()} | Temp: {self._req_temperature_c}C | "
                f"Status: {self.check_status()}")


class DurableProduct(Product):
    """
    Long-life items with material and fragility properties.
    
    >>> d = DurableProduct("D01", "Vase", 50.0, 0.05, 2.0, "Glass", True)
    >>> d.calculate_storage_cost(1)
    0.12
    """

    def __init__(self, product_id, name, base_price, volume_m3, weight_kg, material_type, is_fragile):
        """Initializes durable item."""
        super().__init__(product_id, name, base_price, volume_m3, weight_kg)
        self._material_type = material_type
        self._is_fragile = is_fragile

    @property
    def product_type(self):
        """Returns 'Durable'."""
        return "Durable"

    def calculate_storage_cost(self, days):
        """Calculates cost based on volume with a fragility surcharge."""
        daily_cost = self.volume_m3 * 2.0
        if self._is_fragile:
            daily_cost *= 1.20
        return round(daily_cost * days, 2)

    def get_product_info(self):
        """Returns detailed durable info string."""
        fragility = "Fragile" if self._is_fragile else "Robust"
        return (f"[Durable] ID: {self.product_id} | Name: {self.name} | "
                f"Material: {self._material_type} | Type: {fragility}")


class InventoryManager:
    """
    Handles the registry of products and financial summaries.
    
    >>> im = InventoryManager()
    >>> d = DurableProduct("D01", "Desk", 100.0, 0.5, 10.0, "Wood", False)
    >>> im.add_product(d)
    [INFO]: Product Added: Desk (ID: D01)
    True
    """

    def __init__(self):
        """Initializes empty inventory and category tracking."""
        self._inventory = {}
        self._category_count = {"Perishable": 0, "Durable": 0}

    def add_product(self, product):
        """Adds a product if ID is unique."""
        if product.product_id in self._inventory:
            print(f"[WARNING]: Add Failed: Product ID {product.product_id} already exists.")
            return False
        self._inventory[product.product_id] = product
        self._category_count[product.product_type] += 1
        print(f"[INFO]: Product Added: {product.name} (ID: {product.product_id})")
        return True

    def remove_product(self, product_id):
        """Removes a product by ID."""
        if product_id not in self._inventory:
            print(f"[ERROR]: Remove Failed: Product ID {product_id} not found.")
            return False
        product = self._inventory.pop(product_id)
        self._category_count[product.product_type] -= 1
        print(f"[INFO]: Product Removed: {product.name} (ID: {product_id})")
        return True

    def get_product(self, product_id):
        """Retrieves product by ID safely."""
        return self._inventory.get(product_id)

    def update_product_price(self, product_id, new_price):
        """Updates product price with validation."""
        product = self.get_product(product_id)
        if not product:
            print(f"[ERROR]: Product {product_id} not found for price update.")
            return False
        try:
            old_price = product.base_price
            product.base_price = new_price
            print(f"[INFO]: Price updated for {product_id}: {old_price} -> {new_price}")
            return True
        except ValueError as e:
            print(f"[ERROR]: Failed to update price: {e}")
            return False

    def get_total_inventory_value(self):
        """Calculates the sum of all base prices."""
        return round(sum(p.base_price for p in self._inventory.values()), 2)

    def check_expiring_products(self):
        """Lists perishable items near expiration."""
        warnings = []
        for p in self._inventory.values():
            if p.product_type == "Perishable":
                status = p.check_status()
                if status in {"EXPIRED", "CRITICAL"}:
                    warnings.append(f"WARNING: {p.name} is {status}")
        return warnings

    def calculate_total_projected_storage_cost(self, days):
        """Aggregates storage costs for all items."""
        total_cost = sum(p.calculate_storage_cost(days) for p in self._inventory.values())
        print(f"[INFO]: Projected storage cost for {days} days: ${total_cost}")
        return total_cost

    def generate_report(self):
        """Prints a comprehensive inventory status report."""
        print("\n" + "=" * 50)
        print(f"SCWOS INVENTORY REPORT - {datetime.now().date()}")
        print("=" * 50)
        print(f"Total Items: {len(self._inventory)}")
        print(f"Perishables: {self._category_count['Perishable']}")
        print(f"Durables:    {self._category_count['Durable']}")
        print("-" * 50)
        for p in self._inventory.values():
            print(p.get_product_info())
        print("=" * 50 + "\n")