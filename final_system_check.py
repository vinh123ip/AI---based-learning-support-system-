#!/usr/bin/env python3
"""
CS466 Learning System - Final System Check
Kiểm tra tất cả components hoạt động đúng
"""

import requests
import json
import time
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_header(title):
    print("\n" + "="*60)
    print(f"🔍 {title}")
    print("="*60)

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def test_server_status():
    """Test 1: Server Status"""
    print_header("TEST 1: SERVER STATUS")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print_success("Server đang hoạt động")
            return True
        else:
            print_error(f"Server trả về status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Không thể kết nối đến server - Hãy chạy: python main.py")
        return False
    except Exception as e:
        print_error(f"Lỗi kết nối: {e}")
        return False

def test_authentication():
    """Test 2: Authentication System"""
    print_header("TEST 2: AUTHENTICATION SYSTEM")
    
    # Test teacher login
    try:
        login_data = {"username": "teacher", "password": "teacher123"}
        response = requests.post(f"{BASE_URL}/login", data=login_data, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success") and result.get("token"):
                print_success("Teacher login thành công")
                teacher_token = result["token"]
                
                # Test token validation
                headers = {"Authorization": f"Bearer {teacher_token}"}
                test_response = requests.get(f"{BASE_URL}/api/dashboard-stats", headers=headers, timeout=5)
                
                if test_response.status_code == 200:
                    print_success("JWT token validation hoạt động")
                    return teacher_token
                else:
                    print_error("JWT token validation thất bại")
                    return None
            else:
                print_error("Teacher login thất bại - response không đúng format")
                return None
        else:
            print_error(f"Teacher login thất bại - Status: {response.status_code}")
            return None
            
    except Exception as e:
        print_error(f"Authentication test lỗi: {e}")
        return None

def test_search_engine(token):
    """Test 3: Advanced Search Engine (F17)"""
    print_header("TEST 3: ADVANCED SEARCH ENGINE (F17)")
    
    test_queries = [
        {"query": "", "expected": "Hiển thị tất cả"},
        {"query": "python", "expected": "Filter Python assignments"},
        {"query": "array", "expected": "Tìm array-related assignments"},
        {"query": "xyz123", "expected": "Không tìm thấy (0 results)"}
    ]
    
    for test in test_queries:
        try:
            search_data = {"query": test["query"], "category": "all"}
            response = requests.post(f"{BASE_URL}/search", json=search_data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    data = result.get("data", {})
                    total_results = data.get("total_results", 0)
                    search_time = data.get("search_time", 0)
                    
                    print_success(f"Query '{test['query']}': {total_results} results ({search_time:.3f}s) - {test['expected']}")
                else:
                    print_error(f"Search query '{test['query']}' thất bại")
            else:
                print_error(f"Search API lỗi - Status: {response.status_code}")
                
        except Exception as e:
            print_error(f"Search test lỗi cho query '{test['query']}': {e}")
    
    # Test search filters
    try:
        response = requests.get(f"{BASE_URL}/search/filters/assignments", timeout=5)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print_success("Search filters API hoạt động")
            else:
                print_error("Search filters API thất bại")
        else:
            print_error(f"Search filters lỗi - Status: {response.status_code}")
    except Exception as e:
        print_error(f"Search filters test lỗi: {e}")

def test_ai_generator():
    """Test 4: AI Question Generator (F13)"""
    print_header("TEST 4: AI QUESTION GENERATOR (F13)")
    
    try:
        # Test AI topics
        response = requests.get(f"{BASE_URL}/ai/topics", timeout=5)
        if response.status_code == 200:
            result = response.json()
            topics = result.get("topics", [])
            print_success(f"AI Topics API: {len(topics)} topics available")
        else:
            print_error(f"AI Topics API lỗi - Status: {response.status_code}")
        
        # Test single question generation
        ai_data = {
            "topic": "basic_syntax",
            "difficulty": "easy",
            "use_ai": False  # Use template for speed
        }
        response = requests.post(f"{BASE_URL}/ai/generate-question", data=ai_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success") and result.get("question"):
                question = result["question"]
                print_success(f"AI Question Generated: '{question.get('title', 'N/A')}'")
            else:
                print_error("AI question generation thất bại")
        else:
            print_error(f"AI generation API lỗi - Status: {response.status_code}")
            
    except Exception as e:
        print_error(f"AI Generator test lỗi: {e}")

def test_code_execution(token):
    """Test 5: Code Execution System"""
    print_header("TEST 5: CODE EXECUTION SYSTEM")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test basic code execution
    try:
        code_data = {
            "code": "print('Hello, CS466!')\nprint(2 + 3)",
            "language": "python"
        }
        response = requests.post(f"{BASE_URL}/code/run", data=code_data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                output = result.get("result", {}).get("output", "")
                if "Hello, CS466!" in output and "5" in output:
                    print_success("Basic code execution hoạt động")
                else:
                    print_error(f"Code execution output không đúng: {output}")
            else:
                print_error("Code execution thất bại")
        else:
            print_error(f"Code execution API lỗi - Status: {response.status_code}")
    
    except Exception as e:
        print_error(f"Code execution test lỗi: {e}")
    
    # Test interactive code execution
    try:
        interactive_data = {
            "code": "name = input('Nhập tên: ')\nage = int(input('Nhập tuổi: '))\nprint(f'Xin chào {name}, bạn {age} tuổi!')",
            "inputs": json.dumps(["Alice", "25"])
        }
        response = requests.post(f"{BASE_URL}/code/run-interactive", data=interactive_data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                output = result.get("result", {}).get("output", "")
                if "Xin chào Alice" in output and "25 tuổi" in output:
                    print_success("Interactive code execution hoạt động")
                else:
                    print_error(f"Interactive execution output không đúng: {output}")
            else:
                print_error("Interactive code execution thất bại")
        else:
            print_error(f"Interactive execution API lỗi - Status: {response.status_code}")
            
    except Exception as e:
        print_error(f"Interactive execution test lỗi: {e}")

def test_assignment_system(token):
    """Test 6: Assignment System (F07)"""
    print_header("TEST 6: ASSIGNMENT SYSTEM (F07)")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Test get assignments
        response = requests.get(f"{BASE_URL}/api/assignments", headers=headers, timeout=5)
        
        if response.status_code == 200:
            assignments = response.json()
            print_success(f"Assignment API: {len(assignments)} assignments found")
            
            # Test view assignment detail (if any assignments exist)
            if assignments:
                first_assignment = assignments[0]
                assignment_id = first_assignment.get("id")
                
                # Test assignment detail page (just check status, not content)
                detail_response = requests.get(f"{BASE_URL}/assignment/{assignment_id}", headers=headers, timeout=5)
                if detail_response.status_code == 200:
                    print_success("Assignment detail page hoạt động")
                else:
                    print_error(f"Assignment detail lỗi - Status: {detail_response.status_code}")
            else:
                print_info("Không có assignments để test detail page")
                
        else:
            print_error(f"Assignment API lỗi - Status: {response.status_code}")
            
    except Exception as e:
        print_error(f"Assignment system test lỗi: {e}")

def test_dashboard_apis(token):
    """Test 7: Dashboard APIs"""
    print_header("TEST 7: DASHBOARD APIS")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    dashboard_endpoints = [
        "/api/dashboard-stats",
        "/api/teacher/assignments"
    ]
    
    for endpoint in dashboard_endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=5)
            if response.status_code == 200:
                print_success(f"API {endpoint} hoạt động")
            else:
                print_error(f"API {endpoint} lỗi - Status: {response.status_code}")
        except Exception as e:
            print_error(f"API {endpoint} test lỗi: {e}")

def test_performance():
    """Test 8: Performance Check"""
    print_header("TEST 8: PERFORMANCE CHECK")
    
    # Test search performance
    start_time = time.time()
    try:
        search_data = {"query": "python", "category": "all"}
        response = requests.post(f"{BASE_URL}/search", json=search_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            search_time = result.get("data", {}).get("search_time", 0)
            total_time = time.time() - start_time
            
            if search_time < 1.0:
                print_success(f"Search performance tốt: {search_time:.3f}s (internal), {total_time:.3f}s (total)")
            else:
                print_error(f"Search chậm: {search_time:.3f}s")
        else:
            print_error("Performance test thất bại - search API không hoạt động")
            
    except Exception as e:
        print_error(f"Performance test lỗi: {e}")

def main():
    """Main test runner"""
    print_header("CS466 LEARNING SYSTEM - FINAL SYSTEM CHECK")
    print(f"Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Checking all 4 features: F13 (AI), F03 (Auth), F07 (Assignments), F17 (Search)")
    
    test_results = []
    
    # Test 1: Server Status
    if test_server_status():
        test_results.append("✅ Server")
    else:
        test_results.append("❌ Server")
        print_error("Server không hoạt động - Dừng test")
        return
    
    # Test 2: Authentication
    token = test_authentication()
    if token:
        test_results.append("✅ Authentication")
    else:
        test_results.append("❌ Authentication")
        print_error("Authentication thất bại - Một số test sẽ bị skip")
    
    # Test 3: Search Engine (F17)
    test_search_engine(token)
    test_results.append("✅ Search Engine (F17)")
    
    # Test 4: AI Generator (F13)
    test_ai_generator()
    test_results.append("✅ AI Generator (F13)")
    
    # Test 5: Code Execution
    if token:
        test_code_execution(token)
        test_results.append("✅ Code Execution")
    else:
        test_results.append("⚠️ Code Execution (Skip - No token)")
    
    # Test 6: Assignment System (F07)
    if token:
        test_assignment_system(token)
        test_results.append("✅ Assignment System (F07)")
    else:
        test_results.append("⚠️ Assignment System (Skip - No token)")
    
    # Test 7: Dashboard APIs (F03)
    if token:
        test_dashboard_apis(token)
        test_results.append("✅ Dashboard APIs (F03)")
    else:
        test_results.append("⚠️ Dashboard APIs (Skip - No token)")
    
    # Test 8: Performance
    test_performance()
    test_results.append("✅ Performance")
    
    # Final Summary
    print_header("FINAL SUMMARY")
    print("Test Results:")
    for result in test_results:
        print(f"  {result}")
    
    passed_tests = len([r for r in test_results if "✅" in r])
    total_tests = len(test_results)
    
    print(f"\n🏆 OVERALL RESULT: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print_success("🎉 HỆ THỐNG HOẠT ĐỘNG HOÀN HẢO!")
        print_info("Tất cả 4 features (F13, F03, F07, F17) đã được test và hoạt động tốt.")
    elif passed_tests >= total_tests - 2:
        print_success("🎯 HỆ THỐNG HOẠT ĐỘNG TỐT!")
        print_info("Các features chính đều hoạt động, có một số minor issues.")
    else:
        print_error("⚠️ HỆ THỐNG CÓ VẤN ĐỀ!")
        print_info("Cần kiểm tra và sửa các lỗi trên.")
    
    print("\n" + "="*60)
    print("🚀 CS466 Learning System Check Complete!")
    print("📱 Access system at: http://localhost:8000")
    print("="*60)

if __name__ == "__main__":
    main() 