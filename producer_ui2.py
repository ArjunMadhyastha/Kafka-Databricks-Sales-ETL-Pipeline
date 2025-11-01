import time
import json
import random
import uuid
import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
from kafka import KafkaProducer

# --- 1. Configuration & Global State ---
TOPIC_NAME = "PipelineProject"
KAFKA_SERVER = "kafka-d22a4d0-pipelineproject.f.aivencloud.com:25693"

# Menu Data (Kept consistent with your schema)
MENU = [
    {"item": "Masala Dosa", "price": 70}, 
    {"item": "Idli", "price": 40}, 
    {"item": "Idli Vada", "price": 70}, 
    {"item": "Poori", "price": 50}, 
    {"item": "Chapati", "price": 50}, 
    {"item": "Plain Dosa", "price": 50}, 
    {"item": "Tea", "price": 10}, 
    {"item": "Coffee", "price": 15}, 
    {"item": "Cold Drink", "price": 20}, 
    {"item": "Lassi", "price": 25}
]
TABLES = [f"T{i}" for i in range(1, 11)]
PAYMENT_MODES = ["CASH", "CARD", "UPI"]

# --- 2. Kafka Producer Setup ---
try:
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_SERVER,
        security_protocol="SSL",
        ssl_cafile="ca-2.pem",
        ssl_certfile="service-2.cert",
        ssl_keyfile="service-2.key",
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    PRODUCER_READY = True
except Exception as e:
    print(f"ERROR: Failed to initialize Kafka Producer. Check certificates/server details. Error: {e}")
    PRODUCER_READY = False
    producer = None


