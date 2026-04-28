# Backlog — Solo Companion
**Last updated:** 2026-04-28 · Round 2
**Project status:** In Design Review

---

## At a Glance

### Slice Status
| Status | Count |
|--------|-------|
| 🔄 In Review | 0 |
| ✅ Ready | 24 |
| 🔬 Blocked | 0 |
| ⏸ Deferred | 0 |
| 🔨 In Build | 0 |
| 🔍 In QA | 0 |
| 🧪 In Test | 0 |
| ✓ Done | 0 |

### Traffic
| | |
|---|---|
| **Currently in build** | — |
| **Next up (Ready, not started)** | SL-001, SL-002, SL-003 |
| **Blocked — waiting on** | — |
| **Open spikes** | — |

*Phases and deliverables added when prd-to-plan runs.*

---

## Slice Detail

---

### SL-001 · App Startup and Server

Status: Ready
Phase: Pending prd-to-plan
Deliverable: Pending prd-to-plan

Plain language description:
The companion app starts automatically when the Mac logs in and runs silently in the background. When the solo opens their browser and goes to the companion's local address, the app is already there — no manual launch required.

Technical description:
Flask server on a fixed port (8710 — next available in the ~/Apps suite). LaunchAgent plist registered at ~/Library/LaunchAgents/com.scotth.solocompanion.plist, same pattern as the existing app suite. Server entry point at app.py. Routes defined for: / (dashboard), /project/<name> (project detail). No external packages beyond Flask.

Design anchor: sprint-01-dashboard.html — full app shell
Data anchor: Pending data-scaffold
Process anchor: Open Solo Companion app → B (main path) · infrastructure

References:
  - ~/Apps/CLAUDE.md — LaunchAgent pattern and port convention for this app suite
  - ~/Library/LaunchAgents/ — existing plist files for reference

Done criteria:
  - Server starts on login without manual intervention
  - http://localhost:8710 returns the dashboard with no errors
  - Server restart recovers cleanly without data loss

Self-verification checklist:
  - Confirm LaunchAgent plist is registered and server starts on login simulation
  - Confirm dashboard route returns HTTP 200
  - Confirm /project/<name> route returns HTTP 200 for a known project name

Builder confirmation:
Pending build

Depends on: none
Notes: Port 8710 chosen as next available after the existing suite (8700–8765). Confirm no conflict before build starts.

---

### SL-002 · Sync on Open — Project Discovery

Status: Ready
Phase: Pending prd-to-plan
Deliverable: Pending prd-to-plan

Plain language description:
Every time the solo opens the companion app, it reads the framework's project registry to discover all active projects and their locations on disk. The solo never has to tell the companion where projects live — it finds them automatically.

Technical description:
On each request to / (dashboard), trigger a sync pass. Read ~/Developer/engineering-playbook/projects.md — parse the markdown table to extract project name and path for every registered project. Store discovered projects in SQLite projects table. Record sync timestamp. If a project path no longer exists on disk, mark it inactive rather than deleting — preserves history. Framework path is set once at install time (config file or environment variable).

Design anchor: sprint-01-dashboard.html — last synced timestamp, sidebar project list
Data anchor: Pending data-scaffold
Process anchor: Dashboard loads — syncs from framework files → C (main path) · infrastructure

References:
  - ~/Developer/engineering-playbook/projects.md — the registry file being parsed
  - docs/continuity/handoff.md — sync model decision: sync on open + manual refresh

Done criteria:
  - All projects in projects.md appear in the sidebar after sync
  - Sync timestamp updates correctly on each open
  - A project path that no longer exists is marked inactive, not deleted

Self-verification checklist:
  - Add a test project to projects.md and confirm it appears on next sync
  - Confirm sync timestamp reflects actual sync time
  - Confirm inactive marking works when a path is removed

Builder confirmation:
Pending build

Depends on: SL-001
Notes: Sync runs on every dashboard request in Phase 1 — no file watcher. This keeps the implementation simple and covers the primary use case (open app to orient before a session).

---

### SL-003 · Sync — Parse Framework Files and Populate SQLite

Status: Ready
Phase: Pending prd-to-plan
Deliverable: Pending prd-to-plan

Plain language description:
After discovering which projects exist, the companion reads each project's framework files and turns them into structured data the app can display. This is what makes the dashboard and project detail screens show real information — not just project names.

Technical description:
For each active project path, read and parse the following files:
  - docs/backlog.md → phases, deliverables, slices (status, IDs, names, review_url field)
  - docs/continuity/handoff.md → current phase, open right now items (flagged source), outstanding questions
  - docs/continuity/current-phase.md → current phase name and status
  - docs/continuity/decisions.md → decision and change log entries
  - docs/process/to-be-*.md → existence check only (surfaces in Materials)
  - docs/process/as-is-*.md → existence check only
  - docs/discovery-brief.md → existence check only
  - docs/design/sprint-*.html → existence check only (surfaces in Materials)

SQLite schema:
  projects(id, name, path, color, last_synced, is_active)
  phases(id, project_id, name, status, started_date, gate_status, progress_pct)
  deliverables(id, project_id, phase_name, name, status, type, slice_count)
  slices(id, project_id, phase_name, deliverable_name, slice_id, name, status, review_url, last_modified, is_blocked, is_flagged, flagged_reason)
  materials(id, project_id, phase_name, name, type, file_path)
  decisions(id, project_id, title, phase, date, body, why)
  changes(id, project_id, title, date, was_value, became_value)
  questions(id, project_id, text, source, who_can_answer, open_days)
  flags(id, project_id, text, object_type, object_id, flagged_reason)

