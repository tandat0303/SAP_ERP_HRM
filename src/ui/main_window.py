import tkinter as tk
from tkinter import messagebox
from src.ui.employee_ui import EmployeeUI
from src.ui.attendance_ui import AttendanceUI
from src.ui.candidate_ui import CandidateUI
from src.ui.feedback_ui import FeedbackUI
from src.ui.salary_ui import SalaryUI

class HRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quản lý nhân sự")
        self.root.geometry("800x600")

        # Tạo menu
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # Menu chức năng
        self.function_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Chức năng", menu=self.function_menu)

        # Thêm các mục menu
        self.function_menu.add_command(label="Quản lý nhân viên", command=self.show_employee_ui)
        self.function_menu.add_command(label="Chấm công", command=self.show_attendance_ui)
        self.function_menu.add_command(label="Quản lý ứng viên", command=self.show_candidate_ui)
        self.function_menu.add_command(label="Phản hồi", command=self.show_feedback_ui)
        self.function_menu.add_command(label="Báo cáo lương", command=self.show_salary_ui)
        self.function_menu.add_separator()
        self.function_menu.add_command(label="Thoát", command=self.root.quit)

        # Frame chính để hiển thị giao diện từng chức năng
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)

        # Biến để lưu giao diện hiện tại
        self.current_ui = None

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_employee_ui(self):
        self.clear_main_frame()
        self.current_ui = EmployeeUI(self.main_frame)

    def show_attendance_ui(self):
        self.clear_main_frame()
        self.current_ui = AttendanceUI(self.main_frame)

    def show_candidate_ui(self):
        self.clear_main_frame()
        self.current_ui = CandidateUI(self.main_frame)

    def show_feedback_ui(self):
        self.clear_main_frame()
        self.current_ui = FeedbackUI(self.main_frame)

    def show_salary_ui(self):
        self.clear_main_frame()
        self.current_ui = SalaryUI(self.main_frame)