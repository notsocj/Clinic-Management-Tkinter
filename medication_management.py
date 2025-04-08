import tkinter as tk
from tkinter import ttk, messagebox
from db_helper import DatabaseHelper
from tkinter import Tk, Label, Entry, Button

# Update the MedAutoCompleteCombobox class with improved dropdown prevention
class MedAutoCompleteCombobox(ttk.Combobox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_selecting = False
        
        # Override the key bindings to disable automatic dropdown
        self.bind("<KeyRelease>", self._on_key_release)
        self.bind("<<ComboboxSelected>>", self._on_selection)
        self.bind("<Down>", self._on_down)
        
        # Disable the built-in Combobox postcommand that shows the dropdown
        self._original_postcommand = self.cget('postcommand')
        self.config(postcommand=self._prevent_auto_post)
        
    def _prevent_auto_post(self):
        """Override default dropdown behavior to prevent it from showing automatically"""
        # Call original postcommand to update values, but don't show dropdown
        if callable(self._original_postcommand):
            self._original_postcommand()
    
    def _on_key_release(self, event):
        """Handle key release events to filter dropdown without losing focus"""
        # Skip processing special keys
        if event.keysym in ('Up', 'Down', 'Left', 'Right', 'Return', 'Escape'):
            return
        
        # Get current text and update matches
        current_text = self.get().strip()
        self.after(1, lambda: self.master.on_brand_key_release(event))
    
    def _on_selection(self, event):
        """Handle selection when dropdown is explicitly shown"""
        self._is_selecting = True
        # Call the original handler
        self._is_selecting = False
        return  # Allow default behavior
        
    def _on_down(self, event):
        """Custom down arrow handler to allow explicit dropdown show"""
        # Only show dropdown when Down arrow is pressed
        if self.cget('values'):
            self.event_generate('<Down>')
            return "break"  # Handle it ourselves
        return  # Let default handler work

class MedicationManagementWindow:
    def __init__(self, parent, callback=None):
        self.parent = parent
        self.callback = callback  # Function to call when medications are saved
        
        # Create the window
        self.window = tk.Toplevel(parent)
        self.window.title("Medication Management")
        self.window.geometry("1000x700")
        self.window.configure(bg="#e6f7ff")
        
        # Color scheme (matching main application)
        self.PRIMARY_COLOR = "#3498db"  # Blue
        self.SECONDARY_COLOR = "#e6f7ff"  # Light blue
        self.ACCENT_COLOR = "#2ecc71"  # Green
        self.WARNING_COLOR = "#e74c3c"  # Red
        self.TEXT_COLOR = "#2c3e50"  # Dark blue/grey
        self.BUTTON_TEXT_COLOR = "white"
        
        # Database helper
        self.db = DatabaseHelper()
        
        # Current medications list
        self.medications = []
        
        # Notification label (added for in-window notifications)
        self.notification_label = None
        
        # Create UI elements
        self.create_widgets()
        self.load_medicines()
        
    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self.window, bg=self.SECONDARY_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Notification area - Add this new frame
        self.notification_frame = tk.Frame(main_frame, bg=self.SECONDARY_COLOR)
        self.notification_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Input section
        input_frame = tk.LabelFrame(main_frame, text="Medication Details", bg=self.SECONDARY_COLOR, fg=self.TEXT_COLOR, font=("Arial", 11, "bold"))
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Brand selection
        tk.Label(input_frame, text="Brand Name:", bg=self.SECONDARY_COLOR, fg=self.TEXT_COLOR).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        # Create a frame to hold the brand dropdown and button
        brand_frame = tk.Frame(input_frame, bg=self.SECONDARY_COLOR)
        brand_frame.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        self.brand_var = tk.StringVar()
        self.brand_dropdown = MedAutoCompleteCombobox(brand_frame, textvariable=self.brand_var, width=30)
        self.brand_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.brand_dropdown.bind("<<ComboboxSelected>>", self.on_brand_select)
        self.brand_dropdown.bind("<KeyRelease>", self.on_brand_key_release)
        
        
        # Generic selection
        tk.Label(input_frame, text="Generic Name:", bg=self.SECONDARY_COLOR, fg=self.TEXT_COLOR).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.generic_var = tk.StringVar()
        self.generic_dropdown = ttk.Combobox(input_frame, textvariable=self.generic_var, width=30)
        self.generic_dropdown.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.generic_dropdown.bind("<<ComboboxSelected>>", self.on_generic_select)
        
        # Quantity
        tk.Label(input_frame, text="Quantity:", bg=self.SECONDARY_COLOR, fg=self.TEXT_COLOR).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.quantity_entry = ttk.Entry(input_frame, width=10)
        self.quantity_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Administration - Changed from Combobox to Entry
        tk.Label(input_frame, text="Administration:", bg=self.SECONDARY_COLOR, fg=self.TEXT_COLOR).grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.admin_var = tk.StringVar()
        self.admin_entry = ttk.Entry(input_frame, textvariable=self.admin_var, width=30)
        self.admin_entry.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        
        # Add button for the input frame
        add_button = tk.Button(input_frame, text="Add to List", 
                              bg=self.ACCENT_COLOR, fg=self.BUTTON_TEXT_COLOR,
                              padx=10, pady=5, command=self.add_to_list)
        add_button.grid(row=2, column=1, padx=5, pady=10, sticky="e")
        
        # Save to DB button
        save_db_button = tk.Button(input_frame, text="Save to Database", 
                                 bg=self.PRIMARY_COLOR, fg=self.BUTTON_TEXT_COLOR,
                                 padx=10, pady=5, command=self.save_to_database)
        save_db_button.grid(row=2, column=2, padx=5, pady=10, sticky="e")
        
        # Delete from DB button
        delete_db_button = tk.Button(input_frame, text="Delete from Database", 
                                  bg=self.WARNING_COLOR, fg=self.BUTTON_TEXT_COLOR,
                                  padx=10, pady=5, command=self.delete_from_database)
        delete_db_button.grid(row=2, column=3, padx=5, pady=10, sticky="e")
        
        # Medication table view
        table_frame = tk.LabelFrame(main_frame, text="Selected Medications", bg=self.SECONDARY_COLOR, fg=self.TEXT_COLOR, font=("Arial", 11, "bold"))
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)
        
        # Create treeview
        self.tree = ttk.Treeview(table_frame, columns=("ID", "Brand", "Generic", "Quantity", "Administration"), show="headings", height=10)
        self.tree.heading("ID", text="ID")
        self.tree.heading("Brand", text="Brand Name")
        self.tree.heading("Generic", text="Generic Name")
        self.tree.heading("Quantity", text="Quantity")
        self.tree.heading("Administration", text="Administration")
        
        self.tree.column("ID", width=50)
        self.tree.column("Brand", width=200)
        self.tree.column("Generic", width=200)
        self.tree.column("Quantity", width=80)
        self.tree.column("Administration", width=150)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Button section
        button_frame = tk.Frame(main_frame, bg=self.SECONDARY_COLOR)
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # Edit button
        edit_button = tk.Button(button_frame, text="Edit Selected", 
                               bg=self.PRIMARY_COLOR, fg=self.BUTTON_TEXT_COLOR,
                               padx=10, pady=5, command=self.edit_selected)
        edit_button.pack(side=tk.LEFT, padx=5)
        
        # Delete button
        delete_button = tk.Button(button_frame, text="Delete Selected", 
                                 bg=self.WARNING_COLOR, fg=self.BUTTON_TEXT_COLOR,
                                 padx=10, pady=5, command=self.delete_selected)
        delete_button.pack(side=tk.LEFT, padx=5)
        
        # Save all button
        save_button = tk.Button(button_frame, text="Save All Medications", 
                               bg=self.ACCENT_COLOR, fg=self.BUTTON_TEXT_COLOR,
                               padx=10, pady=5, command=self.save_all)
        save_button.pack(side=tk.RIGHT, padx=5)
        
        # Back button
        back_button = tk.Button(button_frame, text="Back to Main Menu", 
                               bg=self.PRIMARY_COLOR, fg=self.BUTTON_TEXT_COLOR,
                               padx=10, pady=5, command=self.back_to_main)
        back_button.pack(side=tk.RIGHT, padx=5)
    
    def load_medicines(self):
        # Get medicines from database
        medicines = self.db.get_medicines()
        
        # Extract brand and generic names
        brands = sorted(list(set([med[1] for med in medicines])))
        generics = sorted(list(set([med[2] for med in medicines])))
        
        # Update dropdown values
        self.brand_dropdown['values'] = brands
        self.generic_dropdown['values'] = generics
        
        # Store medicines for later use - Include quantity and administration
        self.medicine_dict = {med[1]: (med[0], med[2], med[3], med[4]) for med in medicines}  # brand: (id, generic, quantity, admin)
        self.generic_dict = {med[2]: (med[0], med[1], med[3], med[4]) for med in medicines}   # generic: (id, brand, quantity, admin)
    
    def on_brand_select(self, event=None):
        selected_brand = self.brand_var.get()
        if selected_brand and selected_brand in self.medicine_dict:
            # Set the corresponding generic name, quantity and administration
            med_id, generic, quantity, admin = self.medicine_dict[selected_brand]
            self.generic_var.set(generic)
            
            # Only set quantity and administration if they have values
            if quantity:
                self.quantity_entry.delete(0, tk.END)
                self.quantity_entry.insert(0, quantity)
            
            if admin:
                self.admin_var.set(admin)
    
    def on_generic_select(self, event=None):
        selected_generic = self.generic_var.get()
        if selected_generic and selected_generic in self.generic_dict:
            # Set the corresponding brand name, quantity and administration
            med_id, brand, quantity, admin = self.generic_dict[selected_generic]
            self.brand_var.set(brand)
            
            # Only set quantity and administration if they have values
            if quantity:
                self.quantity_entry.delete(0, tk.END)
                self.quantity_entry.insert(0, quantity)
            
            if admin:
                self.admin_var.set(admin)
    
    def add_to_list(self):
        # Get values from inputs
        brand = self.brand_var.get()
        generic = self.generic_var.get()
        quantity = self.quantity_entry.get()
        administration = self.admin_var.get()
        
        # Validate inputs
        if not (brand and generic and quantity and administration):
            self.show_notification("Please fill all fields!", self.WARNING_COLOR)
            return
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
        except ValueError:
            self.show_notification("Quantity must be a positive number!", self.WARNING_COLOR)
            return
        
        # Get medicine ID if available
        med_id = None
        if brand in self.medicine_dict:
            med_id = self.medicine_dict[brand][0]
        
        # Add to treeview
        item_id = self.tree.insert("", tk.END, values=(med_id, brand, generic, quantity, administration))
        
        # Add to our medication list
        self.medications.append({
            "id": med_id,
            "brand": brand,
            "generic": generic,
            "quantity": quantity,
            "administration": administration,
            "tree_id": item_id
        })
        
        self.show_notification(f"Added {brand} to the list")
        
        # Clear inputs
        self.clear_inputs()
    
    def edit_selected(self):
        selected_item = self.tree.selection()
        if not selected_item:
            self.show_notification("Please select a medication to edit!", self.WARNING_COLOR)
            return
        
        # Get values from selected item
        values = self.tree.item(selected_item[0])['values']
        
        # Fill inputs with values
        self.brand_var.set(values[1])
        self.generic_var.set(values[2])
        self.quantity_entry.delete(0, tk.END)
        self.quantity_entry.insert(0, values[3])
        self.admin_var.set(values[4])
        
        # Remove from list
        self.delete_selected(False)  # Don't show confirmation
    
    def delete_selected(self, confirm=True):
        selected_item = self.tree.selection()
        if not selected_item:
            self.show_notification("Please select a medication to delete!", self.WARNING_COLOR)
            return
        
        if confirm:
            response = messagebox.askyesno("Confirm", "Are you sure you want to delete this medication?")
            if not response:
                return
        
        # Get the name for notification
        med_name = self.tree.item(selected_item[0])['values'][1]
        
        # Remove from treeview
        tree_id = selected_item[0]
        self.tree.delete(tree_id)
        
        # Remove from our list
        self.medications = [med for med in self.medications if med["tree_id"] != tree_id]
        
        # Show confirmation
        if confirm:  # Only show notification if not called from edit_selected
            self.show_notification(f"Deleted {med_name} from the list")
    
    def save_all(self):
        """Save all medications and send them back to main window"""
        # Get all medications from the tree view
        all_medications = []
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            all_medications.append({
                "id": values[0],
                "brand": values[1],
                "generic": values[2],
                "quantity": values[3],
                "administration": values[4],
                "tree_id": item
            })
        
        if not all_medications:
            self.show_notification("No medications to save!", self.WARNING_COLOR)
            return
        
        # If we have a callback function, call it with all medications
        if self.callback:
            self.callback(all_medications)
            self.show_notification(f"{len(all_medications)} medications saved successfully!")
            # Close with a slight delay to allow notification to be seen
            self.window.after(1500, self.back_to_main)
    
    def back_to_main(self):
        # Close the window
        self.window.destroy()
    
    def clear_inputs(self):
        self.brand_var.set("")
        self.generic_var.set("")
        self.quantity_entry.delete(0, tk.END)
        self.admin_var.set("")
    
    def save_to_database(self):
        """Save the medicine to the database"""
        # Get values from inputs
        brand = self.brand_var.get()
        generic = self.generic_var.get()
        quantity = self.quantity_entry.get()
        administration = self.admin_var.get()
        
        # Validate inputs
        if not (brand and generic):
            self.show_notification("Please enter at least Brand and Generic Name!", self.WARNING_COLOR)
            return
        
        # Check if medicine already exists in DB
        existing_medicine = None
        if brand in self.medicine_dict:
            existing_medicine = (self.medicine_dict[brand][0], brand, generic, quantity, administration)
        
        if existing_medicine:
            # Confirm overwrite
            response = messagebox.askyesno(
                "Medicine Exists", 
                f"Medicine '{brand}' already exists. Do you want to update it?",
                icon='warning'
            )
            if response:
                # Update existing medicine
                try:
                    self.db.update_medicine((generic, quantity, administration, existing_medicine[0]))
                    self.show_notification(f"Medicine '{brand}' updated successfully!")
                    self.load_medicines()  # Refresh medicine list
                except Exception as e:
                    self.show_notification(f"Error: {str(e)}", self.WARNING_COLOR)
        else:
            # Add new medicine
            try:
                self.db.add_medicine((brand, generic, quantity, administration))
                self.show_notification(f"Medicine '{brand}' added successfully!")
                self.load_medicines()  # Refresh medicine list
            except Exception as e:
                self.show_notification(f"Error: {str(e)}", self.WARNING_COLOR)
    
    def delete_from_database(self):
        """Delete the selected medicine from the database"""
        # Get values from inputs
        brand = self.brand_var.get()
        
        # Validate inputs
        if not brand:
            self.show_notification("Please select a medicine to delete!", self.WARNING_COLOR)
            return
        
        # Check if medicine exists
        if brand not in self.medicine_dict:
            self.show_notification(f"Medicine '{brand}' not found in database!", self.WARNING_COLOR)
            return
        
        # Confirm deletion
        response = messagebox.askyesno(
            "Confirm Delete", 
            f"Are you sure you want to delete medicine '{brand}' from the database?\nThis cannot be undone!",
            icon='warning'
        )
        
        if response:
            try:
                med_id = self.medicine_dict[brand][0]
                self.db.delete_medicine(med_id)
                self.show_notification(f"Medicine '{brand}' deleted successfully!")
                self.load_medicines()  # Refresh medicine list
                self.clear_inputs()    # Clear inputs
            except Exception as e:
                self.show_notification(f"Error: {str(e)}", self.WARNING_COLOR)
    
    def show_notification(self, message, bg_color=None, auto_dismiss=True):
        """Display an in-window notification"""
        # Clear any existing notification
        if self.notification_label:
            self.notification_label.destroy()
        
        # Choose color based on message type if not specified
        if bg_color is None:
            if "success" in message.lower() or "updated" in message.lower() or "added" in message.lower():
                bg_color = self.ACCENT_COLOR
            elif "error" in message.lower() or "failed" in message.lower():
                bg_color = self.WARNING_COLOR
            else:
                bg_color = self.PRIMARY_COLOR
        
        # Create notification label
        self.notification_label = tk.Label(
            self.notification_frame,
            text=message,
            bg=bg_color,
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=5,
            relief=tk.RAISED
        )
        self.notification_label.pack(fill=tk.X, pady=5)
        
        # Auto-dismiss notification after delay
        if auto_dismiss:
            self.window.after(3000, self.clear_notification)

    def clear_notification(self):
        """Clear the notification if it exists"""
        if self.notification_label:
            self.notification_label.destroy()
            self.notification_label = None

    def on_brand_key_release(self, event=None):
        """Handle key release in brand dropdown to update values without showing dropdown"""
        current_text = self.brand_var.get().strip()
        
        # Get all brand names
        all_brands = sorted(list(self.medicine_dict.keys()))
        
        # Filter brands based on current text
        if current_text:
            # First priority: names that start with the typed text
            matching_brands = [b for b in all_brands if b.lower().startswith(current_text.lower())]
            
            # Second priority: names that contain the typed text (if we have fewer than 5 starting matches)
            if len(matching_brands) < 5:
                for brand in all_brands:
                    if (not brand.lower().startswith(current_text.lower()) and 
                        current_text.lower() in brand.lower()):
                        matching_brands.append(brand)
        else:
            matching_brands = all_brands
        
        # Sort and update the dropdown values but DO NOT show dropdown
        if matching_brands:
            matching_brands.sort()
            self.brand_dropdown['values'] = matching_brands
        else:
            self.brand_dropdown['values'] = ["No matches found"]

    def show_brand_dropdown(self):
        """Explicitly show the brand dropdown when requested"""
        if self.brand_dropdown['values']:
            self.brand_dropdown.focus_set()  # Make sure dropdown has focus
            self.brand_dropdown.event_generate('<Down>')  # Show the dropdown
