import tkinter as tk
from tkinter import ttk, messagebox
import tkcalendar  # Add this import for the calendar widget
from db_helper import DatabaseHelper
from medicine_select import MedicineSelector
import sqlite3
from ttkwidgets.autocomplete import AutocompleteCombobox
from datetime import datetime, date
from tkcalendar import Calendar  # Change from DateEntry to Calendar

# Main Application Window
root = tk.Tk()
root.title("Clinic Management System")
root.geometry("1200x700")  # Increased width to accommodate sidebar
root.configure(bg="#e6f7ff")  # Light blue background

# Color scheme
PRIMARY_COLOR = "#3498db"  # Blue
SECONDARY_COLOR = "#e6f7ff"  # Light blue
ACCENT_COLOR = "#2ecc71"  # Green
WARNING_COLOR = "#e74c3c"  # Red
TEXT_COLOR = "#2c3e50"  # Dark blue/grey
BUTTON_TEXT_COLOR = "white"
SIDEBAR_COLOR = "#2c3e50"  # Dark blue/grey for the sidebar

# Custom style
style = ttk.Style()
style.configure("TEntry", padding=5)
style.configure("TButton", padding=5)
style.configure("Treeview", rowheight=25)
style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

# ----------------- Navigation Sidebar ----------------- #
sidebar = tk.Frame(root, bg=SIDEBAR_COLOR, width=180)
sidebar.pack(side=tk.LEFT, fill=tk.Y)
sidebar.pack_propagate(False)  # Prevents the sidebar from shrinking

# Logo or system title
tk.Label(sidebar, text="CLINIC\nMANAGEMENT", bg=SIDEBAR_COLOR, fg="white", 
         font=("Arial", 12, "bold"), pady=20).pack(fill=tk.X)

# Separator
ttk.Separator(sidebar).pack(fill=tk.X, padx=10)

# Function to create sidebar buttons
def create_sidebar_button(text, command=None, color=PRIMARY_COLOR):
    btn = tk.Button(sidebar, text=text, bg=color, fg=BUTTON_TEXT_COLOR, 
                   padx=5, pady=10, bd=0, width=15, command=command,
                   font=("Arial", 10, "bold"))
    btn.pack(pady=5, padx=10)
    return btn

# Content frame to hold all other widgets
content_frame = tk.Frame(root, bg=SECONDARY_COLOR)
content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Button function definitions
def save_record():
    try:
        db = DatabaseHelper()
        patient_name = entry_name.get()
        
        # Check if patient already exists
        existing_patient = db.get_patient_by_name(patient_name)
        patient_id = None
        
        if existing_patient:
            response = messagebox.askyesno(
                "Patient Exists", 
                f"Patient '{patient_name}' already exists. Do you want to add a new checkup record?",
                icon='warning'
            )
            if response:
                patient_id = existing_patient[0]  # Get existing patient's ID
            else:
                return
        else:
            # Save new patient data
            patient_data = (
                patient_name,
                entry_address.get(),
                selected_date.get(),  # Using selected_date instead of birthdate_cal
                entry_age.get(),  # not saved to DB
                entry_phone.get(),
                status_var.get(),
                "",  # occupation
                "",  # referred
                gender_var.get(),
                entry_phone.get()  # phone
            )
            patient_id = db.add_patient(patient_data)
        
        # Save checkup data
        current_date = datetime.now().strftime('%Y-%m-%d')
        checkup_data = (
            patient_id,
            current_date,  # dateOfVisit
            "",          # lab_ids
            text_findings.get("1.0", tk.END),
            current_date,  # last_checkup_date
            entry_bp.get()  # blood_pressure
        )
        
        checkup_id = db.add_checkup(checkup_data)
        
        # Save prescriptions
        for item in tree_med.get_children():
            values = tree_med.item(item)['values']
            prescription_data = (
                patient_id,
                values[1],  # generic
                values[0],  # brand
                values[4],  # quantity
                values[3],  # administration/frequency
                current_date  # last_checkup_date
            )
            db.add_prescription(prescription_data)
            
        messagebox.showinfo("Success", "Record saved successfully!")
        clear_form()
        
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def update_record():
    messagebox.showinfo("Update", "Record updated successfully!")

