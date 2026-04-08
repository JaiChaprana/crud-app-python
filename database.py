import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name="student_system.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.init_tables()

    def init_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                                sap TEXT PRIMARY KEY, name TEXT, course TEXT,
                                program TEXT, age INTEGER, semester INTEGER, email TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS logs (
                                action TEXT, details TEXT, timestamp TEXT)''')
        self.conn.commit()

    def get_student(self, sap):
        self.cursor.execute("SELECT * FROM students WHERE sap=?", (sap,))
        return self.cursor.fetchone()

    def search_students(self, query):
        q = f"%{query}%"
        self.cursor.execute("SELECT * FROM students WHERE name LIKE ? OR sap LIKE ?", (q, q))
        return self.cursor.fetchall()

    def log_action(self, user, action, details):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO logs VALUES (?, ?, ?)",
                            (action, f"[{user}] {details}", timestamp))
        self.conn.commit()
