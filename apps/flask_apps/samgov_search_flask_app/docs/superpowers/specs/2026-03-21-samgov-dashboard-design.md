# SAM.gov Search App - Enhanced Dashboard Design Spec

**Date:** 2026-03-21
**Project:** SAM.gov Federal Contract Opportunity Search - Flask Application Enhancement
**Status:** Approved for Implementation

---

## 1. Concept & Vision

Transform the current SAM.gov search app into a **data analysis workstation** where users can:
1. Download full opportunity data with all API fields
2. Switch between 3 analysis perspectives (Operativo, Mercado, Oportunidades)
3. Freely filter, arrange, and depurate columns before export
4. Each user maintains their own SAM.gov API key in settings

The app prioritizes **simplicity in code** and **flexibility in data manipulation** over visual complexity.

---

## 2. Design Language

### Aesthetic Direction
Government-style professional interface with clean Bootstrap 5 components. Minimal decorative elements - focus on data density and usability.

### Color Palette
- **Primary:** `#003366` (SAM.gov Navy)
- **Secondary:** `#6c757d` (Bootstrap Gray)
- **Success:** `#28a745` (Green for Active status)
- **Warning:** `#ffc107` (Amber for expiring soon)
- **Danger:** `#dc3545` (Red for Archived/Closed)
- **Background:** `#f8f9fa` (Light Gray)
- **Text:** `#212529` (Dark Gray)

### Typography
- **Font:** System Bootstrap fonts (no custom fonts)
- **Headings:** Bootstrap defaults, bold
- **Data Table:** Monospace-friendly for codes/numbers

### Motion Philosophy
- Minimal animations - tab switches are instant
- Loading spinners for API calls
- No decorative transitions

---

## 3. Layout & Structure

### Overall Architecture
```
┌─────────────────────────────────────────────────────┐
│  HEADER: Logo | Dashboard | History | Settings | Logout│
├─────────────────────────────────────────────────────┤
│  SEARCH FORM: Date Range + Filters + [Query API]   │
├─────────────────────────────────────────────────────┤
│  METRICS ROW: Total | Active | NAICS Types | Top State│
├─────────────────────────────────────────────────────┤
│  TABS: [Operativo] [Mercado] [Oportunidades]      │
├─────────────────────────────────────────────────────┤
│  ACTION BAR: [Column Tags] [Export CSV] [Export Excel]│
├─────────────────────────────────────────────────────┤
│                 DATA TABLE (80% viewport height)     │
│  - Filter inputs per column                         │
│  - Sort by clicking headers                         │
│  - Pagination: 25/50/100                            │
└─────────────────────────────────────────────────────┘
```

### Responsive Strategy
- Desktop (>1200px): Full layout
- Tablet (768-1199px): Stacked cards, scrollable table
- Mobile (<768px): Single column, horizontal scroll for table

---

## 4. Features & Interactions

### 4.1 User Settings (API Key Management)

**Location:** `/settings` route, accessible from navbar

**Fields:**
- API Key input (password type, with show/hide toggle)
- "Test Connection" button - validates key with SAM.gov API
- Status indicator: Success (green) / Failed (red message)
- Save button (disabled until validated)

**Behavior:**
- On page load, if user has saved API key, pre-fill field (masked)
- Test Connection calls `/api/check_api_key` with user's key
- Success: Enable Save button, show success message
- Failure: Show error message, disable Save
- On Save: Update user's API key in database, redirect to dashboard

### 4.2 Data Download (API Query)

**Trigger:** "Query API" button on dashboard

**Behavior:**
1. User sets search criteria (date range required, others optional)
2. Click "Query API" → Loading spinner
3. API returns all records (up to 1000) with ALL fields
4. Data stored in session (and optionally cached for reuse)
5. Automatically display in data table with default columns

**Search Form Fields:**
- Date Range: postedFrom, postedTo (required)
- Procurement Type: ptype (dropdown, multi-select)
- Set-Aside Type: typeOfSetAside (dropdown)
- Title Keywords: title (text)
- Organization: organizationName (text)
- State: state (dropdown - US states)
- NAICS Code: ncode (text, 6 digits)
- Classification Code: ccode (text)
- Status: status (dropdown: active, inactive, archived)

### 4.3 Three Analysis Views (Tabs)

#### Tab 1: OPERATIVO (Operational)
*Focus: Status tracking and immediate action items*

**Metrics Cards:**
1. Total Opportunities (count)
2. Active Opportunities (count + %)
3. Archived (count)
4. Closing This Week (count)
5. Closing This Month (count)
6. Top Agency (name + count)

**Quick Filter:** "Closing Soon" (deadline ≤ 7 days)

#### Tab 2: MERCADO (Market)
*Focus: Market intelligence and trends*

**Metrics Cards:**
1. Total Opportunities
2. Unique NAICS Codes (count)
3. Unique Agencies (count)
4. Top NAICS (code + count)
5. Top Set-Aside Type (name + count)
6. Top State (name + count)

**Quick Filter:** NAICS code search

#### Tab 3: OPORTUNIDADES (Opportunities)
*Focus: Targeting specific opportunities*

**Metrics Cards:**
1. Total Opportunities
2. With Award Amount (count)
3. Total Award Value (sum if available)
4. Top Set-Aside Opportunities (8(a), HUBZone, SDVOSB, WOSB)
5. Open Solicitations (count)
6. Average Response Time (days from posted to deadline)

