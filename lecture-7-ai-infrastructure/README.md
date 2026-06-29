# Lecture 7 — AI infrastructure

The new set of tools devops sets up for teams: agents, how to host them, and how to keep costs under control.

**Block 1 — Agents: toolkit, skills, MCP.** Why devops shows up in AI at all. What an agent is (LLM + tools + a loop). Tool/function calling as the foundation. MCP (Model Context Protocol) for giving agents access to systems and data — and devops running the MCP servers. Skills/toolkits as reusable capability sets.

**Block 2 — n8n and GPU.** n8n: self-hosted workflow automation (nodes, triggers, the no-code scenario) and how devops hosts it for teams. Cloud vs self-hosted models — when to pick which (privacy, latency, control, cost). Self-hosted serving: Ollama (dev) vs vLLM/TGI (production). GPU infrastructure: why AI needs GPUs and why they're expensive.

**Block 3 — Rate limits and money.** API keys: handing out and revoking access. Rate limits and per-team quotas — protection against burning everything by accident. An LLM proxy/gateway (LiteLLM) as a single entry point to count tokens and cut access. Money: how tokens are counted, why costs spike, basic budget control.
