"""内存版数据层。

⚠️ 定位：这是**开发期的临时实现**，让 Agent 在没有 MySQL / 文件服务时也能跑通。
   接入 Spring Boot + MySQL 之后，这四个能力会改为：
   · 课件文本 → 由 Java 侧写入数据库，Python 只读检索（或独立向量库）
   · 笔记归档 → 通过 HTTP 回写 Java 业务层
   届时只需替换本文件的实现，工具层不用改。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

_CJK_RUN = re.compile(r"[\u4e00-\u9fff]{2,}")
_ASCII_WORD = re.compile(r"[A-Za-z][A-Za-z0-9_\-]{1,}")


@dataclass
class CoursewareDoc:
    id: int
    title: str
    text: str


@dataclass
class Note:
    id: int
    user_id: int
    title: str
    content: str


@dataclass
class SearchHit:
    courseware_id: int
    courseware_title: str
    paragraph: str
    score: int


def query_terms(query: str) -> set[str]:
    """把查询串切成检索词。

    中文没有空格，这里用「连续汉字段的 2-gram」做粗粒度切分，
    足够支撑开发期检索；接向量库后由 embedding 负责语义匹配。
    """
    terms: set[str] = set()
    for word in _ASCII_WORD.findall(query):
        terms.add(word.lower())
    for run in _CJK_RUN.findall(query):
        for i in range(len(run) - 1):
            terms.add(run[i : i + 2])
    return terms


@dataclass
class InMemoryStore:
    _docs: dict[int, CoursewareDoc] = field(default_factory=dict)
    _notes: dict[int, Note] = field(default_factory=dict)
    _next_note_id: int = 1

    # ---------------- 课件 ----------------
    def add_courseware(self, doc_id: int, title: str, text: str) -> None:
        self._docs[doc_id] = CoursewareDoc(id=doc_id, title=title, text=text)

    def list_courseware(self) -> list[CoursewareDoc]:
        return list(self._docs.values())

    def search(
        self, query: str, courseware_id: int | None = None, top_k: int = 3
    ) -> list[SearchHit]:
        terms = query_terms(query)
        if not terms:
            return []

        if courseware_id is not None:
            doc = self._docs.get(courseware_id)
            docs = [doc] if doc else []
        else:
            docs = list(self._docs.values())

        hits: list[SearchHit] = []
        for doc in docs:
            for para in doc.text.split("\n\n"):
                para = para.strip()
                if not para:
                    continue
                score = sum(para.count(t) for t in terms)
                if score > 0:
                    hits.append(
                        SearchHit(
                            courseware_id=doc.id,
                            courseware_title=doc.title,
                            paragraph=para,
                            score=score,
                        )
                    )

        hits.sort(key=lambda h: h.score, reverse=True)
        return hits[: max(1, top_k)]

    # ---------------- 笔记 ----------------
    def add_note(self, user_id: int, title: str, content: str) -> Note:
        note = Note(id=self._next_note_id, user_id=user_id, title=title, content=content)
        self._notes[note.id] = note
        self._next_note_id += 1
        return note

    def list_notes(self, user_id: int) -> list[Note]:
        return [n for n in self._notes.values() if n.user_id == user_id]

    # ---------------- 测试用 ----------------
    def clear(self) -> None:
        self._docs.clear()
        self._notes.clear()
        self._next_note_id = 1


# 进程内单例（开发期够用；多 worker 部署时需替换为真实存储）
store = InMemoryStore()


DEMO_COURSEWARE = """第一章 极限

1.1 极限的定义
设函数 f(x) 在点 x0 的某个去心邻域内有定义，如果当 x 无限趋近于 x0 时，函数值 f(x) 无限趋近于一个确定的常数 A，则称 A 为函数 f(x) 当 x→x0 时的极限。

1.2 两个重要极限
第一个重要极限：lim(x→0) sin x / x = 1。
第二个重要极限：lim(x→∞) (1 + 1/x)^x = e。

1.3 洛必达法则
对于 0/0 型或 ∞/∞ 型未定式，若分子分母在去心邻域内可导且分母导数不为零，则 lim f(x)/g(x) = lim f'(x)/g'(x)。

1.4 等价无穷小替换
当 x→0 时：sin x ~ x，tan x ~ x，1 - cos x ~ x²/2，ln(1+x) ~ x，e^x - 1 ~ x。

课堂例题
例 1 求 lim(x→0) (sin 3x)/x。解：由等价无穷小 sin 3x ~ 3x，原式 = 3。"""


def boot_demo_data() -> None:
    """开发期灌入一份样例课件，方便前后端联调；接入真实上传后删掉此函数。"""
    if store.list_courseware():
        return
    store.add_courseware(1, "高等数学（上）· 第一章 极限", DEMO_COURSEWARE)