def clear_form():
    # Clear all entry fields and text widgets
    entry_name.delete(0, tk.END)
    entry_address.delete(0, tk.END)
    entry_age.delete(0, tk.END)
    entry_phone.delete(0, tk.END)
    entry_bp.delete(0, tk.END)
    text_complaints.delete("1.0", tk.END)
    text_findings.delete("1.0", tk.END)
    text_remarks.delete("1.0", tk.END)
    # Clear medications treeview
    for item in tree_med.get_children():
        tree_med.delete(item)
    # Reset comboboxes and radiobuttons
    status_var.set("")
    gender_var.set("")
    frequency_var.set("")
    selected_date.set(datetime.now().strftime('%Y-%m-%d'))
    messagebox.showinfo("Clear", "Form cleared successfully!")

def delete_record():
    response = messagebox.askyesno("Delete", "Are you sure you want to delete this record?")
    if response:
        messagebox.showinfo("Delete", "Record deleted successfully!")

def open_med_cert():
    messagebox.showinfo("Medical Certificate", "Medical Certificate module will open here!")

def open_lab_charts():
    messagebox.showinfo("Lab/Charts", "Lab and Charts module will open here!")

# Sidebar buttons
btn_save = create_sidebar_button("Save Record", save_record, ACCENT_COLOR)
btn_update = create_sidebar_button("Update Record", update_record, PRIMARY_COLOR)
btn_clear = create_sidebar_button("Clear Form", clear_form, PRIMARY_COLOR)
btn_delete = create_sidebar_button("Delete Record", delete_record, WARNING_COLOR)
ttk.Separator(sidebar).pack(fill=tk.X, padx=10, pady=5)
btn_med_cert = create_sidebar_button("Medical Certificate", open_med_cert, PRIMARY_COLOR)
btn_lab = create_sidebar_button("Lab/Charts", open_lab_charts, PRIMARY_COLOR)

# Exit button at the bottom of sidebar
tk.Frame(sidebar, bg=SIDEBAR_COLOR, height=100).pack(fill=tk.X, expand=True)
btn_exit = create_sidebar_button("EXIT", root.quit, WARNING_COLOR)

# ----------------- Patient Information Section ----------------- #
frame_patient = tk.LabelFrame(content_frame, text="PATIENT INFORMATION", bg=SECONDARY_COLOR, fg=TEXT_COLOR, font=("Arial", 12, "bold"))
frame_patient.place(x=10, y=10, width=650, height=320)

# Left column of patient info
tk.Label(frame_patient, text="Name:", bg=SECONDARY_COLOR, fg=TEXT_COLOR).grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_name = AutocompleteCombobox(frame_patient, width=37)
entry_name.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_patient, text="Address:", bg=SECONDARY_COLOR, fg=TEXT_COLOR).grid(row=1, column=0, padx=5, pady=5, sticky="w")
entry_address = ttk.Entry(frame_patient, width=40)
entry_address.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame_patient, text="Birthdate:", bg=SECONDARY_COLOR, fg=TEXT_COLOR).grid(row=2, column=0, padx=5, pady=5, sticky="w")
birthdate_frame = tk.Frame(frame_patient, bg=SECONDARY_COLOR)
birthdate_frame.grid(row=2, column=1, padx=5, pady=5, sticky="w")

selected_date = tk.StringVar()
birthdate_entry = ttk.Entry(birthdate_frame, width=15, textvariable=selected_date)
birthdate_entry.pack(side=tk.LEFT, padx=(0,5))

