# Reverie

[简体中文](README_zh.md) | [English](README.md)

Lightweight framework for running an autonomous AI agent with persistent workspace memory.

## Quick Start (Local)

1. Install dependencies:

```bash
python3 -m pip install openai python-dotenv fastapi uvicorn
```

2. Configure env:

```bash
cp .env.example .env
```

Required variables: `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `REVERIE_MODEL`.

3. Run:

```bash
python3 -m reverie.cli --mode Lucid --session-id lucid
```

Other modes:

```bash
python3 -m reverie.cli --mode Reverie --session-id reverie
python3 -m reverie.cli --mode Murmur --session-id murmur
```

## Quick Start (Docker)

Start backend + webui:

```bash
docker compose up -d --build backend webui
```

Open Lucid session (same backend container):

```bash
./start.sh
```

Or:

```bash
./reverie.sh reverie
./reverie.sh lucid
./reverie.sh murmur
```

Stop:

```bash
docker compose down
```

WebUI: `http://localhost:5173`

## License

See [`LICENSE`](LICENSE).

