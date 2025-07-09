#!/usr/bin/env python3
"""
Script to create sample data for testing search functionality
"""

import sqlite3
from datetime import datetime, timedelta
import json

def create_sample_data():
    """Create sample assignments and users for testing"""
    conn = sqlite3.connect('learning_system.db')
    cursor = conn.cursor()
    
    # Sample assignments
    sample_assignments = [
        {
            'title': 'Python Cơ bản - Biến và Toán tử',
            'description': 'Học cách khai báo biến và sử dụng các toán tử trong Python',
            'assignment_type': 'code',
            'language': 'python',
            'difficulty': 'easy',
            'teacher_id': 1,
            'deadline': (datetime.now() + timedelta(days=7)).isoformat(),
            'starter_code': '# Khai báo biến\nname = ""\nage = 0\n\n# Viết code của bạn ở đây',
            'solution': 'name = "Python"\nage = 30\nprint(f"Tên: {name}, Tuổi: {age}")',
            'topic': 'basic_syntax'
        },
        {
            'title': 'Vòng lặp For trong Python',
            'description': 'Thực hành sử dụng vòng lặp for để duyệt qua danh sách',
            'assignment_type': 'code',
            'language': 'python',
            'difficulty': 'medium',
            'teacher_id': 1,
            'deadline': (datetime.now() + timedelta(days=10)).isoformat(),
            'starter_code': '# Duyệt qua danh sách\nnumbers = [1, 2, 3, 4, 5]\n\n# Viết vòng lặp for ở đây',
            'solution': 'numbers = [1, 2, 3, 4, 5]\nfor num in numbers:\n    print(num * 2)',
            'topic': 'loops'
        },
        {
            'title': 'Hàm trong Python',
            'description': 'Định nghĩa và sử dụng hàm trong Python',
            'assignment_type': 'code',
            'language': 'python',
            'difficulty': 'medium',
            'teacher_id': 1,
            'deadline': (datetime.now() + timedelta(days=14)).isoformat(),
            'starter_code': '# Định nghĩa hàm\ndef calculate_sum(a, b):\n    # Viết code ở đây\n    pass',
            'solution': 'def calculate_sum(a, b):\n    return a + b\n\nresult = calculate_sum(5, 3)\nprint(result)',
            'topic': 'functions'
        },
        {
            'title': 'Cấu trúc dữ liệu - List và Dictionary',
            'description': 'Làm việc với list và dictionary trong Python',
            'assignment_type': 'code',
            'language': 'python',
            'difficulty': 'hard',
            'teacher_id': 1,
            'deadline': (datetime.now() + timedelta(days=21)).isoformat(),
            'starter_code': '# Tạo dictionary chứa thông tin sinh viên\nstudents = {}\n\n# Viết code ở đây',
            'solution': 'students = {"name": "John", "age": 20, "grades": [85, 90, 78]}\nprint(students["name"])\nprint(sum(students["grades"])/len(students["grades"]))',
            'topic': 'data_structures'
        },
        {
            'title': 'Thuật toán Sắp xếp',
            'description': 'Implement thuật toán bubble sort',
            'assignment_type': 'code',
            'language': 'python',
            'difficulty': 'hard',
            'teacher_id': 1,
            'deadline': (datetime.now() + timedelta(days=28)).isoformat(),
            'starter_code': '# Implement bubble sort\ndef bubble_sort(arr):\n    # Viết code ở đây\n    pass',
            'solution': 'def bubble_sort(arr):\n    n = len(arr)\n    for i in range(n):\n        for j in range(0, n-i-1):\n            if arr[j] > arr[j+1]:\n                arr[j], arr[j+1] = arr[j+1], arr[j]\n    return arr',
            'topic': 'algorithms'
        },
        {
            'title': 'Trắc nghiệm Python Cơ bản',
            'description': 'Kiểm tra kiến thức cơ bản về Python',
            'assignment_type': 'quiz',
            'language': 'python',
            'difficulty': 'easy',
            'teacher_id': 1,
            'deadline': (datetime.now() + timedelta(days=5)).isoformat(),
            'starter_code': '',
            'solution': '',
            'topic': 'basic_syntax'
        }
    ]
    
    # Insert sample assignments
    for assignment in sample_assignments:
        cursor.execute('''
            INSERT INTO assignments (
                title, description, assignment_type, language, difficulty,
                teacher_id, deadline, starter_code, solution, topic, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            assignment['title'],
            assignment['description'],
            assignment['assignment_type'],
            assignment['language'],
            assignment['difficulty'],
            assignment['teacher_id'],
            assignment['deadline'],
            assignment['starter_code'],
            assignment['solution'],
            assignment['topic'],
            datetime.now().isoformat()
        ))
    
    # Sample users (additional)
    sample_users = [
        {
            'username': 'teacher2',
            'password': 'teacher123',
            'email': 'teacher2@example.com',
            'full_name': 'Nguyễn Văn A',
            'role': 'teacher'
        },
        {
            'username': 'student2',
            'password': 'student123',
            'email': 'student2@example.com',
            'full_name': 'Trần Thị B',
            'role': 'student'
        },
        {
            'username': 'student3',
            'password': 'student123',
            'email': 'student3@example.com',
            'full_name': 'Lê Văn C',
            'role': 'student'
        }
    ]
    
    # Insert sample users
    for user in sample_users:
        cursor.execute('''
            INSERT OR IGNORE INTO users (username, password, email, full_name, role, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            user['username'],
            user['password'],
            user['email'],
            user['full_name'],
            user['role'],
            datetime.now().isoformat()
        ))
    
    conn.commit()
    conn.close()
    print("✅ Sample data created successfully!")
    print("📊 Created:")
    print(f"   - {len(sample_assignments)} assignments")
    print(f"   - {len(sample_users)} users")

if __name__ == "__main__":
    create_sample_data() 