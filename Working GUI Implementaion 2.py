import tkinter as tk
from tkinter import ttk, messagebox
import datetime

# ==============================================================================
# 🔗 BACKEND INTEGRATION (The Bridge)
# ==============================================================================
# We attempt to import the logic classes created by Role 1, 2, and 3.
# This demonstrates "Modular Programming".
try:
    from backend import (
        PerishableProduct, DurableProduct, InventoryManager, 
        Warehouse, Shelf, RefrigeratedUnit, OptimizationEngine,
        TransactionLogger, CustomerOrder, Shipment
    )
except ImportError:
    # Defensive Programming: Fails gracefully if the backend file is missing.
    print("CRITICAL ERROR: Could not import 'backend.py'. Make sure your logic file is named 'backend.py'")
    exit()

# ==============================================================================
# 🎮 MAIN CONTROLLER (Role 4 Responsibility)
# ==============================================================================
class SCWOS_GUI(tk.Tk):
    """
    The Main Application Controller.
    OOP Principle: INHERITANCE (Inherits from tk.Tk)
    Responsibility: 
      1. Initialize the Backend Logic (Model).
      2. Manage the UI Frames (View).
      3. Route user actions to backend methods (Control).
    """
    def __init__(self):
        super().__init__() # Call the constructor of the parent tk.Tk class
        self.title("SCWOS - E-JUST Advanced CSE Project")
        self.geometry("1280x720")
        self.configure(bg="#ecf0f1")

        # --- SYSTEM INITIALIZATION (The "Backend" Engine) ---
        # OOP Principle: COMPOSITION ( The GUI "has a" Logger, Manager, Warehouse )
        self.logger = TransactionLogger()
        self.inventory_mgr = InventoryManager()
        self.warehouse = Warehouse("Central Fulfillment Center")
        
        # Injecting dependencies into the optimizer
        self.optimizer = OptimizationEngine(self.inventory_mgr, self.warehouse)
        self.active_orders = [] # Local state list to track order objects
        
        # --- PRE-LOAD DATA ---
        # We load dummy data so the professor sees a populated system immediately.
        self._initialize_demo_data()

        # --- UI LAYOUT ---
        # Setup the permanent Sidebar
        self.setup_sidebar()
        
        # Setup the container that swaps pages (Frames)
        self.container = tk.Frame(self, bg="white")
        self.container.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        # --- FRAMES SETUP (View Management) ---
        # We create all pages at startup and stack them on top of each other.
        self.frames = {}
        for F in (DashboardFrame, InventoryFrame, WarehouseFrame, OrderFrame, LogsFrame):
            page_name = F.__name__
            # Passing 'self' as controller allows frames to access backend data
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            # Grid places them all in the same cell (0,0) so they overlap
            frame.grid(row=0, column=0, sticky="nsew")

        # Start by showing the Dashboard
        self.show_frame("DashboardFrame")

    def _initialize_demo_data(self):
        """Loads the Milk and Table examples so the app isn't empty on startup."""
        self.logger.log_warning("System Boot Sequence Initiated...")
        
        # Role 2 Integration: Setting up infrastructure
        self.warehouse.add_location(Shelf("SHELF-A", capacity=500, current_load=0, max_height=2.0))
        self.warehouse.add_location(RefrigeratedUnit("FRIDGE-1", capacity=200, min_temp=0, max_temp=5))
        self.warehouse.add_location(Shelf("SHELF-B", capacity=800, current_load=0, max_height=3.0))
        
        # Role 1 Integration: Creating polymorphic products
        # 'milk' is Perishable, 'table' is Durable.
        milk = PerishableProduct("P01", "Almarai Milk", 25.0, 0.005, 1.2, "2025-12-30", 4)
        table = DurableProduct("D01", "Oak Desk", 4500.0, 0.8, 45.0, "Wood", False)
        laptop = DurableProduct("D02", "Dell Laptop", 35000.0, 0.05, 2.5, "Plastic/Metal", True)
        
        self.inventory_mgr.add_product(milk)
        self.inventory_mgr.add_product(table)
        self.inventory_mgr.add_product(laptop)
        
        self.logger.log_warning("Demo Data Loaded Successfully.")

    def setup_sidebar(self):
        """Builds the navigation menu on the left."""
        sidebar = tk.Frame(self, bg="#2c3e50", width=250)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False) # Prevents sidebar from shrinking
        
        # Header
        tk.Label(sidebar, text="SCWOS", font=("Segoe UI", 24, "bold"), fg="#ecf0f1", bg="#2c3e50").pack(pady=40)
        
        # Nav Buttons Definition
        buttons = [
            ("📊 Dashboard", "DashboardFrame"),
            ("📦 Inventory (Role 1)", "InventoryFrame"),
            ("🏭 Warehouse (Role 2)", "WarehouseFrame"),
            ("🚚 Orders (Role 3)", "OrderFrame"),
            ("📜 System Logs", "LogsFrame")
        ]
        
        # Loop to create buttons dynamically
        for text, frame_name in buttons:
            btn = tk.Button(sidebar, text=text, font=("Segoe UI", 12), fg="white", bg="#34495e",
                            bd=0, pady=12, anchor="w", padx=20, activebackground="#1abc9c",
                            # Lambda function to pass specific frame name on click
                            command=lambda f=frame_name: self.show_frame(f))
            btn.pack(fill="x", pady=2)
            
        # Footer
        tk.Label(sidebar, text="v1.0.0 | E-JUST CSE", font=("Arial", 8), fg="#7f8c8d", bg="#2c3e50").pack(side="bottom", pady=20)

    def show_frame(self, page_name):
        """Brings the requested frame to the top of the stack."""
        frame = self.frames[page_name]
        frame.tkraise()
        # OOP Principle: DUCK TYPING
        # If the frame has an 'on_show' method, call it to refresh data.
        if hasattr(frame, "on_show"):
            frame.on_show()

