"""
agent.py — Vòng lặp AI Agent thật (tool-calling loop) dùng DeepSeek API,
quản lý email nhiều tài khoản Gmail qua IMAP/SMTP.

Chạy: python agent.py
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

import mail_tools as mt

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
MODEL = os.getenv("DEEPSEEK_MODEL")

if not DEEPSEEK_API_KEY:
    raise SystemExit("Chưa có DEEPSEEK_API_KEY. Copy .env.example -> .env rồi điền key vào.")

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

accounts = mt.load_accounts("accounts.yaml")

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_accounts",
            "description": "Liệt kê tên các tài khoản email đã cấu hình.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_emails",
            "description": "Lấy danh sách email mới nhất của MỘT tài khoản cụ thể.",
            "parameters": {
                "type": "object",
                "properties": {
                    "account_name": {"type": "string", "description": "Tên tài khoản, khớp với accounts.yaml"},
                    "folder": {"type": "string", "default": "INBOX"},
                    "limit": {"type": "integer", "default": 10},
                    "unread_only": {"type": "boolean", "default": False},
                },
                "required": ["account_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_emails_all_accounts",
            "description": "Lấy danh sách email mới nhất của TẤT CẢ tài khoản cùng lúc — dùng khi người dùng muốn xem tổng quan nhiều hộp thư.",
            "parameters": {
                "type": "object",
                "properties": {
                    "folder": {"type": "string", "default": "INBOX"},
                    "limit_per_account": {"type": "integer", "default": 5},
                    "unread_only": {"type": "boolean", "default": False},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_email",
            "description": "Đọc nội dung đầy đủ của một email theo id (id lấy từ list_emails/search_emails).",
            "parameters": {
                "type": "object",
                "properties": {
                    "account_name": {"type": "string"},
                    "message_id": {"type": "string"},
                    "folder": {"type": "string", "default": "INBOX"},
                },
                "required": ["account_name", "message_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_emails",
            "description": "Tìm email theo cú pháp Gmail search, vd 'from:boss@x.com newer_than:3d', 'subject:invoice is:unread'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "account_name": {"type": "string"},
                    "query": {"type": "string"},
                    "folder": {"type": "string", "default": "INBOX"},
                    "limit": {"type": "integer", "default": 10},
                },
                "required": ["account_name", "query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Gửi email từ một tài khoản cụ thể. Trước khi gọi tool này, phải soạn sẵn nội dung và người dùng sẽ được hỏi xác nhận qua terminal.",
            "parameters": {
                "type": "object",
                "properties": {
                    "account_name": {"type": "string"},
                    "to": {"type": "string"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"},
                    "cc": {"type": "string"},
                },
                "required": ["account_name", "to", "subject", "body"],
            },
        },
    },
]


def call_tool(name, args):
    if name == "list_accounts":
        return list(accounts.keys())
    if name == "list_emails":
        return mt.list_emails(accounts, **args)
    if name == "list_emails_all_accounts":
        return mt.list_emails_all_accounts(accounts, **args)
    if name == "read_email":
        return mt.read_email(accounts, **args)
    if name == "search_emails":
        return mt.search_emails(accounts, **args)
    if name == "send_email":
        print(f"\n⚠️  Agent muốn gửi email:")
        print(f"    Từ    : {args.get('account_name')}")
        print(f"    Đến   : {args.get('to')}")
        print(f"    Tiêu đề: {args.get('subject')}")
        print(f"    Nội dung:\n{args.get('body')}\n")
        confirm = input("Xác nhận gửi? (y/n): ").strip().lower()
        if confirm != "y":
            return {"status": "cancelled_by_user"}
        return mt.send_email(accounts, **args)
    return {"error": f"unknown tool {name}"}


SYSTEM_PROMPT = """Bạn là trợ lý quản lý email cá nhân, có quyền truy cập nhiều tài khoản Gmail qua các tool.
Nhiệm vụ: liệt kê, đọc, tìm kiếm, tóm tắt và soạn/gửi email theo yêu cầu người dùng.
Khi tóm tắt nhiều email: nêu ngắn gọn người gửi + ý chính từng email, nhóm theo tài khoản nếu liệt kê nhiều tài khoản.
Khi người dùng yêu cầu gửi email: LUÔN soạn nội dung rõ ràng trước, không tự suy diễn thông tin còn thiếu — hỏi lại nếu chưa đủ thông tin (người nhận, nội dung).
Trả lời bằng tiếng Việt trừ khi người dùng dùng ngôn ngữ khác."""


def run_agent():
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    print("=== Gmail Agent (DeepSeek) ===")
    print(f"Tài khoản đã cấu hình: {', '.join(accounts.keys())}")
    print("Gõ 'exit' để thoát.\n")

    while True:
        user_input = input("Bạn: ").strip()
        if user_input.lower() in ("exit", "quit"):
            break
        if not user_input:
            continue
        messages.append({"role": "user", "content": user_input})

        while True:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=TOOLS,
            )
            msg = resp.choices[0].message
            messages.append(msg.model_dump(exclude_none=True))

            if not msg.tool_calls:
                print(f"\nAgent: {msg.content}\n")
                break

            for tc in msg.tool_calls:
                name = tc.function.name
                try:
                    args = json.loads(tc.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}
                print(f"  [gọi tool: {name}({args})]")
                try:
                    result = call_tool(name, args)
                except Exception as e:
                    result = {"error": str(e)}
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(result, ensure_ascii=False, default=str),
                    }
                )


if __name__ == "__main__":
    run_agent()
