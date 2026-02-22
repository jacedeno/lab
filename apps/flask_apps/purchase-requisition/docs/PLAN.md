# Project Execution Plan: Capitol Aggregates Requisition App

## Phase 0 — Scaffolding & Configuration
| Step | Deliverable | Details |
|------|-------------|---------|
| 0.1 | Project skeleton | `app.py`, `config.py`, `requirements.txt`, `Dockerfile`, `docker-compose.yml` (local dev) |
| 0.2 | Tailwind CSS setup | `tailwind.config.js` with Capitol Aggregates brand tokens (`ca-green: #387c2b`, `ca-gold: #ffc600`), plus a white-dominant design system |
| 0.3 | Flask app factory | `create_app()` pattern with blueprints, env-based config (`Dev`, `Prod`), structured logging to `stdout` |
| 0.4 | Database init | SQLAlchemy models, Flask-Migrate for Alembic migrations, PostgreSQL connection via `DATABASE_URL` env var |

## Phase 1 — Data Layer
| Step | Deliverable | Details |
|------|-------------|---------|
| 1.1 | `PurchaseRequisition` model | All header fields per spec. `pr_number` auto-generated as zero-padded sequential (`00001`). `status` default `Pending`. |
| 1.2 | `RequisitionItem` model | Child table with FK to `PurchaseRequisition.id`, cascade delete. Fields: `quantity`, `description`, `part_number`, `price`. |
| 1.3 | `Comment` model | Append-only, buyer-only. Child of PR with timestamp and author email. No edit/delete. |
| 1.4 | Atomic save logic | All-or-nothing transaction: Header + all Items in a single `db.session`. Full rollback on any validation failure. PR numbers use PostgreSQL SEQUENCE (gaps acceptable). |
| 1.5 | Initial migration | `flask db init && flask db migrate && flask db upgrade` |

## Phase 2 — Authentication & RBAC
| Step | Deliverable | Details |
|------|-------------|---------|
| 2.1 | Auth middleware | Read `Cf-Access-Authenticated-User-Email` header on every request. Fallback: `DEV_USER_EMAIL` env var for local dev. |
| 2.2 | Role resolution | Buyer emails defined via `BUYER_EMAILS` env var (comma-separated allowlist). All other authenticated users are Requesters. |
| 2.3 | `@buyer_required` decorator | Protects buyer-only routes (status change, comments, export). |
| 2.4 | Jinja context injection | `current_user_email` and `is_buyer` available in every template. |

## Phase 3 — Requester Workflow (UI + API)
| Step | Deliverable | Details |
|------|-------------|---------|
| 3.1 | **New PR form** (`/pr/new`) | Header fields form with client-side + server-side validation: `need_by_date > today`, `cost_code` regex `^\d{5}-\d{6}$`. |
| 3.2 | Dynamic item rows | JavaScript "Add Item" / "Remove Item" rows within the same form. Submitted as a JSON array or indexed form fields. |
| 3.3 | Manager Approval field | Simple Yes/No toggle. Informational only — does not block submission. |
| 3.4 | **My PRs list** (`/pr/mine`) | Table of the requester's own PRs with status badge, date, and title. Filterable/sortable. |
| 3.5 | **PR Detail view** (`/pr/<id>`) | Read-only view of header + items for the requester. |

## Phase 4 — Buyer Workflow (UI + API)
| Step | Deliverable | Details |
|------|-------------|---------|
| 4.1 | **All PRs dashboard** (`/pr/all`) | Full table of all PRs. Search, filter by status, date range. |
| 4.2 | **PR Detail + Actions** (`/pr/<id>`) | Buyer sees same detail view but with: status dropdown, comment box, save button. |
| 4.3 | Status change logic | Update status, log the change, trigger email notification to requester. |
| 4.4 | Comment system | Buyer adds timestamped comments visible on the PR detail view. |
| 4.5 | **Export** (`/pr/export`) | Generate Excel/CSV in-memory via `pandas` + `openpyxl`. Buyer selects PRs or date range to export. |

## Phase 5 — Notifications (Stubbed)
| Step | Deliverable | Details |
|------|-------------|---------|
| 5.1 | Email interface | Pluggable `send_notification()` function with SMTP env var config. **Stubbed with logging** — logs email content to stdout instead of sending. Ready to wire up when SMTP is available. |
| 5.2 | Status change trigger | On buyer status update, call `send_notification()` with PR number, new status, requester email, and comment. |

## Phase 6 — Observability & Ops
| Step | Deliverable | Details |
|------|-------------|---------|
| 6.1 | `/health` endpoint | Returns `{"status": "ok"}` with DB connectivity check. |
| 6.2 | `/metrics` endpoint | Prometheus-compatible metrics via `prometheus_flask_instrumentator` or similar. |
| 6.3 | Structured logging | JSON logs to `stdout` for kube-prometheus-stack collection. |

## Phase 7 — Containerization & K3s Deployment
| Step | Deliverable | Details |
|------|-------------|---------|
| 7.1 | `Dockerfile` | Multi-stage build, non-root user, gunicorn entrypoint. |
| 7.2 | K3s manifests | `Deployment` (3 replicas), `Service`, `Ingress`, `ConfigMap`, `Secret`, `PVC` for PostgreSQL if self-hosted. |
| 7.3 | Cloudflare Tunnel integration | Annotations/config for Zero Trust access. |

---

## Decisions Log

| Q# | Topic | Decision |
|----|-------|----------|
| Q1 | Manager Approval UX | **Simple Yes/No toggle** |
| Q2 | Manager Approval gating | **Informational only** — does not block submission |
| Q3 | Buyer role resolution | **Environment variable allowlist** (`BUYER_EMAILS`) |
| Q4 | Local dev auth fallback | **`DEV_USER_EMAIL` env var** |
| Q5 | Item validation strategy | **All-or-nothing** — entire submission rejected on any error |
| Q6 | PR number gap policy | **Gaps acceptable** — use PostgreSQL SEQUENCE |
| Q7 | Tailwind color strategy | **Custom tokens** — `bg-ca-green`, `text-ca-gold` (default palette preserved) |
| Q8 | Tailwind delivery method | **CDN** — inline config with custom colors |
| Q9 | Email service availability | **Stub for later** — pluggable interface with logging |
| Q10 | Comment system scope | **Append-only, buyer only** — no edit/delete, requester read-only |
