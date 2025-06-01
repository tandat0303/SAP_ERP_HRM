from src.db.database import Database

class EmployeeManager:
    def __init__(self):
        self.db = Database()

    def add_employee(self, id, name, dept, salary, join_date):
        self.db.execute("INSERT OR REPLACE INTO Employees (id, name, department, salary, join_date) VALUES (?, ?, ?, ?, ?)",
                        (id, name, dept, salary, join_date))

    def update_employee(self, id, name, dept, salary, join_date):
        self.db.execute("UPDATE Employees SET name=?, department=?, salary=?, join_date=? WHERE id=?",
                        (name, dept, salary, join_date, id))

    def delete_employee(self, id):
        self.db.execute("DELETE FROM Employees WHERE id=?", (id,))

    def search_employee(self, search_term):
        self.db.execute("SELECT * FROM Employees WHERE id LIKE ? OR name LIKE ?",
                        (f'%{search_term}%', f'%{search_term}%'))
        return self.db.fetch_all()