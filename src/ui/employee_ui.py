import tkinter as tk
from tkinter import messagebox
from ..logic.employee import EmployeeManager

class EmployeeUI:
    def __init__(self, parent):
        self.parent = parent
        self.employee_mgr = EmployeeManager()

        # Tiêu đề
        tk.Label(self.parent, text="QUẢN LÝ NHÂN VIÊN", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=3, pady=10)

        # Form nhập liệu
        tk.Label(self.parent, text="Mã NV:").grid(row=1, column=0, padx=5, pady=5)
        self.id_entry = tk.Entry(self.parent)
        self.id_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.parent, text="Họ tên:").grid(row=2, column=0, padx=5, pady=5)
        self.name_entry = tk.Entry(self.parent)
        self.name_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(self.parent, text="Phòng ban:").grid(row=3, column=0, padx=5, pady=5)
        self.dept_entry = tk.Entry(self.parent)
        self.dept_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(self.parent, text="Lương:").grid(row=4, column=0, padx=5, pady=5)
        self.salary_entry = tk.Entry(self.parent)
        self.salary_entry.grid(row=4, column=1, padx=5, pady=5)

        tk.Label(self.parent, text="Ngày vào làm:").grid(row=5, column=0, padx=5, pady=5)
        self.join_date_entry = tk.Entry(self.parent)
        self.join_date_entry.grid(row=5, column=1, padx=5, pady=5)

        # Nút chức năng
        tk.Button(self.parent, text="Thêm NV", command=self.add_employee).grid(row=6, column=0, padx=5, pady=5)
        tk.Button(self.parent, text="Sửa NV", command=self.update_employee).grid(row=6, column=1, padx=5, pady=5)
        tk.Button(self.parent, text="Xóa NV", command=self.delete_employee).grid(row=6, column=2, padx=5, pady=5)

        # Tìm kiếm
        tk.Label(self.parent, text="Tìm kiếm (Mã/Tên):").grid(row=7, column=0, padx=5, pady=5)
        self.search_entry = tk.Entry(self.parent)
        self.search_entry.grid(row=7, column=1, padx=5, pady=5)
        tk.Button(self.parent, text="Tìm", command=self.search_employee).grid(row=7, column=2, padx=5, pady=5)

        # Bảng hiển thị danh sách nhân viên
        self.employee_listbox = tk.Listbox(self.parent, width=80, height=10)
        self.employee_listbox.grid(row=8, column=0, columnspan=3, padx=5, pady=10)
        self.employee_listbox.bind('<<ListboxSelect>>', self.on_employee_select)

        # Hiển thị danh sách ban đầu
        self.load_employees()

    def load_employees(self):
        self.employee_listbox.delete(0, tk.END)
        self.employee_mgr.execute("SELECT * FROM Employees")
        for row in self.employee_mgr.db.fetch_all():
            self.employee_listbox.insert(tk.END, f"{row[0]} - {row[1]} - {row[2]} - {row[3]} - {row[4]}")

    def add_employee(self):
        id = self.id_entry.get()
        name = self.name_entry.get()
        dept = self.dept_entry.get()
        salary = self.salary_entry.get()
        join_date = self.join_date_entry.get()
        if id and name and dept and salary and join_date:
            try:
                self.employee_mgr.add_employee(id, name, dept, float(salary), join_date)
                messagebox.showinfo("Thành công", "Thêm nhân viên thành công!")
                self.clear_entries()
                self.load_employees()
            except ValueError:
                messagebox.showerror("Lỗi", "Mã nhân viên đã tồn tại!")
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin!")

    def update_employee(self):
        id = self.id_entry.get()
        name = self.name_entry.get()
        dept = self.dept_entry.get()
        salary = self.salary_entry.get()
        join_date = self.join_date_entry.get()
        if id and name and dept and salary and join_date:
            self.employee_mgr.update_employee(id, name, dept, float(salary), join_date)
            messagebox.showinfo("Thành công", "Cập nhật nhân viên thành công!")
            self.clear_entries()
            self.load_employees()
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin!")

    def delete_employee(self):
        id = self.id_entry.get()
        if id:
            self.employee_mgr.delete_employee(id)
            messagebox.showinfo("Thành công", "Xóa nhân viên thành công!")
            self.clear_entries()
            self.load_employees()
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập mã nhân viên!")

    def search_employee(self):
        search_term = self.search_entry.get()
        self.employee_listbox.delete(0, tk.END)
        results = self.employee_mgr.search_employee(search_term)
        for row in results:
            self.employee_listbox.insert(tk.END, f"{row[0]} - {row[1]} - {row[2]} - {row[3]} - {row[4]}")

    def on_employee_select(self, event):
        selected = self.employee_listbox.get(tk.ACTIVE)
        if selected:
            parts = selected.split(" - ")
            self.id_entry.delete(0, tk.END)
            self.id_entry.insert(0, parts[0])
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, parts[1])
            self.dept_entry.delete(0, tk.END)
            self.dept_entry.insert(0, parts[2])
            self.salary_entry.delete(0, tk.END)
            self.salary_entry.insert(0, parts[3])
            self.join_date_entry.delete(0, tk.END)
            self.join_date_entry.insert(0, parts[4])

    def clear_entries(self):
        self.id_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.dept_entry.delete(0, tk.END)
        self.salary_entry.delete(0, tk.END)
        self.join_date_entry.delete(0, tk.END)