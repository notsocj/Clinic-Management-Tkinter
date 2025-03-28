# lab_charts.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import os
import shutil
from datetime import datetime
from db_helper import DatabaseHelper

class LabChartsWindow:
    def __init__(self, parent, patient_name, patient_id=None, new_files=None):
        self.window = tk.Toplevel(parent)
        self.window.title(f"Lab Results & Charts - {patient_name}")
        self.window.geometry("1000x700")
        self.window.configure(bg="#e6f7ff")
        
        # Store references
        self.parent = parent
        self.patient_name = patient_name
        self.patient_id = patient_id
        self.images = []  # Store tuples of (photo, file_path)
        self.db = DatabaseHelper()
        
        # Create a directory to store patient images if it doesn't exist
        self.image_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "patient_images")
        os.makedirs(self.image_dir, exist_ok=True)
        
        # Create UI
        self.create_widgets()
        
        # Load existing or new files
        if patient_id:
            # Load existing images from database
            self.load_patient_images()
            
        # If new files were provided, add them
        if new_files:
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
        
        # "Delete Image" button - ADD THIS NEW BUTTON
        delete_btn = tk.Button(btn_frame, text="Delete Image", 
                             command=self.delete_selected_image,
                             bg="#e74c3c", fg="white",
                             padx=20, pady=5,
                             font=("Arial", 10, "bold"))
        delete_btn.pack(side=tk.LEFT, padx=5)
        
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
    
    def load_patient_images(self):
        """Load existing patient images from the database"""
        if not self.patient_id:
            return
            
        image_paths = self.db.get_patient_lab_images(self.patient_id)
        if image_paths:
            valid_paths = []
            for path in image_paths:
                if os.path.exists(path):
                    valid_paths.append(path)
                else:
                    print(f"Warning: Image file not found: {path}")
            
            if valid_paths:
                self.add_new_files(valid_paths)
                print(f"Loaded {len(valid_paths)} existing images for patient {self.patient_name}")
    
    def add_new_files(self, files):
        for file_path in files:
            try:
                # Validate file exists
                if not os.path.exists(file_path):
                    messagebox.showwarning("File Not Found", f"Cannot find file: {file_path}")
                    continue
                
                # Create a new tab
                tab_frame = ttk.Frame(self.notebook)
                tab_name = os.path.basename(file_path)
                
                # ...existing image display code...
                
                canvas = tk.Canvas(tab_frame, bg="white")
                canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                
                h_scroll = ttk.Scrollbar(tab_frame, orient=tk.HORIZONTAL, command=canvas.xview)
                v_scroll = ttk.Scrollbar(tab_frame, orient=tk.VERTICAL, command=canvas.yview)
                
                canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
                h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
                v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
                
                # Process the image
                pil_image = Image.open(file_path)
                
                # Scale image
                canvas_width = 800
                canvas_height = 600
                width_ratio = canvas_width / pil_image.width
                height_ratio = canvas_height / pil_image.height
                scale_factor = min(width_ratio, height_ratio)
                
                new_width = int(pil_image.width * scale_factor)
                new_height = int(pil_image.height * scale_factor)
                
                pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Create PhotoImage and store
                photo = ImageTk.PhotoImage(pil_image)
                self.images.append((photo, file_path))
                
                # Add image to canvas
                canvas.create_image(0, 0, anchor="nw", image=photo)
                canvas.configure(scrollregion=(0, 0, new_width, new_height))
                
                # Add the tab
                self.notebook.add(tab_frame, text=tab_name)
                self.notebook.select(self.notebook.index(tk.END)-1)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image {file_path}: {str(e)}")
    
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
    
    def save_to_checkup(self):
        """Save the images to the patient's record and create a checkup entry"""
        if not self.patient_id:
            messagebox.showerror("Error", "No patient selected.")
            return
        
        if not self.images:
            messagebox.showwarning("Warning", "No images to save.")
            return
        
        try:
            # Create a patient-specific folder
            patient_folder = os.path.join(self.image_dir, f"patient_{self.patient_id}")
            os.makedirs(patient_folder, exist_ok=True)
            
            # Get list of existing images for this patient
            existing_images = self.db.get_patient_lab_images(self.patient_id)
            
            # Current date for the checkup
            current_date = datetime.now().strftime('%Y-%m-%d')
            saved_paths = []
            new_images_count = 0
            
            # First, check for each image if it's already saved for this patient
            for idx, (photo, original_path) in enumerate(self.images):
                # Check if this image is already in the patient's saved images
                if original_path in existing_images:
                    # Image already exists in database, use the existing path
                    saved_paths.append(original_path)
                    print(f"Image already exists in database: {original_path}")
                    continue
                    
                # Check if the file is already in patient folder but not in DB
                # by comparing file content (md5 hash would be ideal but simple basename check for now)
                base_filename = os.path.basename(original_path)
                duplicate_found = False
                
                # Check if a similar filename exists in patient folder
                for existing_path in existing_images:
                    if os.path.basename(existing_path).endswith(base_filename):
                        # Consider it a duplicate
                        saved_paths.append(existing_path)
                        duplicate_found = True
                        print(f"Similar image found: {existing_path}")
                        break
                
                if duplicate_found:
                    continue
                
                # Generate a unique filename
                filename = f"{current_date}_{idx}_{os.path.basename(original_path)}"
                new_path = os.path.join(patient_folder, filename)
                
                # Only copy if the file isn't already in the patient folder
                if original_path != new_path and not os.path.exists(new_path):
                    shutil.copy2(original_path, new_path)
                    new_images_count += 1
                
                saved_paths.append(new_path)
            
            # If no new images were copied, ask user if they want to continue
            if new_images_count == 0 and saved_paths:
                response = messagebox.askyesno(
                    "No New Images", 
                    "All images are already saved for this patient. Do you still want to create a new checkup entry?",
                    icon='question'
                )
                if not response:
                    return
            
            # Create a new checkup record
            checkup_data = (
                self.patient_id,
                "Lab results/images imported",  # findings
                "",  # lab_ids (will store in LabImages table instead)
                current_date,  # dateOfVisit
                current_date   # last_checkup_date
            )
            
            checkup_id = self.db.add_checkup(checkup_data)
            
            # Save image paths to database only if they're not already saved
            for path in saved_paths:
                # Check if this image path is already in the database
                if path not in existing_images:
                    self.db.save_patient_lab_image(self.patient_id, path, checkup_id)
            
            # Success message with details about new vs existing images
            if new_images_count > 0:
                success_message = f"Saved {new_images_count} new image(s) to patient record."
                if len(saved_paths) - new_images_count > 0:
                    success_message += f"\n{len(saved_paths) - new_images_count} image(s) were already saved."
            else:
                success_message = "No new images were saved, but checkup record was created."
                
            success_message += "\nThese images will appear when you view this patient's lab charts."
            messagebox.showinfo("Success", success_message)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save images: {str(e)}")
    
    def delete_selected_image(self):
        """Delete the currently selected image from the notebook and database"""
        if not self.notebook.tabs():
            messagebox.showinfo("Information", "No images to delete.")
            return
        
        # Get the currently selected tab index
        selected_tab_index = self.notebook.index(self.notebook.select())
        
        # Confirm deletion with the user
        response = messagebox.askyesno(
            "Confirm Deletion",
            "Are you sure you want to delete this image?\nThis cannot be undone.",
            icon='warning'
        )
        
        if not response:
            return
        
        try:
            # Get the image information
            if selected_tab_index < len(self.images):
                _, file_path = self.images[selected_tab_index]
                
                # If this is a saved patient image, remove from database
                if self.patient_id and file_path.startswith(self.image_dir):
                    # Delete from database if it's stored there
                    conn = self.db.get_connection()
                    cursor = conn.cursor()
                    
                    try:
                        # Check if LabImages table exists
                        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='LabImages'")
                        if cursor.fetchone():
                            cursor.execute("""
                                DELETE FROM LabImages 
                                WHERE patient_id = ? AND file_path = ?
                            """, (self.patient_id, file_path))
                            conn.commit()
                            
                            print(f"Deleted image record from database: {file_path}")
                            
                            # Optionally delete the actual file
                            try:
                                if os.path.exists(file_path) and file_path.startswith(self.image_dir):
                                    os.remove(file_path)
                                    print(f"Deleted image file: {file_path}")
                            except Exception as e:
                                print(f"Warning: Could not delete file {file_path}: {str(e)}")
                    except sqlite3.Error as e:
                        print(f"Database error during image deletion: {str(e)}")
                    finally:
                        conn.close()
                
                # Remove from our image list
                self.images.pop(selected_tab_index)
            
            # Remove the tab from the notebook
            self.notebook.forget(selected_tab_index)
            
            # If there are still tabs, select one
            if self.notebook.tabs():
                new_index = min(selected_tab_index, len(self.notebook.tabs()) - 1)
                self.notebook.select(new_index)
                
            messagebox.showinfo("Success", "Image deleted successfully.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete image: {str(e)}")