def show_calendar():
    cal_window = tk.Toplevel(root)
    cal_window.title("Select Birthdate")
    cal_window.geometry("300x250")
    
    def set_date():
        date = cal.selection_get()
        selected_date.set(date.strftime('%Y-%m-%d'))
        update_age()
        cal_window.destroy()
    
    cal = Calendar(cal_window, 
                  selectmode='day',
                  date_pattern='y-mm-dd',
                  background=PRIMARY_COLOR,
                  foreground=BUTTON_TEXT_COLOR,
                  headersbackground=PRIMARY_COLOR,
                  headersforeground=BUTTON_TEXT_COLOR)
    cal.pack(padx=10, pady=10)
    
    ttk.Button(cal_window, text="Select", command=set_date).pack(pady=5)

cal_button = ttk.Button(birthdate_frame, text="📅", width=3, command=show_calendar)
cal_button.pack(side=tk.LEFT)

tk.Label(frame_patient, text="Age:", bg=SECONDARY_COLOR, fg=TEXT_COLOR).grid(row=2, column=1, padx=(200, 5), pady=5, sticky="w")
entry_age = ttk.Entry(frame_patient, width=10)
entry_age.grid(row=2, column=1, padx=(240, 5), pady=5, sticky="w")

tk.Label(frame_patient, text="Phone:", bg=SECONDARY_COLOR, fg=TEXT_COLOR).grid(row=3, column=0, padx=5, pady=5, sticky="w")
entry_phone = ttk.Entry(frame_patient, width=20)
entry_phone.grid(row=3, column=1, padx=5, pady=5, sticky="w")

# Right column of patient info
tk.Label(frame_patient, text="Civil Status:", bg=SECONDARY_COLOR, fg=TEXT_COLOR).grid(row=0, column=2, padx=5, pady=5, sticky="w")
status_var = tk.StringVar()
status_options = ["Single", "Married", "Divorced", "Widowed"]
status_dropdown = ttk.Combobox(frame_patient, textvariable=status_var, values=status_options, width=15)
status_dropdown.grid(row=0, column=3, padx=5, pady=5, sticky="w")

tk.Label(frame_patient, text="Gender:", bg=SECONDARY_COLOR, fg=TEXT_COLOR).grid(row=1, column=2, padx=5, pady=5, sticky="w")
gender_var = tk.StringVar()
ttk.Radiobutton(frame_patient, text="Male", variable=gender_var, value="Male").grid(row=1, column=3, sticky="w")
ttk.Radiobutton(frame_patient, text="Female", variable=gender_var, value="Female").grid(row=1, column=3, padx=(70, 0), sticky="w")

tk.Label(frame_patient, text="Blood Pressure:", bg=SECONDARY_COLOR, fg=TEXT_COLOR).grid(row=2, column=2, padx=5, pady=5, sticky="w")
entry_bp = ttk.Entry(frame_patient, width=15)
entry_bp.grid(row=2, column=3, padx=5, pady=5, sticky="w")

# Medical information section
tk.Label(frame_patient, text="Complaints:", bg=SECONDARY_COLOR, fg=TEXT_COLOR).grid(row=4, column=0, padx=5, pady=5, sticky="nw")
text_complaints = tk.Text(frame_patient, width=40, height=3)
text_complaints.grid(row=4, column=1, padx=5, pady=5, sticky="w")

tk.Label(frame_patient, text="Findings:", bg=SECONDARY_COLOR, fg=TEXT_COLOR).grid(row=5, column=0, padx=5, pady=5, sticky="nw")
text_findings = tk.Text(frame_patient, width=40, height=3)
text_findings.grid(row=5, column=1, padx=5, pady=5, sticky="w")

# ----------------- Queue System ----------------- #
frame_queue = tk.LabelFrame(content_frame, text="TODAY'S QUEUE", bg=SECONDARY_COLOR, fg=TEXT_COLOR, font=("Arial", 12, "bold"))
frame_queue.place(x=670, y=10, width=320, height=320)

