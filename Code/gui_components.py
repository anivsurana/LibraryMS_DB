import tkinter as tk
from tkinter import ttk
from datetime import date, timedelta  # Import date and timedelta for date handling
# Import your database functions
from database import add_borrower, check_out_book, list_borrower_info, add_book_to_all_branches, list_copies_loaned_out, list_late_book_loans

frame_stack = []

# Function to clear all widgets from a frame
def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()

# Function to set up the main menu
def setup_main_menu(root):
    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(fill='both', expand=True)
    frame_stack.append(main_frame)

    title_label = ttk.Label(main_frame, text="Library Management System", font=('Arial', 24))
    title_label.pack(pady=20)

    btn_add_borrower = ttk.Button(main_frame, text="Add New Borrower", command=lambda: setup_add_borrower_frame(root))
    btn_add_borrower.pack(fill='x', padx=20, pady=5)

    btn_check_out_book = ttk.Button(main_frame, text="Check Out Book", command=lambda: setup_check_out_book_frame(root))
    btn_check_out_book.pack(fill='x', padx=20, pady=5)

    btn_list_loaned_copies = ttk.Button(main_frame, text="List Loaned Copies", command=lambda: setup_list_loaned_copies_frame(root))
    btn_list_loaned_copies.pack(fill='x', padx=20, pady=5)

    btn_list_late_loans = ttk.Button(main_frame, text="List Late Book Loans", command=lambda: setup_list_late_loans_frame(root))
    btn_list_late_loans.pack(fill='x', padx=20, pady=5)

    btn_list_borrowers = ttk.Button(main_frame, text="List Borrowers", command=lambda: list_borrower_info())
    btn_list_borrowers.pack(fill='x', padx=20, pady=5)

    

    return main_frame

# Function to set up the 'Add Borrower' frame
def setup_add_borrower_frame(root):
    clear_frame(root)
    frame = ttk.Frame(root, padding="10")
    frame.pack(fill='both', expand=True)
    frame_stack.append(frame)

    ttk.Label(frame, text="Name").grid(row=0, column=0, padx=10, pady=10)
    ttk.Label(frame, text="Address").grid(row=1, column=0, padx=10, pady=10)
    ttk.Label(frame, text="Phone").grid(row=2, column=0, padx=10, pady=10)

    name_entry = ttk.Entry(frame)
    address_entry = ttk.Entry(frame)
    phone_entry = ttk.Entry(frame)

    name_entry.grid(row=0, column=1, padx=10, pady=10)
    address_entry.grid(row=1, column=1, padx=10, pady=10)
    phone_entry.grid(row=2, column=1, padx=10, pady=10)

    ttk.Button(frame, text="Submit", command=lambda: add_borrower(name_entry.get(), address_entry.get(), phone_entry.get())).grid(row=3, column=1, pady=10)
    ttk.Button(frame, text="Back", command=lambda: go_back(root)).grid(row=3, column=0, pady=10)

# Function to set up the 'Check Out Book' frame
def setup_check_out_book_frame(root):
    clear_frame(root)
    frame = ttk.Frame(root, padding="10")
    frame.pack(fill='both', expand=True)
    frame_stack.append(frame)

    ttk.Label(frame, text="Check Out Book", font=('Arial', 18)).grid(row=0, column=0, columnspan=2, pady=10)

    # Entry fields for book details
    ttk.Label(frame, text="Book ID:").grid(row=1, column=0, padx=10, pady=5)
    book_id_entry = ttk.Entry(frame)
    book_id_entry.grid(row=1, column=1, padx=10, pady=5)

    ttk.Label(frame, text="Branch ID:").grid(row=2, column=0, padx=10, pady=5)
    branch_id_entry = ttk.Entry(frame)
    branch_id_entry.grid(row=2, column=1, padx=10, pady=5)

    ttk.Label(frame, text="Card No:").grid(row=3, column=0, padx=10, pady=5)
    card_no_entry = ttk.Entry(frame)
    card_no_entry.grid(row=3, column=1, padx=10, pady=5)

    # Buttons to check out and return to the main menu
    ttk.Button(frame, text="Check Out", command=lambda: check_out_book(
        book_id_entry.get(),
        branch_id_entry.get(),
        card_no_entry.get(),
        date.today(),  # You can replace this with the actual date
        date.today() + timedelta(days=7)  # Due date (7 days from today), you can adjust this as needed
    )).grid(row=4, column=1, pady=10)

    ttk.Button(frame, text="Back", command=lambda: go_back(root)).grid(row=4, column=0, pady=10)

# Function to set up the 'List Loaned Copies' frame
def setup_list_loaned_copies_frame(root):
    clear_frame(root)
    frame = ttk.Frame(root, padding="10")
    frame.pack(fill='both', expand=True)
    frame_stack.append(frame)

    ttk.Label(frame, text="Enter Book Title:").grid(row=0, column=0, padx=10, pady=10)
    book_title_entry = ttk.Entry(frame)
    book_title_entry.grid(row=0, column=1, padx=10, pady=10)

    ttk.Button(frame, text="List Loaned Copies", command=lambda: list_copies_loaned_out(book_title_entry.get())).grid(row=1, column=1, pady=10)
    ttk.Button(frame, text="Back", command=lambda: go_back(root)).grid(row=1, column=0, pady=10)

def setup_list_late_loans_frame(root):
    clear_frame(root)
    frame = ttk.Frame(root, padding="10")
    frame.pack(fill='both', expand=True)
    frame_stack.append(frame)
    
    # Configure the grid
    frame.columnconfigure(1, weight=1)
    frame.rowconfigure(3, weight=1)

    # Date entry labels and fields
    ttk.Label(frame, text="Start Date (YYYY-MM-DD):").grid(row=0, column=0, padx=10, pady=10, sticky='e')
    start_date_entry = ttk.Entry(frame)
    start_date_entry.grid(row=0, column=1, padx=10, pady=10, sticky='ew')

    ttk.Label(frame, text="End Date (YYYY-MM-DD):").grid(row=1, column=0, padx=10, pady=10, sticky='e')
    end_date_entry = ttk.Entry(frame)
    end_date_entry.grid(row=1, column=1, padx=10, pady=10, sticky='ew')

    # Treeview
    columns = ("Card No", "Borrower Name", "Book Title", "Date Out", "Due Date", "Returned Date", "Days Late", "Branch ID", "Late Fee Balance")

    tree = ttk.Treeview(frame, columns=columns, show='headings')
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center")
    tree.grid(row=3, column=0, columnspan=2, sticky='nsew', pady=10)

    # Scrollbar for Treeview
    scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.grid(row=3, column=2, sticky='ns')

    # List and back buttons
    ttk.Button(frame, text="List Late Loans", command=lambda: list_late_book_loans(start_date_entry.get(), end_date_entry.get(), tree)).grid(row=2, column=1, pady=10, sticky='ew')
    ttk.Button(frame, text="Back", command=lambda: go_back(root)).grid(row=2, column=0, pady=10, sticky='ew')

    # Set focus to the start date entry
    start_date_entry.focus()




# Function to go back to the previous frame or main menu
def go_back(root):
    if frame_stack:
        current_frame = frame_stack.pop()
        current_frame.destroy()  # Destroy the current frame

    clear_frame(root)  # Clear the screen
    setup_main_menu(root)  # Display the main menu


# Main application setup
def create_gui():
    root = tk.Tk()
    root.geometry('600x400')  # Set the initial size of the window
    root.title("Library Management System")
    setup_main_menu(root)
    return root

if __name__ == "__main__":
    gui = create_gui()
    gui.mainloop()
