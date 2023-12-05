import tkinter as tk
from gui_components import setup_main_menu

def main():
    root = tk.Tk()
    root.geometry('600x400')
    root.title("Bibliotech")

    # Initialize the main menu
    setup_main_menu(root)

    # Any other initializations here
    
    root.mainloop()

if __name__ == "__main__":
    main()
