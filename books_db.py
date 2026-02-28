# books_db.py
import sqlite3

# Database file name
DB_FILE = "library.db"


def init_db():
    """Initialize the database and create the 'books' table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)  # Connect to SQLite database (creates file if not exists)
    cursor = conn.cursor()  # Create a cursor object to execute SQL commands
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  # Unique ID for each book, auto-incremented
            title TEXT NOT NULL,                   # Book title (required)
            author TEXT NOT NULL,                  # Author name (required)
            isbn TEXT UNIQUE NOT NULL,             # ISBN number (required and unique)
            genre TEXT,                            # Genre of the book (optional)
            availability TEXT                      # Availability status (Available/Not Available)
        )
    """)
    conn.commit()  # Save changes
    conn.close()  # Close the connection


def create_book(title, author, isbn, genre, availability):
    """Insert a new book into the database.

    Raises:
        ValueError: If a book with the same ISBN already exists.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO books (title, author, isbn, genre, availability) VALUES (?, ?, ?, ?, ?)",
            (title, author, isbn, genre, availability)
        )
        conn.commit()  # Save changes
    except sqlite3.IntegrityError:
        # Raised if ISBN is not unique
        raise ValueError("ISBN already exists!")
    finally:
        conn.close()  # Ensure connection is closed even if error occurs


def read_books():
    """Retrieve all books from the database.

    Returns:
        list of sqlite3.Row: Each row represents a book.
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Enable dictionary-like access (row["title"])
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books")
    rows = cursor.fetchall()  # Fetch all rows
    conn.close()
    return rows


def update_book(book_id, title, author, isbn, genre, availability):
    """Update an existing book's information by its ID.

    Args:
        book_id (int): ID of the book to update.
        title (str): New title.
        author (str): New author.
        isbn (str): New ISBN.
        genre (str): New genre.
        availability (str): New availability status.
    """
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
    """Delete a book from the database by its ID.

    Args:
        book_id (int): ID of the book to delete.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books WHERE id=?", (book_id,))
    conn.commit()
    conn.close()


def search_books_db(query):
    """Search for books by title, author, or ISBN containing the query string.

    Args:
        query (str): Search string.

    Returns:
        list of sqlite3.Row: Books matching the search query.
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Enable dictionary-like access
    cursor = conn.cursor()
    query_like = f"%{query}%"  # Use wildcards for partial matching
    cursor.execute("""
        SELECT * FROM books
        WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ?
    """, (query_like, query_like, query_like))
    rows = cursor.fetchall()
    conn.close()
    return rows
