# Lab 7 — Automating a DevOps process with n8n + AI

## Goal

Come up with a **real use-case** where a devops engineer simplifies a process in a company, and implement it as an **n8n workflow that combines AI and non-AI steps**, talks to external systems through **MCP servers**, and uses an **AI agent with its own toolkit and skills**. Then run it locally and show it works.

This lab pulls together everything from the lecture: agents, tools, toolkit, skills, MCP servers, and n8n as the glue.

---

## Part 1 — Design your use-case

Pick a process that a devops engineer could automate to make life easier — either **for everyone in the company**, or **for one group** (e.g. developers, testers, support).

Write a short description (½ page is enough):
- **Who** it helps (all employees / a specific group).
- **What** problem it solves and why it's annoying today.
- **What** the automation does, end to end (trigger → steps → result).

> **Example (do not copy — invent your own):** an **alert-analysis assistant**. Trigger: an alert arrives from Alertmanager. The workflow then goes to **GitLab** (recent commits/MRs), **Prometheus** (the metric behind the alert) and **Kibana** (related logs), an AI step writes a human-readable analysis, and the result is saved as a **text file / message** for the on-call engineer.

Other directions to spark ideas: onboarding a new employee, triaging incoming bug reports, preparing a release summary, routing support tickets, generating a daily status digest.

---

## Part 2 — Implementation requirements

Your n8n workflow **must** include all of the following. Treat this as a checklist:

- [ ] **A trigger** that starts the workflow (webhook, schedule, incoming message, etc.).
- [ ] **Both AI and non-AI steps.** At least one step calls an AI model/agent; at least one step is plain logic or a plain service call (no AI).
- [ ] **At least two MCP servers** that give the agent access to external systems or data. You may use ready-made MCP servers (e.g. filesystem, GitHub) — you don't have to write them from scratch.
- [ ] **An AI toolkit with 3–5 tools.** For each tool document: its name, what it does, and what it takes as input.
- [ ] **Described skills.** Write down the skill(s) your agent follows — the know-how: in what order it acts and by what rules.
- [ ] **A concrete result** the workflow produces (a file, a message, a created ticket, etc.).

Simplifications are allowed for local running — see Part 3.

---

## Part 3 — Run it locally

You must run the whole thing locally and demonstrate it working end to end.

- Run **n8n locally** (Docker is fine).
- Connect your **MCP servers** and the **AI steps**.
- **Simplifications are OK:** you may use mock/test data instead of real production systems (e.g. a sample alert, a test repo, fake metrics), and a small/cheap model. The point is to show the *flow* works, not to run real infrastructure.
- Trigger the workflow and show it produces the expected result.

---

## What to submit

Put everything in a folder named after your use-case:

1. **`README.md`** — your use-case description (Part 1) + how to run it.
2. **The exported n8n workflow** (JSON) and a **screenshot** of the workflow on the canvas.
3. **MCP servers** — which two (or more) you used and what each gives the agent.
4. **AI toolkit** — the 3–5 tools (name / what / input).
5. **Skills** — the documented know-how your agent follows.
6. **Proof it runs** — screenshots of a successful run and the produced result (file/message). A short screen recording is welcome but optional.

---

## Evaluation criteria

| Criterion | What we look at |
|---|---|
| Use-case | Realistic, clearly described, clearly helps someone |
| Workflow | Has a trigger, runs end to end, mixes AI and non-AI steps |
| MCP servers | At least two, used meaningfully |
| Toolkit | 3–5 tools, each documented |
| Skills | Described — clear order and rules the agent follows |
| Local run | Demonstrated working with a real result |
| Understanding | You can explain *why* each part is there |

---

## How to start

Open this repository with your AI assistant and ask it to help you with **Lab 7**. The assistant is set up to guide you **step by step** and check your understanding along the way — it won't hand you a finished solution, and that's on purpose. Start by describing your use-case idea and let it walk you through the rest.