# Current date display
current_date = datetime.now()
date_string = current_date.strftime("%A, %B %d, %Y")
tk.Label(frame_queue, text=date_string, bg=SECONDARY_COLOR, fg=TEXT_COLOR, font=("Arial", 10, "bold")).pack(pady=5)

tree_queue = ttk.Treeview(frame_queue, columns=("No", "Name", "Time"), show="headings", height=8)
tree_queue.heading("No", text="#")
tree_queue.heading("Name", text="Patient Name")
tree_queue.heading("Time", text="Time")
tree_queue.column("No", width=30)
tree_queue.column("Name", width=150)
tree_queue.column("Time", width=80)
tree_queue.pack(padx=5, pady=5)

# Add scrollbar to queue
scrollbar = ttk.Scrollbar(frame_queue, orient="vertical", command=tree_queue.yview)
tree_queue.configure(yscroll=scrollbar.set)
scrollbar.place(relx=0.97, rely=0.28, relheight=0.58)

queue_frame = tk.Frame(frame_queue, bg=SECONDARY_COLOR)
queue_frame.pack(pady=5)

# Queue counter
queue_counter = 0

def add_to_queue():
    global queue_counter
    name = entry_name.get()
    if name:
        queue_counter += 1
        current_time = datetime.now().strftime("%H:%M")
        tree_queue.insert("", "end", values=(queue_counter, name, current_time))
        # Save to Queue table using DatabaseHelper
        try:
            db = DatabaseHelper()
            db.add_to_queue((queue_counter, name, current_time))
        except Exception as e:
            messagebox.showerror("Error", f"Could not save to queue: {str(e)}")
    else:
        messagebox.showwarning("Input Error", "Enter patient name!")

def remove_from_queue():
    selected_item = tree_queue.selection()
    if selected_item:
        tree_queue.delete(selected_item)
    else:
        messagebox.showwarning("Selection Error", "Select a patient to remove from queue!")

btn_add_queue = tk.Button(queue_frame, text="Add to Queue", bg=ACCENT_COLOR, fg=BUTTON_TEXT_COLOR, padx=10, pady=5, command=add_to_queue)
btn_add_queue.pack(side=tk.LEFT, padx=5)

btn_remove_queue = tk.Button(queue_frame, text="Unqueue", bg=WARNING_COLOR, fg=BUTTON_TEXT_COLOR, padx=10, pady=5, command=remove_from_queue)
btn_remove_queue.pack(side=tk.LEFT, padx=5)

# ----------------- Remarks Section ----------------- #
frame_remarks = tk.LabelFrame(content_frame, text="REMARKS & NOTES", bg=SECONDARY_COLOR, fg=TEXT_COLOR, font=("Arial", 12, "bold"))
frame_remarks.place(x=10, y=340, width=485, height=280)

text_remarks = tk.Text(frame_remarks, width=55, height=14)
text_remarks.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Add scrollbar to remarks
remarks_scrollbar = ttk.Scrollbar(frame_remarks, orient="vertical", command=text_remarks.yview)
text_remarks.configure(yscroll=remarks_scrollbar.set)
remarks_scrollbar.place(relx=0.97, rely=0.05, relheight=0.9)

# ----------------- Prescription Section ----------------- #
frame_med = tk.LabelFrame(content_frame, text="PRESCRIPTION/MEDICATION", bg=SECONDARY_COLOR, fg=TEXT_COLOR, font=("Arial", 12, "bold"))
frame_med.place(x=505, y=340, width=485, height=280)

tree_med = ttk.Treeview(frame_med, columns=("Brand", "Generic", "Dosage", "Frequency", "Quantity"), show="headings", height=6)
tree_med.heading("Brand", text="Brand Name")
tree_med.heading("Generic", text="Generic Name")
tree_med.heading("Dosage", text="Dosage")
tree_med.heading("Frequency", text="Frequency")
tree_med.heading("Quantity", text="Quantity")
tree_med.column("Brand", width=90)
tree_med.column("Generic", width=90)
tree_med.column("Dosage", width=70)
tree_med.column("Frequency", width=90)
tree_med.column("Quantity", width=60)
tree_med.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

