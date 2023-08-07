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

def update_due_date(bill_id, due_date):
    # Convert the user-input date to the desired format (YYYY-MM-DD)
    due_date_obj = datetime.datetime.strptime(due_date, "%Y-%m-%d").date()
    cursor.execute("""
        UPDATE bills SET due_date = ?, is_paid = 0 WHERE id = ?
    """, (due_date_obj, bill_id))
    conn.commit()

def update_company_name(bill_id, new_company_name):
    cursor.execute("""
        UPDATE bills SET company = ? WHERE id = ?
    """, (new_company_name, bill_id))
    conn.commit()

def update_amount_due(bill_id, new_amount_due):
    cursor.execute("""
        UPDATE bills SET amount = ? WHERE id = ?
    """, (new_amount_due, bill_id))
    conn.commit()

def main():
    while True:
        print("\nWhat would you like to do?\n")
        print("\033[33m1.\033[0m Add a bill")
        print("\033[33m2.\033[0m View bills")
        print("\033[33m3.\033[0m Modify a bill")
        print("\033[33m4.\033[0m Exit\n")

        choice = input("\033[47m\033[30mEnter your choice:\033[0m ")
        print()

        if choice == "1":
            company = input("Enter the company name: ")
            amount = float(input("Enter the bill amount: "))
            due_date = input("Enter the due date (YYYY-MM-DD): ")
            add_bill(company, amount, due_date)
        elif choice == "2":
            bills = view_bills()
            total_owed = calculate_total_owed()
            sorted_bills = sorted(bills, key=lambda x: (not x[4], x[3]))  # Sort by not is_paid (False first) and then due_date (ascending)
            print("---------------------------------------------------------------------------------------")
            print("| \033[1mID\033[0m           | \033[1mCompany\033[0m         | \033[1mAmount\033[0m        | \033[1mDue Date\033[0m       | \033[1mPaid Status\033[0m       |")
            print("---------------------------------------------------------------------------------------")
            for bill in sorted_bills:
                amount = f"\033[32m${bill[2]:.2f}\033[0m" if bill[4] else f"\033[31m${bill[2]:.2f}\033[0m"  # Green if paid, red if unpaid
                paid_status = "\033[32mYes\033[0m" if bill[4] else "\033[31mNo\033[0m"  # Green for "Yes", red for "No"
                due_date = bill[3]
                due_date_obj = datetime.datetime.strptime(due_date, "%Y-%m-%d").date()
                today = datetime.date.today()
                days_until_due = (due_date_obj - today).days
                if 0 <= days_until_due <= 30:  # If due date is within 30 days
                    due_date = "\033[33m" + due_date + "\033[0m"  # Yellow color for due date
                elif days_until_due > 30: # If due date is beyond 30 days
                    due_date = "\033[32m" + due_date + "\033[0m" # Green color for due date
                else: #If we're late on our payment
                    due_date = "\033[31m" + due_date + "\033[0m" #Red color for due date
                print(f"| {bill[0]:<13}| {bill[1]:<15} | {amount:<22} | {due_date:<24}| {paid_status:<15}            |")
            print("---------------------------------------------------------------------------------------")
            print(f"                            \033[4mTotal Amount Owed: ${total_owed:.2f}\033[0m")
        elif choice == "3":
            bills = view_bills()
            print("---------------------------------------------------------------------------------------")
            print("| \033[1mID\033[0m           | \033[1mCompany\033[0m         | \033[1mAmount\033[0m        | \033[1mDue Date\033[0m       | \033[1mPaid Status\033[0m       |")
            print("---------------------------------------------------------------------------------------")
            for bill in bills:
                amount = f"\033[32m${bill[2]:.2f}\033[0m" if bill[4] else f"\033[31m${bill[2]:.2f}\033[0m"  # Green if paid, red if unpaid
                paid_status = "\033[32mYes\033[0m" if bill[4] else "\033[31mNo\033[0m"  # Green for "Yes", red for "No"
                due_date = bill[3]
                due_date_obj = datetime.datetime.strptime(due_date, "%Y-%m-%d").date()
                today = datetime.date.today()
                days_until_due = (due_date_obj - today).days
                if 0 <= days_until_due <= 30:  # If due date is within 30 days
                    due_date = "\033[33m" + due_date + "\033[0m"  # Yellow color for due date
                elif days_until_due > 30: # If due date is beyond 30 days
                    due_date = "\033[32m" + due_date + "\033[0m" # Green color for due date
                else: #If we're late on our payment
                    due_date = "\033[31m" + due_date + "\033[0m" #Red color for due date
                print(f"| {bill[0]:<13}| {bill[1]:<15} | {amount:<22} | {due_date:<24}| {paid_status:<15}            |")
            print("---------------------------------------------------------------------------------------")
            selected_id = input("\n\033[47m\033[30mPlease enter a bill ID:\033[0m ")
            
            if selected_id == '0':
                break
            
            try:
                selected_id = int(selected_id)
                bill = next((b for b in bills if b[0] == selected_id), None)
                if bill:
                    print("\n---------------------------------------------------------------------------------------")
                    print("| \033[1mID\033[0m           | \033[1mCompany\033[0m         | \033[1mAmount\033[0m        | \033[1mDue Date\033[0m       | \033[1mPaid Status\033[0m       |")
                    print("---------------------------------------------------------------------------------------")
                    amount = f"\033[32m${bill[2]:.2f}\033[0m" if bill[4] else f"\033[31m${bill[2]:.2f}\033[0m"  # Green if paid, red if unpaid
                    paid_status = "\033[32mYes\033[0m" if bill[4] else "\033[31mNo\033[0m"  # Green for "Yes", red for "No"
                    due_date = bill[3]
                    due_date_obj = datetime.datetime.strptime(due_date, "%Y-%m-%d").date()
                    today = datetime.date.today()
                    days_until_due = (due_date_obj - today).days
                    if 0 <= days_until_due <= 30:  # If due date is within 30 days
                        due_date = "\033[33m" + due_date + "\033[0m"  # Yellow color for due date
                    elif days_until_due > 30: # If due date is beyond 30 days
                        due_date = "\033[32m" + due_date + "\033[0m" # Green color for due date
                    else: #If we're late on our payment
                        due_date = "\033[31m" + due_date + "\033[0m" #Red color for due date
                    print(f"| {bill[0]:<13}| {bill[1]:<15} | {amount:<22} | {due_date:<24}| {paid_status:<15}            |")
                    print("---------------------------------------------------------------------------------------")

                    while True:
                        print("\nSelect an action:\n")
                        print("\033[33m1.\033[0m Mark as paid")
                        print("\033[33m2.\033[0m Mark as unpaid")
                        print("\033[33m3.\033[0m Change due date")
                        print("\033[33m4.\033[0m Change company name")
                        print("\033[33m5.\033[0m Change amount due")
                        print("\033[33m6.\033[0m Remove bill")
                        print("\033[33m7.\033[0m Return to main menu")

                        sub_choice = input("\n\033[47m\033[30mEnter your choice:\033[0m ")

                        if sub_choice == "1":
                            mark_as_paid(selected_id)
                            bills = view_bills()
                            bill = next((b for b in bills if b[0] == selected_id), None)
                            print("\n\033[32mBill", selected_id, "marked as paid.\033[0m\n")
                            break
                        elif sub_choice == "2":
                            mark_as_unpaid(selected_id)
                            bills = view_bills()
                            bill = next((b for b in bills if b[0] == selected_id), None)
                            print("\n\033[31mBill", selected_id, "marked as unpaid.\033[0m\n")
                            break
                        elif sub_choice == "3":
                            new_due_date = input("\n\033[47m\033[30mEnter the new due date (YYYY-MM-DD):\033[0m ")
                            update_due_date(selected_id, new_due_date)
                            bills = view_bills()
                            bill = next((b for b in bills if b[0] == selected_id), None)
                            print("\n\033[33mBill", selected_id, "due date changed.\033[0m\n")
                            break
                        elif sub_choice == "4":
                            new_company_name = input("\n\033[47m\033[30mEnter the new company name:\033[0m ")
                            update_company_name(selected_id, new_company_name)
                            bills = view_bills()
                            bill = next((b for b in bills if b[0] == selected_id), None)
                            print("\n\033[33mBill", selected_id, "company name changed.\033[0m\n")
                            break
                        elif sub_choice == "5":
                            new_amount_due = float(input("\n\033[47m\033[30mEnter the new amount due:\033[0m $"))
                            update_amount_due(selected_id, new_amount_due)
                            bills = view_bills()
                            bill = next((b for b in bills if b[0] == selected_id), None)
                            print("\n\033[33mBill", selected_id, "balance changed.\033[0m\n")
                            break
                        elif sub_choice == "6":
                            remove_bill(selected_id)
                            print("\n\033[31mBill", selected_id, "removed.\033[0m")
                            bill = None
                            break
                        elif sub_choice == "7":
                            break
                        else:
                            print("Invalid choice. Please try again.")
                else:
                    print("Bill ID not found. Please enter a valid bill ID.")
                if bill:
                    print("---------------------------------------------------------------------------------------")
                    print("| \033[1mID\033[0m           | \033[1mCompany\033[0m         | \033[1mAmount\033[0m        | \033[1mDue Date\033[0m       | \033[1mPaid Status\033[0m       |")
                    print("---------------------------------------------------------------------------------------")
                    amount = f"\033[32m${bill[2]:.2f}\033[0m" if bill[4] else f"\033[31m${bill[2]:.2f}\033[0m"  # Green if paid, red if unpaid
                    paid_status = "\033[32mYes\033[0m" if bill[4] else "\033[31mNo\033[0m"  # Green for "Yes", red for "No"
                    due_date = bill[3]
                    due_date_obj = datetime.datetime.strptime(due_date, "%Y-%m-%d").date()
                    today = datetime.date.today()
                    days_until_due = (due_date_obj - today).days
                    if 0 <= days_until_due <= 30:  # If due date is within 30 days
                        due_date = "\033[33m" + due_date + "\033[0m"  # Yellow color for due date
                    elif days_until_due > 30: # If due date is beyond 30 days
                        due_date = "\033[32m" + due_date + "\033[0m" # Green color for due date
                    else: #If we're late on our payment
                        due_date = "\033[31m" + due_date + "\033[0m" #Red color for due date
                    print(f"| {bill[0]:<13}| {bill[1]:<15} | {amount:<22} | {due_date:<24}| {paid_status:<15}            |")
                    print("---------------------------------------------------------------------------------------")
            except ValueError:
                print("\nInvalid input.")
        elif choice == "4":
            print("Exiting the bill tracker.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    create_table()
    main()

# Close the connection to the database when the program is finished
conn.close()
