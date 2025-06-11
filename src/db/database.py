import sqlite3
import datetime
import os


class Database:
    def __init__(self, db_path=None):
        """
        Khởi tạo kết nối database
        Args:
            db_path: Đường dẫn đến file database
        """
        # Nếu không có db_path, tạo file database cùng cấp với file database.py
        if db_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(current_dir, "hr_database.db")

        # Tạo thư mục nếu chưa tồn tại
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()

        # Cấu hình database
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.execute("PRAGMA journal_mode = WAL")

        self._create_tables()

    def _create_tables(self):
        """Tạo tất cả các bảng cần thiết"""

        # Bảng Employees - Thông tin nhân viên
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Employees (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                salary REAL NOT NULL,
                join_date TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                position TEXT,
                status TEXT DEFAULT 'Active',
                created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Bảng Attendance - Chấm công
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                attendance_id TEXT UNIQUE,
                employee_id TEXT NOT NULL,
                date TEXT NOT NULL,
                time_in TEXT NOT NULL,
                time_out TEXT NOT NULL,
                work_hours REAL,
                overtime_hours REAL DEFAULT 0,
                status TEXT DEFAULT 'Present',
                notes TEXT,
                created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES Employees(id)
            )
        """)

        # Bảng Candidates - Ứng viên
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id TEXT UNIQUE,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                position TEXT NOT NULL,
                experience INTEGER DEFAULT 0,
                education TEXT,
                skills TEXT,
                status TEXT DEFAULT 'Chờ xử lý',
                application_date TEXT DEFAULT CURRENT_DATE,
                interview_date TEXT,
                notes TEXT,
                resume_path TEXT,
                created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Bảng Feedbacks - Phản hồi nhân viên
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Feedbacks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feedback_id TEXT UNIQUE,
                employee_id TEXT NOT NULL,
                category TEXT DEFAULT 'Chung',
                priority TEXT DEFAULT 'Thấp',
                subject TEXT,
                content TEXT NOT NULL,
                status TEXT DEFAULT 'Chờ xử lý',
                is_anonymous BOOLEAN DEFAULT 0,
                created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_date TEXT DEFAULT CURRENT_TIMESTAMP,
                handler TEXT,
                response TEXT,
                response_date TEXT
            )
        """)

        # Bảng AdminResponses - Phản hồi của admin (để tương thích)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS AdminResponses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                response_id TEXT UNIQUE,
                feedback_id TEXT NOT NULL,
                response TEXT NOT NULL,
                created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (feedback_id) REFERENCES Feedbacks(feedback_id)
            )
        """)

        # Bảng Payrolls - Bảng lương chi tiết
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Payrolls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                payroll_id TEXT UNIQUE,
                employee_id TEXT NOT NULL,
                month INTEGER NOT NULL,
                year INTEGER NOT NULL,
                basic_salary REAL NOT NULL,
                work_days INTEGER DEFAULT 22,
                actual_work_days INTEGER DEFAULT 22,
                absent_days INTEGER DEFAULT 0,
                overtime_hours REAL DEFAULT 0,
                overtime_pay REAL DEFAULT 0,
                allowances REAL DEFAULT 0,
                lunch_allowance REAL DEFAULT 0,
                transport_allowance REAL DEFAULT 0,
                performance_bonus REAL DEFAULT 0,
                other_bonus REAL DEFAULT 0,
                gross_salary REAL NOT NULL,
                social_insurance REAL DEFAULT 0,
                health_insurance REAL DEFAULT 0,
                unemployment_insurance REAL DEFAULT 0,
                tax_deduction REAL DEFAULT 0,
                other_deductions REAL DEFAULT 0,
                total_deductions REAL DEFAULT 0,
                net_salary REAL NOT NULL,
                status TEXT DEFAULT 'Draft',
                notes TEXT,
                created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES Employees(id)
            )
        """)

        # Bảng SalaryComponents - Các thành phần lương
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS SalaryComponents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT NOT NULL,
                component_type TEXT NOT NULL, -- 'allowance', 'bonus', 'deduction'
                component_name TEXT NOT NULL,
                amount REAL NOT NULL,
                is_recurring BOOLEAN DEFAULT 1,
                effective_date TEXT,
                end_date TEXT,
                created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES Employees(id)
            )
        """)

        # Bảng UserSessions - Phiên đăng nhập (cho tương lai)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS UserSessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                session_token TEXT UNIQUE,
                login_time TEXT DEFAULT CURRENT_TIMESTAMP,
                logout_time TEXT,
                ip_address TEXT,
                user_agent TEXT,
                is_active BOOLEAN DEFAULT 1
            )
        """)

        # Bảng SystemLogs - Log hệ thống
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS SystemLogs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                action TEXT NOT NULL,
                table_name TEXT,
                record_id TEXT,
                old_values TEXT,
                new_values TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                success BOOLEAN DEFAULT 1,
                error_message TEXT
            )
        """)

        # Tạo các index để tối ưu hiệu suất
        self._create_indexes()

        self.conn.commit()

    def _create_indexes(self):
        """Tạo các index để tối ưu hiệu suất truy vấn"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_employees_department ON Employees(department)",
            "CREATE INDEX IF NOT EXISTS idx_employees_status ON Employees(status)",
            "CREATE INDEX IF NOT EXISTS idx_attendance_employee_date ON Attendance(employee_id, date)",
            "CREATE INDEX IF NOT EXISTS idx_attendance_date ON Attendance(date)",
            "CREATE INDEX IF NOT EXISTS idx_candidates_status ON Candidates(status)",
            "CREATE INDEX IF NOT EXISTS idx_candidates_position ON Candidates(position)",
            "CREATE INDEX IF NOT EXISTS idx_feedbacks_employee ON Feedbacks(employee_id)",
            "CREATE INDEX IF NOT EXISTS idx_feedbacks_status ON Feedbacks(status)",
            "CREATE INDEX IF NOT EXISTS idx_feedbacks_category ON Feedbacks(category)",
            "CREATE INDEX IF NOT EXISTS idx_payrolls_employee_month ON Payrolls(employee_id, month, year)",
            "CREATE INDEX IF NOT EXISTS idx_payrolls_month_year ON Payrolls(month, year)",
            "CREATE INDEX IF NOT EXISTS idx_system_logs_timestamp ON SystemLogs(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_system_logs_user ON SystemLogs(user_id)"
        ]

        for index_sql in indexes:
            try:
                self.cursor.execute(index_sql)
            except sqlite3.Error as e:
                print(f"Warning: Could not create index: {e}")

    def execute(self, query, params=None):
        """
        Thực thi câu lệnh SQL
        Args:
            query: Câu lệnh SQL
            params: Tham số cho câu lệnh SQL
        """
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False

    def execute_many(self, query, params_list):
        """
        Thực thi nhiều câu lệnh SQL cùng lúc
        Args:
            query: Câu lệnh SQL
            params_list: Danh sách các tham số
        """
        try:
            self.cursor.executemany(query, params_list)
            return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False

    def fetch_all(self):
        """Lấy tất cả kết quả từ câu lệnh SELECT cuối cùng"""
        return self.cursor.fetchall()

    def fetch_one(self):
        """Lấy một kết quả từ câu lệnh SELECT cuối cùng"""
        return self.cursor.fetchone()

    def commit(self):
        """Commit các thay đổi"""
        try:
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Commit error: {e}")
            return False

    def rollback(self):
        """Rollback các thay đổi"""
        try:
            self.conn.rollback()
            return True
        except sqlite3.Error as e:
            print(f"Rollback error: {e}")
            return False

    def begin_transaction(self):
        """Bắt đầu transaction"""
        self.execute("BEGIN TRANSACTION")

    def get_last_insert_id(self):
        """Lấy ID của bản ghi vừa được insert"""
        return self.cursor.lastrowid

    def get_row_count(self):
        """Lấy số lượng hàng bị ảnh hưởng bởi câu lệnh cuối cùng"""
        return self.cursor.rowcount

    # Các phương thức tiện ích cho từng bảng

    def get_table_info(self, table_name):
        """Lấy thông tin cấu trúc bảng"""
        self.execute(f"PRAGMA table_info({table_name})")
        return self.fetch_all()

    def table_exists(self, table_name):
        """Kiểm tra bảng có tồn tại không"""
        self.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        return self.fetch_one() is not None

    def get_table_count(self, table_name, condition=None, params=None):
        """Đếm số lượng bản ghi trong bảng"""
        query = f"SELECT COUNT(*) FROM {table_name}"
        if condition:
            query += f" WHERE {condition}"
        self.execute(query, params)
        result = self.fetch_one()
        return result[0] if result else 0

    def insert_record(self, table_name, data):
        """
        Insert bản ghi mới
        Args:
            table_name: Tên bảng
            data: Dictionary chứa dữ liệu {column: value}
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        success = self.execute(query, list(data.values()))
        if success:
            self.commit()
            return self.get_last_insert_id()
        return None

    def update_record(self, table_name, data, condition, condition_params=None):
        """
        Cập nhật bản ghi
        Args:
            table_name: Tên bảng
            data: Dictionary chứa dữ liệu cần cập nhật
            condition: Điều kiện WHERE
            condition_params: Tham số cho điều kiện
        """
        set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {condition}"

        params = list(data.values())
        if condition_params:
            params.extend(condition_params)

        success = self.execute(query, params)
        if success:
            self.commit()
            return self.get_row_count()
        return 0

    def delete_record(self, table_name, condition, params=None):
        """
        Xóa bản ghi
        Args:
            table_name: Tên bảng
            condition: Điều kiện WHERE
            params: Tham số cho điều kiện
        """
        query = f"DELETE FROM {table_name} WHERE {condition}"
        success = self.execute(query, params)
        if success:
            self.commit()
            return self.get_row_count()
        return 0

    def select_records(self, table_name, columns="*", condition=None, params=None,
                       order_by=None, limit=None, group_by=None, joins=None):
        """
        Lấy bản ghi từ bảng
        Args:
            table_name: Tên bảng
            columns: Các cột cần lấy
            condition: Điều kiện WHERE
            params: Tham số cho điều kiện
            order_by: Sắp xếp
            limit: Giới hạn số lượng
            group_by: Nhóm theo
            joins: JOIN với bảng khác
        """
        query = f"SELECT {columns} FROM {table_name}"

        if joins:
            query += f" {joins}"
        if condition:
            query += f" WHERE {condition}"
        if group_by:
            query += f" GROUP BY {group_by}"
        if order_by:
            query += f" ORDER BY {order_by}"
        if limit:
            query += f" LIMIT {limit}"

        self.execute(query, params)
        return self.fetch_all()

    # Phương thức backup và restore

    def backup_database(self, backup_path):
        """
        Backup database
        Args:
            backup_path: Đường dẫn file backup
        """
        try:
            backup_conn = sqlite3.connect(backup_path)
            self.conn.backup(backup_conn)
            backup_conn.close()
            return True
        except sqlite3.Error as e:
            print(f"Backup error: {e}")
            return False

    def restore_database(self, backup_path):
        """
        Restore database từ backup
        Args:
            backup_path: Đường dẫn file backup
        """
        try:
            if os.path.exists(backup_path):
                backup_conn = sqlite3.connect(backup_path)
                backup_conn.backup(self.conn)
                backup_conn.close()
                return True
            return False
        except sqlite3.Error as e:
            print(f"Restore error: {e}")
            return False

    def vacuum_database(self):
        """Tối ưu hóa database (VACUUM)"""
        try:
            self.execute("VACUUM")
            return True
        except sqlite3.Error as e:
            print(f"Vacuum error: {e}")
            return False

    def get_database_size(self):
        """Lấy kích thước database"""
        try:
            return os.path.getsize(self.db_path)
        except OSError:
            return 0

    def get_database_stats(self):
        """Lấy thống kê database"""
        stats = {}

        tables = [
            'Employees', 'Attendance', 'Candidates',
            'Feedbacks', 'Payrolls', 'SalaryComponents'
        ]

        for table in tables:
            if self.table_exists(table):
                stats[table] = self.get_table_count(table)
            else:
                stats[table] = 0

        stats['database_size'] = self.get_database_size()
        stats['last_backup'] = None  # Có thể implement sau

        return stats

    # Phương thức log hệ thống

    def log_action(self, user_id, action, table_name=None, record_id=None,
                   old_values=None, new_values=None, ip_address=None, success=True, error_message=None):
        """
        Ghi log hành động của user
        Args:
            user_id: ID người dùng
            action: Hành động (CREATE, UPDATE, DELETE, etc.)
            table_name: Tên bảng bị ảnh hưởng
            record_id: ID bản ghi bị ảnh hưởng
            old_values: Giá trị cũ (JSON string)
            new_values: Giá trị mới (JSON string)
            ip_address: Địa chỉ IP
            success: Thành công hay không
            error_message: Thông báo lỗi nếu có
        """
        log_data = {
            'user_id': user_id,
            'action': action,
            'table_name': table_name,
            'record_id': record_id,
            'old_values': old_values,
            'new_values': new_values,
            'ip_address': ip_address,
            'success': success,
            'error_message': error_message
        }

        return self.insert_record('SystemLogs', log_data)

    def get_user_logs(self, user_id, limit=100):
        """Lấy log của user"""
        return self.select_records(
            'SystemLogs',
            condition='user_id = ?',
            params=[user_id],
            order_by='timestamp DESC',
            limit=limit
        )

    def get_system_logs(self, start_date=None, end_date=None, limit=1000):
        """Lấy log hệ thống"""
        condition = None
        params = []

        if start_date and end_date:
            condition = "timestamp BETWEEN ? AND ?"
            params = [start_date, end_date]
        elif start_date:
            condition = "timestamp >= ?"
            params = [start_date]
        elif end_date:
            condition = "timestamp <= ?"
            params = [end_date]

        return self.select_records(
            'SystemLogs',
            condition=condition,
            params=params,
            order_by='timestamp DESC',
            limit=limit
        )

    # Phương thức kiểm tra và sửa chữa

    def check_database_integrity(self):
        """Kiểm tra tính toàn vẹn database"""
        try:
            self.execute("PRAGMA integrity_check")
            result = self.fetch_one()
            return result[0] == 'ok' if result else False
        except sqlite3.Error as e:
            print(f"Integrity check error: {e}")
            return False

    def analyze_database(self):
        """Phân tích database để tối ưu hiệu suất"""
        try:
            self.execute("ANALYZE")
            return True
        except sqlite3.Error as e:
            print(f"Analyze error: {e}")
            return False

    def close(self):
        """Đóng kết nối database"""
        try:
            if self.conn:
                self.conn.close()
                return True
        except sqlite3.Error as e:
            print(f"Close error: {e}")
            return False

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()
        self.close()

    def __del__(self):
        """Destructor"""
        self.close()


# Singleton pattern cho database connection
class DatabaseManager:
    _instance = None
    _database = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    def get_database(self, db_path=None):
        """Lấy instance database (singleton)"""
        if self._database is None:
            if db_path is None:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                db_path = os.path.join(current_dir, "hr_database.db")
            self._database = Database(db_path)
        return self._database

    def close_database(self):
        """Đóng database connection"""
        if self._database:
            self._database.close()
            self._database = None


# Utility functions
def get_db():
    """Hàm tiện ích để lấy database instance"""
    return DatabaseManager().get_database()


def init_sample_data():
    """Khởi tạo dữ liệu mẫu cho testing"""
    db = get_db()

    # Sample employees
    sample_employees = [
        {
            'id': 'EMP001',
            'name': 'Nguyễn Văn A',
            'department': 'IT',
            'salary': 25000000,
            'join_date': '2023-01-15',
            'phone': '0901234567',
            'email': 'nguyenvana@company.com',
            'position': 'Senior Developer'
        },
        {
            'id': 'EMP002',
            'name': 'Trần Thị B',
            'department': 'HR',
            'salary': 18000000,
            'join_date': '2023-03-01',
            'phone': '0901234568',
            'email': 'tranthib@company.com',
            'position': 'HR Specialist'
        },
        {
            'id': 'EMP003',
            'name': 'Lê Văn C',
            'department': 'Marketing',
            'salary': 22000000,
            'join_date': '2023-02-10',
            'phone': '0901234569',
            'email': 'levanc@company.com',
            'position': 'Marketing Manager'
        }
    ]

    for emp in sample_employees:
        # Check if employee exists
        existing = db.select_records('Employees', condition='id = ?', params=[emp['id']])
        if not existing:
            db.insert_record('Employees', emp)

    print("Sample data initialized successfully!")


if __name__ == "__main__":
    # Test database
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_db_path = os.path.join(current_dir, "hr_database.db")

    with Database(test_db_path) as db:
        print("Database initialized successfully!")
        print(f"Database location: {test_db_path}")
        print("Database stats:", db.get_database_stats())

        # Initialize sample data
        init_sample_data()

        # Test integrity
        if db.check_database_integrity():
            print("Database integrity check: PASSED")
        else:
            print("Database integrity check: FAILED")