# --- 3. UI Application Class ---
class OrderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Restaurant Order Pipeline Tester")
        self.geometry("650x750")
        self.resizable(False, False)
        
        # Configure a custom style for the send button
        style = ttk.Style(self)
        style.configure('Send.TButton', font=('Arial', 12, 'bold'), foreground='green')

        self.order_quantities = {}
        self.total_amount = tk.DoubleVar(value=0.0)

        self._create_widgets()
        self._update_total()

    def _create_widgets(self):
        # --------------------- TOP HEADER ---------------------
        header_font = tkfont.Font(family="Arial", size=18, weight="bold")
        ttk.Label(self, text="Dosa Delight - Order Entry", font=header_font, foreground="#0056b3").pack(pady=10)

        # --------------------- 1. Order Metadata Frame ---------------------
        meta_frame = ttk.LabelFrame(self, text="Order Metadata", padding="15")
        meta_frame.pack(padx=15, pady=5, fill="x")

        # Table ID
        ttk.Label(meta_frame, text="Table ID:", font=('Arial', 10)).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.table_var = tk.StringVar(value=TABLES[0])
        ttk.Combobox(meta_frame, textvariable=self.table_var, values=TABLES, state="readonly", width=10).grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # Customer Count
        ttk.Label(meta_frame, text="Customers:", font=('Arial', 10)).grid(row=0, column=2, padx=10, pady=5, sticky="w")
        self.customer_var = tk.IntVar(value=1)
        ttk.Spinbox(meta_frame, from_=1, to=10, textvariable=self.customer_var, wrap=True, width=5).grid(row=0, column=3, padx=10, pady=5, sticky="w")

        # Payment Mode
        ttk.Label(meta_frame, text="Payment:", font=('Arial', 10)).grid(row=0, column=4, padx=10, pady=5, sticky="w")
        self.payment_var = tk.StringVar(value=PAYMENT_MODES[0])
        ttk.Combobox(meta_frame, textvariable=self.payment_var, values=PAYMENT_MODES, state="readonly", width=8).grid(row=0, column=5, padx=10, pady=5, sticky="ew")
        
        # --------------------- 2. Item Selection Frame ---------------------
        menu_frame = ttk.LabelFrame(self, text="Select Items (Quantity)", padding="15")
        menu_frame.pack(padx=15, pady=10, fill="both", expand=True)

        # Header Row for Menu Items
        ttk.Label(menu_frame, text="Item Name", font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ttk.Label(menu_frame, text="Price (Rs.)", font=('Arial', 10, 'bold')).grid(row=0, column=1, padx=10, pady=5, sticky="w")
        ttk.Label(menu_frame, text="Quantity", font=('Arial', 10, 'bold')).grid(row=0, column=2, padx=10, pady=5, sticky="w")

        # Create input fields for each menu item
        for i, item in enumerate(MENU):
            item_name = item['item']
            item_price = item['price']
            row = i + 1

            # Item Name
            ttk.Label(menu_frame, text=item_name).grid(row=row, column=0, padx=10, pady=2, sticky="w")
            
            # Price
            ttk.Label(menu_frame, text=f"{item_price}").grid(row=row, column=1, padx=10, pady=2, sticky="w")
            
            # Quantity Spinbox
            quantity_var = tk.IntVar(value=0)
            spinbox = ttk.Spinbox(menu_frame, from_=0, to=50, textvariable=quantity_var, wrap=True, width=5)
            spinbox.grid(row=row, column=2, padx=10, pady=2, sticky="w")
            
            # Bind the variable to update total amount whenever quantity changes
            quantity_var.trace_add("write", lambda *args: self._update_total())
            
            self.order_quantities[item_name] = {"var": quantity_var, "price": item_price}
        
        # --------------------- 3. Total and Send Frame ---------------------
        footer_frame = ttk.Frame(self, padding="15", relief="groove")
        footer_frame.pack(padx=15, pady=10, fill="x")
        
        # Total Amount Display
        ttk.Label(footer_frame, text="ORDER TOTAL:", font=('Arial', 12, 'bold')).pack(side="left", padx=10)
        ttk.Label(footer_frame, textvariable=self.total_amount, font=('Arial', 18, 'bold'), foreground='darkred').pack(side="left")
        ttk.Label(footer_frame, text="Rs.").pack(side="left", padx=(0, 30))

        # Reset Button
        ttk.Button(footer_frame, text="CLEAR", command=self.reset_form, width=8).pack(side="right", padx=10)

        # Send Button
        send_button = ttk.Button(footer_frame, text="SEND ORDER", command=self.send_order, style='Send.TButton')
        send_button.pack(side="right")
        
        if not PRODUCER_READY:
             ttk.Label(footer_frame, text="PRODUCER OFFLINE!", foreground='red', font=('Arial', 10, 'bold')).pack(side="right", padx=10)


    def _update_total(self):
        """Recalculates the total amount based on current Spinbox values."""
        current_total = 0
        for item_data in self.order_quantities.values():
            try:
                quantity = item_data["var"].get()
                price = item_data["price"]
                current_total += quantity * price
            except Exception:
                # Silently fail if input is temporarily non-numeric
                pass
        self.total_amount.set(f"{current_total:.2f}")

    def send_order(self):
        """Constructs the order message and sends it via Kafka."""
        if not PRODUCER_READY:
            messagebox.showerror("Error", "Kafka Producer is not initialized.")
            return

        final_order_items = []
        calculated_amount = 0

        # 1. Compile the list of items ordered
        for item_name, data in self.order_quantities.items():
            quantity = data["var"].get()
            price = data["price"]
            
            if quantity > 0:
                final_order_items.append({
                    "name": item_name,
                    "quantity": quantity,
                    "price": price
                })
                calculated_amount += quantity * price

        if not final_order_items:
            messagebox.showwarning("Warning", "The order is empty. Please select at least one item.")
            return
        
        # Validation Check (Ensures total display matches calculation)
        if calculated_amount != float(self.total_amount.get()):
             messagebox.showwarning("Warning", "Total amount mismatch. Please verify inputs.")
             return

        # 2. Assemble the final message dictionary
        message = {
            # Generate a random integer ID (6-digit range)
            "order_id": random.randint(100000, 999999), 
            "table_id": self.table_var.get(),
            "customer_per_order": self.customer_var.get(),
            "payment_mode": self.payment_var.get(),
            "items": final_order_items,
            "amount": calculated_amount,
            "timestamp": int(time.time())
        }

        # 3. Send to Kafka
        try:
            producer.send(TOPIC_NAME, value=message)
            producer.flush() 
            messagebox.showinfo("Success", f"Order {message['order_id']} sent successfully! Total: Rs. {calculated_amount}")
            
            # Optional: Reset the form after successful send
            self.reset_form()

        except Exception as e:
            messagebox.showerror("Kafka Error", f"Failed to send message: {e}")
            print(f"Error sending message: {e}")

    def reset_form(self):
        """Resets quantities and other form fields."""
        # Reset quantities
        for item_data in self.order_quantities.values():
            item_data["var"].set(0)
            
        # Reset metadata
        self.table_var.set(TABLES[0])
        self.customer_var.set(1)
        self.payment_var.set(PAYMENT_MODES[0])
        self._update_total()


# --- 4. Run the Application ---
if __name__ == "__main__":
    app = OrderApp()
    app.mainloop()

    # Cleanly close the producer when the application window is closed
    if PRODUCER_READY and producer:
        print("\nUI closed. Closing Kafka producer.")
        producer.close()