# books_gui.py
import tkinter as tk
from tkinter import ttk, messagebox
import books_db as db  # Backend database functions for books

class BookManagerApp(tk.Tk):
    def __init__(self):
        """Initialize the Book Manager GUI."""
        super().__init__()
        self.title("📚 Book Management System")
        self.geometry("950x550")
        self.resizable(False, False)
        self.configure(bg="#BD9E89")  # Main background color

        # Initialize database (create tables if they don't exist)
        db.init_db()

        # Build GUI elements (form, buttons, search bar, table)
        self._build_widgets()

        # Populate the table with books from the database
        self.view_books()

    def _build_widgets(self):
        """Create all widgets for book management."""
        # --- Form Frame for entry fields ---
        form_frame = tk.Frame(self, bg="#BD9E89", padx=10, pady=10)
        form_frame.pack(side=tk.TOP, fill=tk.X)

        # Labels and Entry fields for book details
        labels = ["Book Title *", "Author *", "ISBN *", "Genre", "Availability"]
        self.entries = {}  # Store Entry widgets
        for i, label in enumerate(labels):
            tk.Label(form_frame, text=label, bg="#BD9E89", fg="#545454",
                     font=("Arial", 10, "bold")).grid(row=i, column=0, sticky="w", pady=5)
            if label == "Availability":
                # Dropdown for availability
                self.availability_var = tk.StringVar(value="Available")
                combo = ttk.Combobox(form_frame, textvariable=self.availability_var,
                                     values=["Available", "Not Available"], state="readonly", width=37)
                combo.grid(row=i, column=1, pady=5)
            else:
                # Text entry for other fields
                entry = tk.Entry(form_frame, width=40)
                entry.grid(row=i, column=1, pady=5)
                self.entries[label] = entry

        # --- Buttons Frame ---
        btn_frame = tk.Frame(form_frame, bg="#BD9E89")
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)

        def create_button(master, text, command):
            """Helper function to create a styled button."""
            return tk.Button(master, text=text, command=command,
                             bg="#F1ECE5", fg="#545454",
                             font=("Arial", 10, "bold"), width=12,
                             relief="raised", activebackground="#CED1D4")

        # Define buttons and commands
        buttons = [
            ("Add", self.add_book),
            ("Update", self.update_book),
            ("Delete", self.delete_book),
            ("Clear", self.clear_form),
            ("Exit", self.quit_app)
        ]
        # Add buttons to the grid
        for col, (text, cmd) in enumerate(buttons):
            btn = create_button(btn_frame, text, cmd)
            btn.grid(row=0, column=col, padx=5)

        # --- Search Frame ---
        search_frame = tk.Frame(self, bg="#BD9E89", padx=10, pady=5)
        search_frame.pack(fill=tk.X)
        tk.Label(search_frame, text="Search by Title, Author, or ISBN:",
                 bg="#BD9E89", fg="#545454", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.search_var, width=40).pack(side=tk.LEFT, padx=5)
        # Search button
        tk.Button(search_frame, text="Search", command=self.search_books,
                  bg="#F1ECE5", fg="#545454", activebackground="#CED1D4").pack(side=tk.LEFT)
        # Show all button
        tk.Button(search_frame, text="Show All", command=self.view_books,
                  bg="#F1ECE5", fg="#545454", activebackground="#CED1D4").pack(side=tk.LEFT, padx=5)

        # --- Table Frame to display books ---
        table_frame = tk.Frame(self, bg="#E4C9B2", padx=10, pady=10)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))

        columns = ("id", "title", "author", "isbn", "genre", "availability")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        # --- Style the table ---
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"), foreground="#545454")
        style.configure("Treeview", font=("Arial", 10), rowheight=25)

        # Configure each column
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=140, anchor="center")

        # Add vertical scrollbar
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Bind row selection to populate form
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    # ---------- CRUD METHODS ----------
    def add_book(self):
        """Add a book with validation."""
        title = self.entries["Book Title *"].get().strip()
        author = self.entries["Author *"].get().strip()
        isbn = self.entries["ISBN *"].get().strip()
        genre = self.entries["Genre"].get().strip()
        availability = self.availability_var.get()

        # Validate required fields
        if not title or not author or not isbn:
            messagebox.showerror("Error", "Title, Author, and ISBN are required!")
            return

        try:
            db.create_book(title, author, isbn, genre, availability)
            messagebox.showinfo("Success", "Book added successfully!")
            self.view_books()   # Refresh table
            self.clear_form()   # Clear form after adding
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def view_books(self):
        """Display all books in the table."""
        # Clear existing rows
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Insert books from database
        for book in db.read_books():
            self.tree.insert("", tk.END, values=(book["id"], book["title"], book["author"],
                                                 book["isbn"], book["genre"], book["availability"]))

    def search_books(self):
        """Search books and show results or info message if none found."""
        query = self.search_var.get().strip()
        if not query:
            self.view_books()  # Show all if query empty
            return

        results = db.search_books_db(query)
        # Clear table
        for item in self.tree.get_children():
            self.tree.delete(item)

        if results:
            for book in results:
                self.tree.insert("", tk.END, values=(book["id"], book["title"], book["author"],
                                                     book["isbn"], book["genre"], book["availability"]))
        else:
            messagebox.showinfo("No Results", f"No books found matching '{query}'.")

    def update_book(self):
        """Update selected book with validation."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a book to update!")
            return
        book_id = self.tree.item(selected[0], "values")[0]

        title = self.entries["Book Title *"].get().strip()
        author = self.entries["Author *"].get().strip()
        isbn = self.entries["ISBN *"].get().strip()

        if not title or not author or not isbn:
            messagebox.showerror("Error", "Title, Author, and ISBN are required!")
            return

        db.update_book(book_id, title, author, isbn,
                       self.entries["Genre"].get().strip(),
                       self.availability_var.get())
        messagebox.showinfo("Success", "Book updated successfully!")
        self.view_books()  # Refresh table

    def delete_book(self):
        """Delete selected book from database."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a book to delete!")
            return
        book_id = self.tree.item(selected[0], "values")[0]
        db.delete_book(book_id)
        messagebox.showinfo("Deleted", "Book deleted successfully!")
        self.view_books()  # Refresh table

    def clear_form(self):
        """Clear all form fields and reset table selection."""
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.availability_var.set("Available")  # Reset dropdown
        self.tree.selection_remove(self.tree.selection())  # Deselect table row

    def on_tree_select(self, event):
        """Populate form fields when selecting a row in the table."""
        sel = self.tree.selection()
        if sel:
            values = self.tree.item(sel[0], "values")
            self.entries["Book Title *"].delete(0, tk.END); self.entries["Book Title *"].insert(0, values[1])
            self.entries["Author *"].delete(0, tk.END); self.entries["Author *"].insert(0, values[2])
            self.entries["ISBN *"].delete(0, tk.END); self.entries["ISBN *"].insert(0, values[3])
            self.entries["Genre"].delete(0, tk.END); self.entries["Genre"].insert(0, values[4])
            self.availability_var.set(values[5])

    def quit_app(self):
        """Exit application with confirmation dialog."""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.destroy()

if __name__ == "__main__":
    app = BookManagerApp()
    app.mainloop()
