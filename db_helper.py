import sqlite3
from datetime import datetime

class DatabaseHelper:
    def __init__(self, db_path='Login.db'):
        self.db_path = db_path

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def get_medicines(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Check if the quantity and administration columns exist
            cursor.execute("PRAGMA table_info(medicine)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            # If columns don't exist, alter the table to add them
            if 'quantity' not in column_names:
                cursor.execute("ALTER TABLE medicine ADD COLUMN quantity TEXT DEFAULT ''")
            if 'administration' not in column_names:
                cursor.execute("ALTER TABLE medicine ADD COLUMN administration TEXT DEFAULT ''")
            
            # Get all medicine data including new fields
            cursor.execute("SELECT id, brand, generic, quantity, administration FROM medicine")
            medicines = cursor.fetchall()
            conn.commit()
            return medicines
        except sqlite3.Error as e:
            print(f"Database error in get_medicines: {e}")
            return []
        finally:
            conn.close()

    def get_labs(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Labs")
        labs = cursor.fetchall()
        conn.close()
        return labs

    def add_patient(self, patient_data):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO Patients (name, address, birthdate, cell, civil_status, 
                occupation, referred, gender, phone) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                patient_data[0],  # name
                patient_data[1],  # address
                patient_data[2],  # birthdate
                "",              # cell
                patient_data[4],  # civil_status (was incorrectly using index 5)
                "",              # occupation
                "",              # referred
                patient_data[5],  # gender (was incorrectly using index 6 which doesn't exist)
                patient_data[3]   # phone (was incorrectly using index 4)
            ))
            patient_id = cursor.lastrowid
            conn.commit()
            return patient_id
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def add_checkup(self, checkup_data):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO Checkups (patient_id, findings, lab_ids, dateOfVisit, 
                last_checkup_date)
                VALUES (?, ?, ?, ?, ?)
            """, (
                checkup_data[0],  # patient_id
                checkup_data[1],  # findings (from remarks)
                checkup_data[2],  # lab_ids
                checkup_data[3],  # dateOfVisit
                checkup_data[4]   # last_checkup_date same as visit date
            ))
            checkup_id = cursor.lastrowid
            conn.commit()
            return checkup_id
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def add_prescription(self, prescription_data):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Prescriptions (patient_id, generic, brand, quantity, 
            administration, last_checkup_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, prescription_data)
        conn.commit()
        conn.close()

    def get_patient_history(self, patient_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.*, p.* FROM Checkups c
            JOIN Prescriptions p ON c.id = p.checkup_id
            WHERE c.patient_id = ?
        """, (patient_id,))
        history = cursor.fetchall()
        conn.close()
        return history

    def get_patients(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM Patients ORDER BY name")
        patients = cursor.fetchall()
        conn.close()
        return patients

    def get_patient_details(self, patient_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM Patients 
            WHERE id = ?
        """, (patient_id,))
        patient = cursor.fetchone()
        conn.close()
        return patient

    def add_to_queue(self, queue_data):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Queue (Pname) VALUES (?)", (queue_data[1],))
        conn.commit()
        conn.close()

    def get_patient_by_name(self, name):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM Patients 
            WHERE name = ?
        """, (name,))
        patient = cursor.fetchone()
        conn.close()
        return patient

    def add_medicine(self, medicine_data):
        """Add a new medicine to the database with quantity and administration"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Check if the medicine_data has 4 elements (brand, generic, quantity, administration)
            if len(medicine_data) >= 4:
                cursor.execute("""
                    INSERT INTO medicine (brand, generic, quantity, administration)
                    VALUES (?, ?, ?, ?)
                """, medicine_data[:4])  # Use the first four elements
            else:
                # Backward compatibility if only brand and generic are provided
                cursor.execute("""
                    INSERT INTO medicine (brand, generic)
                    VALUES (?, ?)
                """, medicine_data[:2])
            
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def update_medicine(self, medicine_data):
        """Update an existing medicine in the database including quantity and administration"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Check if medicine_data has all fields (generic, quantity, administration, id)
            if len(medicine_data) >= 4:
                cursor.execute("""
                    UPDATE medicine
                    SET generic = ?, quantity = ?, administration = ?
                    WHERE id = ?
                """, medicine_data)
            else:
                # Backward compatibility if only generic and id are provided
                cursor.execute("""
                    UPDATE medicine
                    SET generic = ?
                    WHERE id = ?
                """, medicine_data)
            
            conn.commit()
            return cursor.rowcount
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def delete_medicine(self, medicine_id):
        """Delete a medicine from the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                DELETE FROM medicine
                WHERE id = ?
            """, (medicine_id,))
            conn.commit()
            return cursor.rowcount
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def delete_patient(self, patient_id):
        """Delete a patient and all associated records from the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Start a transaction
            conn.execute("BEGIN TRANSACTION")
            
            # Delete prescriptions for the patient
            cursor.execute("""
                DELETE FROM Prescriptions 
                WHERE patient_id = ?
            """, (patient_id,))
            
            # Delete checkups for the patient
            cursor.execute("""
                DELETE FROM Checkups 
                WHERE patient_id = ?
            """, (patient_id,))
            
            # Delete the patient record
            cursor.execute("""
                DELETE FROM Patients 
                WHERE id = ?
            """, (patient_id,))
            
            # Commit the transaction
            conn.commit()
            return True
        except sqlite3.Error as e:
            # If there's an error, roll back the transaction
            conn.rollback()
            print(f"Database error during deletion: {e}")
            raise
        finally:
            conn.close()

    def get_patient_checkups(self, patient_id):
        """Get all checkups for a specific patient ordered by date"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id, findings, lab_ids, dateOfVisit, last_checkup_date, blood_pressure 
                FROM Checkups 
                WHERE patient_id = ? 
                ORDER BY dateOfVisit DESC
            """, (patient_id,))
            checkups = cursor.fetchall()
            return checkups
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
        finally:
            conn.close()

    def get_prescriptions_for_checkup(self, patient_id, checkup_date):
        """Get prescriptions for a specific checkup date"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Modified query to get only prescriptions for specific date
            cursor.execute("""
                SELECT brand, generic, quantity, administration 
                FROM Prescriptions 
                WHERE patient_id = ? 
                AND DATE(last_checkup_date) = DATE(?)
            """, (patient_id, checkup_date))
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
        finally:
            conn.close()

    def get_checkup_by_date(self, patient_id, checkup_date):
        """Get a checkup record for a specific patient and date"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id, findings, lab_ids, dateOfVisit, last_checkup_date, blood_pressure
                FROM Checkups 
                WHERE patient_id = ? AND DATE(last_checkup_date) = DATE(?)
            """, (patient_id, checkup_date))
            checkup = cursor.fetchone()
            return checkup
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            conn.close()

    def update_checkup(self, checkup_data):
        """Update an existing checkup record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE Checkups 
                SET findings = ?, lab_ids = ?, blood_pressure = ?
                WHERE id = ?
            """, (
                checkup_data[0],  # findings
                checkup_data[1],  # lab_ids
                checkup_data[2],  # blood_pressure
                checkup_data[3],  # checkup_id
            ))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def delete_prescriptions_for_checkup(self, patient_id, checkup_date):
        """Delete all prescriptions for a specific checkup date"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                DELETE FROM Prescriptions 
                WHERE patient_id = ? AND DATE(last_checkup_date) = DATE(?)
            """, (patient_id, checkup_date))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def save_patient_lab_image(self, patient_id, file_path, checkup_id=None):
        """Save a lab image path associated with a patient"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Check if the LabImages table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='LabImages'")
            if not cursor.fetchone():
                # Create the table if it doesn't exist
                cursor.execute("""
                    CREATE TABLE LabImages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        patient_id INTEGER,
                        checkup_id INTEGER,
                        file_path TEXT,
                        upload_date TEXT,
                        FOREIGN KEY (patient_id) REFERENCES Patients(id),
                        FOREIGN KEY (checkup_id) REFERENCES Checkups(id)
                    )
                """)
                
            # Get current date
            current_date = datetime.now().strftime('%Y-%m-%d')
            
            # Insert the image record
            cursor.execute("""
                INSERT INTO LabImages (patient_id, checkup_id, file_path, upload_date)
                VALUES (?, ?, ?, ?)
            """, (patient_id, checkup_id, file_path, current_date))
            
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    def get_patient_lab_images(self, patient_id):
        """Get all lab images associated with a patient"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Check if the LabImages table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='LabImages'")
            if not cursor.fetchone():
                return []
                
            # Get all images for the patient
            cursor.execute("""
                SELECT file_path FROM LabImages
                WHERE patient_id = ?
                ORDER BY upload_date DESC
            """, (patient_id,))
            
            image_paths = [row[0] for row in cursor.fetchall()]
            return image_paths
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
        finally:
            conn.close()

    def get_checkup_lab_images(self, checkup_id):
        """Get lab images associated with a specific checkup"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Check if the LabImages table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='LabImages'")
            if not cursor.fetchone():
                return []
                
            # Get images for the checkup
            cursor.execute("""
                SELECT file_path FROM LabImages
                WHERE checkup_id = ?
                ORDER BY upload_date DESC
            """, (checkup_id,))
            
            image_paths = [row[0] for row in cursor.fetchall()]
            return image_paths
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
        finally:
            conn.close()

    def delete_patient_lab_image(self, patient_id, file_path):
        """Delete a lab image record from the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Check if the LabImages table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='LabImages'")
            if not cursor.fetchone():
                return False
                
            # Delete the image record
            cursor.execute("""
                DELETE FROM LabImages 
                WHERE patient_id = ? AND file_path = ?
            """, (patient_id, file_path))
            
            conn.commit()
            return cursor.rowcount > 0  # Return True if a record was deleted
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
