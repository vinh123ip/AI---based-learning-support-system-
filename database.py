import sqlite3
from datetime import datetime
import json

class Database:
    def __init__(self, db_name="learning_system.db"):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Initialize database with all required tables"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT,
                full_name TEXT,
                role TEXT DEFAULT 'student',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Assignments table - Updated with AI fields
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                assignment_type TEXT DEFAULT 'code',
                language TEXT DEFAULT 'python',
                difficulty TEXT DEFAULT 'medium',
                teacher_id INTEGER,
                deadline TIMESTAMP,
                starter_code TEXT,
                solution TEXT,
                test_cases TEXT,
                topic TEXT,
                ai_generated BOOLEAN DEFAULT 0,
                ai_question_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (teacher_id) REFERENCES users (id),
                FOREIGN KEY (ai_question_id) REFERENCES ai_questions (id)
            )
        ''')
        
        # AI Questions table - NEW
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                topic TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                starter_code TEXT,
                solution TEXT,
                test_cases TEXT,
                generated_by TEXT DEFAULT 'ai',
                teacher_id INTEGER,
                is_approved BOOLEAN DEFAULT 0,
                usage_count INTEGER DEFAULT 0,
                rating REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (teacher_id) REFERENCES users (id)
            )
        ''')
        
        # Question Topics table - NEW
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS question_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                parent_topic_id INTEGER,
                difficulty_levels TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_topic_id) REFERENCES question_topics (id)
            )
        ''')
        
        # Question Generation History - NEW
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS question_generation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id INTEGER,
                topic TEXT,
                difficulty TEXT,
                count INTEGER,
                success_count INTEGER,
                ai_used BOOLEAN,
                generation_time REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (teacher_id) REFERENCES users (id)
            )
        ''')
        
        # Submissions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                assignment_id INTEGER,
                student_id INTEGER,
                code TEXT,
                files TEXT,
                answers TEXT,
                score REAL,
                feedback TEXT,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (assignment_id) REFERENCES assignments (id),
                FOREIGN KEY (student_id) REFERENCES users (id)
            )
        ''')
        
        # Insert default topics
        self._insert_default_topics(cursor)
        
        # Insert default users if not exist
        self._insert_default_users(cursor)
        
        conn.commit()
        conn.close()
    
    def _insert_default_topics(self, cursor):
        """Insert default question topics"""
        topics = [
            ("Cú pháp cơ bản", "Variables, operators, basic I/O", None, '["easy", "medium"]'),
            ("Câu lệnh điều kiện", "if/else, logical operators", None, '["easy", "medium"]'),
            ("Vòng lặp", "for, while loops, nested loops", None, '["easy", "medium", "hard"]'),
            ("Hàm", "Function definition, parameters, return values", None, '["medium", "hard"]'),
            ("Cấu trúc dữ liệu", "Lists, dictionaries, tuples", None, '["medium", "hard"]'),
            ("Thuật toán", "Sorting, searching, recursion", None, '["hard"]'),
            ("Xử lý chuỗi", "String manipulation, formatting", None, '["easy", "medium"]'),
            ("Xử lý file", "File I/O operations", None, '["medium", "hard"]'),
            ("Lập trình hướng đối tượng", "Classes, objects, inheritance", None, '["hard"]'),
            ("Xử lý ngoại lệ", "Try/except, error handling", None, '["medium", "hard"]')
        ]
        
        for topic in topics:
            cursor.execute('''
                INSERT OR IGNORE INTO question_topics (name, description, parent_topic_id, difficulty_levels)
                VALUES (?, ?, ?, ?)
            ''', topic)
    
    def _insert_default_users(self, cursor):
        """Insert default users if they don't exist"""
        cursor.execute('SELECT COUNT(*) FROM users')
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO users (username, password, email, full_name, role)
                VALUES ('teacher', 'teacher123', 'teacher@example.com', 'Giáo viên', 'teacher')
            ''')
            cursor.execute('''
                INSERT INTO users (username, password, email, full_name, role)
                VALUES ('student', 'student123', 'student@example.com', 'Học sinh', 'student')
            ''')
    
    # AI Questions methods
    def save_ai_question(self, question_data: dict, teacher_id: int = None) -> int:
        """Save AI generated question to database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO ai_questions (
                title, description, topic, difficulty, starter_code, solution, 
                test_cases, generated_by, teacher_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            question_data.get('title', ''),
            question_data.get('description', ''),
            question_data.get('topic', ''),
            question_data.get('difficulty', 'medium'),
            question_data.get('starter_code', ''),
            question_data.get('solution', ''),
            json.dumps(question_data.get('test_cases', [])),
            question_data.get('generated_by', 'ai'),
            teacher_id,
            datetime.now().isoformat()
        ))
        
        question_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return question_id
    
    def get_ai_questions(self, teacher_id: int = None, topic: str = None, 
                        difficulty: str = None, limit: int = 20) -> list:
        """Get AI generated questions with filters"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        query = '''
            SELECT q.*, u.full_name as teacher_name
            FROM ai_questions q
            LEFT JOIN users u ON q.teacher_id = u.id
            WHERE 1=1
        '''
        params = []
        
        if teacher_id:
            query += ' AND q.teacher_id = ?'
            params.append(teacher_id)
        
        if topic:
            query += ' AND q.topic = ?'
            params.append(topic)
        
        if difficulty:
            query += ' AND q.difficulty = ?'
            params.append(difficulty)
        
        query += ' ORDER BY q.created_at DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        questions = []
        
        for row in cursor.fetchall():
            question = {
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'topic': row[3],
                'difficulty': row[4],
                'starter_code': row[5],
                'solution': row[6],
                'test_cases': json.loads(row[7]) if row[7] else [],
                'generated_by': row[8],
                'teacher_id': row[9],
                'is_approved': bool(row[10]),
                'usage_count': row[11],
                'rating': row[12],
                'created_at': row[13],
                'updated_at': row[14],
                'teacher_name': row[15] if row[15] else 'Unknown'
            }
            questions.append(question)
        
        conn.close()
        return questions
    
    def approve_ai_question(self, question_id: int, teacher_id: int) -> bool:
        """Approve an AI generated question"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE ai_questions 
            SET is_approved = 1, teacher_id = ?, updated_at = ?
            WHERE id = ?
        ''', (teacher_id, datetime.now().isoformat(), question_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def increment_question_usage(self, question_id: int):
        """Increment usage count for a question"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE ai_questions 
            SET usage_count = usage_count + 1
            WHERE id = ?
        ''', (question_id,))
        
        conn.commit()
        conn.close()
    
    def rate_ai_question(self, question_id: int, rating: float) -> bool:
        """Rate an AI generated question"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE ai_questions 
            SET rating = ?, updated_at = ?
            WHERE id = ?
        ''', (rating, datetime.now().isoformat(), question_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def get_question_topics(self) -> list:
        """Get all available question topics"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM question_topics 
            WHERE is_active = 1 
            ORDER BY name
        ''')
        
        topics = []
        for row in cursor.fetchall():
            topic = {
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'parent_topic_id': row[3],
                'difficulty_levels': json.loads(row[4]) if row[4] else [],
                'is_active': bool(row[5]),
                'created_at': row[6]
            }
            topics.append(topic)
        
        conn.close()
        return topics
    
    def save_generation_history(self, teacher_id: int, topic: str, difficulty: str, 
                               count: int, success_count: int, ai_used: bool, 
                               generation_time: float):
        """Save question generation history"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO question_generation_history (
                teacher_id, topic, difficulty, count, success_count, 
                ai_used, generation_time, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            teacher_id, topic, difficulty, count, success_count,
            ai_used, generation_time, datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def create_assignment_from_ai_question(self, question_id: int, teacher_id: int, 
                                         title: str = None, deadline: str = None) -> int:
        """Create assignment from AI question"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Get question data
        cursor.execute('SELECT * FROM ai_questions WHERE id = ?', (question_id,))
        question = cursor.fetchone()
        
        if not question:
            conn.close()
            return None
        
        # Create assignment
        assignment_title = title or question[1]  # question title
        assignment_deadline = deadline or (datetime.now() + timedelta(days=7)).isoformat()
        
        cursor.execute('''
            INSERT INTO assignments (
                title, description, assignment_type, language, difficulty,
                teacher_id, deadline, starter_code, solution, test_cases,
                topic, ai_generated, ai_question_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            assignment_title,
            question[2],  # description
            'code',
            'python',
            question[4],  # difficulty
            teacher_id,
            assignment_deadline,
            question[5],  # starter_code
            question[6],  # solution
            question[7],  # test_cases
            question[3],  # topic
            True,
            question_id,
            datetime.now().isoformat()
        ))
        
        assignment_id = cursor.lastrowid
        
        # Increment usage count
        cursor.execute('''
            UPDATE ai_questions 
            SET usage_count = usage_count + 1
            WHERE id = ?
        ''', (question_id,))
        
        conn.commit()
        conn.close()
        
        return assignment_id
    
    # Existing methods remain the same...
    def get_user_by_username(self, username):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        return user
    
    def create_assignment(self, title, description, assignment_type, language, difficulty, teacher_id, deadline, starter_code='', solution='', test_cases=''):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO assignments (title, description, assignment_type, language, difficulty, teacher_id, deadline, starter_code, solution, test_cases)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, description, assignment_type, language, difficulty, teacher_id, deadline, starter_code, solution, test_cases))
        assignment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return assignment_id
    
    def get_assignments(self, teacher_id=None):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        if teacher_id:
            cursor.execute('''
                SELECT a.*, u.full_name as teacher_name 
                FROM assignments a 
                JOIN users u ON a.teacher_id = u.id 
                WHERE a.teacher_id = ?
                ORDER BY a.created_at DESC
            ''', (teacher_id,))
        else:
            cursor.execute('''
                SELECT a.*, u.full_name as teacher_name 
                FROM assignments a 
                JOIN users u ON a.teacher_id = u.id 
                ORDER BY a.created_at DESC
            ''')
        
        assignments = []
        for row in cursor.fetchall():
            assignment = {
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'assignment_type': row[3],
                'language': row[4],
                'difficulty': row[5],
                'teacher_id': row[6],
                'deadline': row[7],
                'starter_code': row[8],
                'solution': row[9],
                'test_cases': row[10],
                'topic': row[11] if len(row) > 11 else '',
                'ai_generated': bool(row[12]) if len(row) > 12 else False,
                'ai_question_id': row[13] if len(row) > 13 else None,
                'created_at': row[14] if len(row) > 14 else row[11],
                'teacher_name': row[-1]
            }
            assignments.append(assignment)
        
        conn.close()
        return assignments
    
    def get_assignment_by_id(self, assignment_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT a.*, u.full_name as teacher_name 
            FROM assignments a 
            JOIN users u ON a.teacher_id = u.id 
            WHERE a.id = ?
        ''', (assignment_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'assignment_type': row[3],
                'language': row[4],
                'difficulty': row[5],
                'teacher_id': row[6],
                'deadline': row[7],
                'starter_code': row[8],
                'solution': row[9],
                'test_cases': row[10],
                'topic': row[11] if len(row) > 11 else '',
                'ai_generated': bool(row[12]) if len(row) > 12 else False,
                'ai_question_id': row[13] if len(row) > 13 else None,
                'created_at': row[14] if len(row) > 14 else row[11],
                'teacher_name': row[-1]
            }
        return None
    
    def submit_assignment(self, assignment_id, student_id, code='', files='', answers=''):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO submissions (assignment_id, student_id, code, files, answers)
            VALUES (?, ?, ?, ?, ?)
        ''', (assignment_id, student_id, code, files, answers))
        submission_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return submission_id
    
    def get_submissions(self, assignment_id=None, student_id=None):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        query = '''
            SELECT s.*, a.title as assignment_title, u.full_name as student_name
            FROM submissions s
            JOIN assignments a ON s.assignment_id = a.id
            JOIN users u ON s.student_id = u.id
            WHERE 1=1
        '''
        params = []
        
        if assignment_id:
            query += ' AND s.assignment_id = ?'
            params.append(assignment_id)
        
        if student_id:
            query += ' AND s.student_id = ?'
            params.append(student_id)
        
        query += ' ORDER BY s.submitted_at DESC'
        
        cursor.execute(query, params)
        submissions = []
        
        for row in cursor.fetchall():
            submission = {
                'id': row[0],
                'assignment_id': row[1],
                'student_id': row[2],
                'code': row[3],
                'files': row[4],
                'answers': row[5],
                'score': row[6],
                'feedback': row[7],
                'submitted_at': row[8],
                'assignment_title': row[9],
                'student_name': row[10]
            }
            submissions.append(submission)
        
        conn.close()
        return submissions
    
    # ================================
    # SEARCH METHODS - F17
    # ================================
    
    def get_all_assignments(self):
        """Get all assignments for search"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT a.*, u.username as teacher_name
            FROM assignments a
            LEFT JOIN users u ON a.teacher_id = u.id
            ORDER BY a.created_at DESC
        ''')
        
        assignments = []
        for row in cursor.fetchall():
            assignment = {
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'assignment_type': row[3],
                'language': row[4],
                'difficulty': row[5],
                'teacher_id': row[6],
                'deadline': row[7],
                'starter_code': row[8],
                'solution': row[9],
                'test_cases': row[10],
                'topic': row[11] if len(row) > 11 else '',
                'ai_generated': bool(row[12]) if len(row) > 12 else False,
                'ai_question_id': row[13] if len(row) > 13 else None,
                'created_at': row[14] if len(row) > 14 else row[11],
                'teacher_name': row[-1]
            }
            assignments.append(assignment)
        
        conn.close()
        return assignments
    
    def get_all_users(self):
        """Get all users for search (excluding passwords)"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, username, email, full_name, role, created_at
            FROM users
            ORDER BY created_at DESC
        ''')
        
        users = []
        for row in cursor.fetchall():
            user = {
                'id': row[0],
                'username': row[1],
                'email': row[2],
                'full_name': row[3],
                'role': row[4],
                'created_at': row[5]
            }
            users.append(user)
        
        conn.close()
        return users

# Global database instance
db = Database() 