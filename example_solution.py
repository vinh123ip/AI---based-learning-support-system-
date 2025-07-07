# Example Solution - Sửa lỗi IndentationError
# Bài toán: Tìm các số trong khoảng 2000-3000 chia hết cho 7 nhưng không chia hết cho 5

# ❌ CODE SAI (như trong hình):
# j = 0                           # Lỗi: j phải là list, không phải int
# for i in range(2000, 3000):
# if (i%7==0) and (i%5!=0):      # Lỗi: thiếu indent sau for
#     j.append(str(i))           # Lỗi: j.append() không work với int
# print(','.join(j))

# ✅ CODE ĐÚNG:
j = []  # Khởi tạo list rỗng, không phải số 0
for i in range(2000, 3000):
    if (i%7==0) and (i%5!=0):  # Indent đúng: 4 spaces sau for
        j.append(str(i))       # Indent đúng: 8 spaces trong if
print(','.join(j))

print("\n" + "="*50)
print("GIẢI THÍCH CHI TIẾT:")
print("="*50)

# Giải thích từng bước:
print("1. Khởi tạo list rỗng:")
j = []
print(f"   j = {j} (type: {type(j).__name__})")

print("\n2. Duyệt qua từng số từ 2000 đến 2999:")
count = 0
for i in range(2000, 3000):
    if (i%7==0) and (i%5!=0):
        j.append(str(i))
        count += 1
        if count <= 5:  # Chỉ hiển thị 5 số đầu
            print(f"   Số {i}: {i}%7={i%7}, {i}%5={i%5} → Thêm vào list")

print(f"\n3. Tổng cộng tìm được {len(j)} số thỏa mãn điều kiện")
print(f"4. Kết quả cuối cùng: {','.join(j[:10])}..." if len(j) > 10 else f"4. Kết quả cuối cùng: {','.join(j)}")

print("\n" + "="*50)
print("CÁC LỖI THƯỜNG GẶP:")
print("="*50)

print("❌ IndentationError:")
print("   - Python yêu cầu indent chính xác")
print("   - Sau for/if/while/def: phải có indent")
print("   - Sử dụng 4 spaces hoặc 1 tab (không trộn lẫn)")

print("\n❌ TypeError với list:")
print("   - j = 0 → j.append() sẽ lỗi")
print("   - j = [] → j.append() sẽ work")

print("\n✅ Cách sửa:")
print("   1. Khởi tạo j = [] thay vì j = 0")
print("   2. Indent đúng: 4 spaces sau for")
print("   3. Indent đúng: 8 spaces trong if")
print("   4. Kiểm tra syntax trước khi chạy") 