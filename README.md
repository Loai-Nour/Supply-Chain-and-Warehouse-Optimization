# Supply-Chain-and-Warehouse-Optimization

SCWOS is an advanced OOP Python project for 3rd year CSE Advanced Programming course at E-JUST. It models a Supply Chain and Warehouse Optimization System, managing hierarchical products, intelligent storage, and logistics to simulate and optimize inventory and order fulfillment workflows.

# 🏭 Supply Chain and Warehouse Optimization System (SCWOS)

**Course:** Advanced Programming (CSE 3rd Year)  
**Institution:** E-JUST  
**Team Size:** 4 Members  

---

## 📖 Project Overview
SCWOS is a comprehensive Python application designed to simulate and optimize modern warehouse logistics. It integrates **Inventory Management**, **Storage Optimization**, and **Order Processing** into a unified dashboard. 

The system leverages **Object-Oriented Programming (OOP)** principles—including Inheritance, Polymorphism, Abstraction, and Encapsulation—to handle complex business logic for perishable and durable goods.

## 🚀 Key Features
* **Role 1 (Inventory):** Tracks hierarchical products (Perishable vs. Durable) with expiration and fragility logic.
* **Role 2 (Optimization):** Algorithms to automatically assign the best storage location (Shelf vs. Fridge) based on product requirements.
* **Role 3 (Logistics):** Full order lifecycle management: *Pending → Picked → Shipped → Delivered*.
* **Role 4 (UI/Integration):** A professional Tkinter GUI that integrates all modules with real-time visual feedback and logging.

## 🛠️ System Architecture (OOP Roles)

| Module | Responsibility | Key Classes |
| :--- | :--- | :--- |
| **Backend Core** | Business Logic | `Product`, `Warehouse`, `Order` |
| **Inventory** | Data Management | `InventoryManager`, `PerishableProduct` |
| **Optimization** | Algorithms | `OptimizationEngine`, `StorageLocation` |
| **Frontend** | User Interface | `SCWOS_GUI`, `DashboardFrame` |

## 💻 How to Run

1.  **Prerequisites:** Python 3.x (No external libraries required).
2.  **File Structure:** Ensure `main.py` and `backend.py` are in the same folder.
3.  **Execute:**
    ```bash
    python main.py
    ```
4.  **Usage:** The system pre-loads demo data ("Milk", "Desk"). Use the Sidebar to navigate between Inventory, Warehouse, and Order screens.

## 📸 Interface
The application features a sidebar navigation layout with dynamic frames for:
* **Dashboard:** Real-time KPI cards.
* **Inventory:** Spreadsheet-style view of stock.
* **Warehouse:** Visual capacity bars for storage units.
* **Orders:** Workflow buttons for shipping/delivery.

## 🏗️ System Architecture (UML Diagram)
---
*Built with ❤️ by the SCWOS Team for E-JUST.*
---

## 📖 Roles Description:

### Role 1:

## Goal:
- Manage products without depending on their concrete implementations
- Apply OOP principles: abstraction, inheritance, polymorphism, and encapsulation
- Safely calculate prices, storage costs, and expiration warnings

The system supports two product categories:
- Perishable products (expire and require temperature control)
- Durable products (long-life items, optionally fragile)

---

### 2. Core Classes:

## 2.1 Product (Abstract Base Class):

The Product class defines the common structure for all products. It cannot be instantiated directly.

Responsibilities:
- Store shared attributes (ID, name, price, volume, weight)
- Enforce validation rules
- Define abstract methods that subclasses must implement

Attributes:
- product_id: unique identifier
- name: validated product name
- base_price: validated price (must be ≥ 0)
- volume_m3, weight_kg: (physical properties)

Abstract Members:
- product_type
- calculate_storage_cost (days)
- get_product_info()

This ensures all product types behave consistently.

---

## 2.2 PerishableProduct:

Represents items that expire and require temperature-controlled storage.

Additional Attributes:
- expiry_date (YYYY-MM-DD format)
- req_temperature_c
- check_status() → Returns FRESH, CRITICAL, or EXPIRED

Methods:
- calculate_storage_cost(days) → Includes cooling and energy factors
- get_product_info() → Returns formatted perishable details

