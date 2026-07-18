# Lecture 3 — Message brokers and cache

This lecture is about how services talk to each other without getting in each other's way, and how to speed up a system with a cache. Three heroes: **RabbitMQ**, **Kafka** and **Redis** — all three are usually deployed and run by devops, while developers just use them.

**Running example.** The whole lecture uses one application — **grocery delivery** (think of something like a rapid-delivery app). It has three services that constantly pass data to each other:

- **user-service** — the customer picks products and places an order; the output is an order with a list of items, an address and payment details;
- **picker-service** — a picker in the store gets an assignment and assembles the order (an item may be out of stock — then a replacement or removal is needed);
- **courier-service** — a courier is assigned an already-assembled order, picks it up from the store, delivers it to the customer and streams their location to the map along the way.

An order's life: the customer places it → the picker assembles it → the courier delivers it. At each step the services need to learn about each other's events — and that's where brokers come in.

This README works as a **self-contained summary**. Three parts: first *why brokers are needed*, then *Kafka (and how RabbitMQ differs from it)*, and finally *Redis*.

---

## Part 1 — Why brokers are needed

### The problem with direct calls

The customer places an order — and a lot must happen off that one event: the picker must be told to assemble it, then the courier to deliver it, plus charging the payment, notifying the customer, updating analytics.

The most direct way — **user-service** itself calls all the other services one by one and waits for each. This is **synchronous** communication, and it has problems:

- **Tight coupling.** user-service must know about the picker, courier, payment, notifications — everyone.
- **Waiting.** The order isn't placed until everyone responds; the customer waits.
- **Fragility.** The notifications service goes down — placing an order breaks entirely.
- **Peaks.** At lunchtime there are 10× more orders — and every service must survive the peak at once, right now.

### Synchronous vs asynchronous

- **Synchronous** — "call and stay on the line until they answer."
- **Asynchronous** — "leave a message and get on with your day." The recipient handles it when they can.

Brokers are about the second approach.

### What a message broker is

> **A message broker** — an intermediary service through which components exchange messages without talking to each other directly. The sender (**producer**) puts a message into the broker; the recipient (**consumer**) picks it up. The broker stores messages and is responsible for delivering them.

In our example user-service just publishes one "order created" event to the broker and immediately answers the customer "order accepted" — without waiting for anyone. From there the event lives its own life: picker-service picks it up and queues the order for assembly; once assembled, picker-service publishes "order assembled"; courier-service picks that up and assigns a free courier; the courier takes it — "in transit", delivers it — "delivered". Plus payment, notifications and analytics also react to "order created". Nobody calls anyone directly — everyone communicates through events in the broker.

### What this gives you

- **Decoupling.** user-service doesn't know who will read "order created" — picker, analytics, notifications. You can add a new recipient service without touching user-service.
- **A buffer for peaks.** At the lunch peak orders pile up in the broker, and pickers work through them as they can — nothing is lost.
- **Asynchrony.** user-service doesn't wait for the order to be assembled and delivered.
- **Reliable delivery.** The broker keeps a message until it's picked up; picker-service restarted — the message will wait.

Reliability rests on **acknowledgements (ack)**: until the consumer confirms it processed a message, the message counts as undelivered and will be handed out again. Hence three levels of **delivery guarantees**:

- **at-most-once** — a message may be lost, but there will be no duplicate;
- **at-least-once** — no loss, but duplicates are possible, so the handler must be idempotent; this is the most common mode;
- **exactly-once** — neither loss nor duplicates, but it's the most expensive and isn't supported everywhere.

### Two basic patterns

- **Queue.** A message is taken by **one** of the recipients — work is split among them. Example: the task "assemble order #123" should be taken by **one** picker on shift, not all at once.
- **Publish-subscribe (pub/sub).** **All** subscribers receive the message. Example: the "order created" event is needed at once by the picker, notifications and analytics.

("Event stream" is not a separate pattern but how Kafka implements pub/sub: a durable log you can re-read. More in Part 2.)

This difference is the key to the next part: RabbitMQ is good at the queue model, Kafka at pub/sub via a durable event stream.

### Where devops fits in

A broker is a separate service (more often a cluster) that **devops deploys, configures and maintains**: access, fault tolerance, storage for messages, monitoring. Developers of the user, picker and courier services just publish and read messages through it.

---

## Part 2 — Kafka (and a bit of RabbitMQ)

### RabbitMQ in brief

**RabbitMQ** — a classic message broker that speaks the AMQP protocol. The model:

- a producer sends a message to an **exchange**;
- the exchange, by routing rules, puts it into one or more **queues**;
- a consumer reads from a queue and acknowledges processing (**ack**), after which the message is **removed** from the queue.

