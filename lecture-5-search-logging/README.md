# Lecture 5 — Search and logging (Elasticsearch)

Elasticsearch is a distributed search and analytics engine built on the Apache Lucene library. In infrastructure it covers two jobs: full-text search inside products, and centralized collection and analysis of logs. This README is a self-contained summary — the material is laid out so you can learn it without the lecture. Structure: purpose and use cases → terminology → statuses and operations.

---

## Part 1 — Purpose and use cases

### Limitations of a relational DB

Relational databases are a poor fit for two classes of task:

1. **Full-text search.** `LIKE '%...%'` doesn't use indexes efficiently, ignores morphology, typos and relevance; on large volumes it runs in linear time.
2. **Analytics over large volumes.** Aggregations (counts, percentiles, top-N) over millions of rows require full scans and run slowly.

Application scenarios where this is critical:

- catalog search: millions of products, queries with typos, ranking by relevance;
- incident triage from logs: searching by `trace_id` and a time range across the logs of dozens of services;
- operational analytics: number of 5xx errors per service over a period, the slowest endpoints.

### How Elasticsearch solves these

- **Inverted index.** For each term it stores the list of documents where the term occurs. Text search runs against the index rather than by scanning.
- **Analyzers.** At index time text is split into terms and normalized (lowercasing, stemming). This enables search by word form and tolerance to typos (fuzzy search).
- **Relevance ranking.** Results are ordered by how well they match the query (the BM25 algorithm).
- **Aggregations engine.** Counts, percentiles, top-N run in near real-time; dashboards in Kibana are built on top of them.

Core principle: the heavy lifting happens at index time (writes), which makes queries (reads) fast.

### Definition

> **Elasticsearch** — a distributed search and analytics engine built on Apache Lucene, providing full-text search and aggregations over large volumes of data in near real-time.

### The ELK stack

For logging, Elasticsearch is used as part of the ELK stack:

> **ELK = Elasticsearch + Logstash + Kibana**; complemented by **Beats** agents.

Processing pipeline: **services → Filebeat / Logstash (collection and processing) → Elasticsearch (storage and indexing) → Kibana (search and visualization)**.

- **Elasticsearch** — storage and search.
- **Logstash** — collection and processing of data (parsing, filtering, enrichment). **Beats** (in particular Filebeat) — lightweight agents on hosts that ship data.
- **Kibana** — web interface for search and dashboards.

Setting up centralized logging means setting up this whole pipeline. This is the main use case for Elasticsearch from the DevOps side.

### Elasticsearch vs a relational DB

Elasticsearch is not a replacement for the primary database and is not used as the source of truth. Key differences:

- no multi-document transactions (ACID);
- no joins (`JOIN`); the data model is denormalized;
- visibility model is near real-time: a document becomes searchable not instantly (default refresh interval ≈ 1 s);
- data is indexed from the primary DB; if an index is lost, it is restored by re-indexing.

| | Relational DB | Elasticsearch |
|---|---|---|
| Purpose | Storing data, transactions | Search and analytics |
| Role in the system | Source of truth | Derived store |
| Transactions (ACID) | Yes | No (atomicity only per single document) |
| Joins (JOIN) | Yes | No (denormalized model) |
| Write visibility | Immediately after commit | Near real-time (≈ 1 s) |
| Data loss | Unrecoverable | Recoverable by re-indexing from the DB |

In a production system the DB and Elasticsearch are used together: the DB is the system of record (source of truth), Elasticsearch is a derived store for search and analytics.

### OpenSearch

OpenSearch is a fork of Elasticsearch and Kibana, created by AWS in 2021. Reason: in 2021 Elastic changed the license of Elasticsearch and Kibana from Apache 2.0 to SSPL / Elastic License, which are not formally OSI open-source (the change was aimed primarily at cloud providers). AWS took the last Apache-2.0 version and forked it; components were renamed: Elasticsearch → OpenSearch, Kibana → OpenSearch Dashboards. The project stays on Apache 2.0 and is governed by the OpenSearch Software Foundation (Linux Foundation).

For search and logging OpenSearch and Elasticsearch are functionally close; the choice is usually driven by license and cloud platform (AWS OpenSearch Service vs Elastic Cloud), not features. Over time their APIs gradually diverge.

---

## Part 2 — Terminology: indices, shards, replicas

**Document** — the unit of storage, a JSON object.
- 🛒 a product: `{"name": "Adidas sneakers", "price": 7990, "size": 42}`
- 📋 a log entry: `{"timestamp": "2026-06-30T03:14:00Z", "level": "ERROR", "service": "checkout", "trace_id": "abc123"}`

**Index** — a named collection of documents with a similar structure; functionally analogous to a table.
- 🛒 index `products` — all products
- 📋 index `logs-2026.06.30` — logs for one day

**Mapping** — the schema of an index: the list of fields and their types. Determines how fields are indexed and searched; the type of an existing field cannot be changed without re-indexing.
- 🛒 `price` — number, `name` — text (analyzed), `size` — number
- 📋 `timestamp` — date, `level` — keyword, `message` — text

