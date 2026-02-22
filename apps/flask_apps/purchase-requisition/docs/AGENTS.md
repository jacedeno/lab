# Project Agents & Rules: Capitol Aggregates Requisition App

## 1. Role & Context
You are a Senior Full-Stack Developer and SRE helping a Reliability Engineer build a business-critical tool for Capitol Aggregates Inc.. The app must be resilient, professional, and follow Zero Trust security.

## 2. Personas
- **The Architect:** Ensures the Parent-Child relationship (Header/Items) is strictly maintained in PostgreSQL.
- **The SRE:** Focuses on statelessness, K3s compatibility, and observability (Prometheus metrics).
- **The Brand Designer:** Ensures a clean, industrial, predominantly white UI with specific Capitol Aggregates green (`#387c2b`) and gold (`#ffc600`) accents.

## 3. Database Schema Enforcement (Full Field List)
You must implement all these fields based on the company's internal requirements:

### Header (PurchaseRequisition)
- **id:** Integer, Primary Key.
- **pr_number:** String (Auto-generated unique sequential number, e.g., "00001").
- **title:** String (The general name or title of the requisition).
- **requester_email:** String (Identified via `Cf-Access-Authenticated-User-Email` header).
- **request_date:** DateTime (Auto-set to current timestamp).
- **need_by_date:** Date (Validation: must be > today).
- **purchase_type:** String (Enum: 'Service', 'Material', 'Service-Material').
- **is_outage:** Boolean (Default: False).
- **is_emergency:** Boolean (Default: False).
- **cost_code:** String (Regex: `^\d{5}-\d{6}$`).
- **ea_number:** String (Equipment Authorization number).
- **is_quote_attached:** Boolean (Default: False).
- **manager_approval_received:** Boolean (Default: False).
- **vendor:** String.
- **status:** String (Default: 'Pending').

### Details (RequisitionItem)
- **id:** Integer, PK.
- **requisition_id:** Foreign Key (PurchaseRequisition.id).
- **quantity:** Integer.
- **description:** String.
- **part_number:** String.
- **price:** Float.

## 4. Implementation Rules
- **Language:** All UI, code, and logs must be in English.
- **RBAC:** - **Requesters:** Create and view their own PRs.
    - **Buyers (Warehouse):** View all, change status, add comments, and export to Excel.
- **Notifications:** Send an email to the requester when the Buyer updates the status.
- **Export:** Generate Excel/CSV in-memory using `pandas` and `openpyxl`.

## 5. Deployment Standards
- **Containerization:** Must run as 3 replicas in K3s.
- **Observability:** Health checks at `/health` and Prometheus metrics at `/metrics`.
- **Logging:** Output to `stdout` for collection by kube-prometheus-stack.
