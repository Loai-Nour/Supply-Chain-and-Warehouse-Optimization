import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import backend
from datetime import datetime
import pickle
import os

class InventoryTab(ttk.Frame):
    def __init__(self, parent, inventory_manager, logger):
        super().__init__(parent)
        self.inv_mgr = inventory_manager
        self.logger = logger
        self.create_widgets()

    def create_widgets(self):
        # Layout: Left side for inputs, Right side for list
        split = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        split.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- Left Panel: Input Form ---
        left_frame = ttk.LabelFrame(split, text="Add Product", padding=10)
        split.add(left_frame, weight=1)

        # Product Type Selection
        self.prod_type = tk.StringVar(value="Perishable")
        ttk.Radiobutton(left_frame, text="Perishable", variable=self.prod_type, value="Perishable", command=self.toggle_inputs).pack(anchor="w")
        ttk.Radiobutton(left_frame, text="Durable", variable=self.prod_type, value="Durable", command=self.toggle_inputs).pack(anchor="w")
        
        # Common Fields
        lbl = ttk.Label(left_frame, text="ID:")
        lbl.pack(anchor="w", pady=5)
        self.entry_id = ttk.Entry(left_frame)
        self.entry_id.pack(fill=tk.X)

        lbl = ttk.Label(left_frame, text="Name:")
        lbl.pack(anchor="w", pady=5)
        self.entry_name = ttk.Entry(left_frame)
        self.entry_name.pack(fill=tk.X)

        lbl = ttk.Label(left_frame, text="Price ($):")
        lbl.pack(anchor="w", pady=5)
        self.entry_price = ttk.Entry(left_frame)
        self.entry_price.pack(fill=tk.X)

        lbl = ttk.Label(left_frame, text="Volume (m3):")
        lbl.pack(anchor="w", pady=5)
        self.entry_vol = ttk.Entry(left_frame)
        self.entry_vol.pack(fill=tk.X)

        lbl = ttk.Label(left_frame, text="Weight (kg):")
        lbl.pack(anchor="w", pady=5)
        self.entry_weight = ttk.Entry(left_frame)
        self.entry_weight.pack(fill=tk.X)

        # Variable Fields Frame
        self.var_frame = ttk.Frame(left_frame)
        self.var_frame.pack(fill=tk.X, pady=10)
        
        # Add Button
        ttk.Button(left_frame, text="Add Product", command=self.add_product).pack(fill=tk.X, pady=10)

        # --- Right Panel: Inventory List ---
        right_frame = ttk.LabelFrame(split, text="Current Inventory", padding=10)
        split.add(right_frame, weight=3)

        columns = ("id", "name", "type", "price", "status")
        self.tree = ttk.Treeview(right_frame, columns=columns, show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("type", text="Type")
        self.tree.heading("price", text="Price")
        self.tree.heading("status", text="Info")
        self.tree.column("id", width=50)
        
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        ttk.Button(right_frame, text="Refresh", command=self.refresh_list).pack(fill=tk.X)
        ttk.Button(right_frame, text="Remove Selected", command=self.remove_product).pack(fill=tk.X, pady=5)
        ttk.Button(right_frame, text="Update Price", command=self.update_price).pack(fill=tk.X, pady=5)
        ttk.Button(right_frame, text="Generate Report", command=self.show_report).pack(fill=tk.X, pady=5)

        # Initial Setup
        self.perishable_inputs = []
        self.durable_inputs = []
        self.create_variable_inputs()
        self.toggle_inputs()
        self.refresh_list()

    def create_variable_inputs(self):
        # Perishable specific widgets
        lbl_date = ttk.Label(self.var_frame, text="Expiry (YYYY-MM-DD):")
        ent_date = ttk.Entry(self.var_frame)
        lbl_temp = ttk.Label(self.var_frame, text="Req. Temp (C):")
        ent_temp = ttk.Entry(self.var_frame)
        self.perishable_widgets = [lbl_date, ent_date, lbl_temp, ent_temp]
        self.ent_expiry = ent_date
        self.ent_temp = ent_temp

        # Durable specific widgets
        lbl_mat = ttk.Label(self.var_frame, text="Material:")
        ent_mat = ttk.Entry(self.var_frame)
        self.is_fragile = tk.BooleanVar()
        chk_frag = ttk.Checkbutton(self.var_frame, text="Fragile", variable=self.is_fragile)
        self.durable_widgets = [lbl_mat, ent_mat, chk_frag]
        self.ent_material = ent_mat

    def toggle_inputs(self):
        # Clear frame
        for widget in self.var_frame.winfo_children():
            widget.pack_forget()

        if self.prod_type.get() == "Perishable":
            for w in self.perishable_widgets:
                w.pack(anchor="w", fill=tk.X, pady=2)
        else:
            for w in self.durable_widgets:
                w.pack(anchor="w", fill=tk.X, pady=2)

    def add_product(self):
        try:
            pid = self.entry_id.get()
            name = self.entry_name.get()
            price = float(self.entry_price.get())
            vol = float(self.entry_vol.get())
            weight = float(self.entry_weight.get())

            if self.prod_type.get() == "Perishable":
                expiry = self.ent_expiry.get()
                temp = int(self.ent_temp.get())
                prod = backend.PerishableProduct(pid, name, price, vol, weight, expiry, temp)
            else:
                mat = self.ent_material.get()
                frag = self.is_fragile.get()
                prod = backend.DurableProduct(pid, name, price, vol, weight, mat, frag)

            if self.inv_mgr.add_product(prod):
                self.logger.log_info(f"Product Added: {name} ({prod.product_type})")
                messagebox.showinfo("Success", f"Product {name} added!")
                self.refresh_list()
                # Clear basics
                self.entry_id.delete(0, tk.END)
                self.entry_name.delete(0, tk.END)
            else:
                messagebox.showerror("Error", "Product ID already exists!")

        except ValueError as e:
            messagebox.showerror("Input Error", str(e))

    def remove_product(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Selection", "Please select a product to remove.")
            return
        
        item = self.tree.item(sel[0])
        pid = item['values'][0]
        name = item['values'][1]
        
        if messagebox.askyesno("Confirm", f"Are you sure you want to remove {name} ({pid})?"):
            if self.inv_mgr.remove_product(pid):
                self.logger.log_info(f"Product Removed: {name} ({pid})")
                messagebox.showinfo("Success", "Product removed.")
                self.refresh_list()
            else:
                messagebox.showerror("Error", "Product could not be removed.")

    def update_price(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Selection", "Select a product to update.")
            return

        item = self.tree.item(sel[0])
        pid = item['values'][0]
        name = item['values'][1]
        
        # Simple input dialog
        new_price = tk.simpledialog.askfloat("Update Price", f"Enter new price for {name}:")
        if new_price is not None:
            if self.inv_mgr.update_product_price(pid, new_price):
                self.logger.log_info(f"Price Update: {name} ({pid}) -> ${new_price}")
                messagebox.showinfo("Success", "Price updated.")
                self.refresh_list()
            else:
                messagebox.showerror("Error", "Failed to update price (cannot be negative).")

    def show_report(self):
        report = self.inv_mgr.generate_report()
        # Show in a new window
        top = tk.Toplevel(self)
        top.title("Inventory Report")
        top.geometry("600x600")
        txt = tk.Text(top)
        txt.pack(fill=tk.BOTH, expand=True)
        txt.insert(tk.END, report)
        txt.config(state='disabled')

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Access private inventory dict for display (demo purposes)
        for p in self.inv_mgr._inventory.values():
            info = ""
            if isinstance(p, backend.PerishableProduct):
                info = f"Exp: {p.expiry_date.date()} | {p.check_status()}"
            else:
                info = f"Mat: {p._material_type}"
            
            self.tree.insert("", tk.END, values=(p.product_id, p.name, p.product_type, p.base_price, info))


class WarehouseTab(ttk.Frame):
    def __init__(self, parent, warehouse, inventory_manager, optimizer, logger):
        super().__init__(parent)
        self.warehouse = warehouse
        self.inv_mgr = inventory_manager
        self.optimizer = optimizer
        self.logger = logger
        self.create_widgets()

    def create_widgets(self):
        split = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        split.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left: Add Location
        left_frame = ttk.LabelFrame(split, text="Add Storage Location", padding=10)
        split.add(left_frame, weight=1)

        self.loc_type = tk.StringVar(value="Shelf")
        ttk.Radiobutton(left_frame, text="Shelf (Durable)", variable=self.loc_type, value="Shelf", command=self.toggle_loc_inputs).pack(anchor="w")
        ttk.Radiobutton(left_frame, text="Fridge (Perishable)", variable=self.loc_type, value="Fridge", command=self.toggle_loc_inputs).pack(anchor="w")

        lbl = ttk.Label(left_frame, text="Location ID:")
        lbl.pack(anchor="w", pady=5)
        self.ent_loc_id = ttk.Entry(left_frame)
        self.ent_loc_id.pack(fill=tk.X)

        lbl = ttk.Label(left_frame, text="Capacity (kg):")
        lbl.pack(anchor="w", pady=5)
        self.ent_cap = ttk.Entry(left_frame)
        self.ent_cap.pack(fill=tk.X)

        self.loc_var_frame = ttk.Frame(left_frame)
        self.loc_var_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(left_frame, text="Add Location", command=self.add_location).pack(fill=tk.X)
        
        ttk.Separator(left_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        ttk.Label(left_frame, text="Store Product:").pack(anchor="w")
        self.combo_products = ttk.Combobox(left_frame)
        self.combo_products.pack(fill=tk.X)
        ttk.Button(left_frame, text="Auto-Place Item", command=self.place_item).pack(fill=tk.X, pady=5)
        ttk.Button(left_frame, text="Check Suitability", command=self.check_suitability).pack(fill=tk.X, pady=5)
        
        ttk.Separator(left_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        ttk.Label(left_frame, text="Manage Location Items:").pack(anchor="w")
        ttk.Button(left_frame, text="Remove Selected Item from Location", command=self.remove_item_from_loc).pack(fill=tk.X, pady=5)


        # Right: Locations List
        right_frame = ttk.LabelFrame(split, text="Storage Status", padding=10)
        split.add(right_frame, weight=3)

        cols = ("id", "type", "cap", "load", "free")
        self.tree = ttk.Treeview(right_frame, columns=cols, show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("type", text="Type")
        self.tree.heading("cap", text="Capacity")
        self.tree.heading("load", text="Load")
        self.tree.heading("free", text="Free Space")
        self.tree.pack(fill=tk.BOTH, expand=True)

        ttk.Button(right_frame, text="Refresh", command=self.refresh_all).pack(fill=tk.X)
        
        self.setup_loc_inputs()
        self.toggle_loc_inputs()
        self.refresh_all()

    def setup_loc_inputs(self):
        # Shelf
        self.lbl_height = ttk.Label(self.loc_var_frame, text="Max Height (m):")
        self.ent_height = ttk.Entry(self.loc_var_frame)
        self.shelf_widgets = [self.lbl_height, self.ent_height]

        # Fridge
        self.lbl_min = ttk.Label(self.loc_var_frame, text="Min Temp (C):")
        self.ent_min = ttk.Entry(self.loc_var_frame)
        self.lbl_max = ttk.Label(self.loc_var_frame, text="Max Temp (C):")
        self.ent_max = ttk.Entry(self.loc_var_frame)
        self.fridge_widgets = [self.lbl_min, self.ent_min, self.lbl_max, self.ent_max]

    def toggle_loc_inputs(self):
        for w in self.loc_var_frame.winfo_children():
            w.pack_forget()
        
        if self.loc_type.get() == "Shelf":
            for w in self.shelf_widgets:
                w.pack(anchor="w", fill=tk.X)
        else:
            for w in self.fridge_widgets:
                w.pack(anchor="w", fill=tk.X)

    def add_location(self):
        try:
            lid = self.ent_loc_id.get()
            cap = float(self.ent_cap.get())

            if self.loc_type.get() == "Shelf":
                mh = float(self.ent_height.get())
                loc = backend.Shelf(lid, cap, 0, mh)
            else:
                mint = float(self.ent_min.get())
                maxt = float(self.ent_max.get())
                loc = backend.RefrigeratedUnit(lid, cap, mint, maxt)
            
            self.warehouse.add_location(loc)
            self.logger.log_info(f"Location Added: {lid}")
            self.refresh_all()
            messagebox.showinfo("Success", f"Location {lid} added.")
        except ValueError:
            messagebox.showerror("Error", "Invalid numeric input.")

    def place_item(self):
        sel = self.combo_products.get()
        if not sel:
            return
        
        pid = sel.split(" - ")[0]
        product = self.inv_mgr.get_product(pid)
        if not product:
            return

        loc = self.optimizer.find_best_location(product)
        if loc:
            if loc.add_item(product):
                self.logger.log_info(f"Item Placed: {product.name} -> {loc.location_id}")
                messagebox.showinfo("Stored", f"Placed {product.name} in {loc.location_id}")
                self.refresh_all()
            else:
                messagebox.showwarning("Full", "Location found but it might be full now?")
        else:
            messagebox.showerror("No Space", "No suitable location found for this item.")

    def check_suitability(self):
        # 1. Get Product
        sel_prod = self.combo_products.get()
        if not sel_prod:
            messagebox.showwarning("Select", "Select a product first.")
            return
        pid = sel_prod.split(" - ")[0]
        product = self.inv_mgr.get_product(pid)

        # 2. Get Location (via selection in right tree)
        sel_loc = self.tree.selection()
        if not sel_loc:
            # If no location selected, maybe just check all? Na, explicit is better.
            messagebox.showwarning("Select", "Select a location from the list on the right.")
            return
        
        item = self.tree.item(sel_loc[0])
        lid = item['values'][0]
        loc = self.warehouse.find_location_by_id(lid)

        if not product or not loc:
            return

        is_fit = loc.is_suitable(product)
        msg = "SUITABLE" if is_fit else "NOT SUITABLE"
        messagebox.showinfo("Suitability Check", f"Product: {product.name}\nLocation: {loc.location_id}\nResult: {msg}")

    def remove_item_from_loc(self):
        # 1. Get Location
        sel_loc = self.tree.selection()
        if not sel_loc:
            messagebox.showwarning("Select", "Select a location from the list first.")
            return
        lid = self.tree.item(sel_loc[0])['values'][0]
        loc = self.warehouse.find_location_by_id(lid)

        # 2. Get Product (to determine weight to remove)
        sel_prod = self.combo_products.get()
        if not sel_prod:
            messagebox.showwarning("Select", "Select the product type you are removing (to calculate weight).")
            return
        pid = sel_prod.split(" - ")[0]
        product = self.inv_mgr.get_product(pid)

        if loc and product:
            loc.remove_item(product)
            self.logger.log_info(f"Item Removed from Loc: {product.name} from {loc.location_id}")
            self.refresh_all()
            messagebox.showinfo("Removed", f"Removed weight of {product.name} from {loc.location_id}")

    def refresh_all(self):
        # Update tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for loc in self.warehouse.locations:
            ltype = "Shelf" if isinstance(loc, backend.Shelf) else "Fridge"
            self.tree.insert("", tk.END, values=(loc.location_id, ltype, loc.capacity, loc.current_load, loc.get_remaining_capacity()))

        # Update combo
        products = [f"{p.product_id} - {p.name}" for p in self.inv_mgr._inventory.values()]
        self.combo_products['values'] = products


class OrderTab(ttk.Frame):
    def __init__(self, parent, inventory_manager, warehouse, logger):
        super().__init__(parent)
        self.inv_mgr = inventory_manager
        self.wh = warehouse
        self.logger = logger
        self.orders = []
        self.create_widgets()

    def create_widgets(self):
        main_layout = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_layout.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left: Create Order
        left = ttk.LabelFrame(main_layout, text="New Order", padding=10)
        main_layout.add(left, weight=1)

        ttk.Label(left, text="Order ID:").pack(anchor="w")
        self.ent_oid = ttk.Entry(left)
        self.ent_oid.pack(fill=tk.X)
        self.ent_oid.insert(0, f"ORD-{backend.random.randint(100,999)}")

        ttk.Label(left, text="Customer:").pack(anchor="w", pady=5)
        self.ent_cust = ttk.Entry(left)
        self.ent_cust.pack(fill=tk.X)

        ttk.Label(left, text="Select Items (Multi-select):").pack(anchor="w", pady=5)
        self.lst_products = tk.Listbox(left, selectmode=tk.MULTIPLE, height=10)
        self.lst_products.pack(fill=tk.X, expand=True)
        
        ttk.Button(left, text="Create Order", command=self.create_order).pack(fill=tk.X, pady=10)
        ttk.Button(left, text="Refresh Items", command=self.refresh_items).pack(fill=tk.X)

        # Right: Manage Orders
        right = ttk.LabelFrame(main_layout, text="Active Orders", padding=10)
        main_layout.add(right, weight=2)

        cols = ("oid", "cust", "status", "items")
        self.tree = ttk.Treeview(right, columns=cols, show="headings")
        self.tree.heading("oid", text="Order ID")
        self.tree.heading("cust", text="Customer")
        self.tree.heading("status", text="Status")
        self.tree.heading("items", text="Items")
        self.tree.pack(fill=tk.BOTH, expand=True)

        btn_frame = ttk.Frame(right)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="PICK", command=self.do_pick).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(btn_frame, text="SHIP", command=self.do_ship).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(btn_frame, text="DELIVER", command=self.do_deliver).pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.refresh_items()

    def refresh_items(self):
        self.lst_products.delete(0, tk.END)
        self.product_map = []
        for p in self.inv_mgr._inventory.values():
            self.lst_products.insert(tk.END, f"{p.name} (${p.base_price})")
            self.product_map.append(p)

    def refresh_orders(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for o in self.orders:
            self.tree.insert("", tk.END, values=(o.order_id, o._customer_name, o.status, len(o.items)))

    def create_order(self):
        selections = self.lst_products.curselection()
        if not selections:
            messagebox.showwarning("Empty", "Select at least one product.")
            return

        items = [self.product_map[i] for i in selections]
        oid = self.ent_oid.get()
        cust = self.ent_cust.get()
        
        if not oid or not cust:
            messagebox.showerror("Error", "ID and Customer required.")
            return

        # Check existing ID
        for o in self.orders:
            if o.order_id == oid:
                messagebox.showerror("Error", "Order ID exists.")
                return

        new_order = backend.CustomerOrder(oid, cust, items, self.logger)
        self.orders.append(new_order)
        self.refresh_orders()
        self.ent_oid.delete(0, tk.END)
        self.ent_oid.insert(0, f"ORD-{backend.random.randint(100,999)}")
        messagebox.showinfo("Success", "Order created.")

    def _get_selected_order(self):
        sel = self.tree.selection()
        if not sel: return None
        item = self.tree.item(sel[0])
        oid = item['values'][0]
        for o in self.orders:
            if o.order_id == oid:
                return o
        return None

    def do_pick(self):
        order = self._get_selected_order()
        if order:
            try:
                order.start_picking(self.inv_mgr)
                self.refresh_orders()
            except ValueError as e:
                messagebox.showerror("Error", str(e))

    def do_ship(self):
        order = self._get_selected_order()
        if order:
            try:
                order.mark_shipped()
                # Create dummy shipment for side effects
                backend.Shipment(f"SHP-{order.order_id}", order.order_id, "FedEx", self.logger)
                self.refresh_orders()
            except ValueError as e:
                messagebox.showerror("Error", str(e))

    def do_deliver(self):
        order = self._get_selected_order()
        if order:
            try:
                order.mark_delivered()
                self.refresh_orders()
            except ValueError as e:
                messagebox.showerror("Error", str(e))


class LogsTab(ttk.Frame):
    def __init__(self, parent, logger):
        super().__init__(parent)
        self.logger = logger
        self.txt = tk.Text(self, state='disabled')
        self.txt.pack(fill=tk.BOTH, expand=True)
        ttk.Button(self, text="Refresh Logs", command=self.refresh).pack(fill=tk.X)
        self.refresh()

    def refresh(self):
        self.txt.config(state='normal')
        self.txt.delete(1.0, tk.END)
        self.txt.insert(tk.END, self.logger.export_as_text())
        self.txt.config(state='disabled')


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SCWOS Warehouse Management")
        self.geometry("1000x800")

        # Initialize Backend Systems
        self.logger = backend.TransactionLogger()
        self.inv_mgr = backend.InventoryManager()
        self.warehouse = backend.Warehouse("Central Hub")
        self.optimizer = backend.OptimizationEngine(self.inv_mgr, self.warehouse)

        # Persistence File
        self.data_file = "warehouse_data.pkl"

        # Check for start fresh or load
        # For simplicity, we seed data by default, but user can Load.
        self.seed_data()

        # UI Setup
        self.create_menu()
        
        # Tabs
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        self.tab_inv = InventoryTab(notebook, self.inv_mgr, self.logger)
        notebook.add(self.tab_inv, text="Inventory")

        self.tab_wh = WarehouseTab(notebook, self.warehouse, self.inv_mgr, self.optimizer, self.logger)
        notebook.add(self.tab_wh, text="Warehouse")

        self.tab_ord = OrderTab(notebook, self.inv_mgr, self.warehouse, self.logger)
        notebook.add(self.tab_ord, text="Orders")

        self.tab_logs = LogsTab(notebook, self.logger)
        notebook.add(self.tab_logs, text="System Logs")
        
        notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def create_menu(self):
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Save Data", command=self.save_data)
        file_menu.add_command(label="Load Data", command=self.load_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        self.config(menu=menubar)

    def on_tab_change(self, event):
        # Refresh tabs when switched to
        self.tab_inv.refresh_list()
        self.tab_wh.refresh_all()
        self.tab_ord.refresh_items()
        self.tab_logs.refresh()

    def seed_data(self):
        # Sample Data
        self.inv_mgr.add_product(backend.PerishableProduct("P01", "Milk", 2.50, 0.005, 1.1, "2025-12-30", 4))
        self.inv_mgr.add_product(backend.DurableProduct("D01", "Table", 150.00, 0.5, 20.0, "Wood", False))
        
        self.warehouse.add_location(backend.Shelf("Shelf-A", 500, 0, 2.0))
        self.warehouse.add_location(backend.RefrigeratedUnit("Fridge-B", 200, 0, 5))

    def save_data(self):
        data = {
            "inventory": self.inv_mgr,
            "warehouse": self.warehouse,
            "orders": self.tab_ord.orders,
            # We can't pickle tkinter objects, so we need to be careful.
            # Luckily backend objects are pure python.
        }
        try:
            with open(self.data_file, "wb") as f:
                pickle.dump(data, f)
            messagebox.showinfo("Save", f"Data saved to {self.data_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    def load_data(self):
        if not os.path.exists(self.data_file):
            messagebox.showwarning("Load", "No saved data file found.")
            return
        
        try:
            with open(self.data_file, "rb") as f:
                data = pickle.load(f)
            
            # Restore state
            self.inv_mgr = data["inventory"]
            self.warehouse = data["warehouse"]
            
            # Update References
            self.optimizer.inventory_manager = self.inv_mgr
            self.optimizer.warehouse = self.warehouse
            
            # Update Pointers in Tabs
            self.tab_inv.inv_mgr = self.inv_mgr
            self.tab_wh.inv_mgr = self.inv_mgr
            self.tab_wh.warehouse = self.warehouse
            self.tab_wh.optimizer = self.optimizer
            self.tab_ord.inv_mgr = self.inv_mgr
            self.tab_ord.wh = self.warehouse
            self.tab_ord.orders = data["orders"]
            
            # Log update isn't persisted (it's new session), but that's fine for now.
            
            messagebox.showinfo("Load", "Data loaded successfully.")
            self.tab_inv.refresh_list()
            self.tab_wh.refresh_all()
            self.tab_ord.refresh_orders()
            self.tab_ord.refresh_items()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load: {e}")


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()