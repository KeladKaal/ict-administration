# Lecture 6 — GitLab, nginx and access

This lecture is about the infrastructure devops keeps running for the development team: where the code lives and how it's built (GitLab + CI/CD), how requests reach the services (nginx), and how single sign-on into the internal tools works (Keycloak).

This README works as a **self-contained summary**. Three parts: *GitLab and CI/CD from the administration side*, *nginx*, *access and single sign-on (Keycloak)*. Examples use the familiar **grocery delivery** app: its services are developed, built and deployed through this infrastructure.

---

## Part 1 — GitLab and CI/CD (from the administration side)

### What GitLab is

> **GitLab** is a platform for the whole lifecycle of code: git repository hosting, **CI/CD**, a container registry, issues and more. It comes cloud-hosted (GitLab.com) and **self-hosted** — when a company stands up its own instance.

Developers push code and write pipelines; **devops stands up and maintains GitLab itself** and everything around it.

### CI/CD: pipelines and jobs

- **Pipeline** — a chain of automatic steps on every push/merge: build → test → deploy.
- **Stages and jobs** — stages and the tasks inside them.
- What to do is described in the **`.gitlab-ci.yml`** file in the repository — developers write it.

The idea: a commit automatically turns into a built and deployed service, with no manual builds.

### Runners (the devops zone)

> **GitLab Runner** — an agent that **executes the pipeline's jobs**. GitLab itself only orchestrates; the work is done by runners.

What devops configures:

- **shared vs specific** — runners shared across all projects or dedicated to a specific one;
- **executors** — how a runner executes a job: `docker` (each job in a container — the most common), `shell`, `kubernetes`;
- **registration** of a runner to the GitLab instance, scaling under load.

### Container registry

GitLab has a built-in **Docker image registry**: the pipeline builds the service's image and puts it in the registry, from where it's later deployed. devops watches access and disk space (images pile up).

### Where devops fits in

Deploy and update self-hosted GitLab, stand up and scale runners, set up the registry, back things up (repositories are data too), watch resources. Developers just use it.

---

## Part 2 — nginx

### What nginx is

> **nginx** — a web server most often used as a **reverse proxy** and load balancer in front of services.

### Reverse proxy

A reverse proxy is a single entry point: the client knocks on nginx, and it proxies the request to the right service in the internal network. The benefits: backends are hidden, you can route by path/domain (`/api` → one service, `/` → another) and add headers.

### Load balancing

If a service runs in several instances, nginx spreads requests among them (round-robin and other strategies) — this handles load and survives the failure of one instance.

### TLS termination

HTTPS usually "ends" right at nginx: it holds the certificates, decrypts TLS, and then talks to the services over the internal network. Managing certificates centrally, in one place, is convenient.

### Where devops fits in

Write and maintain the config (upstreams, routes, TLS), renew certificates, watch availability. For a developer nginx is transparent — they just know the entry address.

---

## Part 3 — Access and single sign-on (Keycloak)

### The problem

There are many internal tools: GitLab, Grafana, Kibana, n8n… If each has its own users and passwords, it's chaos: onboarding a new employee means 10 accounts, offboarding means revoking access 10 times, and everyone has a different password everywhere. You need **single sign-on**.

### What Keycloak is

> **Keycloak** — an open-source identity and access management (IAM) system. It provides **single sign-on (SSO)** into all applications via the standard **OIDC** (OpenID Connect) and **SAML** protocols.

Key concepts:

- **realm** — an isolated space (for example, "company employees");
- **client** — an application that trusts Keycloak to handle login (GitLab, Grafana as OIDC clients);
- **users, roles** — the users and their roles.

### How SSO works

The user logs in **once** to Keycloak; after that the applications (GitLab, Grafana) redirect them there on login and receive confirmation of their identity. Onboarding/offboarding an employee happens in one place; there's a single password.

### Directory and federation

Keycloak can store users itself, but it can also **federate** with an external directory:

- **LDAP** — the user directory protocol;
- **FreeIPA** — an open-source "AD for Linux" (LDAP + Kerberos + host management);
- **Active Directory** — the corporate standard (the Windows world).

So Keycloak is about **logging into applications (SSO/IdP)**, while LDAP/FreeIPA/AD are about **the user directory itself**; the two are often connected.

### Where devops fits in

Stand up and maintain Keycloak, create a realm and connect applications as clients (GitLab, Grafana via OIDC), set up roles, and if needed — federation with LDAP/AD. After that the whole team logs in with a single account.

---

## Key takeaways

- **GitLab** — repositories + CI/CD + registry; self-hosted is maintained by devops. Runners (executors, shared/specific) execute the pipeline's jobs.
- **nginx** — a reverse proxy: single entry point, load balancing, TLS termination.
- **Keycloak** — single sign-on (SSO) into the internal tools via OIDC/SAML; can federate with LDAP/FreeIPA/AD.
- All of this is infrastructure that devops stands up for the team, and developers simply use it.

---

## Lab

**[Lab 6 — The team's internal GitLab: single sign-on, an nginx boundary, and runners](lab.md)**

You stand up and protect a self-hosted **GitLab**: login to GitLab and Grafana goes through single sign-on with **Keycloak** (OIDC); in front of GitLab there's an **nginx** that's not just a proxy but a boundary with TLS and access rules (lock down the admin area/registry, rate-limit login); in CI/CD you compare **static and dynamic (ephemeral) runners**. On top of it all — the mandatory monitoring: your own dashboard and 3 metrics to alert on.
