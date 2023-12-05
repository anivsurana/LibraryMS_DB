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


def add_book_to_all_branches(title, publisher_name, author_name):
    conn = connect_to_db()
    cursor = conn.cursor()
    
    try:
        conn.start_transaction()

        # Insert the new book
        insert_book_query = "INSERT INTO BOOK (Title, Book_Publisher) VALUES (%s, %s)"
        cursor.execute(insert_book_query, (title, publisher_name))
        book_id = cursor.lastrowid
        
        # Insert the author
        insert_author_query = "INSERT INTO BOOK_AUTHORS (Book_Id, Author_Name) VALUES (%s, %s)"
        cursor.execute(insert_author_query, (book_id, author_name))

        # Insert copies for each branch
        insert_copies_query = "INSERT INTO BOOK_COPIES (Book_Id, Branch_Id, No_Of_Copies) VALUES (%s, %s, %s)"
        for branch_id in range(1, 6):
            cursor.execute(insert_copies_query, (book_id, branch_id, 5))

        conn.commit()
        print(f"Book '{title}' added successfully with author '{author_name}' to all branches.")
    except mysql.connector.Error as err:
        conn.rollback()
        print(f"Failed to add book: {err}")
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
def list_late_book_loans(start_date, end_date, tree):
    conn = connect_to_db()
    cursor = conn.cursor()

    query = """
    SELECT 
        Card_No,
        `Borrower Name`,
        `Book Title`,
        Date_Out,
        Due_Date,
        Returned_Date,
        `Days Returned Late`,
        Branch_Id,
        `LateFeeBalance`
    FROM 
        vBookLoanInfo
    WHERE 
        Due_Date BETWEEN %s AND %s
        AND `Days Returned Late` > 0
    """
    try:
        cursor.execute(query, (start_date, end_date))
        rows = cursor.fetchall()

        for row in rows:
            tree.insert("", tk.END, values=row)

        if not rows:
            tree.insert("", tk.END, values=("No Results", "", "", "", "", "", "", ""))

    except mysql.connector.Error as err:
        tree.insert("", tk.END, values=(f"Error: {err}", "", "", "", "", "", "", ""))
    finally:
        cursor.close()
        conn.close()



# database.py
def list_borrower_info(search_criteria, tree):
    conn = connect_to_db()
    cursor = conn.cursor()

    query = """
    SELECT 
        Card_No AS 'ID', 
        `Borrower Name` AS 'Name', 
        COALESCE(`LateFeeBalance`, 0) AS 'LateFeeBalance' 
    FROM 
        vBookLoanInfo
    """

    params = ()
    if search_criteria:
        query += " WHERE (`Card_No` LIKE %s OR `Borrower Name` LIKE %s)"
        params = ('%' + search_criteria + '%', '%' + search_criteria + '%')
    query += " ORDER BY `LateFeeBalance` DESC"

    try:
        cursor.execute(query, params if params else ())
        rows = cursor.fetchall()
        for row in rows:
            id, name, balance = row
            formatted_balance = "${:,.2f}".format(balance)
            tree.insert("", "end", values=(id, name, formatted_balance))
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()


def list_book_info(borrower_id=None, book_title=None):
    conn = connect_to_db()
    cursor = conn.cursor()

    query = """
    SELECT 
        Card_No AS 'Borrower ID', 
        `Borrower Name` AS 'Borrower Name', 
        `Book Title` AS 'Title', 
        Branch_Id AS 'Branch ID', 
        COALESCE(CONCAT('$', FORMAT(LateFeeBalance, 2)), 'Non-Applicable') AS 'Late Fee'
    FROM 
        vbookloaninfo
    """

    params = []  # Ensure this is a list
    conditions = []

    if borrower_id:
        conditions.append("Card_No = %s")
        params.append(borrower_id)  # Append to the list
    if book_title:
        conditions.append("`Book Title` LIKE %s")
        params.append(f"%{book_title}%")  # Append to the list

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY `LateFeeBalance` DESC"

    try:
        cursor.execute(query, params)  # Pass the list to the execute method
        rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []
    finally:
        cursor.close()
        conn.close()
