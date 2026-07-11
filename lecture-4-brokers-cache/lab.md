# Lab 4 — Kafka for two services: set it up and configure it from scratch

## The situation

A developer comes to you, the devops engineer:

> "I have two services — a user service and a picker service. The user creates orders, the picker has to receive and process them. I need Kafka between them. Please set it up and configure it."

The services aren't written yet — you write them. And then — this is the main part — **you stand up and configure Kafka for them from scratch** and check how it behaves in different situations.

## Part 1 — Write the two services

Sketch two small services — the language is up to you, you may generate them with AI. Keep them **simple and visual**: the point is not the code, but being able to see Kafka at work.

**user-service:**
- An HTTP page on localhost with a "Create order" button.
- On click — publishes an "order created" event (e.g. `order_id` and a list of items) to a Kafka topic.
- Shows what it sent and — for clarity — into which **partition** and at which **offset** (Kafka returns this on send).

**picker-service:**
- Reads the topic as a **consumer group**.
- For each message it "assembles" the order (a simple pause is fine) and shows what it processed: partition, offset and its own instance name.

Each service has its own **Dockerfile**. So it's convenient to change settings through configuration later, expose at least these as environment variables: the Kafka address, the topic, the consumer group, the instance name.

## Part 2 — Stand up Kafka and run the services

- Stand up **Kafka** through configuration (Helm values on Kubernetes or Docker configuration; no ZooKeeper needed — KRaft mode).
- Create the `orders` topic **from configuration**.
- Build the service images and run them so they can see your Kafka and open on localhost.
- Click "Create order" and make sure orders reach the picker.

## The main rule: everything through configuration, not the CLI

In production Kafka is configured **declaratively**, not with manual commands. So first choose your **level of work** — it decides how you describe everything:

- **Container level** → use **`docker compose`**: describe Kafka, the topic, the services and Kafka UI in `docker-compose.yml`, and make changes by editing that file and running `docker compose up`.
- **Kubernetes level** → work **through Helm**: Kafka and the topic from a chart/operator (e.g. Strimzi with `KafkaTopic`), the services and Kafka UI as your own manifests or chart, and changes via `values` and `helm upgrade`.

Either way:

- Kafka, the topic and its parameters (partition count, retention) are set **in configuration**, not with a `kafka-topics.sh` command.
- **Any change** is a **config edit and re-apply**.
- The only exception is operations that don't exist in config (e.g. resetting offsets): those you do through Kafka UI (Part 5), also without the CLI.

## Part 3 — Business situations (solved through configuration)

Below are real business problems that you reproduce on your services. For each, **figure out yourself which Kafka setting solves it**, make the change through configuration (edit config + re-apply) and check the result. In the README describe: what the problem was, what you changed in Kafka and why it helped (via lecture concepts).

1. **Prepare for a sale, then scale back down.** A big sale is coming — a spike of orders is expected, and you need the processing to be shareable across several pickers in parallel. Prepare Kafka for this in advance and verify on the service pages that orders can now be distributed across several consumers. And when the sale ends and the flow drops — return the configuration to the smaller one. If you couldn't reduce the number of partitions — explain why.
2. **Adding a second picker.** Stand up a **second instance of the picker service** in the same consumer group. Create several orders and see, on both pickers' pages, how orders got split between them. Check: what happens if there are more pickers than "slots" for them?
3. **The picker went down during a deploy.** Turn off the picker service and click "Create order" several times. Explain and show how to make sure these orders are **not lost** and will be assembled once the picker service is back. Then bring the picker back and check your hypothesis.

## Part 4 — Stand up Kafka UI

Add a web interface — **Kafka UI** — to your configuration (e.g. the `provectuslabs/kafka-ui` image; the broker address is the `KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS` variable, the cluster name is `KAFKA_CLUSTERS_0_NAME`). Open it at http://localhost:8080 and find your `orders` topic, its partitions and the consumer group.

## Part 5 — Business situations (solved through Kafka UI)

Work through these via Kafka UI, without the command line:

4. **Investigating a complaint about a specific order.** Create several orders and remember the number of one of them. In Kafka UI find that exact message in the `orders` topic: determine which partition and offset it's in, and whether the picker has processed it (by the group's position/lag).
5. **Recomputing history for analytics.** Imagine the analysts need to replay all orders from the very beginning. In Kafka UI reset the picker group's offsets to the start (reset offsets → earliest) and watch on the picker service page how it re-assembles all past orders. Explain why Kafka allows this and a regular queue doesn't.
6. **The disk is filling up with old orders.** Orders are only needed for a couple of days but pile up forever. Lower the topic's retention (via config and re-apply, or by editing the topic in Kafka UI), create orders, let the period expire and show in Kafka UI that old messages are removed even though they've already been read.

## Part 6 — Monitoring (mandatory)

Set up monitoring for your Kafka. **Decide yourself which metrics matter on the dashboard**, build a dashboard from them, and then **pick 3 metrics you'd build alerts on** and explain your choice — what each one catches and what it threatens.


Note: if the system doesn't expose Prometheus metrics itself, add a separate exporter for it.

The tool is up to you.

## What to submit

1. **The code of the two services** with Dockerfiles.
2. **`README.md`** — how you stood up Kafka, Kafka UI and the services **through configuration**; what you changed in each situation (config edits) and what you observed (explained via lecture concepts); your dashboard and the rationale for the 3 alert metrics.
3. **Your configs** — whatever you used to stand up and configure everything (Helm values / manifests / Docker configuration).
4. **Screenshots**: both service pages, Kafka UI (topic, partitions, lag, reset offsets), the monitoring dashboard.

## How to start

Open this repository with your AI assistant and ask it to help you with **Lab 4**. The assistant is set up to guide you **step by step** and check your understanding — it won't hand you a finished solution, and that's on purpose. Start with Part 1 (sketch the two services).

> **Using AI?** Make sure your assistant follows the repo's rules in [`AGENTS.md`](../AGENTS.md). Most tools pick it up automatically; if yours doesn't, point it at that file and ask it to follow it.
