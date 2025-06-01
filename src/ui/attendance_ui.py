import tkinter as tk
from tkinter import messagebox
from src.logic.attendance import AttendanceManager

class AttendanceUI:
    def __init__(self, parent):
        self.parent = parent
        self.attendance_mgr = AttendanceManager()

        # Tiêu đề
        tk.Label(self.parent, text="CHẤM CÔNG", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=3, pady=10)

        # Form nhập liệu
        tk.Label(self.parent, text="Mã NV:").grid(row=1, column=0, padx=5, pady=5)
        self.attendance_id_entry = tk.Entry(self.parent)
        self.attendance_id_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.parent, text="Ngày:").grid(row=2, column=0, padx=5, pady=5)
        self.date_entry = tk.Entry(self.parent)
        self.date_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(self.parent, text="Thời gian vào:").grid(row=3, column=0, padx=5, pady=5)
        self.time_in_entry = tk.Entry(self.parent)
        self.time_in_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(self.parent, text="Thời gian ra:").grid(row=4, column=0, padx=5, pady=5)
        self.time_out_entry = tk.Entry(self.parent)
        self.time_out_entry.grid(row=4, column=1, padx=5, pady=5)

        tk.Button(self.parent, text="Ghi chấm công", command=self.add_attendance).grid(row=5, column=1, padx=5, pady=5)

        # Bảng hiển thị danh sách chấm công
        self.attendance_listbox = tk.Listbox(self.parent, width=80, height=10)
        self.attendance_listbox.grid(row=6, column=0, columnspan=3, padx=5, pady=10)

        # Hiển thị danh sách ban đầu
        self.load_attendance()

    def load_attendance(self):
        self.attendance_listbox.delete(0, tk.END)
        self.attendance_mgr.db.execute("SELECT * FROM Attendance")
        for row in self.attendance_mgr.db.fetch_all():
            self.attendance_listbox.insert(tk.END, f"{row[0]} - {row[1]} - {row[2]} - {row[3]} - {row[4]}")

    def add_attendance(self):
        employee_id = self.attendance_id_entry.get()
        date = self.date_entry.get()
        time_in = self.time_in_entry.get()
        time_out = self.time_out_entry.get()
        if employee_id and date and time_in and time_out:
            self.attendance_mgr.add_attendance(employee_id, date, time_in, time_out)
            messagebox.showinfo("Thành công", "Ghi chấm công thành công!")
            self.clear_entries()
            self.load_attendance()
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin chấm công!")

    def clear_entries(self):
        self.attendance_id_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.time_in_entry.delete(0, tk.END)
        self.time_out_entry.delete(0, tk.END)