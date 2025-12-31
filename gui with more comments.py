import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import backend  # Imports the logic file (backend.py) where your classes like Product, Warehouse reside
from datetime import datetime
import pickle   # Used for saving and loading data to a file
import os       # Used to check if a file exists on the computer

# =============================================================================
# TAB 1: INVENTORY MANAGEMENT
# =============================================================================
class InventoryTab(ttk.Frame):
    """
    This class represents the 'Inventory' tab in the application.
    It inherits from ttk.Frame, meaning it is a container for other widgets.
    """
    def __init__(self, parent, inventory_manager, logger):
        # Initialize the parent class (ttk.Frame)
        super().__init__(parent)
        
        # Store references to the backend systems so we can use them later
        self.inv_mgr = inventory_manager
        self.logger = logger
        
        # specific function to build the visible interface
        self.create_widgets()

    def create_widgets(self):
        # --- Layout Setup ---
        # PanedWindow creates a split view (resizable divider)
        split = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        split.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- LEFT PANEL: INPUT FORM ---
        # Create a frame for adding products on the left side
        left_frame = ttk.LabelFrame(split, text="Add Product", padding=10)
        split.add(left_frame, weight=1) # weight=1 means it takes up less space than the right

        # Radio buttons to switch between Perishable and Durable inputs
        # 'variable' connects both buttons to the same data string
        self.prod_type = tk.StringVar(value="Perishable")
        ttk.Radiobutton(left_frame, text="Perishable", variable=self.prod_type, value="Perishable", command=self.toggle_inputs).pack(anchor="w")
        ttk.Radiobutton(left_frame, text="Durable", variable=self.prod_type, value="Durable", command=self.toggle_inputs).pack(anchor="w")
        
        # --- Standard Fields (ID, Name, Price, etc.) ---
        # We create a Label (text) and an Entry (input box) for each field
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

        # --- Dynamic Fields Frame ---
        # This frame holds inputs that change based on Product Type (e.g., Expiry Date vs Material)
        self.var_frame = ttk.Frame(left_frame)
        self.var_frame.pack(fill=tk.X, pady=10)
        
        # Button to trigger the 'add_product' function
        ttk.Button(left_frame, text="Add Product", command=self.add_product).pack(fill=tk.X, pady=10)

        # --- RIGHT PANEL: PRODUCT LIST ---
        # Create a frame for viewing the list on the right side
        right_frame = ttk.LabelFrame(split, text="Current Inventory", padding=10)
        split.add(right_frame, weight=3) # weight=3 means it takes up more space

        # define the columns for the table (Treeview)
        columns = ("id", "name", "type", "price", "status")
        self.tree = ttk.Treeview(right_frame, columns=columns, show="headings")
        
        # Set the text for the column headers
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("type", text="Type")
        self.tree.heading("price", text="Price")
        self.tree.heading("status", text="Info")
        self.tree.column("id", width=50) # Make ID column smaller
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        # Pack the list and scrollbar onto the screen
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Action Buttons below the list
        ttk.Button(right_frame, text="Refresh", command=self.refresh_list).pack(fill=tk.X)
        ttk.Button(right_frame, text="Remove Selected", command=self.remove_product).pack(fill=tk.X, pady=5)
        ttk.Button(right_frame, text="Update Price", command=self.update_price).pack(fill=tk.X, pady=5)
        ttk.Button(right_frame, text="Generate Report", command=self.show_report).pack(fill=tk.X, pady=5)

        # --- Final Initialization ---
        # Prepare the lists of widgets for dynamic switching
        self.perishable_inputs = []
        self.durable_inputs = []
        self.create_variable_inputs() # Create the specific input fields
        self.toggle_inputs()          # Show the correct inputs (default Perishable)
        self.refresh_list()           # Load current data

    def create_variable_inputs(self):
        """Creates the widgets for specific product types but doesn't show them yet."""
        # 1. Perishable specific widgets (Expiry Date, Temperature)
        lbl_date = ttk.Label(self.var_frame, text="Expiry (YYYY-MM-DD):")
        ent_date = ttk.Entry(self.var_frame)
        lbl_temp = ttk.Label(self.var_frame, text="Req. Temp (C):")
        ent_temp = ttk.Entry(self.var_frame)
        # Store them in a list so we can pack/unpack them easily
        self.perishable_widgets = [lbl_date, ent_date, lbl_temp, ent_temp]
        self.ent_expiry = ent_date
        self.ent_temp = ent_temp

        # 2. Durable specific widgets (Material, Fragile Checkbox)
        lbl_mat = ttk.Label(self.var_frame, text="Material:")
        ent_mat = ttk.Entry(self.var_frame)
        self.is_fragile = tk.BooleanVar()
        chk_frag = ttk.Checkbutton(self.var_frame, text="Fragile", variable=self.is_fragile)
        # Store in list
        self.durable_widgets = [lbl_mat, ent_mat, chk_frag]
        self.ent_material = ent_mat

    def toggle_inputs(self):
        """Swaps the visible inputs based on the RadioButton selection."""
        # First, remove all widgets currently in the variable frame
        for widget in self.var_frame.winfo_children():
            widget.pack_forget()

        # Check which radio button is selected
        if self.prod_type.get() == "Perishable":
            # Add perishable widgets
            for w in self.perishable_widgets:
                w.pack(anchor="w", fill=tk.X, pady=2)
        else:
            # Add durable widgets
            for w in self.durable_widgets:
                w.pack(anchor="w", fill=tk.X, pady=2)

    def add_product(self):
        """Collects data from form, creates object, sends to backend."""
        try:
            # Get data from standard entry boxes
            pid = self.entry_id.get()
            name = self.entry_name.get()
            price = float(self.entry_price.get())  # Convert text to number
            vol = float(self.entry_vol.get())
            weight = float(self.entry_weight.get())

            # Create the specific object based on type
            if self.prod_type.get() == "Perishable":
                expiry = self.ent_expiry.get()
                temp = int(self.ent_temp.get())
                # Create Perishable Object
                prod = backend.PerishableProduct(pid, name, price, vol, weight, expiry, temp)
            else:
                mat = self.ent_material.get()
                frag = self.is_fragile.get()
                # Create Durable Object
                prod = backend.DurableProduct(pid, name, price, vol, weight, mat, frag)

            # Send to Inventory Manager Backend
            if self.inv_mgr.add_product(prod):
                self.logger.log_info(f"Product Added: {name} ({prod.product_type})")
                messagebox.showinfo("Success", f"Product {name} added!")
                self.refresh_list()
                
                # Clear basic inputs for next entry
                self.entry_id.delete(0, tk.END)
                self.entry_name.delete(0, tk.END)
            else:
                messagebox.showerror("Error", "Product ID already exists!")

        except ValueError as e:
            # Catches errors if user types text into a number field
            messagebox.showerror("Input Error", str(e))

    def remove_product(self):
        """Removes the selected item from the Treeview list."""
        # Get selected row
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Selection", "Please select a product to remove.")
            return
        
        # Get the Product ID from the selected row
        item = self.tree.item(sel[0])
        pid = item['values'][0]
        name = item['values'][1]
        
        # Confirm with user
        if messagebox.askyesno("Confirm", f"Are you sure you want to remove {name} ({pid})?"):
            if self.inv_mgr.remove_product(pid):
                self.logger.log_info(f"Product Removed: {name} ({pid})")
                messagebox.showinfo("Success", "Product removed.")
                self.refresh_list()
            else:
                messagebox.showerror("Error", "Product could not be removed.")

    def update_price(self):
        """updates price of selected item."""
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Selection", "Select a product to update.")
            return

        item = self.tree.item(sel[0])
        pid = item['values'][0]
        name = item['values'][1]
        
        # Show a small pop-up dialog to ask for the new price
        new_price = tk.simpledialog.askfloat("Update Price", f"Enter new price for {name}:")
        if new_price is not None:
            if self.inv_mgr.update_product_price(pid, new_price):
                self.logger.log_info(f"Price Update: {name} ({pid}) -> ${new_price}")
                messagebox.showinfo("Success", "Price updated.")
                self.refresh_list()
            else:
                messagebox.showerror("Error", "Failed to update price (cannot be negative).")

    def show_report(self):
        """Generates text report and shows it in a new window."""
        report = self.inv_mgr.generate_report()
        
        # Toplevel creates a new pop-up window
        top = tk.Toplevel(self)
        top.title("Inventory Report")
        top.geometry("600x600")
        
        # Text widget to display the long string
        txt = tk.Text(top)
        txt.pack(fill=tk.BOTH, expand=True)
        txt.insert(tk.END, report)
        txt.config(state='disabled') # Make it read-only

    def refresh_list(self):
        """Clears the table and re-reads data from backend."""
        # Delete all current rows in the UI
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Loop through dictionary in backend
        # Note: Accessing _inventory (private) directly for demo purposes
        for p in self.inv_mgr._inventory.values():
            info = ""
            # Determine special info based on type
            if isinstance(p, backend.PerishableProduct):
                info = f"Exp: {p.expiry_date.date()} | {p.check_status()}"
            else:
                info = f"Mat: {p._material_type}"
            
            # Insert row into table
            self.tree.insert("", tk.END, values=(p.product_id, p.name, p.product_type, p.base_price, info))