Cooling cost is higher for frozen products, and items near expiry are flagged.

---

## 2.3 DurableProduct:

Represents long-life products without expiration dates.

Additional Attributes:
- material_type
- is_fragile

---

## 3. Inventory Management:

### 3.1 InventoryManager:

The InventoryManager handles all inventory operations while remaining independent of product implementations.

Main Responsibilities:
- Add and remove products safely
- Prevent duplicate product IDs
- Track category counts

Methods:
- add_product(product)
- remove_product(product_id)
- get_product(product_id)
- get_total_inventory_value()
- check_expiring_products()
- calculate_total_projected_storage_cost(days)
- generate_report()

Polymorphism is used when calculating storage costs, allowing each product to apply its own logic.

---

## 4. OOP Concepts Applied

- Abstraction: Product defines required behavior
- Inheritance: PerishableProduct and DurableProduct extend Product
- Polymorphism: Storage cost calculated dynamically per product type
- Encapsulation: Controlled access using properties and validation






## Role 2: Warehouse & Storage Management

This role manages the physical structure of the warehouse and implements the logic for optimal storage placement.

---

### Responsibilities
- Represent different types of storage locations
- Enforce storage rules such as weight limits and temperature constraints
- Track current load and available capacity
- Organize multiple storage locations inside a warehouse
- Decide the best storage location for a product

---

## Core Classes

### StorageLocation (Abstract Base Class)

`StorageLocation` is an abstract class that represents any type of storage unit.  
It cannot be instantiated directly and serves as a base for all storage types.

#### Responsibilities
- Store common attributes for all storage locations
- Manage capacity and current load
- Define a required method to check if a product can be stored

#### Attributes
- `location_id`: unique identifier for the storage unit
- `capacity`: maximum allowed weight
- `current_load`: current stored weight
- `items_count`: number of stored items
- `last_updated`: last time the storage was modified

#### Abstract Method
- `is_suitable(product)`: forces subclasses to define their own suitability rules

#### Other Methods
- `add_item(product)`: adds a product if it is suitable
- `remove_item(product)`: removes a product and updates load
- `get_remaining_capacity()`: returns remaining capacity

---

### Shelf

The `Shelf` class represents a normal storage shelf used for durable products.

#### Responsibilities
- Store durable (non-perishable) products
- Enforce height and weight constraints

#### Additional Attribute
- `max_height`: maximum allowed height for products

#### Logic
- Accepts only `DurableProduct` objects
- Checks that product height does not exceed the shelf limit
- Ensures total weight does not exceed capacity

#### OOP Concepts
- Inheritance (extends `StorageLocation`)
- Polymorphism (custom `is_suitable` implementation)

---

### RefrigeratedUnit

The `RefrigeratedUnit` class represents cold storage for perishable products.

#### Responsibilities
- Store temperature-sensitive products
- Enforce temperature range constraints
- Enforce capacity limits

#### Additional Attributes
- `min_temp`: minimum supported temperature
- `max_temp`: maximum supported temperature

#### Logic
- Accepts only `PerishableProduct` objects
- Checks that required temperature is within the allowed range
- Ensures weight does not exceed capacity

#### OOP Concepts
- Inheritance
- Polymorphism

---

## Warehouse Management

### Warehouse

The `Warehouse` class represents a warehouse that contains multiple storage locations.

#### Responsibilities
- Store and manage all storage locations
- Calculate total available capacity
- Allow searching for locations

#### Attributes
- `name`: warehouse name
- `locations`: list of `StorageLocation` objects

#### Methods
- `add_location(location)`
- `get_free_capacity()`
- `list_locations()`
- `find_location_by_id(location_id)`

---

## Optimization Engine

### OptimizationEngine

The `OptimizationEngine` is responsible for deciding where a product should be stored.

#### Responsibilities
- Work with the warehouse and inventory system
- Evaluate storage locations
- Select the first suitable location for a product

#### Attributes
- `inventory_manager`: reference to inventory data
- `warehouse`: reference to the warehouse

#### Method
- `find_best_location(product)`: loops through locations and returns the first suitable one, or `None` if no location is available

