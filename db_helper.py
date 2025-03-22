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
                patient_data[5],  # civil_status
                "",              # occupation
                "",              # referred
                patient_data[6],  # gender
                patient_data[4]   # phone
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
            checkup_data[3],  # findings
            "",              # lab_ids
            checkup_data[1],  # dateOfVisit
            checkup_data[1],  # last_checkup_date same as visit date
            ""               # blood_pressure
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