# =============================================================================
# TAB 2: WAREHOUSE / STORAGE LOCATIONS
# =============================================================================
class WarehouseTab(ttk.Frame):
    def __init__(self, parent, warehouse, inventory_manager, optimizer, logger):
        super().__init__(parent)
        self.warehouse = warehouse
        self.inv_mgr = inventory_manager
        self.optimizer = optimizer
        self.logger = logger
        self.create_widgets()

    def create_widgets(self):
        # Create split layout
        split = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        split.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- LEFT PANEL: ADD LOCATIONS & ACTIONS ---
        left_frame = ttk.LabelFrame(split, text="Add Storage Location", padding=10)
        split.add(left_frame, weight=1)

        # Radio buttons for location type (Shelf vs Fridge)
        self.loc_type = tk.StringVar(value="Shelf")
        ttk.Radiobutton(left_frame, text="Shelf (Durable)", variable=self.loc_type, value="Shelf", command=self.toggle_loc_inputs).pack(anchor="w")
        ttk.Radiobutton(left_frame, text="Fridge (Perishable)", variable=self.loc_type, value="Fridge", command=self.toggle_loc_inputs).pack(anchor="w")

        # Standard Location Fields
        lbl = ttk.Label(left_frame, text="Location ID:")
        lbl.pack(anchor="w", pady=5)
        self.ent_loc_id = ttk.Entry(left_frame)
        self.ent_loc_id.pack(fill=tk.X)

        lbl = ttk.Label(left_frame, text="Capacity (kg):")
        lbl.pack(anchor="w", pady=5)
        self.ent_cap = ttk.Entry(left_frame)
        self.ent_cap.pack(fill=tk.X)

        # Variable inputs container
        self.loc_var_frame = ttk.Frame(left_frame)
        self.loc_var_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(left_frame, text="Add Location", command=self.add_location).pack(fill=tk.X)
        
        # Separator line
        ttk.Separator(left_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        # --- Placing Items Logic ---
        ttk.Label(left_frame, text="Store Product:").pack(anchor="w")
        
        # Combobox: A dropdown menu to select a product
        self.combo_products = ttk.Combobox(left_frame)
        self.combo_products.pack(fill=tk.X)
        
        ttk.Button(left_frame, text="Auto-Place Item", command=self.place_item).pack(fill=tk.X, pady=5)
        ttk.Button(left_frame, text="Check Suitability", command=self.check_suitability).pack(fill=tk.X, pady=5)
        
        ttk.Separator(left_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        # Removing Item Logic
        ttk.Label(left_frame, text="Manage Location Items:").pack(anchor="w")
        ttk.Button(left_frame, text="Remove Selected Item from Location", command=self.remove_item_from_loc).pack(fill=tk.X, pady=5)


        # --- RIGHT PANEL: LOCATION LIST ---
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
        
        # Setup the inputs for first run
        self.setup_loc_inputs()
        self.toggle_loc_inputs()
        self.refresh_all()

    def setup_loc_inputs(self):
        """Prepare inputs for Shelf vs Fridge."""
        # Shelf inputs
        self.lbl_height = ttk.Label(self.loc_var_frame, text="Max Height (m):")
        self.ent_height = ttk.Entry(self.loc_var_frame)
        self.shelf_widgets = [self.lbl_height, self.ent_height]

        # Fridge inputs
        self.lbl_min = ttk.Label(self.loc_var_frame, text="Min Temp (C):")
        self.ent_min = ttk.Entry(self.loc_var_frame)
        self.lbl_max = ttk.Label(self.loc_var_frame, text="Max Temp (C):")
        self.ent_max = ttk.Entry(self.loc_var_frame)
        self.fridge_widgets = [self.lbl_min, self.ent_min, self.lbl_max, self.ent_max]

    def toggle_loc_inputs(self):
        """Show inputs matching radio selection."""
        for w in self.loc_var_frame.winfo_children():
            w.pack_forget()
        
        if self.loc_type.get() == "Shelf":
            for w in self.shelf_widgets:
                w.pack(anchor="w", fill=tk.X)
        else:
            for w in self.fridge_widgets:
                w.pack(anchor="w", fill=tk.X)

    def add_location(self):
        """Creates a location object (Shelf/Fridge) and adds to warehouse."""
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
        """Uses the Optimization Engine to find where an item fits."""
        # Get selection from dropdown
        sel = self.combo_products.get()
        if not sel:
            return
        
        # Extract ID (Format is "ID - Name")
        pid = sel.split(" - ")[0]
        product = self.inv_mgr.get_product(pid)
        if not product:
            return

        # Use backend logic to find best spot
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
        """Manually checks if specific product fits in specific selected location."""
        # 1. Get Product from Dropdown
        sel_prod = self.combo_products.get()
        if not sel_prod:
            messagebox.showwarning("Select", "Select a product first.")
            return
        pid = sel_prod.split(" - ")[0]
        product = self.inv_mgr.get_product(pid)

        # 2. Get Location (via selection in right tree)
        sel_loc = self.tree.selection()
        if not sel_loc:
            messagebox.showwarning("Select", "Select a location from the list on the right.")
            return
        
        item = self.tree.item(sel_loc[0])
        lid = item['values'][0]
        loc = self.warehouse.find_location_by_id(lid)

        if not product or not loc:
            return

        # Run check
        is_fit = loc.is_suitable(product)
        msg = "SUITABLE" if is_fit else "NOT SUITABLE"
        messagebox.showinfo("Suitability Check", f"Product: {product.name}\nLocation: {loc.location_id}\nResult: {msg}")

    def remove_item_from_loc(self):
        """Removes an item's weight from a location."""
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
        """Reloads the list of locations and updates the product dropdown."""
        # Update tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for loc in self.warehouse.locations:
            ltype = "Shelf" if isinstance(loc, backend.Shelf) else "Fridge"
            self.tree.insert("", tk.END, values=(loc.location_id, ltype, loc.capacity, loc.current_load, loc.get_remaining_capacity()))

        # Update product dropdown values
        products = [f"{p.product_id} - {p.name}" for p in self.inv_mgr._inventory.values()]
        self.combo_products['values'] = products


# =============================================================================
# TAB 3: ORDER PROCESSING
# =============================================================================
class OrderTab(ttk.Frame):
    def __init__(self, parent, inventory_manager, warehouse, logger):
        super().__init__(parent)
        self.inv_mgr = inventory_manager
        self.wh = warehouse
        self.logger = logger
        self.orders = [] # Local list to track active orders in memory
        self.create_widgets()

    def create_widgets(self):
        main_layout = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_layout.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- LEFT: CREATE ORDER FORM ---
        left = ttk.LabelFrame(main_layout, text="New Order", padding=10)
        main_layout.add(left, weight=1)

        ttk.Label(left, text="Order ID:").pack(anchor="w")
        self.ent_oid = ttk.Entry(left)
        self.ent_oid.pack(fill=tk.X)
        # Pre-fill with a random ID for convenience
        self.ent_oid.insert(0, f"ORD-{backend.random.randint(100,999)}")

        ttk.Label(left, text="Customer:").pack(anchor="w", pady=5)
        self.ent_cust = ttk.Entry(left)
        self.ent_cust.pack(fill=tk.X)

        ttk.Label(left, text="Select Items (Multi-select):").pack(anchor="w", pady=5)
        
        # Listbox allows selecting multiple items (unlike Combobox)
        self.lst_products = tk.Listbox(left, selectmode=tk.MULTIPLE, height=10)
        self.lst_products.pack(fill=tk.X, expand=True)
        
        ttk.Button(left, text="Create Order", command=self.create_order).pack(fill=tk.X, pady=10)
        ttk.Button(left, text="Refresh Items", command=self.refresh_items).pack(fill=tk.X)

        # --- RIGHT: MANAGE ORDERS ---
        right = ttk.LabelFrame(main_layout, text="Active Orders", padding=10)
        main_layout.add(right, weight=2)

        cols = ("oid", "cust", "status", "items")
        self.tree = ttk.Treeview(right, columns=cols, show="headings")
        self.tree.heading("oid", text="Order ID")
        self.tree.heading("cust", text="Customer")
        self.tree.heading("status", text="Status")
        self.tree.heading("items", text="Items")
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Workflow Buttons
        btn_frame = ttk.Frame(right)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="PICK", command=self.do_pick).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(btn_frame, text="SHIP", command=self.do_ship).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(btn_frame, text="DELIVER", command=self.do_deliver).pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.refresh_items()

    def refresh_items(self):
        """Fills the ListBox with available products."""
        self.lst_products.delete(0, tk.END)
        self.product_map = [] # Helper list to map Listbox index to Product Object
        for p in self.inv_mgr._inventory.values():
            self.lst_products.insert(tk.END, f"{p.name} (${p.base_price})")
            self.product_map.append(p)

    def refresh_orders(self):
        """Updates the Order Treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        for o in self.orders:
            self.tree.insert("", tk.END, values=(o.order_id, o._customer_name, o.status, len(o.items)))

    def create_order(self):
        """Compiles selected items into a new Order object."""
        # Get indices of selected rows in Listbox
        selections = self.lst_products.curselection()
        if not selections:
            messagebox.showwarning("Empty", "Select at least one product.")
            return

        # Map indices back to actual product objects
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

        # Create Order Object
        new_order = backend.CustomerOrder(oid, cust, items, self.logger)
        self.orders.append(new_order)
        self.refresh_orders()
        
        # Reset ID field
        self.ent_oid.delete(0, tk.END)
        self.ent_oid.insert(0, f"ORD-{backend.random.randint(100,999)}")
        messagebox.showinfo("Success", "Order created.")

    def _get_selected_order(self):
        """Helper to find which order is clicked in the treeview."""
        sel = self.tree.selection()
        if not sel: return None
        item = self.tree.item(sel[0])
        oid = item['values'][0]
        for o in self.orders:
            if o.order_id == oid:
                return o
        return None

    def do_pick(self):
        """Updates order status to Picked."""
        order = self._get_selected_order()
        if order:
            try:
                order.start_picking(self.inv_mgr)
                self.refresh_orders()
            except ValueError as e:
                messagebox.showerror("Error", str(e))

    def do_ship(self):
        """Updates order status to Shipped."""
        order = self._get_selected_order()
        if order:
            try:
                order.mark_shipped()
                # Create dummy shipment for logging
                backend.Shipment(f"SHP-{order.order_id}", order.order_id, "FedEx", self.logger)
                self.refresh_orders()
            except ValueError as e:
                messagebox.showerror("Error", str(e))

    def do_deliver(self):
        """Updates order status to Delivered."""
        order = self._get_selected_order()
        if order:
            try:
                order.mark_delivered()
                self.refresh_orders()
            except ValueError as e:
                messagebox.showerror("Error", str(e))


# =============================================================================
# TAB 4: LOGS VIEW
# =============================================================================
class LogsTab(ttk.Frame):
    def __init__(self, parent, logger):
        super().__init__(parent)
        self.logger = logger
        # Text widget for displaying multi-line text
        self.txt = tk.Text(self, state='disabled') 
        self.txt.pack(fill=tk.BOTH, expand=True)
        ttk.Button(self, text="Refresh Logs", command=self.refresh).pack(fill=tk.X)
        self.refresh()

    def refresh(self):
        # Enable editing momentarily to insert text
        self.txt.config(state='normal')
        self.txt.delete(1.0, tk.END) # Clear all
        self.txt.insert(tk.END, self.logger.export_as_text()) # Insert logs
        self.txt.config(state='disabled') # Disable editing again


# =============================================================================
# MAIN APPLICATION WINDOW
# =============================================================================
class MainApp(tk.Tk):
    """
    The main entry point of the application.
    Inherits from tk.Tk (the main window).
    """
    def __init__(self):
        super().__init__()
        self.title("SCWOS Warehouse Management")
        self.geometry("1000x800") # Set window size

        # --- Initialize Backend Systems ---
        # These are the logic classes from your backend.py
        self.logger = backend.TransactionLogger()
        self.inv_mgr = backend.InventoryManager()
        self.warehouse = backend.Warehouse("Central Hub")
        self.optimizer = backend.OptimizationEngine(self.inv_mgr, self.warehouse)

        # File path for saving/loading
        self.data_file = "warehouse_data.pkl"

        # Load dummy data for testing (or you could load from file)
        self.seed_data()

        # --- UI Setup ---
        self.create_menu()
        
        # Notebook handles Tabs
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Create instances of our Tab classes and add them to notebook
        self.tab_inv = InventoryTab(notebook, self.inv_mgr, self.logger)
        notebook.add(self.tab_inv, text="Inventory")

        self.tab_wh = WarehouseTab(notebook, self.warehouse, self.inv_mgr, self.optimizer, self.logger)
        notebook.add(self.tab_wh, text="Warehouse")

        self.tab_ord = OrderTab(notebook, self.inv_mgr, self.warehouse, self.logger)
        notebook.add(self.tab_ord, text="Orders")

        self.tab_logs = LogsTab(notebook, self.logger)
        notebook.add(self.tab_logs, text="System Logs")
        
        # Add event listener to refresh tabs when clicked
        notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def create_menu(self):
        """Creates the File > Save/Load/Exit menu at top."""
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Save Data", command=self.save_data)
        file_menu.add_command(label="Load Data", command=self.load_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        self.config(menu=menubar)

    def on_tab_change(self, event):
        """Refreshes the active tab so data stays in sync."""
        self.tab_inv.refresh_list()
        self.tab_wh.refresh_all()
        self.tab_ord.refresh_items()
        self.tab_logs.refresh()

    def seed_data(self):
        """Creates some dummy data so the app isn't empty on start."""
        self.inv_mgr.add_product(backend.PerishableProduct("P01", "Milk", 2.50, 0.005, 1.1, "2025-12-30", 4))
        self.inv_mgr.add_product(backend.DurableProduct("D01", "Table", 150.00, 0.5, 20.0, "Wood", False))
        
        self.warehouse.add_location(backend.Shelf("Shelf-A", 500, 0, 2.0))
        self.warehouse.add_location(backend.RefrigeratedUnit("Fridge-B", 200, 0, 5))

    def save_data(self):
        """Saves current state to a binary file using Pickle."""
        data = {
            "inventory": self.inv_mgr,
            "warehouse": self.warehouse,
            "orders": self.tab_ord.orders,
        }
        try:
            with open(self.data_file, "wb") as f:
                pickle.dump(data, f)
            messagebox.showinfo("Save", f"Data saved to {self.data_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    def load_data(self):
        """Loads state from file and overwrites current app state."""
        if not os.path.exists(self.data_file):
            messagebox.showwarning("Load", "No saved data file found.")
            return
        
        try:
            with open(self.data_file, "rb") as f:
                data = pickle.load(f)
            
            # Restore state variables
            self.inv_mgr = data["inventory"]
            self.warehouse = data["warehouse"]
            
            # Update References in other objects (IMPORTANT)
            # We must tell the optimizer and tabs to look at the NEW loaded objects
            self.optimizer.inventory_manager = self.inv_mgr
            self.optimizer.warehouse = self.warehouse
            
            self.tab_inv.inv_mgr = self.inv_mgr
            self.tab_wh.inv_mgr = self.inv_mgr
            self.tab_wh.warehouse = self.warehouse
            self.tab_wh.optimizer = self.optimizer
            self.tab_ord.inv_mgr = self.inv_mgr
            self.tab_ord.wh = self.warehouse
            self.tab_ord.orders = data["orders"]
            
            messagebox.showinfo("Load", "Data loaded successfully.")
            
            # Refresh all UIs
            self.tab_inv.refresh_list()
            self.tab_wh.refresh_all()
            self.tab_ord.refresh_orders()
            self.tab_ord.refresh_items()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load: {e}")

# Check if this file is being run directly (not imported)
if __name__ == "__main__":
    app = MainApp()
    app.mainloop() # Keeps the window open