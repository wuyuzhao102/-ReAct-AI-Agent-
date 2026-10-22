# 🐍 agent · Python 智能体模块（ReAct Agent）

> **负责人**：成员 3 ｜ **工作分支**：`feature/agent` ｜ **状态**：⏳ 待开发
> 🔥 **这是本项目的核心亮点模块**，也是答辩时最容易被追问的部分。

## 技术栈

| 项 | 选型 |
| :--- | :--- |
| Web 框架 | FastAPI + Uvicorn |
| Agent 框架 | LangChain（ReAct Agent） |
| 文档解析 | PyPDF（PDF）、python-docx（Word） |
| 大模型 | DeepSeek / 通义千问（OpenAI 兼容接口） |
| 文本检索 | 先用简单关键词 / TF-IDF，后期可升级向量检索 |
| 配置 | `.env` + python-dotenv |

## 核心：ReAct 循环

```text
用户问题
   ↓
┌──────────────────────────────────────────────┐
│ Thought：我现在还缺什么信息？下一步调用哪个工具？ │
│    ↓                                          │
│ Action：调用工具（最多 8 轮）                   │
│    ↓                                          │
│ Observation：拿到真实结果（课件原文/题目/计划）   │
└──────────────────────────────────────────────┘
   ↓ 任务完成
输出 Markdown + trace（Thought/Action/Observation 轨迹）
```

## 四个工具

| 工具函数 | 作用 | 关键参数 |
| :--- | :--- | :--- |
| `课件检索` | 在用户课件的文本索引中检索知识点 | `keyword`、`courseware_id` |
| `习题生成` | 基于课件原文生成练习题与解析 | `context`、`count`、`difficulty` |
| `备考计划` | 按考试时间与薄弱点排备考计划 | `exam_date`、`weak_points` |
| `笔记归档` | 把产出归档进学习档案 | `title`、`content` |

## 防死循环设计（必做）

1. **最大轮次上限**：默认 8 轮，超出强制收敛输出。
2. **任务完成判定**：模型返回 `final_answer` 或显式 `finish` 时立即结束。
3. **工具失败重试上限**：同一工具连续失败 2 次即跳过并说明原因。
4. **超时保护**：单次请求总时长上限（如 120s）。

## 目录结构（✅ 已实现 ／ ⏳ 规划中）

```text
agent/
├── requirements.txt              # ✅ 依赖
├── .env.example                  # ✅ 环境变量示例（真 Key 放本地 .env）
├── pytest.ini                    # ✅ 测试配置
├── app/
│   ├── main.py                   # ✅ FastAPI 入口（/、/health、/agent/tools、/agent/chat）
│   ├── config.py                 # ✅ 配置（环境变量 / .env）
│   ├── schemas.py                # ✅ 与 Java 层的数据契约
│   ├── parsers/
│   │   └── cleaner.py            # ✅ 课件文本清洗
│   ├── store/
│   │   └── memory.py             # ✅ 内存数据层（接 MySQL 后替换）
│   ├── tools/
│   │   ├── base.py               # ✅ 工具定义与注册表
│   │   ├── box.py                # ✅ 按用户绑定工具箱
│   │   ├── courseware.py         # ✅ 工具①课件检索
│   │   ├── exercise.py           # ✅ 工具②出题（规则版）
│   │   ├── plan.py               # ✅ 工具③备考计划
│   │   └── archive.py            # ✅ 工具④笔记归档
│   └── react/
│       ├── agent.py              # ✅ ReAct 循环 + 四条安全阀
│       ├── reasoner.py           # ✅ 规则兜底（LLM 版 ⏳ 待接入）
│       └── types.py              # ✅ 决策数据结构
└── tests/
    ├── test_api.py               # ✅ 接口契约
    ├── test_tools.py             # ✅ 四个工具
    ├── test_react_loop.py        # ✅ 循环与安全阀
    └── test_cleaner.py           # ✅ 文本清洗
```

## ReAct 循环怎么跑

```
用户提问
  ↓
ReActAgent 循环（最多 max_react_steps 轮）
  ├─ Reasoner.decide()  →  Thought + Action / 最终答案
  ├─ ToolBox 执行工具    →  Observation
  └─ 四条安全阀：轮次上限 / 重复调用打断 / 工具异常转观察 / 必定返回
  ↓
ChatResponse { answer(Markdown), trace[思考轨迹], finished }
```

`trace` 是答辩亮点：前端可以把每一步 Thought / Action / Observation 展开给学生看。

**当前由 `RuleBasedReasoner` 驱动**（不依赖大模型），走到的是：
检索 → 出题 →（有考试日期则）排计划 → 归档 → 总结。

**下一步**：新增 `LLMReasoner`（把 `registry.describe()` 塞进 prompt，让大模型输出 Thought/Action JSON），
在 `main.py` 里按 `settings.llm_configured` 选择用哪个 Reasoner —— 循环与工具层一行都不用改。


## 本地运行（VS Code）

### 1. 虚拟环境（已建好，路径 `agent/.venv`）

```powershell
# 如果 .venv 被删了，重新建（注意用 --without-pip，本机 ensurepip 不可用）
D:\python\python.exe -m venv --without-pip .venv
D:\python\python.exe -m pip --python .venv\Scripts\python.exe install -r requirements.txt
```

### 2. 配 Key

```powershell
copy .env.example .env
# 然后编辑 .env，把 LLM_API_KEY 换成自己的（DeepSeek 或通义千问）
```

### 3. 启动

```powershell
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

打开 http://localhost:8000/docs 能看到自动生成的接口文档。

### 4. 测试

```powershell
.venv\Scripts\python.exe -m pytest
```

### 5. VS Code 里更省事

- 仓库根目录已提交 `.vscode/settings.json`、`launch.json`、`extensions.json`
- 首次打开会提示 **安装推荐扩展**，点安装即可（Python、Pylance、Vue、Java、GitLens…）
- 按 **F5** 选 `🐍 Agent 服务 (FastAPI :8000)` 就能断点调试
- 测试面板（烧瓶图标）里可以直接点运行，不用敲命令

> ⚠️ 环境说明：本机 Python 是 **3.14**，`venv` 自带 pip 的引导（ensurepip）在这台机器上不可用，
> 所以要用上面的 `--without-pip` + 基础 pip 的方式建环境。其他同学如果是 3.11/3.12 直接用 `python -m venv .venv` 即可。


## 开发前必读

- [团队协作规范](../docs/01-团队协作规范.md)
- [开发环境与接口约定](../docs/03-开发环境与接口约定.md)

## 提醒

- `.env` 存 API Key，**已被 `.gitignore` 屏蔽，绝不提交**；仓库只提交 `.env.example`。
- 课件 PDF 不进仓库（原创课件有版权，且体积大）。
- 每次改 Prompt 后，把「输入 → trace → 输出」贴到 PR 里，方便对比效果。
