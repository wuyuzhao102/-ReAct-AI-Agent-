# ⌨️ Git 命令速查表

> 打印出来贴在桌边。**加粗的**是每天都会用到的。
> 详细说明见 [团队协作规范](01-团队协作规范.md)。

---

## 🚀 开始工作前（每天）

| 目的 | 命令 |
| :--- | :--- |
| 查看当前在哪个分支 | **`git branch`** |
| 切换到 dev 并同步最新代码 | **`git switch dev`** → **`git pull`** |
| 切回自己的分支 | **`git switch feature/frontend`** |
| 把 dev 的最新内容合并进自己分支 | **`git merge dev`** |

---

## 📝 提交与推送（核心四步）

| 目的 | 命令 |
| :--- | :--- |
| 看改了哪些文件 | **`git status`** |
| 看具体改了哪几行 | `git diff` |
| 暂存全部改动 | **`git add .`** |
| 暂存指定文件 | `git add src/views/Login.vue` |
| 提交 | **`git commit -m "feat(frontend): 完成登录页"`** |
| 推送 | **`git push`** |
| 第一次推新分支 | `git push -u origin feature/frontend` |

---

## 🌿 分支操作

| 目的 | 命令 |
| :--- | :--- |
| 列出本地分支 | `git branch` |
| 列出所有分支（含远端） | `git branch -a` |
| 新建并切换分支 | `git switch -c feature/xxx` |
| 删除本地分支 | `git branch -d feature/xxx` |
| 拉取远端最新分支列表 | `git fetch --prune` |

---

## 🔍 查看历史

| 目的 | 命令 |
| :--- | :--- |
| 最近 10 条简洁记录 | `git log --oneline -10` |
| 带图的分支历史 | `git log --graph --oneline --all -20` |
| 某个文件的历史 | `git log --oneline -- 文件名` |
| 谁改的某一行 | `git blame 文件名` |
| 当前远端地址 | `git remote -v` |

---

## ↩️ 撤销（安全操作）

| 目的 | 命令 |
| :--- | :--- |
| 放弃某文件的改动（未 add） | `git restore 文件名` |
| 从暂存区取出（保留改动） | `git restore --staged 文件名` |
| 修改最后一次提交说明（未推） | `git commit --amend -m "新说明"` |
| 撤销最后一次提交（保留代码） | `git reset --soft HEAD~1` |
| 从 Git 移除但保留本地文件 | `git rm --cached 文件` |
| 临时保存改动 | `git stash` |
| 恢复临时保存 | `git stash pop` |
| 看 stash 列表 | `git stash list` |

> 🚫 **危险命令，新手禁止单独使用**：`git reset --hard`、`git clean -fd`、`git push -f`、`git checkout --theirs .`

---

## 🔧 一次性配置

```bash
git config --global user.name  "你的名字"
git config --global user.email "你的邮箱"
git config --global core.quotepath false
git config --global core.autocrlf false
git config --global core.longpaths true
git config --global init.defaultBranch main
git config --global pull.rebase false
```

---

## 🆘 实在搞乱了

```bash
cd ..
rm -rf -- "-ReAct-AI-Agent-"
git clone https://github.com/wuyuzhao102/-ReAct-AI-Agent-.git
```

> 只要 `push` 过，代码就在云端。**改一点推一点** 是最好的保险。
