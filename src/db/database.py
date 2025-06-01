import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect("hr_database.db")
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Employees (
                id TEXT PRIMARY KEY, name TEXT, department TEXT, salary REAL, join_date TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Attendance (
                attendance_id TEXT PRIMARY KEY, employee_id TEXT, date TEXT, time_in TEXT, time_out TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Candidates (
                candidate_id TEXT PRIMARY KEY, name TEXT, email TEXT, position TEXT, application_date TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Feedback (
                feedback_id TEXT PRIMARY KEY, employee_id TEXT, feedback TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS AdminResponses (
                response_id TEXT PRIMARY KEY, feedback_id TEXT, response TEXT
            )
        """)
        self.conn.commit()

    def execute(self, query, params=None):
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        self.conn.commit()

    def fetch_all(self):
        return self.cursor.fetchall()

    def __del__(self):
        self.conn.close()