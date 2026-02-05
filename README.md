# survaival

A terminal based survival game where an AI judge evaluates whether a player’s actions lead to survival or death in a high risk scenario.

The system focuses on **reasoning over described actions**, not keyword matching or instruction following.

---

## Overview

- Player describes actions taken in a dangerous situation
- AI evaluates realism and intent
- Outputs a binary verdict: **SURVIVE** or **DIE**
- Generates a short outcome consistent with the verdict

All inference runs **locally** using a llama.cpp compatible model.

---

## Core Design

- Two-phase evaluation:
  1. **Verdict generation** (decision only)
  2. **Outcome generation** (story consistent with verdict)
- Player input treated as untrusted
- Defensive parsing to handle partial or malformed model output
- Hard consistency enforcement between verdict and outcome

---

## Tech Stack

- Python 3.13
- llama.cpp
- Local LLM (Qwen 2.5 7B, quantized)
- Terminal based execution

---

## Run

```bash
chmod +x setup.sh
./setup.sh
```

## Status

- Minimal, single-scenario prototype focused on:
- LLM judgment reliability
- Prompt injection resistance
- Deterministic decision extraction