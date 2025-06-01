import tkinter as tk
from tkinter import messagebox
from src.logic.employee import EmployeeManager
from src.logic.attendance import AttendanceManager
from src.logic.candidate import CandidateManager
from src.logic.feedback import FeedbackManager
from src.logic.salary import SalaryManager

class HRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quản lý nhân sự")
        self.root.geometry("800x600")

        # Khởi tạo các manager
        self.employee_mgr = EmployeeManager()
        self.attendance_mgr = AttendanceManager()
        self.candidate_mgr = CandidateManager()
        self.feedback_mgr = FeedbackManager()
        self.salary_mgr = SalaryManager()

        # Giao diện
        tk.Label(root, text="Mã NV:").grid(row=0, column=0, padx=5, pady=5)
        self.id_entry = tk.Entry(root)
        self.id_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(root, text="Họ tên:").grid(row=1, column=0, padx=5, pady=5)
        self.name_entry = tk.Entry(root)
        self.name_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(root, text="Phòng ban:").grid(row=2, column=0, padx=5, pady=5)
        self.dept_entry = tk.Entry(root)
        self.dept_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(root, text="Lương:").grid(row=3, column=0, padx=5, pady=5)
        self.salary_entry = tk.Entry(root)
        self.salary_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(root, text="Ngày vào làm:").grid(row=4, column=0, padx=5, pady=5)
        self.join_date_entry = tk.Entry(root)
        self.join_date_entry.grid(row=4, column=1, padx=5, pady=5)

        tk.Button(root, text="Thêm NV", command=self.add_employee).grid(row=5, column=0, padx=5, pady=5)
        tk.Button(root, text="Sửa NV", command=self.update_employee).grid(row=5, column=1, padx=5, pady=5)
        tk.Button(root, text="Xóa NV", command=self.delete_employee).grid(row=5, column=2, padx=5, pady=5)

        tk.Label(root, text="Tìm kiếm (Mã/Tên):").grid(row=6, column=0, padx=5, pady=5)
        self.search_entry = tk.Entry(root)
        self.search_entry.grid(row=6, column=1, padx=5, pady=5)
        tk.Button(root, text="Tìm", command=self.search_employee).grid(row=6, column=2, padx=5, pady=5)

        # Chấm công
        tk.Label(root, text="Chấm công - Mã NV:").grid(row=7, column=0, padx=5, pady=5)
        self.attendance_id_entry = tk.Entry(root)
        self.attendance_id_entry.grid(row=7, column=1, padx=5, pady=5)

        tk.Label(root, text="Ngày:").grid(row=8, column=0, padx=5, pady=5)
        self.date_entry = tk.Entry(root)
        self.date_entry.grid(row=8, column=1, padx=5, pady=5)

        tk.Label(root, text="Thời gian vào:").grid(row=9, column=0, padx=5, pady=5)
        self.time_in_entry = tk.Entry(root)
        self.time_in_entry.grid(row=9, column=1, padx=5, pady=5)

        tk.Label(root, text="Thời gian ra:").grid(row=10, column=0, padx=5, pady=5)
        self.time_out_entry = tk.Entry(root)
        self.time_out_entry.grid(row=10, column=1, padx=5, pady=5)

        tk.Button(root, text="Ghi chấm công", command=self.add_attendance).grid(row=11, column=1, padx=5, pady=5)

        # Ứng viên
        tk.Label(root, text="Ứng viên - Tên:").grid(row=12, column=0, padx=5, pady=5)
        self.candidate_name_entry = tk.Entry(root)
        self.candidate_name_entry.grid(row=12, column=1, padx=5, pady=5)

        tk.Label(root, text="Email:").grid(row=13, column=0, padx=5, pady=5)
        self.candidate_email_entry = tk.Entry(root)
        self.candidate_email_entry.grid(row=13, column=1, padx=5, pady=5)

        tk.Label(root, text="Vị trí ứng tuyển:").grid(row=14, column=0, padx=5, pady=5)
        self.candidate_position_entry = tk.Entry(root)
        self.candidate_position_entry.grid(row=14, column=1, padx=5, pady=5)

        tk.Button(root, text="Thêm ứng viên", command=self.add_candidate).grid(row=15, column=1, padx=5, pady=5)

        # Phản hồi
        tk.Label(root, text="Phản hồi:").grid(row=16, column=0, padx=5, pady=5)
        self.feedback_entry = tk.Entry(root)
        self.feedback_entry.grid(row=16, column=1, padx=5, pady=5)
        tk.Button(root, text="Gửi phản hồi", command=self.add_feedback).grid(row=16, column=2, padx=5, pady=5)

        tk.Label(root, text="Trả lời phản hồi:").grid(row=17, column=0, padx=5, pady=5)
        self.response_entry = tk.Entry(root)
        self.response_entry.grid(row=17, column=1, padx=5, pady=5)
        tk.Button(root, text="Gửi trả lời", command=self.add_response).grid(row=17, column=2, padx=5, pady=5)

        # Báo cáo lương
        tk.Button(root, text="Báo cáo lương", command=self.generate_salary_report).grid(row=18, column=1, padx=5, pady=5)

        # Danh sách kết quả
        self.result_listbox = tk.Listbox(root, width=80, height=10)
        self.result_listbox.grid(row=19, column=0, columnspan=3, padx=5, pady=5)
        self.result_listbox.bind('<<ListboxSelect>>', self.show_feedback_and_response)

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
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin!")

    def delete_employee(self):
        id = self.id_entry.get()
        if id:
            self.employee_mgr.delete_employee(id)
            messagebox.showinfo("Thành công", "Xóa nhân viên thành công!")
            self.clear_entries()
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập mã nhân viên!")

    def search_employee(self):
        search_term = self.search_entry.get()
        self.result_listbox.delete(0, tk.END)
        results = self.employee_mgr.search_employee(search_term)
        for row in results:
            self.result_listbox.insert(tk.END, f"{row[0]} - {row[1]} - {row[2]} - {row[3]} - {row[4]}")

    def add_attendance(self):
        employee_id = self.attendance_id_entry.get()
        date = self.date_entry.get()
        time_in = self.time_in_entry.get()
        time_out = self.time_out_entry.get()
        if employee_id and date and time_in and time_out:
            self.attendance_mgr.add_attendance(employee_id, date, time_in, time_out)
            messagebox.showinfo("Thành công", "Ghi chấm công thành công!")
            self.attendance_id_entry.delete(0, tk.END)
            self.date_entry.delete(0, tk.END)
            self.time_in_entry.delete(0, tk.END)
            self.time_out_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin chấm công!")

    def add_candidate(self):
        name = self.candidate_name_entry.get()
        email = self.candidate_email_entry.get()
        position = self.candidate_position_entry.get()
        if name and email and position:
            self.candidate_mgr.add_candidate(name, email, position)
            messagebox.showinfo("Thành công", "Thêm ứng viên thành công!")
            self.candidate_name_entry.delete(0, tk.END)
            self.candidate_email_entry.delete(0, tk.END)
            self.candidate_position_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin ứng viên!")

    def add_feedback(self):
        employee_id = self.id_entry.get()
        feedback = self.feedback_entry.get()
        if employee_id and feedback:
            self.feedback_mgr.add_feedback(employee_id, feedback)
            messagebox.showinfo("Thành công", "Gửi phản hồi thành công!")
            self.feedback_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập mã nhân viên và phản hồi!")

    def add_response(self):
        selected = self.result_listbox.get(tk.ACTIVE)
        if selected:
            feedback_id = selected.split(" - ")[0]
            response = self.response_entry.get()
            if response:
                self.feedback_mgr.add_response(feedback_id, response)
                messagebox.showinfo("Thành công", "Gửi trả lời thành công!")
                self.response_entry.delete(0, tk.END)
            else:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập câu trả lời!")
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn phản hồi để trả lời!")

    def show_feedback_and_response(self, event):
        self.result_listbox.delete(0, tk.END)
        feedbacks = self.feedback_mgr.get_all_feedbacks_with_responses()
        for feedback in feedbacks:
            self.result_listbox.insert(tk.END, f"{feedback[0]} - {feedback[1]} - {feedback[2]} - Trả lời: {feedback[3]}")

    def generate_salary_report(self):
        self.result_listbox.delete(0, tk.END)
        report = self.salary_mgr.generate_salary_report()
        for line in report:
            self.result_listbox.insert(tk.END, line)

    def clear_entries(self):
        self.id_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.dept_entry.delete(0, tk.END)
        self.salary_entry.delete(0, tk.END)
        self.join_date_entry.delete(0, tk.END)
        self.attendance_id_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.time_in_entry.delete(0, tk.END)
        self.time_out_entry.delete(0, tk.END)
        self.candidate_name_entry.delete(0, tk.END)
        self.candidate_email_entry.delete(0, tk.END)
        self.candidate_position_entry.delete(0, tk.END)
        self.feedback_entry.delete(0, tk.END)
        self.response_entry.delete(0, tk.END)