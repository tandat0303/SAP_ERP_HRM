import tkinter as tk
from tkinter import ttk, messagebox
from src.ui.employee_ui import EmployeeUI
from src.ui.attendance_ui import AttendanceUI
from src.ui.candidate_ui import CandidateUI
from src.ui.feedback_ui import FeedbackUI
from src.ui.salary_ui import SalaryUI


class HRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hệ thống Quản lý Nhân sự")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)

        # Cấu hình style
        self.setup_styles()

        # Cấu hình layout chính
        self.setup_main_layout()

        # Tạo sidebar navigation
        self.create_sidebar()

        # Frame chính để hiển thị content
        self.main_content = ttk.Frame(self.content_frame, style="Content.TFrame")
        self.main_content.pack(fill="both", expand=True, padx=20, pady=20)

        # Biến để lưu giao diện hiện tại
        self.current_ui = None

        # Hiển thị trang chủ mặc định
        self.show_home()

    def setup_styles(self):
        """Cấu hình styles cho ứng dụng"""
        style = ttk.Style()

        # Cấu hình theme
        style.theme_use('clam')

        # Style cho sidebar
        style.configure("Sidebar.TFrame", background="#2c3e50")
        style.configure("SidebarButton.TButton",
                        background="#34495e",
                        foreground="white",
                        font=("Arial", 11),
                        padding=(20, 15))
        style.map("SidebarButton.TButton",
                  background=[('active', '#3498db'), ('pressed', '#2980b9')])

        # Style cho content area
        style.configure("Content.TFrame", background="#ecf0f1")
        style.configure("Title.TLabel",
                        font=("Arial", 24, "bold"),
                        background="#ecf0f1",
                        foreground="#2c3e50")

        # Style cho header
        style.configure("Header.TFrame", background="#3498db")
        style.configure("HeaderTitle.TLabel",
                        font=("Arial", 18, "bold"),
                        background="#3498db",
                        foreground="white")

    def setup_main_layout(self):
        """Cấu hình layout chính"""
        # Header
        self.header_frame = ttk.Frame(self.root, style="Header.TFrame")
        self.header_frame.pack(fill="x", side="top")

        header_label = ttk.Label(self.header_frame,
                                 text="🏢 Hệ thống Quản lý Nhân sự",
                                 style="HeaderTitle.TLabel")
        header_label.pack(pady=15)

        # Main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill="both", expand=True)

        # Sidebar
        self.sidebar_frame = ttk.Frame(self.main_container, style="Sidebar.TFrame", width=250)
        self.sidebar_frame.pack(fill="y", side="left")
        self.sidebar_frame.pack_propagate(False)

        # Content area
        self.content_frame = ttk.Frame(self.main_container, style="Content.TFrame")
        self.content_frame.pack(fill="both", expand=True, side="right")

    def create_sidebar(self):
        """Tạo sidebar navigation"""
        # Logo/Title
        title_label = ttk.Label(self.sidebar_frame,
                                text="MENU CHÍNH",
                                font=("Arial", 14, "bold"),
                                background="#2c3e50",
                                foreground="white")
        title_label.pack(pady=(30, 20))

        # Navigation buttons
        nav_items = [
            ("🏠 Trang chủ", self.show_home),
            ("👥 Quản lý nhân viên", self.show_employee_ui),
            ("⏰ Chấm công", self.show_attendance_ui),
            ("🎯 Quản lý ứng viên", self.show_candidate_ui),
            ("💬 Phản hồi", self.show_feedback_ui),
            ("💰 Báo cáo lương", self.show_salary_ui),
        ]

        for text, command in nav_items:
            btn = ttk.Button(self.sidebar_frame,
                             text=text,
                             command=command,
                             style="SidebarButton.TButton")
            btn.pack(fill="x", padx=10, pady=5)

        # Separator
        separator = ttk.Separator(self.sidebar_frame, orient="horizontal")
        separator.pack(fill="x", padx=20, pady=20)

        # Exit button
        exit_btn = ttk.Button(self.sidebar_frame,
                              text="🚪 Thoát",
                              command=self.confirm_exit,
                              style="SidebarButton.TButton")
        exit_btn.pack(fill="x", padx=10, pady=5)

    def clear_main_content(self):
        """Xóa nội dung hiện tại"""
        for widget in self.main_content.winfo_children():
            widget.destroy()

    def show_home(self):
        """Hiển thị trang chủ"""
        self.clear_main_content()

        # Welcome message
        welcome_frame = ttk.Frame(self.main_content, style="Content.TFrame")
        welcome_frame.pack(fill="both", expand=True)

        title = ttk.Label(welcome_frame,
                          text="Chào mừng đến với Hệ thống Quản lý Nhân sự",
                          style="Title.TLabel")
        title.pack(pady=(50, 30))

        # Quick stats or info cards
        info_frame = ttk.Frame(welcome_frame, style="Content.TFrame")
        info_frame.pack(pady=20)

        info_text = """
        📋 Chức năng chính:
        • Quản lý thông tin nhân viên
        • Theo dõi chấm công
        • Quản lý ứng viên tuyển dụng
        • Xử lý phản hồi nhân viên
        • Tạo báo cáo lương

        👈 Sử dụng menu bên trái để điều hướng
        """

        info_label = ttk.Label(info_frame,
                               text=info_text,
                               font=("Arial", 12),
                               background="#ecf0f1",
                               justify="left")
        info_label.pack()

    def show_employee_ui(self):
        self.clear_main_content()
        self.current_ui = EmployeeUI(self.main_content)

    def show_attendance_ui(self):
        self.clear_main_content()
        self.current_ui = AttendanceUI(self.main_content)

    def show_candidate_ui(self):
        self.clear_main_content()
        self.current_ui = CandidateUI(self.main_content)

    def show_feedback_ui(self):
        self.clear_main_content()
        self.current_ui = FeedbackUI(self.main_content)

    def show_salary_ui(self):
        self.clear_main_content()
        self.current_ui = SalaryUI(self.main_content)

    def confirm_exit(self):
        """Xác nhận thoát ứng dụng"""
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn thoát?"):
            self.root.quit()
