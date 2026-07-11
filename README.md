# Administration of Information and Communication Technologies

> 🌐 **Language:** English (branch `main`) · [Русская версия → branch `main-rus`](https://github.com/KeladKaal/ict-administration/tree/main-rus)

A hands-on course for people starting out in devops.

We look at the systems a devops engineer sets up and keeps running so that developers can build on top of them — databases, message brokers, search, storage, monitoring, and more. The idea is simple: **devops configures it, developers use it.** By the end you'll understand what these systems are, why developers need them, and what it takes to run them well (access, backups, monitoring, and the problems that come up).

No deep prior knowledge needed — just basic command line and Docker.

## Lectures

Seven lectures, 1.5 hours each. Every lecture has three short blocks (~25–30 min). Click a lecture to see what's inside.

1. [Introduction, the devops role, GitLab + CI/CD](lecture-1-introduction/) — what the course is about and how code gets to production
2. [Monitoring and observability](lecture-2-monitoring-observability/) — Prometheus, Grafana, metrics/logs/traces
3. [Databases](lecture-3-databases/) — PostgreSQL/MySQL: access, replication, backups, migrations
4. [Message brokers and cache](lecture-4-brokers-cache/) — Kafka, RabbitMQ, Redis
5. [Search and logging](lecture-5-search-logging/) — Elasticsearch / ELK
6. [Storage, delivery and security](lecture-6-storage-delivery-security/) — S3, CDN, nginx, secrets
7. [AI infrastructure](lecture-7-ai-infrastructure/) — agents, tools, MCP, n8n, hosting and cost

## Labs

You can run the infrastructure in the labs (databases, clusters, services) **however you prefer** — locally via Docker / `docker compose`, or in Kubernetes. The choice is yours and is not spelled out in each lab. What matters is that it runs locally and you can show it works.

**Mandatory in every lab — monitoring.** Every lab requires setting up monitoring for the system you deployed and picking **3 key graphs (metrics)** you'd realistically build alerts on — with an explanation of why those three. Monitoring is covered in lecture 2, so from there on it runs as a cross-cutting theme in every lab.

## Using AI for the labs

Using an AI assistant is allowed and encouraged — but this repo is set up so it **helps you learn instead of handing you finished answers**: it works step by step, explains the reasoning, and checks your understanding before moving on.

The rules live in [`AGENTS.md`](AGENTS.md) (and `CLAUDE.md` for Claude Code). Most AI tools pick these up automatically. **If yours doesn't, just point it at [`AGENTS.md`](AGENTS.md)** and ask it to follow the file.

## How this repo is organized

- One folder per lecture, each with a short README describing its blocks.
- **`main`** — everything in **English**. **`main-rus`** — the same in **Russian**.
- Anything pushed here is mirrored in both languages: English → `main`, Russian → `main-rus`.

## License

© 2026 KeladKaal. Licensed under [CC BY-NC 4.0](LICENSE). Reuse and adapt freely for **non-commercial** purposes, with **credit** to the author.
