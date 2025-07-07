# 🎓 CS466 Learning System 
## Hệ thống học tập Perl & Python với AI tích hợp

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production_Ready-brightgreen.svg)]()

> 🏆 **Đồ án nhóm môn CS466** - Hệ thống học tập trực tuyến hiện đại với 4 tính năng chính: **F03** (Phân quyền), **F07** (Làm bài), **F13** (AI Generator), **F17** (Tìm kiếm nâng cao)

## 📋 Mô tả

Hệ thống học tập trực tuyến cho môn **CS466 - Perl & Python** được phát triển với **FastAPI + JavaScript**, tích hợp **AI** để hỗ trợ giảng dạy và học tập. Hệ thống cung cấp trải nghiệm học lập trình tương tự như **online-python.com** và **LeetCode**.

## ✨ Tính năng chính

### 🎓 Cho Sinh viên (F03, F07, F17)
- **Dashboard cá nhân** với thống kê tiến độ học tập
- **Làm bài tập** với 3 loại: Code, Quiz, Upload file
- **Code Editor trực tuyến** với Monaco Editor (như VS Code)
- **Chạy code Python/Perl** trực tiếp trên browser
- **Tìm kiếm nâng cao** với filters đa dạng
- **Nộp bài tự động** với auto-save
- **Responsive design** cho mobile

### 👨‍🏫 Cho Giáo viên
- **Dashboard quản lý** với báo cáo chi tiết
- **Tạo bài tập** đa dạng với deadline
- **AI sinh câu hỏi** tự động (F13)
- **Xem bài nộp** và chấm điểm
- **Thống kê lớp học** với biểu đồ

### 🤖 AI Features (F13)
- **Sinh câu hỏi trắc nghiệm** tự động
- **Đánh giá code** và gợi ý cải thiện
- **Hỗ trợ học tập** thông minh
- **Lộ trình học** cá nhân hóa

## 🚀 Cài đặt

### 1. Yêu cầu hệ thống
```bash
Python 3.8+
Node.js (optional - cho development)
```

### 2. Clone project
```bash
git clone https://github.com/your-username/cs466-learning-system.git
cd cs466-learning-system
```

> 💡 **Lưu ý**: Thay `your-username` bằng tên GitHub thực tế của bạn

### 3. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 4. Cấu hình môi trường
Tạo file `.env` từ mẫu:
```bash
cp .env.example .env
```

Chỉnh sửa `.env`:
```env
# OpenAI API (bắt buộc cho AI features)
OPENAI_API_KEY=your-openai-api-key-here

# JWT Secret (thay đổi trong production)
JWT_SECRET_KEY=your-super-secret-key-here

# Database
DATABASE_URL=sqlite:///cs466_database.db

# App settings
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=True
```

### 5. Khởi chạy ứng dụng
```bash
python main.py
```

Hoặc với uvicorn:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 6. Truy cập hệ thống
Mở browser và vào: `http://localhost:8000`

## 🔐 Tài khoản mặc định

### Giáo viên
- **Username:** `teacher`
- **Password:** `teacher123`

### Sinh viên
- **Username:** `student`  
- **Password:** `student123`

## 📁 Cấu trúc project

```
cs466-learning-system/
├── main.py                 # FastAPI app chính
├── requirements.txt        # Dependencies Python
├── config.py              # Cấu hình hệ thống
├── README.md              # File này
│
├── modules/               # Python modules
│   ├── auth.py           # Xác thực & JWT
│   ├── assignments.py    # Quản lý bài tập
│   ├── ai_generator.py   # AI sinh câu hỏi
│   └── search.py         # Tìm kiếm nâng cao
│
├── templates/            # HTML templates
│   ├── login.html        # Trang đăng nhập
│   ├── student_dashboard.html
│   ├── teacher_dashboard.html
│   └── solve_assignment.html
│
├── static/              # Static files
│   └── css/
│       └── style.css    # CSS chung
│
├── uploads/             # File upload (tự tạo)
└── logs/               # Log files (tự tạo)
```

## 🛠️ Tính năng chi tiết

### F03 - Giao diện phân quyền
- ✅ Login với JWT authentication
- ✅ Dashboard riêng cho GV/SV
- ✅ Navigation sidebar động
- ✅ Profile management

### F07 - Làm bài & nộp bài
- ✅ Code editor với Monaco (VS Code)
- ✅ Syntax highlighting Python/Perl
- ✅ Chạy code trực tuyến
- ✅ Test cases tự động
- ✅ File upload với drag & drop
- ✅ Quiz trắc nghiệm tương tác
- ✅ Auto-save progress
- ✅ Countdown timer

