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

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Trang chủ - Đăng nhập"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    """Xử lý đăng nhập"""
    user = auth_manager.authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_manager.create_access_token(
        data={"sub": str(user["id"]), "role": user["role"]},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer", "role": user["role"]}

@app.get("/dashboard/{role}", response_class=HTMLResponse)
async def dashboard(request: Request, role: str):
    """Dashboard cho GV hoặc SV"""
    if role not in ["teacher", "student"]:
        raise HTTPException(status_code=404, detail="Not found")
    
    # Check if user has valid token in JavaScript
    if role == "teacher":
        return templates.TemplateResponse("teacher_dashboard.html", {"request": request})
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

# Add CORS middleware
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 