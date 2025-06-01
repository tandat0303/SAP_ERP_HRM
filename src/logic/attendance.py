from src.db.database import Database

class AttendanceManager:
    def __init__(self):
        self.db = Database()

    def add_attendance(self, employee_id, date, time_in, time_out):
        attendance_id = f"ATT{len(self.db.fetch_all('SELECT * FROM Attendance')) + 1}"
        self.db.execute("INSERT INTO Attendance (attendance_id, employee_id, date, time_in, time_out) VALUES (?, ?, ?, ?, ?)",
                        (attendance_id, employee_id, date, time_in, time_out))