Flagged item derivation rules (applied at parse time):
  1. Any slice with status In Progress whose file last-modified is more than 3 days ago → flagged, reason: "stale progress"
  2. Items in handoff.md "Open right now" section → flagged, reason: text of the item
  3. Items in handoff.md "Outstanding questions" section → questions table

Blocked item rule: any slice with status Blocked in backlog.md.

Design anchor: sprint-01-dashboard.html — Needs Attention section, bucket data
Data anchor: Pending data-scaffold
Process anchor: Dashboard loads — syncs from framework files → C (main path) · infrastructure

References:
  - ~/Developer/engineering-playbook/docs/records-spec.md — canonical backlog record format being parsed
  - docs/design/deferred-decisions.md — flagging derivation decisions

Done criteria:
  - All slices from backlog.md appear in SQLite with correct status after sync
  - Flagged items derived correctly per the three rules
  - Blocked items identified correctly from slice status
  - Materials table populated with correct file paths for all discovered files

Self-verification checklist:
  - Add a slice with Blocked status to a test backlog.md, confirm it surfaces as blocked in SQLite
  - Set a slice to In Progress with a last-modified date > 3 days, confirm it appears as flagged
  - Add an item to handoff.md "Open right now", confirm it appears in flags table
  - Confirm materials populated for a project with all expected file types

Builder confirmation:
Pending build

