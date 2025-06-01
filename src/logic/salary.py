from src.db.database import Database
import datetime

class SalaryManager:
    def __init__(self):
        self.db = Database()

    def generate_salary_report(self):
        report = []
        month = datetime.datetime.now().strftime("%Y-%m")
        self.db.execute("SELECT id, name, salary FROM Employees")
        total_salary = 0
        for row in self.db.fetch_all():
            employee_id, name, salary = row
            report.append(f"{employee_id} - {name} - Lương: {salary}")
            total_salary += salary
        report.append(f"Tổng lương tháng {month}: {total_salary}")
        return report