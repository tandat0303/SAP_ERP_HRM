import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import calendar
from src.logic.salary import SalaryManager


class SalaryUI:
    def __init__(self, parent):
        self.parent = parent
        self.salary_mgr = SalaryManager()

        self.setup_styles()
        self.create_layout()
        self.load_salary_data()

    def setup_styles(self):
        """Cấu hình styles"""
        style = ttk.Style()

        style.configure("Title.TLabel",
                        font=("Arial", 20, "bold"),
                        background="#ecf0f1",
                        foreground="#2c3e50")

        style.configure("Highlight.TLabel",
                        font=("Arial", 12, "bold"),
                        background="#3498db",
                        foreground="white")

    def create_layout(self):
        """Tạo layout chính"""
        main_frame = ttk.Frame(self.parent, style="Content.TFrame")
        main_frame.pack(fill="both", expand=True)

        # Title
        title = ttk.Label(main_frame, text="💰 BÁO CÁO LƯƠNG", style="Title.TLabel")
        title.pack(pady=(0, 30))

        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True, padx=20)

        # Tab 1: Salary Report
        report_tab = ttk.Frame(notebook)
        notebook.add(report_tab, text="Báo cáo lương")

        # Tab 2: Payroll Calculation
        payroll_tab = ttk.Frame(notebook)
        notebook.add(payroll_tab, text="Tính lương")

        # Tab 3: Salary Analysis
        analysis_tab = ttk.Frame(notebook)
        notebook.add(analysis_tab, text="Phân tích lương")

        self.create_report_tab(report_tab)
        self.create_payroll_tab(payroll_tab)
        self.create_analysis_tab(analysis_tab)

    def create_report_tab(self, parent):
        """Tạo tab báo cáo lương"""
        container = ttk.Frame(parent, padding=20)
        container.pack(fill="both", expand=True)

        # Filter section
        filter_frame = ttk.LabelFrame(container, text="Bộ lọc báo cáo", padding=15)
        filter_frame.pack(fill="x", pady=(0, 20))

        # Month/Year selection
        ttk.Label(filter_frame, text="Tháng:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.month_var = tk.StringVar(value=str(datetime.now().month))
        month_combo = ttk.Combobox(filter_frame, textvariable=self.month_var, width=10,
                                   values=[str(i) for i in range(1, 13)])
        month_combo.grid(row=0, column=1, padx=(0, 20))
        month_combo.state(['readonly'])

        ttk.Label(filter_frame, text="Năm:").grid(row=0, column=2, sticky="w", padx=(0, 10))
        self.year_var = tk.StringVar(value=str(datetime.now().year))
        year_combo = ttk.Combobox(filter_frame, textvariable=self.year_var, width=10,
                                  values=[str(i) for i in range(2020, 2030)])
        year_combo.grid(row=0, column=3, padx=(0, 20))
        year_combo.state(['readonly'])

        # Department filter
        ttk.Label(filter_frame, text="Phòng ban:").grid(row=0, column=4, sticky="w", padx=(0, 10))
        self.dept_filter_var = tk.StringVar(value="Tất cả")
        dept_combo = ttk.Combobox(filter_frame, textvariable=self.dept_filter_var, width=15,
                                  values=["Tất cả", "IT", "HR", "Kế toán", "Marketing", "Bán hàng"])
        dept_combo.grid(row=0, column=5, padx=(0, 20))
        dept_combo.state(['readonly'])

        # Action buttons
        ttk.Button(filter_frame, text="📊 Xem báo cáo lương",
                   command=self.open_salary_report_window).grid(row=0, column=6, padx=10)
        ttk.Button(filter_frame, text="📈 Xem thống kê tổng quan",
                   command=self.open_statistics_window).grid(row=0, column=7, padx=5)

        # Quick actions section
        actions_frame = ttk.LabelFrame(container, text="Thao tác nhanh", padding=15)
        actions_frame.pack(fill="x", pady=(0, 20))

        # Quick action buttons
        quick_buttons = [
            ("📋 Báo cáo tháng hiện tại", self.open_current_month_report),
            ("📊 So sánh theo phòng ban", self.open_department_comparison),
            ("📈 Xu hướng lương 6 tháng", self.open_salary_trend),
            ("💰 Top lương cao nhất", self.open_top_salaries)
        ]

        for i, (text, command) in enumerate(quick_buttons):
            btn = ttk.Button(actions_frame, text=text, command=command, width=25)
            btn.grid(row=i // 2, column=i % 2, padx=10, pady=5, sticky="ew")

        # Configure grid weights
        actions_frame.grid_columnconfigure(0, weight=1)
        actions_frame.grid_columnconfigure(1, weight=1)

        # Info section
        info_frame = ttk.LabelFrame(container, text="Hướng dẫn", padding=15)
        info_frame.pack(fill="both", expand=True)

        info_text = """
📋 HƯỚNG DẪN SỬ DỤNG:

• Chọn tháng, năm và phòng ban để lọc dữ liệu
• Nhấn "Xem báo cáo lương" để mở bảng lương chi tiết
• Nhấn "Xem thống kê tổng quan" để xem các chỉ số tổng hợp
• Sử dụng các nút thao tác nhanh để xem báo cáo đặc biệt

💡 MẸO:
• Báo cáo sẽ mở trong cửa sổ riêng để dễ dàng so sánh
• Có thể xuất dữ liệu ra Excel từ cửa sổ báo cáo
• Sử dụng Ctrl+F để tìm kiếm trong bảng lương
        """

        info_label = ttk.Label(info_frame, text=info_text, font=("Arial", 10), justify="left")
        info_label.pack(anchor="w")

    def create_payroll_tab(self, parent):
        """Tạo tab tính lương"""
        container = ttk.Frame(parent, padding=20)
        container.pack(fill="both", expand=True)

        # Employee selection
        select_frame = ttk.LabelFrame(container, text="Chọn nhân viên", padding=15)
        select_frame.pack(fill="x", pady=(0, 20))

        ttk.Label(select_frame, text="Mã nhân viên:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.payroll_employee_var = tk.StringVar()
        employee_combo = ttk.Combobox(select_frame, textvariable=self.payroll_employee_var, width=20)
        employee_combo.grid(row=0, column=1, padx=(0, 20))

        ttk.Button(select_frame, text="🔍 Tải thông tin", command=self.load_employee_info).grid(row=0, column=2, padx=10)

        # Payroll calculation form
        calc_frame = ttk.LabelFrame(container, text="Tính toán lương", padding=20)
        calc_frame.pack(fill="both", expand=True)

        # Left panel - Input
        left_panel = ttk.Frame(calc_frame)
        left_panel.pack(side="left", fill="y", padx=(0, 20))

        # Basic salary info
        ttk.Label(left_panel, text="Thông tin cơ bản:", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2,
                                                                                         sticky="w", pady=(0, 10))

        fields = [
            ("Lương cơ bản:", "basic_salary"),
            ("Số ngày làm việc:", "work_days"),
            ("Số ngày nghỉ:", "absent_days"),
            ("Giờ làm thêm:", "overtime_hours"),
            ("Phụ cấp ăn trưa:", "lunch_allowance"),
            ("Phụ cấp xăng xe:", "transport_allowance"),
            ("Thưởng hiệu suất:", "performance_bonus"),
            ("Khấu trừ BHXH:", "social_insurance"),
            ("Khấu trừ thuế:", "tax_deduction"),
            ("Khấu trừ khác:", "other_deductions")
        ]

        self.payroll_entries = {}
        for i, (label_text, field_name) in enumerate(fields):
            row = i + 1
            ttk.Label(left_panel, text=label_text).grid(row=row, column=0, sticky="w", pady=5, padx=(0, 10))
            entry = ttk.Entry(left_panel, width=15, font=("Arial", 11))
            entry.grid(row=row, column=1, pady=5)
            self.payroll_entries[field_name] = entry

            # Set default values
            if field_name in ["work_days"]:
                entry.insert(0, "22")
            elif field_name in ["absent_days", "overtime_hours"]:
                entry.insert(0, "0")
            elif field_name in ["social_insurance"]:
                entry.insert(0, "8")  # 8% BHXH
            elif field_name in ["tax_deduction"]:
                entry.insert(0, "10")  # 10% thuế

        # Calculation buttons
        btn_frame = ttk.Frame(left_panel)
        btn_frame.grid(row=len(fields) + 1, column=0, columnspan=2, pady=20)

        ttk.Button(btn_frame, text="🧮 Tính lương", command=self.calculate_salary).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="📋 Xem chi tiết", command=self.open_payroll_detail_window).pack(side="left", padx=5)

        # Right panel - Quick result
        right_panel = ttk.LabelFrame(calc_frame, text="Kết quả nhanh", padding=15)
        right_panel.pack(side="right", fill="both", expand=True)

        # Quick result display
        self.quick_result_frame = ttk.Frame(right_panel)
        self.quick_result_frame.pack(fill="both", expand=True)

        # Result labels
        self.result_labels = {}
        result_items = [
            ("Lương cơ bản:", "basic_salary"),
            ("Tổng thu nhập:", "gross_salary"),
            ("Tổng khấu trừ:", "total_deductions"),
            ("Thực lĩnh:", "net_salary")
        ]

        for i, (label_text, key) in enumerate(result_items):
            ttk.Label(self.quick_result_frame, text=label_text, font=("Arial", 11, "bold")).grid(row=i, column=0,
                                                                                                 sticky="w", pady=5)
            value_label = ttk.Label(self.quick_result_frame, text="0 ₫", font=("Arial", 11), foreground="#2c3e50")
            value_label.grid(row=i, column=1, sticky="e", pady=5, padx=(10, 0))
            self.result_labels[key] = value_label

        # Save button
        ttk.Button(right_panel, text="💾 Lưu bảng lương", command=self.save_payroll).pack(pady=10)

    def create_analysis_tab(self, parent):
        """Tạo tab phân tích lương"""
        container = ttk.Frame(parent, padding=20)
        container.pack(fill="both", expand=True)

        # Analysis options
        options_frame = ttk.LabelFrame(container, text="Tùy chọn phân tích", padding=15)
        options_frame.pack(fill="x", pady=(0, 20))

        ttk.Label(options_frame, text="Loại phân tích:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.analysis_type_var = tk.StringVar(value="Theo phòng ban")
        analysis_combo = ttk.Combobox(options_frame, textvariable=self.analysis_type_var, width=20,
                                      values=["Theo phòng ban", "Theo thâm niên", "Theo mức lương", "Xu hướng lương"])
        analysis_combo.grid(row=0, column=1, padx=(0, 20))
        analysis_combo.state(['readonly'])

        ttk.Button(options_frame, text="📈 Xem phân tích", command=self.open_analysis_window).grid(row=0, column=2,
                                                                                                  padx=10)

        # Analysis shortcuts
        shortcuts_frame = ttk.LabelFrame(container, text="Phân tích nhanh", padding=15)
        shortcuts_frame.pack(fill="x", pady=(0, 20))

        analysis_buttons = [
            ("📊 Phân tích theo phòng ban", lambda: self.open_specific_analysis("Theo phòng ban")),
            ("⏰ Phân tích theo thâm niên", lambda: self.open_specific_analysis("Theo thâm niên")),
            ("💰 Phân tích theo mức lương", lambda: self.open_specific_analysis("Theo mức lương")),
            ("📈 Xu hướng lương", lambda: self.open_specific_analysis("Xu hướng lương"))
        ]

        for i, (text, command) in enumerate(analysis_buttons):
            btn = ttk.Button(shortcuts_frame, text=text, command=command, width=25)
            btn.grid(row=i // 2, column=i % 2, padx=10, pady=5, sticky="ew")

        shortcuts_frame.grid_columnconfigure(0, weight=1)
        shortcuts_frame.grid_columnconfigure(1, weight=1)

        # Charts placeholder
        charts_frame = ttk.LabelFrame(container, text="Biểu đồ và thống kê", padding=15)
        charts_frame.pack(fill="both", expand=True)

        chart_placeholder = ttk.Label(charts_frame,
                                      text="📊 Các biểu đồ phân tích sẽ được hiển thị trong cửa sổ riêng\n\n" +
                                           "💡 Nhấn các nút phân tích ở trên để xem chi tiết\n" +
                                           "📈 Hỗ trợ xuất dữ liệu và in ấn",
                                      font=("Arial", 12),
                                      justify="center")
        chart_placeholder.pack(expand=True)

    # Window creation methods
    def open_salary_report_window(self):
        """Mở cửa sổ báo cáo lương"""
        try:
            month = int(self.month_var.get())
            year = int(self.year_var.get())
            dept_filter = self.dept_filter_var.get()

            # Create new window
            report_window = tk.Toplevel(self.parent)
            report_window.title(f"Báo cáo lương tháng {month}/{year}")
            report_window.geometry("1000x600")
            report_window.resizable(True, True)

            # Window icon and properties
            report_window.transient(self.parent)
            report_window.grab_set()

            # Main frame
            main_frame = ttk.Frame(report_window, padding=10)
            main_frame.pack(fill="both", expand=True)

            # Header
            header_frame = ttk.Frame(main_frame)
            header_frame.pack(fill="x", pady=(0, 10))

            title_label = ttk.Label(header_frame,
                                    text=f"📊 BÁO CÁO LƯƠNG THÁNG {month}/{year}",
                                    font=("Arial", 16, "bold"))
            title_label.pack(side="left")

            # Export button
            export_btn = ttk.Button(header_frame, text="📤 Xuất Excel",
                                    command=lambda: self.export_salary_report(month, year, dept_filter))
            export_btn.pack(side="right")

            # Filter info
            filter_info = f"Phòng ban: {dept_filter}"
            ttk.Label(main_frame, text=filter_info, font=("Arial", 10)).pack(anchor="w")

            # Treeview for salary data
            tree_frame = ttk.Frame(main_frame)
            tree_frame.pack(fill="both", expand=True, pady=(10, 0))

            columns = ("Mã NV", "Tên", "Phòng ban", "Lương cơ bản", "Phụ cấp", "Thưởng", "Khấu trừ", "Thực lĩnh")
            tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20)

            # Configure columns
            column_widths = {
                "Mã NV": 80, "Tên": 150, "Phòng ban": 120, "Lương cơ bản": 120,
                "Phụ cấp": 100, "Thưởng": 100, "Khấu trừ": 100, "Thực lĩnh": 120
            }

            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=column_widths.get(col, 100), anchor="center")

            # Scrollbars
            v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
            h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

            tree.grid(row=0, column=0, sticky="nsew")
            v_scrollbar.grid(row=0, column=1, sticky="ns")
            h_scrollbar.grid(row=1, column=0, sticky="ew")

            tree_frame.grid_rowconfigure(0, weight=1)
            tree_frame.grid_columnconfigure(0, weight=1)

            # Load data
            self.load_salary_report_data(tree, month, year, dept_filter)

            # Summary frame
            summary_frame = ttk.LabelFrame(main_frame, text="Tổng kết", padding=10)
            summary_frame.pack(fill="x", pady=(10, 0))

            # Calculate and display summary
            self.display_salary_summary(summary_frame, tree)

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể mở báo cáo lương: {str(e)}")

    def open_statistics_window(self):
        """Mở cửa sổ thống kê tổng quan"""
        try:
            month = int(self.month_var.get())
            year = int(self.year_var.get())

            # Create new window
            stats_window = tk.Toplevel(self.parent)
            stats_window.title(f"Thống kê lương tháng {month}/{year}")
            stats_window.geometry("800x500")
            stats_window.resizable(True, True)

            stats_window.transient(self.parent)
            stats_window.grab_set()

            # Main frame
            main_frame = ttk.Frame(stats_window, padding=20)
            main_frame.pack(fill="both", expand=True)

            # Title
            title_label = ttk.Label(main_frame,
                                    text=f"📈 THỐNG KÊ LƯƠNG THÁNG {month}/{year}",
                                    font=("Arial", 16, "bold"))
            title_label.pack(pady=(0, 20))

            # Stats cards frame
            cards_frame = ttk.Frame(main_frame)
            cards_frame.pack(fill="x", pady=(0, 20))

            # Get statistics
            stats = self.salary_mgr.get_salary_statistics(month, year)

            # Create stat cards
            stat_cards = [
                ("👥 Tổng nhân viên", f"{stats.get('total_employees', 0)}", "#3498db"),
                ("💰 Tổng chi lương", f"{stats.get('total_salary', 0):,.0f} ₫", "#e74c3c"),
                ("📊 Lương trung bình", f"{stats.get('avg_salary', 0):,.0f} ₫", "#f39c12"),
                ("🏆 Lương cao nhất", f"{stats.get('max_salary', 0):,.0f} ₫", "#27ae60")
            ]

            for i, (title, value, color) in enumerate(stat_cards):
                card = ttk.LabelFrame(cards_frame, text=title, padding=15)
                card.grid(row=0, column=i, padx=10, sticky="ew")

                value_label = ttk.Label(card, text=value, font=("Arial", 14, "bold"))
                value_label.pack()

                cards_frame.grid_columnconfigure(i, weight=1)

            # Department breakdown
            dept_frame = ttk.LabelFrame(main_frame, text="Phân tích theo phòng ban", padding=15)
            dept_frame.pack(fill="both", expand=True)

            # Department treeview
            dept_columns = ("Phòng ban", "Số NV", "Tổng lương", "Lương TB")
            dept_tree = ttk.Treeview(dept_frame, columns=dept_columns, show="headings", height=10)

            for col in dept_columns:
                dept_tree.heading(col, text=col)
                dept_tree.column(col, width=150, anchor="center")

            # Load department data
            dept_data = stats.get('by_department', [])
            for dept_info in dept_data:
                dept_tree.insert("", "end", values=(
                    dept_info[0],  # department
                    dept_info[1],  # emp_count
                    f"{dept_info[2]:,.0f} ₫",  # total_salary
                    f"{dept_info[3]:,.0f} ₫"  # avg_salary
                ))

            dept_tree.pack(fill="both", expand=True)

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể mở thống kê: {str(e)}")

    def open_payroll_detail_window(self):
        """Mở cửa sổ chi tiết bảng lương"""
        if not hasattr(self, 'current_calculation'):
            messagebox.showwarning("Cảnh báo", "Vui lòng tính lương trước!")
            return

        try:
            # Create new window
            detail_window = tk.Toplevel(self.parent)
            detail_window.title("Chi tiết bảng lương")
            detail_window.geometry("600x700")
            detail_window.resizable(False, False)

            detail_window.transient(self.parent)
            detail_window.grab_set()

            # Main frame
            main_frame = ttk.Frame(detail_window, padding=20)
            main_frame.pack(fill="both", expand=True)

            # Title
            title_label = ttk.Label(main_frame,
                                    text="📋 CHI TIẾT BẢNG LƯƠNG",
                                    font=("Arial", 16, "bold"))
            title_label.pack(pady=(0, 20))

            # Detailed calculation display
            calc = self.current_calculation

            detail_text = f"""
╔══════════════════════════════════════╗
║           BẢNG TÍNH LƯƠNG            ║
╠══════════════════════════════════════╣
║ THÔNG TIN CƠ BẢN:                    ║
║ • Mã nhân viên: {calc['employee_id']:>17} ║
║ • Tháng/Năm: {calc['month']:>2}/{calc['year']:<15} ║
║ • Lương cơ bản: {calc['basic_salary']:>15,.0f} ₫ ║
║ • Ngày làm việc: {calc['work_days']:>14} ngày ║
║ • Ngày nghỉ: {calc['absent_days']:>18} ngày ║
║ • Giờ làm thêm: {calc['overtime_hours']:>15} giờ ║
╠══════════════════════════════════════╣
║ TÍNH TOÁN LƯƠNG:                     ║
║ • Tiền làm thêm: {calc['overtime_pay']:>13,.0f} ₫ ║
║ • Phụ cấp ăn trưa: {calc['lunch_allowance']:>11,.0f} ₫ ║
║ • Phụ cấp xăng xe: {calc['transport_allowance']:>11,.0f} ₫ ║
║ • Thưởng hiệu suất: {calc['performance_bonus']:>10,.0f} ₫ ║
║ • Thưởng khác: {calc.get('other_bonus', 0):>15,.0f} ₫ ║
║                                      ║
║ TỔNG LƯƠNG TRƯỚC KHẤU TRỪ: {calc['gross_salary']:>7,.0f} ₫ ║
╠══════════════════════════════════════╣
║ KHẤU TRỪ:                            ║
║ • BHXH: {calc['social_insurance']:>23,.0f} ₫ ║
║ • BHYT: {calc.get('health_insurance', 0):>23,.0f} ₫ ║
║ • BHTN: {calc.get('unemployment_insurance', 0):>23,.0f} ₫ ║
║ • Thuế TNCN: {calc['tax_deduction']:>17,.0f} ₫ ║
║ • Khấu trừ khác: {calc['other_deductions']:>13,.0f} ₫ ║
║                                      ║
║ TỔNG KHẤU TRỪ: {calc['total_deductions']:>17,.0f} ₫ ║
╠══════════════════════════════════════╣
║ LƯƠNG THỰC LĨNH: {calc['net_salary']:>15,.0f} ₫ ║
╚══════════════════════════════════════╝
            """

            # Text widget to display calculation
            text_widget = tk.Text(main_frame, font=("Courier", 10), height=30, width=50)
            text_widget.pack(fill="both", expand=True)
            text_widget.insert("1.0", detail_text)
            text_widget.config(state="disabled")

            # Buttons frame
            btn_frame = ttk.Frame(main_frame)
            btn_frame.pack(fill="x", pady=(10, 0))

            ttk.Button(btn_frame, text="💾 Lưu bảng lương",
                       command=lambda: self.save_payroll_from_window(detail_window)).pack(side="left", padx=5)
            ttk.Button(btn_frame, text="🖨️ In bảng lương",
                       command=self.print_payroll).pack(side="left", padx=5)
            ttk.Button(btn_frame, text="📤 Xuất PDF",
                       command=self.export_payroll_pdf).pack(side="left", padx=5)
            ttk.Button(btn_frame, text="❌ Đóng",
                       command=detail_window.destroy).pack(side="right", padx=5)

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể mở chi tiết bảng lương: {str(e)}")

    def open_analysis_window(self):
        """Mở cửa sổ phân tích"""
        analysis_type = self.analysis_type_var.get()
        self.open_specific_analysis(analysis_type)

    def open_specific_analysis(self, analysis_type):
        """Mở cửa sổ phân tích cụ thể"""
        try:
            # Create new window
            analysis_window = tk.Toplevel(self.parent)
            analysis_window.title(f"Phân tích lương - {analysis_type}")
            analysis_window.geometry("800x600")
            analysis_window.resizable(True, True)

            analysis_window.transient(self.parent)
            analysis_window.grab_set()

            # Main frame
            main_frame = ttk.Frame(analysis_window, padding=20)
            main_frame.pack(fill="both", expand=True)

            # Title
            title_label = ttk.Label(main_frame,
                                    text=f"📈 PHÂN TÍCH LƯƠNG - {analysis_type.upper()}",
                                    font=("Arial", 16, "bold"))
            title_label.pack(pady=(0, 20))

            # Analysis content
            analysis_frame = ttk.Frame(main_frame)
            analysis_frame.pack(fill="both", expand=True)

            # Get analysis data
            analysis_result = self.get_analysis_data(analysis_type)

            # Display analysis
            analysis_text = tk.Text(analysis_frame, font=("Courier", 11), wrap=tk.WORD)
            analysis_scrollbar = ttk.Scrollbar(analysis_frame, orient="vertical", command=analysis_text.yview)
            analysis_text.configure(yscrollcommand=analysis_scrollbar.set)

            analysis_text.pack(side="left", fill="both", expand=True)
            analysis_scrollbar.pack(side="right", fill="y")

            analysis_text.insert("1.0", analysis_result)
            analysis_text.config(state="disabled")

            # Buttons frame
            btn_frame = ttk.Frame(main_frame)
            btn_frame.pack(fill="x", pady=(10, 0))

            ttk.Button(btn_frame, text="📤 Xuất báo cáo",
                       command=lambda: self.export_analysis(analysis_type)).pack(side="left", padx=5)
            ttk.Button(btn_frame, text="🖨️ In báo cáo",
                       command=lambda: self.print_analysis(analysis_type)).pack(side="left", padx=5)
            ttk.Button(btn_frame, text="❌ Đóng",
                       command=analysis_window.destroy).pack(side="right", padx=5)

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể mở phân tích: {str(e)}")

    # Quick action methods
    def open_current_month_report(self):
        """Mở báo cáo tháng hiện tại"""
        self.month_var.set(str(datetime.now().month))
        self.year_var.set(str(datetime.now().year))
        self.dept_filter_var.set("Tất cả")
        self.open_salary_report_window()

    def open_department_comparison(self):
        """Mở so sánh theo phòng ban"""
        self.open_specific_analysis("Theo phòng ban")

    def open_salary_trend(self):
        """Mở xu hướng lương 6 tháng"""
        self.open_specific_analysis("Xu hướng lương")

    def open_top_salaries(self):
        """Mở top lương cao nhất"""
        try:
            # Create new window
            top_window = tk.Toplevel(self.parent)
            top_window.title("Top lương cao nhất")
            top_window.geometry("600x400")
            top_window.resizable(True, True)

            top_window.transient(self.parent)
            top_window.grab_set()

            # Main frame
            main_frame = ttk.Frame(top_window, padding=20)
            main_frame.pack(fill="both", expand=True)

            # Title
            title_label = ttk.Label(main_frame,
                                    text="🏆 TOP LƯƠNG CAO NHẤT",
                                    font=("Arial", 16, "bold"))
            title_label.pack(pady=(0, 20))

            # Top salaries treeview
            columns = ("Hạng", "Mã NV", "Tên", "Phòng ban", "Lương")
            tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)

            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100, anchor="center")

            # Load top salary data (sample)
            sample_data = [
                (1, "EMP001", "Nguyễn Văn A", "IT", "35,000,000"),
                (2, "EMP002", "Trần Thị B", "IT", "32,000,000"),
                (3, "EMP003", "Lê Văn C", "Marketing", "30,000,000"),
                (4, "EMP004", "Phạm Thị D", "HR", "28,000,000"),
                (5, "EMP005", "Hoàng Văn E", "IT", "27,000,000")
            ]

            for data in sample_data:
                tree.insert("", "end", values=data)

            tree.pack(fill="both", expand=True)

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể mở top lương: {str(e)}")

    # Helper methods
    def load_salary_report_data(self, tree, month, year, dept_filter):
        """Load dữ liệu báo cáo lương vào treeview"""
        try:
            # Clear existing items
            for item in tree.get_children():
                tree.delete(item)

            # Get report data from SalaryManager
            report_data = self.salary_mgr.get_monthly_payroll_report(month, year, dept_filter)

            for payroll in report_data:
                if len(payroll) >= 24:  # Ensure we have enough data
                    emp_id = payroll[2]  # employee_id
                    name = payroll[-2]  # name từ JOIN
                    dept = payroll[-1]  # department từ JOIN
                    basic_salary = payroll[4]
                    gross_salary = payroll[16]
                    net_salary = payroll[23]

                    # Calculate components
                    allowance = payroll[10] + payroll[11] + payroll[12]  # tổng phụ cấp
                    bonus = payroll[13] + payroll[14]  # tổng thưởng
                    deduction = payroll[22]  # tổng khấu trừ

                    tree.insert("", "end", values=(
                        emp_id, name, dept,
                        f"{basic_salary:,.0f}",
                        f"{allowance:,.0f}",
                        f"{bonus:,.0f}",
                        f"{deduction:,.0f}",
                        f"{net_salary:,.0f}"
                    ))

        except Exception as e:
            # Fallback to sample data
            sample_data = [
                ("EMP001", "Nguyễn Văn A", "IT", "20,000,000", "2,000,000", "3,000,000", "5,000,000", "20,000,000"),
                ("EMP002", "Trần Thị B", "HR", "18,000,000", "1,800,000", "2,000,000", "4,500,000", "17,300,000"),
                ("EMP003", "Lê Văn C", "Marketing", "22,000,000", "2,200,000", "4,000,000", "5,500,000", "22,700,000")
            ]

            for data in sample_data:
                tree.insert("", "end", values=data)

    def display_salary_summary(self, parent, tree):
        """Hiển thị tổng kết lương"""
        try:
            # Calculate summary from tree data
            total_employees = len(tree.get_children())
            total_salary = 0

            for item in tree.get_children():
                values = tree.item(item)['values']
                if len(values) > 7:
                    try:
                        salary = float(values[7].replace(',', ''))
                        total_salary += salary
                    except:
                        pass

            avg_salary = total_salary / total_employees if total_employees > 0 else 0

            # Display summary
            summary_text = f"""
📊 TỔNG KẾT:
• Tổng số nhân viên: {total_employees}
• Tổng chi lương: {total_salary:,.0f} ₫
• Lương trung bình: {avg_salary:,.0f} ₫
            """

            summary_label = ttk.Label(parent, text=summary_text, font=("Arial", 10))
            summary_label.pack(anchor="w")

        except Exception as e:
            ttk.Label(parent, text="Không thể tính tổng kết", font=("Arial", 10)).pack()

    def get_analysis_data(self, analysis_type):
        """Lấy dữ liệu phân tích"""
        if analysis_type == "Theo phòng ban":
            return """
📊 PHÂN TÍCH LƯƠNG THEO PHÒNG BAN

┌─────────────────────────────────────────────────────────┐
│ PHÒNG BAN        │ SỐ NV │ LƯƠNG TB    │ TỔNG LƯƠNG      │
├─────────────────────────────────────────────────────────┤
│ IT               │   15  │ 25,000,000  │ 375,000,000     │
│ HR               │    8  │ 18,000,000  │ 144,000,000     │
│ Kế toán          │    6  │ 20,000,000  │ 120,000,000     │
│ Marketing        │   10  │ 22,000,000  │ 220,000,000     │
│ Bán hàng         │   12  │ 19,000,000  │ 228,000,000     │
└─────────────────────────────────────────────────────────┘

📈 NHẬN XÉT:
• Phòng IT có mức lương trung bình cao nhất
• Phòng HR có số lượng nhân viên ít nhất
• Tổng chi phí lương: 1,087,000,000 VNĐ/tháng
• Mức lương trung bình toàn công ty: 21,294,118 VNĐ

💡 KHUYẾN NGHỊ:
• Xem xét tăng lương cho phòng HR để cân bằng
• Phòng IT đang có mức lương cạnh tranh tốt
• Cần đánh giá hiệu suất để điều chỉnh lương phù hợp
            """

        elif analysis_type == "Theo thâm niên":
            return """
📊 PHÂN TÍCH LƯƠNG THEO THÂM NIÊN

┌─────────────────────────────────────────────────────────┐
│ THÂM NIÊN        │ SỐ NV │ LƯƠNG TB    │ % TĂNG/NĂM      │
├─────────────────────────────────────────────────────────┤
│ < 1 năm          │   12  │ 15,000,000  │ -               │
│ 1-2 năm          │   18  │ 18,500,000  │ 23.3%           │
│ 3-5 năm          │   20  │ 23,000,000  │ 24.3%           │
│ 5-10 năm         │   15  │ 28,000,000  │ 21.7%           │
│ > 10 năm         │    6  │ 35,000,000  │ 25.0%           │
└─────────────────────────────────────────────────────────┘

📈 NHẬN XÉT:
• Mức tăng lương theo thâm niên khá đều
• Nhân viên mới chiếm tỷ lệ cao (42.3%)
• Cần chú ý giữ chân nhân viên có kinh nghiệm

💡 KHUYẾN NGHỊ:
• Xây dựng chương trình retention cho nhân viên senior
• Tăng cường đào tạo cho nhân viên mới
• Xem xét bonus thâm niên cho nhân viên lâu năm
            """

        elif analysis_type == "Theo mức lương":
            return """
📊 PHÂN TÍCH PHÂN BỐ LƯƠNG

┌─────────────────────────────────────────────────────────┐
│ KHOẢNG LƯƠNG     │ SỐ NV │ TỶ LỆ %     │ TỔNG LƯƠNG      │
├─────────────────────────────────────────────────────────┤
│ < 15 triệu       │    8  │  11.3%      │  96,000,000     │
│ 15-20 triệu      │   25  │  35.2%      │ 437,500,000     │
│ 20-25 triệu      │   18  │  25.4%      │ 405,000,000     │
│ 25-30 triệu      │   12  │  16.9%      │ 330,000,000     │
│ > 30 triệu       │    8  │  11.3%      │ 280,000,000     │
└─────────────────────────────────────────────────────────┘

📈 NHẬN XÉT:
• Phần lớn nhân viên có mức lương 15-25 triệu (60.6%)
• Chỉ có 11.3% nhân viên có mức lương > 30 triệu
• Cần xem xét điều chỉnh lương cho nhóm < 15 triệu

💡 KHUYẾN NGHỊ:
• Xây dựng thang lương rõ ràng theo vị trí
• Đánh giá thị trường để đảm bảo tính cạnh tranh
• Tạo cơ hội thăng tiến cho nhân viên
            """

        else:  # Xu hướng lương
            return """
📊 XU HƯỚNG LƯƠNG THEO THỜI GIAN

┌─────────────────────────────────────────────────────────┐
│ THỜI GIAN        │ LƯƠNG TB    │ % TĂNG     │ CHỈ SỐ CPI  │
├─────────────────────────────────────────────────────────┤
│ 2020             │ 16,500,000  │ -          │ 3.2%        │
│ 2021             │ 18,200,000  │ 10.3%      │ 3.8%        │
│ 2022             │ 19,800,000  │  8.8%      │ 4.5%        │
│ 2023             │ 21,300,000  │  7.6%      │ 3.9%        │
│ 2024             │ 23,500,000  │ 10.3%      │ 4.2%        │
└─────────────────────────────────────────────────────────┘

📈 NHẬN XÉT:
• Mức tăng lương trung bình hàng năm: 9.25%
• Mức tăng lương luôn cao hơn chỉ số CPI
• Xu hướng tăng lương ổn định qua các năm

💡 KHUYẾN NGHỊ:
• Duy trì chính sách tăng lương hàng năm
• Theo dõi chỉ số lạm phát để điều chỉnh phù hợp
• Xem xét tăng lương đột xuất cho các vị trí quan trọng
            """

    # Calculation and data methods
    def load_employee_list(self):
        """Load danh sách nhân viên cho combobox"""
        try:
            from ..logic.employee import EmployeeManager
            emp_mgr = EmployeeManager()
            employees = emp_mgr.get_all_employees()

            employee_list = [f"{emp[0]} - {emp[1]}" for emp in employees]

            # Update combobox values if it exists
            for widget in self.parent.winfo_children():
                if isinstance(widget, ttk.Combobox):
                    widget['values'] = employee_list
                    break

        except Exception as e:
            print(f"Error loading employees: {e}")

    def load_employee_info(self):
        """Load thông tin nhân viên được chọn"""
        selected = self.payroll_employee_var.get()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn nhân viên!")
            return

        try:
            employee_id = selected.split(" - ")[0]

            from ..logic.employee import EmployeeManager
            emp_mgr = EmployeeManager()
            employee = emp_mgr.get_employee_by_id(employee_id)

            if employee:
                basic_salary = employee[3]  # salary field
                self.payroll_entries['basic_salary'].delete(0, tk.END)
                self.payroll_entries['basic_salary'].insert(0, str(basic_salary))

                messagebox.showinfo("Thành công", f"Đã tải thông tin nhân viên {employee_id}")
            else:
                messagebox.showwarning("Cảnh báo", "Không tìm thấy thông tin nhân viên!")

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải thông tin nhân viên: {str(e)}")

    def calculate_salary(self):
        """Tính toán lương"""
        try:
            # Get input values
            basic_salary = float(self.payroll_entries['basic_salary'].get() or 0)
            work_days = int(self.payroll_entries['work_days'].get() or 22)
            absent_days = int(self.payroll_entries['absent_days'].get() or 0)
            overtime_hours = float(self.payroll_entries['overtime_hours'].get() or 0)
            lunch_allowance = float(self.payroll_entries['lunch_allowance'].get() or 0)
            transport_allowance = float(self.payroll_entries['transport_allowance'].get() or 0)
            performance_bonus = float(self.payroll_entries['performance_bonus'].get() or 0)
            social_insurance_rate = float(self.payroll_entries['social_insurance'].get() or 8)
            tax_rate = float(self.payroll_entries['tax_deduction'].get() or 10)
            other_deductions = float(self.payroll_entries['other_deductions'].get() or 0)

            # Calculate using SalaryManager
            actual_work_days = work_days - absent_days
            payroll_data = self.salary_mgr.calculate_payroll(
                employee_id=self.payroll_employee_var.get().split(" - ")[0] if self.payroll_employee_var.get() else "",
                month=datetime.now().month,
                year=datetime.now().year,
                basic_salary=basic_salary,
                work_days=work_days,
                actual_work_days=actual_work_days,
                absent_days=absent_days,
                overtime_hours=overtime_hours,
                lunch_allowance=lunch_allowance,
                transport_allowance=transport_allowance,
                performance_bonus=performance_bonus,
                social_insurance_rate=social_insurance_rate,
                tax_rate=tax_rate,
                other_deductions=other_deductions
            )

            # Update quick result display
            self.result_labels['basic_salary'].config(text=f"{payroll_data['basic_salary']:,.0f} ₫")
            self.result_labels['gross_salary'].config(text=f"{payroll_data['gross_salary']:,.0f} ₫")
            self.result_labels['total_deductions'].config(text=f"{payroll_data['total_deductions']:,.0f} ₫")
            self.result_labels['net_salary'].config(text=f"{payroll_data['net_salary']:,.0f} ₫", foreground="#27ae60")

            # Store calculation results
            self.current_calculation = payroll_data

            messagebox.showinfo("Thành công", "Tính lương thành công! Nhấn 'Xem chi tiết' để xem bảng lương đầy đủ.")

        except ValueError as e:
            messagebox.showerror("Lỗi", "Vui lòng nhập đúng định dạng số!")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def save_payroll(self):
        """Lưu bảng lương"""
        if not hasattr(self, 'current_calculation'):
            messagebox.showwarning("Cảnh báo", "Vui lòng tính lương trước khi lưu!")
            return

        try:
            payroll_id = self.salary_mgr.save_payroll(self.current_calculation)
            messagebox.showinfo("Thành công", f"Đã lưu bảng lương với mã: {payroll_id}")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def save_payroll_from_window(self, window):
        """Lưu bảng lương từ cửa sổ chi tiết"""
        self.save_payroll()
        window.destroy()

    # Export and print methods
    def export_salary_report(self, month, year, dept_filter):
        """Xuất báo cáo lương ra Excel"""
        messagebox.showinfo("Thông báo", f"Chức năng xuất Excel báo cáo tháng {month}/{year} sẽ được phát triển!")

    def export_analysis(self, analysis_type):
        """Xuất phân tích ra file"""
        messagebox.showinfo("Thông báo", f"Chức năng xuất phân tích '{analysis_type}' sẽ được phát triển!")

    def print_payroll(self):
        """In bảng lương"""
        messagebox.showinfo("Thông báo", "Chức năng in bảng lương sẽ được phát triển!")

    def print_analysis(self, analysis_type):
        """In phân tích"""
        messagebox.showinfo("Thông báo", f"Chức năng in phân tích '{analysis_type}' sẽ được phát triển!")

    def export_payroll_pdf(self):
        """Xuất bảng lương ra PDF"""
        messagebox.showinfo("Thông báo", "Chức năng xuất PDF sẽ được phát triển!")

    def load_salary_data(self):
        """Load dữ liệu lương ban đầu"""
        try:
            # Load employee list for payroll tab
            self.load_employee_list()
        except Exception as e:
            print(f"Error loading salary data: {e}")
