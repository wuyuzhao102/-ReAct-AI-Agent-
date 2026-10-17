# 🖥️ frontend · 前端模块（Vue 3）

> **负责人**：成员 1 ｜ **工作分支**：`feature/frontend` ｜ **状态**：⏳ 待开发

## 技术栈

| 项 | 选型 |
| :--- | :--- |
| 框架 | Vue 3（组合式 API `<script setup>`）+ Vite |
| UI 库 | Element Plus |
| 路由 / 状态 | Vue Router + Pinia |
| 请求 | Axios（统一封装 `/api` 前缀 + JWT 拦截器） |
| Markdown 渲染 | markdown-it + KaTeX（数学公式） |

## 计划页面

| 页面 | 路由 | 主要功能 |
| :--- | :--- | :--- |
| 登录 / 注册 | `/login` | 表单校验、JWT 保存 |
| 课件管理 | `/courseware` | 上传 PDF/Word、列表、删除、解析状态 |
| AI 对话 | `/chat` | 对话气泡、四类工具结果渲染、Thought 轨迹展开 |
| 学习档案 | `/archive` | 历史对话、笔记、错题本 |

## 计划目录

```text
frontend/
├── index.html
├── package.json
├── vite.config.js          # 配置 /api 代理到 8080
└── src/
    ├── main.js
    ├── App.vue
    ├── api/                # 接口封装
    ├── assets/
    ├── components/         # 通用组件
    ├── router/
    ├── stores/             # Pinia
    ├── styles/
    └── views/              # 页面
```

## 开发前必读

- [团队协作规范](../docs/01-团队协作规范.md)
- [开发环境与接口约定](../docs/03-开发环境与接口约定.md)

## 约定

- 前端**只调 Java 的 `/api/**`**，不直连 Python 服务。
- 不在代码里写死后端地址（走 Vite proxy）。
- 任何密钥、Token 都不进前端源码。