**Quick Filter:** "Has Award Amount" checkbox

### 4.4 Data Table Features

**Column Management (Tag-style):**
- "Columns" button shows active columns as tags
- X on tag removes from view
- "Add column" dropdown to add more

**Table Interactions:**
- Click header to sort (asc/desc toggle)
- Filter input below each column header
- Pagination: 25/50/100 rows per page selector

**Export Functionality:**
- "Export CSV" - downloads current filtered/arranged data
- "Export Excel" - downloads as .xlsx with 3 sheets (one per tab), headers bold, freeze row, auto-sized columns
- Export respects: visible columns, applied filters, sort order

### 4.5 Search Form vs. Table Filters

**Server-side (Search Form):**
- Initial data pull from SAM.gov API
- Date range, NAICS, type, set-aside, keywords
- Only way to get new data from API

**Client-side (Table):**
- Filter among already-downloaded data
- Column visibility
- Sort order
- Does NOT re-query API

---

## 5. Component Inventory

### 5.1 Header Component
- Logo/Brand (left)
- Nav items: Dashboard, History, Settings
- User email display
- Logout button
- **States:** Authenticated only (no header on login page)

### 5.2 Metrics Card
- Large number/metric
- Label text
- **States:** Loading (spinner), Loaded, Empty (N/A)

### 5.3 Tab Bar
- Three tabs with text labels
- Active tab highlighted (primary color)
- **States:** Default, Hover, Active

### 5.4 Action Bar
- Column tags display
- Export CSV button
- Export Excel button
- **States:** Default, Loading (during export)

### 5.5 Data Table
- Sticky header row
- Sortable column headers (with arrows)
- Filter input row
- Pagination footer
- **States:** Loading, Empty ("No data - run a search"), Populated

### 5.6 Settings Form
- API Key input (with reveal toggle)
- Test Connection button
- Validation status indicator
- Save button
- **States:** Initial, Testing, Valid, Invalid, Saving, Saved

---

## 6. Technical Approach

### 6.1 Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Redirect to dashboard or login |
| `/login` | GET/POST | Authentication |
| `/logout` | GET | Clear session |
| `/dashboard` | GET | Main view with search form and data table |
| `/search` | POST | Query SAM.gov API, store in session |
| `/export/csv` | GET | Export current data as CSV |
| `/export/excel` | GET | Export current data as Excel |
| `/history` | GET | Past searches list |
| `/repeat_search/<id>` | GET | Repeat historical search |
| `/settings` | GET/POST | User API key management |
| `/api/check_api_key` | POST | Validate API key with SAM.gov |

### 6.2 Data Flow

```
1. User logs in → Load user's API key from DB (if exists)
2. User configures search → POST to /search
3. /search calls SAM.gov API with user's API key
4. Full response stored in session['search_results']
5. Dashboard displays data in table with default columns
6. User switches tabs → Same data, different metrics/quick filters
7. User toggles columns → Updates session['visible_columns']
8. User applies table filters → JavaScript filters displayed rows
9. User exports → /export/csv or /export/excel with current filters
```

### 6.3 Database Changes

**User Model Update:**
- Add `sam_api_key` field (String, nullable)

### 6.4 Frontend Libraries

- **Bootstrap 5:** UI framework
- **DataTables.js:** Enhanced table with sorting, filtering, pagination
- **SheetJS (xlsx):** Excel export
- **No charting library:** Keep it simple

### 6.5 Key Implementation Notes

1. **No client-side charting** - Use CSS for distributions
2. **DataTables.js** for table handling (sorting, filtering, pagination built-in)
3. **pandas + openpyxl** for server-side Excel generation
4. **JavaScript filter inputs** below table headers for per-column filtering
5. **Column visibility** managed via DataTables column().visible() API

---

## 7. Default Column Configuration

### Default Columns (Initial View - 10)
1. Title
2. Solicitation Number
3. Status
4. Posted Date
5. Response Deadline
6. Agency
7. Set-Aside
8. NAICS Code
9. Location (City)
10. Point of Contact Name

### All Available Columns (30)
1. Title
2. Solicitation Number
3. Notice ID
4. Status
5. Posted Date
6. Response Deadline
7. Agency
8. Full Parent Path Name
9. Set-Aside
10. Set-Aside Code
11. NAICS Code
12. Classification Code
13. Procurement Type
14. Base Type
15. Location (City)
16. Location (State)
17. Location (Zip)
18. Point of Contact Name
19. Point of Contact Email
20. Point of Contact Phone
21. Award Amount
22. Award Date
23. Award Number
24. Awardee Name
25. Awardee UEI
26. Office City
27. Office State
28. Description
29. UI Link
30. Resource Links

---

## 8. Implementation Phases

### Phase 1: Foundation
- Settings page with API key validation
- Search form with all SAM.gov filters
- Session-based data storage

### Phase 2: Data Table
- DataTables.js integration
- Column selector (Tag-style)
- Client-side filtering and sorting

### Phase 3: Analysis Views
- Three tabs with metrics
- Quick filters per tab
- Export to CSV/Excel

### Phase 4: Polish
- Error handling
- Empty states
- Loading states
- Responsive design
