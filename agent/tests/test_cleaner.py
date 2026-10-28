"""课件文本清洗的单元测试。"""

from app.parsers.cleaner import clean_text, normalize_for_search


def test_merges_chinese_broken_lines():
    raw = "极限的定义是：当 x 无限趋近于某个值\n时，函数值趋近于常数。"
    assert "某个值时" in clean_text(raw)


def test_fixes_hyphenated_word_break():
    raw = "exam-\nple"
    assert "example" in clean_text(raw)


def test_drops_page_number_lines():
    raw = "正文第一段。\n— 3 —\n第 2 页 / 共 10 页\nPage 4 of 9\n正文第二段。"
    cleaned = clean_text(raw)
    assert "—" not in cleaned
    assert "共 10 页" not in cleaned
    assert "Page" not in cleaned
    assert "正文第一段。" in cleaned and "正文第二段。" in cleaned


def test_removes_zero_width_and_control_chars():
    raw = "零宽\u200b字符\x07与控制符"
    cleaned = clean_text(raw)
    assert "\u200b" not in cleaned
    assert "\x07" not in cleaned
    assert "零宽字符" in cleaned


def test_keeps_list_and_heading_lines_separate():
    raw = "# 第一章 极限\n- 极限定义\n- 两个重要极限"
    cleaned = clean_text(raw)
    assert "# 第一章 极限" in cleaned
    assert "- 极限定义" in cleaned


def test_collapses_blank_lines():
    raw = "第一段\n\n\n\n\n第二段"
    assert "\n\n\n" not in clean_text(raw)


def test_empty_input():
    assert clean_text("") == ""
    assert clean_text("   \n  ") == ""


def test_normalize_for_search_flattens_whitespace():
    raw = "极限\n的  定义"
    out = normalize_for_search(raw)
    assert "\n" not in out
    assert "  " not in out
