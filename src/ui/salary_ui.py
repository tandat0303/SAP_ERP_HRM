import tkinter as tk
from src.logic.salary import SalaryManager

class SalaryUI:
    def __init__(self, parent):
        self.parent = parent
        self.salary_mgr = SalaryManager()

        # Tiêu đề
        tk.Label(self.parent, text="BÁO CÁO LƯƠNG", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        tk.Button(self.parent, text="Tạo báo cáo", command=self.generate_salary_report).grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        # Bảng hiển thị báo cáo lương
        self.salary_listbox = tk.Listbox(self.parent, width=80, height=10)
        self.salary_listbox.grid(row=2, column=0, columnspan=2, padx=5, pady=10)

    def generate_salary_report(self):
        self.salary_listbox.delete(0, tk.END)
        report = self.salary_mgr.generate_salary_report()
        for line in report:
            self.salary_listbox.insert(tk.END, line)