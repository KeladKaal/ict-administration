# Lecture 7 — AI infrastructure

The newest layer devops sets up for teams: agents, the tools they use, automation, and the cost of it all. The lecture has two halves with a break in between — first *what it is and how it works*, then *where it runs and what it costs*.

## Plan

### 1. Warm-up: where are you with AI? (discussion)

Questions to the group:
- Have you tried hosting your own model?
- Do you only use chat, or build something more complex?
- Do you use AI in your IDE?
- Where in devops processes do you think AI could be plugged in?

### 2. AI chatbot

- **Definition:** a program that holds a natural-language dialogue — on each request the model generates a text answer, relying only on what it learned during training.
- **The point:** it answers but doesn't act; no external tools.
- **Example:** ask "how do I restart a service?" → it gives you the command, you run it yourself.

### 3. AI agent

- **vs chatbot:** an agent *acts*, not just answers. Key boundary — it has tools and autonomy.
- **Definition (Sber's three criteria):** planning, execution via tools to interact with the outside world, and autonomy (acting without approving every step).
- Technically: LLM + tools + a loop.

### 4. Tools and skills

- **Tool** = one action. Two parts: a **description** (text the model sees) + a **handler** (what actually runs the call — usually code).
- **Skill** = packaged know-how: *how* to do a task — in what order and by what rules. May include its own tools.
- Important: tool = *what* the agent can do; skill = *how* it does the task.

### 5. Toolkit

- A ready-made **bundle of tools** around one system or task, plugged into the agent as a whole.
- Saves you from wiring tools one by one.
- **Example:** a GitHub toolkit — `create_issue`, `open_pull_request`, `list_commits`, `add_comment`.

### 6. MCP and MCP servers

- **MCP (Model Context Protocol)** — an open standard for connecting AI models to external tools and data. Analogy: "USB-C for AI".
- **MCP server** — a service that exposes tools and data access over this standard. Behind it is real code that talks to the system.
- Can be **local** (a process next to the app) or **remote** (a networked service). The remote ones are what **devops** deploys and controls.

### 7. Automation platforms

- Once you have tools and skills, you need to **wire them into a process**.
- Two paths: **build it yourself** (code) vs **use a ready-made workflow-automation platform** (often no-code).
- **Examples:** n8n (self-hosted), Zapier, Make (cloud, simple), Dify, Flowise (AI/agent-focused).

### 8. n8n

- A visual, mostly **no-code workflow automation** platform that you can **self-host**.
- **Concepts:** workflow (the scenario), node (a step: trigger / action / logic), trigger (what starts it), execution (one run).
- Has **AI and agent nodes** → mixes AI and non-AI steps in one process. **devops** hosts it for teams and guards the connected credentials.

### 9. Hosting and money *(after the break)*

- **Self-hosted vs cloud** — the main fork: run the model yourself or call a provider's API.
- **Self-hosted — pros:** data stays in-house, full control, no vendor lock-in, cheaper at large volumes. **Cons:** needs GPUs (expensive), hard to run and maintain, you own uptime, weaker models than top cloud ones.
- **Cloud — pros:** fast start, top models, scales itself, pay-as-you-go. **Cons:** data leaves to a provider, vendor lock-in, costs grow with volume, you depend on provider limits.
- **GPU:** your own model needs GPUs — they're expensive, scarce, and burn money even when idle.
- **AI gateway:** a single entry point to the models — counts tokens and cost, controls access, can balance requests.

## Lab

[Lab 7 — Automating a DevOps process with n8n + AI](lab.md): design a real automation use-case and build it in n8n with MCP servers, an AI toolkit and skills, then run it locally.
