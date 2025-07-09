import sqlite3
import subprocess
import tempfile
import os
from datetime import datetime
from typing import Optional, List, Dict
from fastapi import UploadFile
import json
import uuid

class AssignmentManager:
    def __init__(self):
        self.init_database()
    
    def init_database(self):
        """Khởi tạo database cho bài tập"""
        conn = sqlite3.connect("cs466_database.db")
        cursor = conn.cursor()
        
        # Tạo bảng assignments
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                assignment_type TEXT NOT NULL,
                language TEXT NOT NULL,
                deadline TIMESTAMP,
                teacher_id INTEGER,
                test_cases TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (teacher_id) REFERENCES users (id)
            )
        ''')
        
        # Tạo bảng submissions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                assignment_id INTEGER,
                student_id INTEGER,
                code TEXT,
                answers TEXT,
                file_path TEXT,
                result TEXT,
                score INTEGER,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (assignment_id) REFERENCES assignments (id),
                FOREIGN KEY (student_id) REFERENCES users (id)
            )
        ''')
        
        # Tạo bài tập mẫu
        cursor.execute("SELECT COUNT(*) FROM assignments")
        if cursor.fetchone()[0] == 0:
            sample_assignments = [
                {
                    "title": "Hello World - Python",
                    "description": "Viết chương trình in ra 'Hello, World!' trong Python",
                    "assignment_type": "code",
                    "language": "python",
                    "deadline": "2024-12-31 23:59:59",
                    "teacher_id": 1,
                    "test_cases": json.dumps([
                        {"input": "", "expected_output": "Hello, World!"}
                    ])
                },
                {
                    "title": "Tính tổng hai số",
                    "description": "Viết hàm tính tổng hai số nguyên",
                    "assignment_type": "code",
                    "language": "python",
                    "deadline": "2024-12-31 23:59:59",
                    "teacher_id": 1,
                    "test_cases": json.dumps([
                        {"input": "5 3", "expected_output": "8"},
                        {"input": "10 -5", "expected_output": "5"}
                    ])
                },
                {
                    "title": "Kiến thức cơ bản Python",
                    "description": "Câu hỏi trắc nghiệm về Python",
                    "assignment_type": "quiz",
                    "language": "python",
                    "deadline": "2024-12-31 23:59:59",
                    "teacher_id": 1,
                    "test_cases": json.dumps([
                        {
                            "question": "Python là ngôn ngữ lập trình gì?",
                            "options": ["Compiled", "Interpreted", "Assembly", "Machine"],
                            "correct": 1
                        },
                        {
                            "question": "Từ khóa nào dùng để khai báo hàm trong Python?",
                            "options": ["function", "def", "func", "define"],
                            "correct": 1
                        }
                    ])
                }
            ]
            
            for assignment in sample_assignments:
                cursor.execute('''
                    INSERT INTO assignments (title, description, assignment_type, language, deadline, teacher_id, test_cases)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    assignment["title"],
                    assignment["description"],
                    assignment["assignment_type"],
                    assignment["language"],
                    assignment["deadline"],
                    assignment["teacher_id"],
                    assignment["test_cases"]
                ))
        
        conn.commit()
        conn.close()
    
    def create_assignment(self, title: str, description: str, assignment_type: str, 
                         language: str, deadline: str, teacher_id: int) -> int:
        """Tạo bài tập mới"""
        conn = sqlite3.connect("cs466_database.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO assignments (title, description, assignment_type, language, deadline, teacher_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, description, assignment_type, language, deadline, teacher_id))
        
        assignment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        if assignment_id is None:
            raise ValueError("Failed to create assignment")
        return assignment_id
    
    def get_assignment(self, assignment_id: int) -> Optional[Dict]:
        """Lấy thông tin bài tập"""
        conn = sqlite3.connect("cs466_database.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT a.*, u.full_name as teacher_name
            FROM assignments a
            JOIN users u ON a.teacher_id = u.id
            WHERE a.id = ?
        ''', (assignment_id,))
        
        assignment = cursor.fetchone()
        conn.close()
        
        if assignment:
            return {
                "id": assignment[0],
                "title": assignment[1],
                "description": assignment[2],
                "assignment_type": assignment[3],
                "language": assignment[4],
                "deadline": assignment[5],
                "teacher_id": assignment[6],
                "test_cases": json.loads(assignment[7]) if assignment[7] else [],
                "created_at": assignment[8],
                "teacher_name": assignment[9]
            }
        return None
    
    def get_assignments_by_teacher(self, teacher_id: int) -> List[Dict]:
        """Lấy danh sách bài tập của giáo viên"""
        conn = sqlite3.connect("cs466_database.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM assignments WHERE teacher_id = ?
            ORDER BY created_at DESC
        ''', (teacher_id,))
        
        assignments = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": assignment[0],
                "title": assignment[1],
                "description": assignment[2],
                "assignment_type": assignment[3],
                "language": assignment[4],
                "deadline": assignment[5],
                "teacher_id": assignment[6],
                "test_cases": json.loads(assignment[7]) if assignment[7] else [],
                "created_at": assignment[8]
            }
            for assignment in assignments
        ]
    
    def get_all_assignments(self) -> List[Dict]:
        """Lấy tất cả bài tập (cho sinh viên)"""
        conn = sqlite3.connect("cs466_database.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT a.*, u.full_name as teacher_name
            FROM assignments a
            JOIN users u ON a.teacher_id = u.id
            ORDER BY a.created_at DESC
        ''')
        
        assignments = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": assignment[0],
                "title": assignment[1],
                "description": assignment[2],
                "assignment_type": assignment[3],
                "language": assignment[4],
                "deadline": assignment[5],
                "teacher_id": assignment[6],
                "test_cases": json.loads(assignment[7]) if assignment[7] else [],
                "created_at": assignment[8],
                "teacher_name": assignment[9]
            }
            for assignment in assignments
        ]
    
    def submit_assignment(self, assignment_id: int, student_id: int, 
                         code: Optional[str] = None, answers: Optional[str] = None, files: Optional[List[UploadFile]] = None) -> int:
        """Nộp bài tập"""
        conn = sqlite3.connect("cs466_database.db")
        cursor = conn.cursor()
        
        file_paths = []
        if files:
            # Lưu multiple files
            upload_dir = "uploads"
            os.makedirs(upload_dir, exist_ok=True)
            for file in files:
                if file and file.filename:
                    file_path = os.path.join(upload_dir, f"{uuid.uuid4()}_{file.filename}")
                    with open(file_path, "wb") as f:
                        f.write(file.file.read())
                    file_paths.append(file_path)
        
        # Ensure submissions table has answers column
        cursor.execute("PRAGMA table_info(submissions)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'answers' not in columns:
            cursor.execute("ALTER TABLE submissions ADD COLUMN answers TEXT")
        
        cursor.execute('''
            INSERT INTO submissions (assignment_id, student_id, code, answers, file_path)
            VALUES (?, ?, ?, ?, ?)
        ''', (assignment_id, student_id, code, answers, json.dumps(file_paths) if file_paths else None))
        
        submission_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        if submission_id is None:
            raise ValueError("Failed to submit assignment")
        return submission_id
    
    def run_code(self, code: str, language: str) -> Dict:
        """Chạy code trực tuyến - Optimized for performance"""
        if language not in ["python", "perl"]:
            return {"error": "Language not supported"}
        
        # Quick validation
        if not code.strip():
            return {"error": "Empty code"}
        
        if len(code) > 10000:  # Limit code length
            return {"error": "Code too long (max 10000 characters)"}
        
        temp_file = None
        try:
            # Create temp file with UTF-8 encoding
            import tempfile
            fd, temp_file = tempfile.mkstemp(suffix=f'.{language}', text=True)
            
            # Write code with UTF-8 encoding
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Optimized environment setup
            env = {
                'PYTHONIOENCODING': 'utf-8',
                'PYTHONUNBUFFERED': '1',
                'PATH': os.environ.get('PATH', ''),
                'SYSTEMROOT': os.environ.get('SYSTEMROOT', ''),
                'TEMP': os.environ.get('TEMP', ''),
                'TMP': os.environ.get('TMP', '')
            }
            
            # Faster execution with reduced timeout
            timeout = 3  # Reduced from 5 to 3 seconds
            
            if language == "python":
                cmd = ["python", "-u", "-W", "ignore", temp_file]
            else:  # perl
                cmd = ["perl", temp_file]
            
            # Use asyncio for better performance
            import asyncio
            
            async def run_subprocess():
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    env=env
                )
                
                try:
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(), 
                        timeout=timeout
                    )
                    return_code = process.returncode
                    
                    # Decode output safely
                    output = stdout.decode('utf-8', errors='replace').strip() if stdout else ""
                    error = stderr.decode('utf-8', errors='replace').strip() if stderr else ""
                    
                    return output, error, return_code
                    
                except asyncio.TimeoutError:
                    process.kill()
                    await process.wait()
                    raise subprocess.TimeoutExpired(cmd, timeout)
            
            # Run the async function
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            output, error, return_code = loop.run_until_complete(run_subprocess())
            
            return {
                "output": output,
                "error": error,
                "return_code": return_code
            }
            
        except subprocess.TimeoutExpired:
            return {"error": f"Code execution timeout ({timeout}s)"}
        except Exception as e:
            return {"error": f"Execution error: {str(e)}"}
        finally:
            # Clean up temp file
            if temp_file:
                try:
                    os.unlink(temp_file)
                except:
                    pass
    
    def get_submissions(self, assignment_id: int) -> List[Dict]:
        """Lấy danh sách bài nộp"""
        conn = sqlite3.connect("cs466_database.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.*, u.full_name as student_name
            FROM submissions s
            JOIN users u ON s.student_id = u.id
            WHERE s.assignment_id = ?
            ORDER BY s.submitted_at DESC
        ''', (assignment_id,))
        
        submissions = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": submission[0],
                "assignment_id": submission[1],
                "student_id": submission[2],
                "code": submission[3],
                "file_path": submission[4],
                "result": submission[5],
                "score": submission[6],
                "submitted_at": submission[7],
                "student_name": submission[8]
            }
            for submission in submissions
        ] 