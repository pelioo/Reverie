# Reverie 使用指南

## 目录

- [项目简介](#项目简介)
- [快速开始](#快速开始)
- [本地开发部署](#本地开发部署)
- [Docker 部署](#docker-部署)
- [配置说明](#配置说明)
- [运行模式详解](#运行模式详解)
- [WebUI 使用](#webui-使用)
- [API 接口](#api-接口)
- [目录结构](#目录结构)
- [常见问题](#常见问题)

---

## 项目简介

Reverie 是一个**面向自进化的 Agent 运行框架**。其核心创新是"潜意识生成（Subconscious Generation）"：

- **不依赖人类持续提问**，而是生成内部冲动与目标
- **持续写入记忆**，让上下文随时间复利增长
- 支持在"自主成长"和"交互回复"之间自由切换

适用场景：
- 持续产出想法与实验结果的自治研究伙伴
- 能跨天累积上下文的工程开发助理
- 研究长时运行 Agent 涌现行为的沙盒平台
- "常驻在线个人 AI" 的原型基础设施

---

## 快速开始

### 方式一：Docker 快速启动（5 分钟）

```bash
# 1. 克隆项目
git clone https://github.com/your-repo/reverie.git
cd reverie

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，填入 OPENAI_API_KEY、OPENAI_BASE_URL、REVERIE_MODEL

# 3. 启动全部服务（后端 + WebUI）
docker compose up -d --build

# 4. 进入交互模式
./start.sh

# 5. 访问
# WebUI: http://localhost:5173
# API:   http://localhost:8000/health
```

### 方式二：本地开发部署

详见下一节。

---

## 本地开发部署

### 前置条件

- Python 3.10+
- Node.js 18+（仅使用 WebUI 时需要）
- OpenAI 兼容 API 密钥（OpenAI / Claude / 本地模型等）

### 步骤 1：安装 Python 依赖

```bash
# 使用虚拟环境（推荐）
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 步骤 2：配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，至少填写以下必填项：

```env
# 必填
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
REVERIE_MODEL=gpt-4o-mini

# 可选（使用默认值）
REVERIE_MEMORY_DIR=memory
REVERIE_WORKSPACE_ROOT=workspace
REVERIE_SOUL_TEMPLATE=souls/soul.md
```

### 步骤 3：启动后端 API（可选）

如果不使用 WebUI 实时查看，可以跳过此步，直接运行 CLI。

```bash
# 终端 1: 启动 API 服务
uvicorn reverie.api:app --reload --port 8000
```

### 步骤 4：启动 WebUI（可选）

```bash
# 终端 2: 启动前端
cd webui
npm install
npm run dev
# 访问 http://localhost:5173
```

### 步骤 5：运行 Agent

```bash
# 三种模式选择一种

# 模式 1：Reverie（自主成长）- 无人值守，持续探索
python -m reverie.cli --mode Reverie --session-id my-reverie

# 模式 2：Lucid（交互回复）- 等待用户提问
python -m reverie.cli --mode Lucid --session-id my-lucid

# 模式 3：Murmur（混合模式）- 可自主漂移，也可随时交互
python -m reverie.cli --mode Murmur --session-id my-murmur
```

### 完整命令示例

```bash
# 带所有参数启动
python -m reverie.cli \
  --mode Murmur \
  --session-id dev-session \
  --model gpt-4o-mini \
  --workspace-root ./workspace \
  --memory-dir memory \
  --temperature 0.7 \
  --max-idle 60

# 指定运行轮次
python -m reverie.cli --mode Lucid --session-id test --ticks 10

# 预置用户消息
python -m reverie.cli --mode Lucid --session-id test -m "你好，帮我解释这个项目" -m "再告诉我它的核心优势"
```

---

## Docker 部署

### 常用命令

```bash
# 启动全部服务（后端 + WebUI）
docker compose up -d --build

# 仅启动后端
docker compose up -d --build backend

# 使用脚本管理
./reverie.sh reverie    # 后台运行 Reverie 模式
./reverie.sh lucid     # 进入交互式 Lucid 会话
./reverie.sh murmur    # 进入混合 Murmur 会话
./reverie.sh logs      # 查看日志
./reverie.sh down      # 停止所有服务
```

### 环境变量覆盖

```bash
# 通过环境变量指定模式
REVERIE_RUN_MODE=Lucid REVERIE_SESSION_ID=my-session docker compose run --rm backend
```

---

## 配置说明

### 环境变量详解

| 变量 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `OPENAI_API_KEY` | ✅ | - | OpenAI 兼容 API 密钥 |
| `OPENAI_BASE_URL` | ✅ | - | API 地址 |
| `REVERIE_MODEL` | ✅ | - | 模型名称 |
| `REVERIE_MEMORY_DIR` | | `memory` | 记忆存储目录 |
| `REVERIE_WORKSPACE_ROOT` | | `workspace` | 工作空间根目录 |
| `REVERIE_SOUL_TEMPLATE` | | `souls/soul.md` | Agent 人格模板 |
| `REVERIE_RUN_MODE` | | `Reverie` | 运行模式 |
| `REVERIE_SESSION_ID` | | `reverie` | 会话标识符 |
| `REVERIE_ENABLE_API` | | `1` | 是否启用 API 服务 |
| `REVERIE_API_HOST` | | `0.0.0.0` | API 监听地址 |
| `REVERIE_API_PORT` | | `8000` | API 监听端口 |

### 支持的模型

Reverie 使用 OpenAI 兼容 API，理论上支持所有 OpenAI 兼容模型：

- OpenAI: `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`
- Claude (通过兼容网关): `claude-3-opus`, `claude-3-sonnet`
- 本地模型: `llama`, `qwen`, `deepseek` 系列
- 其他兼容 API: MiniMax, 硅基流动, Together 等

### 人格模板

修改 `souls/soul.md` 或 `souls/soul_zh.md` 可自定义 Agent 的行为风格。

---

## 运行模式详解

### Reverie 模式（自主成长）

```
状态：无人值守运行
特点：
  - Agent 持续探索、规划、调用工具
  - 记忆随时间累积增长
  - 自动后台运行，可关闭终端
  - 支持 API/WebUI 观察状态

适用：长时间自治实验、持续研究
```

### Lucid 模式（交互回复）

```
状态：等待用户输入
特点：
  - Agent 基于累积记忆响应用户提问
  - 每次交互都会更新记忆
  - 适合精准问答场景

适用：开发助理、问题解答
```

### Murmur 模式（混合状态）

```
状态：可自主可交互
特点：
  - 融合两种状态
  - 空闲时自主探索
  - 用户提问时立即响应

适用：日常陪伴、混合工作流
```

### CLI 交互命令

在 Lucid/Murmur 模式下：

```
/quit          - 退出程序
/reset         - 重置当前会话
/mode <mode>   - 切换模式 (Reverie/Lucid/Murmur)
/memory        - 查看当前记忆状态
/status        - 查看运行状态
/help          - 显示帮助信息
```

---

## WebUI 使用

### 访问

启动 WebUI 后访问 `http://localhost:5173`

### 功能

- **活动流可视化**：实时查看 Agent 的思考和行动
- **记忆浏览器**：查看和管理累积的记忆
- **会话管理**：切换不同会话
- **状态监控**：观察 Agent 运行状态

### WebUI + API 联动

```bash
# 终端 1: 启动后端（启用 API）
python -m reverie.cli --mode Reverie --session-id reverie

# 终端 2: 启动 WebUI
cd webui && npm run dev

# 浏览器打开 http://localhost:5173
```

---

## API 接口

### 健康检查

```
GET http://localhost:8000/health
```

### 主要接口

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/api/sessions` | GET | 列出所有会话 |
| `/api/sessions/{id}` | GET | 获取会话详情 |
| `/api/memory/{session_id}` | GET | 获取会话记忆 |
| `/api/chat` | POST | 发送消息 |

### API 使用示例

```bash
# 健康检查
curl http://localhost:8000/health

# 获取会话列表
curl http://localhost:8000/api/sessions

# 发送消息
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "my-session", "message": "你好"}'
```

---

## 目录结构

```
reverie/
├── reverie/              # Python 核心代码
│   ├── api/              # FastAPI 服务
│   ├── cli.py            # 命令行入口
│   ├── context/          # 上下文管理
│   ├── llm/              # LLM 接口封装
│   ├── memory/           # 记忆系统
│   ├── orchestrator/     # 任务编排
│   ├── scheduler/        # 调度器
│   ├── subconscious/     # 潜意识模块
│   ├── session_state/    # 会话状态
│   ├── tools/            # 内置工具
│   ├── tui/              # 终端 UI
│   └── user_tools/       # 用户自定义工具
│
├── webui/                # React 前端
│   ├── src/
│   └── package.json
│
├── souls/                # Agent 人格模板
│   ├── soul.md           # 英文模板
│   └── soul_zh.md        # 中文模板
│
├── workspace/            # Agent 工作空间
├── memory/               # 记忆存储
├── python/               # Python 辅助脚本
│
├── .env                  # 环境配置
├── .env.example          # 环境配置模板
├── requirements.txt      # Python 依赖
├── Dockerfile            # Docker 镜像定义
├── docker-compose.yml    # Docker Compose 配置
├── reverie.sh            # Docker 管理脚本
├── start.sh              # 快速启动脚本
└── USAGE.md              # 本文档
```

---

## 常见问题

### Q: 启动时报错 `Missing OPENAI_API_KEY`

**A**: 确保在 `.env` 文件中正确配置了 `OPENAI_API_KEY`，或在运行命令时通过参数传入：

```bash
python -m reverie.cli --api-key sk-your-key ...
```

### Q: Docker 启动失败，端口被占用

**A**: 检查端口是否被占用，或修改 `docker-compose.yml` 中的端口映射：

```bash
# 检查端口占用
netstat -ano | findstr :8000
netstat -ano | findstr :5173

# 修改 docker-compose.yml 中的端口后重新启动
```

### Q: 如何切换模型？

**A**: 有两种方式：

1. 修改 `.env` 文件中的 `REVERIE_MODEL`
2. 运行命令时指定：`--model gpt-4o`

### Q: 如何让 Agent 使用中文？

**A**: 确保 `.env` 中配置了中文人格模板，或在启动时指定：

```bash
python -m reverie.cli ... --soul-template souls/soul_zh.md
```

### Q: 记忆保存在哪里？

**A**: 默认保存在 `memory/` 目录下，以 Markdown 文件形式存储。每次会话结束后会自动持久化。

### Q: 如何清理记忆重新开始？

**A**:

```bash
# 方式 1: 删除特定会话的记忆
rm -rf memory/<session_id>*

# 方式 2: 清理全部记忆
rm -rf memory/*

# 方式 3: 使用新 session ID
python -m reverie.cli --session-id new-session ...
```

### Q: WebUI 无法连接后端？

**A**: 确保后端已启动且 API 服务启用：

```bash
# 检查后端是否运行
curl http://localhost:8000/health

# 确保 REVERIE_ENABLE_API=1
```

### Q: 如何自定义 Agent 的工具？

**A**: 参考 `reverie/user_tools/` 目录，添加自定义 Python 函数即可。

---

## 获取帮助

- 📖 项目文档：[README_zh.md](./README_zh.md)
- 🐛 问题反馈：GitHub Issues
- 💬 讨论区：GitHub Discussions

---

*最后更新：2026-05-02*
