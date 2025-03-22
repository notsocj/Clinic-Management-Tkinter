import tkinter as tk
from tkinter import ttk
from db_helper import DatabaseHelper

class MedicineSelector(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Select Medicine")
        self.geometry("600x400")
        self.selected_medicine = None
        
        # Create treeview
        self.tree = ttk.Treeview(self, columns=("ID", "Name", "Generic", "Type"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Brand Name")
        self.tree.heading("Generic", text="Generic Name")
        self.tree.heading("Type", text="Type")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        # Layout
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Load medicines
        self.load_medicines()
        
        # Bind double-click event
        self.tree.bind("<Double-1>", self.select_medicine)

    def load_medicines(self):
        db = DatabaseHelper()
        medicines = db.get_medicines()
        for med in medicines:
            self.tree.insert("", "end", values=med)

    def select_medicine(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            self.selected_medicine = self.tree.item(selected_item)['values']
            self.destroy()
