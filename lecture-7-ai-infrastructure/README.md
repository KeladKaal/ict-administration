# Lecture 7 — AI infrastructure

The new layer devops sets up for teams. This lecture is split into two parts with a break in between.

## Part 1 — Processes

What modern AI is made of and how automated processes are built from it.

- **Agents and their building blocks.** Chatbot vs agent. What a tool is (description + handler). Toolkits as bundles of tools. Skills as packaged know-how. MCP (Model Context Protocol) and MCP servers as the standard way to expose tools and data — run by devops.
- **n8n.** Self-hosted, no-code workflow automation: how steps (including AI and agent steps) are wired into a working process, and how devops hosts it for teams.

## Part 2 — Administration and money

Where it all runs and what it costs — the pure devops view.

- **Hosting and GPU.** Cloud APIs vs self-hosted models, Ollama vs vLLM, why AI needs GPUs and why they're expensive.
- **Access and money.** API keys, rate limits and per-team quotas, an LLM proxy/gateway as a single entry point, how tokens are counted and why costs spike.

## Lab

[Lab 7 — Automating a DevOps process with n8n + AI](lab.md): design a real automation use-case and build it in n8n with MCP servers, an AI toolkit and skills, then run it locally.
