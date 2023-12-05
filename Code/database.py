import tkinter as tk
from tkinter import messagebox
import mysql.connector

# Database connection details
DB_HOST = "localhost"
DB_USER = "root"
DB_PASS = "password123"
DB_NAME = "lmsystem"

# Connect to the database
def connect_to_db():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )

# Add a borrower to the database
def add_borrower(name, address, phone):
    conn = connect_to_db()
    cursor = conn.cursor()
    query = "INSERT INTO BORROWER (Name, Address, Phone) VALUES (%s, %s, %s)"
    try:
        cursor.execute(query, (name, address, phone))
        conn.commit()
        card_no = cursor.lastrowid  # Get the last inserted ID
        messagebox.showinfo("Success", f"Borrower added successfully! Welcome, your card number is {card_no}")
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Failed to add borrower: {err}")
    finally:
        cursor.close()
        conn.close()


def check_out_book(book_id, branch_id, card_no, date_out, due_date):
    conn = connect_to_db()
    cursor = conn.cursor()

    # Add a record to Book_Loan
    query_loan = "INSERT INTO BOOK_LOANS (Book_Id, Branch_Id, Card_No, Date_Out, Due_Date) VALUES (%s, %s, %s, %s, %s)"
    try:
        cursor.execute(query_loan, (book_id, branch_id, card_no, date_out, due_date))
        conn.commit()
        messagebox.showinfo("Success", "Book checked out successfully!")

        # Query to get the book name
        query_book_name = "SELECT Title FROM BOOK WHERE Book_Id = %s"
        cursor.execute(query_book_name, (book_id,))
        book_name = cursor.fetchone()[0]

        # Query to get the branch name
        query_branch_name = "SELECT Branch_Name FROM LIBRARY_BRANCH WHERE Branch_Id = %s"
        cursor.execute(query_branch_name, (branch_id,))
        branch_name = cursor.fetchone()[0]

        # Query to get the updated number of copies
        query_copies = "SELECT No_Of_Copies FROM BOOK_COPIES WHERE Book_Id = %s AND Branch_Id = %s"
        cursor.execute(query_copies, (book_id, branch_id))
        no_of_copies = cursor.fetchone()[0]
        
        # Display the updated information
        info_message = f"Book '{book_name}' checked out from '{branch_name}'.\nUpdated number of copies: {no_of_copies}"
        messagebox.showinfo("Checkout Details", info_message)
        
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Failed to check out book: {err}")
    finally:
        cursor.close()
        conn.close()


# Add a new book to all branches
def add_book_to_all_branches(title, book_publisher, author_name):
    conn = connect_to_db()
    cursor = conn.cursor()
    # Assuming you have a function to get all branch IDs
    branch_ids = get_all_branch_ids(cursor)
    try:
        # Insert the new book
        cursor.execute("INSERT INTO BOOK (Title, Book_Publisher) VALUES (%s, %s)", (title, book_publisher))
        book_id = cursor.lastrowid
        # Insert the author
        cursor.execute("INSERT INTO BOOK_AUTHORS (Book_Id, Author_Name) VALUES (%s, %s)", (book_id, author_name))
        # Add copies to all branches
        for branch_id in branch_ids:
            cursor.execute("INSERT INTO BOOK_COPIES (Book_Id, Branch_Id, No_Of_Copies) VALUES (%s, %s, %s)", (book_id, branch_id, 5))
        conn.commit()
        messagebox.showinfo("Success", "Book added to all branches successfully!")
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Failed to add book to all branches: {err}")
    finally:
        cursor.close()
        conn.close()

