from db_connection import get_connection
import psycopg
from datetime import datetime

def get_valid_input(message):
    while True:
        value = input(message).strip()
        if value:
            return value
        print("Input cannot be empty. Please try again.")

def validate_status():
    valid_statuses = ["Applied", "Interview", "Rejected", "Selected"]
    while True:
        status = input("Enter application status: ").strip().title()
        if status in valid_statuses:
            return status
        print("Invalid status! Choose Applied, Interview, Rejected, or Selected.")


def add_application():
    conn = get_connection()
    if conn is None:
        print("Unable to connect to database.")
        return
    cursor = None

    try:
        cursor = conn.cursor()

        company = get_valid_input("Enter company name: ")
        role = get_valid_input("Enter job role: ")
        location = input("Enter job location: ")
        date = input("Enter Application Date: ")
        status = validate_status()
        url = input("Paste Job URL: ")

        query = """
        INSERT INTO applications
        (company_name, job_role, location, application_date, status, job_url)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (company, role, location, date, status, url))
        conn.commit()
        print("Application added successfully!")

    except psycopg.Error as e:
        conn.rollback()
        print("Database error:", e)

    except Exception as e:
        conn.rollback()
        print("Unexpected error:", e)

    finally:
        if cursor:
            cursor.close()
        conn.close()



def view_applications():
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT application_id, company_name, job_role,
                   location, application_date, status
            FROM applications
            ORDER BY application_date DESC
        """)
        records = cursor.fetchall()

        if records:
            print("\n" + "-"*100)
            print(f"{'ID':<5} {'Company':<15} {'Job Role':<30} {'Location':<15} {'Date':<15} {'Status':<12}")
            print("-"*100)
            for record in records:
                print(
                    f"{record[0]:<5} "
                    f"{record[1]:<15} "
                    f"{record[2]:<30} "
                    f"{str(record[3] or '-'):<15} "
                    f"{str(record[4]):<15} "
                    f"{record[5]:<12}"
                )
            print("-"*100)
        else:
            print("No applications found.")
        cursor.close()
        conn.close()



def get_valid_application_id():
    while True:
        application_id = input("Enter Application ID: ").strip()
        if application_id.isdigit() and int(application_id) > 0:
            return int(application_id)
        print("Invalid ID! Please enter a positive number.")

def update_status():
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        application_id = get_valid_application_id()
        new_status = input("Enter new status (Applied/Interview/Rejected/Selected): ")

        query = """
        UPDATE applications
        SET status = %s
        WHERE application_id = %s
        RETURNING application_id, company_name, job_role, status
        """

        cursor.execute(query, (new_status, application_id))
        updated_record = cursor.fetchone()

        if updated_record:
            conn.commit()
            print("\nApplication status updated successfully!")
            print("\n" + "-"*65)
            print(f"{'ID':<5} {'Company':<15} {'Job Role':<25} {'New Status':<12}")
            print("-"*65)
            print(
                f"{updated_record[0]:<5} "
                f"{updated_record[1]:<15} "
                f"{updated_record[2]:<25} "
                f"{updated_record[3]:<15} "
            )
        else:
            conn.rollback()
            print("Application ID not found.")

        cursor.close()
        conn.close()



def delete_application():
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        application_id = get_valid_application_id()

        # Check application exists or not
        cursor.execute(
            "SELECT company_name, job_role FROM applications WHERE application_id = %s",(application_id,)
        )

        record = cursor.fetchone()
        if record:
            print("\nApplication found:")
            print("Company:", record[0])
            print("Job Role:", record[1])
            confirm = input("Are you sure do you want to delete?: ")
            if confirm.lower() == "yes" or confirm.lower() == "y":
                cursor.execute(
                    "DELETE FROM applications WHERE application_id = %s",
                    (application_id,)
                )
                conn.commit()
                print("Application deleted successfully!")
            else:
                conn.rollback()
                print("Deletion cancelled.")
        else:
            print("Application ID not found.")

        cursor.close()
        conn.close()



def get_valid_date(message):
    while True:
        date_input = input(message).strip()

        try:
            return datetime.strptime(
                date_input, "%Y-%m-%d"
            ).date()

        except ValueError:
            print("Invalid date! Use YYYY-MM-DD format.")



def search_application():
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        print("\nSearch by:")
        print("1. Company Name")
        print("2. Job Role")
        print("3. Application Status")
        print("4. Application Date")

        choice = input("Enter your choice: ")

        if choice == "1":
            search_value = input("Enter company name: ")
            query = """
            SELECT * FROM applications
            WHERE company_name ILIKE %s
            ORDER BY application_date
            """
            cursor.execute(query, (f"%{search_value}%",))
        elif choice == "2":
            search_value = input("Enter job role: ")
            query = """
            SELECT * FROM applications
            WHERE job_role ILIKE %s
            ORDER BY application_date
            """
            cursor.execute(query, (f"%{search_value}%",))
        elif choice == "3":
            search_value = input("Enter Application Status: ")
            query = """
            SELECT * FROM applications
            WHERE status ILIKE %s
            ORDER BY application_date
            """
            cursor.execute(query, (f"%{search_value}%",))
        elif choice == "4":
            start_date = get_valid_date("Enter start date (YYYY-MM-DD): ")
            end_date = get_valid_date("Enter end date (YYYY-MM-DD): ")
            if end_date < start_date:
                print("End date cannot be earlier than start date.")
                cursor.close()
                conn.close()
                return
            query = """
            SELECT *
            FROM applications
            WHERE application_date BETWEEN %s AND %s
            ORDER BY application_date DESC
            """
            cursor.execute(query, (start_date, end_date))
        else:
            print("Invalid choice.")
            cursor.close()
            conn.close()
            return

        records = cursor.fetchall()

        if records:
            print("\n" + "-" * 100)
            print(f"{'ID':<5} {'Company':<15} {'Job Role':<22} {'Location':<15} {'Date':<15} {'Status':<12}")
            print("-"*100)
            for record in records:
                print(
                    f"{record[0]:<5} "
                    f"{record[1]:<15} "
                    f"{record[2]:<22} "
                    f"{str(record[3] or '-'):<15} "
                    f"{str(record[4]):<15} "
                    f"{record[5]:<12}"
                )
        else:
            print("No matching applications found.")
        cursor.close()
        conn.close()



def application_statistics():
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        query = """
        SELECT status, COUNT(*) AS total
        FROM applications
        GROUP BY status
        ORDER BY status;
        """
        cursor.execute(query)
        records = cursor.fetchall()
        print("\n--- Application Statistics ---")
        if records:
            for record in records:
                print(f"{record[0]:<15} : {record[1]}")
        else:
            print("No applications found.")
        cursor.close()
        conn.close()



while True:
    print("\n===== JOB APPLICATION TRACKER =====")
    print("1. Add Application")
    print("2. View Applications")
    print("3. Update Applications Status")
    print("4. Delete Applications")
    print("5. Search Applications")
    print("6. Application Statistics")
    print("7. Exit")

    choice = input("Enter your choice: ")
    if choice == "1":
        add_application()
    elif choice == "2":
        view_applications()
    elif choice == "3":
        update_status()
    elif choice == "4":
        delete_application()
    elif choice == "5":
        search_application()
    elif choice == "6":
        application_statistics()
    elif choice == "7":
        print("Thank you for using Job Tracker!")
        break
    else:
        print("Invalid choice. Try again.")
