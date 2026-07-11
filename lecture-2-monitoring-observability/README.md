# Lecture 2 — Monitoring and observability

This lecture is about seeing what happens inside a system, noticing problems early, and acting sensibly when something does blow up. Monitoring comes second in the course for a reason: from here on every lab has a mandatory monitoring part, so it's a cross-cutting theme.

This README works as a **self-contained summary**. Three parts: first *the basics of observability and its three pillars*, then *how to build the monitoring infrastructure*, and finally *working with incidents*. Examples use the familiar **grocery delivery** app (user, picker and courier services).

---

## Part 1 — The basics of observability

### Why it's needed at all

Imagine: 3 a.m., production is down, orders aren't going through, customers leave. There are many services — but *where exactly* the problem is and *why* is unclear. Without monitoring you learn about the outage from customers and fix it blind.

The goal of good monitoring is to **notice degradation early**: while it's still "slower than usual", not "everything is down". The disk is filling up — warned a day ahead; errors are creeping up — spotted while there are a handful, not thousands. The ideal is to fix it before a user notices.

### Observability vs monitoring

> **Monitoring** — answers questions you decided on in advance: you chose what to watch and set up metrics, dashboards and alerts.
>
> **Observability** — a property of a system: it emits enough signals to ask a **new** question after the fact and understand even an unfamiliar situation.

