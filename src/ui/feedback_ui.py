import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from src.logic.feedback import FeedbackManager


class FeedbackUI:
    def __init__(self, parent):
        self.parent = parent
        self.feedback_mgr = FeedbackManager()

        self.setup_styles()
        self.create_layout()
        self.load_feedbacks()

    def setup_styles(self):
        """Cấu hình styles"""
        style = ttk.Style()

        style.configure("Title.TLabel",
                        font=("Arial", 20, "bold"),
                        background="#ecf0f1",
                        foreground="#2c3e50")

        style.configure("Priority.High.TLabel",
                        font=("Arial", 10, "bold"),
                        background="#e74c3c",
                        foreground="white")

        style.configure("Priority.Medium.TLabel",
                        font=("Arial", 10, "bold"),
                        background="#f39c12",
                        foreground="white")

        style.configure("Priority.Low.TLabel",
                        font=("Arial", 10, "bold"),
                        background="#27ae60",
                        foreground="white")

    def create_layout(self):
        """Tạo layout chính"""
        main_frame = ttk.Frame(self.parent, style="Content.TFrame")
        main_frame.pack(fill="both", expand=True)

        # Title
        title = ttk.Label(main_frame, text="💬 QUẢN LÝ PHẢN HỒI", style="Title.TLabel")
        title.pack(pady=(0, 30))

        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True, padx=20)

        # Tab 1: Submit Feedback
        submit_tab = ttk.Frame(notebook)
        notebook.add(submit_tab, text="Gửi phản hồi")

        # Tab 2: Manage Feedback
        manage_tab = ttk.Frame(notebook)
        notebook.add(manage_tab, text="Quản lý phản hồi")

        # Tab 3: Analytics
        analytics_tab = ttk.Frame(notebook)
        notebook.add(analytics_tab, text="Thống kê")

        self.create_submit_tab(submit_tab)
        self.create_manage_tab(manage_tab)
        self.create_analytics_tab(analytics_tab)

    def create_submit_tab(self, parent):
        """Tạo tab gửi phản hồi"""
        container = ttk.Frame(parent, padding=20)
        container.pack(fill="both", expand=True)

        # Form section
        form_frame = ttk.LabelFrame(container, text="Gửi phản hồi mới", padding=20)
        form_frame.pack(fill="x", pady=(0, 20))

        # Employee ID
        ttk.Label(form_frame, text="Mã nhân viên:").grid(row=0, column=0, sticky="w", pady=10, padx=(0, 10))
        self.employee_id_entry = ttk.Entry(form_frame, width=20, font=("Arial", 11))
        self.employee_id_entry.grid(row=0, column=1, pady=10, sticky="ew")

        # Category
        ttk.Label(form_frame, text="Danh mục:").grid(row=0, column=2, sticky="w", pady=10, padx=(20, 10))
        self.category_var = tk.StringVar(value="Chung")
        category_combo = ttk.Combobox(form_frame, textvariable=self.category_var, width=15,
                                      values=["Chung", "Lương thưởng", "Môi trường làm việc",
                                              "Đồng nghiệp", "Quản lý", "Phúc lợi", "Khác"])
        category_combo.grid(row=0, column=3, pady=10)
        category_combo.state(['readonly'])

        # Priority
        ttk.Label(form_frame, text="Mức độ ưu tiên:").grid(row=1, column=0, sticky="w", pady=10, padx=(0, 10))
        self.priority_var = tk.StringVar(value="Thấp")
        priority_combo = ttk.Combobox(form_frame, textvariable=self.priority_var, width=15,
                                      values=["Thấp", "Trung bình", "Cao", "Khẩn cấp"])
        priority_combo.grid(row=1, column=1, pady=10, sticky="ew")
        priority_combo.state(['readonly'])

        # Anonymous option
        self.anonymous_var = tk.BooleanVar()
        anonymous_check = ttk.Checkbutton(form_frame, text="Gửi ẩn danh", variable=self.anonymous_var)
        anonymous_check.grid(row=1, column=2, columnspan=2, sticky="w", pady=10, padx=(20, 0))

        # Feedback content
        ttk.Label(form_frame, text="Nội dung phản hồi:").grid(row=2, column=0, sticky="nw", pady=(10, 5), padx=(0, 10))
        self.feedback_text = tk.Text(form_frame, width=60, height=6, font=("Arial", 11), wrap=tk.WORD)
        self.feedback_text.grid(row=2, column=1, columnspan=3, pady=(10, 5), sticky="ew")

        # Character counter
        self.char_count_label = ttk.Label(form_frame, text="0/1000 ký tự")
        self.char_count_label.grid(row=3, column=1, columnspan=3, sticky="e", pady=(0, 10))

        # Bind text change event
        self.feedback_text.bind('<KeyRelease>', self.update_char_count)

        # Configure grid weights
        form_frame.grid_columnconfigure(1, weight=1)
        form_frame.grid_columnconfigure(3, weight=1)

        # Buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=4, column=0, columnspan=4, pady=20)

        ttk.Button(btn_frame, text="📤 Gửi phản hồi", command=self.submit_feedback).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="🔄 Làm mới", command=self.clear_feedback_form).pack(side="left", padx=10)

        # Recent feedbacks section
        recent_frame = ttk.LabelFrame(container, text="Phản hồi gần đây", padding=10)
        recent_frame.pack(fill="both", expand=True)

        # Recent feedbacks listbox
        self.recent_listbox = tk.Listbox(recent_frame, height=8, font=("Arial", 10))
        recent_scrollbar = ttk.Scrollbar(recent_frame, orient="vertical", command=self.recent_listbox.yview)
        self.recent_listbox.configure(yscrollcommand=recent_scrollbar.set)

        self.recent_listbox.pack(side="left", fill="both", expand=True)
        recent_scrollbar.pack(side="right", fill="y")

    def create_manage_tab(self, parent):
        """Tạo tab quản lý phản hồi"""
        container = ttk.Frame(parent, padding=20)
        container.pack(fill="both", expand=True)

        # Filter section
        filter_frame = ttk.LabelFrame(container, text="Bộ lọc", padding=15)
        filter_frame.pack(fill="x", pady=(0, 20))

        # Filter controls
        ttk.Label(filter_frame, text="Trạng thái:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.filter_status_var = tk.StringVar(value="Tất cả")
        status_filter = ttk.Combobox(filter_frame, textvariable=self.filter_status_var, width=12,
                                     values=["Tất cả", "Chờ xử lý", "Đang xử lý", "Đã xử lý", "Đã đóng"])
        status_filter.grid(row=0, column=1, padx=(0, 20))
        status_filter.state(['readonly'])

        ttk.Label(filter_frame, text="Danh mục:").grid(row=0, column=2, sticky="w", padx=(0, 10))
        self.filter_category_var = tk.StringVar(value="Tất cả")
        category_filter = ttk.Combobox(filter_frame, textvariable=self.filter_category_var, width=15,
                                       values=["Tất cả", "Chung", "Lương thưởng", "Môi trường làm việc",
                                               "Đồng nghiệp", "Quản lý", "Phúc lợi", "Khác"])
        category_filter.grid(row=0, column=3, padx=(0, 20))
        category_filter.state(['readonly'])

        ttk.Label(filter_frame, text="Mức độ:").grid(row=0, column=4, sticky="w", padx=(0, 10))
        self.filter_priority_var = tk.StringVar(value="Tất cả")
        priority_filter = ttk.Combobox(filter_frame, textvariable=self.filter_priority_var, width=12,
                                       values=["Tất cả", "Thấp", "Trung bình", "Cao", "Khẩn cấp"])
        priority_filter.grid(row=0, column=5, padx=(0, 20))
        priority_filter.state(['readonly'])

        ttk.Button(filter_frame, text="🔍 Lọc", command=self.filter_feedbacks).grid(row=0, column=6, padx=10)
        ttk.Button(filter_frame, text="🔄 Tất cả", command=self.load_feedbacks).grid(row=0, column=7, padx=5)

        # Feedback list
        list_frame = ttk.LabelFrame(container, text="Danh sách phản hồi", padding=10)
        list_frame.pack(fill="both", expand=True)

        # Treeview
        columns = ("ID", "Mã NV", "Danh mục", "Mức độ", "Trạng thái", "Ngày gửi", "Người xử lý")
        self.feedback_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)

        # Configure columns
        column_widths = {
            "ID": 50, "Mã NV": 80, "Danh mục": 120, "Mức độ": 80,
            "Trạng thái": 100, "Ngày gửi": 100, "Người xử lý": 100
        }

        for col in columns:
            self.feedback_tree.heading(col, text=col)
            self.feedback_tree.column(col, width=column_widths.get(col, 100), anchor="center")

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.feedback_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient="horizontal", command=self.feedback_tree.xview)
        self.feedback_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Pack treeview and scrollbars
        self.feedback_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        # Bind selection event
        self.feedback_tree.bind('<<TreeviewSelect>>', self.on_feedback_select)

        # Detail and response section
        detail_frame = ttk.LabelFrame(container, text="Chi tiết và phản hồi", padding=15)
        detail_frame.pack(fill="x", pady=(20, 0))

        # Feedback detail
        ttk.Label(detail_frame, text="Nội dung phản hồi:").grid(row=0, column=0, sticky="nw", pady=(0, 5))
        self.feedback_detail = tk.Text(detail_frame, width=60, height=4, font=("Arial", 10),
                                       state="disabled", wrap=tk.WORD)
        self.feedback_detail.grid(row=0, column=1, columnspan=2, pady=(0, 10), sticky="ew")

        # Response section
        ttk.Label(detail_frame, text="Phản hồi của HR:").grid(row=1, column=0, sticky="nw", pady=(0, 5))
        self.response_text = tk.Text(detail_frame, width=60, height=3, font=("Arial", 10), wrap=tk.WORD)
        self.response_text.grid(row=1, column=1, columnspan=2, pady=(0, 10), sticky="ew")

        # Status update
        ttk.Label(detail_frame, text="Cập nhật trạng thái:").grid(row=2, column=0, sticky="w", pady=(0, 10))
        self.update_status_var = tk.StringVar(value="Chờ xử lý")
        status_update_combo = ttk.Combobox(detail_frame, textvariable=self.update_status_var, width=15,
                                           values=["Chờ xử lý", "Đang xử lý", "Đã xử lý", "Đã đóng"])
        status_update_combo.grid(row=2, column=1, sticky="w", pady=(0, 10))
        status_update_combo.state(['readonly'])

        # Action buttons
        btn_frame = ttk.Frame(detail_frame)
        btn_frame.grid(row=2, column=2, sticky="e", pady=(0, 10))

        ttk.Button(btn_frame, text="💾 Lưu phản hồi", command=self.save_response).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="📧 Gửi email", command=self.send_email_response).pack(side="left", padx=5)

        # Configure grid weights
        detail_frame.grid_columnconfigure(1, weight=1)

    def create_analytics_tab(self, parent):
        """Tạo tab thống kê"""
        container = ttk.Frame(parent, padding=20)
        container.pack(fill="both", expand=True)

        # Stats cards
        stats_frame = ttk.Frame(container)
        stats_frame.pack(fill="x", pady=(0, 20))

        # Create stat cards
        self.create_stat_card(stats_frame, "Tổng phản hồi", "0", "#3498db", 0)
        self.create_stat_card(stats_frame, "Chờ xử lý", "0", "#e74c3c", 1)
        self.create_stat_card(stats_frame, "Đã xử lý", "0", "#27ae60", 2)
        self.create_stat_card(stats_frame, "Tỷ lệ hài lòng", "0%", "#f39c12", 3)

        # Charts section (placeholder)
        charts_frame = ttk.LabelFrame(container, text="Biểu đồ thống kê", padding=15)
        charts_frame.pack(fill="both", expand=True)

        # Placeholder for charts
        chart_placeholder = ttk.Label(charts_frame,
                                      text="📊 Biểu đồ thống kê sẽ được hiển thị tại đây\n(Cần tích hợp thư viện matplotlib)",
                                      font=("Arial", 12),
                                      justify="center")
        chart_placeholder.pack(expand=True)

        # Update stats button
        ttk.Button(container, text="🔄 Cập nhật thống kê", command=self.update_analytics).pack(pady=10)

    def create_stat_card(self, parent, title, value, color, column):
        """Tạo card thống kê"""
        card_frame = ttk.LabelFrame(parent, text=title, padding=15)
        card_frame.grid(row=0, column=column, padx=10, sticky="ew")

        value_label = ttk.Label(card_frame, text=value, font=("Arial", 18, "bold"))
        value_label.pack()

        # Store reference for updating
        setattr(self, f"stat_{column}_label", value_label)

        parent.grid_columnconfigure(column, weight=1)

    def update_char_count(self, event=None):
        """Cập nhật số ký tự"""
        content = self.feedback_text.get("1.0", tk.END).strip()
        char_count = len(content)
        self.char_count_label.config(text=f"{char_count}/1000 ký tự")

        # Change color if approaching limit
        if char_count > 900:
            self.char_count_label.config(foreground="red")
        elif char_count > 800:
            self.char_count_label.config(foreground="orange")
        else:
            self.char_count_label.config(foreground="black")

    def validate_feedback_input(self):
        """Validate feedback input"""
        if not self.employee_id_entry.get().strip():
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập mã nhân viên!")
            self.employee_id_entry.focus()
            return False

        content = self.feedback_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập nội dung phản hồi!")
            self.feedback_text.focus()
            return False

        if len(content) > 1000:
            messagebox.showwarning("Cảnh báo", "Nội dung phản hồi không được vượt quá 1000 ký tự!")
            self.feedback_text.focus()
            return False

        return True

    def submit_feedback(self):
        """Gửi phản hồi"""
        if not self.validate_feedback_input():
            return

        try:
            employee_id = self.employee_id_entry.get().strip()
            if self.anonymous_var.get():
                employee_id = "ANONYMOUS"

            feedback_id = self.feedback_mgr.add_feedback_extended(
                employee_id=employee_id,
                content=self.feedback_text.get("1.0", tk.END).strip(),
                category=self.category_var.get(),
                priority=self.priority_var.get(),
                is_anonymous=self.anonymous_var.get(),
                status='Chờ xử lý'
            )

            messagebox.showinfo("Thành công", f"Gửi phản hồi thành công! Mã: {feedback_id}")
            self.clear_feedback_form()
            self.load_feedbacks()
            self.load_recent_feedbacks()

        except ValueError as e:
            messagebox.showerror("Lỗi validation", str(e))
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def load_feedbacks(self):
        """Load danh sách phản hồi"""
        # Clear existing items
        for item in self.feedback_tree.get_children():
            self.feedback_tree.delete(item)

        try:
            feedbacks = self.feedback_mgr.get_all_feedbacks_extended()

            for feedback in feedbacks:
                # feedback format: (id, feedback_id, employee_id, category, priority, subject, content, status, is_anonymous, created_date, updated_date, handler, response, response_date)
                display_values = (
                    feedback[0],  # ID
                    feedback[2],  # Employee ID
                    feedback[3],  # Category
                    feedback[4],  # Priority
                    feedback[7],  # Status
                    feedback[9][:10] if feedback[9] else '',  # Created date (only date part)
                    feedback[11] if feedback[11] else ''  # Handler
                )
                self.feedback_tree.insert("", "end", values=display_values)

        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def load_recent_feedbacks(self):
        """Load phản hồi gần đây"""
        self.recent_listbox.delete(0, tk.END)

        try:
            query = """
                SELECT employee_id, content, created_date 
                FROM Feedbacks 
                ORDER BY created_date DESC 
                LIMIT 5
            """
            self.feedback_mgr.db.execute(query)
            recent = self.feedback_mgr.db.fetch_all()

            for item in recent:
                display_text = f"{item[0]} - {item[1][:50]}..." if len(item[1]) > 50 else f"{item[0]} - {item[1]}"
                self.recent_listbox.insert(tk.END, display_text)

        except Exception as e:
            self.recent_listbox.insert(tk.END, "Không thể tải dữ liệu")

    def filter_feedbacks(self):
        """Lọc phản hồi theo điều kiện"""
        # Clear existing items
        for item in self.feedback_tree.get_children():
            self.feedback_tree.delete(item)

        try:
            conditions = []
            params = []

            if self.filter_status_var.get() != "Tất cả":
                conditions.append("status = ?")
                params.append(self.filter_status_var.get())

            if self.filter_category_var.get() != "Tất cả":
                conditions.append("category = ?")
                params.append(self.filter_category_var.get())

            if self.filter_priority_var.get() != "Tất cả":
                conditions.append("priority = ?")
                params.append(self.filter_priority_var.get())

            query = """
                SELECT id, employee_id, 
                       COALESCE(category, 'Chung') as category,
                       COALESCE(priority, 'Thấp') as priority,
                       COALESCE(status, 'Chờ xử lý') as status,
                       COALESCE(created_date, date('now')) as created_date,
                       COALESCE(handler, '') as handler
                FROM Feedbacks
            """

            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            query += " ORDER BY created_date DESC"

            self.feedback_mgr.db.execute(query, params)
            feedbacks = self.feedback_mgr.db.fetch_all()

            for feedback in feedbacks:
                self.feedback_tree.insert("", "end", values=feedback)

        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi lọc dữ liệu: {str(e)}")

    def on_feedback_select(self, event):
        """Xử lý khi chọn phản hồi"""
        selection = self.feedback_tree.selection()
        if selection:
            item = self.feedback_tree.item(selection[0])
            feedback_id = item['values'][0]

            try:
                # Load feedback detail
                self.feedback_mgr.db.execute("SELECT content FROM Feedbacks WHERE id = ?", (feedback_id,))
                result = self.feedback_mgr.db.fetch_one()

                if result:
                    self.feedback_detail.config(state="normal")
                    self.feedback_detail.delete("1.0", tk.END)
                    self.feedback_detail.insert("1.0", result[0])
                    self.feedback_detail.config(state="disabled")

                # Load existing response if any
                try:
                    self.feedback_mgr.db.execute("SELECT response FROM Feedbacks WHERE id = ?", (feedback_id,))
                    response_result = self.feedback_mgr.db.fetch_one()
                    if response_result and response_result[0]:
                        self.response_text.delete("1.0", tk.END)
                        self.response_text.insert("1.0", response_result[0])
                except:
                    pass

                # Set current status
                current_status = item['values'][4]
                self.update_status_var.set(current_status)

            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể tải chi tiết phản hồi: {str(e)}")

    def save_response(self):
        """Lưu phản hồi của HR"""
        selection = self.feedback_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn phản hồi cần trả lời!")
            return

        response_content = self.response_text.get("1.0", tk.END).strip()
        if not response_content:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập nội dung phản hồi!")
            return

        try:
            item = self.feedback_tree.item(selection[0])
            feedback_id = item['values'][0]

            # Update feedback with response and status
            self.feedback_mgr.add_response(feedback_id, response_content)

            # Update status if changed
            new_status = self.update_status_var.get()
            try:
                self.feedback_mgr.db.execute(
                    "UPDATE Feedbacks SET status = ?, handler = ? WHERE id = ?",
                    (new_status, "HR Admin", feedback_id)
                )
                self.feedback_mgr.db.commit()
            except:
                pass

            messagebox.showinfo("Thành công", "Lưu phản hồi thành công!")
            self.load_feedbacks()

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu phản hồi: {str(e)}")

    def send_email_response(self):
        """Gửi email phản hồi (placeholder)"""
        selection = self.feedback_tree.selection()
        if selection:
            item = self.feedback_tree.item(selection[0])
            employee_id = item['values'][1]
            messagebox.showinfo("Thông báo", f"Chức năng gửi email cho {employee_id} sẽ được phát triển!")

    def update_analytics(self):
        """Cập nhật thống kê"""
        try:
            stats = self.feedback_mgr.get_feedback_statistics()

            # Update stat labels
            self.stat_0_label.config(text=str(stats.get('total_feedbacks', 0)))
            self.stat_1_label.config(text=str(stats.get('by_status', {}).get('Chờ xử lý', 0)))
            self.stat_2_label.config(text=str(stats.get('by_status', {}).get('Đã xử lý', 0)))
            self.stat_3_label.config(text=f"{stats.get('resolution_rate', 0):.1f}%")

        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def clear_feedback_form(self):
        """Xóa form phản hồi"""
        self.employee_id_entry.delete(0, tk.END)
        self.feedback_text.delete("1.0", tk.END)
        self.category_var.set("Chung")
        self.priority_var.set("Thấp")
        self.anonymous_var.set(False)
        self.update_char_count()
