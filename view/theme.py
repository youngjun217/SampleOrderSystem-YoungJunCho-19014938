"""
Terminal UI theme: ANSI colors + Unicode box-drawing characters.
Enables ANSI support on Windows automatically.
"""
import os
import re
import unicodedata

if os.name == "nt":
    os.system("")          # ANSI 활성화 (Windows 10+)

# ── ANSI ─────────────────────────────────────────────────────────────
RST  = "\033[0m"
BOLD = "\033[1m"
DIM  = "\033[2m"

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = (
    "\033[30m", "\033[31m", "\033[32m", "\033[33m",
    "\033[34m", "\033[35m", "\033[36m", "\033[37m",
)
GRAY, BRED, BGREEN, BYELLOW, BBLUE, BMAGENTA, BCYAN, BWHITE = (
    "\033[90m", "\033[91m", "\033[92m", "\033[93m",
    "\033[94m", "\033[95m", "\033[96m", "\033[97m",
)

def c(text, *codes) -> str:
    return "".join(codes) + str(text) + RST

def title(t):   return c(t, BOLD, BCYAN)
def sub(t):     return c(t, BOLD, BWHITE)
def success(t): return c(t, BGREEN)
def warn(t):    return c(t, BYELLOW)
def danger(t):  return c(t, BRED)
def info(t):    return c(t, CYAN)
def muted(t):   return c(t, GRAY)
def bold(t):    return c(t, BOLD)
def primary(t): return c(t, BBLUE)

# ── Status colors ──────────────────────────────────────────────────
STATUS_COLOR = {
    "RESERVED":  BYELLOW,
    "PRODUCING": BBLUE,
    "CONFIRMED": BGREEN,
    "RELEASE":   BCYAN,
    "REJECTED":  BRED,
    "IDLE":      GRAY,
    "RUNNING":   BBLUE,
    "WAITING":   BYELLOW,
    "DONE":      BGREEN,
    "여유":      BGREEN,
    "부족":      BYELLOW,
    "고갈":      BRED,
}

def status_c(text: str) -> str:
    col = STATUS_COLOR.get(text, WHITE)
    return c(text, BOLD, col)

# ── Display width ──────────────────────────────────────────────────
def dw(s: str) -> int:
    plain = re.sub(r"\033\[[0-9;]*m", "", s)
    return sum(2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
               for ch in plain)

def pad_r(text: str, width: int, fill: str = " ") -> str:
    return text + fill * max(0, width - dw(text))

def pad_l(text: str, width: int, fill: str = " ") -> str:
    return fill * max(0, width - dw(text)) + text

# ── Box drawing ───────────────────────────────────────────────────
W = 70          # total outer box width
INNER = W - 4   # usable inner display width (║  …  ║)

TL, TR, BL, BR = "╔", "╗", "╚", "╝"
H,  V          = "═", "║"
ML, MR         = "╠", "╣"
itl, itr       = "┌", "┐"
ibl, ibr       = "└", "┘"
ih, iv         = "─", "│"

def box_top()  -> str: return muted(TL + H * (W - 2) + TR)
def box_mid()  -> str: return muted(ML + H * (W - 2) + MR)
def box_bot()  -> str: return muted(BL + H * (W - 2) + BR)

def box_line(content: str = "") -> str:
    pad = max(0, INNER - dw(content))
    return f"{muted(V)}  {content}{' ' * pad}  {muted(V)}"

def section_line(label: str, width: int = 66) -> str:
    plain = re.sub(r"\033\[[0-9;]*m", "", label)
    bar_w = max(0, width - dw(plain) - 4)
    left  = bar_w // 2
    right = bar_w - left
    return c("─" * left + "  " + plain + "  " + "─" * right, BCYAN, BOLD)

def menu_num(n: str) -> str:
    return c(f" {n} ", BOLD, BLACK, "\033[43m") + RST   # yellow bg, black fg