# ==============================================================================
# 📊 FRAME 1: DASHBOARD
# ==============================================================================
class DashboardFrame(tk.Frame):
    """Displays high-level KPIs."""
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller
        
        tk.Label(self, text="System Overview", font=("Segoe UI", 20, "bold"), bg="white").pack(pady=20, anchor="w", padx=20)
        
        self.stats_frame = tk.Frame(self, bg="white")
        self.stats_frame.pack(fill="x", padx=20)
        
        # Reusable UI component creation
        self.card_inv = self.create_card(self.stats_frame, "Total Products", "0", "#3498db")
        self.card_val = self.create_card(self.stats_frame, "Inventory Value", "$0", "#2ecc71")
        self.card_ord = self.create_card(self.stats_frame, "Active Orders", "0", "#e67e22")

    def create_card(self, parent, title, value, color):
        """Helper to create colored KPI cards."""
        card = tk.Frame(parent, bg=color, width=200, height=100)
        card.pack(side="left", padx=10, pady=10)
        card.pack_propagate(False)
        
        tk.Label(card, text=title, font=("Arial", 10), fg="white", bg=color).pack(pady=(20,5))
        lbl_value = tk.Label(card, text=value, font=("Arial", 20, "bold"), fg="white", bg=color)
        lbl_value.pack()
        return lbl_value

    def on_show(self):
        """Called every time this tab is opened to refresh numbers."""
        # INTEGRATION: Pulling data from Role 1 (Inventory) & Role 3 (Orders)
        # Using direct access `_inventory` to ensure compatibility if getter is missing.
        total_items = len(self.controller.inventory_mgr._inventory) 
        total_val = self.controller.inventory_mgr.get_total_inventory_value()
        active_ords = len(self.controller.active_orders)
        
        self.card_inv.config(text=str(total_items))
        self.card_val.config(text=f"${total_val}")
        self.card_ord.config(text=str(active_ords))

