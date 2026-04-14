# Reverie

[简体中文](README_zh.md) | [English](README.md)

一个轻量框架，用于运行具备持续记忆与自主循环能力的 AI Agent。

## 本地快速启动

1. 安装依赖：

```bash
python3 -m pip install openai python-dotenv fastapi uvicorn
```

2. 配置环境变量：

```bash
cp .env.example .env
```

至少填写：`OPENAI_API_KEY`、`OPENAI_BASE_URL`、`REVERIE_MODEL`。

3. 启动：

```bash
python3 -m reverie.cli --mode Lucid --session-id lucid
```

其他模式：

```bash
python3 -m reverie.cli --mode Reverie --session-id reverie
python3 -m reverie.cli --mode Murmur --session-id murmur
```

## Docker 快速启动

启动 backend + webui：

```bash
docker compose up -d --build backend webui
```

进入 Lucid 会话（同一 backend 容器）：

```bash
./start.sh
```

或使用脚本：

```bash
./reverie.sh reverie
./reverie.sh lucid
./reverie.sh murmur
```

停止：

```bash
docker compose down
```

WebUI 地址：`http://localhost:5173`

## 许可证

见 [`LICENSE`](LICENSE)。

