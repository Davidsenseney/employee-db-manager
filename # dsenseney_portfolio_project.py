# dsenseney_portfolio_project.py
# A simple Employee Database Management System (CRUD)
# Demonstrates OOP, Tkinter, and SQLite
import tkinter
from tkinter import ttk  # 'ttk' gives us modern-looking widgets
from tkinter import messagebox
import sqlite3

class EmployeeApp:
    """
    Main application class for the Employee Database Management System.
    
    This class handles:
    - Creating the main UI (widgets and layout).
    - Managing the database connection.
    - Handling all user interactions and business logic.
    """
    
    def __init__(self, root):
        """Initialize the application."""
        self.root = root
        self.root.title("Employee Management System")
        self.root.geometry("800x600")

        # --- Database Initialization ---
        self.db_conn = sqlite3.connect('employee_database.db')
        self.db_cursor = self.db_conn.cursor()
        self.setup_database()

        # --- Create UI Components ---
        self.create_widgets()
        
        # --- Populate Data ---
        self.refresh_treeview()
        
        # --- Set up protocol for closing the window ---
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_database(self):
        """Create the Employees table if it doesn't already exist."""
        try:
            self.db_cursor.execute('''
            CREATE TABLE IF NOT EXISTS Employees (
                ID INTEGER PRIMARY KEY NOT NULL,
                Name TEXT NOT NULL,
                Salary INTEGER NOT NULL
            )
            ''')
            self.db_conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to create table: {e}")

    def create_widgets(self):
        """Create and lay out all the UI widgets."""
        
        # --- Input Frame ---
        input_frame = ttk.Frame(self.root, padding="10")
        input_frame.pack(fill='x', padx=10, pady=5)

        # Labels
        ttk.Label(input_frame, text="Employee ID:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        ttk.Label(input_frame, text="Full Name:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        ttk.Label(input_frame, text="Salary:").grid(row=2, column=0, padx=5, pady=5, sticky='w')

        # Entry Fields
        self.id_entry = ttk.Entry(input_frame, width=40)
        self.name_entry = ttk.Entry(input_frame, width=40)
        self.salary_entry = ttk.Entry(input_frame, width=40)
        
        self.id_entry.grid(row=0, column=1, padx=5, pady=5)
        self.name_entry.grid(row=1, column=1, padx=5, pady=5)
        self.salary_entry.grid(row=2, column=1, padx=5, pady=5)

        # --- Button Frame ---
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(button_frame, text="Add Employee", command=self.add_employee).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Update Employee", command=self.update_employee).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete Employee", command=self.delete_employee).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear Fields", command=self.clear_fields).pack(side='left', padx=5)
        
        # --- Treeview (Data Display) ---
        tree_frame = ttk.Frame(self.root, padding="10")
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Scrollbar
        tree_scroll = ttk.Scrollbar(tree_frame)
        tree_scroll.pack(side='right', fill='y')

        # The Treeview widget
        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Name", "Salary"), show="headings", yscrollcommand=tree_scroll.set)
        self.tree.pack(fill='both', expand=True)
        tree_scroll.config(command=self.tree.yview)

        # Define column headings
        self.tree.heading("ID", text="Employee ID")
        self.tree.heading("Name", text="Full Name")
        self.tree.heading("Salary", text="Salary")
        
        # Set column widths
        self.tree.column("ID", width=100, anchor='center')
        self.tree.column("Name", width=300)
        self.tree.column("Salary", width=150, anchor='w') # 'e' for east (right) alignment

        # Bind the treeview selection event
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

    def refresh_treeview(self):
        """Clear the Treeview and repopulate it with fresh data from the DB."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Fetch all records
        try:
            self.db_cursor.execute("SELECT ID, Name, Salary FROM Employees ORDER BY ID")
            rows = self.db_cursor.fetchall()
            
            # Insert new data
            for row in rows:
                self.tree.insert("", "end", values=row)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to fetch records: {e}")

    def add_employee(self):
        """Add a new employee to the database."""
        # --- 1. Validation ---
        try:
            emp_id = int(self.id_entry.get())
            emp_name = self.name_entry.get()
            emp_salary = int(self.salary_entry.get())
        except ValueError:
            messagebox.showerror("Input Error", "ID and Salary must be integers.")
            return

        if not emp_name:
            messagebox.showerror("Input Error", "Name field cannot be empty.")
            return

        # --- 2. Database Operation ---
        try:
            self.db_cursor.execute(
                "INSERT INTO Employees (ID, Name, Salary) VALUES (?, ?, ?)",
                (emp_id, emp_name, emp_salary)
            )
            self.db_conn.commit()
            messagebox.showinfo("Success", "Employee added successfully.")

        except sqlite3.IntegrityError:
            messagebox.showerror("Database Error", f"Employee ID {emp_id} already exists.")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

        # --- 3. UI Update ---
        self.clear_fields()
        self.refresh_treeview()

    def update_employee(self):
        """Update an existing employee's name and salary based on ID."""
        # --- 1. Validation ---
        try:
            emp_id = int(self.id_entry.get())
            emp_name = self.name_entry.get()
            emp_salary = int(self.salary_entry.get())
        except ValueError:
            messagebox.showerror("Input Error", "ID and Salary must be integers.")
            return

        if not emp_name:
            messagebox.showerror("Input Error", "Name field cannot be empty.")
            return
            
        # --- 2. Database Operation ---
        try:
            # Check if record exists
            self.db_cursor.execute("SELECT * FROM Employees WHERE ID = ?", (emp_id,))
            if not self.db_cursor.fetchone():
                messagebox.showerror("Error", f"No employee found with ID {emp_id}.")
                return

            # Perform update
            self.db_cursor.execute(
                "UPDATE Employees SET Name = ?, Salary = ? WHERE ID = ?",
                (emp_name, emp_salary, emp_id)
            )
            self.db_conn.commit()
            messagebox.showinfo("Success", "Employee updated successfully.")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
            
        # --- 3. UI Update ---
        self.clear_fields()
        self.refresh_treeview()

    def delete_employee(self):
        """Delete an employee from the database based on ID."""
        # --- 1. Validation ---
        try:
            emp_id = int(self.id_entry.get())
        except ValueError:
            messagebox.showerror("Input Error", "ID must be an integer.")
            return
            
        # --- 2. Confirmation ---
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete employee ID {emp_id}?"):
            return

        # --- 3. Database Operation ---
        try:
            self.db_cursor.execute("DELETE FROM Employees WHERE ID = ?", (emp_id,))
            if self.db_cursor.rowcount == 0:
                messagebox.showerror("Error", f"No employee found with ID {emp_id}.")
            else:
                self.db_conn.commit()
                messagebox.showinfo("Success", "Employee deleted successfully.")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

        # --- 4. UI Update ---
        self.clear_fields()
        self.refresh_treeview()

    def clear_fields(self):
        """Clear all entry fields."""
        self.id_entry.delete(0, 'end')
        self.name_entry.delete(0, 'end')
        self.salary_entry.delete(0, 'end')
        
        # De-select any item in the treeview
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection()[0])

    def on_tree_select(self, event):
        """Event handler for when a user clicks on an item in the Treeview."""
        # Get selected item
        try:
            selected_item = self.tree.selection()[0]
            item_data = self.tree.item(selected_item, 'values')
            
            # Clear current entry fields
            self.clear_fields()
            
            # Insert selected data into entry fields
            self.id_entry.insert(0, item_data[0])
            self.name_entry.insert(0, item_data[1])
            self.salary_entry.insert(0, item_data[2])
        except IndexError:
            # This happens if the selection is cleared
            pass

    def on_closing(self):
        """Handle the window close event."""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.db_conn.close()  # Close the database connection cleanly
            self.root.destroy()


# --- Main execution ---
if __name__ == "__main__":
    main_window = tkinter.Tk()
    app = EmployeeApp(main_window)
    main_window.mainloop()