# Add scrollbar to prescription
med_scrollbar = ttk.Scrollbar(frame_med, orient="vertical", command=tree_med.yview)
tree_med.configure(yscroll=med_scrollbar.set)
med_scrollbar.place(relx=0.97, rely=0.05, relheight=0.5)

# Medication input frame
med_input_frame = tk.Frame(frame_med, bg=SECONDARY_COLOR)
med_input_frame.pack(padx=5, pady=5, fill=tk.X)

# First row of medication inputs
input_row1 = tk.Frame(med_input_frame, bg=SECONDARY_COLOR)
input_row1.pack(fill=tk.X, pady=2)

tk.Label(input_row1, text="Brand:", bg=SECONDARY_COLOR, fg=TEXT_COLOR).pack(side=tk.LEFT, padx=5)
entry_brand = ttk.Entry(input_row1, width=15)
entry_brand.pack(side=tk.LEFT, padx=2)

tk.Label(input_row1, text="Generic:", bg=SECONDARY_COLOR, fg=TEXT_COLOR).pack(side=tk.LEFT, padx=5)
entry_generic = ttk.Entry(input_row1, width=15)
entry_generic.pack(side=tk.LEFT, padx=2)

# Second row of medication inputs
input_row2 = tk.Frame(med_input_frame, bg=SECONDARY_COLOR)
input_row2.pack(fill=tk.X, pady=2)

tk.Label(input_row2, text="Dosage:", bg=SECONDARY_COLOR, fg=TEXT_COLOR).pack(side=tk.LEFT, padx=5)
entry_dosage = ttk.Entry(input_row2, width=10)
entry_dosage.pack(side=tk.LEFT, padx=2)

tk.Label(input_row2, text="Qty:", bg=SECONDARY_COLOR, fg=TEXT_COLOR).pack(side=tk.LEFT, padx=5)
entry_quantity = ttk.Entry(input_row2, width=5)
entry_quantity.pack(side=tk.LEFT, padx=2)

tk.Label(input_row2, text="Freq:", bg=SECONDARY_COLOR, fg=TEXT_COLOR).pack(side=tk.LEFT, padx=5)
frequency_var = tk.StringVar()
freq_options = ["Once daily", "Twice daily", "Three times daily", "Every 4 hours", "Every 6 hours", "As needed"]
freq_dropdown = ttk.Combobox(input_row2, textvariable=frequency_var, values=freq_options, width=12)
freq_dropdown.pack(side=tk.LEFT, padx=2)

# Button row for medication
button_row = tk.Frame(med_input_frame, bg=SECONDARY_COLOR)
button_row.pack(fill=tk.X, pady=5)

def add_medication():
    med_selector = MedicineSelector(root)
    root.wait_window(med_selector)
    
    if med_selector.selected_medicine:
        med_id, brand, generic, med_type = med_selector.selected_medicine
        dosage = entry_dosage.get()
        frequency = frequency_var.get()
        quantity = entry_quantity.get()
        
        if dosage and frequency and quantity:
            tree_med.insert("", "end", values=(brand, generic, dosage, frequency, quantity))
            entry_dosage.delete(0, tk.END)
            entry_quantity.delete(0, tk.END)
            frequency_var.set("")
        else:
            messagebox.showwarning("Input Error", "Please fill all fields!")

def remove_medication():
    selected_item = tree_med.selection()
    if selected_item:
        tree_med.delete(selected_item)
    else:
        messagebox.showwarning("Selection Error", "Select a medication to remove!")

btn_add_med = tk.Button(button_row, text="Add Medication", bg=ACCENT_COLOR, fg=BUTTON_TEXT_COLOR, padx=5, pady=2, command=add_medication)
btn_add_med.pack(side=tk.LEFT, padx=5)

