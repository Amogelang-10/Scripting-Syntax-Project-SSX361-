# members_gui.py
import tkinter as tk
from tkinter import messagebox, ttk
import re
import members_db as db  # Backend module for database operations

class MemberManagerApp(tk.Toplevel):
    def __init__(self, master=None):
        """
        Initialize the Member Manager GUI window.
        Sets up colors, initializes database, builds widgets, and populates the table.
        """
        super().__init__(master)
        # --- Colors ---
        self.bg_color = "#FAF3E0"       # Background color for main window
        self.button_color = "#A3C4BC"   # Default button color
        self.button_active = "#7AA69E"  # Button hover/active color
        self.text_color = "#333333"     # Text color
        self.accent1 = "#FFD580"        # Selection accent for table
        self.accent2 = "#FFFFFF"        # Table background

        self.configure(bg=self.bg_color)
        db.init_db()  # Ensure the members table exists
        self._build_widgets()  # Build form, buttons, search, and table
        self.refresh_treeview()  # Populate the table with members

    def _build_widgets(self):
        """Build all GUI components: form entries, buttons, search, and table."""
        frm = tk.Frame(self, padx=10, pady=10, bg=self.bg_color)
        frm.pack(side=tk.TOP, fill=tk.X)

        bold_font = ("TkDefaultFont", 10, "bold")

        # --- Form Labels and Entry Fields ---
        labels = ["Membership ID *", "Name *", "Surname *", "Contact", "Membership Type"]
        self.entries = {}  # Dictionary to store Entry widgets
        for i, label in enumerate(labels):
            tk.Label(frm, text=label, bg=self.bg_color, fg=self.text_color, font=bold_font).grid(row=i, column=0, sticky="w")
            entry = tk.Entry(frm, width=25, fg=self.text_color)
            entry.grid(row=i, column=1, pady=4)
            self.entries[label] = entry

        # --- Buttons ---
        btn_frame = tk.Frame(frm, bg=self.bg_color)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)

        buttons = [
            ("Add Member", self.add_member),
            ("Update Member", self.update_member),
            ("Delete Member", self.delete_member),
            ("Clear Fields", self.clear_form),
            ("Exit", self.quit_app)
        ]

        # Create buttons with consistent styling
        for text, cmd in buttons:
            btn = tk.Button(btn_frame, text=text, width=15, command=cmd,
                            bg=self.button_color, fg=self.text_color, activebackground=self.button_active)
            btn.pack(side=tk.LEFT, padx=5)

        # --- Search Section ---
        search_frm = tk.Frame(self, padx=10, pady=5, bg=self.bg_color)
        search_frm.pack(fill=tk.X)
        tk.Label(search_frm, text="Search:", bg=self.bg_color, fg=self.text_color, font=bold_font).pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        tk.Entry(search_frm, textvariable=self.search_var, fg=self.text_color).pack(side=tk.LEFT, padx=5)
        tk.Button(search_frm, text="Search", command=self.search_members,
                  bg=self.button_color, fg=self.text_color, activebackground=self.button_active).pack(side=tk.LEFT)
        tk.Button(search_frm, text="Show All", command=self.refresh_treeview,
                  bg=self.button_color, fg=self.text_color, activebackground=self.button_active).pack(side=tk.LEFT, padx=5)

        # --- Table / Treeview ---
        columns = ("membership_id", "name", "surname", "contact", "membership_type")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
        self.tree.column("membership_id", width=100, anchor="center")
        self.tree.column("name", width=150)
        self.tree.column("surname", width=150)
        self.tree.column("contact", width=150)
        self.tree.column("membership_type", width=120, anchor="center")

        # Style table
        style = ttk.Style()
        style.configure("Treeview", background=self.accent2, foreground=self.text_color, fieldbackground=self.accent2)
        style.map("Treeview", background=[('selected', self.accent1)], foreground=[('selected', self.text_color)])

        # Scrollbar for table
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    # ---------- VALIDATION & CRUD METHODS ----------
    def validate_member(self, member_id, name, surname, contact):
        """Validate member input fields. Raises ValueError if invalid."""
        if not member_id or not name or not surname:
            raise ValueError("Membership ID, Name, and Surname are required!")

        # Membership ID must be alphanumeric
        if not re.match(r"^[A-Za-z0-9]+$", member_id):
            raise ValueError("Membership ID must be alphanumeric!")

        # Names can contain letters, spaces, hyphens
        if not re.match(r"^[A-Za-z\s\-]+$", name):
            raise ValueError("Name can only contain letters, spaces, or hyphens!")
        if not re.match(r"^[A-Za-z\s\-]+$", surname):
            raise ValueError("Surname can only contain letters, spaces, or hyphens!")

        # Contact: 10-digit phone or valid email
        if contact:
            phone_pattern = r"^\d{10}$"
            email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
            if not (re.match(phone_pattern, contact) or re.match(email_pattern, contact)):
                raise ValueError("Contact must be a 10-digit phone or a valid email!")

    def add_member(self):
        """Add a new member to the database after validation."""
        try:
            mid = self.entries["Membership ID *"].get().strip()
            name = self.entries["Name *"].get().strip()
            surname = self.entries["Surname *"].get().strip()
            contact = self.entries["Contact"].get().strip()
            mtype = self.entries["Membership Type"].get().strip()

            self.validate_member(mid, name, surname, contact)
            db.create_member(mid, name, surname, contact, mtype)
            self.refresh_treeview()
            self.clear_form()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def update_member(self):
        """Update selected member after validation."""
        try:
            mid = self.entries["Membership ID *"].get().strip()
            name = self.entries["Name *"].get().strip()
            surname = self.entries["Surname *"].get().strip()
            contact = self.entries["Contact"].get().strip()
            mtype = self.entries["Membership Type"].get().strip()

            self.validate_member(mid, name, surname, contact)
            db.update_member(mid, name, surname, contact, mtype)
            self.refresh_treeview()
            self.clear_form()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def delete_member(self):
        """Delete a member after confirmation."""
        mid = self.entries["Membership ID *"].get().strip()
        if not mid:
            messagebox.showerror("Error", "Enter Membership ID to delete.")
            return
        if messagebox.askyesno("Confirm Delete", f"Delete member '{mid}'?"):
            try:
                db.delete_member(mid)
                self.refresh_treeview()
                self.clear_form()
            except ValueError as e:
                messagebox.showerror("Error", str(e))

    # ---------- HELPER METHODS ----------
    def search_members(self):
        """Search members by query and update table."""
        q = self.search_var.get().strip()
        if not q:
            self.refresh_treeview()
            return
        self.refresh_treeview(db.search_members(q))

    def refresh_treeview(self, members=None):
        """Refresh the table with all or filtered members."""
        # Clear current table
        for item in self.tree.get_children():
            self.tree.delete(item)
        if members is None:
            members = db.read_members()
        for m in members:
            self.tree.insert("", tk.END, values=(m["membership_id"], m["name"], m["surname"], m["contact"], m["membership_type"]))

    def on_tree_select(self, event):
        """Populate form fields when a member is selected in the table."""
        sel = self.tree.selection()
        if sel:
            values = self.tree.item(sel[0], "values")
            for i, key in enumerate(self.entries.keys()):
                self.entries[key].delete(0, tk.END)
                self.entries[key].insert(0, values[i])

    def clear_form(self):
        """Clear all form inputs and deselect any table row."""
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.tree.selection_remove(self.tree.selection())

    def quit_app(self):
        """Exit the application after confirmation."""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.destroy()


# ---------- RUN APPLICATION ----------
if __name__ == "__main__":
    db.init_db()  # Ensure database is ready
    app = MemberManagerApp()
    app.mainloop()
