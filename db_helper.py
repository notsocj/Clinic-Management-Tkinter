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
        cursor.execute("SELECT * FROM medicine")
        medicines = cursor.fetchall()
        conn.close()
        return medicines

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
        cursor.execute("""
            INSERT INTO Checkups (patient_id, findings, lab_ids, dateOfVisit, 
            last_checkup_date, blood_pressure)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            checkup_data[0],  # patient_id
            checkup_data[1],  # findings (from remarks)
            checkup_data[2],  # lab_ids
            checkup_data[3],  # dateOfVisit
            checkup_data[4],  # last_checkup_date same as visit date
            checkup_data[5]   # blood_pressure - fixed to use the passed value
        ))
        checkup_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return checkup_id

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
        """Add a new medicine to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO medicine (brand, generic)
                VALUES (?, ?)
            """, medicine_data[:2])  # Only use the first two elements (brand, generic)
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def update_medicine(self, medicine_data):
        """Update an existing medicine in the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
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

    def get_prescriptions_for_checkup(self, checkup_id):
        """Get prescriptions associated with a specific checkup"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT brand, generic, quantity, administration 
                FROM Prescriptions 
                WHERE checkup_id = ?
            """, (checkup_id,))
            prescriptions = cursor.fetchall()
            return prescriptions
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
        finally:
            conn.close()
