import sqlite3
from typing import List, Dict, Optional
import json
import re
from datetime import datetime

class SearchManager:
    def __init__(self):
        self.init_database()
    
    def init_database(self):
        """Khởi tạo database cho search"""
        conn = sqlite3.connect("cs466_database.db")
        cursor = conn.cursor()
        
        # Tạo bảng search_index để tối ưu tìm kiếm
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_index (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_type TEXT NOT NULL,
                content_id INTEGER NOT NULL,
                title TEXT,
                description TEXT,
                keywords TEXT,
                language TEXT,
                difficulty TEXT,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        self.rebuild_search_index()
    
    def rebuild_search_index(self):
        """Rebuild search index từ dữ liệu hiện có"""
        conn = sqlite3.connect("cs466_database.db")
        cursor = conn.cursor()
        
        # Xóa index cũ
        cursor.execute("DELETE FROM search_index")
        
        # Index assignments
        cursor.execute('''
            SELECT id, title, description, assignment_type, language, created_at
            FROM assignments
        ''')
        assignments = cursor.fetchall()
        
        for assignment in assignments:
            keywords = self._extract_keywords(assignment[1] + " " + (assignment[2] or ""))
            difficulty = self._determine_difficulty(assignment[1], assignment[2])
            
            cursor.execute('''
                INSERT INTO search_index 
                (content_type, content_id, title, description, keywords, language, difficulty, category)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                "assignment",
                assignment[0],
                assignment[1],
                assignment[2],
                keywords,
                assignment[4],
                difficulty,
                assignment[3]
            ))
        
        # Index users (for teacher search)
        cursor.execute('''
            SELECT id, username, full_name, email, role
            FROM users WHERE role = 'teacher'
        ''')
        teachers = cursor.fetchall()
        
        for teacher in teachers:
            keywords = self._extract_keywords(teacher[1] + " " + (teacher[2] or ""))
            cursor.execute('''
                INSERT INTO search_index 
                (content_type, content_id, title, description, keywords, language, difficulty, category)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                "teacher",
                teacher[0],
                teacher[2] or teacher[1],
                teacher[3],
                keywords,
                "",
                "",
                "teacher"
            ))
        
        conn.commit()
        conn.close()
    
    def _extract_keywords(self, text: str) -> str:
        """Trích xuất keywords từ text"""
        if not text:
            return ""
        
        # Loại bỏ các từ thường gặp
        stop_words = {
            'và', 'của', 'trong', 'với', 'là', 'có', 'được', 'cho', 'từ', 'các',
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'have', 'has'
        }
        
        # Tách từ và loại bỏ stop words
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return " ".join(keywords)
    
    def _determine_difficulty(self, title: str, description: str) -> str:
        """Xác định độ khó dựa trên title và description"""
        text = (title + " " + (description or "")).lower()
        
        easy_keywords = ['hello', 'world', 'basic', 'simple', 'cơ bản', 'đơn giản']
        hard_keywords = ['advanced', 'complex', 'algorithm', 'nâng cao', 'phức tạp']
        
        if any(keyword in text for keyword in hard_keywords):
            return "hard"
        elif any(keyword in text for keyword in easy_keywords):
            return "easy"
        else:
            return "medium"
    
    def search(self, query: str, category: str = "all", filters: Dict = None) -> List[Dict]:
        """Tìm kiếm nâng cao"""
        conn = sqlite3.connect("cs466_database.db")
        cursor = conn.cursor()
        
        if filters is None:
            filters = {}
        
        # Build SQL query
        sql_conditions = []
        params = []
        
        # Text search
        if query.strip():
            sql_conditions.append('''
                (title LIKE ? OR description LIKE ? OR keywords LIKE ?)
            ''')
            query_pattern = f"%{query}%"
            params.extend([query_pattern, query_pattern, query_pattern])
        
        # Category filter
        if category != "all":
            sql_conditions.append("category = ?")
            params.append(category)
        
        # Language filter
        if filters.get("language"):
            sql_conditions.append("language = ?")
            params.append(filters["language"])
        
        # Difficulty filter
        if filters.get("difficulty"):
            sql_conditions.append("difficulty = ?")
            params.append(filters["difficulty"])
        
        # Date range filter
        if filters.get("date_from"):
            sql_conditions.append("created_at >= ?")
            params.append(filters["date_from"])
        
        if filters.get("date_to"):
            sql_conditions.append("created_at <= ?")
            params.append(filters["date_to"])
        
        # Build final query
        base_query = "SELECT * FROM search_index"
        if sql_conditions:
            base_query += " WHERE " + " AND ".join(sql_conditions)
        
        # Add ordering
        base_query += " ORDER BY created_at DESC"
        
        # Add limit
        limit = filters.get("limit", 50)
        base_query += f" LIMIT {limit}"
        
        cursor.execute(base_query, params)
        results = cursor.fetchall()
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_result = {
                "id": result[0],
                "content_type": result[1],
                "content_id": result[2],
                "title": result[3],
                "description": result[4],
                "keywords": result[5],
                "language": result[6],
                "difficulty": result[7],
                "category": result[8],
                "created_at": result[9]
            }
            
            # Get additional details based on content type
            if result[1] == "assignment":
                assignment_details = self._get_assignment_details(result[2])
                formatted_result.update(assignment_details)
            elif result[1] == "teacher":
                teacher_details = self._get_teacher_details(result[2])
                formatted_result.update(teacher_details)
            
            formatted_results.append(formatted_result)
        
        conn.close()
        return formatted_results
    
    def _get_assignment_details(self, assignment_id: int) -> Dict:
        """Lấy chi tiết bài tập"""
        conn = sqlite3.connect("cs466_database.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT a.deadline, u.full_name as teacher_name, 
                   COUNT(s.id) as submission_count
            FROM assignments a
            LEFT JOIN users u ON a.teacher_id = u.id
            LEFT JOIN submissions s ON a.id = s.assignment_id
            WHERE a.id = ?
            GROUP BY a.id
        ''', (assignment_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "deadline": result[0],
                "teacher_name": result[1],
                "submission_count": result[2]
            }
        return {}
    
    def _get_teacher_details(self, teacher_id: int) -> Dict:
        """Lấy chi tiết giáo viên"""
        conn = sqlite3.connect("cs466_database.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(id) as assignment_count
            FROM assignments
            WHERE teacher_id = ?
        ''', (teacher_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return {
            "assignment_count": result[0] if result else 0
        }
    
    def search_assignments(self, query: str, filters: Dict = None) -> List[Dict]:
        """Tìm kiếm bài tập"""
        if filters is None:
            filters = {}
        filters["content_type"] = "assignment"
        
        return self.search(query, "assignment", filters)
    
    def search_teachers(self, query: str) -> List[Dict]:
        """Tìm kiếm giáo viên"""
        return self.search(query, "teacher")
    
    def get_search_suggestions(self, query: str) -> List[str]:
        """Gợi ý tìm kiếm"""
        conn = sqlite3.connect("cs466_database.db")
        cursor = conn.cursor()
        
        # Tìm các từ khóa tương tự
        cursor.execute('''
            SELECT DISTINCT title FROM search_index
            WHERE title LIKE ?
            ORDER BY title
            LIMIT 10
        ''', (f"%{query}%",))
        
        suggestions = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return suggestions
    
    def get_popular_searches(self) -> List[Dict]:
        """Lấy các tìm kiếm phổ biến"""
        conn = sqlite3.connect("cs466_database.db")
        cursor = conn.cursor()
        
        # Tạo bảng search_history nếu chưa có
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                user_id INTEGER,
                search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            SELECT query, COUNT(*) as count
            FROM search_history
            WHERE search_time >= datetime('now', '-7 days')
            GROUP BY query
            ORDER BY count DESC
            LIMIT 10
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        return [{"query": row[0], "count": row[1]} for row in results]
    
    def log_search(self, query: str, user_id: int = None):
        """Ghi log tìm kiếm"""
        conn = sqlite3.connect("cs466_database.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO search_history (query, user_id)
            VALUES (?, ?)
        ''', (query, user_id))
        
        conn.commit()
        conn.close()
    
    def get_search_analytics(self) -> Dict:
        """Phân tích dữ liệu tìm kiếm"""
        conn = sqlite3.connect("cs466_database.db")
        cursor = conn.cursor()
        
        # Tổng số tìm kiếm
        cursor.execute("SELECT COUNT(*) FROM search_history")
        total_searches = cursor.fetchone()[0]
        
        # Tìm kiếm theo ngày
        cursor.execute('''
            SELECT DATE(search_time) as date, COUNT(*) as count
            FROM search_history
            WHERE search_time >= datetime('now', '-30 days')
            GROUP BY DATE(search_time)
            ORDER BY date
        ''')
        daily_searches = cursor.fetchall()
        
        # Từ khóa phổ biến
        cursor.execute('''
            SELECT query, COUNT(*) as count
            FROM search_history
            WHERE search_time >= datetime('now', '-30 days')
            GROUP BY query
            ORDER BY count DESC
            LIMIT 5
        ''')
        popular_queries = cursor.fetchall()
        
        conn.close()
        
        return {
            "total_searches": total_searches,
            "daily_searches": [{"date": row[0], "count": row[1]} for row in daily_searches],
            "popular_queries": [{"query": row[0], "count": row[1]} for row in popular_queries]
        }
    
    def advanced_search(self, search_params: Dict) -> List[Dict]:
        """Tìm kiếm nâng cao với nhiều tiêu chí"""
        query = search_params.get("query", "")
        category = search_params.get("category", "all")
        language = search_params.get("language", "")
        difficulty = search_params.get("difficulty", "")
        date_from = search_params.get("date_from", "")
        date_to = search_params.get("date_to", "")
        sort_by = search_params.get("sort_by", "created_at")
        sort_order = search_params.get("sort_order", "DESC")
        
        filters = {
            "language": language,
            "difficulty": difficulty,
            "date_from": date_from,
            "date_to": date_to,
            "sort_by": sort_by,
            "sort_order": sort_order
        }
        
        return self.search(query, category, filters) 