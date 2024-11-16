import os
import sqlite3


def get_conn(filepath):
    """
    Returns a connection to the database specified by the filepath
    """
    conn = sqlite3.connect(filepath)

    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS tasks
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       task TEXT NOT NULL,
                       completed BOOLEAN NOT NULL)"""
    )
    conn.commit()
    return conn


def get_all_tasks(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT task FROM tasks")
    rows = cursor.fetchall()
    return [row[0] for row in rows]


def save_task(conn, task):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (task, completed) VALUES (?, ?)", (task, False))
    conn.commit()


def delete_task(conn, task_text):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE task = ?", (task_text,))
    conn.commit()


def close_connection(conn):
    conn.close()
