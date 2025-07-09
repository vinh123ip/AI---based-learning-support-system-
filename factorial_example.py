# Tính giai thừa - Code mẫu cho web environment
# Lưu ý: Không sử dụng input() trong web environment

def fact(x):
    """Tính giai thừa của số x"""
    if x == 0 or x == 1:
        return 1
    return x * fact(x - 1)

# Test với các giá trị mẫu
test_numbers = [0, 1, 3, 5, 8, 10]

print("=== BẢNG TÍNH GIAI THỪA ===")
print("Số  | Giai thừa")
print("-" * 20)

for num in test_numbers:
    result = fact(num)
    print(f"{num:2d}  | {result}")

print("\n=== GIẢI THÍCH ===")
print("Giai thừa (factorial) của n là tích của tất cả số nguyên dương từ 1 đến n")
print("Ký hiệu: n! = n × (n-1) × (n-2) × ... × 2 × 1")
print("Quy ước: 0! = 1")

# Phiên bản iterative (không đệ quy)
def fact_iterative(x):
    """Tính giai thừa bằng vòng lặp"""
    if x == 0 or x == 1:
        return 1
    result = 1
    for i in range(2, x + 1):
        result *= i
    return result

print("\n=== SO SÁNH RECURSIVE VS ITERATIVE ===")
for num in [5, 7, 10]:
    recursive_result = fact(num)
    iterative_result = fact_iterative(num)
    print(f"{num}! = {recursive_result} (recursive) = {iterative_result} (iterative)")

# Xử lý số lớn
print("\n=== TÍNH GIAI THỪA SỐ LỚN ===")
large_numbers = [15, 20, 25]
for num in large_numbers:
    result = fact(num)
    print(f"{num}! = {result:,}")  # Format với dấu phẩy

print("\n✅ Code chạy thành công với encoding UTF-8!")
print("💡 Lưu ý: Trong web environment, sử dụng giá trị cố định thay vì input()") 