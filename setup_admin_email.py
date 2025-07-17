import sqlite3
from passlib.context import CryptContext

def setup_admin_with_email():
    """Setup admin account with email for login"""
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    conn = sqlite3.connect('cs466_database.db')
    cursor = conn.cursor()
    
    # Tạo bảng users nếu chưa có
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            full_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_2fa_enabled BOOLEAN DEFAULT 1
        )
    ''')
    
    # Kiểm tra xem admin có tồn tại không
    cursor.execute('SELECT COUNT(*) FROM users WHERE email = ?', ("admin@dtu.edu.vn",))
    admin_exists = cursor.fetchone()[0] > 0
    
    if admin_exists:
        print("Admin account with admin@dtu.edu.vn already exists!")
        # Cập nhật username thành email nếu cần
        cursor.execute('''
            UPDATE users 
            SET username = ? 
            WHERE email = ? AND role = ?
        ''', ("admin@dtu.edu.vn", "admin@dtu.edu.vn", "admin"))
        print("Updated admin username to email: admin@dtu.edu.vn")
    else:
        # Tạo admin account mới
        admin_password = pwd_context.hash("Admin123")
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, role, full_name, is_2fa_enabled)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ("admin@dtu.edu.vn", "admin@dtu.edu.vn", admin_password, "admin", "Administrator", True))
        print("Created new admin account with email: admin@dtu.edu.vn")
    
    # Tạo các tài khoản mặc định khác nếu chưa có
    default_accounts = [
        ("teacher@dtu.edu.vn", "teacher@dtu.edu.vn", "Teacher123", "teacher", "Giáo viên Demo"),
        ("student@dtu.edu.vn", "student@dtu.edu.vn", "Student123", "student", "Sinh viên Demo")
    ]
    
    for username, email, password, role, full_name in default_accounts:
        cursor.execute('SELECT COUNT(*) FROM users WHERE email = ?', (email,))
        if cursor.fetchone()[0] == 0:
            hashed_password = pwd_context.hash(password)
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, role, full_name, is_2fa_enabled)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, email, hashed_password, role, full_name, True))
            print(f"Created account: {email} ({role})")
    
    conn.commit()
    
    # Hiển thị tất cả accounts
    print("\n=== ALL ACCOUNTS ===")
    cursor.execute('SELECT id, username, email, role, full_name FROM users ORDER BY role, id')
    for row in cursor.fetchall():
        print(f"ID: {row[0]}, Username: {row[1]}, Email: {row[2]}, Role: {row[3]}, Name: {row[4]}")
    
    conn.close()
    print("\n✅ Database setup completed!")
    print("\n🔐 Login Information:")
    print("Admin: admin@dtu.edu.vn / Admin123")
    print("Teacher: teacher@dtu.edu.vn / Teacher123") 
    print("Student: student@dtu.edu.vn / Student123")

if __name__ == "__main__":
    setup_admin_with_email() 