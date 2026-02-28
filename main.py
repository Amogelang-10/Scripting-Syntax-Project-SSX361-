# main.py
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# Database file path
DB_FILE = "library.db"

# ---------- DATABASE INITIALIZATION ----------
def init_db():
    """Initialize the database and create tables if they do not exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Create 'books' table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT UNIQUE NOT NULL,
            genre TEXT,
            availability TEXT
        )
    """)
    # Create 'members' table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS members (
            membership_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            surname TEXT NOT NULL,
            contact TEXT,
            membership_type TEXT
        )
    """)
    conn.commit()
    conn.close()

# ---------- BOOK FUNCTIONS ----------
def create_book(title, author, isbn, genre, availability):
    """Add a new book to the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO books (title, author, isbn, genre, availability) VALUES (?, ?, ?, ?, ?)",
            (title, author, isbn, genre, availability)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise ValueError("ISBN already exists!")  # Prevent duplicate ISBN
    finally:
        conn.close()

def read_books():
    """Return a list of all books in the database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Access columns by name
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_book(book_id, title, author, isbn, genre, availability):
    """Update an existing book's information."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE books
        SET title=?, author=?, isbn=?, genre=?, availability=?
        WHERE id=?
    """, (title, author, isbn, genre, availability, book_id))
    conn.commit()
    conn.close()

def delete_book(book_id):
    """Delete a book from the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books WHERE id=?", (book_id,))
    conn.commit()
    conn.close()

def search_books(query):
    """Search books by title, author, or ISBN."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    q = f"%{query}%"
    cursor.execute("""
        SELECT * FROM books
        WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ?
    """, (q, q, q))
    rows = cursor.fetchall()
    conn.close()
    return rows

# ---------- MEMBER FUNCTIONS ----------
def create_member(mid, name, surname, contact, mtype):
    """Add a new member to the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO members (membership_id, name, surname, contact, membership_type) VALUES (?, ?, ?, ?, ?)",
            (mid, name, surname, contact, mtype)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise ValueError("Membership ID already exists!")
    finally:
        conn.close()

def read_members():
    """Return a list of all members."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM members")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_member(mid, name, surname, contact, mtype):
    """Update member information."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE members
        SET name=?, surname=?, contact=?, membership_type=?
        WHERE membership_id=?
    """, (name, surname, contact, mtype, mid))
    conn.commit()
    conn.close()

def delete_member(mid):
    """Delete a member from the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM members WHERE membership_id=?", (mid,))
    conn.commit()
    conn.close()

