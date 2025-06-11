from src.db.database import get_db
import datetime
import re
import json


class EmployeeManager:
    def __init__(self):
        self.db = get_db()
        self._ensure_tables()

    def _ensure_tables(self):
        """Đảm bảo các bảng cần thiết tồn tại - đã được xử lý trong database.py"""
        pass

    def validate_employee_data(self, id, name, dept, salary, join_date, email=None, phone=None):
        """Validate dữ liệu nhân viên"""
        errors = []

        # Validate ID
        if not id or not id.strip():
            errors.append("Mã nhân viên không được để trống")
        elif not re.match(r'^[A-Z0-9]+$', id.strip()):
            errors.append("Mã nhân viên chỉ được chứa chữ cái in hoa và số")

        # Validate name
        if not name or not name.strip():
            errors.append("Tên nhân viên không được để trống")
        elif len(name.strip()) < 2:
            errors.append("Tên nhân viên phải có ít nhất 2 ký tự")

        # Validate department
        if not dept or not dept.strip():
            errors.append("Phòng ban không được để trống")

        # Validate salary
        try:
            salary_float = float(salary)
            if salary_float < 0:
                errors.append("Lương không được âm")
            elif salary_float > 1000000000:  # 1 tỷ
                errors.append("Lương không được vượt quá 1 tỷ VNĐ")
        except (ValueError, TypeError):
            errors.append("Lương phải là số")

        # Validate join_date
        try:
            datetime.datetime.strptime(join_date, "%Y-%m-%d")
        except ValueError:
            errors.append("Ngày vào làm phải có định dạng YYYY-MM-DD")

        # Validate email if provided
        if email and email.strip():
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email.strip()):
                errors.append("Email không hợp lệ")

        # Validate phone if provided
        if phone and phone.strip():
            phone_pattern = r'^[0-9+\-\s()]{10,15}$'
            if not re.match(phone_pattern, phone.strip().replace(' ', '')):
                errors.append("Số điện thoại không hợp lệ")

        return errors

    def employee_exists(self, employee_id):
        """Kiểm tra nhân viên có tồn tại không"""
        try:
            count = self.db.get_table_count('Employees', 'id = ?', [employee_id])
            return count > 0
        except Exception:
            return False

    def add_employee(self, id, name, dept, salary, join_date, email=None, phone=None, position=None):
        """Thêm nhân viên mới"""
        # Validate dữ liệu
        errors = self.validate_employee_data(id, name, dept, salary, join_date, email, phone)
        if errors:
            raise ValueError("; ".join(errors))

        # Kiểm tra trùng lặp
        if self.employee_exists(id):
            raise ValueError(f"Mã nhân viên {id} đã tồn tại")

        try:
            self.db.begin_transaction()

            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Sử dụng phương thức insert_record mới
            employee_data = {
                'id': id.strip(),
                'name': name.strip(),
                'department': dept.strip(),
                'salary': float(salary),
                'join_date': join_date,
                'email': email.strip() if email else None,
                'phone': phone.strip() if phone else None,
                'position': position.strip() if position else None,
                'status': 'Active',
                'created_date': current_time,
                'updated_date': current_time
            }

            result = self.db.insert_record('Employees', employee_data)

            # Log hành động
            self.db.log_action(
                user_id='system',
                action='ADD_EMPLOYEE',
                table_name='Employees',
                record_id=id.strip(),
                new_values=json.dumps(employee_data, default=str)
            )

            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Không thể thêm nhân viên: {str(e)}")

    def update_employee(self, id, name, dept, salary, join_date, email=None, phone=None, position=None):
        """Cập nhật thông tin nhân viên"""
        # Validate dữ liệu
        errors = self.validate_employee_data(id, name, dept, salary, join_date, email, phone)
        if errors:
            raise ValueError("; ".join(errors))

        # Kiểm tra nhân viên tồn tại
        if not self.employee_exists(id):
            raise ValueError(f"Không tìm thấy nhân viên với mã {id}")

        try:
            self.db.begin_transaction()

            # Lấy dữ liệu cũ để log
            old_data = self.get_employee_by_id(id)

            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Sử dụng phương thức update_record mới
            employee_data = {
                'name': name.strip(),
                'department': dept.strip(),
                'salary': float(salary),
                'join_date': join_date,
                'email': email.strip() if email else None,
                'phone': phone.strip() if phone else None,
                'position': position.strip() if position else None,
                'updated_date': current_time
            }

            self.db.update_record(
                'Employees',
                employee_data,
                'id = ?',
                [id.strip()]
            )

            # Log hành động
            self.db.log_action(
                user_id='system',
                action='UPDATE_EMPLOYEE',
                table_name='Employees',
                record_id=id.strip(),
                old_values=json.dumps(old_data, default=str) if old_data else None,
                new_values=json.dumps(employee_data, default=str)
            )

            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Không thể cập nhật nhân viên: {str(e)}")

    def delete_employee(self, id):
        """Xóa nhân viên (soft delete)"""
        if not id or not id.strip():
            raise ValueError("Mã nhân viên không được để trống")

        if not self.employee_exists(id):
            raise ValueError(f"Không tìm thấy nhân viên với mã {id}")

        try:
            self.db.begin_transaction()

            # Lấy dữ liệu cũ để log
            old_data = self.get_employee_by_id(id)

            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Sử dụng phương thức update_record mới
            self.db.update_record(
                'Employees',
                {'status': 'Deleted', 'updated_date': current_time},
                'id = ?',
                [id.strip()]
            )

            # Log hành động
            self.db.log_action(
                user_id='system',
                action='DELETE_EMPLOYEE',
                table_name='Employees',
                record_id=id.strip(),
                old_values=json.dumps(old_data, default=str) if old_data else None
            )

            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Không thể xóa nhân viên: {str(e)}")

    def search_employee(self, search_term):
        """Tìm kiếm nhân viên"""
        if not search_term or not search_term.strip():
            return self.get_all_employees()

        try:
            search_pattern = f"%{search_term.strip()}%"

            # Sử dụng phương thức select_records mới
            return self.db.select_records(
                'Employees',
                columns="id, name, department, salary, join_date, email, phone, position",
                condition="status != 'Deleted' AND (id LIKE ? OR name LIKE ? OR department LIKE ? OR position LIKE ?)",
                params=[search_pattern, search_pattern, search_pattern, search_pattern],
                order_by="name"
            )
        except Exception as e:
            raise Exception(f"Lỗi tìm kiếm: {str(e)}")

    def get_all_employees(self):
        """Lấy tất cả nhân viên active"""
        try:
            # Sử dụng phương thức select_records mới
            return self.db.select_records(
                'Employees',
                columns="id, name, department, salary, join_date, email, phone, position",
                condition="status != 'Deleted'",
                order_by="name"
            )
        except Exception as e:
            raise Exception(f"Không thể lấy danh sách nhân viên: {str(e)}")

    def get_employee_by_id(self, employee_id):
        """Lấy thông tin nhân viên theo ID"""
        try:
            # Sử dụng phương thức select_records mới
            result = self.db.select_records(
                'Employees',
                columns="id, name, department, salary, join_date, email, phone, position, status",
                condition="id = ? AND status != 'Deleted'",
                params=[employee_id]
            )
            return result[0] if result else None
        except Exception as e:
            raise Exception(f"Không thể lấy thông tin nhân viên: {str(e)}")

    def get_employees_by_department(self, department):
        """Lấy nhân viên theo phòng ban"""
        try:
            # Sử dụng phương thức select_records mới
            return self.db.select_records(
                'Employees',
                columns="id, name, department, salary, join_date, email, phone, position",
                condition="department = ? AND status != 'Deleted'",
                params=[department],
                order_by="name"
            )
        except Exception as e:
            raise Exception(f"Không thể lấy danh sách nhân viên theo phòng ban: {str(e)}")

    def get_employee_statistics(self):
        """Lấy thống kê nhân viên"""
        try:
            stats = {}

            # Tổng số nhân viên
            stats['total_employees'] = self.db.get_table_count('Employees', "status != 'Deleted'")

            # Thống kê theo phòng ban
            dept_stats = self.db.select_records(
                'Employees',
                columns="department, COUNT(*) as count, AVG(salary) as avg_salary",
                condition="status != 'Deleted'",
                order_by="count DESC",
                group_by="department"
            )
            stats['by_department'] = dept_stats

            # Lương trung bình
            avg_result = self.db.select_records(
                'Employees',
                columns="AVG(salary) as avg_salary",
                condition="status != 'Deleted'"
            )
            stats['avg_salary'] = avg_result[0][0] if avg_result and avg_result[0][0] else 0

            # Lương cao nhất và thấp nhất
            minmax_result = self.db.select_records(
                'Employees',
                columns="MAX(salary) as max_salary, MIN(salary) as min_salary",
                condition="status != 'Deleted'"
            )
            if minmax_result and len(minmax_result[0]) >= 2:
                stats['max_salary'] = minmax_result[0][0] if minmax_result[0][0] else 0
                stats['min_salary'] = minmax_result[0][1] if minmax_result[0][1] else 0
            else:
                stats['max_salary'] = 0
                stats['min_salary'] = 0

            return stats
        except Exception as e:
            raise Exception(f"Không thể lấy thống kê: {str(e)}")

    def get_departments(self):
        """Lấy danh sách phòng ban"""
        try:
            # Sử dụng phương thức select_records mới
            result = self.db.select_records(
                'Employees',
                columns="DISTINCT department",
                condition="status != 'Deleted' AND department IS NOT NULL",
                order_by="department"
            )
            return [row[0] for row in result]
        except Exception as e:
            return []
