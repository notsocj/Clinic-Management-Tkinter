import sqlite3

def get_patients():
    conn = sqlite3.connect("Login.db")  # Connect to the database
    cursor = conn.cursor()

    # Execute SELECT statement
    cursor.execute("SELECT * FROM Patients")

    # Fetch all results
    patients = cursor.fetchall()

    # Close connection
    conn.close()

    # Print results
    for patient in patients:
        print(patient)

# Example usage
get_patients()
