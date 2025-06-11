from src.db.database import get_db
import datetime
import calendar
import json


class SalaryManager:
    def __init__(self):
        self.db = get_db()
        self._ensure_tables()

    def _ensure_tables(self):
        """Đảm bảo các bảng cần thiết tồn tại - đã được xử lý trong database.py"""
        pass

    def generate_salary_report(self):
        """Tạo báo cáo lương (phương thức gốc để tương thích)"""
        try:
            report = []
            month = datetime.datetime.now().strftime("%Y-%m")

            # Lấy thông tin nhân viên và lương từ bảng Employees
            employees = self.db.select_records(
                'Employees',
                columns="id, name, salary",
                condition="status != 'Deleted'"
            )

            total_salary = 0
            for employee in employees:
                employee_id, name, salary = employee
                report.append(f"{employee_id} - {name} - Lương: {salary:,.0f} VNĐ")
                total_salary += salary

            report.append(f"Tổng lương tháng {month}: {total_salary:,.0f} VNĐ")
            return report
        except Exception as e:
            return [f"L��i tạo báo cáo: {str(e)}"]

    def calculate_payroll(self, employee_id, month, year, basic_salary, work_days=22,
                          actual_work_days=22, absent_days=0, overtime_hours=0,
                          allowances=0, lunch_allowance=0, transport_allowance=0,
                          performance_bonus=0, other_bonus=0, social_insurance_rate=8,
                          health_insurance_rate=1.5, unemployment_insurance_rate=1,
                          tax_rate=10, other_deductions=0):
        """Tính toán bảng lương chi tiết"""
        try:
            # Tính lương theo ngày làm việc
            daily_salary = basic_salary / work_days
            actual_work_salary = daily_salary * actual_work_days

            # Tính tiền làm thêm (1.5x lương giờ bình thường)
            hourly_salary = daily_salary / 8
            overtime_pay = overtime_hours * hourly_salary * 1.5

            # Tổng lương trước khấu trừ
            gross_salary = (actual_work_salary + overtime_pay + allowances +
                            lunch_allowance + transport_allowance + performance_bonus + other_bonus)

            # Tính các khoản khấu trừ
            social_insurance = gross_salary * (social_insurance_rate / 100)
            health_insurance = gross_salary * (health_insurance_rate / 100)
            unemployment_insurance = gross_salary * (unemployment_insurance_rate / 100)

            # Tính thuế thu nhập cá nhân (đơn giản hóa)
            taxable_income = gross_salary - social_insurance - health_insurance - unemployment_insurance
            tax_deduction = max(0, taxable_income * (tax_rate / 100))

            total_deductions = (social_insurance + health_insurance + unemployment_insurance +
                                tax_deduction + other_deductions)

            # Lương thực lĩnh
            net_salary = gross_salary - total_deductions

            return {
                'employee_id': employee_id,
                'month': month,
                'year': year,
                'basic_salary': basic_salary,
                'work_days': work_days,
                'actual_work_days': actual_work_days,
                'absent_days': absent_days,
                'overtime_hours': overtime_hours,
                'overtime_pay': overtime_pay,
                'allowances': allowances,
                'lunch_allowance': lunch_allowance,
                'transport_allowance': transport_allowance,
                'performance_bonus': performance_bonus,
                'other_bonus': other_bonus,
                'gross_salary': gross_salary,
                'social_insurance': social_insurance,
                'health_insurance': health_insurance,
                'unemployment_insurance': unemployment_insurance,
                'tax_deduction': tax_deduction,
                'other_deductions': other_deductions,
                'total_deductions': total_deductions,
                'net_salary': net_salary
            }
        except Exception as e:
            raise Exception(f"Lỗi tính toán lương: {str(e)}")

    def save_payroll(self, payroll_data, notes=None):
        """Lưu bảng lương vào database"""
        try:
            self.db.begin_transaction()

            # Tạo payroll_id
            count = self.db.get_table_count('Payrolls')
            payroll_id = f"PAY{count + 1:06d}"

            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Sử dụng phương thức insert_record mới
            payroll_record = {
                'payroll_id': payroll_id,
                'employee_id': payroll_data['employee_id'],
                'month': payroll_data['month'],
                'year': payroll_data['year'],
                'basic_salary': payroll_data['basic_salary'],
                'work_days': payroll_data['work_days'],
                'actual_work_days': payroll_data['actual_work_days'],
                'absent_days': payroll_data['absent_days'],
                'overtime_hours': payroll_data['overtime_hours'],
                'overtime_pay': payroll_data['overtime_pay'],
                'allowances': payroll_data['allowances'],
                'lunch_allowance': payroll_data['lunch_allowance'],
                'transport_allowance': payroll_data['transport_allowance'],
                'performance_bonus': payroll_data['performance_bonus'],
                'other_bonus': payroll_data['other_bonus'],
                'gross_salary': payroll_data['gross_salary'],
                'social_insurance': payroll_data['social_insurance'],
                'health_insurance': payroll_data['health_insurance'],
                'unemployment_insurance': payroll_data['unemployment_insurance'],
                'tax_deduction': payroll_data['tax_deduction'],
                'other_deductions': payroll_data['other_deductions'],
                'total_deductions': payroll_data['total_deductions'],
                'net_salary': payroll_data['net_salary'],
                'status': 'Draft',
                'notes': notes,
                'created_date': current_time,
                'updated_date': current_time
            }

            self.db.insert_record('Payrolls', payroll_record)

            # Log hành động
            self.db.log_action(
                user_id='system',
                action='SAVE_PAYROLL',
                table_name='Payrolls',
                record_id=payroll_id,
                new_values=json.dumps(payroll_record, default=str)
            )

            self.db.commit()
            return payroll_id
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Không thể lưu bảng lương: {str(e)}")

    def get_payroll_by_employee(self, employee_id, month=None, year=None):
        """Lấy bảng lương theo nhân viên"""
        try:
            conditions = ["employee_id = ?"]
            params = [employee_id]

            if month:
                conditions.append("month = ?")
                params.append(month)
            if year:
                conditions.append("year = ?")
                params.append(year)

            return self.db.select_records(
                'Payrolls',
                condition=" AND ".join(conditions),
                params=params,
                order_by="year DESC, month DESC"
            )
        except Exception as e:
            raise Exception(f"Không thể lấy bảng lương: {str(e)}")

    def get_monthly_payroll_report(self, month, year, department=None):
        """Lấy báo cáo lương theo tháng"""
        try:
            if department and department != "Tất cả":
                return self.db.select_records(
                    'Payrolls p',
                    columns="p.*, e.name, e.department",
                    condition="p.month = ? AND p.year = ? AND e.department = ?",
                    params=[month, year, department],
                    joins="JOIN Employees e ON p.employee_id = e.id",
                    order_by="e.name"
                )
            else:
                return self.db.select_records(
                    'Payrolls p',
                    columns="p.*, e.name, e.department",
                    condition="p.month = ? AND p.year = ?",
                    params=[month, year],
                    joins="JOIN Employees e ON p.employee_id = e.id",
                    order_by="e.name"
                )
        except Exception as e:
            raise Exception(f"Không thể lấy báo cáo lương tháng: {str(e)}")

    def get_salary_statistics(self, month=None, year=None):
        """Lấy thống kê lương"""
        try:
            stats = {}

            # Điều kiện thời gian
            conditions = []
            params = []
            if month and year:
                conditions.append("month = ? AND year = ?")
                params = [month, year]

            condition_str = " AND ".join(conditions) if conditions else None

            # Tổng số nhân viên có lương
            stats['total_employees'] = self.db.get_table_count(
                'Payrolls',
                'DISTINCT employee_id' + (' WHERE ' + condition_str if condition_str else ''),
                params
            )

            # Tổng chi lương
            salary_result = self.db.select_records(
                'Payrolls',
                columns="SUM(net_salary) as total_salary",
                condition=condition_str,
                params=params
            )
            stats['total_salary'] = salary_result[0][0] if salary_result and salary_result[0][0] else 0

            # Lương trung bình
            if stats['total_employees'] > 0:
                stats['avg_salary'] = stats['total_salary'] / stats['total_employees']
            else:
                stats['avg_salary'] = 0

            # Lương cao nhất và thấp nhất
            minmax_result = self.db.select_records(
                'Payrolls',
                columns="MAX(net_salary) as max_salary, MIN(net_salary) as min_salary",
                condition=condition_str,
                params=params
            )
            if minmax_result and minmax_result[0]:
                stats['max_salary'] = minmax_result[0][0] if minmax_result[0][0] else 0
                stats['min_salary'] = minmax_result[0][1] if len(minmax_result[0]) > 1 and minmax_result[0][1] else 0
            else:
                stats['max_salary'] = 0
                stats['min_salary'] = 0

            # Thống kê theo phòng ban
            if month and year:
                dept_stats = self.db.select_records(
                    'Payrolls p',
                    columns="e.department, COUNT(*) as emp_count, SUM(p.net_salary) as total_salary, AVG(p.net_salary) as avg_salary",
                    condition="p.month = ? AND p.year = ?",
                    params=[month, year],
                    joins="JOIN Employees e ON p.employee_id = e.id",
                    group_by="e.department",
                    order_by="total_salary DESC"
                )
            else:
                dept_stats = self.db.select_records(
                    'Payrolls p',
                    columns="e.department, COUNT(*) as emp_count, SUM(p.net_salary) as total_salary, AVG(p.net_salary) as avg_salary",
                    joins="JOIN Employees e ON p.employee_id = e.id",
                    group_by="e.department",
                    order_by="total_salary DESC"
                )

            stats['by_department'] = dept_stats

            return stats
        except Exception as e:
            raise Exception(f"Không thể lấy thống kê lương: {str(e)}")

    def analyze_salary_trends(self, employee_id=None, months=12):
        """Phân tích xu hướng lương"""
        try:
            # Lấy dữ liệu lương trong X tháng gần nhất
            if employee_id:
                trend_data = self.db.select_records(
                    'Payrolls',
                    columns="year, month, net_salary",
                    condition="employee_id = ?",
                    params=[employee_id],
                    order_by="year DESC, month DESC",
                    limit=months
                )
            else:
                trend_data = self.db.select_records(
                    'Payrolls',
                    columns="year, month, AVG(net_salary) as avg_salary",
                    group_by="year, month",
                    order_by="year DESC, month DESC",
                    limit=months
                )

            if len(trend_data) < 2:
                return {"trend": "Không đủ dữ liệu", "growth_rate": 0}

            # Tính tỷ lệ tăng trưởng
            latest_salary = trend_data[0][2] if len(trend_data[0]) > 2 else trend_data[0][1]
            oldest_salary = trend_data[-1][2] if len(trend_data[-1]) > 2 else trend_data[-1][1]

            if oldest_salary > 0:
                growth_rate = ((latest_salary - oldest_salary) / oldest_salary) * 100
            else:
                growth_rate = 0

            # Xác định xu hướng
            if growth_rate > 5:
                trend = "Tăng mạnh"
            elif growth_rate > 0:
                trend = "Tăng nhẹ"
            elif growth_rate > -5:
                trend = "Ổn định"
            else:
                trend = "Giảm"

            return {
                "trend": trend,
                "growth_rate": round(growth_rate, 2),
                "data_points": len(trend_data),
                "latest_salary": latest_salary,
                "oldest_salary": oldest_salary
            }
        except Exception as e:
            raise Exception(f"Không thể phân tích xu hướng lương: {str(e)}")

    def add_salary_component(self, employee_id, component_type, component_name, amount,
                             is_recurring=True, effective_date=None, end_date=None):
        """Thêm thành phần lương (phụ cấp, thưởng, khấu trừ)"""
        valid_types = ['allowance', 'bonus', 'deduction']
        if component_type not in valid_types:
            raise ValueError(f"Loại thành phần không hợp lệ. Chỉ chấp nhận: {', '.join(valid_types)}")

        try:
            self.db.begin_transaction()

            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            component_data = {
                'employee_id': employee_id,
                'component_type': component_type,
                'component_name': component_name,
                'amount': amount,
                'is_recurring': is_recurring,
                'effective_date': effective_date,
                'end_date': end_date,
                'created_date': current_time
            }

            self.db.insert_record('SalaryComponents', component_data)

            # Log hành động
            self.db.log_action(
                user_id='system',
                action='ADD_SALARY_COMPONENT',
                table_name='SalaryComponents',
                record_id=employee_id,
                new_values=json.dumps(component_data, default=str)
            )

            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Không thể thêm thành phần lương: {str(e)}")

    def get_salary_components(self, employee_id, component_type=None):
        """Lấy các thành phần lương của nhân viên"""
        try:
            conditions = ["employee_id = ?"]
            params = [employee_id]

            if component_type:
                conditions.append("component_type = ?")
                params.append(component_type)

            return self.db.select_records(
                'SalaryComponents',
                condition=" AND ".join(conditions),
                params=params,
                order_by="created_date DESC"
            )
        except Exception as e:
            raise Exception(f"Không thể lấy thành phần lương: {str(e)}")

    def update_payroll_status(self, payroll_id, new_status):
        """Cập nhật trạng thái bảng lương"""
        valid_statuses = ['Draft', 'Approved', 'Paid', 'Cancelled']
        if new_status not in valid_statuses:
            raise ValueError(f"Trạng thái không hợp lệ. Chỉ chấp nhận: {', '.join(valid_statuses)}")

        try:
            self.db.begin_transaction()

            # Lấy dữ liệu cũ để log
            old_data = self.get_payroll_by_id(payroll_id)

            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            update_data = {
                'status': new_status,
                'updated_date': current_time
            }

            self.db.update_record(
                'Payrolls',
                update_data,
                'payroll_id = ?',
                [payroll_id]
            )

            # Log hành động
            self.db.log_action(
                user_id='system',
                action='UPDATE_PAYROLL_STATUS',
                table_name='Payrolls',
                record_id=payroll_id,
                old_values=json.dumps(old_data, default=str) if old_data else None,
                new_values=json.dumps(update_data, default=str)
            )

            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Không thể cập nhật trạng thái bảng lương: {str(e)}")

    def get_payroll_by_id(self, payroll_id):
        """Lấy bảng lương theo ID"""
        try:
            result = self.db.select_records(
                'Payrolls',
                condition='payroll_id = ?',
                params=[payroll_id]
            )
            return result[0] if result else None
        except Exception as e:
            return None

    def delete_payroll(self, payroll_id):
        """Xóa bảng lương"""
        try:
            self.db.begin_transaction()

            # Lấy dữ liệu cũ để log
            old_data = self.get_payroll_by_id(payroll_id)

            self.db.delete_record('Payrolls', 'payroll_id = ?', [payroll_id])

            # Log hành động
            self.db.log_action(
                user_id='system',
                action='DELETE_PAYROLL',
                table_name='Payrolls',
                record_id=payroll_id,
                old_values=json.dumps(old_data, default=str) if old_data else None
            )

            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Không thể xóa bảng lương: {str(e)}")

    def export_payroll_data(self, month, year, format='dict'):
        """Xuất dữ liệu lương để export"""
        try:
            data = self.db.select_records(
                'Payrolls p',
                columns="p.*, e.name, e.department",
                condition="p.month = ? AND p.year = ?",
                params=[month, year],
                joins="JOIN Employees e ON p.employee_id = e.id",
                order_by="e.department, e.name"
            )

            if format == 'dict':
                # Chuyển đổi thành dictionary để dễ xử lý
                columns = [
                    'id', 'payroll_id', 'employee_id', 'month', 'year', 'basic_salary',
                    'work_days', 'actual_work_days', 'absent_days', 'overtime_hours',
                    'overtime_pay', 'allowances', 'lunch_allowance', 'transport_allowance',
                    'performance_bonus', 'other_bonus', 'gross_salary', 'social_insurance',
                    'health_insurance', 'unemployment_insurance', 'tax_deduction',
                    'other_deductions', 'total_deductions', 'net_salary', 'status',
                    'notes', 'created_date', 'updated_date', 'name', 'department'
                ]
                return [dict(zip(columns, row)) for row in data]
            else:
                return data
        except Exception as e:
            raise Exception(f"Không thể xuất dữ liệu lương: {str(e)}")
