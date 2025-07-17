import sys
import os
import locale

# Force UTF-8 encoding for the entire application
if sys.platform.startswith('win'):
    # Windows UTF-8 setup
    os.system('chcp 65001 > nul')
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONLEGACYWINDOWSSTDIO'] = '1'
    
# Set locale to UTF-8
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
    except:
        pass

from fastapi import FastAPI, Request, Depends, HTTPException, status, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
import sqlite3
from typing import Optional
import json
import asyncio
from modules.auth import AuthManager
from modules.assignments import AssignmentManager
from modules.ai_question_generator import AIQuestionGenerator
from modules.search_manager import SearchManager
from modules.interactive_executor import InteractiveExecutor
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = FastAPI(
    title="CS466 Learning System", 
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize managers
auth_manager = AuthManager()
assignment_manager = AssignmentManager()
ai_generator = AIQuestionGenerator()
search_manager = SearchManager()
interactive_executor = InteractiveExecutor()

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"user_id": user_id, "role": role}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def send_reset_password_email(to_email: str, user_name: str, reset_token: str) -> bool:
    """Gửi email reset password với link"""
    try:
        from config import get_config
        config = get_config()
        
        # Check SMTP config
        if not config.SMTP_USERNAME or not config.SMTP_PASSWORD:
            print("SMTP not configured")
            return False
        
        # Create reset link
        reset_link = f"http://localhost:8000/reset-password?token={reset_token}"
        
        # Email content
        subject = "Reset mật khẩu - CS466"
        
        body = f"""
Xin chào {user_name},

Bạn đã yêu cầu reset mật khẩu cho tài khoản CS466 Learning System.

Vui lòng click vào link dưới đây để đặt lại mật khẩu:
{reset_link}

Link này sẽ hết hạn sau 10 phút.

Nếu bạn không yêu cầu reset mật khẩu, vui lòng bỏ qua email này.

Trân trọng,
CS466 Learning System
        """
        
        # Create message
        message = MIMEMultipart()
        message['Subject'] = subject
        message['From'] = config.SMTP_USERNAME
        message['To'] = to_email
        
        message.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # Send email
        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        server.starttls()
        server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
        server.send_message(message)
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"Email error: {e}")
        return False

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Trang chủ - Đăng nhập"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Trang đăng ký"""
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register(
    username: str = Form(...),
    password: str = Form(...),
    email: str = Form(...),
    full_name: str = Form(...),
    role: str = Form("student")
):
    """Xử lý đăng ký"""
    if role not in ["teacher", "student"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    # Đăng ký user mới
    success = auth_manager.register_user(username, password, role, full_name, email)
    if not success:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    return {"success": True, "message": "Registration successful"}

@app.post("/send-otp")
async def send_otp(email: str = Form(...)):
    """Gửi OTP đến email (chỉ khi user bật 2FA)"""
    try:
        success, message = auth_manager.send_otp_to_email_if_2fa_enabled(email)
        return {"success": success, "message": message}
    except Exception as e:
        # Silent fail - không thông báo lỗi chi tiết
        return {"success": False, "message": ""}

@app.post("/login")
async def login(email: str = Form(...), password: str = Form(...), otp: str = Form(default="")):
    """Xử lý đăng nhập với 2FA conditional"""
    try:
        # Xác thực email + password + OTP (nếu 2FA bật)
        success, message, user_data = auth_manager.verify_login_with_conditional_otp(email, password, otp)
        
        if not success:
            raise HTTPException(status_code=401, detail=message)
        
        # Tạo access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth_manager.create_access_token(
            data={"sub": str(user_data["id"]), "role": user_data["role"]},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token, 
            "token_type": "bearer", 
            "role": user_data["role"],
            "message": message
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Lỗi hệ thống")

@app.get("/dashboard/{role}", response_class=HTMLResponse)
async def dashboard(request: Request, role: str):
    """Dashboard cho GV, SV hoặc Admin"""
    if role not in ["teacher", "student", "admin"]:
        raise HTTPException(status_code=404, detail="Not found")
    
    # Check if user has valid token in JavaScript
    if role == "teacher":
        return templates.TemplateResponse("teacher_dashboard.html", {"request": request})
    elif role == "admin":
        return templates.TemplateResponse("admin_dashboard.html", {"request": request})
    else:
        return templates.TemplateResponse("student_dashboard.html", {"request": request})

@app.get("/code-editor", response_class=HTMLResponse)
async def code_editor(request: Request):
    """Standalone code editor page like online-python.com"""
    # Check if user has token in JavaScript, no server-side auth required
    return templates.TemplateResponse("code_editor.html", {"request": request})

@app.get("/assignment/create", response_class=HTMLResponse)
async def create_assignment_page(request: Request, user: dict = Depends(get_current_user)):
    """Trang tạo bài tập (chỉ GV)"""
    if user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Access denied")
    return templates.TemplateResponse("create_assignment.html", {"request": request, "user": user})

@app.post("/assignment/create")
async def create_assignment(
    title: str = Form(...),
    description: str = Form(...),
    assignment_type: str = Form(...),
    language: str = Form(...),
    deadline: str = Form(...),
    user: dict = Depends(get_current_user)
):
    """Tạo bài tập mới"""
    if user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Access denied")
    
    assignment_id = assignment_manager.create_assignment(
        title=title,
        description=description,
        assignment_type=assignment_type,
        language=language,
        deadline=deadline,
        teacher_id=user["user_id"]
    )
    
    return {"success": True, "assignment_id": assignment_id}

@app.get("/assignment/{assignment_id}", response_class=HTMLResponse)
async def view_assignment(request: Request, assignment_id: int, user: dict = Depends(get_current_user)):
    """Xem chi tiết bài tập"""
    assignment = assignment_manager.get_assignment(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    return templates.TemplateResponse("assignment_detail.html", {
        "request": request,
        "assignment": assignment,
        "user": user
    })

@app.get("/assignment/{assignment_id}/solve", response_class=HTMLResponse)
async def solve_assignment(request: Request, assignment_id: int, user: dict = Depends(get_current_user)):
    """Trang làm bài tập"""
    if user["role"] != "student":
        raise HTTPException(status_code=403, detail="Access denied")
    
    assignment = assignment_manager.get_assignment(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    return templates.TemplateResponse("solve_assignment.html", {
        "request": request,
        "assignment": assignment,
        "user": user
    })

@app.post("/assignment/{assignment_id}/submit")
async def submit_assignment(
    assignment_id: int,
    code: Optional[str] = Form(None),
    answers: Optional[str] = Form(None),
    files: Optional[list[UploadFile]] = File(None),
    user: dict = Depends(get_current_user)
):
    """Nộp bài tập"""
    if user["role"] != "student":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Validate assignment exists
    assignment = assignment_manager.get_assignment(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Check deadline
    deadline = datetime.fromisoformat(assignment['deadline'].replace('Z', '+00:00'))
    if datetime.now() > deadline:
        raise HTTPException(status_code=400, detail="Assignment deadline has passed")
    
    submission_id = assignment_manager.submit_assignment(
        assignment_id=assignment_id,
        student_id=user["user_id"],
        code=code,
        answers=answers,
        files=files
    )
    
    return {"success": True, "submission_id": submission_id}

# ================================
# AI QUESTION GENERATOR ENDPOINTS
# ================================

@app.get("/ai/question-generator", response_class=HTMLResponse)
async def ai_question_generator_page(request: Request):
    """Trang sinh câu hỏi AI"""
    # Check authentication in JavaScript, not server-side
    try:
        topics = ai_generator.get_available_topics()
        return templates.TemplateResponse("ai_question_generator.html", {
            "request": request,
            "topics": topics
        })
    except Exception as e:
        # Log error silently in production
        return templates.TemplateResponse("ai_question_generator.html", {
            "request": request,
            "topics": []
        })

@app.post("/ai/generate-question")
async def generate_single_question(
    topic: str = Form(...),
    difficulty: str = Form("medium"),
    use_ai: bool = Form(True)
):
    """Generate a single question using AI - No auth required for demo"""
    try:
        question = await ai_generator.generate_question(topic, difficulty, use_ai)
        
        # Save to database (using demo teacher_id = 1)
        from database import db
        question_id = db.save_ai_question(question, 1)  # Demo teacher ID
        question["id"] = question_id
        
        return {"success": True, "question": question}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/ai/generate-multiple-questions")
async def generate_multiple_questions(
    topic: str = Form(...),
    difficulty: str = Form("medium"),
    count: int = Form(3),
    use_ai: bool = Form(True)
):
    """Generate multiple questions using AI - No auth required for demo"""
    
    try:
        import time
        start_time = time.time()
        
        questions = await ai_generator.generate_multiple_questions(topic, count, difficulty)
        
        # Save to database (using demo teacher_id = 1)
        from database import db
        saved_questions = []
        success_count = 0
        
        for question in questions:
            try:
                question_id = db.save_ai_question(question, 1)  # Demo teacher ID
                question["id"] = question_id
                saved_questions.append(question)
                success_count += 1
            except Exception as e:
                # Log error silently in production
                pass
        
        generation_time = time.time() - start_time
        
        # Save generation history
        db.save_generation_history(
            teacher_id=1,  # Demo teacher ID
            topic=topic,
            difficulty=difficulty,
            count=count,
            success_count=success_count,
            ai_used=use_ai,
            generation_time=generation_time
        )
        
        return {
            "success": True, 
            "questions": saved_questions,
            "generated_count": success_count,
            "generation_time": round(generation_time, 2)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/ai/questions")
async def get_ai_questions(
    topic: str = None,
    difficulty: str = None,
    limit: int = 20,
    user: dict = Depends(get_current_user)
):
    """Get AI generated questions"""
    if user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Access denied")
    
    from database import db
    questions = db.get_ai_questions(
        teacher_id=int(user["user_id"]),
        topic=topic,
        difficulty=difficulty,
        limit=limit
    )
    
    return {"success": True, "questions": questions}

@app.post("/ai/question/{question_id}/create-assignment")
async def create_assignment_from_ai_question(
    question_id: int,
    title: str = Form(None),
    deadline_days: int = Form(7),
    user: dict = Depends(get_current_user)
):
    """Create assignment from AI generated question"""
    if user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Access denied")
    
    from database import db
    from datetime import datetime, timedelta
    
    deadline = (datetime.now() + timedelta(days=deadline_days)).isoformat()
    
    assignment_id = db.create_assignment_from_ai_question(
        question_id=question_id,
        teacher_id=int(user["user_id"]),
        title=title,
        deadline=deadline
    )
    
    if assignment_id:
        return {"success": True, "assignment_id": assignment_id}
    else:
        return {"success": False, "error": "Failed to create assignment"}

@app.get("/ai/topics")
async def get_ai_topics():
    """Get available AI question topics - No auth required for basic access"""
    topics = ai_generator.get_available_topics()
    difficulty_levels = ai_generator.get_difficulty_levels()
    
    try:
        from database import db
        db_topics = db.get_question_topics()
    except:
        db_topics = []
    
    return {
        "success": True,
        "topics": topics,
        "difficulty_levels": difficulty_levels,
        "db_topics": db_topics
    }

# ================================
# ADVANCED SEARCH ENDPOINTS - F17
# ================================

@app.get("/search", response_class=HTMLResponse)
async def search_page(request: Request):
    """Trang tìm kiếm nâng cao - F17"""
    # No authentication required for search page access
    return templates.TemplateResponse("search.html", {"request": request})

@app.get("/test-search", response_class=HTMLResponse)
async def test_search_page(request: Request):
    """Trang test search đơn giản"""
    return templates.TemplateResponse("test_search.html", {"request": request})

@app.post("/search")
async def search(request: Request):
    """API tìm kiếm nâng cao - F17 - Nhận cả Form và JSON"""
    try:
        # Check content type
        content_type = request.headers.get("content-type", "")
        
        if "application/json" in content_type:
            # Handle JSON request
            body = await request.json()
            query = str(body.get("query", ""))
            category = str(body.get("category", "all"))
            filters_dict = body.get("filters", {})
            sort_by = str(body.get("sort_by", "relevance"))
            limit = int(body.get("limit", 20))
            offset = int(body.get("offset", 0))
        else:
            # Handle Form data (legacy support)
            form = await request.form()
            query = str(form.get("query", ""))
            category = str(form.get("category", "all"))
            filters_str = str(form.get("filters", "{}"))
            filters_dict = json.loads(filters_str) if filters_str else {}
            sort_by = str(form.get("sort_by", "relevance"))
            limit = int(form.get("limit", 20))
            offset = int(form.get("offset", 0))
        
        results = search_manager.search(
            query=query,
            category=category,
            filters=filters_dict,
            sort_by=sort_by,
            limit=limit,
            offset=offset
        )
        
        return {"success": True, "data": results}
        
    except Exception as e:
        # Log error silently in production
        return {"success": False, "error": str(e)}

@app.get("/search/filters/{category}")
async def get_search_filters(category: str):
    """Lấy danh sách filters cho category"""
    filters = search_manager.get_search_filters(category)
    return {"success": True, "filters": filters}

@app.get("/search/suggestions")
async def get_search_suggestions(query: str = "", category: str = "all"):
    """Lấy gợi ý tìm kiếm"""
    suggestions = search_manager._generate_suggestions(query, category)
    return {"success": True, "suggestions": suggestions}

@app.get("/search/stats")
async def get_search_stats():
    """Thống kê tìm kiếm"""
    stats = search_manager.get_search_stats()
    return {"success": True, "stats": stats}

@app.post("/code/run")
async def run_code(
    code: str = Form(...),
    language: str = Form(...),
    user: dict = Depends(get_current_user)
):
    """Run code online - Basic execution without input"""
    # Quick validation
    if not code or not code.strip():
        return {"success": False, "result": {"error": "Empty code"}}
    
    if len(code) > 10000:
        return {"success": False, "result": {"error": "Code too long"}}
    
    # Check if code has input() calls
    if "input(" in code and language == "python":
        return {
            "success": False, 
            "result": {
                "error": "Code contains input() calls. Please use Interactive Mode or provide fixed values.",
                "suggestion": "Use /code/run-interactive endpoint for input handling"
            }
        }
    
    # Run code asynchronously for better performance
    try:
        import asyncio
        import concurrent.futures
        
        loop = asyncio.get_event_loop()
        
        # Execute in thread pool to avoid blocking
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future = loop.run_in_executor(
                executor, 
                assignment_manager.run_code, 
                code, 
                language
            )
            
            # Wait for result with timeout
            try:
                result = await asyncio.wait_for(future, timeout=5.0)
            except asyncio.TimeoutError:
                return {"success": False, "result": {"error": "Request timeout"}}
        
        return {"success": True, "result": result}
        
    except Exception as e:
        return {"success": False, "result": {"error": f"Server error: {str(e)}"}}

@app.post("/code/run-interactive")
async def run_interactive_code(
    code: str = Form(...),
    inputs: str = Form("[]"),  # JSON array of input values
    user: dict = Depends(get_current_user)
):
    """Run Python code with interactive input support like online-python.com"""
    # Validation
    if not code or not code.strip():
        return {"success": False, "result": {"error": "Empty code"}}
    
    if len(code) > 10000:
        return {"success": False, "result": {"error": "Code too long"}}
    
    try:
        # Parse inputs
        import json
        input_list = json.loads(inputs) if inputs else []
        
        # Execute with inputs
        result = await interactive_executor.execute_with_inputs(code, input_list)
        
        return result
        
    except json.JSONDecodeError:
        return {"success": False, "result": {"error": "Invalid input format"}}
    except Exception as e:
        return {"success": False, "result": {"error": f"Execution error: {str(e)}"}}

# API endpoints for dashboard data
@app.get("/api/dashboard-stats")
async def get_dashboard_stats(user: dict = Depends(get_current_user)):
    """API lấy thống kê dashboard"""
    try:
        if user["role"] == "student":
            # Mock data cho sinh viên
            return {
                "total": 15,
                "completed": 8,
                "pending": 7,
                "progress": 53
            }
        else:
            # Mock data cho giáo viên
            return {
                "totalAssignments": 15,
                "totalStudents": 25,
                "totalSubmissions": 87,
                "avgScore": 85
            }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/api/assignments")
async def get_assignments(user: dict = Depends(get_current_user)):
    """API lấy danh sách bài tập"""
    if user["role"] == "student":
        assignments = assignment_manager.get_all_assignments()
    else:
        assignments = assignment_manager.get_assignments_by_teacher(int(user["user_id"]))
    
    return assignments

@app.get("/api/teacher/assignments") 
async def get_teacher_assignments(user: dict = Depends(get_current_user)):
    """API lấy bài tập của giáo viên"""
    if user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Access denied")
    
    assignments = assignment_manager.get_assignments_by_teacher(int(user["user_id"]))
    return assignments

# ================================
# ADMIN API ENDPOINTS
# ================================

@app.get("/api/admin/users")
async def get_all_users(user: dict = Depends(get_current_user)):
    """API lấy danh sách tất cả người dùng (chỉ admin)"""
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        conn = sqlite3.connect("cs466_database.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email, full_name, role, created_at
            FROM users ORDER BY created_at DESC
        ''')
        
        users = []
        for row in cursor.fetchall():
            users.append({
                "id": row[0],
                "username": row[1],
                "email": row[2],
                "full_name": row[3],
                "role": row[4],
                "created_at": row[5],
                "status": "active"  # Default active status
            })
        
        conn.close()
        return {"success": True, "users": users}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database error")

@app.get("/api/admin/stats")
async def get_admin_stats(user: dict = Depends(get_current_user)):
    """API lấy thống kê cho admin dashboard"""
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        conn = sqlite3.connect("cs466_database.db")
        cursor = conn.cursor()
        
        # Count users by role
        cursor.execute("SELECT role, COUNT(*) FROM users GROUP BY role")
        role_counts = dict(cursor.fetchall())
        
        # Total users
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "success": True,
            "stats": {
                "students": role_counts.get("student", 0),
                "teachers": role_counts.get("teacher", 0),
                "admins": role_counts.get("admin", 0),
                "total": total_users
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database error")

@app.post("/api/admin/users")
async def create_user(
    username: str = Form(...),
    email: str = Form(...),
    full_name: str = Form(...),
    role: str = Form(...),
    password: str = Form(...),
    is_active: bool = Form(True),
    user: dict = Depends(get_current_user)
):
    """API tạo người dùng mới (chỉ admin)"""
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Validate role
        if role not in ["admin", "teacher", "student"]:
            raise HTTPException(status_code=400, detail="Invalid role")
        
        # Validate password
        if len(password) < 6:
            raise HTTPException(status_code=400, detail="Mật khẩu phải có ít nhất 6 ký tự")
        
        if not any(c.isupper() for c in password):
            raise HTTPException(status_code=400, detail="Mật khẩu phải có ít nhất 1 chữ in hoa")
        
        if not any(c.isdigit() for c in password):
            raise HTTPException(status_code=400, detail="Mật khẩu phải có ít nhất 1 chữ số")
        
        if not any(c.isalpha() for c in password):
            raise HTTPException(status_code=400, detail="Mật khẩu phải có ít nhất 1 chữ cái")
        
        # Create user
        success = auth_manager.register_user(username, password, role, full_name, email)
        
        if not success:
            raise HTTPException(status_code=400, detail="Username hoặc email đã tồn tại")
        
        return {"success": True, "message": "Tạo người dùng thành công"}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database error")

@app.put("/api/admin/users/{user_id}")
async def update_user(
    user_id: int,
    username: str = Form(...),
    email: str = Form(...),
    full_name: str = Form(...),
    role: str = Form(...),
    is_active: bool = Form(True),
    user: dict = Depends(get_current_user)
):
    """API cập nhật thông tin người dùng (chỉ admin)"""
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Validate role
        if role not in ["admin", "teacher", "student"]:
            raise HTTPException(status_code=400, detail="Invalid role")
        
        conn = sqlite3.connect("cs466_database.db")
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update user
        cursor.execute('''
            UPDATE users 
            SET username = ?, email = ?, full_name = ?, role = ?
            WHERE id = ?
        ''', (username, email, full_name, role, user_id))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Cập nhật người dùng thành công"}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database error")

@app.delete("/api/admin/users/{user_id}")
async def delete_user(user_id: int, user: dict = Depends(get_current_user)):
    """API xóa người dùng (chỉ admin)"""
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Prevent self-deletion
        if int(user["user_id"]) == user_id:
            raise HTTPException(status_code=400, detail="Không thể xóa chính mình")
        
        conn = sqlite3.connect("cs466_database.db")
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=404, detail="User not found")
        
        # Delete user (should also handle cascading deletes in production)
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Xóa người dùng thành công"}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database error")

@app.post("/api/admin/users/{user_id}/reset-password")
async def reset_user_password(user_id: int, user: dict = Depends(get_current_user)):
    """API reset mật khẩu người dùng (chỉ admin) - Gửi email với link reset"""
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        conn = sqlite3.connect("cs466_database.db")
        cursor = conn.cursor()
        
        # Check if user exists and get email
        cursor.execute("SELECT email, full_name FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        if not result:
            conn.close()
            raise HTTPException(status_code=404, detail="User not found")
        
        user_email, user_name = result
        
        # Generate reset token
        import secrets
        import uuid
        reset_token = str(uuid.uuid4()) + secrets.token_urlsafe(32)
        
        # Create password_reset_tokens table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token TEXT UNIQUE NOT NULL,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Insert reset token (expires in 10 minutes)
        from datetime import datetime, timedelta
        expires_at = (datetime.now() + timedelta(minutes=10)).isoformat()
        
        cursor.execute('''
            INSERT INTO password_reset_tokens (token, user_id, expires_at)
            VALUES (?, ?, ?)
        ''', (reset_token, user_id, expires_at))
        
        conn.commit()
        conn.close()
        
        # Send reset email
        success = send_reset_password_email(user_email, user_name, reset_token)
        
        if success:
            return {
                "success": True,
                "message": "Email reset mật khẩu đã được gửi"
            }
        else:
            # If email fails, remove token from database
            conn = sqlite3.connect("cs466_database.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM password_reset_tokens WHERE token = ?", (reset_token,))
            conn.commit()
            conn.close()
            
            raise HTTPException(status_code=500, detail="Không thể gửi email")
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database error")

# Add CORS middleware
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================================
# PROFILE ENDPOINTS
# ================================

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """Trang hồ sơ cá nhân"""
    # Check authentication in JavaScript, not server-side
    return templates.TemplateResponse("profile.html", {"request": request})

@app.get("/logout")
async def logout():
    """Đăng xuất - Clear client-side token và redirect về trang login"""
    response = RedirectResponse(url="/", status_code=302)
    # Có thể thêm logic clear server-side session nếu cần
    return response

@app.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(request: Request, token: str):
    """Trang reset mật khẩu"""
    # Validate token
    conn = sqlite3.connect("cs466_database.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT rt.user_id, rt.expires_at, u.email, u.full_name
        FROM password_reset_tokens rt
        JOIN users u ON rt.user_id = u.id
        WHERE rt.token = ?
    ''', (token,))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return templates.TemplateResponse("reset_password.html", {
            "request": request, 
            "error": "Token không hợp lệ"
        })
    
    user_id, expires_at, email, full_name = result
    
    # Check if token expired
    from datetime import datetime
    expires_time = datetime.fromisoformat(expires_at)
    
    if datetime.now() > expires_time:
        return templates.TemplateResponse("reset_password.html", {
            "request": request, 
            "error": "Token đã hết hạn"
        })
    
    return templates.TemplateResponse("reset_password.html", {
        "request": request,
        "token": token,
        "email": email,
        "full_name": full_name
    })

@app.post("/reset-password")
async def reset_password_submit(
    token: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...)
):
    """Xử lý reset mật khẩu"""
    try:
        # Validate passwords match
        if new_password != confirm_password:
            raise HTTPException(status_code=400, detail="Mật khẩu xác nhận không khớp")
        
        # Validate password requirements
        if len(new_password) < 6:
            raise HTTPException(status_code=400, detail="Mật khẩu phải có ít nhất 6 ký tự")
        
        if not any(c.isupper() for c in new_password):
            raise HTTPException(status_code=400, detail="Mật khẩu phải có ít nhất 1 chữ in hoa")
        
        if not any(c.isdigit() for c in new_password):
            raise HTTPException(status_code=400, detail="Mật khẩu phải có ít nhất 1 chữ số")
        
        if not any(c.isalpha() for c in new_password):
            raise HTTPException(status_code=400, detail="Mật khẩu phải có ít nhất 1 chữ cái")
        
        # Check for special characters (not allowed)
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if any(c in special_chars for c in new_password):
            raise HTTPException(status_code=400, detail="Mật khẩu không được chứa ký tự đặc biệt")
        
        # Validate token
        conn = sqlite3.connect("cs466_database.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id, expires_at
            FROM password_reset_tokens
            WHERE token = ?
        ''', (token,))
        
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            raise HTTPException(status_code=400, detail="Token không hợp lệ")
        
        user_id, expires_at = result
        
        # Check if token expired
        from datetime import datetime
        expires_time = datetime.fromisoformat(expires_at)
        
        if datetime.now() > expires_time:
            conn.close()
            raise HTTPException(status_code=400, detail="Token đã hết hạn")
        
        # Update password
        new_password_hash = auth_manager.get_password_hash(new_password)
        cursor.execute('''
            UPDATE users 
            SET password_hash = ?
            WHERE id = ?
        ''', (new_password_hash, user_id))
        
        # Delete token (used)
        cursor.execute("DELETE FROM password_reset_tokens WHERE token = ?", (token,))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Đổi mật khẩu thành công"}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Lỗi hệ thống")

@app.get("/api/profile")
async def get_profile(user: dict = Depends(get_current_user)):
    """API lấy thông tin hồ sơ cá nhân"""
    try:
        conn = sqlite3.connect("cs466_database.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email, full_name, role, created_at
            FROM users WHERE id = ?
        ''', (user["user_id"],))
        
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data:
            return {
                "success": True,
                "profile": {
                    "id": user_data[0],
                    "username": user_data[1],
                    "email": user_data[2],
                    "full_name": user_data[3],
                    "role": user_data[4],
                    "created_at": user_data[5],
                    "birth_date": None,  # Sẽ implement sau
                    "gender": None,      # Sẽ implement sau
                    "is_2fa_enabled": auth_manager.is_2fa_enabled(int(user["user_id"]))
                }
            }
        else:
            raise HTTPException(status_code=404, detail="User not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database error")

@app.post("/api/profile/update")
async def update_profile(
    full_name: str = Form(...),
    birth_date: Optional[str] = Form(None),
    gender: Optional[str] = Form(None),
    user: dict = Depends(get_current_user)
):
    """API cập nhật thông tin hồ sơ cá nhân"""
    try:
        conn = sqlite3.connect("cs466_database.db")
        cursor = conn.cursor()
        
        # Cập nhật thông tin cơ bản
        cursor.execute('''
            UPDATE users 
            SET full_name = ?
            WHERE id = ?
        ''', (full_name, user["user_id"]))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": "Cập nhật hồ sơ thành công!",
            "updated_fields": {
                "full_name": full_name,
                "birth_date": birth_date,
                "gender": gender
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database error")

@app.post("/api/profile/toggle-2fa")
async def toggle_2fa(user: dict = Depends(get_current_user)):
    """API toggle trạng thái 2FA"""
    try:
        user_id = int(user["user_id"])
        
        # Lấy trạng thái hiện tại
        current_status = auth_manager.is_2fa_enabled(user_id)
        
        # Đảo ngược trạng thái
        new_status = not current_status
        auth_manager.set_2fa_status(user_id, new_status)
        
        return {
            "success": True,
            "is_2fa_enabled": new_status,
            "message": f"2FA đã được {'bật' if new_status else 'tắt'}"
        }
        
    except Exception as e:
        return {"success": False, "message": "Lỗi hệ thống"}

@app.post("/api/profile/send-otp-password")
async def send_otp_for_password_change(user: dict = Depends(get_current_user)):
    """Gửi OTP để đổi mật khẩu (luôn bắt buộc 2FA)"""
    try:
        # Lấy email của user
        conn = sqlite3.connect("cs466_database.db")
        cursor = conn.cursor()
        cursor.execute('SELECT email FROM users WHERE id = ?', (user["user_id"],))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_email = result[0]
        
        # Gửi OTP qua email (luôn gửi cho đổi mật khẩu, bất kể 2FA setting)
        success, message = auth_manager.send_otp_to_email(user_email)
        
        return {
            "success": success,
            "message": message if success else "Có lỗi xảy ra khi gửi OTP"
        }
        
    except Exception as e:
        return {"success": False, "message": "Lỗi hệ thống"}

@app.post("/api/profile/change-password") 
async def change_password(
    current_password: str = Form(...),
    new_password: str = Form(...),
    otp: str = Form(...),
    user: dict = Depends(get_current_user)
):
    """API đổi mật khẩu với OTP verification"""
    try:
        # Validate mật khẩu mới
        if len(new_password) < 6:
            return {"success": False, "message": "Mật khẩu mới phải có ít nhất 6 ký tự"}
        
        if not any(c.isupper() for c in new_password):
            return {"success": False, "message": "Mật khẩu mới phải có ít nhất 1 chữ in hoa"}
        
        if not any(c.isdigit() for c in new_password):
            return {"success": False, "message": "Mật khẩu mới phải có ít nhất 1 chữ số"}
        
        if not any(c.isalpha() for c in new_password):
            return {"success": False, "message": "Mật khẩu mới phải có ít nhất 1 chữ cái"}
        
        # Kiểm tra ký tự đặc biệt (không được có)
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if any(c in special_chars for c in new_password):
            return {"success": False, "message": "Mật khẩu mới không được chứa ký tự đặc biệt"}
        
        # Lấy thông tin user hiện tại
        conn = sqlite3.connect("cs466_database.db")
        cursor = conn.cursor()
        cursor.execute('SELECT email, password_hash FROM users WHERE id = ?', (user["user_id"],))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return {"success": False, "message": "Không tìm thấy người dùng"}
        
        user_email, current_password_hash = result
        
        # Xác thực mật khẩu hiện tại
        if not auth_manager.verify_password(current_password, current_password_hash):
            conn.close()
            return {"success": False, "message": "Mật khẩu hiện tại không đúng"}
        
        # Xác thực OTP
        if not auth_manager.verify_otp(user_email, otp):
            conn.close()
            return {"success": False, "message": "Mã OTP không đúng hoặc đã hết hạn"}
        
        # Cập nhật mật khẩu mới
        new_password_hash = auth_manager.get_password_hash(new_password)
        cursor.execute('''
            UPDATE users 
            SET password_hash = ?
            WHERE id = ?
        ''', (new_password_hash, user["user_id"]))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": "Đổi mật khẩu thành công!"
        }
        
    except Exception as e:
        return {"success": False, "message": "Lỗi hệ thống"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000) 