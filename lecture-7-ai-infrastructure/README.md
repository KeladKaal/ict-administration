# Lecture 7 — AI infrastructure

The newest layer devops sets up for teams: agents, the tools they use, automation, and the cost of it all.

This README is a **self-contained summary** — if you missed the lecture, you can learn the material here. It has two halves: first *what AI is made of and how processes are built from it*, then *where it runs and what it costs*.

---

## 0. Before you start — think about it

- Have you tried hosting your own model?
- Do you only use chat, or build something more complex?
- Do you use AI in your IDE?
- Where in devops processes do you think AI could be plugged in?

The whole lecture answers the last question: AI is now ordinary infrastructure — something a devops engineer deploys, gives access to, and pays for.

---

## 1. AI chatbot

> **AI chatbot** — a program that holds a natural-language dialogue: on each request the model generates a text answer, relying **only on what it learned during training**. It has no external tools and takes no actions — it answers, and a human does everything else.

- The point: a chatbot **answers but doesn't act**.
- **Example:** you ask "how do I restart a service?" → it gives you the command → *you* run it yourself.

---

## 2. AI agent

> **AI agent** — an automated system that meets three criteria *(Sber's definition)*:
> - **Planning** — understand the task and build a plan of action;
> - **Execution** — carry the actions out itself, using tools to interact with the outside world;
> - **Autonomy** — follow the plan without approving every step with a human.

Technically an agent is **LLM + tools + a loop**: the model decides which tool to call, sees the result, and continues until the task is done.

**Example:** you ask "find open pull requests in our repo and remind the authors" → the agent lists the open PRs, then comments on each one — it carries out a multi-step task on its own, not just answering.

**Chatbot vs agent:**

| | Chatbot | Agent |
|---|---|---|
| What it does | Answers questions | Completes whole tasks |
| Initiative | Waits for the next question | Plans the steps itself |
| Tools | None — only the model's knowledge | Yes — acts in the outside world |
| Autonomy | Every step is on the human | Acts without approving each step |

> **A chatbot tells you what to do. An agent does it.**

---

## 3. Tools and skills

> **AI tool** — a concrete action the agent can call to get information or affect the outside world. It has two parts: a **description** (text the model sees: what it does and what input it needs) and a **handler** (what actually executes the call — usually code).

The model itself does nothing in the world — it only decides *which tool to call*. The code around it does the work.

**Example — a `get_weather` tool:**
1. You ask: "should I take an umbrella in Moscow?"
2. The model decides to call `get_weather(Moscow)`
3. The code runs the call → returns "rain, +12"
4. The model answers: "yes, take an umbrella"

> **AI skill** — a reusable package of know-how: *how* to do a specific task — in what order to act and by what rules. A skill may include its own tools.

**Example — an "incident triage" skill:** "first check the metrics → find the anomaly in the logs → if the service is down, restart it → post a summary in the channel." It relies on tools, but adds the order and the rules.

**Tool vs skill:** a tool is *what* the agent can do; a skill is *how* it does a task well.

---

## 4. Toolkit

> **AI toolkit** — a ready-made **bundle of tools** built around one system or task, plugged into the agent as a whole.

Instead of wiring tools in one by one, you hand the agent a whole box.

**Example — a "GitHub" toolkit:** `create_issue` + `open_pull_request` + `list_commits` + `add_comment`. Give the agent this toolkit and it can work with GitHub as a whole.

**Toolkit vs MCP server (below):** a toolkit is *what* set of tools the agent is given; an MCP server is *how* those tools are delivered — as a standalone service over a standard protocol.

---

## 5. MCP and MCP servers

> **Model Context Protocol (MCP)** — an open standard for connecting AI models to external tools and data over a single protocol.

Analogy: **MCP is like USB-C for AI** — one connector instead of a custom cable for every system. Build a tool once to the standard, and any MCP-capable agent can use it.

> **MCP server** — a service that exposes tools and data access to an agent over the MCP standard. Inside it is real code that talks to the actual system (a database, an API, files).

- Can be **local** (a process running next to the app) or **remote** (a networked service).
- Created by: the services themselves (GitHub, Slack), the community, or **your own internal devops** for internal systems.
- **Examples:** a *GitHub MCP server* exposes the GitHub toolkit's tools (`create_issue`, `list_pull_requests`, …); a *filesystem MCP server* exposes `read_file`, `write_file`, `list_directory`. One server = one system, with several tools inside.
- **devops angle:** a remote MCP server is a real service — deploy it, update it, limit access. *Toolkit = what the agent was given; MCP server = where it's deployed and who controls it.*

**How the layers fit together:**

> **skill — how to act · tool — what to do · MCP server — where the tool comes from and how it reaches the real system.**

---

## 6. Automation platforms

Once you have tools and skills, you need to **wire them into a process**. Two paths:

- **Build it yourself** — code the orchestration (flexible, but slow to build and maintain).
- **Use a ready-made workflow-automation platform** — assemble the process from blocks, often with no code.

**Examples:**
- **No-code / low-code:** **n8n** (self-hosted), **Zapier**, **Make** (cloud, simple)
- **AI/agent-focused:** **Dify**, **Flowise**

We use **n8n** because it's no-code yet self-hostable and close to devops.

---

## 7. n8n

> **n8n** — a workflow-automation platform: a visual builder where you assemble a process from blocks ("when X happens → do Y → then Z"). Mostly no-code, and you can self-host it.

**Key concepts:**
- **Workflow** — the scenario (a chain of steps)
- **Node** — one step: a trigger, an action, or logic
- **Trigger** — what starts the workflow (a webhook, a schedule, an event)
- **Execution** — one run (you can see what worked and what failed)

**Example process:** an incoming request email *(trigger)* → AI parses the text *(AI node)* → a Jira ticket is created *(action)* → a Slack notification is sent *(action)*. Note it mixes AI and non-AI steps.

**devops angle:** n8n has **AI and agent nodes**, so an agent can be one of the steps. n8n is the "glue" that ties agents, AI and ordinary services into one process. devops self-hosts it, guards the connected credentials, and gives it to teams.

---

## 8. Hosting and money *(after the break)*

### Self-hosted vs cloud — the main fork

Where does the model "live"? Either you **call a provider's API** (cloud) or **run the model yourself** (self-hosted). There's no universal answer — it's a trade-off.

**Self-hosted**
- ✅ Data stays in-house · full control · no vendor lock-in · cheaper at large volumes
- ❌ Needs GPUs (expensive) · hard to run and maintain · you own uptime and scaling · models usually weaker than top cloud ones

**Cloud**
- ✅ Fast start · top models · scales itself · pay-as-you-go
- ❌ Data leaves to a provider · vendor lock-in · gets pricier as volume grows (you pay per token) · you depend on provider limits and availability

### GPU

Models run on **GPUs**, not ordinary servers — so your own model needs GPUs. They're **expensive**, often **scarce**, and **burn money even when idle**. So "host your own" is, first of all, a money decision.

### AI gateway

> **AI gateway (proxy)** — a single entry point to the models for all teams.

- **Counts tokens and cost** — you can see who spent how much
- **Controls access** — keys, rate limits, can cut someone off
- Can **balance** requests across models/providers

> **Tokens** ≈ chunks of text. You pay per token — the more text you send and receive, the more it costs. Costs creep up quietly, then the bill arrives large.

---

## Lab

[Lab 7 — Automating a DevOps process with n8n + AI](lab.md): design a real automation use-case and build it in n8n with MCP servers, an AI toolkit and skills, then run it locally.