### F13 - AI sinh câu hỏi
- ✅ Tích hợp OpenAI GPT-3.5/4
- ✅ Sinh câu hỏi theo chủ đề
- ✅ Điều chỉnh độ khó
- ✅ Fallback questions khi AI lỗi
- ✅ Export thành bài tập

### F17 - Tìm kiếm nâng cao  
- ✅ Full-text search
- ✅ Filter theo ngôn ngữ, độ khó
- ✅ Search suggestions
- ✅ Category filtering
- ✅ Date range filter

## 🎨 UI/UX Features

### 🎭 Giao diện
- **Modern design** với Bootstrap 5
- **Gradient theme** chuyên nghiệp
- **Dark mode** support
- **Animations** mượt mà
- **Mobile responsive**

### 🔄 Tương tác
- **Real-time updates** với JavaScript
- **AJAX calls** không reload page
- **Loading states** với spinners
- **Error handling** thân thiện
- **Progress indicators**

### 📱 Mobile Support
- **Touch-friendly** buttons
- **Responsive layout**
- **Mobile navigation**
- **Optimized forms**

## 🔧 Cấu hình nâng cao

### AI Configuration
```python
# modules/ai_generator.py
AI_MODEL = "gpt-3.5-turbo"  # hoặc "gpt-4"
AI_MAX_TOKENS = 1500
AI_TEMPERATURE = 0.7
```

### Code Execution
```python
# modules/assignments.py
CODE_TIMEOUT = 5  # seconds
SANDBOX_ENABLED = True
ALLOWED_IMPORTS = ["os", "sys", "math"]
```

### Security
```python
# config.py
BCRYPT_ROUNDS = 12
SESSION_TIMEOUT = 3600
MAX_LOGIN_ATTEMPTS = 5
```

## 🐛 Troubleshooting

### Lỗi thường gặp

1. **Port đã được sử dụng**
```bash
# Thay đổi port trong .env
APP_PORT=8001
```

2. **OpenAI API lỗi**
```bash
# Kiểm tra API key trong .env
OPENAI_API_KEY=sk-...
```

3. **Database lỗi**
```bash
# Xóa database và tạo lại
rm cs466_database.db
python main.py
```

4. **Permission lỗi**
```bash
# Tạo thư mục cần thiết
mkdir uploads logs
chmod 755 uploads logs
```

## 📊 Performance

### Metrics
- **Load time:** < 2s
- **API response:** < 500ms
- **Code execution:** < 5s
- **Search:** < 1s

### Optimizations
- Database indexing
- Static file caching
- Lazy loading
- Image compression
- Minified CSS/JS

## 🚀 Deployment

### Development
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production
```bash
# Với Gunicorn
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Với Docker
docker build -t cs466-app .
docker run -p 8000:8000 cs466-app
```

### Environment Variables (Production)
```env
DEBUG=False
JWT_SECRET_KEY=very-secure-secret-key
DATABASE_URL=postgresql://user:pass@host:5432/db
OPENAI_API_KEY=your-production-api-key
```

## 🧪 Testing

### Chạy tests
```bash
# Unit tests
python -m pytest tests/

# Integration tests  
python -m pytest tests/integration/

# Coverage report
python -m pytest --cov=modules tests/
```

### Test accounts
```python
# Tự động tạo test data
python scripts/create_test_data.py
```

## 📈 Monitoring

### Logs
```bash
# Xem logs realtime
tail -f logs/cs466.log

# Log levels: DEBUG, INFO, WARNING, ERROR
```

### Health check
```bash
curl http://localhost:8000/health
```

## 🤝 Contributing

1. Fork project
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 📞 Contact

- **Email:** tranhminhdang@dtu.edu.vn
- **University:** DTU - SCS
- **Course:** CS466 - Perl & Python

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [Bootstrap](https://getbootstrap.com/) - CSS framework  
- [Monaco Editor](https://microsoft.github.io/monaco-editor/) - Code editor
- [OpenAI](https://openai.com/) - AI integration
- [Chart.js](https://www.chartjs.org/) - Data visualization

---

**🎯 Mục tiêu:** Tạo ra hệ thống học tập hiện đại, tương tác cao và tích hợp AI để nâng cao chất lượng giảng dạy môn Perl & Python.

**⭐ Nếu project hữu ích, hãy cho một star!** 