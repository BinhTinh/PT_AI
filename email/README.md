# Gmail Agent (DeepSeek)

Agent chạy trên máy cá nhân, quản lý nhiều tài khoản Gmail (liệt kê, đọc, tìm kiếm,
tóm tắt, soạn/gửi email) thông qua vòng lặp tool-calling thật với DeepSeek API.
Không cần OAuth Google — chỉ dùng IMAP/SMTP + App Password.

## 1. Chuẩn bị mỗi tài khoản Gmail

Với **từng** tài khoản Gmail muốn agent truy cập:

1. Bật **2-Step Verification**: https://myaccount.google.com/security
2. Tạo **App Password**: https://myaccount.google.com/apppasswords
   - Chọn app "Mail", thiết bị "Other" → đặt tên tùy ý (vd "gmail-agent")
   - Google sẽ cho ra 1 chuỗi 16 ký tự dạng `abcd efgh ijkl mnop` — copy lại
3. Đảm bảo IMAP đang bật: Gmail → Settings → "Forwarding and POP/IMAP" → Enable IMAP

App Password chỉ có quyền IMAP/SMTP, **không** truy cập được các dịch vụ Google khác —
an toàn hơn nhiều so với dùng mật khẩu chính.

## 2. Lấy DeepSeek API key

https://platform.deepseek.com/ → tạo API key.

## 3. Cài đặt

```bash
cd gmail-agent
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
cp accounts.yaml.example accounts.yaml
```

Sửa `.env`: điền `DEEPSEEK_API_KEY`.
Sửa `accounts.yaml`: điền email + app password cho từng tài khoản (thêm bao nhiêu tài khoản tùy ý).

## 4. Chạy

```bash
python agent.py
```

Ví dụ lệnh có thể gõ:

- "Liệt kê 5 email mới nhất của tất cả tài khoản"
- "Có email nào chưa đọc từ sếp trong 3 ngày qua ở tài khoản work không?"
- "Tóm tắt email mới nhất từ [tên người gửi] ở tài khoản personal"
- "Soạn email trả lời [người nhận] với nội dung ... rồi gửi từ tài khoản work"

Với lệnh gửi email, agent sẽ **luôn hỏi xác nhận (y/n) trên terminal** trước khi gửi thật —
đây là điểm chặn an toàn quan trọng, không nên bỏ đi.

## 5. Ghi chú / giới hạn

- `search_emails` dùng cú pháp tìm kiếm kiểu Gmail (`from:`, `subject:`, `newer_than:7d`,
  `is:unread`, ...) vì tận dụng extension `X-GM-RAW` riêng của Gmail IMAP.
- Nội dung email khi đọc bị cắt ở 8000 ký tự để tránh tốn token — chỉnh trong
  `mail_tools.py` (`body[:8000]`) nếu cần dài hơn.
- Đây là bản khung tối giản (CLI, không lưu lịch sử hội thoại giữa các lần chạy).
  Có thể mở rộng thêm: lưu trạng thái đã đọc, chạy định kỳ (cron), giao diện web,
  hoặc thêm tool xóa/gắn nhãn email.
- Đổi `DEEPSEEK_MODEL` trong `.env` nếu DeepSeek đổi tên model sau này.
