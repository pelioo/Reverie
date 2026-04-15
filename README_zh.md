# Reverie

[简体中文](README_zh.md) | [English](README.md)

**Reverie 是一个面向自进化的 Agent 运行框架**：无人询问时持续探索成长；有人提问时基于当前成长状态进行响应。

https://github.com/user-attachments/assets/e77ee847-89f6-4552-a5f7-3dbea8351754

## 为什么是 Reverie

多数 Agent 依赖“人类持续提问”来驱动。

Reverie 的核心创新是：**潜意识生成（subconscious generation）**。

- 不再完全依赖外部输入，而是生成内部冲动与目标。
- 持续写入记忆，让上下文随时间复利增长。
- 可在“自主成长”和“交互回复”之间自由切换。

这使 Reverie 非常适合：**长周期自治实验**、**记忆驱动智能研究**、**自导演化 Agent 探索**。

## 三种核心模式

### 1) Reverie 模式（自主成长）

无人值守运行。Agent 持续探索、规划、调用工具并更新记忆。

### 2) Lucid 模式（交互回复）

用户提问时，Agent 基于当前累积的记忆与状态进行回答。

### 3) Murmur 模式（混合状态）

融合两种状态：既能自主漂移成长，也能随时接管交互。

## 与常见 Agent 框架的差异

- **潜意识优先循环**：以内部意图生成替代纯 Prompt 触发。
- **持久化记忆栈**：跨会话保留状态，避免“每次从零开始”。
- **工具原生执行**：搜索、文件 I/O、命令执行、记忆操作一体化。
- **可观测性友好**：提供 API 与 WebUI 观察运行过程。

## 架构速览

- `reverie/subconscious/`：潜意识提示与状态塑形
- `reverie/memory/`：记忆类型、评分与持久化
- `reverie/scheduler/`：自治轮次调度与队列
- `reverie/orchestrator/`：规划、工具循环与执行编排
- `reverie/api/`：FastAPI 服务与运行态读取
- `webui/`：活动流与记忆可视化

## 本地快速启动

1. 安装依赖

```bash
python3 -m pip install openai python-dotenv fastapi uvicorn
```

2. 配置环境变量

```bash
cp .env.example .env
```

最少填写：

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `REVERIE_MODEL`

3. 按模式启动

```bash
python3 -m reverie.cli --mode Reverie --session-id reverie
python3 -m reverie.cli --mode Lucid --session-id lucid
python3 -m reverie.cli --mode Murmur --session-id murmur
```

## Docker 快速启动

启动 backend + webui：

```bash
docker compose up -d --build backend webui
```

直接启动并进入 Lucid 会话：

```bash
./start.sh
```

或按模式执行：

```bash
./reverie.sh reverie
./reverie.sh lucid
./reverie.sh murmur
```

常用运维命令：

```bash
./reverie.sh logs
./reverie.sh down
```

WebUI：`http://localhost:5173`  
API 健康检查：`http://localhost:8000/health`

## 典型使用场景

- 持续产出想法与实验结果的自治研究伙伴
- 能跨天累积上下文的工程开发助理
- 研究长时运行 Agent 涌现行为的沙盒平台
- “常驻在线个人 AI” 的原型基础设施

## 路线图

- 更强的长期记忆检索与整合机制
- 潜意识意图生成的质量约束与评估
- 多 Agent 协作与共享记忆空间
- 更完善的可观测性与基准评测体系

## 如果这个方向打动你

如果你认同“**先成长，再回答**”的 Agent 形态，请给 Reverie 一个 Star。

这会直接帮助项目吸引更多贡献者，加速自进化 Agent 的开源探索。

## 许可证

见 [`LICENSE`](LICENSE)。