btn_remove_med = tk.Button(button_row, text="Remove", bg=WARNING_COLOR, fg=BUTTON_TEXT_COLOR, padx=5, pady=2, command=remove_medication)
btn_remove_med.pack(side=tk.LEFT, padx=5)

# Let's update the add_to_queue function to calculate age from birthdate
def calculate_age(birth_date_str):
    try:
        birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return str(age)
    except:
        return ""

# Add a function to update age when birthdate changes
def update_age(event=None):
    try:
        birth_date = datetime.strptime(selected_date.get(), '%Y-%m-%d')
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        entry_age.delete(0, tk.END)
        entry_age.insert(0, str(age))
    except:
        pass

# Add this after the entry definitions
def load_patient_names():
    db = DatabaseHelper()
    patients = db.get_patients()
    patient_names = [patient[1] for patient in patients]
    entry_name['completevalues'] = patient_names
    return {name: id for id, name in patients}

patient_dict = load_patient_names()

def on_name_select(event=None):
    selected_name = entry_name.get()
    if (selected_name in patient_dict):
        db = DatabaseHelper()
        patient = db.get_patient_details(patient_dict[selected_name])
        if patient:
            # Clear existing fields
            entry_address.delete(0, tk.END)
            entry_phone.delete(0, tk.END)
            
            # Fill in patient details from database
            entry_address.insert(0, patient[2])  # address
            # Convert string date to datetime before setting
            date_obj = datetime.strptime(patient[3], '%Y-%m-%d')
            selected_date.set(date_obj.strftime('%Y-%m-%d'))
            entry_phone.insert(0, patient[9])  # phone
            status_var.set(patient[5])  # civil_status 
            gender_var.set(patient[8])  # gender
            update_age()

entry_name.bind('<<ComboboxSelected>>', on_name_select)

# Modify the queue system to allow editing
def edit_queue_item(event=None):
    selected_item = tree_queue.selection()
    if selected_item:
        # Get the patient name from queue
        values = tree_queue.item(selected_item)['values']
        patient_name = values[1]
        
        # Clear current form
        clear_form()
        
        # Set the patient name and trigger the selection event
        entry_name.set(patient_name)
        on_name_select()  # This will load the patient details

# Bind double click on queue
tree_queue.bind('<Double-1>', edit_queue_item)

# Add this function near other birthdate-related functions
def on_date_input(event=None):
    try:
        date_str = selected_date.get()
        # Only process if there's actual input
        if date_str and date_str != "YYYY-MM-DD":
            # Try to parse the date
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            # If successful, update age
            today = date.today()
            age = today.year - date_obj.year - ((today.month, today.day) < (date_obj.month, date_obj.day))
            entry_age.delete(0, tk.END)
            entry_age.insert(0, str(age))
            birthdate_entry.config(foreground="black")
    except ValueError:
        # If date is invalid, show in red but don't update age
        birthdate_entry.config(foreground="red")
        
# Near where birthdate_entry is created, add these bindings
birthdate_entry.bind("<KeyRelease>", on_date_input)
birthdate_entry.bind("<FocusOut>", on_date_input)

# Add placeholder text and handlers
birthdate_entry.insert(0, "YYYY-MM-DD")
birthdate_entry.config(foreground="gray")

def on_entry_focus_in(event):
    if birthdate_entry.get() == "YYYY-MM-DD":
        birthdate_entry.delete(0, tk.END)
        birthdate_entry.config(foreground="black")

def on_entry_focus_out(event):
    if not birthdate_entry.get():
        birthdate_entry.insert(0, "YYYY-MM-DD")
        birthdate_entry.config(foreground="gray")
    else:
        on_date_input(event)

birthdate_entry.bind("<FocusIn>", on_entry_focus_in)
birthdate_entry.bind("<FocusOut>", on_entry_focus_out)

root.mainloop()