def search_members(query):
    """Search members by ID, name, or surname."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    q = f"%{query}%"
    cursor.execute("""
        SELECT * FROM members
        WHERE membership_id LIKE ? OR name LIKE ? OR surname LIKE ?
    """, (q, q, q))
    rows = cursor.fetchall()
    conn.close()
    return rows

# ---------- BOOK MANAGER GUI ----------
class BookManagerApp(tk.Toplevel):
    """Tkinter window to manage books (Add, Update, Delete, Search)."""
    def __init__(self, master=None):
        super().__init__(master)
        self.title("📚 Book Management")
        self.geometry("950x550")
        self.configure(bg="#BD9E89")
        self.entries = {}  # Store entry widgets
        self.availability_var = tk.StringVar(value="Available")
        self.search_var = tk.StringVar()
        self._build_widgets()
        self.view_books()

    def _build_widgets(self):
        """Create the form, buttons, search bar, and table."""
        # Form frame
        form_frame = tk.Frame(self, bg="#BD9E89", padx=10, pady=10)
        form_frame.pack(side=tk.TOP, fill=tk.X)
        labels = ["Book Title *", "Author *", "ISBN *", "Genre", "Availability"]
        for i, label in enumerate(labels):
            tk.Label(form_frame, text=label, bg="#BD9E89", fg="#545454",
                     font=("Arial", 10, "bold")).grid(row=i, column=0, sticky="w", pady=5)
            if label == "Availability":
                combo = ttk.Combobox(form_frame, textvariable=self.availability_var,
                                     values=["Available", "Not Available"], state="readonly", width=37)
                combo.grid(row=i, column=1, pady=5)
            else:
                entry = tk.Entry(form_frame, width=40)
                entry.grid(row=i, column=1, pady=5)
                self.entries[label] = entry

        # Buttons
        btn_frame = tk.Frame(form_frame, bg="#BD9E89")
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)
        for text, cmd in [("Add", self.add_book), ("Update", self.update_book),
                          ("Delete", self.delete_book), ("Clear", self.clear_form),
                          ("Exit", self.quit_app)]:
            tk.Button(btn_frame, text=text, command=cmd,
                      bg="#F1ECE5", fg="#545454", font=("Arial", 10, "bold"),
                      width=12, relief="raised", activebackground="#CED1D4").pack(side=tk.LEFT, padx=5)

        # Search frame
        search_frame = tk.Frame(self, bg="#BD9E89", padx=10, pady=5)
        search_frame.pack(fill=tk.X)
        tk.Label(search_frame, text="Search Title/Author/ISBN:", bg="#BD9E89", fg="#545454").pack(side=tk.LEFT)
        tk.Entry(search_frame, textvariable=self.search_var, width=40).pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Search", command=self.search_books,
                  bg="#F1ECE5", fg="#545454", activebackground="#CED1D4").pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Show All", command=self.view_books,
                  bg="#F1ECE5", fg="#545454", activebackground="#CED1D4").pack(side=tk.LEFT, padx=5)

        # Table frame
        table_frame = tk.Frame(self, bg="#E4C9B2", padx=10, pady=10)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        columns = ("id", "title", "author", "isbn", "genre", "availability")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"), foreground="#545454")
        style.configure("Treeview", font=("Arial", 10), rowheight=25)
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=140, anchor="center")
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    # ---------- BOOK CRUD METHODS ----------
    def add_book(self):
        """Add book from form to database."""
        title = self.entries["Book Title *"].get().strip()
        author = self.entries["Author *"].get().strip()
        isbn = self.entries["ISBN *"].get().strip()
        genre = self.entries["Genre"].get().strip()
        availability = self.availability_var.get()
        if not title or not author or not isbn:
            messagebox.showerror("Error", "Title, Author, ISBN required!")
            return
        try:
            create_book(title, author, isbn, genre, availability)
            messagebox.showinfo("Success", "Book added successfully!")
            self.view_books()
            self.clear_form()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def view_books(self):
        """Display all books in the table."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        for b in read_books():
            self.tree.insert("", tk.END, values=(b["id"], b["title"], b["author"], b["isbn"], b["genre"], b["availability"]))

    def search_books(self):
        """Search books and display results in table."""
        q = self.search_var.get().strip()
        if not q:
            self.view_books()
            return
        results = search_books(q)
        for item in self.tree.get_children():
            self.tree.delete(item)
        if results:
            for b in results:
                self.tree.insert("", tk.END, values=(b["id"], b["title"], b["author"], b["isbn"], b["genre"], b["availability"]))
        else:
            messagebox.showinfo("No results", f"No books found matching '{q}'")

    def update_book(self):
        """Update selected book with form values."""
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Select a book!")
            return
        book_id = self.tree.item(sel[0], "values")[0]
        title = self.entries["Book Title *"].get().strip()
        author = self.entries["Author *"].get().strip()
        isbn = self.entries["ISBN *"].get().strip()
        if not title or not author or not isbn:
            messagebox.showerror("Error", "Title, Author, ISBN required!")
            return
        update_book(book_id, title, author, isbn,
                    self.entries["Genre"].get().strip(),
                    self.availability_var.get())
        messagebox.showinfo("Success", "Book updated successfully!")
        self.view_books()

    def delete_book(self):
        """Delete selected book."""
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Select a book!")
            return
        book_id = self.tree.item(sel[0], "values")[0]
        delete_book(book_id)
        messagebox.showinfo("Deleted", "Book deleted successfully!")
        self.view_books()

    def clear_form(self):
        """Clear all form fields and reset availability."""
        for e in self.entries.values():
            e.delete(0, tk.END)
        self.availability_var.set("Available")
        self.tree.selection_remove(self.tree.selection())

    def on_tree_select(self, event):
        """Populate form fields when a table row is selected."""
        sel = self.tree.selection()
        if sel:
            values = self.tree.item(sel[0], "values")
            self.entries["Book Title *"].delete(0, tk.END); self.entries["Book Title *"].insert(0, values[1])
            self.entries["Author *"].delete(0, tk.END); self.entries["Author *"].insert(0, values[2])
            self.entries["ISBN *"].delete(0, tk.END); self.entries["ISBN *"].insert(0, values[3])
            self.entries["Genre"].delete(0, tk.END); self.entries["Genre"].insert(0, values[4])
            self.availability_var.set(values[5])

    def quit_app(self):
        """Close the book manager window."""
        if messagebox.askyesno("Exit", "Close Book Manager?"):
            self.destroy()

