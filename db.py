import sqlite3
from pathlib import Path

# Database location
DB_PATH = Path("data/vigil.db")


def get_connection():
    """Create and return a connection to the VIGIL database."""
    DB_PATH.parent.mkdir(exist_ok=True)
    return sqlite3.connect(DB_PATH)


def initialize_database():
    """Create the voters table if it doesn't already exist."""
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS voters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            face_registered INTEGER DEFAULT 0,
            has_voted INTEGER DEFAULT 0
        )
    """)

    connection.commit()
    connection.close()


def register_voter(student_id, name):
    """Register a new student as a voter."""
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO voters (student_id, name)
            VALUES (?, ?)
        """, (student_id, name))

        connection.commit()
        print(f"✓ Voter registered: {student_id} - {name}")

    except sqlite3.IntegrityError:
        print(f"⚠ Voter ID already exists: {student_id}")

    finally:
        connection.close()


def get_voter(student_id):
    """Retrieve a voter using their student ID."""
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM voters
        WHERE student_id = ?
    """, (student_id,))

    voter = cursor.fetchone()

    connection.close()

    return voter


def mark_face_registered(student_id):
    """Mark that a voter's face has been registered."""
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE voters
        SET face_registered = 1
        WHERE student_id = ?
    """, (student_id,))

    connection.commit()
    connection.close()


def mark_as_voted(student_id):
    """Mark a voter as having voted."""
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE voters
        SET has_voted = 1
        WHERE student_id = ?
    """, (student_id,))

    connection.commit()
    connection.close()

def get_all_voters():
    """Return all registered voters."""
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM voters
    """)

    voters = cursor.fetchall()

    connection.close()

    return voters

if __name__ == "__main__":
    initialize_database()

    print("VIGIL database initialized successfully.")
    

    register_voter("25UAD105", "Adith")
    print(get_voter("25UAD105"))