import openai
import json
import random
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import asyncio

class AIQuestionGenerator:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize AI Question Generator with OpenAI API"""
        self.api_key = api_key or "your-openai-api-key-here"
        if self.api_key != "your-openai-api-key-here":
            openai.api_key = self.api_key
        
        # Question templates for different topics
        self.topics = {
            "basic_syntax": {
                "name": "Cú pháp cơ bản",
                "description": "Variables, operators, basic I/O",
                "difficulty_range": ["easy", "medium"]
            },
            "conditionals": {
                "name": "Câu lệnh điều kiện", 
                "description": "if/else, logical operators",
                "difficulty_range": ["easy", "medium"]
            },
            "loops": {
                "name": "Vòng lặp",
                "description": "for, while loops, nested loops",
                "difficulty_range": ["easy", "medium", "hard"]
            },
            "functions": {
                "name": "Hàm",
                "description": "Function definition, parameters, return values",
                "difficulty_range": ["medium", "hard"]
            },
            "data_structures": {
                "name": "Cấu trúc dữ liệu",
                "description": "Lists, dictionaries, tuples",
                "difficulty_range": ["medium", "hard"]
            },
            "algorithms": {
                "name": "Thuật toán",
                "description": "Sorting, searching, recursion",
                "difficulty_range": ["hard"]
            }
        }
        
        # Predefined questions for fallback
        self.fallback_questions = self._load_fallback_questions()
    
    def _load_fallback_questions(self) -> Dict:
        """Load predefined questions as fallback when AI is not available"""
        return {
            "basic_syntax": {
                "easy": [
                    {
                        "title": "Tính tổng hai số",
                        "description": "Viết chương trình nhập vào hai số nguyên và in ra tổng của chúng.",
                        "starter_code": "# Nhập hai số\na = int(input('Nhập số thứ nhất: '))\nb = int(input('Nhập số thứ hai: '))\n\n# Tính tổng\n# Viết code của bạn ở đây\n",
                        "solution": "# Nhập hai số\na = int(input('Nhập số thứ nhất: '))\nb = int(input('Nhập số thứ hai: '))\n\n# Tính tổng\ntong = a + b\nprint(f'Tổng của {a} và {b} là: {tong}')",
                        "test_cases": [
                            {"input": ["5", "3"], "expected_output": "Tổng của 5 và 3 là: 8"},
                            {"input": ["10", "20"], "expected_output": "Tổng của 10 và 20 là: 30"}
                        ]
                    },
                    {
                        "title": "Kiểm tra số chẵn lẻ",
                        "description": "Viết chương trình nhập vào một số nguyên và kiểm tra số đó là chẵn hay lẻ.",
                        "starter_code": "# Nhập số\nn = int(input('Nhập một số: '))\n\n# Kiểm tra chẵn lẻ\n# Viết code của bạn ở đây\n",
                        "solution": "# Nhập số\nn = int(input('Nhập một số: '))\n\n# Kiểm tra chẵn lẻ\nif n % 2 == 0:\n    print(f'{n} là số chẵn')\nelse:\n    print(f'{n} là số lẻ')",
                        "test_cases": [
                            {"input": ["4"], "expected_output": "4 là số chẵn"},
                            {"input": ["7"], "expected_output": "7 là số lẻ"}
                        ]
                    }
                ],
                "medium": [
                    {
                        "title": "Tính giai thừa",
                        "description": "Viết chương trình tính giai thừa của một số nguyên dương.",
                        "starter_code": "# Nhập số\nn = int(input('Nhập số cần tính giai thừa: '))\n\n# Tính giai thừa\n# Viết code của bạn ở đây\n",
                        "solution": "# Nhập số\nn = int(input('Nhập số cần tính giai thừa: '))\n\n# Tính giai thừa\nfactorial = 1\nfor i in range(1, n + 1):\n    factorial *= i\n\nprint(f'Giai thừa của {n} là: {factorial}')",
                        "test_cases": [
                            {"input": ["5"], "expected_output": "Giai thừa của 5 là: 120"},
                            {"input": ["3"], "expected_output": "Giai thừa của 3 là: 6"}
                        ]
                    }
                ]
            },
            "loops": {
                "easy": [
                    {
                        "title": "In dãy số từ 1 đến N",
                        "description": "Viết chương trình in ra các số từ 1 đến N (N được nhập từ bàn phím).",
                        "starter_code": "# Nhập N\nn = int(input('Nhập N: '))\n\n# In dãy số\n# Viết code của bạn ở đây\n",
                        "solution": "# Nhập N\nn = int(input('Nhập N: '))\n\n# In dãy số\nfor i in range(1, n + 1):\n    print(i)",
                        "test_cases": [
                            {"input": ["5"], "expected_output": "1\n2\n3\n4\n5"},
                            {"input": ["3"], "expected_output": "1\n2\n3"}
                        ]
                    }
                ],
                "medium": [
                    {
                        "title": "Tính tổng các số từ 1 đến N",
                        "description": "Viết chương trình tính tổng các số từ 1 đến N.",
                        "starter_code": "# Nhập N\nn = int(input('Nhập N: '))\n\n# Tính tổng\n# Viết code của bạn ở đây\n",
                        "solution": "# Nhập N\nn = int(input('Nhập N: '))\n\n# Tính tổng\ntong = 0\nfor i in range(1, n + 1):\n    tong += i\n\nprint(f'Tổng từ 1 đến {n} là: {tong}')",
                        "test_cases": [
                            {"input": ["5"], "expected_output": "Tổng từ 1 đến 5 là: 15"},
                            {"input": ["10"], "expected_output": "Tổng từ 1 đến 10 là: 55"}
                        ]
                    }
                ]
            },
            "functions": {
                "medium": [
                    {
                        "title": "Hàm tính diện tích hình chữ nhật",
                        "description": "Viết hàm tính diện tích hình chữ nhật và sử dụng hàm đó.",
                        "starter_code": "# Định nghĩa hàm\ndef tinh_dien_tich(chieu_dai, chieu_rong):\n    # Viết code của bạn ở đây\n    pass\n\n# Sử dụng hàm\ncd = float(input('Nhập chiều dài: '))\ncr = float(input('Nhập chiều rong: '))\n\n# Gọi hàm và in kết quả\n# Viết code của bạn ở đây\n",
                        "solution": "# Định nghĩa hàm\ndef tinh_dien_tich(chieu_dai, chieu_rong):\n    return chieu_dai * chieu_rong\n\n# Sử dụng hàm\ncd = float(input('Nhập chiều dài: '))\ncr = float(input('Nhập chiều rong: '))\n\n# Gọi hàm và in kết quả\ndien_tich = tinh_dien_tich(cd, cr)\nprint(f'Diện tích hình chữ nhật là: {dien_tich}')",
                        "test_cases": [
                            {"input": ["5", "3"], "expected_output": "Diện tích hình chữ nhật là: 15.0"},
                            {"input": ["10", "2"], "expected_output": "Diện tích hình chữ nhật là: 20.0"}
                        ]
                    }
                ]
            }
        }
    
    async def generate_question(self, topic: str, difficulty: str = "medium", 
                              use_ai: bool = True) -> Dict:
        """Generate a question for given topic and difficulty"""
        
        if use_ai and self.api_key != "your-openai-api-key-here":
            try:
                return await self._generate_ai_question(topic, difficulty)
            except Exception as e:
                print(f"AI generation failed: {e}")
                return self._get_fallback_question(topic, difficulty)
        else:
            return self._get_fallback_question(topic, difficulty)
    
    async def _generate_ai_question(self, topic: str, difficulty: str) -> Dict:
        """Generate question using OpenAI API"""
        topic_info = self.topics.get(topic, {})
        topic_name = topic_info.get("name", topic)
        topic_desc = topic_info.get("description", "")
        
        prompt = f"""
