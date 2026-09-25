"""
mail_tools.py — Các hàm IMAP/SMTP dùng làm "tool" cho agent.
Chỉ dùng Gmail App Password (không cần OAuth), hoạt động với nhiều tài khoản.
"""

import imaplib
import smtplib
import email
from email.header import decode_header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import yaml


def load_accounts(path="accounts.yaml"):
    """Đọc accounts.yaml -> dict {ten_tai_khoan: {email, app_password, ...}}"""
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return {acc["name"]: acc for acc in data["accounts"]}


def _decode(s):
    if s is None:
        return ""
    parts = decode_header(s)
    out = ""
    for text, enc in parts:
        if isinstance(text, bytes):
            out += text.decode(enc or "utf-8", errors="replace")
        else:
            out += text
    return out


def _connect_imap(account):
    imap = imaplib.IMAP4_SSL(
        account.get("imap_host", "imap.gmail.com"),
        account.get("imap_port", 993),
    )
    imap.login(account["email"], account["app_password"])
    return imap


def _connect_smtp(account):
    smtp = smtplib.SMTP_SSL(
        account.get("smtp_host", "smtp.gmail.com"),
        account.get("smtp_port", 465),
    )
    smtp.login(account["email"], account["app_password"])
    return smtp


def _fetch_headers(imap, ids):
    results = []
    for i in ids:
        status, msg_data = imap.fetch(i, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])")
        raw_header = msg_data[0][1]
        msg = email.message_from_bytes(raw_header)
        results.append(
            {
                "id": i.decode(),
                "from": _decode(msg.get("From")),
                "subject": _decode(msg.get("Subject")),
                "date": msg.get("Date"),
            }
        )
    return results


def list_emails(accounts, account_name, folder="INBOX", limit=10, unread_only=False):
    """Lấy N email mới nhất của MỘT tài khoản."""
    account = accounts[account_name]
    imap = _connect_imap(account)
    try:
        imap.select(folder, readonly=True)
        criteria = "UNSEEN" if unread_only else "ALL"
        status, data = imap.search(None, criteria)
        ids = data[0].split()
        ids = ids[-limit:] if len(ids) > limit else ids
        ids = list(reversed(ids))  # mới nhất trước
        return _fetch_headers(imap, ids)
    finally:
        imap.logout()


def list_emails_all_accounts(accounts, folder="INBOX", limit_per_account=5, unread_only=False):
    """Lấy email mới nhất của TẤT CẢ tài khoản cùng lúc."""
    all_results = {}
    for name in accounts:
        try:
            all_results[name] = list_emails(accounts, name, folder, limit_per_account, unread_only)
        except Exception as e:
            all_results[name] = {"error": str(e)}
    return all_results


def read_email(accounts, account_name, message_id, folder="INBOX"):
    """Đọc toàn bộ nội dung một email theo id (id lấy từ list_emails)."""
    account = accounts[account_name]
    imap = _connect_imap(account)
    try:
        imap.select(folder, readonly=True)
        status, msg_data = imap.fetch(message_id.encode(), "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                disp = str(part.get("Content-Disposition"))
                if ctype == "text/plain" and "attachment" not in disp:
                    charset = part.get_content_charset() or "utf-8"
                    payload = part.get_payload(decode=True)
                    if payload:
                        body += payload.decode(charset, errors="replace")
        else:
            charset = msg.get_content_charset() or "utf-8"
            payload = msg.get_payload(decode=True)
            body = payload.decode(charset, errors="replace") if payload else ""

        return {
            "from": _decode(msg.get("From")),
            "to": _decode(msg.get("To")),
            "subject": _decode(msg.get("Subject")),
            "date": msg.get("Date"),
            "body": body[:8000],  # giới hạn độ dài để tránh tốn token
        }
    finally:
        imap.logout()


def search_emails(accounts, account_name, query, folder="INBOX", limit=10):
    """
    Tìm email theo cú pháp Gmail search (vd: 'from:boss@x.com newer_than:3d',
    'subject:invoice is:unread').
    """
    account = accounts[account_name]
    imap = _connect_imap(account)
    try:
        imap.select(folder, readonly=True)
        status, data = imap.search(None, "X-GM-RAW", f'"{query}"')
        ids = data[0].split()
        ids = ids[-limit:] if len(ids) > limit else ids
        ids = list(reversed(ids))
        return _fetch_headers(imap, ids)
    finally:
        imap.logout()


def send_email(accounts, account_name, to, subject, body, cc=None):
    """Gửi email từ một tài khoản cụ thể."""
    account = accounts[account_name]
    msg = MIMEMultipart()
    msg["From"] = account["email"]
    msg["To"] = to
    if cc:
        msg["Cc"] = cc
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    smtp = _connect_smtp(account)
    try:
        recipients = [to] + ([cc] if cc else [])
        smtp.sendmail(account["email"], recipients, msg.as_string())
        return {"status": "sent", "to": to, "subject": subject}
    finally:
        smtp.quit()
