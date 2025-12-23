from abc import ABC, abstractmethod
from datetime import datetime

# Abstract Class: Product
# This class defines the common structure and rules
# that all product types in the system must follow.
class Product(ABC):

    def __init__(self, product_id, name, base_price, volume_m3, weight_kg):
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
        return self._product_id

    # Product name with validation on update
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        if not new_name:
            raise ValueError("Product name cannot be empty.")
        self._name = new_name

    # Base price with protection against invalid values
    @property
    def base_price(self):
        return self._base_price

    @base_price.setter
    def base_price(self, new_price):
        if new_price < 0:
            print(f"[ERROR]: Attempted to set negative price for {self._product_id}")
            raise ValueError("Price cannot be negative.")
        self._base_price = new_price

    # Physical properties are exposed as read-only
    @property
    def volume_m3(self):
        return self._volume_m3

    @property
    def weight_kg(self):
        return self._weight_kg

    # Each product must declare its category/type
    @property
    @abstractmethod
    def product_type(self):
        pass

    # Polymorphic method: storage cost depends on product type
    @abstractmethod
    def calculate_storage_cost(self, days):
        pass

    # Returns a formatted string describing the product
    @abstractmethod
    def get_product_info(self):
        pass


# PerishableProduct Represents items with expiration dates
class PerishableProduct(Product):

    def __init__(self, product_id, name, base_price, volume_m3, weight_kg, expiry_date, req_temperature_c):
        super().__init__(product_id, name, base_price, volume_m3, weight_kg)
        
        try:
            self._expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d") #we have to use %Y %m %d and we cannot change the letters
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format.")

        self._req_temperature_c = req_temperature_c
        self._is_spoiled = False

    @property
    def product_type(self):
        return "Perishable"

    @property
    def expiry_date(self):
        return self._expiry_date

    # Checks freshness based on current time
    def check_status(self):
        current_time = datetime.now()
        if current_time > self._expiry_date:
            self._is_spoiled = True
            return "EXPIRED"
        
        days_left = (self._expiry_date - current_time).days
        if days_left < 3:
            return "CRITICAL"
        return "FRESH"

    def calculate_storage_cost(self, days):
        base_rate = 5.0
        if self._req_temperature_c > 0:
            energy_factor = 1.5 # Standard Cooling
        else:
            energy_factor = 3.0 # Deep Freeze
        
        volume_cost = self.volume_m3 * base_rate 
        energy_cost = self.weight_kg * 0.1 * energy_factor
        
        return round((volume_cost + energy_cost) * days, 2) #round the cost to 2 decimal places

    def get_product_info(self):
        status = self.check_status()
        return (
            f"[Perishable] ID: {self.product_id} | Name: {self.name} | "
            f"Expiry: {self._expiry_date.date()} | Temp: {self._req_temperature_c}C | "
            f"Status: {status}"
        )

#Represents long-life items
class DurableProduct(Product):

    def __init__(self, product_id, name, base_price, volume_m3, weight_kg, material_type, is_fragile):
        super().__init__(product_id, name, base_price, volume_m3, weight_kg)
        self._material_type = material_type
        self._is_fragile = is_fragile

    @property
    def product_type(self):
        return "Durable"

    def calculate_storage_cost(self, days):
        base_rate = 2.0
        daily_cost = self.volume_m3 * base_rate
        
        if self._is_fragile: #fragile product needs a more safe inviroment
            daily_cost *= 1.20 # daily_cost= daily_cost * 2

        return round(daily_cost * days, 2)

    def get_product_info(self):
        fragility = "Fragile" if self._is_fragile else "Robust"
        return (f"[Durable] ID: {self.product_id} | Name: {self.name} | "
            f"Material: {self._material_type} | Type: {fragility}")
# InventoryManager
# class responsible for managing products
# without knowing their implementations.
class InventoryManager:

    def __init__(self):
        self._inventory = {} #inventory made as a dictionary to link the ID to the product
        self._category_count = {"Perishable": 0, "Durable": 0}

    # Adds a product if the ID is unique
    def add_product(self, product):
        if product.product_id in self._inventory: #prevents duplicating products
            print(f"[WARNING]: Add Failed: Product ID {product.product_id} already exists.")
            return False
        self._inventory[product.product_id] = product
        self._category_count[product.product_type] += 1 #increament count
        
        print(f"[INFO]: Product Added: {product.name} (ID: {product.product_id})")
        return True

    # Removes a product safely by ID
    def remove_product(self, product_id):
        if product_id not in self._inventory:
            print(f"[ERROR]: Remove Failed: Product ID {product_id} not found.")
            return False
        product = self._inventory.pop(product_id) 
        self._category_count[product.product_type] -= 1 #decreament count
        
        print(f"[INFO]: Product Removed: {product.name} (ID: {product_id})")
        return True

    # Retrieves a product if missing
    def get_product(self, product_id):
        return self._inventory.get(product_id) #we use get to prevent crashing the program

    # Updates price while respecting product validation
    def update_product_price(self, product_id, new_price):
        product = self.get_product(product_id)
        if not product:
            print(f"[ERROR]: Product {product_id} not found for price update.")
            return False

        try:
            old_price = product.base_price #save the old price
            product.base_price = new_price #plug in the new price
            print(f"[INFO]: Price updated for {product_id}: {old_price} -> {new_price}")
            return True
        except ValueError as e:
            print(f"[ERROR]: Failed to update price: {e}")
            return False

    # Calculates total value of inventory (base prices)
    def get_total_inventory_value(self):
        return round(sum(p.base_price for p in self._inventory.values()), 2)

    # Identifies perishable products close to expiration
    def check_expiring_products(self):
        warnings = []
        for p in self._inventory.values():
            if p.product_type == "Perishable":
                status = p.check_status()
                if status in {"EXPIRED", "CRITICAL"}:
                    warnings.append(f"WARNING: {p.name} is {status}")
        return warnings
    # Uses polymorphism to calculate storage costs
    def calculate_total_projected_storage_cost(self, days):
        total_cost = sum(p.calculate_storage_cost(days) for p in self._inventory.values())
        print(f"[INFO]: Projected storage cost for {days} days: ${total_cost}")
        return total_cost 
    # Generates an inventory summary
    def generate_report(self):
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