In our example: a queue "orders to assemble". user-service puts tasks there, and there are several picker-workers — each takes an order, assembles it, acknowledges (ack), and the task disappears from the queue. Different stores can be routed to different queues — that's flexible routing. RabbitMQ is a "smart broker, dumb consumer": routing logic lives in the broker.

### Kafka — a distributed event log

**Kafka** is built fundamentally differently. It's not a queue that messages are crossed off, but a **log** — an ordered stream of events that is stored and can be re-read. Key concepts (on the example of a topic `order-events` with all order events):

- **Topic** — a named stream of events on one subject. For example, `order-events`: "created", "assembled", "in transit", "delivered".
- **Partition.** A topic is split into partitions; each partition is an ordered, append-only log of messages. Partitions are distributed across brokers — hence parallelism and horizontal scale. Which partition a message lands in is decided by the **key** (same key → same partition). **Ordering is guaranteed only within a single partition**, not across the whole topic. That's why events of one order go into one partition (key = `order_id`) — so "created → assembled → delivered" go strictly in order.
- **Offset** — the sequence number of a message in a partition, i.e. the read position. Each consumer remembers its own offset.
- **Retention.** A read message is **not deleted** — it stays in the topic for a set time (7 days by default) or up to a size limit. So you can re-read history: e.g. replay all orders for the month to recompute analytics.
- **Consumer group.** Consumers in one group split the partitions among themselves. In our example the `order-events` stream is read independently by **three groups**: the picker group reacts to "order created" and starts assembly; the courier group waits for "order assembled" to assign a courier; the analytics group counts everything (number of orders, average assembly time). Each keeps its own offset and doesn't disturb the others.
- **Replication.** Each partition is copied to several brokers (replication factor) — if a broker goes down, data isn't lost.

Kafka is a "dumb broker, smart consumer": the broker just stores the log, while the logic (what to read and from which offset) lives in the consumer.

Kafka is a distributed system of several **brokers** (nodes). A separate ZooKeeper used to coordinate the cluster; in newer versions it's replaced by the built-in **KRaft** mechanism (ZooKeeper was fully removed in Kafka 4.0).

### Dead-letter queue (DLQ)

Kafka doesn't delete messages on read, and a consumer goes through a partition in order (by offset). If a "poison" message that can't be processed shows up, the consumer gets stuck on it and can't move further down the partition.

> **Dead-letter queue (DLQ)** — a separate place where messages a consumer failed to process (an error, retries exhausted) are sent, so they aren't lost and don't block reading.

In Kafka a DLQ is usually a **separate topic**: after several failed attempts the consumer writes the problem event to it, commits the offset and moves on. The message itself isn't lost — it's handled separately (an operator or a dedicated handler), while the order flow doesn't stall.

In our example: an order can't be assembled — the item is missing and no replacement was found — the event goes to a DLQ topic, and the rest of the orders are processed further. (RabbitMQ has a built-in mechanism for the same — a dead-letter exchange.)

### Kafka vs RabbitMQ — when to use which

| | RabbitMQ | Kafka |
|---|---|---|
| Model | Task queue | Log (stream) of events |
| After reading | Message is removed | Stays (retention), can re-read |
| Who receives | One of the consumers | Many independent consumers/groups |
| In our example | "Assemble order #123" — one picker takes it | The order event stream is read by picker, courier and analytics |
| Typical cases | Background tasks, commands | Logs, analytics, event-driven, streaming |

Simply put: you need to **hand out tasks** that someone does once and forgets (assemble a specific order) — that's RabbitMQ. You need a **stream of events** read by many and sometimes re-read (all order statuses) — that's Kafka.

### Where devops fits in

Kafka is a distributed cluster: several brokers, partitions and their replicas, coordination (KRaft). devops is responsible for the cluster size, replication factor, retention settings and disk space (events pile up!).

### What you usually watch (monitoring)

The main thing — are consumers falling behind and are there enough resources. Common signals:

- **Consumer lag** — in Kafka that's *consumer lag* (how far a consumer is behind the end of a partition), in RabbitMQ it's the queue length. Growing → we're not keeping up (e.g. picker-service isn't catching up with the order stream). The most important metric.
- **Throughput** — how many messages per second come in and go out.
- **Broker resources** — disk (messages pile up!), memory, CPU.
- **Cluster health** — in Kafka watch replication: under-replicated and offline partitions mean a broker problem.
- **Errors** — a growing DLQ, rejected publishes. (RabbitMQ separately — unacked messages and memory/disk alarms that block publishers.)

---

## Part 3 — Redis

### What it is

> **Redis** — a very fast in-memory data structure store: it keeps all data in RAM and responds in fractions of a millisecond. Used as a cache, a database and a message broker.

