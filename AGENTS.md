# AGENTS.md · 给 AI 编码助手的 Git 协作规则

> **本仓库的使用者不熟悉 Git。所有 Git 操作由你（AI）代劳，不要让他们手敲命令。**
> 汇报用中文，3 行以内：① 做了什么 ② 推没推上去 ③ 下一步要做什么。

---

## 0. 项目信息

| 项 | 值 |
| :--- | :--- |
| 仓库 | `https://github.com/wuyuzhao102/-ReAct-AI-Agent-.git` |
| 目录名 | `-ReAct-AI-Agent-`（前后各一个短横线，命令里要加引号） |
| 项目 | 基于 ReAct Agent 的校园课程学习助手（Vue3 + SpringBoot + FastAPI + MySQL） |
| 主干 | `main` —— **只读，任何人不得直接改** |
| 集成分支 | `dev` —— **只读，任何人不得直接改** |

## 1. 先确定"我是谁"

开工前问用户是哪一位，并记住（**只在属于自己的目录里改代码**）：

| 成员 | 负责目录 | 工作分支 |
| :--- | :--- | :--- |
| 朱斌 | `frontend/` | `feature/frontend` |
| 黄博成 | `backend/` | `feature/backend` |
| 伍宇钊 | `agent/` | `feature/agent` |
| 严博誉 | `docs/` | `feature/docs` |

跨目录改动（例如前端要改接口约定文档）必须先征求用户同意。

## 2. 分支模型（先看懂这张图，再动手）

```
main          ← 交付主干：只接受来自 dev 的 PR（阶段验收时才合一次）
  ↑
dev           ← 集成分支：只接受来自 feature/* 的 PR（四人的代码在这里汇合）
  ↑
feature/frontend   feature/backend   feature/agent   feature/docs
            ↑ 每人只在自己的这一条分支上写代码
```

**四条铁律**

1. 每个人**有且只有一条**自己的 `feature/` 分支，**长期使用**，不是每天新建。
2. `main` 和 `dev` 是**只读**的。你修改它们的唯一途径，是**自己发的 PR 被别人合并**。
3. 代码只能在 `feature/*` 上产生：本地写、本地提交、推送到**自己的远端分支**。
4. 从 `dev` 到 `main` 的合并**由项目负责人统一发起**，其他人不要发。

## 3. 红线（违反任何一条都算严重错误）

1. ❌ 在 `main` 或 `dev` 上**直接改代码、提交、推送**
2. ❌ **在 GitHub 网页上直接编辑 `main` / `dev` 里的文件**（这条最容易犯，一样属于直接改分支）
3. ❌ `git push -f` / `--force`（把 `main`、`dev`、别人的分支覆盖掉）
4. ❌ `git reset --hard`、`git clean -fd`、`git checkout --theirs .`
5. ❌ 提交这些内容：`.env`、`application-local.yml`、任何 API Key / 密码 / 学号身份证、`node_modules/`、`target/`、`dist/`、`.venv/`、`__pycache__/`、`*.pdf`、单文件 >10MB
6. ❌ 修改公共文件：`README.md`、`docs/01-团队协作规范.md`、`docs/03-开发环境与接口约定.md`、`.gitignore`、`AGENTS.md`（确需修改先问用户）
7. ❌ 在别人的 `feature/*` 分支上提交

## 4. 每天开工（用户说"开工"时执行）

**目标**：让本地 `dev` 是最新的，再把它合进自己的分支，然后才开始写代码。

```bash
git fetch origin
git switch dev
git pull                      # ① 先把本地 dev 更新到最新
git switch <我的分支>          # ② 切回自己的分支
git merge dev                 # ③ 把最新 dev 合进自己的分支
git status
```

汇报：`已同步 dev（N 个新提交），当前在 feature/xxx，工作区干净 / 有 N 个改动`。

