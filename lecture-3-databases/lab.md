# Lab 3 — Database replication: stand it up, break it, recover

## Scenario

You have a small service that **writes records to a database and reads them back** — the topic is up to you (notes, products, posts, sensor readings — anything). Reads are growing, and to avoid loading the main database, the reading part is moved to a **replica**. Your task is to stand up replication, connect the service to it, and then see live what the lecture was about: **replica lag (replication lag)**, its link to the **CAP theorem**, and what happens when the **primary fails (failover)**.

You write the service yourself (you can generate it with AI) — it's simple and only exists so you can see the database's behavior. The main, learning part is the devops work **around** the database: replication, failover and monitoring.

## Part 0 — Choose a database

You can do the lab on one of two databases — **pick one yourself**. Both have replication, but it's built differently, and you'll see it from different angles:

- **PostgreSQL** — you configure replication **by hand through configuration** (primary and standby), and you do the failover **manually** (promote the replica yourself). Closer to "classic" relational operations: more control, more manual work.
- **MongoDB** — you stand up a **replica set**: replication is built in, and failover is **automatic** (the nodes elect a new primary themselves — elections). Here, instead of a manual promotion, you play with **read preference** (where to read from) and **write concern** (how many nodes confirm a write).

Note in the README right away which database you chose and why.

## Part 1 — Stand up replication (through configuration)

You bring everything up **declaratively** — through `docker compose` (container level) or Helm/manifests (Kubernetes level). Manual commands inside containers only where there's no other way (e.g. initializing a replica set), and you note that in the README.

**If PostgreSQL:**
- Stand up a **primary** and at least one **replica (standby)** with **streaming replication**.
- The replica must pull changes from the primary and be available **for reads**.
- Verify that data written to the primary appears on the replica.

**If MongoDB:**
- Stand up a **replica set** of three nodes (one primary + two secondaries — an odd number is needed for elections).
- Initialize the set and make sure one node became primary, the others secondary.
- Verify that a write to the primary replicates to the secondaries.

## Part 2 — Connect the sample service (read/write splitting)

Sketch a small service (language and topic up to you, you can generate it with AI). Keep it simple and visual — the code isn't the point:

- An **HTTP page** on localhost with a **"Create record"** button — on click it writes a record to the database.
- A **"Records"** list — reads and shows what's in the database.
- A **"Pour in load"** button — creates a batch of records in a row (useful for catching the lag).

The key point — **split writes from reads**:
- writes (**"Create record"**) go to the **primary**;
- reads (**"Records"**) go to the **replica** (in Postgres — to the standby; in Mongo — via **read preference `secondary`**).

Move the primary and replica addresses into environment variables — it's easier to switch that way. The service has its own **Dockerfile**.

## Part 3 — Catch the replication lag

Now the interesting bit, the whole reason for this.

1. Click **"Pour in load"** so a lot of writes flow into the primary.
2. Immediately refresh the **"Records"** list (reads from the replica).
3. Observe: for a while the just-created records **aren't in the list** — the replica is behind.

In the README describe: what exactly you saw, why it happens, and **what it threatens**. Figure out how you could **measure the size of the lag** in your database.

## Part 4 — The CAP theorem (must be mentioned)

Tie what you saw to the **CAP theorem** — right in the README:

- Which way does your current setup lean — toward **consistency (C)** or **availability (A)**? Why is an asynchronous replica with stale reads a lean toward A?
- What would you change in your database to shift toward **C**, and **what would you pay for it**?

A short but meaningful argument is enough — on your own example, not in the abstract.

## Part 5 — Failover: drop the primary

Check how the system survives the loss of the main node.

**If PostgreSQL (manual failover):**
1. "Drop" the primary (stop the container).
2. Try to create a record — you'll see that the write no longer goes through.
3. **Promote the replica to primary** (promote the standby) and switch the service to it. Check the write again.
4. In the README: what happened to writes and reads at each step; what would happen if the old primary suddenly came back; how such a manual failover is automated in production.

**If MongoDB (automatic failover):**
1. "Drop" the current primary (stop the container).
2. Observe how the nodes **elect a new primary themselves** (elections). Roughly time how long it took.
3. Verify that writes go through again (the driver reconnects to the new primary).
4. In the README: what happened to writes and reads during the elections; why an **odd number of nodes** and a majority are needed; what happens if only one of the three nodes is left.

## Part 6 — Monitoring (mandatory)

Set up monitoring for your database and its replication. **Decide yourself which metrics matter on the dashboard**, build a dashboard from them, and then **pick 3 metrics you'd build alerts on**, and explain your choice — what each one catches and what it threatens.

If the system doesn't expose metrics in Prometheus format itself — set up a separate exporter for it.

The tooling is up to you.

## What to submit

1. **The service code** with a Dockerfile.
2. **`README.md`** — which database you chose and why; how you stood up replication **through configuration**; what you observed in parts 3 and 5 (lag and failover) explained through the lecture's concepts; your **CAP** reasoning (part 4); your dashboard and the rationale for the 3 alert metrics.
3. **Your configs** — whatever brought it all up (Docker configuration / Helm values / manifests).
4. **Screenshots**: the service page, the moment with the reading lag, the state after failover, the monitoring dashboard.

## How to start

Open this repository with your AI assistant and ask for help with **Lab 3**. The assistant is set up to guide you **step by step** and check your understanding — it deliberately won't hand out a finished solution. Start with Part 0 (choose a database) and Part 1 (stand up replication).

> **Using AI?** Make sure your assistant follows the repository rules in [`AGENTS.md`](../AGENTS.md). Most tools pick it up automatically; if yours didn't — just point it at this file and ask it to follow it.
