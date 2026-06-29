# Lecture 4 — Search and logging

Elasticsearch powers both product search and centralized logs across all services.

**Block 1 — What it is and the data model.** Elasticsearch vs a database, indices/documents/mapping, shards and replicas.

**Block 2 — The ELK stack.** The log pipeline: Filebeat/Logstash → Elasticsearch → Kibana, plus ILM (rotating old logs so the disk doesn't fill up).

**Block 3 — Operations.** Cluster status (green/yellow/red), backups to S3, access and TLS, common problems (unassigned shards, full disk, oversharding).
