import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from src.logic.candidate import CandidateManager


class CandidateUI:
    def __init__(self, parent):
        self.parent = parent
        self.candidate_mgr = CandidateManager()

        self.setup_styles()
        self.create_layout()
        self.load_candidates()

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
        title = ttk.Label(main_frame, text="🎯 QUẢN LÝ ỨNG VIÊN", style="Title.TLabel")
        title.pack(pady=(0, 30))

        # Create main container
        container = ttk.Frame(main_frame)
        container.pack(fill="both", expand=True, padx=20)

        # Left panel - Form
        left_panel = ttk.LabelFrame(container, text="Thông tin ứng viên", padding=20)
        left_panel.pack(side="left", fill="y", padx=(0, 20))

        self.create_form(left_panel)

        # Right panel - Candidate list
        right_panel = ttk.LabelFrame(container, text="Danh sách ứng viên", padding=10)
        right_panel.pack(side="right", fill="both", expand=True)

        self.create_candidate_list(right_panel)

    def create_form(self, parent):
        """Tạo form nhập thông tin ứng viên"""
        # Form fields
        fields = [
            ("Họ và tên:", "name"),
            ("Email:", "email"),
            ("Số điện thoại:", "phone"),
            ("Vị trí ứng tuyển:", "position"),
            ("Kinh nghiệm (năm):", "experience"),
            ("Trình độ học vấn:", "education"),
            ("Kỹ năng:", "skills")
        ]

        self.entries = {}
        for i, (label_text, field_name) in enumerate(fields):
            ttk.Label(parent, text=label_text).grid(row=i, column=0, sticky="w", pady=8, padx=(0, 10))

            if field_name == "skills":
                # Use Text widget for skills (multiline)
                entry = tk.Text(parent, width=30, height=3, font=("Arial", 10))
                entry.grid(row=i, column=1, pady=8, sticky="ew")
            else:
                entry = ttk.Entry(parent, width=30, font=("Arial", 11))
                entry.grid(row=i, column=1, pady=8)

            self.entries[field_name] = entry

        # Status dropdown
        ttk.Label(parent, text="Trạng thái:").grid(row=len(fields), column=0, sticky="w", pady=8, padx=(0, 10))
        self.status_var = tk.StringVar(value="Chờ xử lý")
        status_combo = ttk.Combobox(parent, textvariable=self.status_var, width=27,
                                    values=["Chờ xử lý", "Đã phỏng vấn", "Đậu", "Trượt", "Từ chối"])
        status_combo.grid(row=len(fields), column=1, pady=8)
        status_combo.state(['readonly'])

        # Buttons
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=len(fields) + 1, column=0, columnspan=2, pady=20)

        buttons = [
            ("➕ Thêm ứng viên", self.add_candidate),
            ("✏️ Cập nhật", self.update_candidate),
            ("🗑️ Xóa", self.delete_candidate),
            ("🔄 Làm mới", self.clear_entries)
        ]

        for i, (text, command) in enumerate(buttons):
            btn = ttk.Button(btn_frame, text=text, command=command)
            btn.grid(row=i // 2, column=i % 2, padx=5, pady=5, sticky="ew")

        # Search section
        search_frame = ttk.LabelFrame(parent, text="Tìm kiếm", padding=10)
        search_frame.grid(row=len(fields) + 2, column=0, columnspan=2, pady=(20, 0), sticky="ew")

        ttk.Label(search_frame, text="Từ khóa:").pack(anchor="w")
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(fill="x", pady=(5, 10))

        search_btn = ttk.Button(search_frame, text="🔍 Tìm kiếm", command=self.search_candidates)
        search_btn.pack()

        # Bind Enter key to search
        self.search_entry.bind('<Return>', lambda e: self.search_candidates())

    def create_candidate_list(self, parent):
        """Tạo danh sách ứng viên"""
        # Treeview
        columns = ("ID", "Tên", "Email", "Vị trí", "Kinh nghiệm", "Trạng thái", "Ngày nộp")
        self.candidate_tree = ttk.Treeview(parent, columns=columns, show="headings", height=20)

        # Configure columns
        column_widths = {
            "ID": 50, "Tên": 150, "Email": 180, "Vị trí": 120,
            "Kinh nghiệm": 80, "Trạng thái": 100, "Ngày nộp": 100
        }

        for col in columns:
            self.candidate_tree.heading(col, text=col)
            self.candidate_tree.column(col, width=column_widths.get(col, 100), anchor="center")

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.candidate_tree.yview)
        h_scrollbar = ttk.Scrollbar(parent, orient="horizontal", command=self.candidate_tree.xview)
        self.candidate_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Pack treeview and scrollbars
        self.candidate_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        # Bind selection event
        self.candidate_tree.bind('<<TreeviewSelect>>', self.on_candidate_select)

        # Context menu
        self.create_context_menu()

    def create_context_menu(self):
        """Tạo context menu cho danh sách ứng viên"""
        self.context_menu = tk.Menu(self.candidate_tree, tearoff=0)
        self.context_menu.add_command(label="📧 Gửi email", command=self.send_email)
        self.context_menu.add_command(label="📞 Gọi điện", command=self.make_call)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="✏️ Chỉnh sửa", command=self.edit_selected)
        self.context_menu.add_command(label="🗑️ Xóa", command=self.delete_selected)

        # Bind right click
        self.candidate_tree.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        """Hiển thị context menu"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def validate_input(self):
        """Validate form input"""
        required_fields = {
            'name': 'Họ tên',
            'email': 'Email',
            'position': 'Vị trí ứng tuyển'
        }

        for field, label in required_fields.items():
            value = self.get_entry_value(field)
            if not value.strip():
                messagebox.showwarning("Cảnh báo", f"Vui lòng nhập {label}!")
                self.entries[field].focus()
                return False

        # Validate email format
        email = self.get_entry_value('email')
        if '@' not in email or '.' not in email:
            messagebox.showwarning("Cảnh báo", "Định dạng email không hợp lệ!")
            self.entries['email'].focus()
            return False

        # Validate experience is numeric (if provided)
        experience = self.get_entry_value('experience')
        if experience and not experience.isdigit():
            messagebox.showwarning("Cảnh báo", "Kinh nghiệm phải là số!")
            self.entries['experience'].focus()
            return False

        return True

    def get_entry_value(self, field):
        """Lấy giá trị từ entry field"""
        entry = self.entries[field]
        if isinstance(entry, tk.Text):
            return entry.get("1.0", tk.END).strip()
        else:
            return entry.get().strip()

    def set_entry_value(self, field, value):
        """Đặt giá trị cho entry field"""
        entry = self.entries[field]
        if isinstance(entry, tk.Text):
            entry.delete("1.0", tk.END)
            entry.insert("1.0", value)
        else:
            entry.delete(0, tk.END)
            entry.insert(0, value)

    def add_candidate(self):
        """Thêm ứng viên mới"""
        if not self.validate_input():
            return

        try:
            candidate_id = self.candidate_mgr.add_candidate_extended(
                name=self.get_entry_value('name'),
                email=self.get_entry_value('email'),
                phone=self.get_entry_value('phone'),
                position=self.get_entry_value('position'),
                experience=int(self.get_entry_value('experience')) if self.get_entry_value('experience') else 0,
                education=self.get_entry_value('education'),
                skills=self.get_entry_value('skills'),
                status=self.status_var.get()
            )
            messagebox.showinfo("Thành công", f"Thêm ứng viên thành công! Mã: {candidate_id}")
            self.clear_entries()
            self.load_candidates()

        except ValueError as e:
            messagebox.showerror("Lỗi validation", str(e))
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def update_candidate(self):
        """Cập nhật thông tin ứng viên"""
        selection = self.candidate_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ứng viên cần cập nhật!")
            return

        if not self.validate_input():
            return

        try:
            item = self.candidate_tree.item(selection[0])
            candidate_id = item['values'][0]

            candidate_data = {
                'id': candidate_id,
                'name': self.get_entry_value('name'),
                'email': self.get_entry_value('email'),
                'phone': self.get_entry_value('phone'),
                'position': self.get_entry_value('position'),
                'experience': self.get_entry_value('experience') or '0',
                'education': self.get_entry_value('education'),
                'skills': self.get_entry_value('skills'),
                'status': self.status_var.get()
            }

            # Update in database
            self.candidate_mgr.update_candidate_extended(**candidate_data)
            messagebox.showinfo("Thành công", "Cập nhật ứng viên thành công!")
            self.clear_entries()
            self.load_candidates()

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật ứng viên: {str(e)}")

    def delete_candidate(self):
        """Xóa ứng viên"""
        selection = self.candidate_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ứng viên cần xóa!")
            return

        item = self.candidate_tree.item(selection[0])
        candidate_name = item['values'][1]

        if messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa ứng viên '{candidate_name}'?"):
            try:
                candidate_id = item['values'][0]
                self.candidate_mgr.delete_candidate(candidate_id)
                messagebox.showinfo("Thành công", "Xóa ứng viên thành công!")
                self.clear_entries()
                self.load_candidates()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa ứng viên: {str(e)}")

    def load_candidates(self):
        """Load danh sách ứng viên"""
        # Clear existing items
        for item in self.candidate_tree.get_children():
            self.candidate_tree.delete(item)

        try:
            candidates = self.candidate_mgr.get_all_candidates()

            for candidate in candidates:
                # candidate format: (id, candidate_id, name, email, phone, position, experience, education, skills, status, application_date, interview_date, notes)
                display_values = (
                    candidate[0],  # ID
                    candidate[2],  # Name
                    candidate[3],  # Email
                    candidate[5],  # Position
                    candidate[6] if candidate[6] else 0,  # Experience
                    candidate[9],  # Status
                    candidate[10]  # Application date
                )
                self.candidate_tree.insert("", "end", values=display_values)

        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def search_candidates(self):
        """Tìm kiếm ứng viên"""
        search_term = self.search_entry.get().strip()

        # Clear existing items
        for item in self.candidate_tree.get_children():
            self.candidate_tree.delete(item)

        try:
            candidates = self.candidate_mgr.search_candidates(search_term)

            for candidate in candidates:
                display_values = (
                    candidate[0],  # ID
                    candidate[2],  # Name
                    candidate[3],  # Email
                    candidate[5],  # Position
                    candidate[6] if candidate[6] else 0,  # Experience
                    candidate[9],  # Status
                    candidate[10]  # Application date
                )
                self.candidate_tree.insert("", "end", values=display_values)

            if not candidates:
                messagebox.showinfo("Thông báo", "Không tìm thấy ứng viên nào!")

        except Exception as e:
            messagebox.showerror("Lỗi", str(e))


    def on_candidate_select(self, event):
        """Xử lý khi chọn ứng viên"""
        selection = self.candidate_tree.selection()
        if selection:
            item = self.candidate_tree.item(selection[0])
            values = item['values']

            # Fill form with selected candidate data
            try:
                self.set_entry_value('name', values[1])
                self.set_entry_value('email', values[2])
                self.set_entry_value('phone', values[3] if len(values) > 3 else '')
                self.set_entry_value('position', values[3] if len(values) <= 5 else values[3])
                self.set_entry_value('experience', str(values[4]) if len(values) > 4 else '0')
                self.set_entry_value('education', '')
                self.set_entry_value('skills', '')

                if len(values) > 5:
                    self.status_var.set(values[5])
                else:
                    self.status_var.set('Chờ xử lý')

            except Exception as e:
                print(f"Error loading candidate data: {e}")


    def send_email(self):
        """Gửi email cho ứng viên (placeholder)"""
        selection = self.candidate_tree.selection()
        if selection:
            item = self.candidate_tree.item(selection[0])
            email = item['values'][2]
            messagebox.showinfo("Thông báo", f"Chức năng gửi email đến {email} sẽ được phát triển!")


    def make_call(self):
        """Gọi điện cho ứng viên (placeholder)"""
        selection = self.candidate_tree.selection()
        if selection:
            item = self.candidate_tree.item(selection[0])
            name = item['values'][1]
            messagebox.showinfo("Thông báo", f"Chức năng gọi điện cho {name} sẽ được phát triển!")


    def edit_selected(self):
        """Chỉnh sửa ứng viên được chọn"""
        self.on_candidate_select(None)


    def delete_selected(self):
        """Xóa ứng viên được chọn"""
        self.delete_candidate()


    def clear_entries(self):
        """Xóa tất cả các trường nhập liệu"""
        for field, entry in self.entries.items():
            if isinstance(entry, tk.Text):
                entry.delete("1.0", tk.END)
            else:
                entry.delete(0, tk.END)

        self.status_var.set("Chờ xử lý")
