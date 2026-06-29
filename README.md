# Administration of Information and Communication Technologies

> 🌐 **Language:** English (branch `main`) · [Русская версия → branch `main-rus`](https://github.com/KeladKaal/ict-administration/tree/main-rus)

A hands-on course for people starting out in devops.

We look at the systems a devops engineer sets up and keeps running so that developers can build on top of them — databases, message brokers, search, storage, monitoring, and more. The idea is simple: **devops configures it, developers use it.** By the end you'll understand what these systems are, why developers need them, and what it takes to run them well (access, backups, monitoring, and the problems that come up).

No deep prior knowledge needed — just basic command line and Docker.

## Lectures

Seven lectures, 1.5 hours each. Every lecture has three short blocks (~25–30 min). Click a lecture to see what's inside.

1. [Introduction, the devops role, GitLab + CI/CD](lecture-1-introduction/) — what the course is about and how code gets to production
2. [Databases](lecture-2-databases/) — PostgreSQL/MySQL: access, replication, backups, migrations
3. [Message brokers and cache](lecture-3-brokers-cache/) — Kafka, RabbitMQ, Redis
4. [Search and logging](lecture-4-search-logging/) — Elasticsearch / ELK
5. [Storage, delivery and security](lecture-5-storage-delivery-security/) — S3, CDN, nginx, secrets
6. [Monitoring and observability](lecture-6-monitoring-observability/) — Prometheus, Grafana, metrics/logs/traces
7. [AI infrastructure](lecture-7-ai-infrastructure/) — n8n, agents, MCP, vector databases

## How this repo is organized

- One folder per lecture, each with a short README describing its three blocks.
- **`main`** — everything in **English**. **`main-rus`** — the same in **Russian**.
- Anything pushed here is mirrored in both languages: English → `main`, Russian → `main-rus`.

## License

© 2026 KeladKaal. Licensed under [CC BY-NC 4.0](LICENSE). Reuse and adapt freely for **non-commercial** purposes, with **credit** to the author.