Depends on: SL-001, SL-002
Notes: This is the most complex slice in the build. The markdown parsing must be robust to minor formatting variations in the framework files — the framework does not enforce rigid formatting. Use section-header anchoring (## Section Name) rather than line-number-based parsing. When a section is not found, treat as empty — not an error.

---

### SL-004 · Sidebar — Project List, Recency, and Navigation

Status: Ready
Phase: Pending prd-to-plan
Deliverable: Pending prd-to-plan

Plain language description:
The left sidebar shows the list of all active projects, each with a colored dot and a recency indicator showing how recently the project was worked on. Clicking a project navigates to that project's detail page. The Views section at the top links to Dashboard and Activity Feed.

Technical description:
Render the sidebar from the projects table in SQLite. Color assigned by hashing project name against a fixed palette of 8 colors: #2563EB, #0D9488, #7C3AED, #D97706, #DC2626, #059669, #DB2777, #0891B2. Hash function: sum of char codes mod 8. Recency derived from the most recently modified file in the project's path (os.path.getmtime scan). Display as: "today" (<24h), "Nd" (N days ago), "Nw" (N weeks ago). Active project highlighted with color-matched left border. Activity Feed nav item links to /feed (Phase 2 — render a coming-soon placeholder at that route).

Design anchor: sprint-01-dashboard.html — sidebar, sprint-02-project-detail.html — sidebar with active state
Data anchor: Pending data-scaffold
Process anchor: See recency signals → H (main path) · Open companion app for cross-project check → U (main path)

References:
  - sprint-01-dashboard.html — sidebar design, color dot treatment, recency labels
  - ~/Apps/CLAUDE.md — dark theme color tokens (sidebar background matches suite)

Done criteria:
  - All active projects appear in sidebar with correct color dot
  - Recency label reflects actual last-modified time of project files
  - Clicking a project loads that project's detail page
  - Active project is visually distinguished in sidebar

Self-verification checklist:
  - Confirm color assignment is stable (same project always gets same color)
  - Confirm recency label updates correctly for a project modified today vs 3 days ago
  - Confirm clicking each project loads the correct project detail page

Builder confirmation:
Pending build

Depends on: SL-002, SL-003
Notes: Activity Feed route (/feed) renders a placeholder in Phase 1. Do not build the feed — just a page that says it's coming. The sidebar nav item should still appear and be clickable so the sidebar is complete.

---

### SL-005 · Dashboard Top Bar

Status: Ready
Phase: Pending prd-to-plan
Deliverable: Pending prd-to-plan

Plain language description:
The top of the dashboard shows the page title, a count of how many active projects are being tracked, when the data was last synced, and a refresh button the solo can click to pull the latest data from their framework files.

Technical description:
Top bar reads from: projects table (count of is_active=1 records), last_synced timestamp from most recent sync record. Refresh button POSTs to /sync, which triggers SL-002 + SL-003 re-run, then redirects to /. Display last synced as relative time using the same recency format as the sidebar.

Design anchor: sprint-01-dashboard.html — top bar
Data anchor: Pending data-scaffold
Process anchor: Dashboard loads — syncs from framework files → C (main path)

Done criteria:
  - Project count matches actual number of active projects in SQLite
  - Last synced time updates correctly after a refresh
  - Refresh button triggers a new sync and reflects updated data on return

Self-verification checklist:
  - Add a project to projects.md, click refresh, confirm count increments
  - Confirm last synced timestamp updates on each refresh click

Builder confirmation:
Pending build

Depends on: SL-002, SL-003
Notes: None.

---

### SL-006 · Needs Attention — Blocked Card

Status: Ready
Phase: Pending prd-to-plan
Deliverable: Pending prd-to-plan

Plain language description:
When any project has a slice that is blocked — meaning work cannot proceed until something is resolved — it appears in a red-tinted card at the top of the dashboard. Each blocked item shows the slice ID, what's blocking it, which project it belongs to, and how long it has been open. When there are no blocked items across any project, this card does not appear.

Technical description:
Query slices table WHERE is_blocked = 1 ORDER BY last_modified ASC. Render each as an action-item row with: slice_id, blocked_reason (from Notes field of slice record), project name with color dot, open_days derived from last_modified. Empty state: if query returns zero rows, render nothing — the Blocked card section is entirely absent from the DOM, not rendered as an empty container.

Design anchor: sprint-01-dashboard.html — Needs Attention Blocked card
Data anchor: Pending data-scaffold
Process anchor: See blocked items → F (main path)

Done criteria:
  - All blocked slices across all projects appear in the card
  - Card is absent entirely when no blocked slices exist
  - Each row shows slice ID, reason, project, and correct open duration
  - Clicking a row opens the slice overlay

Self-verification checklist:
  - Set a slice to Blocked in a test backlog.md, confirm it appears after sync
  - Confirm card is absent when no blocked slices exist
  - Confirm open_days calculates correctly

Builder confirmation:
Pending build

Depends on: SL-003, SL-011
Notes: Empty state means the card is not rendered — not rendered with a "no blocked items" message. The dashboard should feel clean when everything is unblocked.

---

### SL-007 · Needs Attention — Flagged Card

Status: Ready
Phase: Pending prd-to-plan
Deliverable: Pending prd-to-plan

Plain language description:
When any project has items that warrant attention — stale slices, open notes from the handoff file, or items the solo has flagged — they appear in an amber-tinted card on the dashboard. Each flagged item shows what the signal is, which project it came from, and what type of object it relates to. When there are nothing flagged across any project, this card does not appear.

Technical description:
Query flags table ORDER BY project_id, created_at. Render each as an action-item row with: flagged_reason, project name with color dot, object_type, object_id (if slice). Three derivation sources written at sync time (SL-003): stale In Progress slices (>3 days), handoff.md "Open right now" items, handoff.md "Outstanding questions." Empty state: card absent entirely when flags table is empty.

Design anchor: sprint-01-dashboard.html — Needs Attention Flagged card
Data anchor: Pending data-scaffold
Process anchor: See flagged items → G (main path)

Done criteria:
  - Stale In Progress slice (>3 days) appears as a flagged item after sync
  - "Open right now" items from handoff.md appear as flagged items
  - Card is absent entirely when flags table is empty
  - Clicking a flagged slice item opens the slice overlay

Self-verification checklist:
  - Set a slice to In Progress, set its last_modified to 4 days ago, confirm flag surfaces
  - Add an "Open right now" item to handoff.md, confirm it appears after sync
  - Confirm card is absent when flags table is empty

Builder confirmation:
Pending build

Depends on: SL-003, SL-011
Notes: "Outstanding questions" items appear in the questions table and surface on the project detail Action tab, not in the Flagged card on the dashboard. The dashboard Flagged card shows stale progress and open handoff items only.

---

### SL-008 · Dashboard — Phases Bucket

Status: Ready
Phase: Pending prd-to-plan
Deliverable: Pending prd-to-plan

Plain language description:
The Phases section of the dashboard shows every active build phase across all projects — one row per phase, with the project name, current phase name, and a progress bar showing how far through the slices the solo is.

Technical description:
Query phases table WHERE status = 'In Progress'. For each row: render project name (primary, with color dot), phase name (secondary), progress bar derived from (done_slices / total_slices * 100) calculated from slices table. Clicking any row opens the phase overlay. No filter control on this bucket — phases are few enough that showing all is appropriate.

Design anchor: sprint-01-dashboard.html — Phases bucket
Data anchor: Pending data-scaffold
Process anchor: See all active phases across all projects → E (main path)

Done criteria:
  - All In Progress phases across all projects appear with correct project name and phase name
  - Progress bar reflects actual slice completion ratio
  - Clicking a row opens the phase overlay

Self-verification checklist:
  - Confirm a phase in a test project appears in the bucket
  - Confirm progress bar updates after a slice status change and sync
  - Confirm row click opens phase overlay

Builder confirmation:
Pending build

Depends on: SL-003, SL-013
Notes: None.

---

### SL-009 · Dashboard — Deliverables Bucket with Project Filter

Status: Ready
Phase: Pending prd-to-plan
Deliverable: Pending prd-to-plan

Plain language description:
The Deliverables section of the dashboard shows deliverables that are currently being worked on across all projects. A filter lets the solo narrow the view to a single project. Each row shows the deliverable name, which project it belongs to, and its current status.

Technical description:
Query deliverables table WHERE status IN ('Active', 'Defined') ORDER BY project_id, name. Filter dropdown renders project names with color dots — selecting a project re-renders the list filtered by project_id. "All projects" is the default. Clicking a row opens the deliverable overlay.

Design anchor: sprint-01-dashboard.html — Deliverables bucket, filter dropdown
Data anchor: Pending data-scaffold
Process anchor: See all active deliverables across all projects → E (main path)

Done criteria:
  - All Active and Defined deliverables appear across projects by default
  - Project filter correctly narrows the list
  - Clicking a row opens the deliverable overlay

Self-verification checklist:
  - Confirm deliverables from two different projects both appear without filter
  - Confirm filter to one project shows only that project's deliverables
  - Confirm row click opens deliverable overlay

Builder confirmation:
Pending build

Depends on: SL-003, SL-012
Notes: None.

---

### SL-010 · Dashboard — Slices Bucket with Project Filter

Status: Ready
Phase: Pending prd-to-plan
Deliverable: Pending prd-to-plan

Plain language description:
The Slices section of the dashboard shows slices that are actively being worked on across all projects — In Progress, In QA, and In Test. A filter lets the solo narrow to one project. Each row shows the slice ID, name, project, and current status.

Technical description:
Query slices table WHERE status IN ('In Progress', 'In QA', 'In Test') ORDER BY project_id, slice_id. Project filter same pattern as SL-009. Clicking a row opens the slice overlay.

Design anchor: sprint-01-dashboard.html — Slices bucket, filter dropdown
Data anchor: Pending data-scaffold
Process anchor: See all active slices across all projects → E (main path)

Done criteria:
  - In Progress, In QA, and In Test slices appear across all projects by default
  - Project filter correctly narrows the list
  - Clicking a row opens the slice overlay

Self-verification checklist:
  - Confirm slices in two projects both appear without filter
  - Confirm Ready and Done slices do not appear in this bucket
  - Confirm row click opens slice overlay

Builder confirmation:
Pending build

Depends on: SL-003, SL-011
Notes: Ready slices are not shown here — they haven't started. Done slices are not shown — they're complete. This bucket is the "in flight" view only.

---

### SL-011 · Overlay — Slice Panel

Status: Ready
Phase: Pending prd-to-plan
Deliverable: Pending prd-to-plan

Plain language description:
When the solo clicks any slice — anywhere in the app — a panel slides over the current screen showing everything about that slice: its description, which project and deliverable it belongs to, its current status, the four anchors, and its quality gates. A button at the bottom takes the solo to that slice's project detail page.

Technical description:
Shared overlay component rendered server-side from the slices table. Fields displayed: slice_id, name, project (with color dot), status, deliverable, phase, plain language description, technical description, acceptance criteria, design anchor, data anchor, process anchor, done anchor, quality gate statuses (code review, QA sign-off, review link, builder confirmation — derived from slice status). "Take me to this project" button links to /project/<name>#slices. "Already on this project" state renders a disabled version of the button when the overlay is triggered from within that project's detail page. Backdrop click and ✕ button both dismiss.

Design anchor: sprint-01-dashboard.html — slice overlay panel (all fields)
Data anchor: Pending data-scaffold
Process anchor: infrastructure — shared overlay component used by multiple to-be steps

Done criteria:
  - All slice fields render correctly from SQLite data
  - "Take me to this project" navigates to the correct project
  - "Already on this project" state renders correctly on project detail pages
  - Backdrop click and ✕ both dismiss the overlay

Self-verification checklist:
  - Open a slice overlay from the dashboard and confirm all fields populated
  - Open a slice overlay from a project detail page and confirm "Already on this project" state
  - Confirm backdrop click dismisses without navigating

Builder confirmation:
Pending build

Depends on: SL-003
Notes: The four anchors section reads the anchor fields directly from the slice record. Quality gate statuses in Phase 1 are derived from slice status — not separate fields. A slice In Progress has code review and QA as pending. A slice Done has all four gates shown as confirmed.

---

### SL-012 · Overlay — Deliverable Panel

Status: Ready
Phase: Pending prd-to-plan
Deliverable: Pending prd-to-plan

Plain language description:
When the solo clicks a deliverable anywhere in the app, a panel appears showing the deliverable's description, which phase it belongs to, its status, and the list of slices within it with their current statuses.

Technical description:
Shared overlay component rendered from deliverables table + slices table JOIN. Fields: deliverable name, project (with color dot), status, phase, plain language description, technical description, acceptance criteria, slice list (slice_id, name, status for each). Same dismiss behavior as SL-011. "Take me to this project" links to /project/<name>#progress.

Design anchor: sprint-01-dashboard.html — deliverable overlay panel
Data anchor: Pending data-scaffold
Process anchor: infrastructure — shared overlay component

Done criteria:
  - All deliverable fields render correctly
  - Slice list within the overlay shows correct slice IDs, names, and statuses
  - Dismiss behavior matches slice overlay

Self-verification checklist:
  - Open a deliverable overlay from the dashboard and confirm all fields populated
  - Confirm the slice list reflects current slice statuses from SQLite

Builder confirmation:
Pending build

Depends on: SL-003
Notes: None.

---

### SL-013 · Overlay — Phase Panel

Status: Ready
Phase: Pending prd-to-plan
Deliverable: Pending prd-to-plan

Plain language description:
When the solo clicks a phase anywhere in the app, a panel appears showing the phase's description, gate status, a progress breakdown by slice status, and the list of deliverables within it.

Technical description:
Shared overlay component from phases table + deliverables table + slices table. Fields: phase name, project (with color dot), status, gate status, started date, previous phase, next phase, plain language description, technical description, acceptance criteria, 4-bucket count grid (Done/In Progress/In Test/Ready from slices table grouped by status), deliverables list (name and status). Dismiss behavior same as SL-011.

Design anchor: sprint-01-dashboard.html — phase overlay panel
Data anchor: Pending data-scaffold
Process anchor: infrastructure — shared overlay component

Done criteria:
  - Phase fields render correctly
  - 4-bucket count grid reflects actual slice counts from SQLite
  - Deliverables list shows correct statuses

Self-verification checklist:
  - Open a phase overlay and confirm count grid matches actual slice statuses
  - Confirm deliverables list is complete

Builder confirmation:
Pending build

Depends on: SL-003
Notes: None.

---

### SL-014 · Project Detail — Routing and Breadcrumb

Status: Ready
Phase: Pending prd-to-plan
Deliverable: Pending prd-to-plan

Plain language description:
Clicking any project in the sidebar — or the "Take me to this project" button in any overlay — loads a dedicated page for that project. The page shows the project name in the breadcrumb at the top and a pill showing the current build phase.

Technical description:
Route: /project/<project_name>. Reads project record and current phase from SQLite. Renders breadcrumb (Dashboard / project_name), phase pill (current phase name + status). Default tab is Action. Tab state managed via URL fragment or query param (?tab=progress etc) so direct links to specific tabs are possible. 404 handling if project_name not found.

Design anchor: sprint-02-project-detail.html — top bar, breadcrumb, phase pill
Data anchor: Pending data-scaffold
Process anchor: See that project's Action tab → V (main path)

Done criteria:
  - /project/<name> loads for every active project in SQLite
  - Breadcrumb shows correct project name, links back to dashboard
  - Phase pill shows current phase name
  - 404 renders gracefully for unknown project names

Self-verification checklist:
  - Navigate to project detail for each test project and confirm breadcrumb and phase pill
  - Click breadcrumb home and confirm return to dashboard
  - Confirm 404 for /project/nonexistent

Builder confirmation:
Pending build

Depends on: SL-003, SL-004
Notes: None.

---

### SL-015 · Project Detail — Action Tab

Status: Ready
Phase: Pending prd-to-plan
Deliverable: Pending prd-to-plan

Plain language description:
The Action tab is the first thing the solo sees when they open a project. It shows three sections: anything that is blocking work (with a red treatment), anything that is flagged for attention (amber), and any outstanding questions that need an answer. Every item is clickable and shows full details.

Technical description:
Query slices table WHERE project_id = X AND is_blocked = 1 for Blocked section. Query flags table WHERE project_id = X for Flagged section. Query questions table WHERE project_id = X for Outstanding Questions section. Each blocked/flagged slice item opens slice overlay (SL-011). Empty state per section: if a section has zero items, it is not rendered. If all three sections are empty, render a clean "No action items" state.

Design anchor: sprint-02-project-detail.html — Action tab
Data anchor: Pending data-scaffold
Process anchor: See that project's Action tab — questions, blocks, flags → V (main path)

Done criteria:
  - Blocked section shows all blocked slices for the project
  - Flagged section shows all flagged items for the project
  - Outstanding Questions section shows all questions from handoff.md
  - Empty sections are absent, not rendered as empty containers
  - All three sections empty renders a clean "No action items" state

Self-verification checklist:
  - Set a slice to Blocked for a project, confirm it appears in Action tab
  - Add a stale In Progress slice, confirm it appears in Flagged section
  - Confirm clean state when no action items exist

Builder confirmation:
Pending build

Depends on: SL-003, SL-011, SL-014
Notes: None.

---

### SL-016 · Progress Tab — Phase Summary Card

Status: Ready
Phase: Pending prd-to-plan
Deliverable: Pending prd-to-plan

Plain language description:
The top of the Progress tab shows a summary card for the current phase — its name, when it started, whether the gate has been cleared, and a progress bar showing how many slices are done.

Technical description:
Reads from phases table for current project. Renders: phase name, started_date, gate_status, progress bar (done_count / total_count from slices table), 4-bucket status counts. Card is clickable — opens phase overlay (SL-013).

Design anchor: sprint-02-project-detail.html — Progress tab, phase summary card
Data anchor: Pending data-scaffold
Process anchor: See all active phases → E · infrastructure (project-scoped view)

Done criteria:
  - Phase name, started date, and gate status render correctly
  - Progress bar and status counts match slice data in SQLite
  - Clicking the card opens the phase overlay

Self-verification checklist:
  - Confirm progress bar updates after a slice status change and sync
  - Confirm phase overlay opens on card click

Builder confirmation:
Pending build

Depends on: SL-003, SL-013, SL-014
Notes: None.

---

### SL-017 · Progress Tab — Deliverables Section

Status: Ready
Phase: Pending prd-to-plan
Deliverable: Pending prd-to-plan

Plain language description:
Below the phase summary, the Progress tab shows all deliverables in the current phase — each as a clickable row showing the deliverable name, how many slices it contains, and its current status.

Technical description:
Query deliverables table WHERE project_id = X AND phase_name = current_phase. Render each as a clickable row: icon, name, slice_count, status badge. Row click opens deliverable overlay (SL-012).

Design anchor: sprint-02-project-detail.html — Progress tab, Deliverables section
Data anchor: Pending data-scaffold
Process anchor: infrastructure — project-scoped deliverable view

Done criteria:
  - All deliverables for the current phase render with correct name, count, and status
  - Row click opens deliverable overlay

Self-verification checklist:
  - Confirm all deliverables for the current phase appear
  - Confirm deliverable overlay opens on row click

Builder confirmation:
Pending build

Depends on: SL-003, SL-012, SL-016
Notes: None.

---

### SL-018 · Progress Tab — Slice List

Status: Ready
Phase: Pending prd-to-plan
Deliverable: Pending prd-to-plan

Plain language description:
Below the deliverables, the Progress tab shows the full list of slices in the current phase — each with its ID, name, which deliverable it belongs to, and its status. Done UI slices show a Review button that opens the built screen in the browser.

Technical description:
Query slices table WHERE project_id = X AND phase_name = current_phase ORDER BY slice_id. Render each as a clickable row: slice_id, name, deliverable_name, status badge. If status = Done AND review_url IS NOT NULL: render Review button (opens review_url in new tab, stopPropagation so row click doesn't fire). If status = Done AND review_url IS NOT NULL AND app not running: render "Start & Review" button (amber treatment, triggers SL-024 flow). Row click opens slice overlay.

Design anchor: sprint-02-project-detail.html — Progress tab, slice list, review button
Data anchor: Pending data-scaffold
Process anchor: Review link appears in companion app → O (main path) · Click Review → Q · Start & Review → R

Done criteria:
  - All slices for the current phase render with correct ID, name, deliverable, and status
  - Review button appears only on Done slices with a review_url
  - Start & Review button appears on Done slices with review_url when app is not running
  - Row click opens slice overlay; Review/Start & Review button click does not trigger row click

Self-verification checklist:
  - Confirm slice list matches backlog.md contents after sync
  - Set a slice to Done with a review_url and confirm Review button appears
  - Confirm Review button opens the URL in a new tab
  - Confirm Start & Review button appears when port check fails

Builder confirmation:
Pending build

Depends on: SL-003, SL-011, SL-017, SL-024
Notes: Port check for "is the app running" is a synchronous GET to the app's port from tech-context.md. Timeout 500ms. If the port is not responding, Show Start & Review. SL-024 handles the start command execution.

---

### SL-019 · Backlog Tab

Status: Ready
Phase: Pending prd-to-plan
Deliverable: Pending prd-to-plan

Plain language description:
The Backlog tab shows the full picture of the project across all phases — every phase, every deliverable, and every slice including upcoming work that hasn't started yet. Everything is clickable. Upcoming phases and slices are visually dimmed so active work is clearly distinct.

Technical description:
Three sections: Phases (all phases from phases table for the project, ordered by phase sequence), Deliverables (all deliverables for the project, ordered by phase then name), Slices (all slices for the project, ordered by slice_id). Upcoming items (status = Planning or Upcoming) rendered at 50% opacity. Each row clickable — opens the appropriate overlay. Phase rows: backlog-phase-row with progress bar. Deliverable rows: deliverable-row with phase label and status. Slice rows: slice-row with slice_id, name, deliverable, status, review button where applicable.

Design anchor: sprint-02-project-detail.html — Backlog tab, all three sections
Data anchor: Pending data-scaffold
Process anchor: infrastructure — full project scope view

Done criteria:
  - All phases, deliverables, and slices for the project render across all phases
  - Upcoming items are visually dimmed
  - Each item type opens the correct overlay on click
  - Review buttons behave correctly (same as SL-018)

Self-verification checklist:
  - Confirm slices from multiple phases all appear in the Backlog tab
  - Confirm upcoming slices are dimmed relative to active slices
  - Confirm each overlay type opens correctly

Builder confirmation:
Pending build

Depends on: SL-003, SL-011, SL-012, SL-013, SL-014
Notes: None.

---

### SL-020 · Materials Tab — Inline Document Rendering

Status: Ready
Phase: Pending prd-to-plan
Deliverable: Pending prd-to-plan

Plain language description:
The Materials tab shows all framework documents for the project organized by phase. Clicking a markdown document opens an overlay that renders the document content inline — the solo can read the discovery brief, process maps, or any other text document without leaving the companion app or opening a separate editor.

Technical description:
Read materials table for the project. Render phase-grouped document cards. On card click for markdown files: read the file content from disk, render a simple markdown-to-HTML conversion using stdlib only (no external packages). Conversion handles: # h1, ## h2, ### h3, **bold**, *italic*, - unordered lists, --- horizontal rules, paragraphs (double newline separated). Rendered in the material-doc overlay with a scrollable body. "Open in editor" button in footer passes the file path to a system open command (subprocess.run(['open', file_path])). Mermaid files (.md containing mermaid blocks): render the raw text content in a code-formatted block — do not attempt to render the diagram.

Design anchor: sprint-02-project-detail.html — Materials tab, material-doc overlay
Data anchor: Pending data-scaffold
Process anchor: infrastructure — project materials access

References:
  - ~/Apps/CLAUDE.md — Python stdlib only rule. No markdown parsing libraries.

Done criteria:
  - All markdown document cards render in correct phase sections
  - Clicking a markdown card opens the overlay with rendered content
  - Headings, bold, lists, and horizontal rules render correctly
  - "Open in editor" opens the file in the system default app
  - Mermaid files show raw text, not a broken render attempt

Self-verification checklist:
  - Open the discovery brief overlay and confirm headings, paragraphs, and lists render correctly
  - Open a to-be process map card and confirm mermaid content shows as formatted text
  - Click "Open in editor" and confirm the file opens in the system default app

Builder confirmation:
Pending build

Depends on: SL-003, SL-014
Notes: Stdlib-only regex rendering approach (resolved Round 2). Pattern order matters — h3 before h2 before h1 to prevent partial matches:
  re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
  re.sub(r'^## (.+)$',  r'<h2>\1</h2>', text, flags=re.MULTILINE)
  re.sub(r'^# (.+)$',   r'<h1>\1</h1>', text, flags=re.MULTILINE)
  re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
  re.sub(r'\*(.+?)\*',     r'<em>\1</em>', text)
  re.sub(r'^- (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
  Consecutive <li> blocks wrapped in <ul> via second pass.
  re.sub(r'^---$', r'<hr>', text, flags=re.MULTILINE)
  Remaining double-newline-separated blocks not starting with < wrapped in <p>.
  Mermaid blocks (content starting with ```mermaid) wrapped in <pre> — readable raw display, no render attempt.

---

### SL-021 · Materials Tab — HTML Screen Overlay

Status: Ready
Phase: Pending prd-to-plan
Deliverable: Pending prd-to-plan

Plain language description:
Clicking a design screen in the Materials tab opens a panel showing the screen's name, which phase it belongs to, when it was created, and a description of what it covers. An "Open in browser" button opens the HTML file in the system default browser.

Technical description:
For materials WHERE type = 'HTML Screen': open the material-screen overlay. Render: screen name, phase label, file creation date (os.path.getctime), file path (mono), description derived from file name convention (sprint-NN-[description].html → human-readable). "Open in browser" button: subprocess.run(['open', file_path]) — system default browser handles .html files.

Design anchor: sprint-02-project-detail.html — material-screen overlay
Data anchor: Pending data-scaffold
Process anchor: infrastructure — design screen access from materials

Done criteria:
  - HTML screen cards appear in the Design phase section of Materials
  - Clicking opens the screen overlay with correct metadata
  - "Open in browser" opens the HTML file in the default browser

Self-verification checklist:
  - Click a design screen card and confirm overlay shows correct file name and phase
  - Click "Open in browser" and confirm the HTML file opens in the browser

Builder confirmation:
Pending build

Depends on: SL-003, SL-014
Notes: File creation date used as "created" date — this may show the sync date if files were moved. Acceptable for Phase 1.

---

### SL-022 · Decisions & Changes Tab

Status: Ready
Phase: Pending prd-to-plan
Deliverable: Pending prd-to-plan

Plain language description:
The Decisions & Changes tab shows a log of every design decision made during the project and every time a scope or approach change was recorded. Decisions include the reasoning behind them. Changes show what was and what became.

Technical description:
Two sections: Decisions (from decisions table WHERE project_id = X, ordered by date DESC) and Changes (from changes table WHERE project_id = X, ordered by date DESC). Decisions render: title, phase label, date, body, why-reasoning (border-left treatment). Changes render: title, date, was/became grid. No overlay — these are read-only reference entries, not interactive objects.

Design anchor: sprint-02-project-detail.html — Decisions & Changes tab
Data anchor: Pending data-scaffold
Process anchor: infrastructure — project decision history

Done criteria:
  - All decisions from decisions.md render with title, phase, date, body, and reasoning
  - All changes render with title, date, was, and became
  - Entries are ordered most recent first

Self-verification checklist:
  - Add a decision to a test decisions.md and confirm it appears after sync
  - Confirm was/became grid renders correctly for a change entry

Builder confirmation:
Pending build

Depends on: SL-003, SL-014
Notes: None.

---

### SL-023 · Review Link Surfacing

Status: Ready
Phase: Pending prd-to-plan
Deliverable: Pending prd-to-plan

Plain language description:
When the solo-build skill ships a slice and serves the built UI for review, the URL it serves gets stored in the slice record. The companion reads that URL at sync time and surfaces a Review button on that slice wherever it appears — in the dashboard Slices bucket, the Progress tab, and the Backlog tab.

Technical description:
The companion reads review_url from each slice record in backlog.md at sync time (SL-003) and stores it in the slices table. Any slice with status Done and a non-null review_url gets the Review button rendered on its row. The companion does not write this field — it reads it. The solo-build skill (via a separate framework curator change) is responsible for writing review_url to the slice record when it serves the built UI.

Design anchor: sprint-02-project-detail.html — Progress tab, slice row with Review button
Data anchor: Pending data-scaffold
Process anchor: Review link appears in companion app → O (main path)

References:
  - docs/continuity/handoff.md — note: framework curator change to solo-build skill required to write review_url field. Handle in separate curator pass.

Done criteria:
  - Slice with review_url in backlog.md shows Review button after sync
  - Slice without review_url shows no Review button regardless of status
  - Review button opens the URL in a new browser tab

Self-verification checklist:
  - Add a review_url to a Done slice record in a test backlog.md, sync, confirm Review button appears
  - Confirm clicking Review opens the URL in a new tab

Builder confirmation:
Pending build

Depends on: SL-003, SL-018
Notes: The framework curator change to solo-build is a separate workstream. This slice implements the companion's read side only. The companion works correctly once solo-build is updated to write the field — until then, no Review buttons will appear (graceful degradation, not an error).

---

### SL-024 · Start & Review Action

Status: Ready
Phase: Pending prd-to-plan
Deliverable: Pending prd-to-plan

Plain language description:
If the solo wants to review a completed UI slice but the project's app is not currently running, they click "Start & Review" instead of "Review." The companion starts the app for them and then opens the review URL in the browser — no terminal required.

Technical description:
Port check: on page render for any page showing a Review button, perform a GET to the app's port (read from tech-context.md → start_command field, extract port). Timeout 500ms. If port responds: render Review button (teal). If port does not respond: render "Start & Review" button (amber). On "Start & Review" click: POST to /start-and-review?project=<name>&url=<review_url>. Server-side: read start_command from tech-context.md for the project, run subprocess.Popen(start_command, shell=True, cwd=project_path). Poll the port every 500ms for up to 10 seconds. When port responds, redirect the response to review_url. If port does not respond within 10s, return an error page.

Design anchor: sprint-02-project-detail.html — Progress tab, Start & Review button (amber)
Data anchor: Pending data-scaffold
Process anchor: App not running → Click Start and Review → R (branch path)

References:
  - docs/continuity/handoff.md — Start & Review is the one operational action the companion takes. Read-only boundary holds for all other actions.

Done criteria:
  - Review button appears when port is responding; Start & Review when it is not
  - Start & Review successfully starts the app and opens the review URL
  - If app does not start within 10 seconds, error page is shown with clear message
  - Port check does not cause noticeable page load delay

Self-verification checklist:
  - With the app stopped, confirm Start & Review button appears
  - Click Start & Review and confirm app starts and review URL opens
  - Kill the start command mid-attempt and confirm error page appears after 10s timeout

Builder confirmation:
Pending build

Depends on: SL-003, SL-018, SL-023
Notes: tech-context.md field name for the start command needs to be confirmed — check the framework's tech-context template for the exact field name before build. If the field does not exist in the current format, this is a blocker that requires a framework curator change.

---

## Review Log

### Round 2 — 2026-04-28
**Focus:** Resolve SL-020 rendering approach. Confirm tech-context.md start_command field status.
**Slices promoted to Ready:** SL-020
**Slices added:** None
**Spikes triggered:** None
**Design changes:** None
**Data questions resolved this round:**
  - SL-020 stdlib markdown rendering: regex approach with h3→h2→h1 order, <ul> wrap pass, <pre> for mermaid. Documented in SL-020 notes.
  - SL-024 start_command field: not yet standardized in tech-context.md format. Bundles with review_url curator change — both fields added in same pass.
**Next round focus:** None — all 24 slices Ready. Proceed to prd-to-plan.

---

### Round 1 — 2026-04-28
**Focus:** Full first pass — both Phase 1 screens (Dashboard, Project Detail)
**Slices promoted to Ready:** SL-001 through SL-019, SL-021 through SL-024 (23 slices)
**Slices In Review:** SL-020 (stdlib markdown rendering approach needs documentation before Ready)
**Spikes triggered:** None
**Design changes:** None — screens approved as-is
**Data questions resolved this round:**
  - Flagged items: derived from three sources (stale progress, handoff "Open right now", handoff questions)
  - Recency signal: file last-modified timestamp
  - Project color: auto-assigned via name hash against fixed 8-color palette
  - Review URL: review_url field in slice record — requires solo-build curator change (separate workstream)
**Next round focus:** Resolve SL-020 markdown rendering approach → promote to Ready. Confirm tech-context.md start_command field name → unblock SL-024 note. Build can start on SL-001, SL-002, SL-003.

---

## Decisions and Change Log

### 2026-04-28 — Flagged item derivation defined
Decision: Flagged items derived at sync time from three sources: stale In Progress slices (>3 days by file last-modified), handoff.md "Open right now" section, handoff.md "Outstanding questions" section.
Reason: No formal flagged field exists in framework files today. Derivation covers the meaningful cases without requiring framework format changes.
Impact: SL-007, SL-015 defined accordingly.
Confirmed by: Solo

### 2026-04-28 — Recency signal source defined
Decision: Recency in sidebar derived from most recently modified file in the project directory (os.path.getmtime scan).
Reason: File timestamps are always available, require no framework changes, and accurately reflect when work was last done.
Impact: SL-004 defined accordingly.
Confirmed by: Solo

### 2026-04-28 — Project color assignment defined
Decision: Color auto-assigned by hashing project name against a fixed palette of 8 colors. No user configuration in Phase 1.
Reason: Keeps Phase 1 simple. Color count stays small enough that auto-assignment avoids collisions in practice.
Impact: SL-004 defined accordingly.
Confirmed by: Solo

### 2026-04-28 — Framework curator change required before Start & Review build
Decision: tech-context.md does not have a standardized start_command field. The solo-build curator change (review_url in backlog slice records) must also add start_command to the tech-context format. Both fields land in the same curator pass before SL-024 build starts.
Reason: Confirmed by checking the Fantasy Player Evaluation System tech-context.md — no start_command field exists in the current format.
Impact: SL-024 notes updated. Build on SL-024 waits for curator pass to complete.
Confirmed by: Solo

### 2026-04-28 — Review URL storage defined
Decision: review_url stored as a field in the slice record in backlog.md. The companion reads it; solo-build writes it.
Reason: Single source of truth in the framework file. Companion stays read-only.
Impact: SL-023 defined accordingly. Solo-build framework curator change required in a separate pass.
Confirmed by: Solo
