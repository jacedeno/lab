# Project Specification: Capitol Aggregates Requisition App

## 1. Visual Identity & Branding
- **Company Name:** Capitol Aggregates Inc.
- **Design Philosophy:** Clean, predominantly white "Enterprise" look with strategic green and gold accents.
- **Colors:**
  - **Brand Green (Primary):** `#387c2b` (Navbar, primary actions).
  - **Brand Gold (Secondary):** `#ffc600` (Accents, warnings).
- **Logo:** Displayed top-left from `/static/images/logo.png`.

## 2. Technical Stack
- **Backend:** Flask (Python) with SQLAlchemy.
- **Database:** PostgreSQL (High Availability in K3s).
- **Auth:** Zero Trust via Cloudflare Tunnel (`Cf-Access-Authenticated-User-Email`).
- **Infrastructure:** Containerized (3 replicas) on K3s cluster.

## 3. Data Schema & Forms

### Header (Filled by Requester)
- **pr_number:** Auto-generated (e.g., "00001").
- **title:** Short descriptive name for the PR (e.g., "Lubricants").
- **requester_email:** Captured from header.
- **request_date:** Auto-set to current time.
- **need_by_date:** Date picker (Must be in the future).
- **purchase_type:** Enum ('Service', 'Material', 'Service-Material').
- **is_outage:** Boolean toggle.
- **is_emergency:** Boolean toggle.
- **cost_code:** String (Validation: `#####-######`).
- **ea_number:** Equipment Authorization number.
- **is_quote_attached:** Boolean (Yes/No).
- **manager_approval_received:** Boolean/Select. Requester indicates "Yes" if approved or "No" if approval wasn't required for this amount.
- **vendor:** Target vendor for the purchase.
- **status:** Default "Pending".

### Details (The Requisition Items)
*Note: Requester adds these to the PR; Buyer uses this table for processing.*
- **quantity:** Numerical amount.
- **description:** Material or service details.
- **part_number:** Manufacturer part number.
- **price:** Estimated unit price.

## 4. Workflow & Roles
- **Requester Side:** Fill header -> Add items to table -> Submit.
- **Buyer Side:** Full visibility of Header + Item Details for all PRs.
- **Capabilities:** Change status, add comments, and export selected data to Excel/CSV.
- **Notifications:** Automatic email to requester upon status changes.
