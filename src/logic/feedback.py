from src.db.database import get_db
import datetime
import json


class FeedbackManager:
    def __init__(self):
        self.db = get_db()
        self._ensure_tables()

    def _ensure_tables(self):
        """Đảm bảo các bảng cần thiết tồn tại - đã được xử lý trong database.py"""
        pass

    def validate_feedback_data(self, employee_id, content, category=None, priority=None):
        """Validate dữ liệu phản hồi"""
        errors = []

        # Validate employee_id
        if not employee_id or not employee_id.strip():
            errors.append("Mã nhân viên không được để trống")

        # Validate content
        if not content or not content.strip():
            errors.append("Nội dung phản hồi không được để trống")
        elif len(content.strip()) > 1000:
            errors.append("Nội dung phản hồi không được vượt quá 1000 ký tự")

        # Validate category
        valid_categories = ['Chung', 'Lương thưởng', 'Môi trường làm việc',
                            'Đồng nghiệp', 'Quản lý', 'Phúc lợi', 'Khác']
        if category and category not in valid_categories:
            errors.append(f"Danh mục không hợp lệ. Chỉ chấp nhận: {', '.join(valid_categories)}")

        # Validate priority
        valid_priorities = ['Thấp', 'Trung bình', 'Cao', 'Khẩn cấp']
        if priority and priority not in valid_priorities:
            errors.append(f"Mức độ ưu tiên không hợp lệ. Chỉ chấp nhận: {', '.join(valid_priorities)}")

        return errors

    def add_feedback(self, employee_id, feedback):
        """Thêm phản hồi (phương thức gốc để tương thích)"""
        return self.add_feedback_extended(employee_id=employee_id, content=feedback)

    def add_feedback_extended(self, employee_id, content, category='Chung', priority='Thấp',
                              subject=None, is_anonymous=False, status='Chờ xử lý'):
        """Thêm phản hồi với thông tin mở rộng"""
        # Validate dữ liệu
        errors = self.validate_feedback_data(employee_id, content, category, priority)
        if errors:
            raise ValueError("; ".join(errors))

        try:
            self.db.begin_transaction()

            # Tạo feedback_id
            count = self.db.get_table_count('Feedbacks')
            feedback_id = f"FB{count + 1:06d}"

            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Sử dụng phương thức insert_record mới
            feedback_data = {
                'feedback_id': feedback_id,
                'employee_id': employee_id.strip(),
                'category': category,
                'priority': priority,
                'subject': subject.strip() if subject else None,
                'content': content.strip(),
                'status': status,
                'is_anonymous': is_anonymous,
                'created_date': current_time,
                'updated_date': current_time
            }

            self.db.insert_record('Feedbacks', feedback_data)

            # Log hành động
            self.db.log_action(
                user_id='system',
                action='ADD_FEEDBACK',
                table_name='Feedbacks',
                record_id=feedback_id,
                new_values=json.dumps(feedback_data, default=str)
            )

            self.db.commit()
            return feedback_id
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Không thể thêm phản hồi: {str(e)}")

    def add_response(self, feedback_id, response):
        """Thêm phản hồi của admin"""
        if not response or not response.strip():
            raise ValueError("Nội dung phản hồi không được để trống")

        try:
            self.db.begin_transaction()

            # Lấy dữ liệu cũ để log
            old_data = self.get_feedback_by_id(feedback_id)

            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Cập nhật phản hồi trong bảng chính
            feedback_update = {
                'response': response.strip(),
                'response_date': current_time,
                'status': 'Đã xử lý',
                'updated_date': current_time
            }

            self.db.update_record(
                'Feedbacks',
                feedback_update,
                'feedback_id = ?',
                [feedback_id]
            )

            # Thêm vào bảng AdminResponses để tương thích
            response_count = self.db.get_table_count('AdminResponses')
            response_id = f"RES{response_count + 1:06d}"

            admin_response_data = {
                'response_id': response_id,
                'feedback_id': feedback_id,
                'response': response.strip(),
                'created_date': current_time
            }

            self.db.insert_record('AdminResponses', admin_response_data)

            # Log hành động
            self.db.log_action(
                user_id='system',
                action='ADD_RESPONSE',
                table_name='Feedbacks',
                record_id=feedback_id,
                old_values=json.dumps(old_data, default=str) if old_data else None,
                new_values=json.dumps(feedback_update, default=str)
            )

            self.db.commit()
            return response_id
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Không thể thêm phản hồi: {str(e)}")

    def update_feedback_status(self, feedback_id, new_status, handler=None):
        """Cập nhật trạng thái phản hồi"""
        valid_statuses = ['Chờ xử lý', 'Đang xử lý', 'Đã xử lý', 'Đã đóng']
        if new_status not in valid_statuses:
            raise ValueError(f"Trạng thái không hợp lệ. Chỉ chấp nhận: {', '.join(valid_statuses)}")

        try:
            self.db.begin_transaction()

            # Lấy dữ liệu cũ để log
            old_data = self.get_feedback_by_id(feedback_id)

            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            update_data = {
                'status': new_status,
                'handler': handler,
                'updated_date': current_time
            }

            self.db.update_record(
                'Feedbacks',
                update_data,
                'feedback_id = ?',
                [feedback_id]
            )

            # Log hành động
            self.db.log_action(
                user_id='system',
                action='UPDATE_FEEDBACK_STATUS',
                table_name='Feedbacks',
                record_id=feedback_id,
                old_values=json.dumps(old_data, default=str) if old_data else None,
                new_values=json.dumps(update_data, default=str)
            )

            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Không thể cập nhật trạng thái: {str(e)}")

    def get_all_feedbacks_with_responses(self):
        """Lấy tất cả phản hồi kèm trả lời (tương thích với code cũ)"""
        try:
            return self.db.select_records(
                'Feedbacks',
                columns="feedback_id, employee_id, content, COALESCE(response, 'Chưa có trả lời') as response",
                order_by="created_date DESC"
            )
        except Exception as e:
            raise Exception(f"Không thể lấy danh sách phản hồi: {str(e)}")

    def get_all_feedbacks_extended(self):
        """Lấy tất cả phản hồi với thông tin mở rộng"""
        try:
            return self.db.select_records(
                'Feedbacks',
                columns="id, feedback_id, employee_id, category, priority, subject, content, status, is_anonymous, created_date, updated_date, handler, response, response_date",
                order_by="created_date DESC"
            )
        except Exception as e:
            raise Exception(f"Không thể lấy danh sách phản hồi: {str(e)}")

    def get_feedbacks_by_status(self, status):
        """Lấy phản hồi theo trạng thái"""
        try:
            return self.db.select_records(
                'Feedbacks',
                columns="id, feedback_id, employee_id, category, priority, subject, content, status, is_anonymous, created_date, updated_date, handler, response, response_date",
                condition="status = ?",
                params=[status],
                order_by="created_date DESC"
            )
        except Exception as e:
            raise Exception(f"Không thể lấy phản hồi theo trạng thái: {str(e)}")

    def get_feedbacks_by_category(self, category):
        """Lấy phản hồi theo danh mục"""
        try:
            return self.db.select_records(
                'Feedbacks',
                columns="id, feedback_id, employee_id, category, priority, subject, content, status, is_anonymous, created_date, updated_date, handler, response, response_date",
                condition="category = ?",
                params=[category],
                order_by="created_date DESC"
            )
        except Exception as e:
            raise Exception(f"Không thể lấy phản hồi theo danh mục: {str(e)}")

    def get_feedbacks_by_priority(self, priority):
        """Lấy phản hồi theo mức độ ưu tiên"""
        try:
            return self.db.select_records(
                'Feedbacks',
                columns="id, feedback_id, employee_id, category, priority, subject, content, status, is_anonymous, created_date, updated_date, handler, response, response_date",
                condition="priority = ?",
                params=[priority],
                order_by="created_date DESC"
            )
        except Exception as e:
            raise Exception(f"Không thể lấy phản hồi theo mức độ ưu tiên: {str(e)}")

    def search_feedbacks(self, search_term):
        """Tìm kiếm phản hồi"""
        if not search_term or not search_term.strip():
            return self.get_all_feedbacks_extended()

        try:
            search_pattern = f"%{search_term.strip()}%"
            return self.db.select_records(
                'Feedbacks',
                columns="id, feedback_id, employee_id, category, priority, subject, content, status, is_anonymous, created_date, updated_date, handler, response, response_date",
                condition="employee_id LIKE ? OR content LIKE ? OR subject LIKE ? OR response LIKE ?",
                params=[search_pattern, search_pattern, search_pattern, search_pattern],
                order_by="created_date DESC"
            )
        except Exception as e:
            raise Exception(f"Lỗi tìm kiếm phản hồi: {str(e)}")

    def get_feedback_by_id(self, feedback_id):
        """Lấy phản hồi theo ID"""
        try:
            result = self.db.select_records(
                'Feedbacks',
                columns="id, feedback_id, employee_id, category, priority, subject, content, status, is_anonymous, created_date, updated_date, handler, response, response_date",
                condition="feedback_id = ?",
                params=[feedback_id]
            )
            return result[0] if result else None
        except Exception as e:
            raise Exception(f"Không thể lấy thông tin phản hồi: {str(e)}")

    def get_recent_feedbacks(self, limit=10):
        """Lấy phản hồi gần đây"""
        try:
            return self.db.select_records(
                'Feedbacks',
                columns="feedback_id, employee_id, content, created_date",
                order_by="created_date DESC",
                limit=limit
            )
        except Exception as e:
            raise Exception(f"Không thể lấy phản hồi gần đây: {str(e)}")

    def get_feedback_statistics(self):
        """Lấy thống kê phản hồi"""
        try:
            stats = {}

            # Tổng số phản hồi
            stats['total_feedbacks'] = self.db.get_table_count('Feedbacks')

            # Thống kê theo trạng thái
            status_stats = self.db.select_records(
                'Feedbacks',
                columns="status, COUNT(*) as count",
                group_by="status",
                order_by="count DESC"
            )
            stats['by_status'] = dict(status_stats)

            # Thống kê theo danh mục
            category_stats = self.db.select_records(
                'Feedbacks',
                columns="category, COUNT(*) as count",
                group_by="category",
                order_by="count DESC"
            )
            stats['by_category'] = dict(category_stats)

            # Thống kê theo mức độ ưu tiên
            priority_stats = self.db.select_records(
                'Feedbacks',
                columns="priority, COUNT(*) as count",
                group_by="priority",
                order_by="count DESC"
            )
            stats['by_priority'] = dict(priority_stats)

            # Phản hồi mới trong tháng
            current_month = datetime.datetime.now().strftime("%Y-%m")
            stats['new_this_month'] = self.db.get_table_count(
                'Feedbacks',
                'created_date LIKE ?',
                [f"{current_month}%"]
            )

            # Tỷ lệ phản hồi đã xử lý
            if stats['total_feedbacks'] > 0:
                resolved_count = stats['by_status'].get('Đã xử lý', 0)
                stats['resolution_rate'] = (resolved_count / stats['total_feedbacks']) * 100
            else:
                stats['resolution_rate'] = 0

            # Thời gian phản hồi trung bình (placeholder)
            stats['avg_response_time'] = "2.5 ngày"  # Cần tính toán thực tế

            return stats
        except Exception as e:
            raise Exception(f"Không thể lấy thống kê phản hồi: {str(e)}")

    def delete_feedback(self, feedback_id):
        """Xóa phản hồi"""
        try:
            self.db.begin_transaction()

            # Lấy dữ liệu cũ để log
            old_data = self.get_feedback_by_id(feedback_id)

            # Xóa phản hồi admin trước
            self.db.delete_record('AdminResponses', 'feedback_id = ?', [feedback_id])

            # Xóa phản hồi chính
            self.db.delete_record('Feedbacks', 'feedback_id = ?', [feedback_id])

            # Log hành động
            self.db.log_action(
                user_id='system',
                action='DELETE_FEEDBACK',
                table_name='Feedbacks',
                record_id=feedback_id,
                old_values=json.dumps(old_data, default=str) if old_data else None
            )

            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Không thể xóa phản hồi: {str(e)}")

    def get_feedbacks_by_employee(self, employee_id):
        """Lấy phản hồi theo nhân viên"""
        try:
            return self.db.select_records(
                'Feedbacks',
                columns="id, feedback_id, employee_id, category, priority, subject, content, status, is_anonymous, created_date, updated_date, handler, response, response_date",
                condition="employee_id = ?",
                params=[employee_id],
                order_by="created_date DESC"
            )
        except Exception as e:
            raise Exception(f"Không thể lấy phản hồi theo nhân viên: {str(e)}")
