# 📋 Hướng dẫn sử dụng Admin Dashboard

## 🔐 Tài khoản Admin mặc định

Hệ thống đã tạo sẵn tài khoản admin với thông tin:
- **Email (Login):** `admin@dtu.edu.vn`
- **Password:** `Admin123`

**Lưu ý:** Đăng nhập bằng email, không phải username!

## 🚀 Cách truy cập Admin Dashboard

1. Truy cập trang chủ: `http://localhost:8000`
2. Đăng nhập bằng tài khoản admin
3. Hệ thống sẽ tự động chuyển hướng đến `/dashboard/admin`

## 🎛️ Các tính năng của Admin Dashboard

### 📊 Dashboard Tổng quan
- **Thống kê người dùng:** Hiển thị số lượng admin, giáo viên, sinh viên
- **Thao tác nhanh:** Tạo tài khoản, tìm kiếm, xuất dữ liệu

### 👥 Quản lý người dùng

#### 🔍 Tìm kiếm và lọc
- **Tìm kiếm theo:** ID, tên đăng nhập, email, họ tên
- **Lọc theo vai trò:** Admin, Giáo viên, Sinh viên
- **Lọc theo trạng thái:** Hoạt động, Tạm khóa

#### ➕ Tạo tài khoản mới
1. Click nút "Thêm người dùng" hoặc "Tạo mới" từ dashboard
2. Điền thông tin:
   - **Tên đăng nhập** (bắt buộc)
   - **Email** (bắt buộc, phải unique)
   - **Họ và tên** (bắt buộc)
   - **Vai trò** (Admin/Giáo viên/Sinh viên)
   - **Mật khẩu** (bắt buộc khi tạo mới)
   - **Trạng thái tài khoản**
   - **Bật 2FA** (tùy chọn)

#### ✏️ Chỉnh sửa thông tin
1. Click nút "Chỉnh sửa" (icon bút) trong danh sách người dùng
2. Cập nhật thông tin cần thiết
3. Click "Cập nhật" để lưu

#### 🔄 Thay đổi vai trò
- Admin có thể thay đổi vai trò của bất kỳ user nào
- Hỗ trợ chuyển đổi giữa: Admin ↔ Giáo viên ↔ Sinh viên

#### 🔑 Reset mật khẩu
1. Click nút "Reset mật khẩu" (icon chìa khóa)
2. Xác nhận thao tác
3. Hệ thống sẽ tạo mật khẩu mới tự động
4. Mật khẩu mới sẽ hiển thị trong thông báo

#### 🗑️ Xóa tài khoản
1. Click nút "Xóa" (icon thùng rác)
2. Xác nhận thao tác (có popup xác nhận)
3. **Lưu ý:** Không thể xóa chính mình

### 📄 Phân trang
- Hiển thị 10 user/trang
- Điều hướng dễ dàng với pagination
- Hiển thị tổng số kết quả

## 🔒 Yêu cầu mật khẩu

Khi tạo tài khoản mới, mật khẩu phải đáp ứng:
- ✅ Ít nhất 6 ký tự
- ✅ Ít nhất 1 chữ cái viết hoa
- ✅ Ít nhất 1 chữ số
- ✅ Ít nhất 1 chữ cái
- ❌ Không chứa ký tự đặc biệt

## 🛡️ Bảo mật

### Phân quyền
- Chỉ user có role `admin` mới truy cập được Admin Dashboard
- JWT token authentication cho tất cả API calls
- Tự động redirect về login nếu không có quyền

### Validation
- Email phải unique trong hệ thống
- Username phải unique
- Các trường bắt buộc được validate

## 🎨 Giao diện

### Layout
- **Sidebar menu:** Điều hướng chính
- **Responsive design:** Tương thích mobile/tablet
- **Modern UI:** Bootstrap 5 + custom CSS
- **Icons:** Font Awesome 6

### Thông báo
- **Success alerts:** Màu xanh cho thao tác thành công
- **Error alerts:** Màu đỏ cho lỗi
- **Warning alerts:** Màu vàng cho cảnh báo
- **Auto-dismiss:** Tự động ẩn sau 5 giây

## 🔧 Các tính năng bổ sung

### Popup xác nhận
- Xóa user: Yêu cầu xác nhận
- Thay đổi role: Popup xác nhận
- Reset password: Xác nhận trước khi thực hiện

### Keyboard shortcuts
- **Enter:** Submit form
- **Esc:** Đóng modal

## 🔄 Tương lai phát triển

Giao diện đã chuẩn bị sẵn để mở rộng:
- 📝 Quản lý bài tập (tab "Quản lý bài tập")
- ⚙️ Cài đặt hệ thống (tab "Cài đặt hệ thống")
- 📊 Analytics chi tiết
- 📧 Email notifications
- 📋 Audit logs

## ⚠️ Lưu ý quan trọng

1. **Không xóa tài khoản admin cuối cùng** - Có thể khóa khỏi hệ thống
2. **Backup database** trước khi thao tác lớn
3. **Test thận trọng** trước khi deploy production
4. **Theo dõi logs** để phát hiện bất thường

## 🐛 Troubleshooting

### Không thể đăng nhập admin
- Kiểm tra username/password chính xác
- Đảm bảo database đã được khởi tạo
- Kiểm tra logs server

### Không load được danh sách user
- Kiểm tra JWT token còn hạn
- Verify API endpoints hoạt động
- Kiểm tra quyền admin

### Lỗi khi tạo user
- Kiểm tra email/username đã tồn tại
- Validate password requirements
- Kiểm tra kết nối database

---

**💡 Tip:** Sử dụng Developer Tools (F12) để debug các lỗi JavaScript và network requests! 