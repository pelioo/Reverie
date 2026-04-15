# Reverie

[简体中文](README_zh.md) | [English](README.md)

**Reverie is an agent runtime for self-evolution**: when nobody asks, it keeps exploring and growing; when asked, it answers from its current growth state.

https://github.com/user-attachments/assets/e77ee847-89f6-4552-a5f7-3dbea8351754

## Why Reverie

Most agents wait for human prompts.

Reverie introduces a different primitive: **subconscious generation**.

- It synthesizes internal impulses/goals instead of depending on continuous human input.
- It writes memory continuously and compounds context over time.
- It can be switched between autonomous growth and interactive response.

This makes Reverie suitable for experiments in **long-horizon autonomous behavior**, **memory-driven intelligence**, and **self-directed agent research**.

## Core Modes

### 1) Reverie Mode (autonomous growth)

Runs unattended. The agent continuously explores, plans, executes tools, and updates memory.

### 2) Lucid Mode (interactive response)

When the user asks a question, the agent responds based on the memory/state accumulated so far.

### 3) Murmur Mode (hybrid)

Blends both worlds: autonomous drifting + user-driven interaction.

## What makes it different

- **Subconscious-first loop**: replaces prompt-only triggering with internally generated intent.
- **Persistent memory stack**: keeps state across sessions and decisions.
- **Tool-native execution**: search, file I/O, command execution, memory operations.
- **Built for observability**: API + WebUI to inspect runtime state.

## Architecture at a glance

- `reverie/subconscious/`: subconscious prompting and state shaping
- `reverie/memory/`: memory types, scoring, persistence
- `reverie/scheduler/`: autonomous turn scheduling and queueing
- `reverie/orchestrator/`: planning, tool loops, execution flow
- `reverie/api/`: FastAPI services for dashboard/runtime access
- `webui/`: visualization interface for activity and memory

## Quick Start (Local)

1. Install dependencies

```bash
python3 -m pip install openai python-dotenv fastapi uvicorn
```

2. Configure env

```bash
cp .env.example .env
```

Minimum required variables:

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `REVERIE_MODEL`

3. Run by mode

```bash
python3 -m reverie.cli --mode Reverie --session-id reverie
python3 -m reverie.cli --mode Lucid --session-id lucid
python3 -m reverie.cli --mode Murmur --session-id murmur
```

## Quick Start (Docker)

Start backend + webui:

```bash
docker compose up -d --build backend webui
```

Start and enter Lucid session directly:

```bash
./start.sh
```

Or use mode commands:

```bash
./reverie.sh reverie
./reverie.sh lucid
./reverie.sh murmur
```

Useful operations:

```bash
./reverie.sh logs
./reverie.sh down
```

WebUI: `http://localhost:5173`  
API Health: `http://localhost:8000/health`

## Use Cases

- Autonomous research companion that keeps generating and refining ideas
- Persistent coding assistant that accumulates project context
- Sandbox for studying emergent behavior in long-running agents
- Prototype platform for “always-on” personal AI systems

## Roadmap

- Stronger long-term memory retrieval and consolidation
- Better subconscious intent quality controls
- Multi-agent collaboration and shared memory spaces
- Richer observability and evaluation benchmarks

## Star This Project

If the idea of agents that **grow before you ask** resonates with you, please give Reverie a star.

It helps the project attract contributors and accelerate research toward truly self-evolving agents.

## License

See [`LICENSE`](LICENSE).
