import os
import sqlite3


def get_conn(filepath):
    """
    Returns a connection to the database specified by the filepath.
    Ensures the tasks table exists with the proper schema.
    """
    conn = sqlite3.connect(filepath)

    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                deadline TEXT,
                location TEXT,
                url TEXT
                    )"""
    )
    conn.commit()
    return conn


def get_all_tasks(conn):
    """
    Fetches all tasks from the database.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT title, deadline, location, url FROM tasks")
    rows = cursor.fetchall()

    tasks = []
    for row in rows:
        task = {"title": row[0], "deadline": row[1], "location": row[2], "url": row[3]}
        tasks.append(task)

    return tasks


def save_task(conn, title, deadline=None, location=None, url=None):
    """
    Saves a new task to the database with optional deadline, location, and URL.
    """
    cursor = conn.cursor()

    # Insert task into database with optional fields
    cursor.execute(
        """
        INSERT INTO tasks (title, deadline, location, url)
        VALUES (?, ?, ?, ?)
    """,
        (title, deadline, location, url),
    )

    conn.commit()


def delete_task(conn, task_title):
    """
    Deletes a task from the database by its title.
    """
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE title = ?", (task_title,))
    conn.commit()


def close_connection(conn):
    """
    Closes the database connection.
    """
    conn.close()
