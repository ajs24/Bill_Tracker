import sqlite3

# Establishing a connection to the database (creates a new database if it doesn't exist)
conn = sqlite3.connect("bill_tracker.db")
cursor = conn.cursor()

def create_table():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            amount REAL,
            due_date TEXT,
            is_paid INTEGER DEFAULT 0
        )
    """)
    conn.commit()

def add_bill(company, amount, due_date):
    cursor.execute("""
        INSERT INTO bills (company, amount, due_date) VALUES (?, ?, ?)
    """, (company, amount, due_date))
    conn.commit()

def view_bills():
    cursor.execute("""
        SELECT * FROM bills
    """)
    return cursor.fetchall()

def mark_as_paid(bill_id):
    cursor.execute("""
        UPDATE bills SET is_paid = 1 WHERE id = ?
    """, (bill_id,))
    conn.commit()

def mark_as_unpaid(bill_id):
    cursor.execute("""
        UPDATE bills SET is_paid = 0 WHERE id = ?
    """, (bill_id,))
    conn.commit()

def remove_bill(bill_id):
    cursor.execute("""
        DELETE FROM bills WHERE id = ?
    """, (bill_id,))
    conn.commit()

    # Reorder the IDs after deletion
    cursor.execute("""
        UPDATE bills SET id = id - 1 WHERE id > ?
    """, (bill_id,))
    conn.commit()

def calculate_total_owed():
    cursor.execute("""
        SELECT SUM(amount) FROM bills WHERE is_paid = 0
    """)
    total_owed = cursor.fetchone()[0]
    return total_owed if total_owed else 0.0

def view_unpaid_bills():
    cursor.execute("""
        SELECT * FROM bills WHERE is_paid = 0
    """)
    unpaid_bills = cursor.fetchall()

    # Calculate the total owed
    total_owed = calculate_total_owed()

    return unpaid_bills, total_owed

def update_due_date(bill_id, due_date):
    cursor.execute("""
        UPDATE bills SET due_date = ?, is_paid = 0 WHERE id = ?
    """, (due_date, bill_id))
    conn.commit()

def main():
    while True:
        print("\nWhat would you like to do?")
        print("1. Add a bill")
        print("2. View bills")
        print("3. Mark a bill as paid")
        print("4. Mark bill as unpaid")
        print("5. View unpaid bills")
        print("6. Remove a bill")
        print("7. Update due date")
        print("8. Exit")

        choice = input("Enter your choice: ")
        print()

        if choice == "1":
            company = input("Enter the company name: ")
            amount = float(input("Enter the bill amount: "))
            due_date = input("Enter the due date (YYYY-MM-DD): ")
            add_bill(company, amount, due_date)
        elif choice == "2":
            bills = view_bills()
            for bill in bills:
                print(f"ID: {bill[0]}, Company: {bill[1]}, Amount: ${bill[2]}, Due Date: {bill[3]}, Paid: {'Yes' if bill[4] else 'No'}")
        elif choice == "3":
            bill_id = int(input("Enter the ID of the bill to mark as paid: "))
            mark_as_paid(bill_id)
        elif choice == "4":
            bill_id = int(input("Enter the ID of the bill to mark as unpaid: "))
            mark_as_unpaid(bill_id)
        elif choice == "5":
            unpaid_bills, total_owed = view_unpaid_bills()
            for bill in unpaid_bills:
                print(f"ID: {bill[0]}, Company: {bill[1]}, Amount: ${bill[2]}, Due Date: {bill[3]}")
            print(f"\033[4mTotal Amount Owed: ${total_owed:.2f}\033[0m")
        elif choice == "6":
            bill_id = int(input("Enter the ID of the bill to remove: "))
            remove_bill(bill_id)
        elif choice == "7":
            bill_id = int(input("Enter the ID of the bill to update the due date: "))
            due_date = input("Enter the due date (YYYY-MM-DD): ")
            update_due_date(bill_id, due_date)

        elif choice == "8":
            print("Exiting the bill tracker.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    create_table()
    main()

# Close the connection to the database when the program is finished
conn.close()
