import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from io import BytesIO
import requests
import uuid

class BarcodeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Barcode Scanner")
        self.root.geometry("800x600")
        self.root.iconphoto(False, tk.PhotoImage(file="C:/Python/barcode/icon.png"))
        self.root.configure(bg="#F2F2F2")

        self.barcode_groups = {}

        # Initialize a set to store scanned barcode IDs
        self.scanned_barcode_ids = set()

        self.create_widgets()

    def create_widgets(self):
        # Create a notebook with two tabs: Scan and Search
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True)

        scan_frame = ttk.Frame(notebook)
        search_frame = ttk.Frame(notebook)

        notebook.add(scan_frame, text="Scan")
        notebook.add(search_frame, text="Search")

        # Create and organize the form elements for scanning
        name_label = tk.Label(scan_frame, text="Name:")
        self.name_entry = tk.Entry(scan_frame)
        quantity_label = tk.Label(scan_frame, text="Quantity:")
        self.quantity_entry = tk.Entry(scan_frame)
        price_label = tk.Label(scan_frame, text="Price:")
        self.price_entry = tk.Entry(scan_frame)
        image_url_label = tk.Label(scan_frame, text="Image URL:")
        self.image_url_entry = tk.Entry(scan_frame)
        group_name_label = tk.Label(scan_frame, text="Group Name:")
        self.group_name_entry = tk.Entry(scan_frame)

        # Create buttons for scan action and saving
        scan_button = tk.Button(scan_frame, text="Scan Barcode", command=self.scan_barcode)
        save_button = tk.Button(scan_frame, text="Save", command=self.save_data)
        clear_button = tk.Button(scan_frame, text="Clear Fields", command=self.clear_fields)

        # Create a label for scan result
        self.scan_result_label = tk.Label(scan_frame, text="", wraplength=400)

        # Grid layout for scanning elements
        name_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        quantity_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.quantity_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        price_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.price_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        image_url_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.image_url_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        group_name_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.group_name_entry.grid(row=4, column=1, padx=10, pady=5, sticky="w")
        scan_button.grid(row=5, columnspan=2, padx=10, pady=10)
        save_button.grid(row=6, columnspan=2, padx=10, pady=10)
        clear_button.grid(row=7, columnspan=2, padx=10, pady=10)
        self.scan_result_label.grid(row=8, columnspan=2, padx=10, pady=5)

        # Create and organize the form elements for searching
        search_label = tk.Label(search_frame, text="Search:")
        self.search_entry = tk.Entry(search_frame)
        search_button = tk.Button(search_frame, text="Search", command=self.search)

        # Create a scrolled text widget for displaying search results
        self.search_result_text = scrolledtext.ScrolledText(search_frame, state="disabled", wrap=tk.WORD, width=50, height=10)

        # Grid layout for searching elements
        search_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.search_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        search_button.grid(row=0, column=2, padx=10, pady=10)
        self.search_result_text.grid(row=1, column=0, columnspan=3, padx=10, pady=5)

    def scan_barcode(self):
        try:
            image_url = self.image_url_entry.get()
            name = self.name_entry.get()
            quantity = self.quantity_entry.get()
            price = self.price_entry.get()
            group_name = self.group_name_entry.get()

            # Input validation
            if not name or not quantity or not price or not group_name:
                messagebox.showerror("Error", "Please fill in all fields.")
                return

            if image_url:
                response = requests.get(image_url)
                if response.status_code == 200:
                    image_bytes = BytesIO(response.content)
                    image = cv2.imdecode(np.frombuffer(image_bytes.read(), np.uint8), cv2.IMREAD_COLOR)

                    decoded_objects = decode(image)

                    barcode_data = []

                    for obj in decoded_objects:
                        barcode_id = uuid.uuid4()  # Generate a unique ID for the barcode
                        if barcode_id not in self.scanned_barcode_ids:
                            self.scanned_barcode_ids.add(barcode_id)
                            barcode_data.append({
                                'type': obj.type,
                                'data': obj.data.decode('utf-8'),
                                'name': name,
                                'quantity': quantity,
                                'price': price,
                                'group': group_name,
                            })

                    # Add the barcode data to the corresponding group
                    if group_name not in self.barcode_groups:
                        self.barcode_groups[group_name] = []
                    self.barcode_groups[group_name].extend(barcode_data)

                    self.scan_result_label.config(text=f"Data saved to group '{group_name}'. Barcodes: {barcode_data}")
                else:
                    messagebox.showerror("Error", "Failed to fetch the image")
            else:
                messagebox.showerror("Error", "No image URL provided")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def save_data(self):
        try:
            # Get the barcode data
            group_name = self.group_name_entry.get()

            if group_name in self.barcode_groups and self.barcode_groups[group_name]:
                # Specify the file path where you want to save the data
                file_path = "C:/Python/barcode/barcode_data.txt"

                with open(file_path, 'a') as file:
                    for data in self.barcode_groups[group_name]:
                        file.write(f"Group: {data['group']}, Name: {data['name']}, Type: {data['type']}, Data: {data['data']}, Quantity: {data['quantity']}, Price: {data['price']}\n")

                messagebox.showinfo("Info", f"Data saved successfully to the specified file path under group '{group_name}'")
            else:
                messagebox.showerror("Error", "No data to save")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def search(self):
        try:
            query = self.search_entry.get().strip().lower()

            # Specify the file path where the data is saved
            file_path = "C:/Python/barcode/barcode_data.txt"

            with open(file_path, 'r') as file:
                results = []
                lines = file.readlines()
                for line in lines:
                    if query in line.lower():
                        results.append(line)

            if results:
                self.search_result_text.config(state="normal")
                self.search_result_text.delete(1.0, tk.END)
                for result in results:
                    self.search_result_text.insert(tk.END, result)
                self.search_result_text.config(state="disabled")
            else:
                self.search_result_text.config(state="normal")
                self.search_result_text.delete(1.0, tk.END)
                self.search_result_text.insert(tk.END, "No matching data found")
                self.search_result_text.config(state="disabled")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_fields(self):
        self.name_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.image_url_entry.delete(0, tk.END)
        self.group_name_entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = BarcodeApp(root)
    root.mainloop()
