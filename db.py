import sqlite3
from pathlib import Path

DB_PATH = Path("data/vigil.db")


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def initialize_database():
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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            candidate TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES voters(student_id)
        )
    """)

    connection.commit()
    connection.close()


def register_voter(student_id, name):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO voters (student_id, name)
            VALUES (?, ?)
        """, (student_id, name))

        connection.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        connection.close()


def get_voter(student_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM voters
        WHERE student_id = ?
    """, (student_id,))

    voter = cursor.fetchone()
    connection.close()

    return voter


def get_all_voters():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM voters")

    voters = cursor.fetchall()
    connection.close()

    return voters


def mark_face_registered(student_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE voters
        SET face_registered = 1
        WHERE student_id = ?
    """, (student_id,))

    updated = cursor.rowcount > 0

    connection.commit()
    connection.close()

    return updated


def mark_as_voted(student_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE voters
        SET has_voted = 1
        WHERE student_id = ?
    """, (student_id,))

    updated = cursor.rowcount > 0

    connection.commit()
    connection.close()

    return updated


def cast_vote(student_id, candidate):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO votes (student_id, candidate)
            VALUES (?, ?)
        """, (student_id, candidate))

        cursor.execute("""
            UPDATE voters
            SET has_voted = 1
            WHERE student_id = ?
        """, (student_id,))

        connection.commit()
        return True

    except sqlite3.IntegrityError:
        connection.rollback()
        return False

    finally:
        connection.close()


def get_vote(student_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT candidate
        FROM votes
        WHERE student_id = ?
    """, (student_id,))

    vote = cursor.fetchone()
    connection.close()

    return vote


if __name__ == "__main__":
    initialize_database()
    print("VIGIL database initialized successfully.")