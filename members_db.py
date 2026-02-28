# members_db.py
import sqlite3

# Database file name for storing member records
DB_NAME = "members.db"


def init_db():
    """Initialize the database and create the 'members' table if it does not exist."""
    conn = sqlite3.connect(DB_NAME)  # Connect to SQLite database (creates file if not exists)
    cursor = conn.cursor()  # Create a cursor object to execute SQL commands
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS members (
            membership_id TEXT PRIMARY KEY,   # Unique membership ID for each member
            name TEXT NOT NULL,               # Member's first name (required)
            surname TEXT NOT NULL,            # Member's surname (required)
            contact TEXT,                     # Contact info (optional)
            membership_type TEXT              # Membership type (e.g., Student, Regular, Premium)
        )
    """)
    conn.commit()  # Save changes
    conn.close()  # Close connection


def create_member(membership_id, name, surname, contact, membership_type):
    """
    Insert a new member into the database.

    Args:
        membership_id (str): Unique ID for the member.
        name (str): Member's first name.
        surname (str): Member's surname.
        contact (str): Contact details.
        membership_type (str): Membership type.

    Raises:
        ValueError: If required fields are missing or the member ID already exists.
    """
    if not membership_id or not name or not surname:
        raise ValueError("Membership ID, Name, and Surname are required.")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO members (membership_id, name, surname, contact, membership_type)
            VALUES (?, ?, ?, ?, ?)
        """, (membership_id, name, surname, contact, membership_type))
        conn.commit()  # Save changes
    except sqlite3.IntegrityError:
        # Raised if the membership_id already exists
        raise ValueError(f"Member with ID '{membership_id}' already exists.")
    finally:
        conn.close()  # Ensure connection is closed


def read_members():
    """
    Retrieve all members from the database, sorted by name.

    Returns:
        list of sqlite3.Row: Each row represents a member.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Enable dictionary-like access
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM members ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    return rows


def update_member(membership_id, name, surname, contact, membership_type):
    """
    Update an existing member's information by membership ID.

    Raises:
        ValueError: If no member with the given ID exists.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE members
        SET name=?, surname=?, contact=?, membership_type=?
        WHERE membership_id=?
    """, (name, surname, contact, membership_type, membership_id))
    if cursor.rowcount == 0:
        # No rows were updated → ID does not exist
        conn.close()
        raise ValueError(f"No member found with ID '{membership_id}'.")
    conn.commit()
    conn.close()


def delete_member(membership_id):
    """
    Delete a member from the database by membership ID.

    Raises:
        ValueError: If no member with the given ID exists.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM members WHERE membership_id=?", (membership_id,))
    if cursor.rowcount == 0:
        # No rows were deleted → ID does not exist
        conn.close()
        raise ValueError(f"No member found with ID '{membership_id}'.")
    conn.commit()
    conn.close()


def search_members(query):
    """
    Search for members by ID, name, surname, contact, or membership type.

    Args:
        query (str): Search string.

    Returns:
        list of sqlite3.Row: Members matching the search query.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    like_q = f"%{query}%"  # Wildcards for partial matching
    cursor.execute("""
        SELECT * FROM members
        WHERE membership_id LIKE ? OR name LIKE ? OR surname LIKE ? OR contact LIKE ? OR membership_type LIKE ?
        ORDER BY name
    """, (like_q, like_q, like_q, like_q, like_q))
    rows = cursor.fetchall()
    conn.close()
    return rows


# ---------- TESTING / STANDALONE EXECUTION ----------
if __name__ == "__main__":
    init_db()
    print("Database initialized. Current members:")
    for m in read_members():
        print(dict(m))  # Print each member as a dictionary for readability
