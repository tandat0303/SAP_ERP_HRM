import tkinter as tk
from tkinter import ttk, messagebox
from ..logic.employee import EmployeeManager


class EmployeeUI:
    def __init__(self, parent):
        self.parent = parent
        self.employee_mgr = EmployeeManager()

        # Setup styles
        self.setup_styles()

        # Create main layout
        self.create_layout()

        # Load initial data
        self.load_employees()

    def setup_styles(self):
        """Cấu hình styles"""
        style = ttk.Style()

        style.configure("Title.TLabel",
                        font=("Arial", 20, "bold"),
                        background="#ecf0f1",
                        foreground="#2c3e50")

        style.configure("Section.TLabel",
                        font=("Arial", 12, "bold"),
                        background="#ecf0f1",
                        foreground="#34495e")

        style.configure("Action.TButton",
                        font=("Arial", 10, "bold"),
                        padding=(15, 8))

    def create_layout(self):
        """Tạo layout chính"""
        # Main container
        main_frame = ttk.Frame(self.parent, style="Content.TFrame")
        main_frame.pack(fill="both", expand=True)

        # Title
        title = ttk.Label(main_frame, text="👥 QUẢN LÝ NHÂN VIÊN", style="Title.TLabel")
        title.pack(pady=(0, 30))

        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)

        # Tab 1: Employee Management
        self.employee_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.employee_tab, text="Quản lý nhân viên")

        # Tab 2: Search
        self.search_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.search_tab, text="Tìm kiếm")

        self.create_employee_tab()
        self.create_search_tab()

    def create_employee_tab(self):
        """Tạo tab quản lý nhân viên"""
        # Left panel - Form
        left_panel = ttk.LabelFrame(self.employee_tab, text="Thông tin nhân viên", padding=20)
        left_panel.pack(side="left", fill="y", padx=(0, 10), pady=10)

        # Form fields
        fields = [
            ("Mã nhân viên:", "id_entry"),
            ("Họ và tên:", "name_entry"),
            ("Phòng ban:", "dept_entry"),
            ("Lương (VNĐ):", "salary_entry"),
            ("Ngày vào làm:", "join_date_entry")
        ]

        self.entries = {}
        for i, (label_text, entry_name) in enumerate(fields):
            ttk.Label(left_panel, text=label_text).grid(row=i, column=0, sticky="w", pady=8, padx=(0, 10))
            entry = ttk.Entry(left_panel, width=25, font=("Arial", 11))
            entry.grid(row=i, column=1, pady=8)
            self.entries[entry_name] = entry

        # Buttons frame
        btn_frame = ttk.Frame(left_panel)
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=20)

        buttons = [
            ("➕ Thêm", self.add_employee, "#27ae60"),
            ("✏️ Sửa", self.update_employee, "#f39c12"),
            ("🗑️ Xóa", self.delete_employee, "#e74c3c"),
            ("🔄 Làm mới", self.clear_entries, "#95a5a6")
        ]

        for i, (text, command, color) in enumerate(buttons):
            btn = ttk.Button(btn_frame, text=text, command=command, style="Action.TButton")
            btn.grid(row=i // 2, column=i % 2, padx=5, pady=5, sticky="ew")

        # Right panel - Employee list
        right_panel = ttk.LabelFrame(self.employee_tab, text="Danh sách nhân viên", padding=10)
        right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0), pady=10)

        # Treeview for employee list
        columns = ("ID", "Tên", "Phòng ban", "Lương", "Ngày vào")
        self.employee_tree = ttk.Treeview(right_panel, columns=columns, show="headings", height=15)

        # Configure columns
        for col in columns:
            self.employee_tree.heading(col, text=col)
            self.employee_tree.column(col, width=120, anchor="center")

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(right_panel, orient="vertical", command=self.employee_tree.yview)
        h_scrollbar = ttk.Scrollbar(right_panel, orient="horizontal", command=self.employee_tree.xview)
        self.employee_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Pack treeview and scrollbars
        self.employee_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        right_panel.grid_rowconfigure(0, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)

        # Bind selection event
        self.employee_tree.bind('<<TreeviewSelect>>', self.on_employee_select)

    def create_search_tab(self):
        """Tạo tab tìm kiếm"""
        search_frame = ttk.Frame(self.search_tab, padding=20)
        search_frame.pack(fill="both", expand=True)

        # Define columns for search results
        columns = ("ID", "Tên", "Phòng ban", "Lương", "Ngày vào")

        # Search section
        search_section = ttk.LabelFrame(search_frame, text="Tìm kiếm nhân viên", padding=15)
        search_section.pack(fill="x", pady=(0, 20))

        ttk.Label(search_section, text="Từ khóa (Mã NV hoặc Tên):").pack(anchor="w")

        search_input_frame = ttk.Frame(search_section)
        search_input_frame.pack(fill="x", pady=(5, 0))

        self.search_entry = ttk.Entry(search_input_frame, font=("Arial", 12))
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        search_btn = ttk.Button(search_input_frame, text="🔍 Tìm kiếm", command=self.search_employee)
        search_btn.pack(side="right")

        # Bind Enter key to search
        self.search_entry.bind('<Return>', lambda e: self.search_employee())

        # Results section
        results_section = ttk.LabelFrame(search_frame, text="Kết quả tìm kiếm", padding=10)
        results_section.pack(fill="both", expand=True)

        # Search results treeview
        self.search_tree = ttk.Treeview(results_section, columns=columns, show="headings", height=12)

        for col in columns:
            self.search_tree.heading(col, text=col)
            self.search_tree.column(col, width=120, anchor="center")

        search_v_scrollbar = ttk.Scrollbar(results_section, orient="vertical", command=self.search_tree.yview)
        self.search_tree.configure(yscrollcommand=search_v_scrollbar.set)

        self.search_tree.pack(side="left", fill="both", expand=True)
        search_v_scrollbar.pack(side="right", fill="y")

    def load_employees(self):
        """Load danh sách nhân viên"""
        # Clear existing items
        for item in self.employee_tree.get_children():
            self.employee_tree.delete(item)

        try:
            employees = self.employee_mgr.get_all_employees()

            for employee in employees:
                # Format salary with thousand separators
                formatted_salary = f"{float(employee[3]):,.0f}"
                self.employee_tree.insert("", "end", values=(
                    employee[0], employee[1], employee[2], formatted_salary, employee[4]
                ))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách nhân viên: {str(e)}")

    def validate_input(self):
        """Validate form input"""
        required_fields = {
            'id_entry': 'Mã nhân viên',
            'name_entry': 'Họ tên',
            'dept_entry': 'Phòng ban',
            'salary_entry': 'Lương',
            'join_date_entry': 'Ngày vào làm'
        }

        for field, label in required_fields.items():
            if not self.entries[field].get().strip():
                messagebox.showwarning("Cảnh báo", f"Vui lòng nhập {label}!")
                self.entries[field].focus()
                return False

        # Validate salary is numeric
        try:
            float(self.entries['salary_entry'].get())
        except ValueError:
            messagebox.showwarning("Cảnh báo", "Lương phải là số!")
            self.entries['salary_entry'].focus()
            return False

        return True

    def add_employee(self):
        """Thêm nhân viên mới"""
        if not self.validate_input():
            return

        try:
            self.employee_mgr.add_employee(
                id=self.entries['id_entry'].get().strip(),
                name=self.entries['name_entry'].get().strip(),
                dept=self.entries['dept_entry'].get().strip(),
                salary=float(self.entries['salary_entry'].get()),
                join_date=self.entries['join_date_entry'].get().strip()
            )
            messagebox.showinfo("Thành công", "Thêm nhân viên thành công!")
            self.clear_entries()
            self.load_employees()

        except ValueError as e:
            messagebox.showerror("Lỗi validation", str(e))
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def update_employee(self):
        """Cập nhật thông tin nhân viên"""
        if not self.validate_input():
            return

        try:
            employee_data = {
                'id': self.entries['id_entry'].get().strip(),
                'name': self.entries['name_entry'].get().strip(),
                'dept': self.entries['dept_entry'].get().strip(),
                'salary': float(self.entries['salary_entry'].get()),
                'join_date': self.entries['join_date_entry'].get().strip()
            }

            self.employee_mgr.update_employee(**employee_data)
            messagebox.showinfo("Thành công", "Cập nhật nhân viên thành công!")
            self.clear_entries()
            self.load_employees()

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật nhân viên: {str(e)}")

    def delete_employee(self):
        """Xóa nhân viên"""
        employee_id = self.entries['id_entry'].get().strip()
        if not employee_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập mã nhân viên cần xóa!")
            return

        if messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa nhân viên {employee_id}?"):
            try:
                self.employee_mgr.delete_employee(employee_id)
                messagebox.showinfo("Thành công", "Xóa nhân viên thành công!")
                self.clear_entries()
                self.load_employees()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa nhân viên: {str(e)}")

    def search_employee(self):
        """Tìm kiếm nhân viên"""
        search_term = self.search_entry.get().strip()
        if not search_term:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập từ khóa tìm kiếm!")
            return

        # Clear existing search results
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)

        try:
            results = self.employee_mgr.search_employee(search_term)

            if not results:
                messagebox.showinfo("Thông báo", "Không tìm thấy nhân viên nào!")
                return

            for employee in results:
                formatted_salary = f"{float(employee[3]):,.0f}"
                self.search_tree.insert("", "end", values=(
                    employee[0], employee[1], employee[2], formatted_salary, employee[4]
                ))

        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def on_employee_select(self, event):
        """Xử lý khi chọn nhân viên từ danh sách"""
        selection = self.employee_tree.selection()
        if selection:
            item = self.employee_tree.item(selection[0])
            values = item['values']

            # Fill form with selected employee data
            self.entries['id_entry'].delete(0, tk.END)
            self.entries['id_entry'].insert(0, values[0])

            self.entries['name_entry'].delete(0, tk.END)
            self.entries['name_entry'].insert(0, values[1])

            self.entries['dept_entry'].delete(0, tk.END)
            self.entries['dept_entry'].insert(0, values[2])

            self.entries['salary_entry'].delete(0, tk.END)
            # Remove thousand separators for editing
            salary_value = str(values[3]).replace(',', '')
            self.entries['salary_entry'].insert(0, salary_value)

            self.entries['join_date_entry'].delete(0, tk.END)
            self.entries['join_date_entry'].insert(0, values[4])

    def clear_entries(self):
        """Xóa tất cả các trường nhập liệu"""
        for entry in self.entries.values():
            entry.delete(0, tk.END)