Simply: monitoring is about *known* failures (you anticipated them), observability is about *unknown* ones (the system gives enough data to get to the bottom of something you didn't plan for).

### The three pillars of observability

Observability rests on three sources of signal that complement each other:

- **Metrics** — *what* is happening (numbers over time: load, errors, latency).
- **Logs** — *what exactly* happened (events with details).
- **Traces** — *where exactly* (a request's path through the services).

Example: metrics say "errors went up", logs say "here's the error text and stack trace", the trace says "the error is in the payment service on the third step of the request".

### Metrics

> **A metric** — a numeric measurement taken over time (a time series). For example: orders per minute, error rate, checkout time.

Metrics are cheap to store and aggregate easily, so graphs and alerts are built on them. In Prometheus a metric has a name and **labels** — for example, by service and endpoint.

**Metric types:**

- **counter** — only goes up (number of requests, errors); on a graph you look at the *rate* of growth (requests per second).
- **gauge** — goes up and down (memory used, number of active orders).
- **histogram** — buckets values (response time) → used to compute **percentiles**: p95 = "95% of requests are faster than X".
- **summary** — like a histogram, but the quantiles are computed by the application itself.

### Logs

> **A log** — a record of a specific event with context: time, level, message, details. For example: `ERROR checkout: payment declined, order_id=123`.

If a metric says "errors went up", a log says *what exactly* the error is. It's better to write logs **structured** (JSON) — then they're easy to search and filter. A useful trick: put `trace_id` in the log to jump from a log to a trace and back.

### Traces

> **A trace** — the path of one request through all the services. **A span** — one step inside a trace (an operation) with a start time, duration and a parent. All spans of one request are tied by a shared **trace_id**.

**Why this matters in microservices.** The "place an order" request goes through user → payment → picker. When it's slow, metrics say "slow", logs say "an error somewhere", but only the trace shows that payment ate 2 of the 2.3 seconds. Two key ideas:

- **context propagation** — `trace_id` is passed between services via headers so the trace assembles across all services;
- **sampling** — storing all traces is expensive, so only a fraction is kept.

**How traces appear: Jaeger + OpenTelemetry.** The application code has to be **instrumented**. The standard today is **OpenTelemetry (OTel)**: vendor-neutral, one SDK generates traces (as well as metrics and logs) and sends them via the OTLP protocol. The data goes to the **OTel Collector**, which routes it to backends. The backend for traces is **Jaeger** (or Tempo): it stores traces and provides a UI — a "waterfall" of spans and a service dependency graph. The devops role — stand up the Collector and backend; instrumenting the code is on developers.

Honestly: traces are the least-adopted of the three pillars (you have to instrument the code), but in microservices they're the most powerful tool for finding *where* something is slow.

---

## Part 2 — Tools and architecture

### Two stacks: ELK vs the Grafana stack

- **The Grafana stack** (our main choice): **Prometheus** (metrics) + **Loki** (logs) + **Tempo/Jaeger** (traces) + **Grafana** (a single visualization window) + **Alertmanager** (alerts).
- **ELK**: Elasticsearch + Logstash + Kibana — a strong stack for logs (see the search-and-logging lecture).

Important: it's not either/or. Prometheus is about metrics, ELK/Loki about logs — they solve different problems and often live together. We build on the Grafana stack and keep ELK in mind as the logs alternative.

### Monitoring architecture

How the infrastructure is assembled:

**Services and hosts → agents/exporters → stores → Grafana → Alertmanager**

- **metrics:** exporters → Prometheus (pull model, scrape);
- **logs:** Promtail → Loki;
- **traces:** OTel Collector → Tempo/Jaeger;
- **Grafana** connects to all three as a single window; **Alertmanager** sends notifications.

This is the infrastructure devops stands up.

### What you usually measure — the "golden signals"

Infrastructure is assembled — what to put on it? Two simple sets:

- **RED — for request-handling services** (Tom Wilkie's method): **R**ate — request throughput (count per unit time), **E**rrors — the share of requests that failed, **D**uration — processing time as a distribution (percentiles, not an average — the average hides the tail of slow requests). Example: the checkout service — requests/sec, share of 5xx responses, p95 response time.
- **USE — for resources** (CPU, memory, disk, network; Brendan Gregg's method): **U**tilization — the fraction of time the resource is busy, **S**aturation — the amount of work queued that the resource can't service immediately, **E**rrors — the number of resource errors.

### Exporters

> **An exporter** — a small service that exposes metrics in Prometheus format over HTTP (the `/metrics` endpoint).

Prometheus works by a **pull model**: it goes to the addresses itself and scrapes the metrics. The classic one is **node_exporter** (host metrics: CPU, memory, disk). For databases, brokers, Redis — their own exporters.

### Promtail and Loki

**Promtail** — a lightweight agent that reads logs from hosts and containers, adds labels (service, level) and sends them to **Loki**. In role it's like Filebeat in ELK. Loki indexes only the labels, not the full text — so it's cheaper than Elasticsearch, but search works differently.

### Alerts

Alert rules are written in **PromQL**: "if the error rate is above X for five minutes — alert". The rule itself lives in Prometheus, while **Alertmanager** handles delivery:

- **grouping** — similar firings into one notification (not 100 emails, but one);
- **routing** — to whom and where (team, Slack, email, pager);
- **silences** — muting alerts during planned work.

How to alert *sensibly* — in Part 3.

---

## Part 3 — Incidents

### What an incident is

> **An incident** — an event that breaks (or threatens to break) things for users and requires an organized response.

A fired alert is not yet an incident. An incident is when a service actually degraded for users.

### Severity

To respond proportionally, incidents are assigned a **severity**. An example scale:

- **SEV1** — everything is down, all users affected → wake the team at night;
- **SEV2** — serious degradation, part of the functionality;
- **SEV3** — minor, can wait until working hours.

Severity dictates who to pull in and how fast — not everything is worth waking someone at 3 a.m.

### SLO / SLI / error budget

What should you even alert on? Not every hiccup, but what matters to the user. For that you introduce:

- **SLI** — a measurable quality indicator (e.g. the share of successful requests);
- **SLO** — a target for the SLI (e.g. 99.9% over a month);
- **error budget** — the allowed share of failures (100% − SLO), a budget you can spend.

You alert not on a single error but when the budget is **burning too fast** (burn rate). That way alerts come for a reason.

### Bad and good alerts

**A good alert:**
- **actionable** — it's immediately clear what to do;
- about a **symptom** (users are hurting), not about every internal cause;
- rare and meaningful.

**A bad alert** → noise → **alert fatigue** → in the stream of false firings the real one is missed. The rule: if you don't need to act on an alert — it's not an alert, it's a metric for a dashboard.

### An example incident management process

**Detect → Triage → Mitigate → Resolve → Postmortem.**

- **Detect** — noticed (an alert or a complaint).
- **Triage** — assessed the severity, assigned who fixes it.
- **Mitigate** — the key point: first **restore service** for users (roll back a release, shift traffic), find the root cause later.
- **Resolve** — recovered.
- **Postmortem** — the review after.

For big incidents you appoint an **incident commander** (who coordinates) and a separate person on communications.

### Responding to alerts

- **On-call** — the person on duty who receives the alert.
- **Escalation** — if the on-call doesn't respond within N minutes, the next in the chain is called.
- **Runbook** — a short "what to check and what to do for this alert". With it, even a tired person at night isn't poking around blind.

### Postmortem

> **A postmortem** — a review of an incident after recovery.

Inside: a **timeline** (what happened and when), the **root cause** (not "the service went down", but *why*), and most importantly — **action items**: concrete tasks so it doesn't recur. A postmortem's value is in the improvements it produces.

### Blameless culture

Examine the **system and the process**, not who's to blame. If a person is punished for an incident, everyone starts hiding mistakes and the real cause can't be found. If you examine the system (why a mistake became possible, where a safeguard was missing) — people speak honestly, and the system gets stronger. A person made a mistake → the system that allowed it is at fault.

---

## Key takeaways

- **The three pillars of observability:** metrics (*what*), logs (*what exactly*), traces (*where*).
- **Monitoring** answers known questions, **observability** — unknown ones.
- **Grafana stack:** Prometheus (metrics) + Loki (logs) + Tempo/Jaeger (traces) + Grafana + Alertmanager; ELK — the logs alternative.
- **What you measure:** RED (services) and USE (resources).
- **Alert deliberately:** by SLO/error budget, only actionable alerts, no noise.
- **Incidents:** severity → mitigate first → postmortem; blameless culture.

---

## Lab

[Lab 2 — Full monitoring for a small service](lab.md): build a small service (write or generate it) and stand up all three pillars for it — metrics (Prometheus) and logs (Loki) in Grafana and traces in Jaeger, plus set up alerts.
