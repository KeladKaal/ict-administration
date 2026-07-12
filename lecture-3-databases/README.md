# Lecture 3 — Databases

The database is the heart of almost any application: orders, users and payments all live there. devops stands it up and takes care of it, while developers use it. A service can be restarted, but data can't — so everything around the database (access, replication, backups, monitoring) is on us.

This README works as a **self-contained summary**. Three parts: *relational databases*, *operations and problems*, *NoSQL and MongoDB*. Examples use the familiar **grocery delivery** app (orders and users in a relational DB, flexible data in MongoDB).

---

## Part 1 — Relational databases (PostgreSQL / MySQL)

### What a relational database is

> A **relational database** stores data in tables with a strict schema, linked to each other; queries are written in SQL.

Its main value is transactions with **ACID** guarantees: "charge the money and create the order — either both happen, or neither." Strict structure and integrity make a relational DB the classic **source of truth**. The main representatives are PostgreSQL and MySQL.

### Users and permissions

devops hands out access by the **principle of least privilege**: each service gets its own DB user with only the rights it needs (the orders service — on its own tables, analytics — read-only). No single "superuser for everything" — if one credential leaks, not everything is compromised.

### Connections and connection pooling

A DB has a limited number of simultaneous connections (`max_connections`), and each one costs memory. If every service instance opens its own connections, the limit runs out fast.

> **Connection pooling** (e.g. **PgBouncer**) is a layer that keeps a set of connections and reuses them, instead of opening a new one for every request.

The classic beginner incident — "out of connections" — is exactly the result of having no pool.

### The CAP theorem

As soon as data lives on several nodes (which is what replication and sharding give you), the **CAP theorem** kicks in: of the three properties of a distributed system, only two are achievable at once.

- **Consistency** — every node returns the same, most recent data;
- **Availability** — the system answers every request;
- **Partition tolerance** — it keeps working even if the network between nodes is broken.

A network partition is unavoidable in reality, so **P is mandatory** — and the real choice during a partition is always between **C and A**. Relational databases usually choose **C** (better an error than wrong data in an account), many NoSQL systems choose **A** (better to answer, even if the data lags a bit). You can see this in asynchronous replication below — it leans toward A.

### Replication

> **Replication** — copies of the database on other servers. The **primary** accepts writes, the **replicas** repeat them.

