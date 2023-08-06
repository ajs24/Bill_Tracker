import sqlite3
import datetime

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
    # Convert the user-input date to the desired format (YYYY-MM-DD)
    due_date_obj = datetime.datetime.strptime(due_date, "%Y-%m-%d").date()
    cursor.execute("""
        INSERT INTO bills (company, amount, due_date) VALUES (?, ?, ?)
    """, (company, amount, due_date_obj))
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
    #Modified so that unpaid bills only appear if they are owed within 30 days.

    # Step 1: Get the current date
    current_date = datetime.date.today()

    # Step 2: Calculate the date that is 30 days ahead of the current date
    thirty_days_ahead = current_date + datetime.timedelta(days=30)

    # Step 3: Fetch unpaid bills due within the next 30 days (inclusive)
    cursor.execute("""
        SELECT * FROM bills WHERE is_paid = 0 AND due_date <= ?
    """, (thirty_days_ahead,))
    unpaid_bills = cursor.fetchall()

    # Step 4: Calculate the total owed
    total_owed = calculate_total_owed()

    return unpaid_bills, total_owed

def update_due_date(bill_id, due_date):
    # Convert the user-input date to the desired format (YYYY-MM-DD)
    due_date_obj = datetime.datetime.strptime(due_date, "%Y-%m-%d").date()
    cursor.execute("""
        UPDATE bills SET due_date = ?, is_paid = 0 WHERE id = ?
    """, (due_date_obj, bill_id))
    conn.commit()

def main():
    while True:
        print("\nWhat would you like to do?\n")
        print("\033[33m1.\033[0m Add a bill")
        print("\033[33m2.\033[0m View bills")
        print("\033[33m3.\033[0m Mark a bill as paid")
        print("\033[33m4.\033[0m Mark bill as unpaid")
        print("\033[33m5.\033[0m Remove a bill")
        print("\033[33m6.\033[0m Update due date")
        print("\033[33m7.\033[0m Exit\n")

        choice = input("\033[47m\033[30mEnter your choice:\033[0m ")
        print()

        if choice == "1":
            company = input("Enter the company name: ")
            amount = float(input("Enter the bill amount: "))
            due_date = input("Enter the due date (YYYY-MM-DD): ")
            add_bill(company, amount, due_date)
        elif choice == "2":
            bills = view_bills()
            unpaid_bills, total_owed = view_unpaid_bills()
            sorted_bills = sorted(bills, key=lambda x: (not x[4], x[3]))  # Sort by not is_paid (False first) and then due_date (ascending)
            print("\033[1mID\033[0m             | \033[1mCompany\033[0m         | \033[1mAmount\033[0m        | \033[1mDue Date\033[0m       | \033[1mPaid Status\033[0m       |")
            print("---------------------------------------------------------------------------------------")
            for bill in sorted_bills:
                amount = f"\033[32m${bill[2]:.2f}\033[0m" if bill[4] else f"\033[31m${bill[2]:.2f}\033[0m"  # Green if paid, red if unpaid
                paid_status = "\033[32mYes\033[0m" if bill[4] else "\033[31mNo\033[0m"  # Green for "Yes", red for "No"
                print(f"{bill[0]:<15}| {bill[1]:<15} | {amount:<22} | {bill[3]:<15}| {paid_status:<15}            |")
            print("---------------------------------------------------------------------------------------")
            print(f"                            \033[4mTotal Amount Owed: ${total_owed:.2f}\033[0m")
        elif choice == "3":
            bill_id = int(input("Enter the ID of the bill to mark as paid: "))
            mark_as_paid(bill_id)
        elif choice == "4":
            bill_id = int(input("Enter the ID of the bill to mark as unpaid: "))
            mark_as_unpaid(bill_id)
        elif choice == "5":
            bill_id = int(input("Enter the ID of the bill to remove: "))
            remove_bill(bill_id)
        elif choice == "6":
            bill_id = int(input("Enter the ID of the bill to update the due date: "))
            due_date = input("Enter the due date (YYYY-MM-DD): ")
            update_due_date(bill_id, due_date)

        elif choice == "7":
            print("Exiting the bill tracker.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    create_table()
    main()

# Close the connection to the database when the program is finished
conn.close()