# ==============================================================================
# 📦 FRAME 2: INVENTORY (Demonstrating Role 1)
# ==============================================================================
class InventoryFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller
        
        # Header
        header = tk.Frame(self, bg="white")
        header.pack(fill="x", padx=20, pady=20)
        tk.Label(header, text="Inventory Management", font=("Segoe UI", 18, "bold"), bg="white").pack(side="left")
        tk.Button(header, text="+ Add Product", bg="#27ae60", fg="white", command=self.open_add_window).pack(side="right")

        # Treeview (Spreadsheet Table) Setup
        columns = ("ID", "Name", "Type", "Price", "Weight", "Volume", "Status/Details")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.column("Status/Details", width=250)
        self.tree.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def on_show(self):
        """Refreshes the table data from the Backend Dictionary."""
        # Clear existing rows
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Loop through backend products
        for p in self.controller.inventory_mgr._inventory.values():
            detail = ""
            # OOP Principle: POLYMORPHISM 
            # We treat Perishable and Durable differently based on their type.
            if p.product_type == "Perishable":
                detail = f"Exp: {p.expiry_date.date()} | {p.check_status()}"
            else:
                detail = f"Material: {p._material_type}"
                
            self.tree.insert("", "end", values=(
                p.product_id, p.name, p.product_type, 
                f"${p.base_price}", f"{p.weight_kg}kg", f"{p.volume_m3}m3", detail
            ))

    def open_add_window(self):
        """Opens a pop-up window to add new products."""
        win = tk.Toplevel(self)
        win.title("Add New Product")
        win.geometry("400x600")
        
        tk.Label(win, text="Product Details", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Dictionary to store entry widgets
        entries = {}
        fields = ["ID", "Name", "Price", "Weight (kg)", "Volume (m3)"]
        for f in fields:
            frame = tk.Frame(win)
            frame.pack(fill="x", padx=20, pady=5)
            tk.Label(frame, text=f).pack(side="left")
            e = tk.Entry(frame)
            e.pack(side="right", fill="x", expand=True)
            entries[f] = e
            
        # Dropdown for Polymorphic Type Selection
        tk.Label(win, text="Product Type").pack(pady=(10,0))
        type_var = tk.StringVar(value="Durable")
        cb = ttk.Combobox(win, textvariable=type_var, values=["Durable", "Perishable"])
        cb.pack(pady=5)
        
        # Frame for dynamic fields (Fragile vs Expiry)
        dynamic_frame = tk.Frame(win)
        dynamic_frame.pack(fill="both", expand=True, padx=20)
        
        def update_fields(event):
            """Updates form fields based on Product Type selection."""
            for widget in dynamic_frame.winfo_children(): widget.destroy()
            
            if type_var.get() == "Perishable":
                tk.Label(dynamic_frame, text="Expiry (YYYY-MM-DD):").pack(anchor="w")
                entries["Expiry"] = tk.Entry(dynamic_frame)
                entries["Expiry"].pack(fill="x")
                
                tk.Label(dynamic_frame, text="Req Temp (C):").pack(anchor="w")
                entries["Temp"] = tk.Entry(dynamic_frame)
                entries["Temp"].pack(fill="x")
                
            else:
                tk.Label(dynamic_frame, text="Material:").pack(anchor="w")
                entries["Material"] = tk.Entry(dynamic_frame)
                entries["Material"].pack(fill="x")
                
                entries["Fragile"] = tk.BooleanVar()
                tk.Checkbutton(dynamic_frame, text="Is Fragile?", variable=entries["Fragile"]).pack(anchor="w")

        cb.bind("<<ComboboxSelected>>", update_fields)
        update_fields(None) # Initialize fields
        
        def submit():
            try:
                # INTEGRATION: Creating Backend Objects from Frontend Data
                if type_var.get() == "Perishable":
                    new_p = PerishableProduct(
                        entries["ID"].get(), entries["Name"].get(), float(entries["Price"].get()),
                        float(entries["Volume (m3)"].get()), float(entries["Weight (kg)"].get()),
                        entries["Expiry"].get(), float(entries["Temp"].get())
                    )
                else:
                    new_p = DurableProduct(
                        entries["ID"].get(), entries["Name"].get(), float(entries["Price"].get()),
                        float(entries["Volume (m3)"].get()), float(entries["Weight (kg)"].get()),
                        entries["Material"].get(), entries["Fragile"].get()
                    )
                
                # Call Role 1 Manager
                success = self.controller.inventory_mgr.add_product(new_p)
                if success:
                    messagebox.showinfo("Success", "Product Added!")
                    self.on_show() # Refresh main table
                    win.destroy()
                else:
                    messagebox.showerror("Error", "ID already exists.")
                    
            except ValueError as e:
                # Error Handling (Crucial for User Experience)
                messagebox.showerror("Validation Error", str(e))
                
        tk.Button(win, text="Save Product", bg="#3498db", fg="white", command=submit).pack(fill="x", padx=20, pady=20)

# ==============================================================================
# 🏭 FRAME 3: WAREHOUSE (Demonstrating Role 2)
# ==============================================================================
class WarehouseFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller
        
        tk.Label(self, text="Warehouse Optimization Engine", font=("Segoe UI", 18, "bold"), bg="white").pack(pady=20)
        
        # Optimization Controls
        ctrl = tk.Frame(self, bg="#f8f9fa", pady=15)
        ctrl.pack(fill="x", padx=20)
        
        tk.Label(ctrl, text="Select Product to Store:", bg="#f8f9fa").pack(side="left", padx=10)
        self.prod_combo = ttk.Combobox(ctrl, state="readonly", width=30)
        self.prod_combo.pack(side="left", padx=10)
        
        tk.Button(ctrl, text="RUN OPTIMIZATION", bg="#e74c3c", fg="white", font=("Arial", 10, "bold"),
                  command=self.run_optimizer).pack(side="left", padx=20)
        
        # Visualization Container
        self.viz_container = tk.Frame(self, bg="white")
        self.viz_container.pack(fill="both", expand=True, padx=20, pady=20)

    def on_show(self):
        """Populate dropdown and draw current warehouse state."""
        prods = [p.name for p in self.controller.inventory_mgr._inventory.values()]
        self.prod_combo['values'] = prods
        if prods: self.prod_combo.current(0)
        self.draw_warehouse()

    def draw_warehouse(self):
        """Visualizes Storage Locations using Progress Bars."""
        for w in self.viz_container.winfo_children(): w.destroy()
        
        # Loop through Role 2 Storage Locations
        for loc in self.controller.warehouse.locations:
            frame = tk.LabelFrame(self.viz_container, text=f"{loc.location_id} (Cap: {loc.capacity}kg)", 
                                  font=("Arial", 12, "bold"), bg="white", fg="#2c3e50")
            frame.pack(fill="x", pady=5)
            
            # Calculate utilization %
            percent = (loc.current_load / loc.capacity) * 100
            pb = ttk.Progressbar(frame, orient="horizontal", length=100, mode="determinate")
            pb['value'] = percent
            pb.pack(fill="x", padx=10, pady=5)
            
            tk.Label(frame, text=f"Current Load: {loc.current_load}kg | Utilization: {percent:.1f}%", bg="white").pack(anchor="w", padx=10)

    def run_optimizer(self):
        """Triggers Role 2 Algorithm."""
        p_name = self.prod_combo.get()
        # Find product object by name
        product = next((p for p in self.controller.inventory_mgr._inventory.values() if p.name == p_name), None)
        
        if not product:
            return
            
        # CALLING ROLE 2 BACKEND: OptimizationEngine
        loc = self.controller.optimizer.find_best_location(product)
        
        if loc:
            # If logic allows, add it to location
            success = loc.add_item(product)
            if success:
                messagebox.showinfo("Optimization Success", f"Product '{product.name}' placed in {loc.location_id}")
                self.controller.logger.log_warning(f"OPTIMIZER: Moved {product.name} to {loc.location_id}")
                self.draw_warehouse()
            else:
                messagebox.showwarning("Full", "Location found but it is full!")
        else:
            messagebox.showerror("Optimization Failed", "No suitable storage location found (Check Temp/Type/Capacity)")

# ==============================================================================
# 🚚 FRAME 4: ORDERS (Demonstrating Role 3)
# ==============================================================================
class OrderFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller
        
        tk.Label(self, text="Order Processing Center", font=("Segoe UI", 18, "bold"), bg="white").pack(pady=20)
        
        # Section: Create Order
        top = tk.LabelFrame(self, text="Create New Order", bg="white", padx=10, pady=10)
        top.pack(fill="x", padx=20)
        
        tk.Label(top, text="Customer:").grid(row=0, column=0)
        self.cust_entry = tk.Entry(top)
        self.cust_entry.grid(row=0, column=1, padx=10)
        
        self.item_list = tk.Listbox(top, selectmode="multiple", height=5)
        self.item_list.grid(row=0, column=2, padx=10)
        
        tk.Button(top, text="Create Order", bg="#e67e22", fg="white", command=self.create_order).grid(row=0, column=3)
        
        # Section: Manage Orders
        tk.Label(self, text="Active Orders", font=("Arial", 12, "bold"), bg="white").pack(anchor="w", padx=20, pady=(20,5))
        
        self.order_tree = ttk.Treeview(self, columns=("ID", "Customer", "Status", "Items"), show="headings", height=8)
        self.order_tree.heading("ID", text="Order ID")
        self.order_tree.heading("Customer", text="Customer")
        self.order_tree.heading("Status", text="Status")
        self.order_tree.heading("Items", text="Items Count")
        self.order_tree.pack(fill="x", padx=20)
        
        # Workflow Action Buttons
        btn_frame = tk.Frame(self, bg="white")
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Button(btn_frame, text="✅ Pick Order", command=self.pick_order).pack(side="left", padx=5)
        tk.Button(btn_frame, text="🚚 Ship Order", command=self.ship_order).pack(side="left", padx=5)
        tk.Button(btn_frame, text="📫 Deliver", command=self.deliver_order).pack(side="left", padx=5)

    def on_show(self):
        """Updates listbox with available inventory."""
        self.item_list.delete(0, "end")
        for p in self.controller.inventory_mgr._inventory.values():
            self.item_list.insert("end", p.name)
        self.refresh_table()

    def refresh_table(self):
        """Updates the Order Table from local state."""
        for item in self.order_tree.get_children():
            self.order_tree.delete(item)
        for o in self.controller.active_orders:
            self.order_tree.insert("", "end", values=(o.order_id, o._customer_name, o.status, len(o.items)))

    def create_order(self):
        """Instantiates Role 3 CustomerOrder."""
        indices = self.item_list.curselection()
        if not indices:
            messagebox.showwarning("Warning", "Select items first!")
            return
            
        items_to_order = []
        all_prods = list(self.controller.inventory_mgr._inventory.values())
        for i in indices:
            items_to_order.append(all_prods[i])
            
        # Role 3 Backend Usage
        import random
        oid = f"ORD-{random.randint(1000,9999)}"
        new_order = CustomerOrder(oid, self.cust_entry.get(), items_to_order, self.controller.logger)
        
        self.controller.active_orders.append(new_order)
        self.refresh_table()
        messagebox.showinfo("Success", f"Order {oid} Created!")

    def _get_selected_order(self):
        """Helper to find the Order Object selected in the table."""
        sel = self.order_tree.selection()
        if not sel: return None
        oid = self.order_tree.item(sel[0])['values'][0]
        return next((o for o in self.controller.active_orders if o.order_id == oid), None)

    def pick_order(self):
        """Calls backend logic to transition state Pending -> Picked"""
        o = self._get_selected_order()
        if o:
            try:
                o.start_picking(self.controller.inventory_mgr)
                self.refresh_table()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def ship_order(self):
        """Calls backend logic to transition state Picked -> Shipped"""
        o = self._get_selected_order()
        if o:
            try:
                o.mark_shipped()
                # Create Shipment (Role 3 Feature)
                shp = Shipment(f"SHP-{o.order_id}", o.order_id, "FedEx", self.controller.logger)
                trk = shp.generate_tracking()
                messagebox.showinfo("Shipped", f"Tracking: {trk}")
                self.refresh_table()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def deliver_order(self):
        """Calls backend logic to transition state Shipped -> Delivered"""
        o = self._get_selected_order()
        if o:
            try:
                o.mark_delivered()
                self.refresh_table()
            except Exception as e:
                messagebox.showerror("Error", str(e))

# ==============================================================================
# 📜 FRAME 5: LOGS
# ==============================================================================
class LogsFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller
        tk.Label(self, text="System Logs", font=("Segoe UI", 18, "bold"), bg="white").pack(pady=20)
        
        self.txt = tk.Text(self, font=("Consolas", 10))
        self.txt.pack(fill="both", expand=True, padx=20, pady=20)
        
    def on_show(self):
        self.txt.delete(1.0, "end")
        # Role 3 Backend: Fetching logs from TransactionLogger
        logs = self.controller.logger.export_as_text()
        self.txt.insert("end", logs)

# ==============================================================================
# 🏁 APP ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    app = SCWOS_GUI()
    app.mainloop()