Tạo một bài tập lập trình Python về chủ đề "{topic_name}" ({topic_desc}) với độ khó {difficulty}.

Yêu cầu:
1. Tiêu đề bài tập (ngắn gọn, tiếng Việt)
2. Mô tả chi tiết bài tập (tiếng Việt)
3. Code khởi tạo (starter code) với comment hướng dẫn
4. Lời giải hoàn chỉnh
5. Ít nhất 2 test case với input và expected output

Định dạng JSON:
{{
    "title": "Tiêu đề bài tập",
    "description": "Mô tả chi tiết...",
    "starter_code": "# Code khởi tạo\\n...",
    "solution": "# Lời giải hoàn chỉnh\\n...",
    "test_cases": [
        {{"input": ["input1", "input2"], "expected_output": "output"}},
        {{"input": ["input3", "input4"], "expected_output": "output"}}
    ]
}}

Độ khó {difficulty}:
- easy: Cơ bản, 1-2 bước logic
- medium: Trung bình, 3-5 bước logic, có thể dùng vòng lặp
- hard: Nâng cao, logic phức tạp, thuật toán

Hãy tạo bài tập phù hợp với học sinh Việt Nam.
"""
        
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Bạn là một giáo viên lập trình Python chuyên nghiệp, tạo bài tập cho học sinh Việt Nam."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            if content.startswith('```json'):
                content = content[7:-3]
            elif content.startswith('```'):
                content = content[3:-3]
            
            question_data = json.loads(content)
            
            # Add metadata
            question_data.update({
                "topic": topic,
                "difficulty": difficulty,
                "generated_by": "ai",
                "created_at": datetime.now().isoformat()
            })
            
            return question_data
            
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def _get_fallback_question(self, topic: str, difficulty: str) -> Dict:
        """Get predefined question as fallback"""
        topic_questions = self.fallback_questions.get(topic, {})
        difficulty_questions = topic_questions.get(difficulty, [])
        
        if not difficulty_questions:
            # Try other difficulties for this topic
            for diff in ["easy", "medium", "hard"]:
                if diff in topic_questions and topic_questions[diff]:
                    difficulty_questions = topic_questions[diff]
                    break
        
        if not difficulty_questions:
            # Default question if nothing found
            return self._get_default_question(topic, difficulty)
        
        # Select random question
        question = random.choice(difficulty_questions).copy()
        question.update({
            "topic": topic,
            "difficulty": difficulty,
            "generated_by": "fallback",
            "created_at": datetime.now().isoformat()
        })
        
        return question
    
    def _get_default_question(self, topic: str, difficulty: str) -> Dict:
        """Get default question when nothing else is available"""
        return {
            "title": f"Bài tập {self.topics.get(topic, {}).get('name', topic)}",
            "description": f"Viết chương trình Python về chủ đề {topic} với độ khó {difficulty}.",
            "starter_code": "# Viết code của bạn ở đây\n",
            "solution": "# Lời giải sẽ được cung cấp sau\npass",
            "test_cases": [
                {"input": [], "expected_output": "Kết quả mong đợi"}
            ],
            "topic": topic,
            "difficulty": difficulty,
            "generated_by": "default",
            "created_at": datetime.now().isoformat()
        }
    
    async def generate_multiple_questions(self, topic: str, count: int = 5, 
                                        difficulty: str = "medium") -> List[Dict]:
        """Generate multiple questions for a topic"""
        questions = []
        
        for i in range(count):
            try:
                question = await self.generate_question(topic, difficulty)
                questions.append(question)
                
                # Add small delay to avoid rate limiting
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"Error generating question {i+1}: {e}")
                # Add fallback question
                questions.append(self._get_fallback_question(topic, difficulty))
        
        return questions
    
    def get_available_topics(self) -> Dict:
        """Get list of available topics"""
        return self.topics
    
    def get_difficulty_levels(self) -> List[str]:
        """Get available difficulty levels"""
        return ["easy", "medium", "hard"]
    
    async def create_assignment_from_question(self, question_data: Dict, 
                                            teacher_id: int, 
                                            assignment_title: str = None,
                                            deadline_days: int = 7) -> Dict:
        """Create assignment from generated question"""
        
        title = assignment_title or question_data.get("title", "Bài tập được tạo tự động")
        
        assignment = {
            "title": title,
            "description": question_data.get("description", ""),
            "assignment_type": "code",
            "language": "python",
            "difficulty": question_data.get("difficulty", "medium"),
            "teacher_id": teacher_id,
            "deadline": (datetime.now() + timedelta(days=deadline_days)).isoformat(),
            "starter_code": question_data.get("starter_code", ""),
            "solution": question_data.get("solution", ""),
            "test_cases": json.dumps(question_data.get("test_cases", [])),
            "topic": question_data.get("topic", ""),
            "ai_generated": True,
            "created_at": datetime.now().isoformat()
        }
        
        return assignment

# Global instance
ai_generator = AIQuestionGenerator() 