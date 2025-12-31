# Supply-Chain-and-Warehouse-Optimization
SCWOS is an advanced OOP Python project for 3rd year CSE Advanced Programming course at E-JUST. It models a Supply Chain and Warehouse Optimization System, managing hierarchical products, intelligent storage, and logistics to simulate and optimize inventory and order fulfillment workflows.
#Role 1 :
Goal:
•	Manage products without depending on their concrete implementations
•	Apply OOP principles: abstraction, inheritance, polymorphism, and encapsulation
•	Safely calculate prices, storage costs, and expiration warnings
The system supports two product categories:
•	Perishable products (expire and require temperature control)
•	Durable products (long-life items, optionally fragile)
________________________________________
2. Core Classes:
2.1 Product (Abstract Base Class):
The Product class defines the common structure for all products. It cannot be instantiated directly.
Responsibilities:
•	Store shared attributes (ID, name, price, volume, weight)
•	Enforce validation rules
•	Define abstract methods that subclasses must implement
Attributes:
•	product_id: unique identifier
•	name: validated product name
•	base_price: validated price (must be ≥ 0)
•	volume_m3, weight_kg: (physical properties)
Abstract Members:
•	product_type
•	calculate_storage_cost (days)
•	get_product_info()
This ensures all product types behave consistently.

2.2 PerishableProduct:
Represents items that expire and require temperature-controlled storage.
Additional Attributes:
•	expiry_date (YYYY-MM-DD format)
•	req_temperature_c 
•	check_status() → Returns FRESH, CRITICAL, or EXPIRED
Methods:
•	calculate_storage_cost(days) → Includes cooling and energy factors
•	get_product_info() → Returns formatted perishable details
Cooling cost is higher for frozen products, and items near expiry are flagged.

2.3 DurableProduct:
Represents long-life products without expiration dates.
Additional Attributes:
•	material_type
•	is_fragile

3. Inventory Management:
3.1 InventoryManager:
The InventoryManager handles all inventory operations while remaining independent of product implementations.
Main Responsibilities:
•	Add and remove products safely
•	Prevent duplicate product IDs
•	Track category counts
Methods:
•	add_product(product)
•	remove_product(product_id)
•	get_product(product_id)
•	get_total_inventory_value()
•	check_expiring_products()
•	calculate_total_projected_storage_cost(days)
•	generate_report()
Polymorphism is used when calculating storage costs, allowing each product to apply its own logic.

4. OOP Concepts Applied
•	Abstraction: Product defines required behavior
•	Inheritance: PerishableProduct and DurableProduct extend Product
•	Polymorphism: Storage cost calculated dynamically per product type
•	Encapsulation: Controlled access using properties and validation
