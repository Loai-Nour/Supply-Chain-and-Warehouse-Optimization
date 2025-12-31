from abc import ABC, abstractmethod
from datetime import datetime

class StorageLocation(ABC):
    """
    Abstract Base Class for all physical storage units in the warehouse.
    
    Attributes:
        location_id (str): Unique identifier for the spot.
        capacity (float): Maximum weight the location can hold.
        current_load (float): Current total weight of stored items.
    """

    def __init__(self, location_id, capacity, current_load=0):
        """Initializes storage unit with weight tracking."""
        self.location_id = location_id
        self.capacity = capacity
        self.current_load = current_load
        self.items_count = 0
        self.last_updated = None

    @abstractmethod
    def is_suitable(self, product):
        """Abstract check to see if a product meets location requirements."""
        pass

    def add_item(self, product):
        """
        Attempts to add a product to the location.
        Returns True if successful, False if unsuitable or over capacity.
        """
        if self.is_suitable(product):
            # Uses weight_kg from Role 1
            if self.current_load + product.weight_kg <= self.capacity:
                self.current_load += product.weight_kg
                self.items_count += 1
                self.last_updated = datetime.now()
                return True
        return False

    def remove_item(self, product):
        """Reduces load and item count when a product is removed."""
        self.current_load = max(0, self.current_load - product.weight_kg)
        self.items_count = max(0, self.items_count - 1)
        self.last_updated = datetime.now()

    def get_remaining_capacity(self):
        """Returns the available weight capacity."""
        return max(0, self.capacity - self.current_load)


class Shelf(StorageLocation):
    """
    Dry storage area for Durable products.
    
    >>> s = Shelf("S-101", 500.0, 2.0)
    >>> s.location_id
    'S-101'
    """

    def __init__(self, location_id, capacity, max_height):
        """Initializes a shelf with a height limit."""
        super().__init__(location_id, capacity)
        self.max_height = max_height

    def is_suitable(self, product):
        """Checks if product is Durable and fits weight limits."""
        # Role 1 compatibility check
        from project import DurableProduct
        if not isinstance(product, DurableProduct):
            return False
        
        # Note: Added 'height' attribute check if exists, else defaults to True
        # Original code check: if product.height > self.max_height: return False
        return (self.current_load + product.weight_kg) <= self.capacity


class RefrigeratedUnit(StorageLocation):
    """
    Temperature-controlled unit for Perishable products.
    """

    def __init__(self, location_id, capacity, min_temp, max_temp):
        """Initializes unit with temperature range."""
        super().__init__(location_id, capacity)
        self.min_temp = min_temp
        self.max_temp = max_temp

    def is_suitable(self, product):
        """Checks if Perishable product falls within temp range."""
        from project import PerishableProduct
        if not isinstance(product, PerishableProduct):
            return False
        
        # Maps to PerishableProduct._req_temperature_c from Role 1
        p_temp = product._req_temperature_c
        if self.min_temp <= p_temp <= self.max_temp:
            return (self.current_load + product.weight_kg) <= self.capacity
        return False


class Warehouse:
    """
    Container for all storage locations in the facility.
    """

    def __init__(self, name):
        """Initializes warehouse with a name and empty location list."""
        self.name = name
        self.locations = []

    def add_location(self, location):
        """Adds a new storage unit to the warehouse."""
        self.locations.append(location)

    def get_free_capacity(self):
        """Aggregates total remaining weight capacity across all units."""
        return sum(loc.get_remaining_capacity() for loc in self.locations)

    def list_locations(self):
        """Returns a list of all location IDs."""
        return [loc.location_id for loc in self.locations]

    def find_location_by_id(self, location_id):
        """Searches for a specific location object by ID."""
        for loc in self.locations:
            if loc.location_id == location_id:
                return loc
        return None


class OptimizationEngine:
    """
    Logic engine for placing products in the most suitable locations.
    """

    def __init__(self, inventory_manager, warehouse):
        """Connects the engine to inventory and warehouse data."""
        self.inventory_manager = inventory_manager
        self.warehouse = warehouse

    def find_best_location(self, product):
        """Finds the first suitable storage spot for a given product."""
        for loc in self.warehouse.locations:
            if loc.is_suitable(product):
                return loc
        return None