# List the number of copies loaned out per branch for a given book title
def list_copies_loaned_out(title):
    conn = connect_to_db()
    cursor = conn.cursor()

    query = """
    SELECT LB.Branch_Name, COUNT(*) AS Copies_Loaned
    FROM BOOK_LOANS AS BL
    JOIN BOOK AS B ON BL.Book_Id = B.Book_Id
    JOIN LIBRARY_BRANCH AS LB ON BL.Branch_Id = LB.Branch_Id
    WHERE B.Title = %s AND BL.Returned_Date IS NULL
    GROUP BY BL.Branch_Id, LB.Branch_Name
    """
    try:
        cursor.execute(query, (title,))
        rows = cursor.fetchall()

        if rows:
            result = f"Copies of '{title}' loaned out per branch:\n"
            for row in rows:
                branch_name, copies_loaned = row
                result += f"Branch: {branch_name}, Copies Loaned: {copies_loaned}\n"
            messagebox.showinfo("Loan Info", result)
        else:
            messagebox.showinfo("Loan Info", f"No copies of '{title}' are currently loaned out.")

    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Failed to list copies loaned out: {err}")
    finally:
        cursor.close()
        conn.close()


# List book loans that were returned late within a given due date range
def list_late_book_loans(start_date, end_date):
    conn = connect_to_db()
    cursor = conn.cursor()
    query = """
    SELECT BL.*, DATEDIFF(BL.Returned_Date, BL.Due_Date) AS Days_Late
    FROM BOOK_LOANS AS BL
    WHERE BL.Due_Date BETWEEN %s AND %s AND BL.Returned_Date > BL.Due_Date
    """
    try:
        cursor.execute(query, (start_date, end_date))
        rows = cursor.fetchall()
        for row in rows:
            print(f"Loan ID: {row[0]}, Days Late: {row[-1]}")
        messagebox.showinfo("Success", "List of late book loans retrieved successfully!")
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Failed to list late book loans: {err}")
    finally:
        cursor.close()
        conn.close()

def list_borrower_info(search_criteria=None):
    conn = connect_to_db()
    cursor = conn.cursor()

    # Base query targeting the vBookLoanInfo view
    query = """
    SELECT `Card_No`, `Borrower Name`, `LateFeeBalance`
    FROM vBookLoanInfo
    """

    # Modify the query based on the search criteria
    if search_criteria:
        if search_criteria.isdigit():  # Assuming search by Card_No if it's a digit
            query += " WHERE `Card_No` = %s"
            params = (search_criteria,)
        else:  # Assuming search by part of the name otherwise
            query += " WHERE `Borrower Name` LIKE %s"
            params = ('%' + search_criteria + '%',)
    else:
        # If no search criteria provided, order by LateFeeBalance
        query += " ORDER BY `LateFeeBalance` DESC"
        params = ()

    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        result = "Borrower Info:\n"
        for row in rows:
            result += f"ID: {row[0]}, Name: {row[1]}, Late Fee Balance: ${float(row[2]):.2f}\n"
        # Here, you could return the result string or update a GUI element with the result
        messagebox.showinfo("Borrower Info", result)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Failed to retrieve borrower info: {err}")
    finally:
        cursor.close()
        conn.close()


# # Example usage:
# list_borrower_info()  # List all
# list_borrower_info('123')  # Search by Card_No
# list_borrower_info('John Doe')  # Search by name


# # Main GUI setup
# def create_gui():
#     root = tk.Tk()
#     root.title("Library Management System")

#     # Setup frames for different tasks
#     main_frame = tk.Frame(root)
#     add_borrower_frame = tk.Frame(root)
#     check_out_book_frame = tk.Frame(root)
#     # ... Additional frames for other tasks

#     # Layout frames in the same grid cell to stack them
#     for frame in (main_frame, add_borrower_frame, check_out_book_frame):  # Add additional frames to this list
#         frame.grid(row=0, column=0, sticky='news')

#     # Function to raise a frame to the top for view
#     def raise_frame(frame):
#         frame.tkraise()

#     # Home frame with navigation buttons
#     # ... Add navigation buttons that call raise_frame with the appropriate frame

#     # Add borrower frame with form fields and submission button
#     # ... Add labels, entry widgets, and a button that calls add_borrower

#     # Check out book frame with form fields and submission button
#     # ... Add labels, entry widgets, and a button that calls check_out_book

#     # ... Additional setup for other frames/tasks

#     # Start on the main frame
#     raise_frame(main_frame)

#     return root

# # Run the GUI application
# if __name__ == "__main__":
#     gui = create_gui()
#     gui.mainloop()
