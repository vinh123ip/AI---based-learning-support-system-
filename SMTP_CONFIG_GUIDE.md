# Hướng dẫn cấu hình SMTP cho Reset Password

## 📧 **Tạo file .env**

Tạo file `.env` trong thư mục gốc với nội dung:

```
# SMTP Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=True

# JWT Secret Key
JWT_SECRET_KEY=your-secret-key-change-in-production

# Application Settings
APP_HOST=localhost
APP_PORT=8000
DEBUG=True
```

## 🛠️ **Cách lấy Gmail App Password**

1. **Bật 2-Step Verification:**
   - Vào [myaccount.google.com](https://myaccount.google.com)
   - Security → 2-Step Verification → Bật

2. **Tạo App Password:**
   - Security → App passwords 
   - Select app: "Mail"
   - Select device: "Other" → Nhập "CS466 System"
   - Copy password 16 ký tự

3. **Cập nhật .env:**
   ```
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=abcd-efgh-ijkl-mnop
   ```

## ✅ **Test SMTP Config**

Chạy test script:
```bash
python test_reset_password.py
```

Nếu thấy "✅ All email configs present" thì đã setup thành công!

## 🔧 **Troubleshooting**

- **"SMTP not configured"**: Chưa có file .env
- **"Authentication failed"**: Sai username/password
- **"Connection refused"**: Sai SMTP server/port
- **"SSL Error"**: Kiểm tra SMTP_USE_TLS=True 