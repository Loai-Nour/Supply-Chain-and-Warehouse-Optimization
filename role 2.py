from abc import ABC, abstractmethod
from datetime import datetime


# ============================================================
# ROLE 2: WAREHOUSE & STORAGE MANAGEMENT
# Handles:
# - Physical storage locations (Shelf, RefrigeratedUnit)
# - Warehouse structure and location management
# - Product placement and suitability checks
# - Storage optimization via OptimizationEngine
# - Capacity monitoring and free space calculations
# - Collaboration with InventoryManager to find best locations
# ============================================================

# ------------------------------------------------------------
# StorageLocation (ABC)
# Abstract class for all storage units
# ------------------------------------------------------------
class StorageLocation(ABC):

    def __init__(self, location_id, capacity, current_load):
        self.location_id = location_id
        self.capacity = capacity
        self.current_load = current_load
        self.items_count = 0
        self.last_updated = None


    @abstractmethod
    def is_suitable(self, product):
        pass


    def add_item(self, product):
        suitable = self.is_suitable(product)
        if suitable:
            product_weight = product.weight
            current_load = self.current_load
            new_load = current_load + product_weight
            self.current_load = new_load
            self.items_count += 1
            self.last_updated = datetime.now()
            return True
        else:
            return False


    def remove_item(self, product):
        product_weight = product.weight
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
        remaining = self.capacity - self.current_load
        if remaining < 0:
            remaining = 0
        return remaining


# ------------------------------------------------------------
# Shelf
# ------------------------------------------------------------
class Shelf(StorageLocation):

    def __init__(self, location_id, capacity, current_load, max_height):
        super().__init__(location_id, capacity, current_load)
        self.max_height = max_height


    def is_suitable(self, product):
        # Check type
        if not isinstance(product, DurableProduct):
            return False

        # Check height
        if product.height > self.max_height:
            return False

        # Check weight
        total_weight = self.current_load + product.weight
        if total_weight > self.capacity:
            return False

        return True


# ------------------------------------------------------------
# RefrigeratedUnit
# ------------------------------------------------------------
class RefrigeratedUnit(StorageLocation):


    def __init__(self, location_id, capacity, min_temp, max_temp):
        super().__init__(location_id, capacity, current_load=0)
        self.min_temp = min_temp
        self.max_temp = max_temp


    def is_suitable(self, product):
        # Check type
        if not isinstance(product, PerishableProduct):
            return False

        # Check temperature directly
        if product.temperature_required < self.min_temp:
            return False
        if product.temperature_required > self.max_temp:
            return False

        # Check weight
        total_weight = self.current_load + product.weight
        if total_weight > self.capacity:
            return False

        return True



# ------------------------------------------------------------
# Warehouse
# ------------------------------------------------------------
class Warehouse:
    def __init__(self, name):
        self.name = name
        self.locations = []


    def add_location(self, location):
        self.locations.append(location)


    def get_free_capacity(self):
        total_free = 0
        for loc in self.locations:
            loc_capacity = loc.capacity
            loc_load = loc.current_load
            loc_free = loc_capacity - loc_load
            if loc_free < 0:
                loc_free = 0
            total_free = total_free + loc_free
        return total_free


    def list_locations(self):
        loc_list = []
        for loc in self.locations:
            loc_list.append(loc.location_id)
        return loc_list


    def find_location_by_id(self, location_id):
        found = None
        for loc in self.locations:
            if loc.location_id == location_id:
                found = loc
        return found


# ------------------------------------------------------------
# OptimizationEngine
# ------------------------------------------------------------
class OptimizationEngine:
    def __init__(self, inventory_manager, warehouse):
        self.inventory_manager = inventory_manager
        self.warehouse = warehouse


    def find_best_location(self, product):
        checked_locations = []
        selected_location = None


        for loc in self.warehouse.locations:
            checked_locations.append(loc.location_id)
            suitable = loc.is_suitable(product)
            if suitable is True:
                selected_location = loc
                break

        return selected_location


# ============================================================
# End of Role 2: Warehouse & Storage Management
# ============================================================
