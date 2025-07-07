#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
from datetime import datetime, timedelta
import random

def add_sample_assignments():
    """Thêm các bài tập mẫu để demo tính năng tìm kiếm và sắp xếp A-Z"""
    
    # Danh sách bài tập mẫu với tên đa dạng từ A-Z
    sample_assignments = [
        {'title': 'Array Manipulation in Python', 'description': 'Học cách thao tác với mảng và danh sách trong Python', 'language': 'python', 'difficulty': 'easy', 'assignment_type': 'code'},
        {'title': 'Binary Search Algorithm', 'description': 'Cài đặt thuật toán tìm kiếm nhị phân', 'language': 'python', 'difficulty': 'medium', 'assignment_type': 'code'},
        {'title': 'Calculator Programming', 'description': 'Tạo máy tính đơn giản với Python', 'language': 'python', 'difficulty': 'easy', 'assignment_type': 'code'},
        {'title': 'Database Connection', 'description': 'Kết nối và thao tác với cơ sở dữ liệu SQLite', 'language': 'python', 'difficulty': 'hard', 'assignment_type': 'code'},
        {'title': 'Error Handling Practice', 'description': 'Thực hành xử lý lỗi và exception trong Python', 'language': 'python', 'difficulty': 'medium', 'assignment_type': 'code'},
        {'title': 'File Input/Output Operations', 'description': 'Đọc và ghi file trong Python', 'language': 'python', 'difficulty': 'easy', 'assignment_type': 'code'},
        {'title': 'Graph Theory Basics', 'description': 'Giới thiệu lý thuyết đồ thị và cài đặt cơ bản', 'language': 'python', 'difficulty': 'hard', 'assignment_type': 'code'},
        {'title': 'Hash Table Implementation', 'description': 'Cài đặt bảng băm từ đầu', 'language': 'python', 'difficulty': 'hard', 'assignment_type': 'code'},
        {'title': 'Iterator and Generator', 'description': 'Học về iterator và generator trong Python', 'language': 'python', 'difficulty': 'medium', 'assignment_type': 'code'},
        {'title': 'JSON Data Processing', 'description': 'Xử lý dữ liệu JSON trong Python', 'language': 'python', 'difficulty': 'easy', 'assignment_type': 'code'},
        {'title': 'Kiểm tra số nguyên tố', 'description': 'Viết chương trình kiểm tra số nguyên tố', 'language': 'python', 'difficulty': 'easy', 'assignment_type': 'code'},
        {'title': 'Linear Regression Model', 'description': 'Cài đặt mô hình hồi quy tuyến tính', 'language': 'python', 'difficulty': 'hard', 'assignment_type': 'code'},
        {'title': 'Matrix Operations', 'description': 'Các phép toán ma trận cơ bản', 'language': 'python', 'difficulty': 'medium', 'assignment_type': 'code'},
        {'title': 'Network Programming', 'description': 'Lập trình mạng cơ bản với socket', 'language': 'python', 'difficulty': 'hard', 'assignment_type': 'code'},
        {'title': 'Object-Oriented Programming', 'description': 'Lập trình hướng đối tượng trong Python', 'language': 'python', 'difficulty': 'medium', 'assignment_type': 'code'},
        {'title': 'Prime Number Generator', 'description': 'Sinh số nguyên tố bằng sàng Eratosthenes', 'language': 'python', 'difficulty': 'medium', 'assignment_type': 'code'},
        {'title': 'Queue Data Structure', 'description': 'Cài đặt cấu trúc dữ liệu Queue', 'language': 'python', 'difficulty': 'easy', 'assignment_type': 'code'},
        {'title': 'Recursive Functions', 'description': 'Thực hành các hàm đệ quy', 'language': 'python', 'difficulty': 'medium', 'assignment_type': 'code'},
        {'title': 'String Manipulation', 'description': 'Thao tác với chuỗi ký tự trong Python', 'language': 'python', 'difficulty': 'easy', 'assignment_type': 'code'},
        {'title': 'Tree Traversal Algorithms', 'description': 'Các thuật toán duyệt cây', 'language': 'python', 'difficulty': 'hard', 'assignment_type': 'code'},
        {'title': 'Unit Testing Practice', 'description': 'Thực hành viết unit test với unittest', 'language': 'python', 'difficulty': 'medium', 'assignment_type': 'code'},
        {'title': 'Variable Scope Quiz', 'description': 'Trắc nghiệm về phạm vi biến trong Python', 'language': 'python', 'difficulty': 'easy', 'assignment_type': 'quiz'},
        {'title': 'Web Scraping Basics', 'description': 'Cơ bản về thu thập dữ liệu web', 'language': 'python', 'difficulty': 'medium', 'assignment_type': 'code'},
        {'title': 'XML Parsing Exercise', 'description': 'Phân tích và xử lý file XML', 'language': 'python', 'difficulty': 'medium', 'assignment_type': 'code'},
        {'title': 'Yield and Coroutines', 'description': 'Học về yield và coroutines trong Python', 'language': 'python', 'difficulty': 'hard', 'assignment_type': 'code'},
        {'title': 'Zero Division Handling', 'description': 'Xử lý lỗi chia cho zero', 'language': 'python', 'difficulty': 'easy', 'assignment_type': 'code'}
    ]
    
    # Kết nối database
    conn = sqlite3.connect('learning_system.db')
    cursor = conn.cursor()
    
    try:
        # Lấy teacher_id đầu tiên có sẵn
        cursor.execute("SELECT id FROM users WHERE role = 'teacher' LIMIT 1")
        teacher_result = cursor.fetchone()
        
        if not teacher_result:
            print("Không tìm thấy teacher trong database. Tạo teacher mặc định...")
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, full_name, role, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ('teacher1', 'teacher1@example.com', 'hashed_password', 'Teacher One', 'teacher', datetime.now().isoformat()))
            teacher_id = cursor.lastrowid
        else:
            teacher_id = teacher_result[0]
        
        # Thêm assignments
        for i, assignment in enumerate(sample_assignments):
            # Tính deadline ngẫu nhiên trong 30 ngày tới
            days_ahead = random.randint(7, 30)
            deadline = datetime.now() + timedelta(days=days_ahead)
            
            # Tính created_at trong 30 ngày qua
            days_ago = random.randint(1, 30)
            created_at = datetime.now() - timedelta(days=days_ago)
            
            cursor.execute("""
                INSERT INTO assignments (
                    title, description, assignment_type, language, difficulty,
                    teacher_id, deadline, created_at, starter_code, topic
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                assignment['title'],
                assignment['description'],
                assignment['assignment_type'],
                assignment['language'],
                assignment['difficulty'],
                teacher_id,
                deadline.isoformat(),
                created_at.isoformat(),
                f"# Starter code for {assignment['title']}\n# TODO: Implement your solution here\n",
                assignment['title'].lower().replace(' ', '_')
            ))
        
        conn.commit()
        print(f"✅ Đã thêm {len(sample_assignments)} bài tập mẫu thành công!")
        
        # Hiển thị thống kê
        cursor.execute("SELECT COUNT(*) FROM assignments")
        total_assignments = cursor.fetchone()[0]
        print(f"📊 Tổng số bài tập trong database: {total_assignments}")
        
        # Hiển thị các bài tập theo thứ tự A-Z
        cursor.execute("SELECT title, difficulty FROM assignments ORDER BY title ASC LIMIT 10")
        assignments = cursor.fetchall()
        print("\n📋 10 bài tập đầu tiên (sắp xếp A-Z):")
        for title, difficulty in assignments:
            print(f"   • {title} ({difficulty})")
        
    except Exception as e:
        print(f"❌ Lỗi khi thêm dữ liệu: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Đang thêm bài tập mẫu để demo tính năng tìm kiếm A-Z...")
    add_sample_assignments()
    print("\n✨ Hoàn thành! Bây giờ bạn có thể truy cập http://localhost:8001/search để xem kết quả.") 