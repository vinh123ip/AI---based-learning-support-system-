import sqlite3
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional
import os

class AuthManager:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.SECRET_KEY = "your-secret-key-here"
        self.ALGORITHM = "HS256"
        self.init_database()
    
    def init_database(self):
        """Khởi tạo database"""
        conn = sqlite3.connect("cs466_database.db")
        cursor = conn.cursor()
        
        # Tạo bảng users
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                full_name TEXT,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tạo user mặc định nếu chưa có
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            # Tạo tài khoản giáo viên mặc định
            teacher_password = self.get_password_hash("teacher123")
            cursor.execute('''
                INSERT INTO users (username, password_hash, role, full_name, email)
                VALUES (?, ?, ?, ?, ?)
            ''', ("teacher", teacher_password, "teacher", "Giáo viên Demo", "teacher@dtu.edu.vn"))
            
            # Tạo tài khoản sinh viên mặc định
            student_password = self.get_password_hash("student123")
            cursor.execute('''
                INSERT INTO users (username, password_hash, role, full_name, email)
                VALUES (?, ?, ?, ?, ?)
            ''', ("student", student_password, "student", "Sinh viên Demo", "student@dtu.edu.vn"))
        
        conn.commit()
        conn.close()
    
    def get_password_hash(self, password: str) -> str:
        """Mã hóa mật khẩu"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Xác thực mật khẩu"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def authenticate_user(self, username: str, password: str) -> Optional[dict]:
        """Xác thực người dùng"""
        conn = sqlite3.connect("cs466_database.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, password_hash, role, full_name, email
            FROM users WHERE username = ?
        ''', (username,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user and self.verify_password(password, user[2]):
            return {
                "id": user[0],
                "username": user[1],
                "role": user[3],
                "full_name": user[4],
                "email": user[5]
            }
        return None
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Tạo JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt
    
    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """Lấy thông tin user theo ID"""
        conn = sqlite3.connect("cs466_database.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, role, full_name, email
            FROM users WHERE id = ?
        ''', (user_id,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                "id": user[0],
                "username": user[1],
                "role": user[2],
                "full_name": user[3],
                "email": user[4]
            }
        return None
    
    def register_user(self, username: str, password: str, role: str, full_name: str, email: str) -> bool:
        """Đăng ký người dùng mới"""
        conn = sqlite3.connect("cs466_database.db")
        cursor = conn.cursor()
        
        try:
            password_hash = self.get_password_hash(password)
            cursor.execute('''
                INSERT INTO users (username, password_hash, role, full_name, email)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, password_hash, role, full_name, email))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close() 