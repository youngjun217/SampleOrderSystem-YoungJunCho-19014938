import unicodedata


def dw(s: str) -> int:
    """동아시아 문자는 터미널에서 2칸 → 실제 표시 너비 반환."""
    return sum(2 if unicodedata.east_asian_width(c) in ("W", "F") else 1 for c in s)


def ljust(s: str, width: int) -> str:
    return s + " " * max(0, width - dw(s))


def rjust(s: str, width: int) -> str:
    return " " * max(0, width - dw(s)) + s
