import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import mysql.connector
from mysql.connector import Error
from datetime import datetime

class DatabaseCRUDApp:
    def __init__(self, root):
        self.root = root
        self.root.title("E-Commerce Database Management System - Complete Version")
        self.root.geometry("1300x750")
        self.root.configure(bg='#f0f0f0')
        
        # Database connection parameters
        self.db_config = {
            'host': 'localhost',
            'database': 'delivery_tracking',  # Change to your database name
            'user': 'root',         # Change to your username
            'password': 'Kaarthimysql@321123'  # Change to your password
        }
        
        self.connection = None
        self.connect_to_database()
        
        # Create main UI
        self.create_widgets()
    
    def connect_to_database(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            if self.connection.is_connected():
                print("Successfully connected to database")
        except Error as e:
            messagebox.showerror("Connection Error", f"Error connecting to database: {e}")
    
    def create_widgets(self):
        """Create the main UI components"""
        # Title
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        title_frame.pack(fill='x')
        title_label = tk.Label(title_frame, text="E-Commerce Database Management System - Complete", 
                              font=('Arial', 18, 'bold'), bg='#2c3e50', fg='white')
        title_label.pack(pady=15)
        
        # Main container
        main_container = tk.Frame(self.root, bg='#f0f0f0')
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left panel - Table selection and procedures
        left_panel = tk.Frame(main_container, bg='white', width=250)
        left_panel.pack(side='left', fill='y', padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Add scrollable area for left panel
        canvas = tk.Canvas(left_panel, bg='white')
        scrollbar = ttk.Scrollbar(left_panel, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Table selection
        tk.Label(scrollable_frame, text="Select Table", font=('Arial', 12, 'bold'), 
                bg='white').pack(pady=10)
        
        tables = ['customers', 'orders', 'order_details', 'products', 
                 'returns', 'reviews', 'shipments']
        
        self.table_var = tk.StringVar(value='customers')
        for table in tables:
            rb = tk.Radiobutton(scrollable_frame, text=table.replace('_', ' ').title(), 
                               variable=self.table_var, value=table,
                               font=('Arial', 10), bg='white',
                               command=self.load_table_data)
            rb.pack(anchor='w', padx=20, pady=5)
        
        # Stored Procedures Section
        tk.Label(scrollable_frame, text="\\nStored Procedures", 
                font=('Arial', 11, 'bold'), bg='white', fg='#2980b9').pack(pady=(15,10))
        
        procedures = [
            ('Get Order History', self.call_get_order_history, '#16a085'),
            ('Generate Sales Report', self.call_generate_sales_report, '#27ae60'),
        ]
        
        for proc_name, proc_func, color in procedures:
            btn = tk.Button(scrollable_frame, text=proc_name, command=proc_func,
                          font=('Arial', 9), bg=color, fg='white',
                          width=20, pady=3)
            btn.pack(pady=2, padx=10)
        
        # Functions Section
        tk.Label(scrollable_frame, text="\\nFunctions", 
                font=('Arial', 11, 'bold'), bg='white', fg='#8e44ad').pack(pady=(15,10))
        
        function_buttons = [
            ('Customer LTV', self.calculate_ltv, '#9b59b6'),
            ('Product Revenue', self.calculate_revenue, '#9b59b6')
        ]
        
        for func_name, func_callback, color in function_buttons:
            tk.Button(scrollable_frame, text=func_name, 
                     command=func_callback,
                     font=('Arial', 9), bg=color, fg='white',
                     width=20, pady=3).pack(pady=2, padx=10)
                
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Right panel - Data display and operations
        right_panel = tk.Frame(main_container, bg='white')
        right_panel.pack(side='right', fill='both', expand=True)
        
        # Operation buttons
        btn_frame = tk.Frame(right_panel, bg='white')
        btn_frame.pack(fill='x', pady=10, padx=10)
        
        tk.Button(btn_frame, text="Create", command=self.create_record,
                 bg='#27ae60', fg='white', font=('Arial', 10, 'bold'),
                 width=12).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="Read/Refresh", command=self.load_table_data,
                 bg='#3498db', fg='white', font=('Arial', 10, 'bold'),
                 width=12).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="Update", command=self.update_record,
                 bg='#f39c12', fg='white', font=('Arial', 10, 'bold'),
                 width=12).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="Delete", command=self.delete_record,
                 bg='#e74c3c', fg='white', font=('Arial', 10, 'bold'),
                 width=12).pack(side='left', padx=5)
        
        # Search functionality
        search_frame = tk.Frame(right_panel, bg='white')
        search_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(search_frame, text="Search:", bg='white', font=('Arial', 10)).pack(side='left')
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=('Arial', 10))
        search_entry.pack(side='left', padx=5, fill='x', expand=True)
        tk.Button(search_frame, text="Search", command=self.search_records,
                 bg='#34495e', fg='white', font=('Arial', 9)).pack(side='left', padx=5)
        
        # Treeview for data display
        tree_frame = tk.Frame(right_panel, bg='white')
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        self.tree = ttk.Treeview(tree_frame, 
                                yscrollcommand=vsb.set,
                                xscrollcommand=hsb.set)
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')
        self.tree.pack(fill='both', expand=True)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = tk.Label(self.root, textvariable=self.status_var, 
                             bd=1, relief=tk.SUNKEN, anchor=tk.W, bg='#ecf0f1')
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Initial load
        self.load_table_data()
    
    def get_table_columns(self, table_name):
        """Get column names for a table"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"DESCRIBE {table_name}")
            columns = [column[0] for column in cursor.fetchall()]
            cursor.close()
            return columns
        except Error as e:
            messagebox.showerror("Error", f"Error fetching columns: {e}")
            return []
    
    def load_table_data(self):
        """Load and display table data"""
        table_name = self.table_var.get()
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            # Get column names
            columns = [desc[0] for desc in cursor.description]
            
            # Clear existing data
            self.tree.delete(*self.tree.get_children())
            
            # Configure columns
            self.tree['columns'] = columns
            self.tree['show'] = 'headings'
            
            for col in columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=120)
            
            # Insert data
            for row in rows:
                self.tree.insert('', 'end', values=row)
            
            cursor.close()
            self.status_var.set(f"Loaded {len(rows)} records from {table_name}")
            
        except Error as e:
            messagebox.showerror("Error", f"Error loading data: {e}")
            self.status_var.set("Error loading data")
    
    def search_records(self):
        """Search records in current table"""
        table_name = self.table_var.get()
        search_text = self.search_var.get()
        
        if not search_text:
            self.load_table_data()
            return
        
        try:
            cursor = self.connection.cursor()
            columns = self.get_table_columns(table_name)
            
            # Create search condition for all text columns
            search_conditions = []
            for col in columns:
                search_conditions.append(f"{col} LIKE '%{search_text}%'")
            
            query = f"SELECT * FROM {table_name} WHERE {' OR '.join(search_conditions)}"
            cursor.execute(query)
            rows = cursor.fetchall()
            
            # Clear and populate tree
            self.tree.delete(*self.tree.get_children())
            for row in rows:
                self.tree.insert('', 'end', values=row)
            
            cursor.close()
            self.status_var.set(f"Found {len(rows)} matching records")
            
        except Error as e:
            messagebox.showerror("Error", f"Error searching: {e}")
    
    def create_record(self):
        """Create new record"""
        table_name = self.table_var.get()
        columns = self.get_table_columns(table_name)
        
        if not columns:
            return
        
        # Create input window
        create_window = tk.Toplevel(self.root)
        create_window.title(f"Create New {table_name.replace('_', ' ').title()} Record")
        create_window.geometry("500x600")
        create_window.configure(bg='white')
        
        tk.Label(create_window, text=f"Enter {table_name.replace('_', ' ').title()} Details",
                font=('Arial', 14, 'bold'), bg='white').pack(pady=15)
        
        entries = {}
        
        # Create scrollable frame
        canvas = tk.Canvas(create_window, bg='white')
        scrollbar = ttk.Scrollbar(create_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for col in columns:
            frame = tk.Frame(scrollable_frame, bg='white')
            frame.pack(fill='x', padx=20, pady=5)
            
            tk.Label(frame, text=col + ":", font=('Arial', 10),
                    bg='white', width=20, anchor='w').pack(side='left')
            
            entry = tk.Entry(frame, font=('Arial', 10), width=30)
            entry.pack(side='left', padx=10)
            entries[col] = entry
        
        canvas.pack(side="left", fill="both", expand=True, padx=10)
        scrollbar.pack(side="right", fill="y")
        
        def save_record():
            values = []
            for col in columns:
                val = entries[col].get()
                if val == '' or val.lower() == 'null':
                    values.append(None)
                else:
                    values.append(val)
            
            try:
                cursor = self.connection.cursor()
                placeholders = ', '.join(['%s'] * len(columns))
                query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
                cursor.execute(query, values)
                self.connection.commit()
                cursor.close()
                
                messagebox.showinfo("Success", "Record created successfully!")
                create_window.destroy()
                self.load_table_data()
                
            except Error as e:
                messagebox.showerror("Error", f"Error creating record: {e}")
        
        tk.Button(create_window, text="Save", command=save_record,
                 bg='#27ae60', fg='white', font=('Arial', 11, 'bold'),
                 width=15).pack(pady=20)
    
    def update_record(self):
        """Update selected record"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a record to update")
            return
        
        table_name = self.table_var.get()
        columns = self.get_table_columns(table_name)
        values = self.tree.item(selected[0])['values']
        
        # Create update window
        update_window = tk.Toplevel(self.root)
        update_window.title(f"Update {table_name.replace('_', ' ').title()} Record")
        update_window.geometry("500x600")
        update_window.configure(bg='white')
        
        tk.Label(update_window, text=f"Update {table_name.replace('_', ' ').title()} Details",
                font=('Arial', 14, 'bold'), bg='white').pack(pady=15)
        
        entries = {}
        
        # Create scrollable frame
        canvas = tk.Canvas(update_window, bg='white')
        scrollbar = ttk.Scrollbar(update_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for i, col in enumerate(columns):
            frame = tk.Frame(scrollable_frame, bg='white')
            frame.pack(fill='x', padx=20, pady=5)
            
            tk.Label(frame, text=col + ":", font=('Arial', 10),
                    bg='white', width=20, anchor='w').pack(side='left')
            
            entry = tk.Entry(frame, font=('Arial', 10), width=30)
            entry.insert(0, str(values[i]) if values[i] is not None else '')
            entry.pack(side='left', padx=10)
            entries[col] = entry
        
        canvas.pack(side="left", fill="both", expand=True, padx=10)
        scrollbar.pack(side="right", fill="y")
        
        def save_update():
            new_values = []
            for col in columns:
                val = entries[col].get()
                if val == '' or val.lower() == 'null':
                    new_values.append(None)
                else:
                    new_values.append(val)
            
            try:
                cursor = self.connection.cursor()
                set_clause = ', '.join([f"{col} = %s" for col in columns])
                # Use first column as primary key for WHERE clause
                where_clause = f"{columns[0]} = %s"
                query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
                cursor.execute(query, new_values + [values[0]])
                self.connection.commit()
                cursor.close()
                
                messagebox.showinfo("Success", "Record updated successfully!")
                update_window.destroy()
                self.load_table_data()
                
            except Error as e:
                messagebox.showerror("Error", f"Error updating record: {e}")
        
        tk.Button(update_window, text="Update", command=save_update,
                 bg='#f39c12', fg='white', font=('Arial', 11, 'bold'),
                 width=15).pack(pady=20)
    
    def delete_record(self):
        """Delete selected record"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a record to delete")
            return
        
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this record?"):
            return
        
        table_name = self.table_var.get()
        columns = self.get_table_columns(table_name)
        values = self.tree.item(selected[0])['values']
        
        try:
            cursor = self.connection.cursor()
            # Use first column as primary key
            query = f"DELETE FROM {table_name} WHERE {columns[0]} = %s"
            cursor.execute(query, (values[0],))
            self.connection.commit()
            cursor.close()
            
            messagebox.showinfo("Success", "Record deleted successfully!")
            self.load_table_data()
            
        except Error as e:
            messagebox.showerror("Error", f"Error deleting record: {e}")
    
    # ===========================================
    # STORED PROCEDURES
    # ===========================================
    
    def call_add_customer(self):
        """Call add_customer stored procedure"""
        proc_window = tk.Toplevel(self.root)
        proc_window.title("Add Customer (Procedure)")
        proc_window.geometry("450x500")
        proc_window.configure(bg='white')
        
        tk.Label(proc_window, text="Add Customer via Stored Procedure",
                font=('Arial', 14, 'bold'), bg='white', fg='#2980b9').pack(pady=15)
        
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 
                 'city', 'state', 'zip_code']
        entries = {}
        
        for field in fields:
            frame = tk.Frame(proc_window, bg='white')
            frame.pack(fill='x', padx=30, pady=8)
            tk.Label(frame, text=field.replace('_', ' ').title() + ":", 
                    bg='white', width=15, anchor='w',
                    font=('Arial', 10)).pack(side='left')
            entry = tk.Entry(frame, width=25, font=('Arial', 10))
            entry.pack(side='left')
            entries[field] = entry
        
        def execute_proc():
            try:
                cursor = self.connection.cursor()
                values = [entries[f].get() if entries[f].get() else None for f in fields]
                cursor.callproc('add_customer', values)
                self.connection.commit()
                cursor.close()
                messagebox.showinfo("Success", "Customer added via procedure!")
                proc_window.destroy()
                if self.table_var.get() == 'customers':
                    self.load_table_data()
            except Error as e:
                messagebox.showerror("Error", f"Error: {e}")
        
        tk.Button(proc_window, text="Execute Procedure", command=execute_proc,
                 bg='#3498db', fg='white', font=('Arial', 11, 'bold'),
                 width=20).pack(pady=25)
    
    def call_add_order(self):
        """Call add_order stored procedure"""
        proc_window = tk.Toplevel(self.root)
        proc_window.title("Add Order (Procedure)")
        proc_window.geometry("400x350")
        proc_window.configure(bg='white')
        
        tk.Label(proc_window, text="Add Order via Stored Procedure",
                font=('Arial', 14, 'bold'), bg='white', fg='#2980b9').pack(pady=15)
        
        fields = ['customer_id', 'order_date', 'total_amount', 'status']
        entries = {}
        
        for field in fields:
            frame = tk.Frame(proc_window, bg='white')
            frame.pack(fill='x', padx=30, pady=12)
            tk.Label(frame, text=field.replace('_', ' ').title() + ":", 
                    bg='white', width=15, anchor='w',
                    font=('Arial', 10)).pack(side='left')
            entry = tk.Entry(frame, width=25, font=('Arial', 10))
            if field == 'order_date':
                entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
            elif field == 'status':
                entry.insert(0, 'pending')
            entry.pack(side='left')
            entries[field] = entry
        
        def execute_proc():
            try:
                cursor = self.connection.cursor()
                values = [entries[f].get() if entries[f].get() else None for f in fields]
                cursor.callproc('add_order', values)
                self.connection.commit()
                cursor.close()
                messagebox.showinfo("Success", "Order added via procedure!")
                proc_window.destroy()
                if self.table_var.get() == 'orders':
                    self.load_table_data()
            except Error as e:
                messagebox.showerror("Error", f"Error: {e}")
        
        tk.Button(proc_window, text="Execute Procedure", command=execute_proc,
                 bg='#3498db', fg='white', font=('Arial', 11, 'bold'),
                 width=20).pack(pady=20)
    
    def call_add_product(self):
        """Call add_product stored procedure"""
        proc_window = tk.Toplevel(self.root)
        proc_window.title("Add Product (Procedure)")
        proc_window.geometry("450x550")
        proc_window.configure(bg='white')
        
        tk.Label(proc_window, text="Add Product via Stored Procedure",
                font=('Arial', 14, 'bold'), bg='white', fg='#2980b9').pack(pady=15)
        
        fields = ['product_name', 'description', 'price', 'stock_quantity', 
                 'category', 'supplier']
        entries = {}
        
        for field in fields:
            frame = tk.Frame(proc_window, bg='white')
            frame.pack(fill='x', padx=30, pady=10)
            tk.Label(frame, text=field.replace('_', ' ').title() + ":", 
                    bg='white', width=15, anchor='w',
                    font=('Arial', 10)).pack(side='left')
            
            if field == 'description':
                entry = tk.Text(frame, width=25, height=3, font=('Arial', 10))
            else:
                entry = tk.Entry(frame, width=25, font=('Arial', 10))
            entry.pack(side='left')
            entries[field] = entry
        
        def execute_proc():
            try:
                cursor = self.connection.cursor()
                values = []
                for f in fields:
                    if f == 'description':
                        val = entries[f].get("1.0", tk.END).strip()
                    else:
                        val = entries[f].get()
                    values.append(val if val else None)
                
                cursor.callproc('add_product', values)
                self.connection.commit()
                cursor.close()
                messagebox.showinfo("Success", "Product added via procedure!")
                proc_window.destroy()
                if self.table_var.get() == 'products':
                    self.load_table_data()
            except Error as e:
                messagebox.showerror("Error", f"Error: {e}")
        
        tk.Button(proc_window, text="Execute Procedure", command=execute_proc,
                 bg='#3498db', fg='white', font=('Arial', 11, 'bold'),
                 width=20).pack(pady=20)
    
    def call_delete_customer(self):
        """Call delete_customer stored procedure"""
        proc_window = tk.Toplevel(self.root)
        proc_window.title("Delete Customer (Procedure)")
        proc_window.geometry("400x250")
        proc_window.configure(bg='white')
        
        tk.Label(proc_window, text="Delete Customer via Stored Procedure",
                font=('Arial', 14, 'bold'), bg='white', fg='#e74c3c').pack(pady=20)
        
        frame = tk.Frame(proc_window, bg='white')
        frame.pack(pady=30)
        tk.Label(frame, text="Customer ID:", bg='white', 
                font=('Arial', 12, 'bold')).pack(side='left', padx=15)
        entry = tk.Entry(frame, width=20, font=('Arial', 12))
        entry.pack(side='left')
        
        def execute_proc():
            customer_id = entry.get()
            if not customer_id:
                messagebox.showwarning("Warning", "Please enter Customer ID")
                return
            
            if not messagebox.askyesno("Confirm", f"Delete customer with ID {customer_id}?"):
                return
                
            try:
                cursor = self.connection.cursor()
                cursor.callproc('delete_customer', [customer_id])
                self.connection.commit()
                cursor.close()
                messagebox.showinfo("Success", "Customer deleted via procedure!")
                proc_window.destroy()
                if self.table_var.get() == 'customers':
                    self.load_table_data()
            except Error as e:
                messagebox.showerror("Error", f"Error: {e}")
        
        tk.Button(proc_window, text="Execute Procedure", command=execute_proc,
                 bg='#e74c3c', fg='white', font=('Arial', 11, 'bold'),
                 width=20).pack(pady=20)
    
    def call_delete_product(self):
        """Call delete_product stored procedure"""
        proc_window = tk.Toplevel(self.root)
        proc_window.title("Delete Product (Procedure)")
        proc_window.geometry("400x250")
        proc_window.configure(bg='white')
        
        tk.Label(proc_window, text="Delete Product via Stored Procedure",
                font=('Arial', 14, 'bold'), bg='white', fg='#e74c3c').pack(pady=20)
        
        frame = tk.Frame(proc_window, bg='white')
        frame.pack(pady=30)
        tk.Label(frame, text="Product ID:", bg='white', 
                font=('Arial', 12, 'bold')).pack(side='left', padx=15)
        entry = tk.Entry(frame, width=20, font=('Arial', 12))
        entry.pack(side='left')
        
        def execute_proc():
            product_id = entry.get()
            if not product_id:
                messagebox.showwarning("Warning", "Please enter Product ID")
                return
            
            if not messagebox.askyesno("Confirm", f"Delete product with ID {product_id}?"):
                return
                
            try:
                cursor = self.connection.cursor()
                cursor.callproc('delete_product', [product_id])
                self.connection.commit()
                cursor.close()
                messagebox.showinfo("Success", "Product deleted via procedure!")
                proc_window.destroy()
                if self.table_var.get() == 'products':
                    self.load_table_data()
            except Error as e:
                messagebox.showerror("Error", f"Error: {e}")
        
        tk.Button(proc_window, text="Execute Procedure", command=execute_proc,
                 bg='#e74c3c', fg='white', font=('Arial', 11, 'bold'),
                 width=20).pack(pady=20)
    
    def call_get_order_history(self):
        """Call get_customer_order_history stored procedure"""
        proc_window = tk.Toplevel(self.root)
        proc_window.title("Customer Order History")
        proc_window.geometry("800x600")
        proc_window.configure(bg='white')
        
        tk.Label(proc_window, text="Get Customer Order History",
                font=('Arial', 14, 'bold'), bg='white', fg='#16a085').pack(pady=15)
        
        input_frame = tk.Frame(proc_window, bg='white')
        input_frame.pack(pady=15)
        tk.Label(input_frame, text="Customer ID:", bg='white', 
                font=('Arial', 12)).pack(side='left', padx=10)
        entry = tk.Entry(input_frame, width=20, font=('Arial', 12))
        entry.pack(side='left', padx=10)
        
        # Results area
        result_frame = tk.Frame(proc_window, bg='white')
        result_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        result_text = scrolledtext.ScrolledText(result_frame, width=90, height=25,
                                               font=('Courier', 10))
        result_text.pack(fill='both', expand=True)
        
        def execute_proc():
            customer_id = entry.get()
            if not customer_id:
                messagebox.showwarning("Warning", "Please enter Customer ID")
                return
                
            try:
                cursor = self.connection.cursor()
                cursor.callproc('get_customer_order_history', [customer_id])
                
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, f"Order History for Customer ID: {customer_id}\\n")
                result_text.insert(tk.END, "=" * 80 + "\\n\\n")
                
                for result in cursor.stored_results():
                    columns = [desc[0] for desc in result.description]
                    
                    # Header
                    header_line = " | ".join([col.ljust(15) for col in columns])
                    result_text.insert(tk.END, header_line + "\\n")
                    result_text.insert(tk.END, "-" * len(header_line) + "\\n")
                    
                    # Data rows
                    rows = result.fetchall()
                    if rows:
                        for row in rows:
                            row_line = " | ".join([str(val).ljust(15) if val is not None else "NULL".ljust(15) for val in row])
                            result_text.insert(tk.END, row_line + "\\n")
                    else:
                        result_text.insert(tk.END, "No orders found for this customer.\\n")
                
                cursor.close()
                result_text.insert(tk.END, f"\\n\\nTotal records found: {len(rows) if 'rows' in locals() else 0}")
                
            except Error as e:
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, f"Error executing procedure: {e}")
        
        tk.Button(proc_window, text="Execute Procedure", command=execute_proc,
                 bg='#16a085', fg='white', font=('Arial', 11, 'bold'),
                 width=20).pack(pady=15)
    
    def call_generate_sales_report(self):
        """Call generate_sales_report stored procedure"""
        proc_window = tk.Toplevel(self.root)
        proc_window.title("Generate Sales Report")
        proc_window.geometry("900x700")
        proc_window.configure(bg='white')
        
        tk.Label(proc_window, text="Generate Sales Report",
                font=('Arial', 16, 'bold'), bg='white', fg='#27ae60').pack(pady=15)
        
        # Input frame for date range
        input_frame = tk.Frame(proc_window, bg='white')
        input_frame.pack(pady=15)
        
        tk.Label(input_frame, text="Start Date (YYYY-MM-DD):", bg='white', 
                font=('Arial', 11)).grid(row=0, column=0, padx=10, pady=5, sticky='w')
        start_date_entry = tk.Entry(input_frame, width=15, font=('Arial', 11))
        start_date_entry.insert(0, "2024-01-01")
        start_date_entry.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(input_frame, text="End Date (YYYY-MM-DD):", bg='white', 
                font=('Arial', 11)).grid(row=0, column=2, padx=10, pady=5, sticky='w')
        end_date_entry = tk.Entry(input_frame, width=15, font=('Arial', 11))
        end_date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        end_date_entry.grid(row=0, column=3, padx=10, pady=5)
        
        # Results area
        result_frame = tk.Frame(proc_window, bg='white')
        result_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        result_text = scrolledtext.ScrolledText(result_frame, width=100, height=30,
                                               font=('Courier', 9))
        result_text.pack(fill='both', expand=True)
        
        def execute_proc():
            start_date = start_date_entry.get()
            end_date = end_date_entry.get()
            
            if not start_date or not end_date:
                messagebox.showwarning("Warning", "Please enter both start and end dates")
                return
                
            try:
                cursor = self.connection.cursor()
                cursor.callproc('generate_sales_report', [start_date, end_date])
                
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, f"SALES REPORT\\nPeriod: {start_date} to {end_date}\\n")
                result_text.insert(tk.END, "=" * 90 + "\\n\\n")
                
                for result in cursor.stored_results():
                    columns = [desc[0] for desc in result.description]
                    rows = result.fetchall()
                    
                    if rows:
                        # Header
                        header_line = " | ".join([col.ljust(12) for col in columns])
                        result_text.insert(tk.END, header_line + "\\n")
                        result_text.insert(tk.END, "-" * len(header_line) + "\\n")
                        
                        # Data rows
                        for row in rows:
                            row_line = " | ".join([str(val).ljust(12) if val is not None else "NULL".ljust(12) for val in row])
                            result_text.insert(tk.END, row_line + "\\n")
                        
                        result_text.insert(tk.END, "\\n")
                    else:
                        result_text.insert(tk.END, "No sales data found for the specified period.\\n\\n")
                
                cursor.close()
                result_text.insert(tk.END, f"\\nReport generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
            except Error as e:
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, f"Error generating sales report: {e}")
        
        tk.Button(proc_window, text="Generate Report", command=execute_proc,
                 bg='#27ae60', fg='white', font=('Arial', 12, 'bold'),
                 width=20).pack(pady=15)
    
    def call_process_return(self):
        """Call process_product_return stored procedure"""
        proc_window = tk.Toplevel(self.root)
        proc_window.title("Process Product Return")
        proc_window.geometry("500x450")
        proc_window.configure(bg='white')
        
        tk.Label(proc_window, text="Process Product Return",
                font=('Arial', 14, 'bold'), bg='white', fg='#f39c12').pack(pady=15)
        
        fields = ['order_id', 'product_id', 'quantity', 'reason', 'return_date']
        entries = {}
        
        for field in fields:
            frame = tk.Frame(proc_window, bg='white')
            frame.pack(fill='x', padx=30, pady=12)
            tk.Label(frame, text=field.replace('_', ' ').title() + ":", 
                    bg='white', width=15, anchor='w',
                    font=('Arial', 11)).pack(side='left')
            
            if field == 'reason':
                entry = tk.Text(frame, width=25, height=3, font=('Arial', 10))
            else:
                entry = tk.Entry(frame, width=25, font=('Arial', 11))
                if field == 'return_date':
                    entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
            entry.pack(side='left')
            entries[field] = entry
        
        def execute_proc():
            try:
                cursor = self.connection.cursor()
                values = []
                for f in fields:
                    if f == 'reason':
                        val = entries[f].get("1.0", tk.END).strip()
                    else:
                        val = entries[f].get()
                    values.append(val if val else None)
                
                cursor.callproc('process_product_return', values)
                self.connection.commit()
                cursor.close()
                messagebox.showinfo("Success", "Product return processed successfully!")
                proc_window.destroy()
                if self.table_var.get() == 'returns':
                    self.load_table_data()
            except Error as e:
                messagebox.showerror("Error", f"Error processing return: {e}")
        
        
    
    # ===========================================
    # FUNCTIONS
    # ===========================================
    
    def calculate_ltv(self):
        """Calculate customer lifetime value"""
        func_window = tk.Toplevel(self.root)
        func_window.title("Customer Lifetime Value")
        func_window.geometry("450x300")
        func_window.configure(bg='white')
        
        tk.Label(func_window, text="Calculate Customer LTV",
                font=('Arial', 14, 'bold'), bg='white', fg='#9b59b6').pack(pady=20)
        
        input_frame = tk.Frame(func_window, bg='white')
        input_frame.pack(pady=20)
        tk.Label(input_frame, text="Customer ID:", bg='white', 
                font=('Arial', 12)).pack(side='left', padx=15)
        entry = tk.Entry(input_frame, width=20, font=('Arial', 12))
        entry.pack(side='left')
        
        result_frame = tk.Frame(func_window, bg='white')
        result_frame.pack(pady=20)
        
        result_label = tk.Label(result_frame, text="", font=('Arial', 16, 'bold'),
                               bg='white', fg='#27ae60')
        result_label.pack()
        
        details_label = tk.Label(result_frame, text="", font=('Arial', 11),
                                bg='white', fg='#7f8c8d', wraplength=400)
        details_label.pack(pady=10)
        
        def execute_func():
            customer_id = entry.get()
            if not customer_id:
                messagebox.showwarning("Warning", "Please enter Customer ID")
                return
                
            try:
                cursor = self.connection.cursor()
                query = f"SELECT calculate_customer_ltv({customer_id})"
                cursor.execute(query)
                result = cursor.fetchone()
                cursor.close()
                
                if result and result[0] is not None:
                    ltv_value = float(result[0])
                    result_label.config(text=f"Customer LTV: ${ltv_value:.2f}")
                    details_label.config(text=f"This represents the total lifetime value for customer ID {customer_id}")
                else:
                    result_label.config(text="Customer not found or no orders")
                    details_label.config(text="")
                    
            except Error as e:
                messagebox.showerror("Error", f"Error calculating LTV: {e}")
        
        tk.Button(func_window, text="Calculate LTV", command=execute_func,
                 bg='#9b59b6', fg='white', font=('Arial', 11, 'bold'),
                 width=20).pack(pady=15)
    
    def calculate_revenue(self):
        """Calculate product revenue"""
        func_window = tk.Toplevel(self.root)
        func_window.title("Product Revenue")
        func_window.geometry("450x300")
        func_window.configure(bg='white')
        
        tk.Label(func_window, text="Calculate Product Revenue",
                font=('Arial', 14, 'bold'), bg='white', fg='#9b59b6').pack(pady=20)
        
        input_frame = tk.Frame(func_window, bg='white')
        input_frame.pack(pady=20)
        tk.Label(input_frame, text="Product ID:", bg='white', 
                font=('Arial', 12)).pack(side='left', padx=15)
        entry = tk.Entry(input_frame, width=20, font=('Arial', 12))
        entry.pack(side='left')
        
        result_frame = tk.Frame(func_window, bg='white')
        result_frame.pack(pady=20)
        
        result_label = tk.Label(result_frame, text="", font=('Arial', 16, 'bold'),
                               bg='white', fg='#27ae60')
        result_label.pack()
        
        details_label = tk.Label(result_frame, text="", font=('Arial', 11),
                                bg='white', fg='#7f8c8d', wraplength=400)
        details_label.pack(pady=10)
        
        def execute_func():
            product_id = entry.get()
            if not product_id:
                messagebox.showwarning("Warning", "Please enter Product ID")
                return
                
            try:
                cursor = self.connection.cursor()
                query = f"SELECT calculate_product_revenue({product_id})"
                cursor.execute(query)
                result = cursor.fetchone()
                cursor.close()
                
                if result and result[0] is not None:
                    revenue_value = float(result[0])
                    result_label.config(text=f"Product Revenue: ${revenue_value:.2f}")
                    details_label.config(text=f"This represents the total revenue generated by product ID {product_id}")
                else:
                    result_label.config(text="Product not found or no sales")
                    details_label.config(text="")
                    
            except Error as e:
                messagebox.showerror("Error", f"Error calculating revenue: {e}")
        
        tk.Button(func_window, text="Calculate Revenue", command=execute_func,
                 bg='#9b59b6', fg='white', font=('Arial', 11, 'bold'),
                 width=20).pack(pady=15)
    
# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = DatabaseCRUDApp(root)
    root.mainloop()