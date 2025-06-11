from src.db.database import get_db
import datetime
import re
import json


class CandidateManager:
    def __init__(self):
        self.db = get_db()
        self._ensure_tables()

    def _ensure_tables(self):
        """Đảm bảo các bảng cần thiết tồn tại - đã được xử lý trong database.py"""
        pass

    def validate_candidate_data(self, name, email, position, phone=None, experience=None):
        """Validate dữ liệu ứng viên"""
        errors = []

        # Validate name
        if not name or not name.strip():
            errors.append("Tên ứng viên không được để trống")
        elif len(name.strip()) < 2:
            errors.append("Tên ứng viên phải có ít nhất 2 ký tự")

        # Validate email
        if not email or not email.strip():
            errors.append("Email không được để trống")
        else:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email.strip()):
                errors.append("Email không hợp lệ")

        # Validate position
        if not position or not position.strip():
            errors.append("Vị trí ứng tuyển không được để trống")

        # Validate phone if provided
        if phone and phone.strip():
            phone_pattern = r'^[0-9+\-\s()]{10,15}$'
            if not re.match(phone_pattern, phone.strip().replace(' ', '')):
                errors.append("Số điện thoại không hợp lệ")

        # Validate experience if provided
        if experience is not None:
            try:
                exp_int = int(experience)
                if exp_int < 0:
                    errors.append("Kinh nghiệm không được âm")
                elif exp_int > 50:
                    errors.append("Kinh nghiệm không được vượt quá 50 năm")
            except (ValueError, TypeError):
                errors.append("Kinh nghiệm phải là số")

        return errors

    def email_exists(self, email, exclude_id=None):
        """Kiểm tra email đã tồn tại chưa"""
        try:
            conditions = ["email = ?"]
            params = [email]

            if exclude_id:
                conditions.append("id != ?")
                params.append(exclude_id)

            count = self.db.get_table_count(
                'Candidates',
                " AND ".join(conditions),
                params
            )
            return count > 0
        except Exception:
            return False

    def add_candidate(self, name, email, position):
        """Thêm ứng viên mới (phương thức gốc để tương thích)"""
        return self.add_candidate_extended(name=name, email=email, position=position)

    def add_candidate_extended(self, name, email, position, phone=None, experience=0,
                               education=None, skills=None, status='Chờ xử lý', notes=None):
        """Thêm ứng viên mới với thông tin mở rộng"""
        # Validate dữ liệu
        errors = self.validate_candidate_data(name, email, position, phone, experience)
        if errors:
            raise ValueError("; ".join(errors))

        # Kiểm tra email trùng lặp
        if self.email_exists(email):
            raise ValueError(f"Email {email} đã tồn tại")

        try:
            self.db.begin_transaction()

            # Tạo candidate_id
            count = self.db.get_table_count('Candidates')
            candidate_id = f"CAN{count + 1:06d}"

            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            application_date = datetime.datetime.now().strftime("%Y-%m-%d")

            # Sử dụng phương thức insert_record mới
            candidate_data = {
                'candidate_id': candidate_id,
                'name': name.strip(),
                'email': email.strip(),
                'phone': phone.strip() if phone else None,
                'position': position.strip(),
                'experience': int(experience) if experience else 0,
                'education': education.strip() if education else None,
                'skills': skills.strip() if skills else None,
                'status': status,
                'application_date': application_date,
                'notes': notes,
                'created_date': current_time,
                'updated_date': current_time
            }

            self.db.insert_record('Candidates', candidate_data)

            # Log hành động
            self.db.log_action(
                user_id='system',
                action='ADD_CANDIDATE',
                table_name='Candidates',
                record_id=candidate_id,
                new_values=json.dumps(candidate_data, default=str)
            )

            self.db.commit()
            return candidate_id
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Không thể thêm ứng viên: {str(e)}")

    def update_candidate_extended(self, id, name, email, position, phone=None, experience=0,
                                  education=None, skills=None, status='Chờ xử lý', notes=None):
        """Cập nhật thông tin ứng viên"""
        # Validate dữ liệu
        errors = self.validate_candidate_data(name, email, position, phone, experience)
        if errors:
            raise ValueError("; ".join(errors))

        # Kiểm tra email trùng lặp (trừ chính ứng viên này)
        if self.email_exists(email, exclude_id=id):
            raise ValueError(f"Email {email} đã được sử dụng bởi ứng viên khác")

        try:
            self.db.begin_transaction()

            # Lấy dữ liệu cũ để log
            old_data = self.get_candidate_by_id(id)

            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Sử dụng phương thức update_record mới
            candidate_data = {
                'name': name.strip(),
                'email': email.strip(),
                'phone': phone.strip() if phone else None,
                'position': position.strip(),
                'experience': int(experience) if experience else 0,
                'education': education.strip() if education else None,
                'skills': skills.strip() if skills else None,
                'status': status,
                'notes': notes,
                'updated_date': current_time
            }

            self.db.update_record(
                'Candidates',
                candidate_data,
                'id = ?',
                [id]
            )

            # Log hành động
            self.db.log_action(
                user_id='system',
                action='UPDATE_CANDIDATE',
                table_name='Candidates',
                record_id=str(id),
                old_values=json.dumps(old_data, default=str) if old_data else None,
                new_values=json.dumps(candidate_data, default=str)
            )

            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Không thể cập nhật ứng viên: {str(e)}")

    def delete_candidate(self, candidate_id):
        """Xóa ứng viên"""
        try:
            self.db.begin_transaction()

            # Lấy dữ liệu cũ để log
            old_data = self.get_candidate_by_id(candidate_id)

            # Sử dụng phương thức delete_record mới
            self.db.delete_record(
                'Candidates',
                'id = ? OR candidate_id = ?',
                [candidate_id, candidate_id]
            )

            # Log hành động
            self.db.log_action(
                user_id='system',
                action='DELETE_CANDIDATE',
                table_name='Candidates',
                record_id=str(candidate_id),
                old_values=json.dumps(old_data, default=str) if old_data else None
            )

            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Không thể xóa ứng viên: {str(e)}")

    def get_candidate_by_id(self, candidate_id):
        """Lấy ứng viên theo ID"""
        try:
            result = self.db.select_records(
                'Candidates',
                condition='id = ? OR candidate_id = ?',
                params=[candidate_id, candidate_id]
            )
            return result[0] if result else None
        except Exception as e:
            return None

    def get_all_candidates(self):
        """Lấy tất cả ứng viên"""
        try:
            return self.db.select_records(
                'Candidates',
                columns="id, candidate_id, name, email, phone, position, experience, education, skills, status, application_date, interview_date, notes",
                order_by="application_date DESC"
            )
        except Exception as e:
            raise Exception(f"Không thể lấy danh sách ứng viên: {str(e)}")

    def search_candidates(self, search_term):
        """Tìm kiếm ứng viên"""
        if not search_term or not search_term.strip():
            return self.get_all_candidates()

        try:
            search_pattern = f"%{search_term.strip()}%"
            return self.db.select_records(
                'Candidates',
                columns="id, candidate_id, name, email, phone, position, experience, education, skills, status, application_date, interview_date, notes",
                condition="name LIKE ? OR email LIKE ? OR position LIKE ? OR skills LIKE ?",
                params=[search_pattern, search_pattern, search_pattern, search_pattern],
                order_by="application_date DESC"
            )
        except Exception as e:
            raise Exception(f"Lỗi tìm kiếm ứng viên: {str(e)}")

    def get_candidates_by_status(self, status):
        """Lấy ứng viên theo trạng thái"""
        try:
            return self.db.select_records(
                'Candidates',
                columns="id, candidate_id, name, email, phone, position, experience, education, skills, status, application_date, interview_date, notes",
                condition="status = ?",
                params=[status],
                order_by="application_date DESC"
            )
        except Exception as e:
            raise Exception(f"Không thể lấy ứng viên theo trạng thái: {str(e)}")

    def get_candidates_by_position(self, position):
        """Lấy ứng viên theo vị trí"""
        try:
            return self.db.select_records(
                'Candidates',
                columns="id, candidate_id, name, email, phone, position, experience, education, skills, status, application_date, interview_date, notes",
                condition="position LIKE ?",
                params=[f"%{position}%"],
                order_by="application_date DESC"
            )
        except Exception as e:
            raise Exception(f"Không thể lấy ứng viên theo vị trí: {str(e)}")

    def update_candidate_status(self, candidate_id, new_status, notes=None):
        """Cập nhật trạng thái ứng viên"""
        valid_statuses = ['Chờ xử lý', 'Đã phỏng vấn', 'Đậu', 'Trượt', 'Từ chối']
        if new_status not in valid_statuses:
            raise ValueError(f"Trạng thái không hợp lệ. Chỉ chấp nhận: {', '.join(valid_statuses)}")

        try:
            self.db.begin_transaction()

            # Lấy dữ liệu cũ để log
            old_data = self.get_candidate_by_id(candidate_id)

            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            update_data = {
                'status': new_status,
                'updated_date': current_time
            }

            if notes:
                update_data['notes'] = notes

            self.db.update_record(
                'Candidates',
                update_data,
                'id = ? OR candidate_id = ?',
                [candidate_id, candidate_id]
            )

            # Log hành động
            self.db.log_action(
                user_id='system',
                action='UPDATE_CANDIDATE_STATUS',
                table_name='Candidates',
                record_id=str(candidate_id),
                old_values=json.dumps(old_data, default=str) if old_data else None,
                new_values=json.dumps(update_data, default=str)
            )

            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Không thể cập nhật trạng thái ứng viên: {str(e)}")

    def schedule_interview(self, candidate_id, interview_date, notes=None):
        """Lên lịch phỏng vấn"""
        try:
            # Validate date format
            datetime.datetime.strptime(interview_date, "%Y-%m-%d")

            self.db.begin_transaction()

            # Lấy dữ liệu cũ để log
            old_data = self.get_candidate_by_id(candidate_id)

            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            update_data = {
                'interview_date': interview_date,
                'status': 'Đã phỏng vấn',
                'updated_date': current_time
            }

            if notes:
                update_data['notes'] = notes

            self.db.update_record(
                'Candidates',
                update_data,
                'id = ? OR candidate_id = ?',
                [candidate_id, candidate_id]
            )

            # Log hành động
            self.db.log_action(
                user_id='system',
                action='SCHEDULE_INTERVIEW',
                table_name='Candidates',
                record_id=str(candidate_id),
                old_values=json.dumps(old_data, default=str) if old_data else None,
                new_values=json.dumps(update_data, default=str)
            )

            self.db.commit()
            return True
        except ValueError:
            raise ValueError("Định dạng ngày không đúng (YYYY-MM-DD)")
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Không thể lên lịch phỏng vấn: {str(e)}")

    def get_candidate_statistics(self):
        """Lấy thống kê ứng viên"""
        try:
            stats = {}

            # Tổng số ứng viên
            stats['total_candidates'] = self.db.get_table_count('Candidates')

            # Thống kê theo trạng thái
            status_stats = self.db.select_records(
                'Candidates',
                columns="status, COUNT(*) as count",
                group_by="status",
                order_by="count DESC"
            )
            stats['by_status'] = dict(status_stats)

            # Thống kê theo vị trí
            position_stats = self.db.select_records(
                'Candidates',
                columns="position, COUNT(*) as count",
                group_by="position",
                order_by="count DESC",
                limit=10
            )
            stats['by_position'] = dict(position_stats)

            # Thống kê theo kinh nghiệm
            exp_stats = self.db.select_records(
                'Candidates',
                columns="""CASE 
                            WHEN experience = 0 THEN 'Không có kinh nghiệm'
                            WHEN experience <= 2 THEN '1-2 năm'
                            WHEN experience <= 5 THEN '3-5 năm'
                            WHEN experience <= 10 THEN '6-10 năm'
                            ELSE 'Trên 10 năm'
                          END as exp_range,
                          COUNT(*) as count""",
                group_by="exp_range",
                order_by="count DESC"
            )
            stats['by_experience'] = dict(exp_stats)

            # Ứng viên mới trong tháng
            current_month = datetime.datetime.now().strftime("%Y-%m")
            stats['new_this_month'] = self.db.get_table_count(
                'Candidates',
                'application_date LIKE ?',
                [f"{current_month}%"]
            )

            return stats
        except Exception as e:
            raise Exception(f"Không thể lấy thống kê ứng viên: {str(e)}")

    def get_interview_schedule(self, start_date=None, end_date=None):
        """Lấy lịch phỏng vấn"""
        try:
            conditions = ["interview_date IS NOT NULL"]
            params = []

            if start_date:
                conditions.append("interview_date >= ?")
                params.append(start_date)
            if end_date:
                conditions.append("interview_date <= ?")
                params.append(end_date)

            return self.db.select_records(
                'Candidates',
                columns="candidate_id, name, email, phone, position, interview_date, notes",
                condition=" AND ".join(conditions),
                params=params,
                order_by="interview_date ASC"
            )
        except Exception as e:
            raise Exception(f"Không thể lấy lịch phỏng vấn: {str(e)}")
