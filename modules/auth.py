import sqlite3
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional, Tuple
import os
import re
import smtplib
import secrets
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config

class AuthManager:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.SECRET_KEY = "your-secret-key-here"
        self.ALGORITHM = "HS256"
        self.config = config.get_config()
        
        # Simple in-memory OTP storage
        self.otp_storage = {}  # {email: {"otp": "123456", "expires": timestamp}}
        
        # NOTE: 2FA settings now stored in database, not memory
        # Removed: self.user_2fa_settings = {}
        
        self.init_database()
    
    def init_database(self):
        """Khởi tạo database đơn giản"""
        conn = sqlite3.connect("cs466_database.db")
        cursor = conn.cursor()
        
        # Tạo bảng users với email unique cho login
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                full_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tạo user mặc định nếu chưa có
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            # Tạo tài khoản admin mặc định
            admin_password = self.get_password_hash("Admin123")
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, role, full_name)
                VALUES (?, ?, ?, ?, ?)
            ''', ("admin", "admin@dtu.edu.vn", admin_password, "admin", "Administrator"))
            
            # Tạo tài khoản giáo viên mặc định
            teacher_password = self.get_password_hash("Teacher123")
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, role, full_name)
                VALUES (?, ?, ?, ?, ?)
            ''', ("teacher", "teacher@dtu.edu.vn", teacher_password, "teacher", "Giáo viên Demo"))
            
            # Tạo tài khoản sinh viên mặc định
            student_password = self.get_password_hash("Student123")
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, role, full_name)
                VALUES (?, ?, ?, ?, ?)
            ''', ("student", "student@dtu.edu.vn", student_password, "student", "Sinh viên Demo"))
        
        conn.commit()
        conn.close()
    
    def get_password_hash(self, password: str) -> str:
        """Mã hóa mật khẩu"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Xác thực mật khẩu"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def is_valid_email(self, email: str) -> bool:
        """Kiểm tra định dạng email hợp lệ"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def email_exists(self, email: str) -> Tuple[bool, Optional[int]]:
        """
        Kiểm tra email có tồn tại trong hệ thống không (silent check)
        
        Returns:
            Tuple (exists: bool, user_id: Optional[int])
        """
        if not self.is_valid_email(email):
            return False, None
        
        conn = sqlite3.connect("cs466_database.db")
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
            result = cursor.fetchone()
            
            if result:
                return True, result[0]
            return False, None
            
        except Exception:
            return False, None
        finally:
            conn.close()
    
    def authenticate_user_by_email(self, email: str, password: str) -> Optional[dict]:
        """Xác thực người dùng bằng email và password"""
        if not self.is_valid_email(email):
            return None
        
        conn = sqlite3.connect("cs466_database.db")
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, username, email, password_hash, role, full_name
                FROM users WHERE email = ?
            ''', (email,))
            
            user = cursor.fetchone()
            
            if user and self.verify_password(password, user[3]):
                return {
                    "id": user[0],
                    "username": user[1],
                    "email": user[2],
                    "role": user[4],
                    "full_name": user[5]
                }
            return None
            
        except Exception:
            return None
        finally:
            conn.close()
    
    def generate_otp(self) -> str:
        """Tạo OTP 6 số ngẫu nhiên"""
        return str(secrets.randbelow(900000) + 100000)
    
    def cleanup_expired_otps(self):
        """Xóa các OTP đã hết hạn"""
        current_time = time.time()
        expired_emails = [email for email, data in self.otp_storage.items() 
                         if current_time > data["expires"]]
        
        for email in expired_emails:
            del self.otp_storage[email]
    
    def verify_otp(self, email: str, otp_code: str) -> bool:
        """Xác thực OTP cho email cụ thể"""
        try:
            # Cleanup expired OTPs
            self.cleanup_expired_otps()
            
            # Kiểm tra OTP có tồn tại không
            stored_otp = self.otp_storage.get(email)
            if not stored_otp:
                return False
            
            # Kiểm tra mã OTP
            if stored_otp["otp"] != otp_code:
                return False
            
            # Kiểm tra hết hạn
            if time.time() > stored_otp["expires"]:
                del self.otp_storage[email]
                return False
            
            # OTP hợp lệ - xóa khỏi storage
            del self.otp_storage[email]
            return True
            
        except Exception:
            return False

    def send_otp_email(self, to_email: str, otp_code: str, user_name: str) -> bool:
        """Gửi OTP qua email đơn giản"""
        try:
            # Tạo email content
            subject = f"[CS466] Mã xác thực đăng nhập - {otp_code}"
            
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5;">
                    <div style="max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                        <h2 style="color: #4CAF50; text-align: center;">🔐 Xác thực đăng nhập</h2>
                        <p>Xin chào <strong>{user_name}</strong>!</p>
                        <p>Mã OTP của bạn là:</p>
                        <div style="text-align: center; margin: 20px 0;">
                            <span style="font-size: 32px; font-weight: bold; color: #4CAF50; background: #f0f0f0; padding: 15px 25px; border-radius: 8px; letter-spacing: 5px;">{otp_code}</span>
                        </div>
                        <p style="color: #666; font-size: 14px;">Mã này có hiệu lực trong 5 phút.</p>
                        <p style="color: #666; font-size: 12px;">Nếu bạn không thực hiện đăng nhập, vui lòng bỏ qua email này.</p>
                    </div>
                </body>
            </html>
            """
            
            # Tạo message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = self.config.SMTP_USERNAME
            message['To'] = to_email
            
            html_part = MIMEText(html_content, 'html', 'utf-8')
            message.attach(html_part)
            
            # Gửi email
            server = smtplib.SMTP(self.config.SMTP_SERVER, self.config.SMTP_PORT)
            server.starttls()
            server.login(self.config.SMTP_USERNAME, self.config.SMTP_PASSWORD)
            server.send_message(message)
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"Email error: {e}")  # Simple logging
            return False
    
    def send_otp_to_email(self, email: str) -> Tuple[bool, str]:
        """Gửi OTP đến email (silent validation)"""
        # Cleanup expired OTPs
        self.cleanup_expired_otps()
        
        # Kiểm tra email có tồn tại không (silent)
        email_exists, user_id = self.email_exists(email)
        
        if not email_exists:
            return False, ""  # Silent fail
        
        # Lấy tên user để gửi email
        conn = sqlite3.connect("cs466_database.db")
        cursor = conn.cursor()
        cursor.execute('SELECT full_name FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        full_name = result[0] if result else "Người dùng"
        
        # Tạo OTP
        otp_code = self.generate_otp()
        
        # Lưu vào memory
        self.otp_storage[email] = {
            "otp": otp_code,
            "expires": time.time() + 300,  # 5 phút
            "user_id": user_id
        }
        
        # Gửi email
        if self.send_otp_email(email, otp_code, full_name):
            return True, "OTP đã được gửi đến email của bạn"
        else:
            # Xóa OTP nếu gửi email thất bại
            if email in self.otp_storage:
                del self.otp_storage[email]
            return False, ""
    
    def verify_login_with_otp(self, email: str, password: str, otp_code: str) -> Tuple[bool, str, Optional[dict]]:
        """Xác thực đăng nhập: email + password + OTP"""
        try:
            # Cleanup expired OTPs
            self.cleanup_expired_otps()
            
            # Bước 1: Xác thực email + password
            user_data = self.authenticate_user_by_email(email, password)
            if not user_data:
                return False, "Email hoặc mật khẩu không đúng", None
            
            # Bước 2: Xác thực OTP
            stored_otp = self.otp_storage.get(email)
            if not stored_otp:
                return False, "Mã OTP không hợp lệ hoặc đã hết hạn", None
            
            if stored_otp["otp"] != otp_code:
                return False, "Mã OTP không đúng", None
            
            if time.time() > stored_otp["expires"]:
                del self.otp_storage[email]
                return False, "Mã OTP đã hết hạn", None
            
            # OTP hợp lệ - xóa khỏi storage
            del self.otp_storage[email]
            
            return True, "Đăng nhập thành công", user_data
            
        except Exception as e:
            return False, "Lỗi hệ thống", None
    
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
    
    def is_2fa_enabled(self, user_id: int) -> bool:
        """Kiểm tra xem user có bật 2FA không (default: True)"""
        # NOTE: This function now queries the database for 2FA settings
        conn = sqlite3.connect("cs466_database.db")
        cursor = conn.cursor()
        cursor.execute('''
            SELECT is_2fa_enabled FROM users WHERE id = ?
        ''', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else True # Default True if not found
    
    def set_2fa_status(self, user_id: int, status: bool) -> None:
        """Set trạng thái 2FA cho user"""
        # NOTE: This function now updates the database for 2FA settings
        conn = sqlite3.connect("cs466_database.db")
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET is_2fa_enabled = ? WHERE id = ?
        ''', (status, user_id))
        conn.commit()
        conn.close()
    
    def verify_login_with_conditional_otp(self, email: str, password: str, otp_code: str = "") -> Tuple[bool, str, Optional[dict]]:
        """Xác thực đăng nhập: email + password + OTP (nếu 2FA bật)"""
        try:
            # Bước 1: Xác thực email + password
            user_data = self.authenticate_user_by_email(email, password)
            if not user_data:
                return False, "Email hoặc mật khẩu không đúng", None
            
            user_id = user_data["id"]
            
            # Bước 2: Kiểm tra 2FA có bật không
            if not self.is_2fa_enabled(user_id):
                # 2FA tắt - chỉ cần email + password
                return True, "Đăng nhập thành công", user_data
            
            # Bước 3: 2FA bật - cần xác thực OTP
            if not otp_code:
                return False, "Vui lòng nhập mã OTP", None
            
            # Cleanup expired OTPs
            self.cleanup_expired_otps()
            
            stored_otp = self.otp_storage.get(email)
            if not stored_otp:
                return False, "Mã OTP không hợp lệ hoặc đã hết hạn", None
            
            if stored_otp["otp"] != otp_code:
                return False, "Mã OTP không đúng", None
            
            if time.time() > stored_otp["expires"]:
                del self.otp_storage[email]
                return False, "Mã OTP đã hết hạn", None
            
            # OTP hợp lệ - xóa khỏi storage
            del self.otp_storage[email]
            
            return True, "Đăng nhập thành công", user_data
            
        except Exception as e:
            return False, "Lỗi hệ thống", None
    
    def send_otp_to_email_if_2fa_enabled(self, email: str) -> Tuple[bool, str]:
        """Gửi OTP đến email chỉ khi user bật 2FA"""
        # Kiểm tra email có tồn tại không
        email_exists, user_id = self.email_exists(email)
        
        if not email_exists:
            return False, ""  # Silent fail
        
        # Kiểm tra 2FA có bật không
        if not self.is_2fa_enabled(user_id):
            return False, ""  # Silent fail - không gửi OTP khi 2FA tắt
        
        # 2FA bật - gửi OTP như bình thường
        return self.send_otp_to_email(email) 