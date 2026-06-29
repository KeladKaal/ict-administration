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

Put everything in a folder named after your use-case and submit three things:

1. **`README.md`** — your use-case description (Part 1) and how to run it locally.
2. **The exported n8n workflow** (JSON).
3. **AI skills** — the documented know-how your agent follows (in what order it acts and by what rules).

---

## How to start

Open this repository with your AI assistant and ask it to help you with **Lab 7**. The assistant is set up to guide you **step by step** and check your understanding along the way — it won't hand you a finished solution, and that's on purpose. Start by describing your use-case idea and let it walk you through the rest.

> **Using AI?** Make sure your assistant follows the repo's rules in [`AGENTS.md`](../AGENTS.md). Most tools pick it up automatically; if yours doesn't, point it at that file and ask it to follow it.
