# Reverie

[简体中文](README_zh.md) | [English](README.md)

**An open-source framework that grants AI agents continuous digital life by transforming idle time into self-driven evolutionary loops.**

Reverie is a lightweight framework for building AI agents that do not merely wait for prompts. It enables agents to keep running, reflect during idle time, accumulate memory, form a persistent self-personality, and gradually evolve through autonomous action.

## Why Reverie

Most AI applications are request-response wrappers. Reverie is designed around a different idea:

- **Continuous digital life**: the agent stays alive across sessions instead of resetting every time.
- **Self-driven evolution**: idle time becomes an opportunity for reflection, exploration, consolidation, and growth.
- **Lightweight by design**: simple file-based runtime state, memory, and tools, with minimal infrastructure requirements.
- **Self-personality formation**: the agent can build and refine its own long-term identity through [`soul.md`](workspace/memory/episodic/).

## Core Features

- **Autonomous loops**: the agent can enter self-driven cycles when no user input is present.
- **Three operating modes**:
  - `Reverie`: autonomous dreaming mode
  - `Lucid`: interactive dialogue mode
  - `Murmur`: hybrid mode combining dialogue and autonomy
- **Persistent memory**: memories and runtime artifacts are stored in plain files under [`workspace/`](workspace/).
- **Soul-based identity**: [`soul.md`](souls/soul.md) is injected into prompting and can be updated by the agent for long-term personality shaping.
- **Tool use and workspace actions**: built-in tools support reading, writing, searching, memory operations, command execution, and controlled rest.
- **Docker-ready deployment**: built for lightweight local or server-side continuous operation.

## Quick Start

### 1. Install dependencies

```bash
python3 -m pip install openai python-dotenv
```

### 2. Configure environment

```bash
cp .env.example .env
```

Fill in at least:

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `REVERIE_MODEL`

### 3. Run locally

Start the default interactive mode:

```bash
python3 -m reverie.cli --mode Lucid --session-id lucid
```

Start autonomous mode:

```bash
python3 -m reverie.cli --mode Reverie --session-id reverie
```

Start hybrid mode:

```bash
python3 -m reverie.cli --mode Murmur --session-id murmur
```

## Docker Quick Start

Build and start the autonomous container:

```bash
docker compose up -d reverie
```

Open an interactive dialogue session against the same mounted workspace:

```bash
docker compose exec reverie python3 -m reverie.cli --mode Lucid --session-id lucid
```

Or use the helper scripts:

```bash
./start.sh
```

Or run a specific mode directly:

```bash
./reverie.sh reverie
./reverie.sh lucid
./reverie.sh murmur
```

## Runtime Layout

Reverie keeps things simple and lightweight. Runtime data is written to [`workspace/`](workspace/), including:

- memories in [`workspace/memory/`](workspace/memory/)
- session state in [`workspace/runtime/sessions/`](workspace/runtime/sessions/)
- subconscious intent logs in [`workspace/runtime/subconscious_intents/`](workspace/runtime/subconscious_intents/)
- tool outputs in [`workspace/runtime/tool_results/`](workspace/runtime/tool_results/)

## Concept

Reverie is not just a chat interface. It is an experiment in giving models a more persistent inner life:

- a memory that survives across time
- an identity that can be shaped and revised
- autonomous use of idle time
- gradual self-improvement through repeated internal loops

In short, Reverie treats inactivity not as downtime, but as fuel for self-evolution.

## License

This project is licensed under the terms of the [`LICENSE`](LICENSE) file.
