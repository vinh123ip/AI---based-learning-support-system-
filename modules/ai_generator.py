import openai
import json
import random
from typing import List, Dict
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AIQuestionGenerator:
    def __init__(self):
        # Sử dụng API key từ environment variables
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.client = openai.OpenAI() if openai.api_key else None
        
    async def generate_questions(self, topic: str, difficulty: str, count: int) -> List[Dict]:
        """Sinh câu hỏi tự động bằng AI"""
        if not self.client:
            return self._generate_fallback_questions(topic, difficulty, count)
        
        try:
            prompt = f"""
            Tạo {count} câu hỏi {difficulty} về chủ đề "{topic}" trong lập trình Python/Perl.
            Mỗi câu hỏi phải có:
            1. Câu hỏi (question)
            2. 4 lựa chọn (options)
            3. Đáp án đúng (correct_index từ 0-3)
            4. Giải thích (explanation)
            
            Trả về JSON format:
            {{
                "questions": [
                    {{
                        "question": "Câu hỏi ở đây",
                        "options": ["A", "B", "C", "D"],
                        "correct_index": 0,
                        "explanation": "Giải thích đáp án"
                    }}
                ]
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Bạn là giáo viên lập trình chuyên nghiệp, tạo câu hỏi chất lượng cao."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            # Parse JSON response
            content = response.choices[0].message.content
            result = json.loads(content)
            return result.get("questions", [])
            
        except Exception as e:
            print(f"AI Error: {e}")
            return self._generate_fallback_questions(topic, difficulty, count)
    
    def _generate_fallback_questions(self, topic: str, difficulty: str, count: int) -> List[Dict]:
        """Tạo câu hỏi mẫu khi AI không khả dụng"""
        
        question_bank = {
            "python_basic": [
                {
                    "question": "Python là ngôn ngữ lập trình thuộc loại nào?",
                    "options": ["Compiled", "Interpreted", "Assembly", "Machine Language"],
                    "correct_index": 1,
                    "explanation": "Python là ngôn ngữ thông dịch (interpreted), code được thực thi trực tiếp mà không cần compile trước."
                },
                {
                    "question": "Từ khóa nào được dùng để khai báo hàm trong Python?",
                    "options": ["function", "def", "func", "define"],
                    "correct_index": 1,
                    "explanation": "Từ khóa 'def' được sử dụng để khai báo hàm trong Python."
                },
                {
                    "question": "Cách nào đúng để tạo comment trong Python?",
                    "options": ["// Comment", "/* Comment */", "# Comment", "<!-- Comment -->"],
                    "correct_index": 2,
                    "explanation": "Trong Python, sử dụng # để tạo comment một dòng."
                },
                {
                    "question": "Kiểu dữ liệu nào không có sẵn trong Python?",
                    "options": ["int", "str", "char", "float"],
                    "correct_index": 2,
                    "explanation": "Python không có kiểu dữ liệu 'char' riêng, ký tự được biểu diễn bằng string có độ dài 1."
                }
            ],
            "python_advanced": [
                {
                    "question": "Decorator trong Python được sử dụng để làm gì?",
                    "options": ["Trang trí code", "Modify function behavior", "Tạo class", "Import module"],
                    "correct_index": 1,
                    "explanation": "Decorator được sử dụng để modify hoặc extend behavior của function mà không thay đổi code gốc."
                },
                {
                    "question": "List comprehension nào sau đây tạo ra list [0, 2, 4, 6, 8]?",
                    "options": ["[x for x in range(10)]", "[x*2 for x in range(5)]", "[x for x in range(0,10,2)]", "Cả B và C"],
                    "correct_index": 3,
                    "explanation": "Cả [x*2 for x in range(5)] và [x for x in range(0,10,2)] đều tạo ra [0, 2, 4, 6, 8]."
                }
            ],
            "perl_basic": [
                {
                    "question": "Ký hiệu nào được dùng để khai báo scalar variable trong Perl?",
                    "options": ["@", "$", "%", "&"],
                    "correct_index": 1,
                    "explanation": "Trong Perl, scalar variables được khai báo với ký hiệu $."
                },
                {
                    "question": "Lệnh nào dùng để in ra màn hình trong Perl?",
                    "options": ["echo", "print", "printf", "Cả B và C"],
                    "correct_index": 3,
                    "explanation": "Perl có cả 'print' và 'printf' để in ra màn hình."
                }
            ],
            "data_structures": [
                {
                    "question": "Complexity của việc tìm kiếm trong hash table (best case) là gì?",
                    "options": ["O(1)", "O(log n)", "O(n)", "O(n²)"],
                    "correct_index": 0,
                    "explanation": "Hash table có complexity O(1) cho việc tìm kiếm trong best case."
                },
                {
                    "question": "Stack hoạt động theo nguyên tắc nào?",
                    "options": ["FIFO", "LIFO", "Random", "Priority"],
                    "correct_index": 1,
                    "explanation": "Stack hoạt động theo nguyên tắc LIFO (Last In, First Out)."
                }
            ]
        }
        
        # Chọn ngân hàng câu hỏi dựa trên topic và difficulty
        if "python" in topic.lower():
            if difficulty == "easy":
                questions = question_bank["python_basic"]
            else:
                questions = question_bank["python_advanced"]
        elif "perl" in topic.lower():
            questions = question_bank["perl_basic"]
        elif "data" in topic.lower() or "structure" in topic.lower():
            questions = question_bank["data_structures"]
        else:
            questions = question_bank["python_basic"]
        
        # Trộn và lấy số lượng câu hỏi yêu cầu
        random.shuffle(questions)
        return questions[:min(count, len(questions))]
    
    def generate_coding_exercise(self, topic: str, difficulty: str) -> Dict:
        """Tạo bài tập lập trình"""
        exercises = {
            "python_basic": [
                {
                    "title": "Hello World",
                    "description": "Viết chương trình in ra 'Hello, World!'",
                    "template": "# Viết code của bạn ở đây\nprint('Hello, World!')",
                    "test_cases": [
                        {"input": "", "expected": "Hello, World!"}
                    ]
                },
                {
                    "title": "Tính tổng",
                    "description": "Viết hàm tính tổng hai số",
                    "template": "def sum_two_numbers(a, b):\n    # Viết code của bạn ở đây\n    return a + b\n\n# Test\nprint(sum_two_numbers(3, 5))",
                    "test_cases": [
                        {"input": "3 5", "expected": "8"},
                        {"input": "10 -2", "expected": "8"}
                    ]
                }
            ],
            "python_advanced": [
                {
                    "title": "Fibonacci Sequence",
                    "description": "Viết hàm tạo dãy Fibonacci",
                    "template": "def fibonacci(n):\n    # Viết code của bạn ở đây\n    pass\n\n# Test\nprint(fibonacci(10))",
                    "test_cases": [
                        {"input": "5", "expected": "[0, 1, 1, 2, 3]"},
                        {"input": "8", "expected": "[0, 1, 1, 2, 3, 5, 8, 13]"}
                    ]
                }
            ]
        }
        
        if "python" in topic.lower():
            if difficulty == "easy":
                exercise_list = exercises["python_basic"]
            else:
                exercise_list = exercises["python_advanced"]
        else:
            exercise_list = exercises["python_basic"]
        
        return random.choice(exercise_list)
    
    def evaluate_code(self, code: str, expected_output: str) -> Dict:
        """Đánh giá code bằng AI"""
        if not self.client:
            return {"score": 0, "feedback": "AI không khả dụng"}
        
        try:
            prompt = f"""
            Đánh giá đoạn code Python sau:
            
            Code:
            ```python
            {code}
            ```
            
            Expected Output: {expected_output}
            
            Hãy đánh giá:
            1. Tính đúng đắn (0-40 điểm)
            2. Hiệu quả (0-20 điểm)
            3. Code style (0-20 điểm)
            4. Readability (0-20 điểm)
            
            Trả về JSON:
            {{
                "score": 85,
                "feedback": "Feedback chi tiết",
                "suggestions": ["Gợi ý 1", "Gợi ý 2"]
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Bạn là giáo viên lập trình chuyên nghiệp."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            result = json.loads(content)
            return result
            
        except Exception as e:
            return {"score": 0, "feedback": f"Lỗi đánh giá: {str(e)}", "suggestions": []}
    
    def get_learning_path(self, current_level: str, target_skill: str) -> List[Dict]:
        """Gợi ý lộ trình học tập"""
        learning_paths = {
            "beginner": {
                "python": [
                    {"topic": "Cú pháp cơ bản", "duration": "1 tuần", "resources": ["Tutorial", "Practice"]},
                    {"topic": "Biến và kiểu dữ liệu", "duration": "1 tuần", "resources": ["Video", "Exercise"]},
                    {"topic": "Cấu trúc điều khiển", "duration": "2 tuần", "resources": ["Tutorial", "Project"]},
                    {"topic": "Hàm và module", "duration": "2 tuần", "resources": ["Documentation", "Practice"]}
                ],
                "perl": [
                    {"topic": "Cú pháp cơ bản Perl", "duration": "1 tuần", "resources": ["Tutorial"]},
                    {"topic": "Regular Expression", "duration": "2 tuần", "resources": ["Practice", "Examples"]},
                    {"topic": "File handling", "duration": "1 tuần", "resources": ["Tutorial", "Project"]}
                ]
            },
            "intermediate": {
                "python": [
                    {"topic": "OOP trong Python", "duration": "2 tuần", "resources": ["Tutorial", "Project"]},
                    {"topic": "Exception handling", "duration": "1 tuần", "resources": ["Documentation"]},
                    {"topic": "Libraries và Frameworks", "duration": "3 tuần", "resources": ["Practice", "Project"]}
                ]
            }
        }
        
        return learning_paths.get(current_level, {}).get(target_skill, []) 