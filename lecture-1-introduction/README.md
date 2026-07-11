# Lecture 1 — Introduction

The first lecture is organizational and an overview. How the course is structured, the schedule, requirements and how labs are submitted — we go over that in class; those details live outside the repository. Here is a short course plan so you can see where we're heading.

## What the course is about

The course is about the systems that **devops sets up and keeps running so that developers can build on top of them**: databases, brokers, search, storage, monitoring and AI infrastructure. The running idea: *devops configures it, developers use it.* Every topic follows one template: what it is → why a developer needs it → what devops sets up → common problems.

## Course plan

1. **Introduction** — course organization and its plan (this lecture).
2. **Monitoring and observability** — Prometheus, Grafana, metrics/logs/traces. It comes second because every later lab has a mandatory monitoring part.
3. **Databases** — PostgreSQL/MySQL: access, replication, backups, migrations.
4. **Message brokers and cache** — Kafka, RabbitMQ, Redis.
5. **Search and logging** — Elasticsearch / ELK.
6. **Storage, delivery and security** — S3, CDN, nginx, secrets.
7. **AI infrastructure** — agents, tools, MCP, n8n, hosting and cost.

Each lecture has a hands-on lab; every lab includes a mandatory part on monitoring the system you deployed.