Written in C, speaks the RESP protocol on port 6379, handles on the order of 100k+ operations per second from a single instance. It executes commands **single-threaded**, one after another — so they're atomic (no races or locks). The flip side of being single-threaded: one long command delays all the others (see problems below). There are transactions (MULTI/EXEC), Lua scripts and pipelining.

**License history.** In 2024 Redis switched to a source-available license (stopped being pure open-source), and the community made an open fork, **Valkey**, under the Linux Foundation — exactly like OpenSearch relative to Elasticsearch.

### What it's for (uses) — on our application

- **Cache** — the most common case. Product cards and stock levels are put in Redis so user-service doesn't hit the slow DB on every view. It works by the **cache-aside** pattern: the app first looks in Redis, on a miss goes to the DB and puts the result in the cache with a **TTL** (a lifetime, set with `EXPIRE`).
- **Session storage** — sessions of logged-in users in a shared fast store.
- **Fast-changing data** — the courier's location updates every couple of seconds; Redis is faster than the DB for this (tracking the courier on the map).
- **Counters, rate limiting, leaderboards** — on the atomic `INCR`; rate limiting is `INCR` + `EXPIRE` ("no more than N orders a minute"); a courier leaderboard is a sorted set.

### Not "just strings" — data structures

Redis stores more than strings, and each structure has its own atomic commands: **strings** (`INCR`), **hashes** (a user profile), **lists** (`LPUSH`/`BRPOP` — a queue), **sets** (`SADD`), **sorted sets** (`ZADD`/`ZRANGE` — a leaderboard). Plus special ones: **streams** (a message log), **bitmaps**, **HyperLogLog** (approximate unique counting in tiny memory), **geospatial** (geo queries, "nearest couriers"). Choosing the right structure is half of using Redis well.

### Persistence

Redis is in-memory, but the data doesn't have to vanish on restart. Two mechanisms for saving to disk:

- **RDB** — periodic snapshots of the whole dataset; done by forking the process (copy-on-write), non-blocking. Compact, but on a crash you lose changes since the last snapshot.
- **AOF** (append-only file) — a log of all write operations; the flush-to-disk frequency is configurable (once a second by default). The file is periodically rewritten so it doesn't grow unbounded.

Often both are enabled. Even so, Redis **does not replace the primary DB**: the source of truth is a regular DB, and Redis holds only the cache and auxiliary data.

### Common problems

- **Eviction.** When usage hits the `maxmemory` limit, Redis removes keys by the chosen policy (`allkeys-lru`, `allkeys-lfu`, `volatile-ttl`, etc.); with `noeviction` new writes start failing with an error. Note: lru/lfu are **approximate** — for speed Redis samples some keys rather than tracking all of them.
- **Hot keys.** One popular key (the stock of a sale item everyone checks) gets a disproportionate number of requests → a bottleneck on one node.
- **A long command blocks everything.** Because of single-threading, a heavy command (e.g. `KEYS *` over the whole database) occupies the single thread, and all of Redis stalls meanwhile.
- **Data loss on a crash** without persistence — fine for a cache, not for important data.

### Where devops fits in

devops watches **memory** (the main resource, `maxmemory` + eviction policy) and persistence; sets up fault tolerance — **replication** (asynchronous → on failover you can lose the most recent writes) + **Sentinel** (quorum-based failover) or **Redis Cluster** (sharding across 16384 hash slots, at least 3 masters recommended); monitors memory, cache hit rate, latency and the number of connections.

---

## Key takeaways

- A broker — an intermediary for **asynchronous** exchange: it decouples services, buffers peaks, delivers reliably.
- Two patterns: a **queue** (one recipient gets the message) and **publish-subscribe / pub-sub** (all get it).
- **RabbitMQ** — a task queue ("assemble the order"), the message is processed and removed; flexible routing.
- **Kafka** — a distributed event log ("order stream"): topics, partitions, offset, retention, consumer groups; high throughput, can re-read.
- **Redis** — a fast in-memory store: cache (with TTL), sessions, location, counters; data structures, RDB/AOF persistence, but not a replacement for a DB.

---

## Lab

[Lab 3 — Kafka for two services: set it up and configure it from scratch](lab.md): the student writes (or generates) two simple services, stands up and configures Kafka for them **through configuration** (no manual CLI), verifies situations first by editing config (partitions, number of pickers), then through Kafka UI (replay, retention), and sets up monitoring.

---

## Further reading

- [RabbitMQ: terminology and basic entities](https://habr.com/ru/companies/slurm/articles/703060/) (Habr, in Russian) — a walkthrough of core RabbitMQ concepts: publisher, exchange, binding, queue, message, consumer. A good complement to Part 2.
