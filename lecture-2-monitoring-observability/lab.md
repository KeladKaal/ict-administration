# Lab 2 — Full monitoring for a small service

## Goal

Build a small simple service (write or generate it) and stand up **full monitoring for it: metrics, logs and traces**. Metrics and logs go in **Grafana**, traces separately in **Jaeger**. That's all three pillars of observability on your own service.

## Part 1 — A small service with buttons

Sketch (or generate — the code isn't the point) a simple HTTP service with a page and three buttons, so you can trigger different situations yourself:

- **"Cause an error"** — the endpoint returns an error (5xx) and increments the error counter.
- **"Cause a delay"** — the endpoint responds slowly (e.g. sleeps 1–3 seconds).
- **"Load"** — the service fires a burst of requests at itself so the request rate (RPS) spikes.

The service must also:

- expose **metrics** in Prometheus format at `/metrics`: a request counter, an error counter, a response-time histogram (RED);
- write **structured logs** (JSON): level, message, and the current request's `trace_id`;
- be **instrumented with OpenTelemetry** for traces (see Part 4);
- have its own **Dockerfile**.

Keep the service simple: the point of the lab isn't the code, it's the monitoring around it.

> Stand up the infrastructure (the service, Prometheus, Grafana, Loki, Jaeger, Alertmanager) through configuration — `docker compose` at the container level or Helm on Kubernetes (see the general rule in the root README).

## Part 2 — Metrics (Prometheus + Grafana)

- Stand up **Prometheus** and configure scraping of your service's metrics.
- Stand up **Grafana** and add Prometheus as a data source.
- Build a **RED dashboard**: request rate, error share, response-time percentile (p95).
- Click "Load", "Cause an error", "Cause a delay" and make sure the graphs react.

## Part 3 — Logs (Loki + Promtail → Grafana)

- Stand up **Loki** and the **Promtail** agent (or an equivalent), configure log collection from the service.
- Connect Loki to the **same Grafana** — now metrics and logs are in one window.
- Click "Cause an error" and find that error in the logs.

## Part 4 — Traces (OpenTelemetry → Jaeger)

Three sides here: how the service *emits* traces, how Jaeger is *configured*, and what to *check*.

**How the service should work with traces:**
- Instrument the service with the **OpenTelemetry SDK** for your language. Enable auto-instrumentation of the HTTP framework — then a root span is created automatically for each incoming request.
- In the **"delay"** handler wrap the slow operation in a **nested span** (e.g. `slow-dependency`) — so the waterfall shows the time went there.
- In the **"error"** handler mark the span as errored (status = error) — Jaeger will highlight it.
- Put the current span's `trace_id` into the logs — that links a log and a trace.
- Export traces via the **OTLP** protocol — the address is usually set with `OTEL_EXPORTER_OTLP_ENDPOINT`.

**How to configure Jaeger:**
- The easiest way is **Jaeger all-in-one** (one `jaegertracing/all-in-one` container). It accepts traces over **OTLP** (port 4317 — gRPC, 4318 — HTTP) and serves the **UI on port 16686**.
- Point the service's OTLP exporter at Jaeger (its address and port 4317/4318).
- *(optional, like in production)* put an **OpenTelemetry Collector** in between: the service sends to the Collector, the Collector to Jaeger. This keeps the app unaware of the concrete backend.

**What to check in the Jaeger UI (16686):**
- Pick your service and find traces.
- Click "Cause a delay" → find that trace: the long `slow-dependency` span is visible in the waterfall.
- Click "Cause an error" → find the trace with the errored (red) span.
- Take a `trace_id` from a log in Grafana and find the same trace in Jaeger.

## Part 5 — Alerts in Alertmanager (mandatory)

- Write alert rules in **Prometheus** (in PromQL) and wire **Alertmanager** to it.
- Configure a receiver in Alertmanager (webhook, email, Slack — whatever is convenient; the point is that firing is visible).
- Pick **3 metrics** and write rules for them. **Trigger them with the buttons:**
  - "Cause an error" several times → an error-rate alert;
  - "Load" → a request-spike alert;
  - "Cause a delay" → a p95-latency alert.
- Show the alerts firing in Alertmanager, and in the README explain your choice — what each alert catches and what it threatens.

## What to submit

1. **The service code** with a Dockerfile.
2. **Configs** — whatever you used to stand up the stack (Prometheus + alert rules, Alertmanager, Grafana, Loki/Promtail, Jaeger/OTel; `docker compose` or Helm manifests).
3. **`README.md`** — what you stood up and how, which metrics are on the dashboard and why, the rationale for the 3 alerts.
4. **Screenshots**: the metrics dashboard (Grafana), logs in Grafana, a trace waterfall in Jaeger (delay and error), the firing alerts in Alertmanager.

## How to start

Open this repository with your AI assistant and ask it to help you with **Lab 2**. The assistant may generate the sample service directly — programming isn't the goal here. But the monitoring (Prometheus, Grafana, Loki, Jaeger, Alertmanager) it will walk you through **step by step** and check your understanding — it won't hand you a finished infrastructure solution.

> **Using AI?** Make sure your assistant follows the repo's rules in [`AGENTS.md`](../AGENTS.md). Most tools pick it up automatically; if yours doesn't, point it at that file and ask it to follow it.