# ---------- MEMBER MANAGER GUI ----------
class MemberManagerApp(tk.Toplevel):
    """Tkinter window to manage members (Add, Update, Delete, Search)."""
    def __init__(self, master=None):
        super().__init__(master)
        self.title("👤 Member Management")
        self.geometry("900x500")
        self.configure(bg="#BD9E89")
        self.entries = {}
        self.membership_type_var = tk.StringVar(value="Regular")
        self.search_var = tk.StringVar()
        self._build_widgets()
        self.view_members()

    def _build_widgets(self):
        """Create member form, buttons, search bar, and table."""
        form_frame = tk.Frame(self, bg="#BD9E89", padx=10, pady=10)
        form_frame.pack(side=tk.TOP, fill=tk.X)
        labels = ["Membership ID *", "Name *", "Surname *", "Contact", "Membership Type"]
        for i, label in enumerate(labels):
            tk.Label(form_frame, text=label, bg="#BD9E89", fg="#545454",
                     font=("Arial", 10, "bold")).grid(row=i, column=0, sticky="w", pady=5)
            if label == "Membership Type":
                combo = ttk.Combobox(form_frame, textvariable=self.membership_type_var,
                                     values=["Student", "Regular", "Premium"], state="readonly", width=37)
                combo.grid(row=i, column=1, pady=5)
            else:
                entry = tk.Entry(form_frame, width=40)
                entry.grid(row=i, column=1, pady=5)
                self.entries[label] = entry

        # Buttons
        btn_frame = tk.Frame(form_frame, bg="#BD9E89")
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)
        for text, cmd in [("Add", self.add_member), ("Update", self.update_member),
                          ("Delete", self.delete_member), ("Clear", self.clear_form),
                          ("Exit", self.quit_app)]:
            tk.Button(btn_frame, text=text, command=cmd,
                      bg="#F1ECE5", fg="#545454", font=("Arial", 10, "bold"),
                      width=12, relief="raised", activebackground="#CED1D4").pack(side=tk.LEFT, padx=5)

        # Search frame
        search_frame = tk.Frame(self, bg="#BD9E89", padx=10, pady=5)
        search_frame.pack(fill=tk.X)
        tk.Label(search_frame, text="Search ID/Name/Surname:", bg="#BD9E89", fg="#545454").pack(side=tk.LEFT)
        tk.Entry(search_frame, textvariable=self.search_var, width=40).pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Search", command=self.search_members,
                  bg="#F1ECE5", fg="#545454", activebackground="#CED1D4").pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Show All", command=self.view_members,
                  bg="#F1ECE5", fg="#545454", activebackground="#CED1D4").pack(side=tk.LEFT, padx=5)

        # Table frame
        table_frame = tk.Frame(self, bg="#E4C9B2", padx=10, pady=10)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        columns = ("membership_id", "name", "surname", "contact", "membership_type")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"), foreground="#545454")
        style.configure("Treeview", font=("Arial", 10), rowheight=25)
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=140, anchor="center")
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    # ---------- MEMBER CRUD METHODS ----------
    def add_member(self):
        """Add a new member from form to database."""
        mid = self.entries["Membership ID *"].get().strip()
        name = self.entries["Name *"].get().strip()
        surname = self.entries["Surname *"].get().strip()
        contact = self.entries["Contact"].get().strip()
        mtype = self.membership_type_var.get()
        if not mid or not name or not surname:
            messagebox.showerror("Error", "ID, Name, Surname required!")
            return
        try:
            create_member(mid, name, surname, contact, mtype)
            messagebox.showinfo("Success", "Member added successfully!")
            self.view_members()
            self.clear_form()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def view_members(self):
        """Display all members in the table."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        for m in read_members():
            self.tree.insert("", tk.END, values=(m["membership_id"], m["name"], m["surname"], m["contact"], m["membership_type"]))

    def search_members(self):
        """Search members and display results."""
        q = self.search_var.get().strip()
        if not q:
            self.view_members()
            return
        results = search_members(q)
        for item in self.tree.get_children():
            self.tree.delete(item)
        if results:
            for m in results:
                self.tree.insert("", tk.END, values=(m["membership_id"], m["name"], m["surname"], m["contact"], m["membership_type"]))
        else:
            messagebox.showinfo("No results", f"No members found matching '{q}'")

    def update_member(self):
        """Update selected member with form values."""
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Select a member!")
            return
        mid = self.tree.item(sel[0], "values")[0]
        name = self.entries["Name *"].get().strip()
        surname = self.entries["Surname *"].get().strip()
        contact = self.entries["Contact"].get().strip()
        mtype = self.membership_type_var.get()
        if not name or not surname:
            messagebox.showerror("Error", "Name and Surname required!")
            return
        update_member(mid, name, surname, contact, mtype)
        messagebox.showinfo("Success", "Member updated successfully!")
        self.view_members()

    def delete_member(self):
        """Delete selected member."""
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Select a member!")
            return
        mid = self.tree.item(sel[0], "values")[0]
        delete_member(mid)
        messagebox.showinfo("Deleted", "Member deleted successfully!")
        self.view_members()

    def clear_form(self):
        """Clear member form fields and reset membership type."""
        for e in self.entries.values():
            e.delete(0, tk.END)
        self.membership_type_var.set("Regular")
        self.tree.selection_remove(self.tree.selection())

    def on_tree_select(self, event):
        """Populate member form when a row is selected."""
        sel = self.tree.selection()
        if sel:
            values = self.tree.item(sel[0], "values")
            self.entries["Membership ID *"].delete(0, tk.END); self.entries["Membership ID *"].insert(0, values[0])
            self.entries["Name *"].delete(0, tk.END); self.entries["Name *"].insert(0, values[1])
            self.entries["Surname *"].delete(0, tk.END); self.entries["Surname *"].insert(0, values[2])
            self.entries["Contact"].delete(0, tk.END); self.entries["Contact"].insert(0, values[3])
            self.membership_type_var.set(values[4])

    def quit_app(self):
        """Close the member manager window."""
        if messagebox.askyesno("Exit", "Close Member Manager?"):
            self.destroy()

# ---------- MAIN WINDOW ----------
class MainApp(tk.Tk):
    """Main application window to open Book and Member managers."""
    BG_COLOR = "#BD9E89"
    BTN_COLOR = "#F1ECE5"
    FG_COLOR = "#222222"
    FONT = ("Arial", 10, "bold")  # consistent font

    def __init__(self):
        super().__init__()
        self.title("📖 Library Management System")
        self.geometry("400x300")
        self.configure(bg=self.BG_COLOR)
        self._build_widgets()
        init_db()  # Initialize database when app starts

    def _build_widgets(self):
        """Build main menu buttons."""
        tk.Label(self, text="Library Management System", bg=self.BG_COLOR,
                 fg=self.FG_COLOR, font=self.FONT).pack(pady=20)
        tk.Button(self, text="Manage Books", command=self.open_books,
                  bg=self.BTN_COLOR, fg=self.FG_COLOR, width=20, height=2, font=self.FONT).pack(pady=10)
        tk.Button(self, text="Manage Members", command=self.open_members,
                  bg=self.BTN_COLOR, fg=self.FG_COLOR, width=20, height=2, font=self.FONT).pack(pady=10)
        tk.Button(self, text="Exit", command=self.quit, bg=self.BTN_COLOR,
                  fg=self.FG_COLOR, width=20, height=2, font=self.FONT).pack(pady=10)

    def open_books(self):
        """Open Book Management window."""
        BookManagerApp(self)

    def open_members(self):
        """Open Member Management window."""
        MemberManagerApp(self)

# ---------- ENTRY POINT ----------
if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