- **第一次**（本地还没有自己的分支时）才需要创建：
  ```bash
  git switch -c feature/xxx
  git push -u origin feature/xxx
  ```
- 如果 `merge` 出现冲突 → 立即停下，按第 8 节处理，不要自己删别人的代码。

## 5. 写代码时的提交

**每完成一个"能用一句话说清"的小功能就提交一次**，不要把一天的活攒成巨型提交。

提交前必须做到：

1. `git status` 逐条检查，确认没有第 3 节列出的垃圾文件
2. 跑通对应验证：
   - 前端：`npm run build`
   - 后端：`mvn -q test`
   - Agent：`.venv\Scripts\python.exe -m pytest`
3. `git add <明确路径>`，不要无脑 `git add .`（除非已确认工作区干净）

**提交信息格式（严格）**

```
类型(模块): 一句话说明
```

- 类型只能是：`feat` `fix` `docs` `style` `refactor` `test` `chore`
- 模块只能是：`frontend` `backend` `agent` `docs` `config`
- 示例：`feat(frontend): 完成登录页表单校验` ✅ ／ `update` ❌ ／ `修改` ❌
- 一行写完，不超过 50 字，结尾不要句号

## 6. 每天收工（用户说"收工 / 提交 / 推一下"时执行）

```bash
git add <文件>
git commit -m "类型(模块): 说明"
git push origin <我的分支>      # 只推自己的分支，永远不推 dev / main
```

汇报：`已推送 N 个提交到 feature/xxx，远端已同步`。

## 7. 功能做完之后：发 PR 到 dev

**什么时候发**：一个完整功能做完、自测通过之后（不是每提交一次就发）。
发 PR 前先确认：① 已 push 到自己的分支 ② 分支上已经合并过最新的 `dev`。

**必填信息**

- Base 分支：`dev`（**不是 main**）
- Compare 分支：`feature/xxx`
- 标题：与提交信息同风格，例如 `feat(frontend): 登录页与表单校验`
- 描述：按 `.github/PULL_REQUEST_TEMPLATE.md` 填写，写清「做了什么 / 自测了什么 / 有无已知问题」

**发完之后**：告诉用户去网页点「Create pull request」，并 @ 一位同学 review。
**不要自己尝试合并，也不要直接推 `dev`。**

**PR 显示有冲突时**：在本地 `git switch <我的分支>` → `git merge dev` → 解决冲突 → `git push`，PR 会自动更新。

**合并之后**：提醒用户 `git switch dev && git pull`，否则本地的 `dev` 还是旧的，看不到别人的成果。

## 8. 报错的标准处理（不要自由发挥）

| 现象 | 处理方式 |
| :--- | :--- |
| `Updates were rejected` | `git pull` 之后再 `push`，**绝不 force** |
| `CONFLICT` 冲突 | 停下，列出冲突文件 + 两边差异，等用户决定 |
| `Authentication failed` | 提醒用户重新配置 Personal Access Token；**不要**擅自改 remote 地址 |
| `not a git repository` | 先 `cd` 到项目根目录再操作 |
| `LF will be replaced by CRLF` | 只是提示，忽略即可 |
| `git status` 中文变 `\346\226\207` | `git config --global core.quotepath false` |
| 本地改动挡住了切换/合并 | `git stash` 暂存 → 操作完 `git stash pop` |
| 误把改动提交到了 `dev` / `main` | **立刻停下告诉用户**，不要自行 reset 或 force push |

## 9. `dev` → `main` 的时机

只在**阶段验收**或**项目收尾**时由项目负责人发起：

```
feature/*  ──PR──▶  dev  ──PR（负责人）──▶  main
```

日常开发期间 `main` 保持不动。其他人**不要**自行发 `dev → main` 的 PR。

---

<sub>本文件由项目组维护，修改前请先沟通。人工版详细说明见 [docs/01-团队协作规范.md](docs/01-团队协作规范.md)。</sub>
