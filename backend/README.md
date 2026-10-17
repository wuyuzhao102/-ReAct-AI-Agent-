# ☕ backend · 业务服务模块（Spring Boot）

> **负责人**：成员 2 ｜ **工作分支**：`feature/backend` ｜ **状态**：⏳ 待开发

## 技术栈

| 项 | 选型 |
| :--- | :--- |
| 框架 | Spring Boot 3（JDK 17） |
| 持久层 | MyBatis-Plus（或 Spring Data JPA，**第 1 周内定下来**） |
| 数据库 | MySQL 8.0（库名 `coursemate`，`utf8mb4`） |
| 认证 | JWT（`Authorization: Bearer <token>`） |
| 文档 | Swagger / Knife4j |
| 调用 Python | RestTemplate / WebClient / OpenFeign |

## 职责边界

| ✅ 该做 | ❌ 不该做 |
| :--- | :--- |
| 用户注册登录、密码加密、JWT 签发 | 写 Agent 推理逻辑、Prompt |
| 课件文件存储与元数据管理 | 解析 PDF 正文（交给 Python 服务） |
| 数据库读写、业务编排 | 直接在 Controller 里拼 SQL |
| 转发请求到 Python Agent 服务并透传结果 | 存放大模型 API Key 到仓库 |

## 计划模块

```text
backend/
├── pom.xml
├── sql/                         # 建表脚本（只提交脚本，不提交数据）
└── src/main/java/com/coursemate/
    ├── CoursemateApplication.java
    ├── common/                  # 统一返回、异常、工具
    ├── config/                  # 安全、跨域、Swagger
    ├── user/                    # 用户模块
    ├── courseware/              # 课件模块
    ├── chat/                    # 对话转发
    └── archive/                 # 笔记、错题、档案
```

## 计划接口

| 方法 | 路径 | 说明 |
| :--- | :--- | :--- |
| POST | `/api/auth/register` | 注册 |
| POST | `/api/auth/login` | 登录，返回 JWT |
| POST | `/api/courseware/upload` | 上传课件 |
| GET | `/api/courseware/list` | 课件列表 |
| DELETE | `/api/courseware/{id}` | 删除课件 |
| POST | `/api/chat/send` | 发消息（内部转 Python `/agent/chat`） |
| GET | `/api/archive/notes` | 笔记列表 |
| GET | `/api/archive/wrong-questions` | 错题列表 |

## 开发前必读

- [团队协作规范](../docs/01-团队协作规范.md)
- [开发环境与接口约定](../docs/03-开发环境与接口约定.md)

## 提醒

- `application-local.yml` 存本地数据库密码，**已在 `.gitignore` 屏蔽，不要提交**。
- 表结构改动要同步更新 `sql/` 下的脚本并在群里通知。
