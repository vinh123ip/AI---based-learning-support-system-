# -*- coding: utf-8 -*-
"""
Interactive Python Demo
Tương tự như online-python.com - hỗ trợ input() function
"""

def demo_basic_input():
    """Demo cơ bản với input()"""
    print("=== DEMO BASIC INPUT ===")
    name = input("Nhập tên của bạn: ")
    age = int(input("Nhập tuổi của bạn: "))
    
    print(f"Xin chào {name}!")
    print(f"Bạn {age} tuổi.")
    
    if age >= 18:
        print("Bạn đã trưởng thành!")
    else:
        print("Bạn vẫn còn trẻ!")

def demo_calculator():
    """Demo máy tính đơn giản"""
    print("\n=== DEMO CALCULATOR ===")
    
    while True:
        print("\nChọn phép tính:")
        print("1. Cộng (+)")
        print("2. Trừ (-)")
        print("3. Nhân (*)")
        print("4. Chia (/)")
        print("5. Thoát")
        
        choice = input("Lựa chọn của bạn (1-5): ")
        
        if choice == '5':
            print("Tạm biệt!")
            break
        
        if choice in ['1', '2', '3', '4']:
            try:
                num1 = float(input("Nhập số thứ nhất: "))
                num2 = float(input("Nhập số thứ hai: "))
                
                if choice == '1':
                    result = num1 + num2
                    print(f"{num1} + {num2} = {result}")
                elif choice == '2':
                    result = num1 - num2
                    print(f"{num1} - {num2} = {result}")
                elif choice == '3':
                    result = num1 * num2
                    print(f"{num1} * {num2} = {result}")
                elif choice == '4':
                    if num2 != 0:
                        result = num1 / num2
                        print(f"{num1} / {num2} = {result}")
                    else:
                        print("Lỗi: Không thể chia cho 0!")
                        
            except ValueError:
                print("Lỗi: Vui lòng nhập số hợp lệ!")
        else:
            print("Lựa chọn không hợp lệ!")

def demo_guessing_game():
    """Demo game đoán số"""
    print("\n=== DEMO GUESSING GAME ===")
    import random
    
    secret_number = random.randint(1, 100)
    attempts = 0
    max_attempts = 7
    
    print(f"Tôi đã nghĩ ra một số từ 1 đến 100!")
    print(f"Bạn có {max_attempts} lần đoán.")
    
    while attempts < max_attempts:
        try:
            guess = int(input(f"Lần đoán {attempts + 1}: "))
            attempts += 1
            
            if guess == secret_number:
                print(f"🎉 Chúc mừng! Bạn đã đoán đúng số {secret_number}!")
                print(f"Bạn đã thắng trong {attempts} lần đoán!")
                break
            elif guess < secret_number:
                print("Số bạn đoán nhỏ hơn!")
            else:
                print("Số bạn đoán lớn hơn!")
                
            if attempts < max_attempts:
                print(f"Còn {max_attempts - attempts} lần đoán.")
            
        except ValueError:
            print("Vui lòng nhập một số nguyên!")
            attempts -= 1  # Không tính lần đoán này
    
    if attempts >= max_attempts:
        print(f"😢 Bạn đã hết lượt đoán! Số bí mật là {secret_number}")

def demo_interactive_list():
    """Demo tương tác với danh sách"""
    print("\n=== DEMO INTERACTIVE LIST ===")
    
    my_list = []
    
    while True:
        print("\nDanh sách hiện tại:", my_list)
        print("\nChọn hành động:")
        print("1. Thêm phần tử")
        print("2. Xóa phần tử")
        print("3. Hiển thị danh sách")
        print("4. Tìm kiếm")
        print("5. Thoát")
        
        choice = input("Lựa chọn của bạn: ")
        
        if choice == '1':
            item = input("Nhập phần tử muốn thêm: ")
            my_list.append(item)
            print(f"Đã thêm '{item}' vào danh sách!")
            
        elif choice == '2':
            if my_list:
                print("Danh sách:", my_list)
                try:
                    index = int(input("Nhập vị trí muốn xóa (bắt đầu từ 0): "))
                    if 0 <= index < len(my_list):
                        removed = my_list.pop(index)
                        print(f"Đã xóa '{removed}' khỏi danh sách!")
                    else:
                        print("Vị trí không hợp lệ!")
                except ValueError:
                    print("Vui lòng nhập số nguyên!")
            else:
                print("Danh sách trống!")
                
        elif choice == '3':
            if my_list:
                print("Danh sách của bạn:")
                for i, item in enumerate(my_list):
                    print(f"{i}: {item}")
            else:
                print("Danh sách trống!")
                
        elif choice == '4':
            if my_list:
                search_term = input("Nhập từ khóa tìm kiếm: ")
                found_items = [item for item in my_list if search_term.lower() in item.lower()]
                if found_items:
                    print(f"Tìm thấy {len(found_items)} kết quả:")
                    for item in found_items:
                        print(f"- {item}")
                else:
                    print("Không tìm thấy kết quả nào!")
            else:
                print("Danh sách trống!")
                
        elif choice == '5':
            print("Tạm biệt!")
            break
            
        else:
            print("Lựa chọn không hợp lệ!")

def main():
    """Chương trình chính"""
    print("🐍 INTERACTIVE PYTHON DEMO")
    print("Tương tự như online-python.com")
    print("=" * 50)
    
    while True:
        print("\nChọn demo:")
        print("1. Demo Basic Input")
        print("2. Demo Calculator")
        print("3. Demo Guessing Game")
        print("4. Demo Interactive List")
        print("5. Thoát")
        
        choice = input("\nLựa chọn của bạn: ")
        
        if choice == '1':
            demo_basic_input()
        elif choice == '2':
            demo_calculator()
        elif choice == '3':
            demo_guessing_game()
        elif choice == '4':
            demo_interactive_list()
        elif choice == '5':
            print("Cảm ơn bạn đã sử dụng demo!")
            break
        else:
            print("Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    main() 