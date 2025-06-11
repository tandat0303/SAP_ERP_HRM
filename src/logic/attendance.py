from src.db.database import get_db
import datetime
import re
import json


class AttendanceManager:
    def __init__(self):
        self.db = get_db()
        self._ensure_tables()

    def _ensure_tables(self):
        """Đảm bảo các bảng cần thiết tồn tại - đã được xử lý trong database.py"""
        pass

    def validate_attendance_data(self, employee_id, date, time_in, time_out):
        """Validate dữ liệu chấm công"""
        errors = []

        # Validate employee_id
        if not employee_id or not employee_id.strip():
            errors.append("Mã nhân viên không được để trống")

        # Validate date
        try:
            date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
            # Không cho phép chấm công trong tương lai
            if date_obj.date() > datetime.date.today():
                errors.append("Không thể chấm công cho ngày trong tương lai")
        except ValueError:
            errors.append("Định dạng ngày không đúng (YYYY-MM-DD)")

        # Validate time format
        time_pattern = r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$'
        if not re.match(time_pattern, time_in):
            errors.append("Định dạng giờ vào không đúng (HH:MM)")
        if not re.match(time_pattern, time_out):
            errors.append("Định dạng giờ ra không đúng (HH:MM)")

        # Validate time logic
        try:
            time_in_obj = datetime.datetime.strptime(time_in, "%H:%M")
            time_out_obj = datetime.datetime.strptime(time_out, "%H:%M")

            # Handle overnight shifts
            if time_out_obj <= time_in_obj:
                # Assume time_out is next day
                time_out_obj = time_out_obj.replace(day=time_out_obj.day + 1)

            duration = time_out_obj - time_in_obj
            if duration.total_seconds() > 24 * 3600:  # More than 24 hours
                errors.append("Thời gian làm việc không được vượt quá 24 giờ")
            elif duration.total_seconds() < 3600:  # Less than 1 hour
                errors.append("Thời gian làm việc phải ít nhất 1 giờ")

        except ValueError:
            errors.append("Lỗi xử lý thời gian")

        return errors

    def calculate_work_hours(self, time_in, time_out):
        """Tính toán giờ làm việc và giờ làm thêm"""
        try:
            time_in_obj = datetime.datetime.strptime(time_in, "%H:%M")
            time_out_obj = datetime.datetime.strptime(time_out, "%H:%M")

            # Handle overnight shifts
            if time_out_obj <= time_in_obj:
                time_out_obj = time_out_obj.replace(day=time_out_obj.day + 1)

            duration = time_out_obj - time_in_obj
            total_hours = duration.total_seconds() / 3600

            # Standard work hours (8 hours)
            standard_hours = 8
            work_hours = min(total_hours, standard_hours)
            overtime_hours = max(0, total_hours - standard_hours)

            return round(work_hours, 2), round(overtime_hours, 2)
        except Exception:
            return 0, 0

    def attendance_exists(self, employee_id, date):
        """Kiểm tra đã chấm công cho ngày này chưa"""
        try:
            count = self.db.get_table_count(
                'Attendance',
                'employee_id = ? AND date = ?',
                [employee_id, date]
            )
            return count > 0
        except Exception:
            return False

    def add_attendance(self, employee_id, date, time_in, time_out, notes=None):
        """Thêm bản ghi chấm công"""
        # Validate dữ liệu
        errors = self.validate_attendance_data(employee_id, date, time_in, time_out)
        if errors:
            raise ValueError("; ".join(errors))

        # Kiểm tra trùng lặp
        if self.attendance_exists(employee_id, date):
            raise ValueError(f"Đã có bản ghi chấm công cho nhân viên {employee_id} ngày {date}")

        try:
            self.db.begin_transaction()

            # Tạo attendance_id
            count = self.db.get_table_count('Attendance')
            attendance_id = f"ATT{count + 1:06d}"

            # Tính toán giờ làm việc
            work_hours, overtime_hours = self.calculate_work_hours(time_in, time_out)

            # Xác định trạng thái
            status = self.determine_attendance_status(time_in, work_hours)

            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Sử dụng phương thức insert_record mới
            attendance_data = {
                'attendance_id': attendance_id,
                'employee_id': employee_id.strip(),
                'date': date,
                'time_in': time_in,
                'time_out': time_out,
                'work_hours': work_hours,
                'overtime_hours': overtime_hours,
                'status': status,
                'notes': notes,
                'created_date': current_time
            }

            self.db.insert_record('Attendance', attendance_data)

            # Log hành động
            self.db.log_action(
                user_id='system',
                action='ADD_ATTENDANCE',
                table_name='Attendance',
                record_id=attendance_id,
                new_values=json.dumps(attendance_data, default=str)
            )

            self.db.commit()
            return attendance_id
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Không thể thêm bản ghi chấm công: {str(e)}")

    def determine_attendance_status(self, time_in, work_hours):
        """Xác định trạng thái chấm công"""
        try:
            time_in_obj = datetime.datetime.strptime(time_in, "%H:%M")
            standard_start = datetime.datetime.strptime("08:00", "%H:%M")

            if time_in_obj > standard_start:
                return "Late"  # Đi muộn
            elif work_hours < 4:
                return "Half Day"  # Nửa ngày
            elif work_hours < 8:
                return "Early Leave"  # Về sớm
            else:
                return "Present"  # Đúng giờ
        except Exception:
            return "Present"

    def update_attendance(self, attendance_id, employee_id, date, time_in, time_out, notes=None):
        """Cập nhật bản ghi chấm công"""
        # Validate dữ liệu
        errors = self.validate_attendance_data(employee_id, date, time_in, time_out)
        if errors:
            raise ValueError("; ".join(errors))

        try:
            self.db.begin_transaction()

            # Lấy dữ liệu cũ để log
            old_data = self.get_attendance_by_id(attendance_id)

            # Tính toán lại giờ làm việc
            work_hours, overtime_hours = self.calculate_work_hours(time_in, time_out)
            status = self.determine_attendance_status(time_in, work_hours)

            # Sử dụng phương thức update_record mới
            attendance_data = {
                'employee_id': employee_id.strip(),
                'date': date,
                'time_in': time_in,
                'time_out': time_out,
                'work_hours': work_hours,
                'overtime_hours': overtime_hours,
                'status': status,
                'notes': notes
            }

            self.db.update_record(
                'Attendance',
                attendance_data,
                'attendance_id = ?',
                [attendance_id]
            )

            # Log hành động
            self.db.log_action(
                user_id='system',
                action='UPDATE_ATTENDANCE',
                table_name='Attendance',
                record_id=attendance_id,
                old_values=json.dumps(old_data, default=str) if old_data else None,
                new_values=json.dumps(attendance_data, default=str)
            )

            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Không thể cập nhật bản ghi chấm công: {str(e)}")

    def delete_attendance(self, attendance_id):
        """Xóa bản ghi chấm công"""
        try:
            self.db.begin_transaction()

            # Lấy dữ liệu cũ để log
            old_data = self.get_attendance_by_id(attendance_id)

            # Sử dụng phương thức delete_record mới
            self.db.delete_record('Attendance', 'attendance_id = ?', [attendance_id])

            # Log hành động
            self.db.log_action(
                user_id='system',
                action='DELETE_ATTENDANCE',
                table_name='Attendance',
                record_id=attendance_id,
                old_values=json.dumps(old_data, default=str) if old_data else None
            )

            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Không thể xóa bản ghi chấm công: {str(e)}")

    def get_attendance_by_id(self, attendance_id):
        """Lấy bản ghi chấm công theo ID"""
        try:
            result = self.db.select_records(
                'Attendance',
                condition='attendance_id = ?',
                params=[attendance_id]
            )
            return result[0] if result else None
        except Exception as e:
            return None

    def get_attendance_by_employee(self, employee_id, start_date=None, end_date=None):
        """Lấy chấm công theo nhân viên"""
        try:
            conditions = ["employee_id = ?"]
            params = [employee_id]

            if start_date:
                conditions.append("date >= ?")
                params.append(start_date)
            if end_date:
                conditions.append("date <= ?")
                params.append(end_date)

            return self.db.select_records(
                'Attendance',
                columns="attendance_id, employee_id, date, time_in, time_out, work_hours, overtime_hours, status, notes",
                condition=" AND ".join(conditions),
                params=params,
                order_by="date DESC"
            )
        except Exception as e:
            raise Exception(f"Không thể lấy dữ liệu chấm công: {str(e)}")

    def get_attendance_by_date_range(self, start_date, end_date, employee_id=None):
        """Lấy chấm công theo khoảng thời gian"""
        try:
            conditions = ["date BETWEEN ? AND ?"]
            params = [start_date, end_date]

            if employee_id:
                conditions.append("employee_id = ?")
                params.append(employee_id)

            return self.db.select_records(
                'Attendance',
                columns="attendance_id, employee_id, date, time_in, time_out, work_hours, overtime_hours, status, notes",
                condition=" AND ".join(conditions),
                params=params,
                order_by="date DESC, time_in DESC"
            )
        except Exception as e:
            raise Exception(f"Không thể lấy dữ liệu chấm công: {str(e)}")

    def get_attendance_statistics(self, start_date=None, end_date=None):
        """Lấy thống kê chấm công"""
        try:
            stats = {}

            # Base conditions
            conditions = []
            params = []
            if start_date and end_date:
                conditions.append("date BETWEEN ? AND ?")
                params = [start_date, end_date]

            condition_str = " AND ".join(conditions) if conditions else None

            # Tổng số bản ghi chấm công
            stats['total_records'] = self.db.get_table_count('Attendance', condition_str, params)

            # Thống kê theo trạng thái
            status_stats = self.db.select_records(
                'Attendance',
                columns="status, COUNT(*) as count",
                condition=condition_str,
                params=params,
                group_by="status"
            )
            stats['by_status'] = dict(status_stats)

            # Tổng giờ làm việc và làm thêm
            hours_result = self.db.select_records(
                'Attendance',
                columns="SUM(work_hours) as total_work, SUM(overtime_hours) as total_overtime",
                condition=condition_str,
                params=params
            )

            if hours_result and hours_result[0]:
                stats['total_work_hours'] = hours_result[0][0] if hours_result[0][0] else 0
                stats['total_overtime_hours'] = hours_result[0][1] if hours_result[0][1] else 0
            else:
                stats['total_work_hours'] = 0
                stats['total_overtime_hours'] = 0

            # Trung bình giờ làm việc mỗi ngày
            if stats['total_records'] > 0:
                stats['avg_work_hours'] = stats['total_work_hours'] / stats['total_records']
            else:
                stats['avg_work_hours'] = 0

            return stats
        except Exception as e:
            raise Exception(f"Không thể lấy thống kê chấm công: {str(e)}")

    def get_monthly_attendance_summary(self, year, month, employee_id=None):
        """Lấy tổng hợp chấm công theo tháng"""
        try:
            start_date = f"{year}-{month:02d}-01"
            # Get last day of month
            if month == 12:
                next_month = f"{year + 1}-01-01"
            else:
                next_month = f"{year}-{month + 1:02d}-01"

            conditions = ["date >= ? AND date < ?"]
            params = [start_date, next_month]

            if employee_id:
                conditions.append("employee_id = ?")
                params.append(employee_id)

            return self.db.select_records(
                'Attendance',
                columns="""employee_id, 
                          COUNT(*) as total_days,
                          SUM(work_hours) as total_work_hours,
                          SUM(overtime_hours) as total_overtime_hours,
                          SUM(CASE WHEN status = 'Late' THEN 1 ELSE 0 END) as late_days,
                          SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present_days""",
                condition=" AND ".join(conditions),
                params=params,
                group_by="employee_id",
                order_by="employee_id"
            )
        except Exception as e:
            raise Exception(f"Không thể lấy tổng hợp chấm công: {str(e)}")