This uses polymorphism, since each storage location decides suitability differently.

---

## OOP Concepts Used
- Abstraction: `StorageLocation` defines required behavior
- Inheritance: `Shelf` and `RefrigeratedUnit` extend base storage
- Polymorphism: `is_suitable()` behaves differently per storage type










# 🖥️ SCWOS - Graphical User Interface (Role 4)

**Role:** System Integrator & UI Developer  
**Technology:** Python (Tkinter)  
**Project:** Supply Chain and Warehouse Optimization System (SCWOS)

---

## 📖 Component Overview
The **SCWOS GUI** serves as the central control hub for the Supply Chain Optimization System. It is responsible for bridging the backend logic (Inventory, Warehouse, Orders) with a user-friendly, interactive dashboard. This component implements the **View** and **Controller** layers of the application, ensuring seamless data flow and real-time visualization of warehouse operations.

## ✨ Key Features (My Contribution)

### 1. 📊 Interactive Dashboard
* **Real-Time KPIs:** Displays live metrics for Total Products, Inventory Value, and Active Orders.
* **Dynamic Updates:** Automatically refreshes data states whenever backend logic changes.

### 2. 📝 Dynamic Inventory Management
* **Polymorphic Forms:** The "Add Product" interface changes dynamically based on user selection:
    * *Perishable:* Shows Expiration Date & Temperature fields.
    * *Durable:* Shows Material Type & Fragility Checkbox.
* **Input Validation:** Robust error handling prevents invalid data types (e.g., negative prices) from crashing the system.

### 3. 🏭 Visual Warehouse Optimization
* **Capacity Visualization:** Uses progress bars to visually represent the load status of shelves and refrigerators.
* **Optimization Trigger:** Allows users to select a product and execute the Role 2 optimization algorithm with a single click.

### 4. 🚚 Order Workflow Manager
* **State Management:** Controls the lifecycle of an order through strict button logic:
    * *Pick* (Validates Stock) $\rightarrow$ *Ship* (Generates Tracking) $\rightarrow$ *Deliver* (Finalizes).
* **Error Prevention:** Prevents invalid state transitions (e.g., cannot ship an order before picking).

## 🛠️ OOP Implementation in GUI

This interface is not just a script; it is built using strict **Object-Oriented Programming** principles:

| OOP Concept | Application in GUI |
| :--- | :--- |
| **Inheritance** | All UI pages (`DashboardFrame`, `InventoryFrame`, etc.) inherit from the parent `tk.Frame` class to modularize the code. |
| **Composition** | The main `SCWOS_GUI` class is composed of instances of backend classes (`InventoryManager`, `Warehouse`, `TransactionLogger`), effectively binding the frontend to the backend. |
| **Encapsulation** | UI logic is encapsulated within specific frame classes. For example, `OrderFrame` handles all order logic internally, exposing only necessary methods to the main controller. |
| **Polymorphism** | The `show_frame()` method uses Duck Typing to call the `.on_show()` refresh method on any frame that supports it, regardless of the frame's specific type. |

## 🚀 Usage Guide

1.  **Launch:** Run `main.py` to start the application.
2.  **Navigation:** Use the sidebar menu to switch between modules.
3.  **Demo Data:** The system initializes with pre-loaded data (Milk, Desk, Laptop) to demonstrate functionality immediately.
<img width="1269" height="749" alt="{25A2FDD6-C52C-4E1D-8A02-3804F63FE55F}" src="https://github.com/user-attachments/assets/28a387d9-1043-4bbc-87be-fdf8ece836dd" />
<img width="1920" height="1080" alt="{248A1B24-6122-4032-91AA-7095759D9B27}" src="https://github.com/user-attachments/assets/949036f2-9249-4ba7-ab0f-fdf007165b2f" />


## 📸 Screen Descriptions

1.  **Dashboard:** High-level system statistics.
2.  **Inventory:** Tabular view of all products with detailed status columns.
3.  **Warehouse:** Visual bars showing utilized vs. free space.
4.  **Orders:** Workflow interface for processing customer orders.
5.  **Logs:** Read-only view of the system's transaction history.

---
*Developed by [Loai Nour] – Role 4 Integration Lead*
