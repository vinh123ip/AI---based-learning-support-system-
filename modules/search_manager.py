"""
Advanced Search Manager for CS466 Learning System
Provides comprehensive search functionality for assignments, users, and courses
"""

import re
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

class SearchManager:
    def __init__(self):
        self.search_categories = {
            'assignments': {
                'name': 'Bài tập',
                'fields': ['title', 'description', 'language', 'assignment_type'],
                'filters': ['difficulty', 'language', 'assignment_type', 'teacher', 'date_range', 'status']
            },
            'users': {
                'name': 'Người dùng', 
                'fields': ['username', 'email', 'full_name', 'role'],
                'filters': ['role', 'registration_date', 'active_status']
            },
            'courses': {
                'name': 'Khóa học',
                'fields': ['title', 'description', 'content'],
                'filters': ['language', 'difficulty', 'topic', 'created_date']
            }
        }
        
    def search(self, query: str, category: str = 'all', filters: Optional[Dict] = None, 
               sort_by: str = 'relevance', limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """
        Perform advanced search across specified categories
        """
        if filters is None:
            filters = {}
            
        results = {
            'query': query,
            'category': category,
            'total_results': 0,
            'results': [],
            'suggestions': [],
            'filters_applied': filters,
            'search_time': 0
        }
        
        start_time = datetime.now()
        
        try:
            if category == 'all':
                # Search across all categories
                all_results = []
                for cat in self.search_categories.keys():
                    cat_results = self._search_category(query, cat, filters, sort_by, 10000, 0)  # Get all results first
                    all_results.extend(cat_results)
                
                # Sort all results together
                all_results = self._sort_results(all_results, sort_by)
                results['total_results'] = len(all_results)
                results['results'] = all_results[offset:offset + limit]
            else:
                # Search specific category - get total count first
                all_cat_results = self._search_category(query, category, filters, sort_by, 10000, 0)  # Get all results
                results['total_results'] = len(all_cat_results)
                results['results'] = all_cat_results[offset:offset + limit]
                
            results['suggestions'] = self._generate_suggestions(query, category)
            
        except Exception as e:
            # Log error silently in production
            results['error'] = str(e)
            
        end_time = datetime.now()
        results['search_time'] = (end_time - start_time).total_seconds()
        
        return results
    
    def _search_category(self, query: str, category: str, filters: Dict, 
                        sort_by: str, limit: int, offset: int = 0) -> List[Dict]:
        """Search within a specific category"""
        if category == 'assignments':
            return self._search_assignments(query, filters, sort_by, limit, offset)
        elif category == 'users':
            return self._search_users(query, filters, sort_by, limit, offset)
        elif category == 'courses':
            return self._search_courses(query, filters, sort_by, limit, offset)
        else:
            return []
    
    def _search_assignments(self, query: str, filters: Dict, sort_by: str, 
                           limit: int, offset: int) -> List[Dict]:
        """Search assignments with advanced filtering"""
        import sqlite3
        from datetime import datetime
        
        # Connect to database directly
        conn = sqlite3.connect('learning_system.db')
        cursor = conn.cursor()
        
        # Get all assignments with teacher names
        cursor.execute('''
            SELECT a.id, a.title, a.description, a.assignment_type, a.language, 
                   a.difficulty, a.teacher_id, a.deadline, a.starter_code, 
                   a.solution, a.test_cases, a.topic, a.ai_generated, 
                   a.ai_question_id, a.created_at, u.username as teacher_name
            FROM assignments a
            LEFT JOIN users u ON a.teacher_id = u.id
            ORDER BY a.created_at DESC
        ''')
        
        assignments = []
        for row in cursor.fetchall():
            assignment = {
                'id': row[0],
                'title': row[1] or '',
                'description': row[2] or '',
                'assignment_type': row[3] or '',
                'language': row[4] or '',
                'difficulty': row[5] or '',
                'teacher_id': row[6],
                'deadline': row[7] or '',
                'starter_code': row[8] or '',
                'solution': row[9] or '',
                'test_cases': row[10] or '',
                'topic': row[11] or '',
                'ai_generated': bool(row[12]) if row[12] else False,
                'ai_question_id': row[13],
                'created_at': row[14] or '',
                'teacher_name': row[15] or ''
            }
            assignments.append(assignment)
        
        conn.close()
        results = []
        
        for assignment in assignments:
            # If no query, show all assignments; otherwise calculate relevance
            if not query.strip():
                score = 1.0  # Default score for browsing all assignments
            else:
                score = self._calculate_relevance_score(query, assignment, 'assignments')
            
            # Only include items with positive relevance score and matching filters
            if score > 0 and self._apply_filters(assignment, filters, 'assignments'):
                result = {
                    'id': assignment.get('id'),
                    'type': 'assignment',
                    'title': assignment.get('title', ''),
                    'description': assignment.get('description', ''),
                    'language': assignment.get('language', ''),
                    'assignment_type': assignment.get('assignment_type', ''),
                    'teacher_name': assignment.get('teacher_name', ''),
                    'created_at': assignment.get('created_at', ''),
                    'deadline': assignment.get('deadline', ''),
                    'relevance_score': score,
                    'highlight': self._highlight_matches(query, assignment.get('title', ''))
                }
                results.append(result)
        
        # Sort results
        results = self._sort_results(results, sort_by)
        
        # Return all results (pagination handled at higher level)
        return results
    
    def _search_users(self, query: str, filters: Dict, sort_by: str, 
                     limit: int, offset: int) -> List[Dict]:
        """Search users with filtering"""
        import sqlite3
        
        # Connect to database directly
        conn = sqlite3.connect('learning_system.db')
        cursor = conn.cursor()
        
        # Get all users (excluding passwords)
        cursor.execute('''
            SELECT id, username, email, full_name, role, created_at
            FROM users
            ORDER BY created_at DESC
        ''')
        
        users = []
        for row in cursor.fetchall():
            user = {
                'id': row[0],
                'username': row[1] or '',
                'email': row[2] or '',
                'full_name': row[3] or '',
                'role': row[4] or '',
                'created_at': row[5] or ''
            }
            users.append(user)
        
        conn.close()
        results = []
        
        for user in users:
            # If no query, show all users; otherwise calculate relevance
            if not query.strip():
                score = 1.0  # Default score for browsing all users
            else:
                score = self._calculate_relevance_score(query, user, 'users')
            
            # Only include items with positive relevance score and matching filters
            if score > 0 and self._apply_filters(user, filters, 'users'):
                result = {
                    'id': user.get('id'),
                    'type': 'user',
                    'username': user.get('username', ''),
                    'email': user.get('email', ''),
                    'full_name': user.get('full_name', ''),
                    'role': user.get('role', ''),
                    'created_at': user.get('created_at', ''),
                    'relevance_score': score,
                    'highlight': self._highlight_matches(query, user.get('username', ''))
                }
                results.append(result)
        
        # Sort results
        results = self._sort_results(results, sort_by)
        
        # Return all results (pagination handled at higher level)
        return results
    
    def _search_courses(self, query: str, filters: Dict, sort_by: str, 
                       limit: int, offset: int) -> List[Dict]:
        """Search courses/lessons"""
        # Mock course data for now
        courses = [
            {
                'id': 1,
                'title': 'Python Cơ bản',
                'description': 'Học Python từ đầu với các khái niệm cơ bản',
                'language': 'python',
                'difficulty': 'easy',
                'topic': 'basic_syntax',
                'created_at': '2024-01-15'
            },
            {
                'id': 2, 
                'title': 'Vòng lặp trong Python',
                'description': 'Tìm hiểu về for, while loops và nested loops',
                'language': 'python',
                'difficulty': 'medium',
                'topic': 'loops',
                'created_at': '2024-01-20'
            },
            {
                'id': 3,
                'title': 'Hàm trong Python',
                'description': 'Định nghĩa hàm, tham số, return values',
                'language': 'python', 
                'difficulty': 'medium',
                'topic': 'functions',
                'created_at': '2024-01-25'
            }
        ]
        
        results = []
        
        for course in courses:
            # If no query, show all courses; otherwise calculate relevance
            if not query.strip():
                score = 1.0  # Default score for browsing all courses
            else:
                score = self._calculate_relevance_score(query, course, 'courses')
            
            # Only include items with positive relevance score and matching filters
            if score > 0 and self._apply_filters(course, filters, 'courses'):
                result = {
                    'id': course.get('id'),
                    'type': 'course',
                    'title': course.get('title', ''),
                    'description': course.get('description', ''),
                    'language': course.get('language', ''),
                    'difficulty': course.get('difficulty', ''),
                    'topic': course.get('topic', ''),
                    'created_at': course.get('created_at', ''),
                    'relevance_score': score,
                    'highlight': self._highlight_matches(query, course.get('title', ''))
                }
                results.append(result)
        
        # Sort results
        results = self._sort_results(results, sort_by)
        
        # Return all results (pagination handled at higher level)
        return results
    
    def _calculate_relevance_score(self, query: str, item: Dict, category: str) -> float:
        """Calculate relevance score for search results using advanced search algorithms"""
        if not query.strip():
            return 1.0
            
        query_lower = query.lower().strip()
        score = 0.0
        
        # Get searchable fields for category
        fields = self.search_categories[category]['fields']
        
        # Split query into words for multi-word search
        query_words = [word.strip() for word in query_lower.split() if word.strip()]
        
        for field in fields:
            field_value = str(item.get(field, '')).lower()
            
            if not field_value:
                continue
                
            # Calculate field-specific score
            field_score = 0.0
            
            # 1. Exact phrase match (highest priority)
            if query_lower in field_value:
                if query_lower == field_value:
                    # Perfect exact match
                    field_score += 50.0
                else:
                    # Substring match
                    field_score += 20.0
                    
                    # Bonus for start-of-string match
                    if field_value.startswith(query_lower):
                        field_score += 15.0
                    
                    # Bonus for word boundary match
                    try:
                        if re.search(r'\b' + re.escape(query_lower) + r'\b', field_value):
                            field_score += 10.0
                    except re.error:
                        pass
            
            # 2. Multi-word search - all words must be present
            if len(query_words) > 1:
                words_found = 0
                for word in query_words:
                    if word in field_value:
                        words_found += 1
                        # Bonus for word boundary
                        try:
                            if re.search(r'\b' + re.escape(word) + r'\b', field_value):
                                field_score += 3.0
                            else:
                                field_score += 1.0
                        except re.error:
                            field_score += 1.0
                
                # All words found bonus
                if words_found == len(query_words):
                    field_score += 15.0
                elif words_found > len(query_words) / 2:
                    # Partial match bonus
                    field_score += 5.0
                    
            # 3. Single character or partial matches
            elif len(query_words) == 1:
                word = query_words[0]
                char_matches = field_value.count(word)
                if char_matches > 0:
                    # Base score for character presence
                    field_score += min(char_matches * 2.0, 10.0)
                    
                    # Bonus for start of words
                    try:
                        start_matches = len(re.findall(r'\b' + re.escape(word), field_value))
                        field_score += start_matches * 3.0
                    except re.error:
                        pass
            
            # 4. Field weight multiplier
            if field in ['title', 'username', 'name']:
                # Title fields are most important
                field_score *= 3.0
            elif field in ['description']:
                # Description is secondary
                field_score *= 1.5
            elif field in ['keywords', 'tags']:
                # Keywords are also important
                field_score *= 2.0
            
            score += field_score
        
        # 5. Fuzzy matching for typos (Levenshtein distance)
        if score == 0.0:
            for field in fields:
                field_value = str(item.get(field, '')).lower()
                if field_value and field in ['title', 'username', 'name']:
                    # Check for typos in main fields only
                    similarity = self._calculate_similarity(query_lower, field_value)
                    if similarity > 0.7:  # 70% similarity threshold
                        score += similarity * 5.0
        
        # Return 0 if no match found (this will filter out non-matching items)
        return score if score > 0 else 0.0
    
    def _calculate_similarity(self, s1: str, s2: str) -> float:
        """Calculate similarity using Levenshtein distance algorithm"""
        if not s1 or not s2:
            return 0.0
        
        # Convert to lowercase for comparison
        s1, s2 = s1.lower(), s2.lower()
        
        # If strings are identical
        if s1 == s2:
            return 1.0
        
        # Check if one string contains the other
        if s1 in s2 or s2 in s1:
            return 0.8
        
        # Calculate Levenshtein distance
        len1, len2 = len(s1), len(s2)
        
        # Create matrix
        matrix = [[0] * (len2 + 1) for _ in range(len1 + 1)]
        
        # Initialize first row and column
        for i in range(len1 + 1):
            matrix[i][0] = i
        for j in range(len2 + 1):
            matrix[0][j] = j
        
        # Fill matrix
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                if s1[i-1] == s2[j-1]:
                    matrix[i][j] = matrix[i-1][j-1]
                else:
                    matrix[i][j] = min(
                        matrix[i-1][j] + 1,    # deletion
                        matrix[i][j-1] + 1,    # insertion
                        matrix[i-1][j-1] + 1   # substitution
                    )
        
        # Calculate similarity percentage
        max_len = max(len1, len2)
        distance = matrix[len1][len2]
        similarity = (max_len - distance) / max_len
        
        return max(0.0, similarity)
    
    def _apply_filters(self, item: Dict, filters: Dict, category: str) -> bool:
        """Apply filters to search results"""
        if not filters:
            return True
            
        for filter_key, filter_value in filters.items():
            if not filter_value:
                continue
                
            # Date range filter
            if filter_key == 'date_range':
                if not self._check_date_range(item, filter_value):
                    return False
                    
            # Difficulty filter
            elif filter_key == 'difficulty':
                if item.get('difficulty') != filter_value:
                    return False
                    
            # Language filter
            elif filter_key == 'language':
                if item.get('language') != filter_value:
                    return False
                    
            # Assignment type filter
            elif filter_key == 'assignment_type':
                if item.get('assignment_type') != filter_value:
                    return False
                    
            # Role filter
            elif filter_key == 'role':
                if item.get('role') != filter_value:
                    return False
                    
            # Teacher filter
            elif filter_key == 'teacher':
                teacher_name = item.get('teacher_name', '').lower()
                if filter_value.lower() not in teacher_name:
                    return False
                    
            # Status filter
            elif filter_key == 'status':
                if item.get('status') != filter_value:
                    return False
        
        return True
    
    def _check_date_range(self, item: Dict, date_range: str) -> bool:
        """Check if item falls within date range"""
        try:
            item_date_str = item.get('created_at') or item.get('deadline')
            if not item_date_str:
                return True
                
            # Parse date (handle different formats)
            if 'T' in item_date_str:
                item_date = datetime.fromisoformat(item_date_str.replace('Z', '+00:00'))
            else:
                item_date = datetime.strptime(item_date_str, '%Y-%m-%d')
                
            now = datetime.now()
            
            if date_range == 'today':
                return item_date.date() == now.date()
            elif date_range == 'week':
                return item_date >= now - timedelta(days=7)
            elif date_range == 'month':
                return item_date >= now - timedelta(days=30)
            elif date_range == 'year':
                return item_date >= now - timedelta(days=365)
                
        except Exception as e:
            print(f"Date range check error: {e}")
            
        return True
    
    def _sort_results(self, results: List[Dict], sort_by: str) -> List[Dict]:
        """Sort search results"""
        if sort_by == 'relevance':
            return sorted(results, key=lambda x: x.get('relevance_score', 0), reverse=True)
        elif sort_by == 'date_desc':
            return sorted(results, key=lambda x: x.get('created_at', ''), reverse=True)
        elif sort_by == 'date_asc':
            return sorted(results, key=lambda x: x.get('created_at', ''))
        elif sort_by == 'title':
            return sorted(results, key=lambda x: x.get('title', '').lower())
        else:
            return results
    
    def _highlight_matches(self, query: str, text: str) -> str:
        """Highlight search query matches in text with advanced highlighting"""
        if not query.strip() or not text:
            return text
        
        result_text = text
        query_lower = query.lower().strip()
        
        # Split query into words for multi-word highlighting
        query_words = [word.strip() for word in query_lower.split() if word.strip()]
        
        # Highlight each word
        for word in query_words:
            if len(word) > 0:
                # Create pattern that matches word boundaries for better highlighting
                try:
                    # First try exact word boundary match
                    pattern = r'\b(' + re.escape(word) + r')\b'
                    result_text = re.sub(pattern, r'<mark>\1</mark>', result_text, flags=re.IGNORECASE)
                    
                    # If no word boundary match found, try substring match
                    if '<mark>' not in result_text.lower() or word not in result_text.lower():
                        pattern = '(' + re.escape(word) + ')'
                        result_text = re.sub(pattern, r'<mark>\1</mark>', result_text, flags=re.IGNORECASE)
                        
                except re.error:
                    # Fallback to simple replacement
                    try:
                        # Case-insensitive replacement
                        result_text = re.sub(re.escape(word), f'<mark>{word}</mark>', result_text, flags=re.IGNORECASE)
                    except:
                        # Last resort: simple string replacement
                        result_text = result_text.replace(word, f'<mark>{word}</mark>')
        
        return result_text
    
    def _generate_suggestions(self, query: str, category: str) -> List[str]:
        """Generate search suggestions"""
        suggestions = []
        
        # Common search suggestions based on category
        if category == 'assignments' or category == 'all':
            suggestions.extend([
                'Python cơ bản',
                'Vòng lặp',
                'Hàm',
                'Cấu trúc dữ liệu',
                'Thuật toán',
                'Bài tập khó',
                'Trắc nghiệm'
            ])
            
        if category == 'users' or category == 'all':
            suggestions.extend([
                'Giáo viên',
                'Sinh viên',
                'Admin'
            ])
            
        if category == 'courses' or category == 'all':
            suggestions.extend([
                'Python tutorial',
                'Perl basics',
                'Programming fundamentals'
            ])
        
        # Filter suggestions that contain query
        if query.strip():
            query_lower = query.lower()
            suggestions = [s for s in suggestions if query_lower in s.lower()]
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def get_search_filters(self, category: str) -> Dict[str, Any]:
        """Get available filters for a category"""
        filters = {
            'assignments': {
                'difficulty': ['easy', 'medium', 'hard'],
                'language': ['python', 'perl'],
                'assignment_type': ['code', 'quiz', 'file'],
                'date_range': ['today', 'week', 'month', 'year'],
                'status': ['active', 'completed', 'overdue']
            },
            'users': {
                'role': ['student', 'teacher', 'admin'],
                'date_range': ['today', 'week', 'month', 'year'],
                'active_status': ['active', 'inactive']
            },
            'courses': {
                'language': ['python', 'perl'],
                'difficulty': ['easy', 'medium', 'hard'],
                'topic': ['basic_syntax', 'conditionals', 'loops', 'functions', 'data_structures', 'algorithms'],
                'date_range': ['today', 'week', 'month', 'year']
            }
        }
        
        return filters.get(category, {})
    
    def get_search_stats(self) -> Dict[str, Any]:
        """Get search statistics"""
        import sqlite3
        
        # Get real counts from database
        conn = sqlite3.connect('learning_system.db')
        cursor = conn.cursor()
        
        # Count assignments
        cursor.execute('SELECT COUNT(*) FROM assignments')
        assignments_count = cursor.fetchone()[0]
        
        # Count users
        cursor.execute('SELECT COUNT(*) FROM users')
        users_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_searchable_items': {
                'assignments': assignments_count,
                'users': users_count,
                'courses': 3  # Mock courses count
            },
            'popular_searches': [
                'Python cơ bản',
                'Vòng lặp',
                'Hàm',
                'Bài tập khó'
            ],
            'recent_searches': [
                'Python',
                'loop',
                'function',
                'algorithm'
            ]
        } 