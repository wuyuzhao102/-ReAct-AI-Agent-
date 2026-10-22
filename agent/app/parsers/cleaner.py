"""课件文本清洗。

为什么需要它（对应项目文档「难点 3：PDF 文本提取乱码」）：
    PyPDF 从 PDF 抽出来的文字经常带一堆毛病 ——
    · 每行末尾被硬换行切断，一个完整句子散成好几行；
    · 空白页、页眉页脚、页码混进正文；
    · 零宽字符、不间断空格、控制字符；
    · 连字符断词（"exam-" + 换行 + "ple"）。

    这些脏数据直接丢给大模型，会显著降低检索命中率和回答质量，
    所以先清洗、再建索引。

纯标准库实现，不依赖任何第三方包，方便单独测试。
"""

from __future__ import annotations

import re
import unicodedata

# 零宽字符与软连字符，肉眼不可见但会污染检索
_ZERO_WIDTH = dict.fromkeys(map(ord, "\u200b\u200c\u200d\u2060\ufeff\u00ad"), None)

# 控制字符（保留 \n \t）
_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

# 页码行：— 12 — / - 3 - / 第 3 页 / 第 3 页 / 共 10 页 / Page 3 of 10 / 3/10
_PAGE_NO_PATTERNS = [
    re.compile(r"^\s*[—–\-]\s*\d{1,4}\s*[—–\-]\s*$"),
    re.compile(r"^\s*第\s*\d{1,4}\s*页(\s*[/／]?\s*共\s*\d{1,4}\s*页)?\s*$"),
    re.compile(r"^\s*page\s*\d{1,4}(\s*(of|/)\s*\d{1,4})?\s*$", re.IGNORECASE),
    re.compile(r"^\s*\d{1,4}\s*/\s*\d{1,4}\s*$"),
]

# 连字符断词：exam-\nple -> example
_HYPHEN_BREAK = re.compile(r"(\w)-\n(\w)")

# 汉字 / 中文标点
_CJK = re.compile(r"[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]")


def _is_cjk(ch: str) -> bool:
    return bool(ch) and bool(_CJK.match(ch))


def _drop_page_numbers(text: str) -> str:
    kept = []
    for line in text.split("\n"):
        if any(p.match(line) for p in _PAGE_NO_PATTERNS):
            continue
        kept.append(line)
    return "\n".join(kept)


def _merge_broken_lines(text: str) -> str:
    """把被硬换行切断的句子接回去。

    规则：
    - 上一行结尾是中文，且下一行开头是中文 → 直接拼接，不加空格；
    - 上一行结尾是英文单词，下一行开头是小写字母 → 加一个空格拼接；
    - 其余情况（下一行是标题、列表项、空行）→ 保留换行。
    """
    lines = text.split("\n")
    out: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not out:
            out.append(stripped)
            continue

        prev = out[-1]
        prev_char = prev[-1] if prev else ""
        next_char = stripped[0] if stripped else ""

        mergeable = (
            bool(prev)
            and bool(stripped)
            # 标题/列表项/表格行不合并
            and not stripped.startswith(("#", "-", "*", "•", "|", ">"))
            and not re.match(r"^\d+[.、)]", stripped)
            and (
                (_is_cjk(prev_char) and _is_cjk(next_char))
                or (prev_char.isascii() and prev_char.isalpha() and next_char.islower())
            )
        )

        if mergeable:
            joiner = "" if (_is_cjk(prev_char) and _is_cjk(next_char)) else " "
            out[-1] = prev + joiner + stripped
        else:
            out.append(stripped)
    return "\n".join(out)


def clean_text(raw: str) -> str:
    """把 PDF/Word 抽出的原始文本清洗成可入库、可检索的干净文本。

    步骤：去零宽字符 → 去控制字符 → 统一换行 → 连字符断词修复
         → 去页码 → 合并断行 → 压缩空行 → 去首尾空白
    """
    if not raw:
        return ""

    text = raw.translate(_ZERO_WIDTH)
    text = _CONTROL.sub("", text)
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\u00a0", " ").replace("\u3000", " ")

    text = _HYPHEN_BREAK.sub(r"\1\2", text)
    text = _drop_page_numbers(text)
    text = _merge_broken_lines(text)

    # 行尾空格、连续空行（最多保留一个空行分段）
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def normalize_for_search(text: str) -> str:
    """检索用的归一化：去多余空白，便于关键词匹配。"""
    return re.sub(r"\s+", " ", clean_text(text)).strip()


if __name__ == "__main__":  # pragma: no cover
    import sys

    # Windows 默认控制台是 GBK，打印零宽字符会直接抛 UnicodeEncodeError
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    demo = (
        "第一章 极限\n\n"
        "极限的定义是：当 x 无限趋近于某个值\n"
        "时，函数值无限趋近于一个确定的常数。\n"
        "— 3 —\n"
        "两个重要极限：lim(sin x / x) = 1，\n"
        "以及 lim(1 + 1/x)^x = e。\n\n\n\n"
        "exam-\nple 例句\u200b。\n"
        "第 3 页 / 共 10 页\n"
    )
    print("---------- 清洗前 ----------")
    print(demo.replace("\u200b", "[零宽字符]"))
    print("---------- 清洗后 ----------")
    print(clean_text(demo))
