# AGENTS.md · 给 AI 编码助手的 Git 协作规则

> **本仓库的使用者不熟悉 Git。所有 Git 操作由你（AI）代劳，不要让他们手敲命令。**
> 汇报用中文，3 行以内：① 做了什么 ② 推没推上去 ③ 下一步要做什么。

---

## 0. 项目信息

| 项 | 值 |
| :--- | :--- |
| 仓库 | `https://github.com/wuyuzhao102/-ReAct-AI-Agent-.git` |
| 主干 | `main` —— **禁止直接推送** |
| 集成分支 | `dev` —— **禁止直接推送**，只走 PR |
| 目录名 | `-ReAct-AI-Agent-`（前后各一个短横线，命令里要加引号） |
| 项目 | 基于 ReAct Agent 的校园课程学习助手（Vue3 + SpringBoot + FastAPI + MySQL） |

## 1. 先确定"我是谁"

开工前问用户是哪一位，并记住（**只在属于自己的目录里改代码**）：

| 成员 | 负责目录 | 工作分支 |
| :--- | :--- | :--- |
| 朱斌 | `frontend/` | `feature/frontend` |
| 黄博成 | `backend/` | `feature/backend` |
| 伍宇钊 | `agent/` | `feature/agent` |
| 严博誉 | `docs/` | `feature/docs` |

跨目录改动（例如前端要改接口约定文档）必须先征求用户同意。

## 2. 红线（违反任何一条都算严重错误）

1. ❌ `git push` 到 `main` 或 `dev`
2. ❌ `git push -f` / `--force`
3. ❌ `git reset --hard`、`git clean -fd`、`git checkout --theirs .`
4. ❌ 提交这些内容：`.env`、`application-local.yml`、任何 API Key / 密码 / 学号身份证、`node_modules/`、`target/`、`dist/`、`.venv/`、`__pycache__/`、`*.pdf`、单文件 >10MB
5. ❌ 修改公共文件：`README.md`、`docs/01-团队协作规范.md`、`docs/03-开发环境与接口约定.md`、`.gitignore`、`AGENTS.md`（确需修改先问用户）
6. ❌ 在别人的 `feature/*` 分支上提交

## 3. 每天开工（用户说"开工"时执行）

```bash
git fetch origin
git switch dev && git pull
git switch <我的分支> && git merge dev
git status
```

汇报：`已同步 dev（N 个新提交），当前在 feature/xxx，工作区干净 / 有 N 个改动`。

- 如果当前目录还不是仓库 → 先 `git clone` 再 `git switch <我的分支>`
- 如果 `merge` 出现冲突 → 立即停下，按第 6 节处理

## 4. 写代码时的提交

**每完成一个"能用一句话说清"的小功能就提交一次**，不要把一天的活攒成一个巨型提交。

提交前必须做到：

1. `git status` 逐条检查，确认没有第 2 节列出的垃圾文件
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

## 5. 每天收工（用户说"收工 / 提交 / 推一下"时执行）

```bash
git add <文件>
git commit -m "类型(模块): 说明"
git push origin <我的分支>
```

汇报：`已推送 N 个提交到 feature/xxx，远端已同步`。

## 6. 报错的标准处理（不要自由发挥）

| 现象 | 处理方式 |
| :--- | :--- |
| `Updates were rejected` | `git pull` 之后再 `push`，**绝不 force** |
| `CONFLICT` 冲突 | 停下，列出冲突文件 + 两边差异，等用户决定，不要自行删他人代码 |
| `Authentication failed` | 提醒用户重新配置 Personal Access Token；**不要**擅自改 remote 地址 |
| `not a git repository` | 先 `cd` 到项目根目录再操作 |
| `LF will be replaced by CRLF` | 只是提示，忽略即可 |
| `git status` 中文变 `\346\226\207` | `git config --global core.quotepath false` |
| 本地改动挡住了切换/合并 | `git stash` 暂存 → 操作完 `git stash pop` |

## 7. 功能做完之后

提醒用户去 GitHub 网页发 **Pull Request：`feature/xxx` → `dev`**，PR 描述里写 `Closes #<issue编号>`。
**不要自己尝试合并，也不要直接推 `dev`。**

---

<sub>本文件由项目组维护，修改前请先沟通。人工版详细说明见 [docs/01-团队协作规范.md](docs/01-团队协作规范.md)。</sub>