**Shard** — a self-contained part of an index that holds a subset of its documents and can live on a separate node. A whole index may not fit on a single server, so it is split into shards. Each shard is a full mini-index: it can be searched on its own, and Elasticsearch merges results from all shards (under the hood a shard is a separate Lucene index). Splitting into shards provides horizontal scaling.
- 🛒 an index of 50M products split into 5 shards across nodes
- 📋 a day's log index is too big for one node → split into shards

**Replica** — a copy of a primary shard that Elasticsearch keeps on another node and automatically keeps in sync. Each shard has a "primary" and its replicas — the same data in several copies. Needed for two things: **fault tolerance** (if the node with the primary fails, a replica is promoted to primary and no data is lost) and **read throughput** (searches can be served from replicas too, so more replicas = more parallel reads). Writes go to the primary first, then are copied to the replicas. By default there is one replica per shard, and it is never placed on the same node as its primary (otherwise it would be pointless).
- 🛒 a copy of the products shard on another node — catalog search survives a node failure
- 📋 a copy of the logs shard — logs stay available if a node goes down

**Node** — an Elasticsearch instance. **Cluster** — a set of nodes. Shard distribution is automatic; a replica is not placed on the same node as its primary shard.
- 🛒 + 📋 a 3-node cluster holds both the `products` index and the log indices, distributing their shards across nodes

Summary: shards are responsible for scaling, replicas for fault tolerance and read throughput.

---

## Part 3 — Statuses and operations

### Cluster state

- **green** — all primary shards and replicas are allocated;
- **yellow** — all primary shards are allocated, some replicas are not; data is available, fault tolerance is reduced;
- **red** — at least one primary shard is not allocated; some data is unavailable.

Examples: 🔴 red on the `products` index — part of the catalog isn't found, users see incomplete results; 🟡 yellow on the `logs-2026.06.30` index — the log data is intact but replicas haven't been allocated.

### Common problems

- **Unassigned shards** — shards are not allocated. Causes: node failure, lack of disk space, no suitable node for a replica. A common cause of yellow and red statuses.
- **Disk filling up.** When thresholds (disk watermark) are reached, the cluster limits shard allocation; at flood-stage (95% by default) indices are switched to read-only and writes stop. The most frequent operational incident. 📋 It's usually logs that fill the disk — and then *all* indices go read-only, including 🛒 `products`, so writing products stops too.
- **Oversharding** — an excessive number of small shards increases overhead and memory consumption. 📋 The classic source is logs: an index per day × a year × several shards adds up to thousands of small shards. 🛒 Less often — a separate index per small product subcategory.
- **JVM heap.** Heavy aggregations increase heap usage up to OutOfMemory. Recommendations: heap ≤ 50% of RAM and no more than ≈ 32 GB. Examples of heavy queries: 🛒 a faceted aggregation over the whole catalog, 📋 "top errors across all services for the month".

### ILM (Index Lifecycle Management)

**The problem.** Logs accumulate endlessly. Typically an index is created per period (for example, `logs-2026.06.30` — one per day). Without management this quickly grows into thousands of indices and a full disk.

**What ILM does.** It is a policy that **automatically moves an index through life stages as it ages** and deletes it at the end. Four phases:

- **Hot** — the index is actively written and frequently read (fresh logs). Kept on fast hardware.
- **Warm** — writes stopped, but data is still queried. The index is set read-only and moved to less powerful nodes to free resources.
- **Cold** — rarely queried, kept "just in case". Moved to the cheapest storage.
- **Delete** — the index is deleted once the retention period expires.

Transitions between phases are defined by conditions — by index age, size or document count. A typical logs policy: **hot today → warm after 7 days → delete after 30 days**.

Alongside is **rollover**: instead of one endlessly growing index, ILM creates a new one when the current reaches a threshold (for example, 50 GB or 1 day), and writes continue into the new one. This keeps indices at a manageable size.

Summary: 📋 for logs ILM is practically mandatory — without it the disk fills up (see read-only above). 🛒 Products don't age over time, so a catalog is usually not rotated and doesn't need ILM.

### Backups

Replicas do not replace backups: they don't protect against accidental deletion. The snapshot / restore mechanism is used, typically to object storage (S3). Both kinds of data are backed up: 🛒 a snapshot of the `products` index, 📋 snapshots of log indices.

### Monitoring

Key metrics: cluster state, free disk space, JVM heap usage, number of unassigned shards.

### Role split

- **Developer** — writes queries, analyzes logs, builds dashboards in Kibana.
- **DevOps** — deploys and maintains the cluster, monitoring, backups, access management, rotation setup (ILM).

---

## Key takeaways

- Elasticsearch — a distributed search and analytics engine built on Lucene; not a replacement for a DB but a derived store.
- Two classes of task: full-text search and aggregations over large volumes.
- Logging is implemented with the ELK stack (+ Beats).
- Data structure: document → index (mapping) → shards (scaling) + replicas (fault tolerance) → cluster.
- Operations: watch cluster state and disk; flood-stage switches indices to read-only; rotation via ILM; backups via snapshot/restore.

---

## Lab

[Lab 5 — Deploy ELK and get hands-on with Elasticsearch](lab.md): run Elasticsearch + Kibana locally, load logs, search and aggregate, work through shards/replicas/cluster status, and set up a minimal ILM + rollover.
