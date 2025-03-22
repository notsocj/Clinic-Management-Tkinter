import sqlite3

def delete_patient(patient_name):
    conn = sqlite3.connect("Login.db")  
    cursor = conn.cursor()
    
    # Execute DELETE statement
    cursor.execute("DELETE FROM Patients WHERE name = ?", (patient_name,))
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print(f"Patient '{patient_name}' deleted successfully.")

# Example usage
delete_patient("")
