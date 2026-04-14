# Reverie

[简体中文](README_zh.md) | [English](README.md)

**一个开源框架，通过将空闲时间转化为自驱动进化循环，让 AI Agent 获得持续的数字生命。**

Reverie 是一个轻量级框架，用于构建不只是“等输入再响应”的 AI Agent。它让 Agent 能持续运行，在空闲时反思、积累记忆、建立稳定的“自我人格”，并通过自主行动逐步进化。

## 为什么是 Reverie

多数 AI 应用是一次请求一次回答。Reverie 的设计理念不同：

- **持续数字生命**：Agent 可跨会话保持“活着”的状态，而不是每次重置。
- **自驱进化**：把 idle time 变成反思、探索、整合和成长的机会。
- **轻量级优先**：基于文件的运行时状态、记忆和工具系统，基础设施要求低。
- **自我人格建立**：Agent 可以通过 [`soul.md`](workspace/memory/episodic/) 逐步形成并修订长期身份。

## 核心功能

- **自主循环**：无用户输入时可进入自驱动回合。
- **三种运行模式**：
  - `Reverie`：做梦模式（自主运行）
  - `Lucid`：对话模式（交互输入）
  - `Murmur`：混合模式（对话 + 自主）
- **持久化记忆**：记忆与运行产物以文件形式写入 [`workspace/`](workspace/)。
- **基于 Soul 的身份系统**：[`soul.md`](souls/soul.md) 会被注入提示，并可被 Agent 更新以塑造长期人格。
- **工具与工作区操作**：内置读写、搜索、记忆操作、命令执行、受控休息等能力。
- **容器化部署**：支持轻量本地或服务端持续运行。

## 快速开始

### 1. 安装依赖

```bash
python3 -m pip install openai python-dotenv
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

至少填写以下配置：

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `REVERIE_MODEL`

### 3. 本地运行

启动默认对话模式：

```bash
python3 -m reverie.cli --mode Lucid --session-id lucid
```

启动做梦模式：

```bash
python3 -m reverie.cli --mode Reverie --session-id reverie
```

启动混合模式：

```bash
python3 -m reverie.cli --mode Murmur --session-id murmur
```

## Docker 快速开始

后台启动做梦容器：

```bash
docker compose up -d reverie
```

在同一挂载工作区中开启对话会话：

```bash
docker compose exec reverie python3 -m reverie.cli --mode Lucid --session-id lucid
```

也可以使用脚本：

```bash
./start.sh
```

或按模式直接运行：

```bash
./reverie.sh reverie
./reverie.sh lucid
./reverie.sh murmur
```

## 运行目录

Reverie 保持轻量：运行数据默认写入 [`workspace/`](workspace/)：

- 记忆：[`workspace/memory/`](workspace/memory/)
- 会话状态：[`workspace/runtime/sessions/`](workspace/runtime/sessions/)
- 潜意识意图日志：[`workspace/runtime/subconscious_intents/`](workspace/runtime/subconscious_intents/)
- 工具结果：[`workspace/runtime/tool_results/`](workspace/runtime/tool_results/)

## 核心理念

Reverie 不只是一个聊天界面，而是对“模型内在持续性”的工程化实践：

- 可跨时间延续的记忆
- 可维护和演化的身份
- 对空闲时间的主动利用
- 通过循环实现渐进式自我进化

一句话：Reverie 把“空闲”变成 Agent 进化的燃料。

## 许可证

本项目采用 [`LICENSE`](LICENSE) 中声明的许可证。