Why: **fault tolerance** (primary goes down — a replica is promoted to primary, this is **failover**) and **read scaling** (heavy SELECTs and analytics are moved to replicas so they don't disturb the main load).

- **synchronous** — the primary waits for the replica's acknowledgement: safer, but slower (leans toward C);
- **asynchronous** — it doesn't wait: faster, but the replica falls behind (**replication lag**) and may return stale data (leans toward A, see problems).

### Snapshots and backups

Don't confuse the two concepts:

- **Snapshot** — an instant copy of a volume/disk state: made quickly, but stored **next to** the database. Handy for a fast rollback, but it dies together with the server/storage.
- **Backup** — a separate copy of the data, kept **somewhere else** (another disk, S3): slower, but survives the loss of the server.

Types of backup:

- **Logical** (`pg_dump`) — a dump of the data as SQL.
- **Physical + PITR** (point-in-time recovery) — a copy of the files plus the WAL journal, lets you restore to any moment ("a second before the table was dropped").

The golden rule: **a backup you've never restored is not a backup**. Restores must be tested regularly.

### Schema migrations

> A **migration** is a versioned script that changes the DB structure (add a column, table, index) predictably and repeatably. It lives in the repo next to the code and is applied automatically on rollout.

A simple example migration — add a promo-code column to the orders table:

```sql
ALTER TABLE orders ADD COLUMN promo_code VARCHAR(20);
```

Tools — **Flyway, Liquibase, Alembic**. On a large, busy database even such a change is done carefully, following the **expand/contract** pattern, so the migration doesn't lock the table in production for long.

---

## Part 2 — Operations and problems

### What you monitor on a DB

- **connection count** — how close to the limit;
- **replica lag** (replication lag) — how fresh the data on the replica is;
- **slow queries** and overall load (QPS);
- **cache hit ratio**, disk space and **WAL** growth.

### Slow queries and indexes

The most common cause of slowness is a query **without an index**: the database scans the whole table.

> An **index** is an auxiliary structure (like a table of contents) that sharply speeds up lookups. The cost: it slows down writes and takes space — so you don't put an index on every column.

To see exactly what's slow, look at the query plan (`EXPLAIN`); the top slow queries in Postgres — via `pg_stat_statements`.

### Typical problems

- **Out of connections** — usually no pool or a connection leak.
- **Disk filled up** — WAL growth, undeleted old data, forgotten rotation.
- **Locks** — a long transaction holds rows, the rest wait in a queue.
- **Replica lag** — asynchronous replication couldn't keep up, and you read stale data from the replica.

All of this is caught by the monitoring from the previous section.

---

## Part 3 — NoSQL and MongoDB

### Why NoSQL

A relational DB handles strict, transactional data great, but sometimes it gets in the way: the schema changes often, records have different sets of fields, or there's so much data that you need horizontal scale across many servers.

> **NoSQL** — a family of databases without a rigid relational schema. Types: **document** (MongoDB), **key-value** (Redis), **column** (Cassandra), **graph** (Neo4j).

### MongoDB: what it is

> **MongoDB** — a document database: data is stored as **documents** (essentially JSON, binary BSON inside) in **collections**.

A rough analogy: a collection is like a table, a document like a row — but with a **flexible schema**: documents in one collection can have different fields. Add a new field — no migration of the whole table needed. Default port — 27017.

### Data model: nesting instead of joins

The main shift in thinking. In a relational DB an order, its line items and its address are three tables, assembled on read with a **JOIN**. In Mongo it's often **one document**: the order already contains the array of items and the address — fast to read, everything is together. The cost: data can be duplicated and is harder to keep consistent. Choosing the model ("embed or reference") is the key decision in Mongo.

### Fault tolerance and scale

- **Replica set** — a set of copies: one **primary** accepts writes, several **secondaries** repeat them; primary goes down — the nodes elect a new one (elections).
- **Sharding** — data is split by a **shard key** and spread across shards → horizontal scale. Choosing the shard key correctly is critical: a bad key creates load skew.

### SQL vs MongoDB

| | Relational (SQL) | MongoDB (document) |
|---|---|---|
| Schema | Strict, upfront | Flexible, documents differ |
| Data | Tables + relations (JOIN) | Documents (often nested) |
| Transactions | A strong point | Yes (multi-document since 4.0), but rarely needed |
| Scale | Vertical + read replicas | Horizontal (sharding) out of the box |
| When | Strict data, money, reporting | Flexible/changing data, large volumes |

Multi-document transactions appeared in Mongo in version 4.0 — but they're needed less often, because related data usually lives in a single document.

### When to choose what

- **Relational by default** — strict relations, transactions, reports (orders, payments, users).
- **Mongo** — flexible/heterogeneous structure: a catalog with varying attributes, profiles, events.
- Often an app uses **both**: in our delivery, orders and payments in Postgres, the flexible catalog in Mongo.

---

## Key takeaways

- **Relational** = tables + strict schema + SQL + ACID; the source of truth.
- Around the DB, devops maintains: **access, connection pool, replication, backups, migrations**.
- Data on several nodes → **CAP**: during a network partition you choose between consistency and availability.
- A **snapshot** sits next to the DB (fast, but dies with it), a **backup** lives elsewhere (survives losing the server).
- **Operations:** watch connections, replica lag and disk; slow queries are cured with indexes.
- **NoSQL** — for flexibility and scale; **MongoDB** = documents + replica set + sharding.
- Take relational by default, Mongo for specific tasks; often you need both.

---

## Lab

**[Lab 3 — Database replication: stand it up, break it, recover](lab.md)**

Your choice of PostgreSQL or MongoDB: you stand up replication, split reads from writes, catch **replication lag**, tie it to the **CAP theorem**, and survive a **failover** (manual in Postgres, automatic in Mongo). Plus the mandatory monitoring: your own dashboard and 3 metrics to alert on.
