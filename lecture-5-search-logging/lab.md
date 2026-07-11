# Lab 5 — Deploy ELK and get hands-on with Elasticsearch

## Goal

Run Elasticsearch + Kibana locally, load application logs, learn to search and aggregate over them, work through shards, replicas and cluster status, and set up a minimal rotation (ILM + rollover). All local, with a demonstration that it works.

There is a single scenario — **application logs**: the case DevOps most often sets Elasticsearch up for.

---

## Part 1 — Deploy ELK locally

- Bring up **Elasticsearch + Kibana** (a single-node cluster is enough).
- Wait for startup and open Kibana in the browser.
- Check cluster health (`GET _cluster/health`) and look at the status.
- **Answer in your README:** what is the cluster status, why is it that way on a single node, and what is needed for it to become green?

## Part 2 — Data, index and search

**First you need the logs themselves.** We have no real application, so **generate the test logs yourself** — the easiest way is to ask an AI to generate 20–50 realistic entries in JSON with the fields `timestamp`, `level` (INFO/WARN/ERROR), `service`, `message`, `trace_id` and varied values.

**Create an index with a mapping.** A mapping (from the lecture) is the declaration of the index's fields and their types. A reasonable minimum for logs:
- `timestamp` — date
- `level` — keyword
- `service` — keyword
- `message` — text
- `trace_id` — keyword

**Load the logs** into the index (via the bulk API or one by one).

**Run several queries:**
- full-text search over `message`;
- a filter by `level = ERROR` and by a time range;
- a search by a specific `trace_id`.

**Do one aggregation** — for example, the number of logs by `level` or by `service`.

**Look at the data in Kibana** and build a simple visualization (for example, bars by `level`).

## Part 3 — Minimal ILM + rollover

A minimal but required part — demonstrate automatic rotation:

- Create a simple **ILM policy**: rollover on a threshold (for the demo use a small one — e.g. a few MB by size, or 1 day by age) and **delete** after a short period.
- Attach it via an index template + alias, and write logs to the **alias**, not to a concrete index.
- Show that after rollover fires a new index appears (`GET _cat/indices?v`).

Demonstrating the mechanism is enough — you don't need to run real volumes.

---

## Part 4 — Monitoring (mandatory)

Set up monitoring for your cluster. **Decide yourself which metrics matter on the dashboard**, build a dashboard from them, and then **pick 3 metrics you'd build alerts on** and explain your choice — what each one catches and what it threatens.

The monitoring tool is up to you.

---

## What to submit

Put everything in a folder and submit:

1. **`README.md`** — what you did, the key commands and configs (index mapping, ILM policy), how to run it, and the rationale for the 3 chosen alert metrics.
2. **Launch configs** — whatever you used to bring up ELK (`docker-compose.yml` or Kubernetes manifests).
3. **Screenshots** of the key moments: cluster status, a search result, an aggregation/visualization in Kibana, the list of indices after rollover, and the **3 monitoring graphs**.

---

## How to start

Open this repository with your AI assistant and ask it to help you with **Lab 5**. The assistant is set up to guide you **step by step** and check your understanding along the way — it won't hand you a finished solution, and that's on purpose. Start with Part 1 (bring up ELK) and go from there.

> **Using AI?** Make sure your assistant follows the repo's rules in [`AGENTS.md`](../AGENTS.md). Most tools pick it up automatically; if yours doesn't, point it at that file and ask it to follow it.
