
CAPABILITY_VERSION = "v1"

_CAPABILITIES = {
    "CAP_EMAIL_READ": "Có khả năng đọc nội dung một email cụ thể.",
    "CAP_EMAIL_LIST": "Có khả năng liệt kê email trong một hộp thư.",
    "CAP_EMAIL_SEARCH": "Có khả năng tìm kiếm email theo điều kiện lọc.",
    "CAP_EMAIL_SEND": "Có khả năng gửi email ra ngoài.",
    "CAP_ACCOUNT_ENUM": "Có khả năng liệt kê danh tính/tài khoản đang quản lý.",
}


def list_all() -> list[str]:
    return sorted(_CAPABILITIES.keys())


def is_known(tag: str) -> bool:
    return tag in _CAPABILITIES


def describe(tag: str) -> str | None:
    return _CAPABILITIES.get(tag)
