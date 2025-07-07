# 🚀 CS466 Learning System - Quick Setup Guide

## ⚡ Setup trong 3 phút

### 1️⃣ Prerequisites
```bash
# Kiểm tra Python version
python --version  # Cần Python 3.8+
```

### 2️⃣ Installation
```bash
# Clone repository
git clone https://github.com/your-username/cs466-learning-system.git
cd cs466-learning-system

# Install dependencies
pip install -r requirements.txt
```

### 3️⃣ Run Application
```bash
# Start server
python main.py

# Hoặc với uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4️⃣ Access System
```
🌐 URL: http://localhost:8000
👨‍🏫 Teacher: teacher/teacher123
🎓 Student: student/student123
```

## 🔧 Quick Test
```bash
# Test all features (server phải đang chạy)
python final_system_check.py
```

Expected output:
```
✅ Server Status
✅ Authentication (F03)
✅ Search Engine (F17) 
✅ AI Generator (F13)
✅ Code Execution
✅ Assignment System (F07)
✅ Dashboard APIs
✅ Performance Check

🏆 OVERALL RESULT: 8/8 tests passed
🎉 HỆ THỐNG HOẠT ĐỘNG HOÀN HẢO!
```

## 🎯 Demo Features

### F03 - Authentication & Dashboard
1. Go to `http://localhost:8000`
2. Login as teacher (teacher/teacher123)
3. Explore teacher dashboard with stats

### F07 - Assignment System  
1. Click "Tạo bài tập" to create assignment
2. Login as student (student/student123)
3. Do assignments with code editor

### F13 - AI Question Generator
1. Go to `/ai/question-generator`
2. Select topic and difficulty
3. Generate questions automatically

### F17 - Advanced Search
1. Go to `/search`
2. Try searches: "python", "array", "loop"
3. Use filters and see real-time results

## 🛠️ Troubleshooting

### Port already in use
```bash
# Use different port
uvicorn main:app --port 8001
```

### Database issues
```bash
# The system will auto-create database with sample data
# If issues persist, delete and restart:
rm *.db
python main.py
```

### Missing dependencies
```bash
# Reinstall requirements
pip install --upgrade -r requirements.txt
```

## 📊 System Features

- ✅ **52 sample assignments** ready for demo
- ✅ **2 test accounts** (teacher + student)  
- ✅ **4 main features** (F03, F07, F13, F17)
- ✅ **Modern UI** with Bootstrap 5
- ✅ **Code execution** like online-python.com
- ✅ **AI integration** for question generation
- ✅ **Advanced search** with filters
- ✅ **Mobile responsive** design

## 🎥 Demo Workflow

1. **Teacher Workflow:**
   ```
   Login → Dashboard → Create Assignment → View Submissions
   ```

2. **Student Workflow:**  
   ```
   Login → Dashboard → Browse Assignments → Solve → Submit
   ```

3. **AI Features:**
   ```
   AI Generator → Select Topic → Generate Questions → Create Assignment
   ```

4. **Search Features:**
   ```
   Search Page → Enter Keywords → Filter Results → View Details
   ```

---

**🎯 Ready for demo in 3 minutes!** All features working out of the box. 