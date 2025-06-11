import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from src.logic.attendance import AttendanceManager


class AttendanceUI:
    def __init__(self, parent):
        self.parent = parent
        self.attendance_mgr = AttendanceManager()

        self.setup_styles()
        self.create_layout()
        self.load_attendance()

    def setup_styles(self):
        """Cấu hình styles"""
        style = ttk.Style()

        style.configure("Title.TLabel",
                        font=("Arial", 20, "bold"),
                        background="#ecf0f1",
                        foreground="#2c3e50")

    def create_layout(self):
        """Tạo layout chính"""
        main_frame = ttk.Frame(self.parent, style="Content.TFrame")
        main_frame.pack(fill="both", expand=True)

        # Title
        title = ttk.Label(main_frame, text="⏰ QUẢN LÝ CHẤM CÔNG", style="Title.TLabel")
        title.pack(pady=(0, 30))

        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True)

        # Tab 1: Add Attendance
        add_tab = ttk.Frame(notebook)
        notebook.add(add_tab, text="Chấm công")

        # Tab 2: View Attendance
        view_tab = ttk.Frame(notebook)
        notebook.add(view_tab, text="Xem chấm công")

        self.create_add_tab(add_tab)
        self.create_view_tab(view_tab)

    def create_add_tab(self, parent):
        """Tạo tab chấm công"""
        # Main container
        container = ttk.Frame(parent, padding=20)
        container.pack(fill="both", expand=True)

        # Form section
        form_frame = ttk.LabelFrame(container, text="Thông tin chấm công", padding=20)
        form_frame.pack(fill="x", pady=(0, 20))

        # Create form in grid layout
        fields = [
            ("Mã nhân viên:", "employee_id"),
            ("Ngày (YYYY-MM-DD):", "date"),
            ("Giờ vào (HH:MM):", "time_in"),
            ("Giờ ra (HH:MM):", "time_out")
        ]

        self.entries = {}
        for i, (label_text, field_name) in enumerate(fields):
            row = i // 2
            col = (i % 2) * 3

            ttk.Label(form_frame, text=label_text).grid(row=row, column=col, sticky="w", padx=(0, 10), pady=10)
            entry = ttk.Entry(form_frame, width=20, font=("Arial", 11))
            entry.grid(row=row, column=col + 1, padx=(0, 30), pady=10)
            self.entries[field_name] = entry

        # Auto-fill current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        self.entries['date'].insert(0, current_date)

        # Quick time buttons
        time_frame = ttk.Frame(form_frame)
        time_frame.grid(row=2, column=0, columnspan=6, pady=20)

        ttk.Button(time_frame, text="⏰ Giờ hiện tại (Vào)",
                   command=lambda: self.set_current_time('time_in')).pack(side="left", padx=5)
        ttk.Button(time_frame, text="⏰ Giờ hiện tại (Ra)",
                   command=lambda: self.set_current_time('time_out')).pack(side="left", padx=5)

        # Action buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=3, column=0, columnspan=6, pady=20)

        ttk.Button(btn_frame, text="✅ Ghi chấm công",
                   command=self.add_attendance).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="🔄 Làm mới",
                   command=self.clear_entries).pack(side="left", padx=10)

        # Quick stats section
        stats_frame = ttk.LabelFrame(container, text="Thống kê nhanh", padding=15)
        stats_frame.pack(fill="x")

        self.stats_label = ttk.Label(stats_frame, text="Đang tải thống kê...",
                                     font=("Arial", 10))
        self.stats_label.pack()

        self.update_stats()

    def create_view_tab(self, parent):
        """Tạo tab xem chấm công"""
        container = ttk.Frame(parent, padding=20)
        container.pack(fill="both", expand=True)

        # Filter section
        filter_frame = ttk.LabelFrame(container, text="Bộ lọc", padding=15)
        filter_frame.pack(fill="x", pady=(0, 20))

        ttk.Label(filter_frame, text="Mã nhân viên:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.filter_employee = ttk.Entry(filter_frame, width=15)
        self.filter_employee.grid(row=0, column=1, padx=(0, 20))

        ttk.Label(filter_frame, text="Từ ngày:").grid(row=0, column=2, sticky="w", padx=(0, 10))
        self.filter_from_date = ttk.Entry(filter_frame, width=12)
        self.filter_from_date.grid(row=0, column=3, padx=(0, 20))

        ttk.Label(filter_frame, text="Đến ngày:").grid(row=0, column=4, sticky="w", padx=(0, 10))
        self.filter_to_date = ttk.Entry(filter_frame, width=12)
        self.filter_to_date.grid(row=0, column=5, padx=(0, 20))

        ttk.Button(filter_frame, text="🔍 Lọc",
                   command=self.filter_attendance).grid(row=0, column=6, padx=10)
        ttk.Button(filter_frame, text="🔄 Tất cả",
                   command=self.load_attendance).grid(row=0, column=7, padx=5)

        # Attendance list
        list_frame = ttk.LabelFrame(container, text="Danh sách chấm công", padding=10)
        list_frame.pack(fill="both", expand=True)

        # Treeview
        columns = ("ID", "Mã NV", "Ngày", "Giờ vào", "Giờ ra", "Tổng giờ")
        self.attendance_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)

        # Configure columns
        column_widths = {"ID": 60, "Mã NV": 100, "Ngày": 120, "Giờ vào": 100, "Giờ ra": 100, "Tổng giờ": 100}
        for col in columns:
            self.attendance_tree.heading(col, text=col)
            self.attendance_tree.column(col, width=column_widths.get(col, 100), anchor="center")

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.attendance_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient="horizontal", command=self.attendance_tree.xview)
        self.attendance_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Pack treeview and scrollbars
        self.attendance_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

    def set_current_time(self, field):
        """Đặt thời gian hiện tại"""
        current_time = datetime.now().strftime("%H:%M")
        self.entries[field].delete(0, tk.END)
        self.entries[field].insert(0, current_time)

    def calculate_work_hours(self, time_in, time_out):
        """Tính tổng giờ làm việc"""
        try:
            time_in_obj = datetime.strptime(time_in, "%H:%M")
            time_out_obj = datetime.strptime(time_out, "%H:%M")

            # Handle case where time_out is next day
            if time_out_obj < time_in_obj:
                time_out_obj = time_out_obj.replace(day=time_out_obj.day + 1)

            duration = time_out_obj - time_in_obj
            hours = duration.total_seconds() / 3600
            return f"{hours:.1f}h"
        except:
            return "N/A"

    def validate_attendance_input(self):
        """Validate attendance input"""
        required_fields = {
            'employee_id': 'Mã nhân viên',
            'date': 'Ngày',
            'time_in': 'Giờ vào',
            'time_out': 'Giờ ra'
        }

        for field, label in required_fields.items():
            if not self.entries[field].get().strip():
                messagebox.showwarning("Cảnh báo", f"Vui lòng nhập {label}!")
                self.entries[field].focus()
                return False

        # Validate date format
        try:
            datetime.strptime(self.entries['date'].get(), "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Cảnh báo", "Định dạng ngày không đúng (YYYY-MM-DD)!")
            self.entries['date'].focus()
            return False

        # Validate time format
        for time_field in ['time_in', 'time_out']:
            try:
                datetime.strptime(self.entries[time_field].get(), "%H:%M")
            except ValueError:
                messagebox.showwarning("Cảnh báo", f"Định dạng giờ không đúng (HH:MM)!")
                self.entries[time_field].focus()
                return False

        return True

    def add_attendance(self):
        """Thêm bản ghi chấm công"""
        try:
            employee_id = self.entries['employee_id'].get().strip()
            date = self.entries['date'].get().strip()
            time_in = self.entries['time_in'].get().strip()
            time_out = self.entries['time_out'].get().strip()

            attendance_id = self.attendance_mgr.add_attendance(employee_id, date, time_in, time_out)
            messagebox.showinfo("Thành công", f"Ghi chấm công thành công! Mã: {attendance_id}")
            self.clear_entries()
            self.load_attendance()
            self.update_stats()

        except ValueError as e:
            messagebox.showerror("Lỗi validation", str(e))
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def load_attendance(self):
        """Load danh sách chấm công"""
        # Clear existing items
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)

        try:
            # Sử dụng phương thức mới để lấy dữ liệu
            records = self.attendance_mgr.get_attendance_by_date_range(
                start_date="2020-01-01",
                end_date=datetime.now().strftime("%Y-%m-%d")
            )

            for record in records:
                # record format: (attendance_id, employee_id, date, time_in, time_out, work_hours, overtime_hours, status, notes)
                work_hours_display = f"{record[5]:.1f}h" if len(record) > 5 and record[5] else "N/A"
                self.attendance_tree.insert("", "end", values=(
                    record[0], record[1], record[2], record[3], record[4], work_hours_display
                ))

        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def filter_attendance(self):
        """Lọc chấm công theo điều kiện"""
        # Clear existing items
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)

        try:
            conditions = []
            params = []

            if self.filter_employee.get().strip():
                conditions.append("employee_id LIKE ?")
                params.append(f"%{self.filter_employee.get().strip()}%")

            if self.filter_from_date.get().strip():
                conditions.append("date >= ?")
                params.append(self.filter_from_date.get().strip())

            if self.filter_to_date.get().strip():
                conditions.append("date <= ?")
                params.append(self.filter_to_date.get().strip())

            query = "SELECT * FROM Attendance"
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            query += " ORDER BY date DESC, time_in DESC"

            self.attendance_mgr.db.execute(query, params)
            records = self.attendance_mgr.db.fetch_all()

            for record in records:
                work_hours = self.calculate_work_hours(record[3], record[4])
                self.attendance_tree.insert("", "end", values=(
                    record[0], record[1], record[2], record[3], record[4], work_hours
                ))

        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi lọc dữ liệu: {str(e)}")

    def update_stats(self):
        """Cập nhật thống kê nhanh"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            stats = self.attendance_mgr.get_attendance_statistics(start_date=today, end_date=today)

            today_count = stats.get('total_records', 0)
            total_stats = self.attendance_mgr.get_attendance_statistics()
            total_count = total_stats.get('total_records', 0)

            stats_text = f"📊 Hôm nay: {today_count} lượt chấm công | Tổng cộng: {total_count} bản ghi"
            self.stats_label.config(text=stats_text)

        except Exception as e:
            self.stats_label.config(text="Không thể tải thống kê")

    def clear_entries(self):
        """Xóa các trường nhập liệu"""
        for field, entry in self.entries.items():
            if field != 'date':  # Keep current date
                entry.delete(0, tk.END)
