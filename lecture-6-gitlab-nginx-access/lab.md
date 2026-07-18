# Lab 6 — The team's internal GitLab: single sign-on, an nginx boundary, and runners

## Scenario

You stand up and protect the **team's internal GitLab** — the center of the whole development platform. You'll go through the entire path from the lecture, but not on a toy example — on a real system: you'll set up **single sign-on** into the internal tools, put **nginx as a boundary** in front of GitLab, and configure **CI/CD with static and dynamic runners**. On top of it all — the mandatory **monitoring**.

The small service the pipeline will build, you write yourself (you can generate it with AI) — it's only there as the object that travels through the conveyor. Everything else is the devops infrastructure around GitLab, and that's the learning part.

You deploy everything **however you prefer** (`docker compose` or Kubernetes) and **through configuration**. Manual commands inside containers only where there's no other way, and you note that in the README.

> **Resources.** Self-hosted GitLab CE is memory-hungry — give it at least ~4 GB of RAM, and with Keycloak, Grafana and (for dynamic runners) a local cluster on top — preferably more.
>
> **If one machine isn't enough — team up.** Get a few people together, set up a local network between the laptops, and distribute the services across different machines: for example, GitLab on one, Keycloak on another, Grafana on a third. This isn't a compromise but, on the contrary, a setup that is **closer to real operations**: companies don't usually place different applications on one virtual machine — they run on separate hosts and communicate over the network. Along the way you'll figure out in practice how services find each other over the network, use real addresses and ports instead of `localhost`, and set up network access between hosts.

## Part 1 — Single sign-on into GitLab and Grafana (Keycloak)

We start with access — with how people actually log into the tools.

- Stand up **GitLab CE** and **Keycloak** (through configuration).
- In Keycloak, create a **realm** and one **client** each for GitLab and Grafana (the **OIDC** protocol).
- Configure **login to GitLab via Keycloak** (in GitLab this is an external OmniAuth OpenID Connect provider — supported in the free CE) and **login to Grafana via Keycloak** (OIDC).
- Create one test user in Keycloak and **log in as them to both GitLab and Grafana with a single login** — not through the tools' local accounts.

In the README describe: what a realm and a client are in your setup, how each tool trusts Keycloak to handle login, and what happens step by step on login (the redirects).

## Part 2 — nginx as a boundary in front of GitLab

Now we'll put GitLab behind an external nginx — and not just as a proxy, but with **access control**.

- Put an **external nginx** in front of GitLab as a reverse proxy with **TLS termination** (a self-signed certificate, redirect from 80 to 443).
- Configure **access rules** — choose at least two and justify them:
  - restrict access to the admin area (`/admin`) and/or to the **container registry** to your network/IP only;
  - put **rate limiting** on the login page (protection against brute force);
  - lock down or restrict from the outside whatever isn't needed there.
- Verify that ordinary pages open as before, while the locked-down ones are reachable only from an allowed address or with a rate limit.

In the README describe: what exactly you locked down and how, and why this matters for a real GitLab.

## Part 3 — CI/CD: static and dynamic runners

The most substantial part. We'll compare the two runner types in practice — and not abstractly, but on your own service's jobs.

**Step 1. Stand up both runner types.**
- Register a **static runner** — always running, usually with the `docker` executor.
- Set up **dynamic (ephemeral) runners** that are created per job and terminate afterwards. The method is **your choice**:
  - **kubernetes executor** (a local cluster: minikube/kind) — each job (job) runs in a new pod; with `kubectl` you can watch pods get created per job and terminate after it finishes;
  - **GitLab Runner Autoscaler** (fleeting/docker) — autoscaling without Kubernetes.

**Step 2. First decide which runner suits which jobs.**
Before writing the pipeline, think about the nature of each runner type: a static one has no startup delay but always occupies resources and its environment persists between jobs; a dynamic one doesn't start instantly, but it scales under load, gives a clean environment for every job, and doesn't sit idle. Based on this, **decide for yourself which jobs in your pipeline are better given to dynamic runners and which to the static one**, and write that decision with a justification in the README (before implementing it).

**Step 3. Design the pipeline around that decision.**
Write a **`.gitlab-ci.yml`** for your service so that it builds a Docker image and publishes it to GitLab's built-in **container registry**, with the jobs **split across runners by tags according to your decision from step 2**. There should be several jobs, and at least some able to run in parallel.

**Step 4. Verify in practice.**
Run the pipeline so that **several jobs execute at once**, and watch the difference: dynamic runners are created under load and terminate, while the static one stays the same. Compare with your hypothesis from step 2 — did your split of jobs hold up, or would you change something.

In the README describe: how you registered both types, your split of jobs across runners **with a justification**, what you observed under load, and the conclusion — **when a static runner is better and when a dynamic one is** (idle resources, startup speed, isolation, scale).

## Part 4 — Monitoring (mandatory)

**Choose one of the three platform systems — nginx, GitLab or Keycloak — and set up monitoring for it.** **Decide yourself which metrics matter on the dashboard**, build the dashboard in Grafana (the same one that's already behind single sign-on), and then **pick 3 metrics you'd build alerts on**, and explain your choice — what each one catches and what it threatens.

If the chosen system doesn't expose metrics in Prometheus format itself — set up a separate exporter for it.

## What to submit

1. **The service code** with a Dockerfile and **`.gitlab-ci.yml`** (with tags for the different runners).
2. **`README.md`** — how you set up single sign-on into GitLab and Grafana via Keycloak (realm, client); the nginx config (reverse proxy, TLS and the **access rules**); how you registered the static and dynamic runners and what you saw under load (the static vs dynamic conclusion); your dashboard and the rationale for the 3 alert metrics.
3. **Your configs** — whatever brought it all up (Docker configuration / Helm values / manifests), the nginx config, the Keycloak realm export (if you did one).
4. **Screenshots**: the Keycloak login screen when signing into GitLab and Grafana, a zone locked down with nginx (access denied from outside), the pipeline with jobs on different runners, dynamic runners or pods under load, the monitoring dashboard.

## How to start

Open this repository with your AI assistant and ask for help with **Lab 6**. The assistant is set up to guide you **step by step** and check your understanding — it deliberately won't hand out a finished solution. Start with Part 1 (single sign-on), then the nginx boundary, runners and monitoring.

> **Using AI?** Make sure your assistant follows the repository rules in [`AGENTS.md`](../AGENTS.md). Most tools pick it up automatically; if yours didn't — just point it at this file and ask it to follow it.
