# lab_charts.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog  # Add filedialog for import
from PIL import Image, ImageTk
import os
from db_helper import DatabaseHelper

class LabChartsWindow:
    def __init__(self, parent, patient_name, patient_id=None, new_files=None):
        self.window = tk.Toplevel(parent)
        self.window.title(f"Lab Results & Charts - {patient_name}")
        self.window.geometry("1000x700")
        self.window.configure(bg="#e6f7ff")
        
        self.parent = parent
        self.patient_name = patient_name
        self.patient_id = patient_id
        self.images = []  # Store tuples of (photo, file_path)
        self.db = DatabaseHelper()
        
        self.create_widgets()
        
        # Load existing or new files
        if not new_files and self.patient_id:
            existing_images = self.db.get_patient_lab_images(self.patient_id)
            if existing_images:
                self.add_new_files(existing_images)
        elif new_files:
            self.add_new_files(new_files)
    
    def create_widgets(self):
        self.main_frame = tk.Frame(self.window, bg="#e6f7ff")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        btn_frame = tk.Frame(self.main_frame, bg="#e6f7ff")
        btn_frame.pack(fill=tk.X, pady=10)
        
        # "Import More" button
        import_btn = tk.Button(btn_frame, text="Import More", 
                             command=self.import_more_images,
                             bg="#3498db", fg="white",
                             padx=20, pady=5,
                             font=("Arial", 10, "bold"))
        import_btn.pack(side=tk.LEFT, padx=5)
        
        # "Save to Checkup" button
        save_btn = tk.Button(btn_frame, text="Save to Checkup", 
                           command=self.save_to_checkup,
                           bg="#2ecc71", fg="white",
                           padx=20, pady=5,
                           font=("Arial", 10, "bold"))
        save_btn.pack(side=tk.LEFT, padx=5)
        
        # "Close" button
        close_btn = tk.Button(btn_frame, text="Close", 
                            command=self.window.destroy,
                            bg="#e74c3c", fg="white",
                            padx=20, pady=5,
                            font=("Arial", 10, "bold"))
        close_btn.pack(side=tk.RIGHT, padx=5)
    
    def import_more_images(self):
        """Handle importing additional images into the existing window"""
        file_types = [
            ('Image files', '*.png *.jpg *.jpeg *.gif *.bmp'),
            ('All files', '*.*')
        ]
        files = filedialog.askopenfilenames(
            title="Select Additional Images",
            filetypes=file_types
        )
        if files:
            self.add_new_files(files)
            messagebox.showinfo("Success", f"Added {len(files)} new image(s) to the lab charts.")
    
    def add_new_files(self, files):
        for file_path in files:
            try:
                if not os.path.exists(file_path):
                    messagebox.showwarning("Warning", f"File not found: {file_path}")
                    continue
                
                tab_frame = ttk.Frame(self.notebook)
                tab_name = os.path.basename(file_path)
                
                canvas = tk.Canvas(tab_frame, bg="white")
                canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                
                h_scroll = ttk.Scrollbar(tab_frame, orient=tk.HORIZONTAL, command=canvas.xview)
                v_scroll = ttk.Scrollbar(tab_frame, orient=tk.VERTICAL, command=canvas.yview)
                
                canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
                h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
                v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
                
                pil_image = Image.open(file_path)
                
                canvas_width = 800
                canvas_height = 600
                width_ratio = canvas_width / pil_image.width
                height_ratio = canvas_height / pil_image.height
                scale_factor = min(width_ratio, height_ratio)
                
                new_width = int(pil_image.width * scale_factor)
                new_height = int(pil_image.height * scale_factor)
                
                pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                photo = ImageTk.PhotoImage(pil_image)
                self.images.append((photo, file_path))
                
                canvas.create_image(0, 0, anchor="nw", image=photo)
                canvas.configure(scrollregion=(0, 0, new_width, new_height))
                
                self.notebook.add(tab_frame, text=tab_name)
                self.notebook.select(self.notebook.index(tk.END)-1)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image {file_path}: {str(e)}")
    
    def save_to_checkup(self):
        if not self.patient_id:
            messagebox.showerror("Error", "No patient selected.")
            return
        
        if not self.images:
            messagebox.showwarning("Warning", "No images to save.")
            return
        
        try:
            from datetime import datetime
            current_date = datetime.now().strftime('%Y-%m-%d')
            lab_ids = ",".join([path for _, path in self.images])
            
            checkup_data = (
                self.patient_id,
                "Lab results imported",
                lab_ids,
                current_date,
                current_date
            )
            checkup_id = self.db.add_checkup(checkup_data)
            
            messagebox.showinfo("Success", f"Lab images saved to checkup ID {checkup_id}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save to checkup: {str(e)}")