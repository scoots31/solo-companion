# Backlog — Solo Companion
**Last updated:** 2026-04-28 · SL-008 done — Dashboard Phases bucket with progress bars
**Project status:** Ready for Build

---

## At a Glance

### Slice Status
| Status | Count |
|--------|-------|
| 🔄 In Review | 0 |
| ✅ Ready | 16 |
| 🔬 Blocked | 0 |
| ⏸ Deferred | 0 |
| 🔨 In Build | 0 |
| 🔍 In QA | 0 |
| 🧪 In Test | 0 |
| ✓ Done | 8 |

### Traffic
| | |
|---|---|
| **Currently in build** | — |
| **Next up (Ready, not started)** | SL-009 |
| **Blocked — waiting on** | SL-024 (framework curator change — review_url + start_command) |
| **Open spikes** | — |

---

## Phase Records

---

### Phase 1 · Foundation

Status: Planning

Plain language description:
The companion app starts, runs, and reads real framework files from disk. When Phase 1 is complete, the sync layer reliably turns markdown files into structured data — every project, every phase, every deliverable, every slice, every flag, every decision is in SQLite and queryable. The app is running at localhost:8710 and serving data from real projects.

Technical description:
Flask server registered as a LaunchAgent. Sync layer reads projects.md to discover project paths, then parses each project's framework files (backlog.md, handoff.md, current-phase.md, decisions.md, process maps, design files) into a normalized SQLite schema. Flagged item derivation runs at parse time. The markdown parser handles real-world formatting variations using section-header anchoring rather than line-number parsing. This phase produces no visible UI — it proves the data foundation.

Question this phase answers: Can we reliably read framework files and serve a running app?
Deliverables: D-01
Process steps completed: Open Solo Companion app, Dashboard loads — syncs from framework files
Proves / de-risks: Markdown parsing against real framework files works reliably. SQLite schema holds the full data model. LaunchAgent startup works.

Explicitly out of scope:
All UI. This phase produces a running server and a populated SQLite database — nothing the solo can see in a browser yet.

Blocked by: none
Definition of done: Server starts on login, http://localhost:8710 returns HTTP 200, SQLite populated with correct data from at least two real projects.

Acceptance criteria:
  1. All projects in projects.md appear in SQLite with correct paths and assigned colors after sync
  2. All slices, deliverables, phases, flags, questions, materials, decisions, and changes from real backlog.md and handoff.md files appear in SQLite with correct values
  3. Flagged items derived correctly — stale In Progress slices and handoff "Open right now" items both surface

Self-verification checklist:
  - Start the server and confirm http://localhost:8710 returns HTTP 200
  - Open SQLite and confirm all three object types populated from at least two real projects
  - Manually set a slice to In Progress with old last_modified, confirm it appears as flagged after sync

Builder confirmation:
Pending build

Notes: If the markdown parser fails on any real framework file, stop and fix before proceeding to Phase 2. Phase 2 depends entirely on this layer being correct.

---

### Phase 2 · Dashboard

Status: Planning

Plain language description:
The solo can open the companion app and see everything that matters across all their projects on one screen — what's blocked, what's flagged, what phases and deliverables and slices are active. Clicking any item shows its full details. This is the primary orientation tool — the reason the app exists.

Technical description:
Flask routes and Jinja2 templates for the dashboard view. Reads from SQLite (all tables). Sidebar renders project list with auto-assigned colors and file-based recency. Needs Attention section renders blocked and flagged items from SQLite. Three buckets render active phases, deliverables, and slices with project filters. All three overlay types (slice, deliverable, phase) rendered as shared components — opened via JavaScript, populated from server-rendered data attributes.

Question this phase answers: Can the solo orient across all projects without asking the framework?
Deliverables: D-02, D-03
Process steps completed: See all active phases/deliverables/slices, See blocked items, See flagged items, See recency signals, Solo orients
Proves / de-risks: The core value proposition. If the solo can orient in under a minute from this screen, the app delivers its primary benefit.

Explicitly out of scope:
Project detail — clicking "Take me to this project" in any overlay routes to a 404 until Phase 3.

Blocked by: Phase 1
Definition of done: Dashboard renders with real data from at least two projects. All three buckets populated. Needs Attention shows real blocks and flags. All three overlays open and display correct data.

Acceptance criteria:
  1. Dashboard loads with real data from all registered projects within 2 seconds of opening
  2. Needs Attention section shows all real blocked and flagged items across all projects
  3. All three bucket items are clickable and open correct overlays with complete, accurate data

Self-verification checklist:
  - Open the dashboard with two real projects synced and confirm all three buckets populate
  - Confirm Needs Attention reflects real blocks and flags from current framework files
  - Click every overlay type from every bucket and confirm data is correct and complete

Builder confirmation:
Pending build

Notes: None.

---

### Phase 3 · Project Detail

Status: Planning

Plain language description:
The solo can navigate to any project and see everything about it across five tabs — what needs action, full progress with all slices and deliverables, the complete backlog across all phases, every framework document, and the full decision and change history. The companion replaces every orientation question the solo would otherwise ask the framework.

Technical description:
Flask route /project/<name> with tab routing via query param. Five tab templates reading from SQLite for the selected project. Action tab queries blocked slices and flags tables. Progress and Backlog tabs query phases, deliverables, and slices tables. Materials tab reads the materials table and serves file content for inline rendering (markdown renderer from SL-020). Decisions & Changes tab reads decisions and changes tables. All shared overlay components carry over from Phase 2.

Question this phase answers: Can the solo get complete project context in one place without asking the framework?
Deliverables: D-04, D-05, D-06, D-07, D-08
Process steps completed: See that project's Action tab, cross-project check zero context cost
Proves / de-risks: The companion fully replaces orientation questions for any individual project. A solo can recall any design decision, see any process map, or check slice status without a Claude Code session.

Explicitly out of scope:
Review buttons on slice rows are rendered but non-functional until Phase 4 (review_url will be null until the framework curator change lands). Start & Review not built until Phase 4.

Blocked by: Phase 2
Definition of done: All five tabs load with real data for at least two projects. Materials tab renders markdown inline. Navigation between projects works from sidebar.

Acceptance criteria:
  1. All five tabs load with correct data for any registered project
  2. Materials tab renders at least three document types correctly — markdown inline, HTML screen overlay, mermaid raw text
  3. Clicking any project in the sidebar loads that project's detail at the Action tab

Self-verification checklist:
  - Navigate to two different projects and confirm all five tabs load with correct data for each
  - Open three material types and confirm correct rendering per type
  - Confirm sidebar navigation loads correct project on each click

Builder confirmation:
Pending build

Notes: None.

---

### Phase 4 · Review Flow

Status: Planning

Plain language description:
When a slice ships and the framework serves the built UI, a Review button appears on that slice in the companion app. The solo clicks it and sees the finished work in the browser. If the app is stopped, Start & Review starts it first. No terminal required.

Technical description:
SL-023: review_url field read from SQLite (populated at sync time from slice records in backlog.md). Review button rendered on Done slices with non-null review_url. SL-024: port check on page render, Start & Review button when port not responding, /start-and-review route executes start_command from tech-context.md via subprocess.Popen, polls port until responding, then redirects to review_url.

Question this phase answers: Can the solo review completed work without touching the terminal?
Deliverables: D-09
Process steps completed: Review link appears in companion app, Click Review, Click Start and Review
Proves / de-risks: The full solo build loop — build → companion shows review → solo reviews — works end-to-end without terminal.

Explicitly out of scope:
Activity Feed (Phase 2 of the product — separate build cycle).

Blocked by: Phase 3 · Framework curator change (review_url field in backlog slice records + start_command field in tech-context.md)
Definition of done: Review button appears on a real Done slice with a real review_url. Clicking it opens the running app. Start & Review successfully starts a stopped app and opens the review URL.

Acceptance criteria:
  1. Review button appears on Done slices with review_url populated — absent on all other slices
  2. Clicking Review opens the correct URL in a new browser tab
  3. Start & Review starts a stopped app within 10 seconds and opens the review URL

Self-verification checklist:
  - Add a real review_url to a Done slice record, sync, and confirm Review button appears
  - With the app stopped, click Start & Review and confirm it starts and navigates to the URL
  - Confirm Review button is absent on In Progress and Ready slices

Builder confirmation:
Pending build

Notes: SL-023 (review link surfacing) can build as soon as Phase 3 is complete — it reads review_url from SQLite which is already parsed in SL-003. SL-024 (Start & Review) waits on the framework curator change for start_command. Build SL-023 first, then SL-024 after the curator pass.

---

## Deliverable Records

---

### D-01 · Sync Layer

Status: Accepted
Type: Logic
Phase: 1

Plain language description:
The companion app is running and knows about every project the solo has registered. It has read every framework file for every project and stored the data where the app can use it. The solo can't see any of this yet — but everything the dashboard and project detail screens will show is already in the database, correct and current.

Technical description:
Flask server on port 8710 registered via LaunchAgent. Three-slice sync pipeline: (1) discover projects from projects.md, (2) parse each project's framework files using section-header-anchored markdown parsing, (3) populate SQLite across 9 tables. Flagged item derivation runs at parse time. Sync triggers on every dashboard request and on manual refresh. No UI rendered in this deliverable.

Screens:
  - None (Logic deliverable — no UI output)

Acceptance criteria:
  1. Server starts on login and http://localhost:8710 returns HTTP 200 with no errors
  2. All data from at least two real projects populates SQLite correctly after sync — verified by direct SQLite query
  3. Flagged items (stale In Progress + handoff "Open right now") derive correctly for both projects

Self-verification checklist:
  - Start the server fresh, open SQLite, run SELECT * on each table and confirm data from real projects
  - Confirm flagged derivation by querying flags table against known handoff.md content

Builder confirmation:
Pending build

Slices: SL-001, SL-002, SL-003
References:
  - ~/Developer/engineering-playbook/projects.md — project registry being parsed
  - ~/Developer/engineering-playbook/docs/records-spec.md — backlog format being parsed
  - ~/Apps/CLAUDE.md — LaunchAgent pattern and port convention
Depends on: none
Notes: The markdown parser is the highest-risk element in the entire build. If real framework files expose parsing edge cases not anticipated in SL-003's design, fix them before Phase 2 begins.

---

### D-02 · Dashboard Core

Status: Accepted
Type: Screen
Phase: 2

Plain language description:
The solo opens the companion app and sees a dashboard with their full project landscape. The sidebar shows all active projects with colored dots and recency. The top section surfaces anything that needs attention — blocks in red, flags in amber. Below that, three buckets show what's actively in progress across all projects: phases, deliverables, and slices. The deliverable and slice buckets can be filtered to a single project.

Technical description:
/ route renders the dashboard template. Sidebar populated from projects table. Needs Attention section populated from slices (is_blocked) and flags tables. Three bucket sections populated from phases (status=In Progress), deliverables (status In Active/Defined), and slices (status In Progress/In QA/In Test). Project filter on deliverables and slices buckets implemented as a URL param that re-renders the bucket section. Top bar shows project count, last-synced timestamp, and refresh button (POST /sync → redirect to /).

Screens:
  - sprint-01-dashboard.html (primary)

Acceptance criteria:
  1. Dashboard loads with real data from all registered projects — sidebar, Needs Attention, and all three buckets populated
  2. Needs Attention correctly shows real blocked slices and flagged items; both cards absent when nothing is blocked or flagged
  3. Project filter on deliverables and slices correctly narrows each bucket independently

Self-verification checklist:
  - Load dashboard with two real projects and confirm all sections populated with correct project data
  - Confirm Needs Attention Blocked card is absent when no blocked slices exist
  - Filter deliverables to one project and confirm slices bucket is unaffected (independent filters)

Builder confirmation:
Pending build

Slices: SL-004, SL-005, SL-006, SL-007, SL-008, SL-009, SL-010
References:
  - sprint-01-dashboard.html — design reference for all dashboard elements
Depends on: D-01
Notes: None.

---

### D-03 · Dashboard Overlays

Status: Accepted
Type: Screen
Phase: 2

Plain language description:
Every item on the dashboard is clickable. Clicking a slice, deliverable, or phase opens a panel over the dashboard showing everything about that object — its description, status, anchors, quality gates, and which project it belongs to. A button in the panel takes the solo to that project's detail page.

Technical description:
Three shared overlay components rendered via server-side data attributes on each clickable row. JavaScript reads data attributes and populates the overlay panel on click. Overlay content: slice panel includes all fields from the slice record (plain language description, technical description, acceptance criteria, four anchors, quality gates derived from status). Deliverable panel includes descriptions, phase, slice list with statuses. Phase panel includes descriptions, gate status, 4-bucket count grid, deliverable list. "Take me to this project" links to /project/<name>.

Screens:
  - sprint-01-dashboard.html (primary — all three overlay panels)

Acceptance criteria:
  1. Clicking any item in any bucket opens the correct overlay type with accurate data for that specific item
  2. "Take me to this project" navigates to the correct project detail page
  3. Backdrop click and ✕ button both dismiss the overlay cleanly

Self-verification checklist:
  - Click one item from each bucket type and confirm correct overlay type opens with correct data
  - Click "Take me to this project" from a slice overlay and confirm correct project detail loads
  - Confirm backdrop click dismisses without navigating

Builder confirmation:
Pending build

Slices: SL-011, SL-012, SL-013
References:
  - sprint-01-dashboard.html — overlay panel designs
Depends on: D-02
Notes: "Take me to this project" routes to a 404 until Phase 3. This is expected — note it in the Phase 2 acceptance review.

---

### D-04 · Project Detail — Action Tab

Status: Accepted
Type: Screen
Phase: 3

Plain language description:
Clicking any project in the sidebar — or "Take me to this project" from any overlay — loads a dedicated page for that project. The first thing the solo sees is the Action tab: everything that needs attention for this project specifically. Blocked slices in red, flagged items in amber, outstanding questions below. Every item is clickable.

Technical description:
/project/<name> route with tab routing via ?tab= query param (default: action). Breadcrumb renders project name and links to /. Phase pill reads current phase from phases table. Action tab: three sections (Blocked from slices WHERE is_blocked=1, Flagged from flags table, Questions from questions table), each absent from DOM when empty. All item rows open slice overlay (SL-011). Overlay footer renders "Already on this project" disabled button rather than "Take me to this project."

Screens:
  - sprint-02-project-detail.html (primary — top bar, breadcrumb, tab bar, Action tab)

Acceptance criteria:
  1. /project/<name> loads for every registered project with correct breadcrumb and phase pill
  2. Action tab correctly shows blocked, flagged, and question items — each section absent when empty
  3. Clicking a blocked or flagged item opens the slice overlay with "Already on this project" footer

Self-verification checklist:
  - Navigate to two different projects and confirm breadcrumb and phase pill are correct for each
  - Confirm a project with no action items shows a clean empty state, not empty containers
  - Confirm slice overlay footer shows "Already on this project" (not "Take me to this project") on this page

Builder confirmation:
Pending build

Slices: SL-014, SL-015
References:
  - sprint-02-project-detail.html — breadcrumb, tab bar, Action tab design
Depends on: D-03
Notes: None.

---

### D-05 · Project Detail — Progress Tab

Status: Accepted
Type: Screen
Phase: 3

Plain language description:
The Progress tab shows the solo exactly where the current build phase stands — a summary card for the phase at the top, then all deliverables in the phase with their status, then the full list of every slice in the phase with its ID, name, deliverable, and status. Everything is clickable. Done UI slices with a review URL show a Review button (non-functional until Phase 4).

Technical description:
Progress tab template reads from phases, deliverables, and slices tables for the selected project, filtered to current phase. Phase summary card is clickable (opens phase overlay). Deliverable rows clickable (opens deliverable overlay). Slice rows clickable (opens slice overlay). Review button rendered on Done slices with non-null review_url — button is present but links to # until Phase 4 wires the URL. App-running port check not performed in Phase 3 — defer to Phase 4 when SL-024 builds.

Screens:
  - sprint-02-project-detail.html (primary — Progress tab)

Acceptance criteria:
  1. Phase summary card shows correct phase name, gate status, and progress bar for the current phase
  2. All deliverables and slices for the current phase render with correct names and statuses
  3. Phase, deliverable, and slice overlays all open correctly from Progress tab rows

Self-verification checklist:
  - Confirm progress bar and status count grid match actual slice statuses in SQLite
  - Click phase summary card, a deliverable row, and a slice row — confirm each opens the correct overlay
  - Confirm Review button is absent on non-Done slices and on Done slices with null review_url

Builder confirmation:
Pending build

Slices: SL-016, SL-017, SL-018
References:
  - sprint-02-project-detail.html — Progress tab design
Depends on: D-04
Notes: Review button is rendered but not fully wired until Phase 4. Acceptable for Phase 3 acceptance — note it explicitly in the review.

---

### D-06 · Project Detail — Backlog Tab

Status: Accepted
Type: Screen
Phase: 3

Plain language description:
The Backlog tab shows the complete picture of the project across all phases — every phase, every deliverable, every slice. Active work is clearly distinct from upcoming work. The solo can see where the entire project stands, not just the current phase.

Technical description:
Backlog tab template queries phases, deliverables, and slices tables for the selected project with no phase filter. All phases ordered by sequence. All deliverables ordered by phase then name. All slices ordered by slice_id. Items with Planning/Upcoming status rendered at 50% opacity. All rows clickable with correct overlay types.

Screens:
  - sprint-02-project-detail.html (primary — Backlog tab)

Acceptance criteria:
  1. All phases, deliverables, and slices for the project appear regardless of status or phase
  2. Upcoming/planning items are visually dimmed relative to active items
  3. All three overlay types open correctly from Backlog tab rows

Self-verification checklist:
  - Confirm slices from multiple phases all appear in Backlog tab
  - Confirm upcoming items are rendered at reduced opacity
  - Click one item of each type and confirm correct overlay opens

Builder confirmation:
Pending build

Slices: SL-019
References:
  - sprint-02-project-detail.html — Backlog tab design
Depends on: D-05
Notes: Single-slice deliverable. Acceptance is straightforward — the tab either shows the complete backlog correctly or it does not.

---

### D-07 · Project Detail — Materials Tab

Status: Accepted
Type: Screen
Phase: 3

Plain language description:
The Materials tab shows every framework document for the project, organized by the phase it was produced in. Clicking a markdown document opens it inline — the solo reads the discovery brief, process maps, or handoff notes without leaving the app. Clicking a design screen shows its metadata and a button to open it in the browser.

Technical description:
Materials tab reads from materials table for the selected project, grouped by phase_name. Markdown documents open the material-doc overlay — file content read from disk, rendered via the stdlib regex markdown renderer (SL-020). HTML screen documents open the material-screen overlay — metadata only, "Open in browser" button calls subprocess.run(['open', file_path]).

Screens:
  - sprint-02-project-detail.html (primary — Materials tab, material-doc overlay, material-screen overlay)

Acceptance criteria:
  1. All discovered framework documents appear in correct phase sections
  2. Clicking a markdown document renders its content correctly inline — headings, paragraphs, bold, lists, and horizontal rules
  3. Clicking an HTML screen document opens the screen overlay and "Open in browser" opens the file in the default browser

Self-verification checklist:
  - Click the discovery brief and confirm formatted content renders correctly
  - Click a process map and confirm mermaid content shows as readable raw text, not a broken render
  - Click an HTML screen card and confirm "Open in browser" opens the file

Builder confirmation:
Pending build

Slices: SL-020, SL-021
References:
  - sprint-02-project-detail.html — Materials tab design
Depends on: D-04
Notes: D-07 depends on D-04 (project shell), not D-06 (Backlog tab). Materials tab can be built in parallel with D-05 and D-06 once D-04 is accepted.

---

### D-08 · Project Detail — Decisions & Changes Tab

Status: Accepted
Type: Screen
Phase: 3

Plain language description:
The Decisions & Changes tab shows every design decision made during the project and every time something changed — with the reasoning recorded for each. The solo can recall why any decision was made, and what was changed from what it used to be.

Technical description:
Decisions & Changes tab reads from decisions and changes tables for the selected project. Decisions rendered with title, phase label, date, body text, and why-reasoning (border-left treatment). Changes rendered with title, date, was/became grid. Both sections ordered most recent first. No overlays — read-only reference content.

Screens:
  - sprint-02-project-detail.html (primary — Decisions & Changes tab)

Acceptance criteria:
  1. All decisions from decisions.md render with title, phase, date, body, and reasoning
  2. All changes render with title, date, was value, and became value
  3. Both sections ordered most recent first

Self-verification checklist:
  - Add a test decision to a real decisions.md, sync, and confirm it appears with all fields
  - Confirm entries are ordered most recent first

Builder confirmation:
Pending build

Slices: SL-022
References:
  - sprint-02-project-detail.html — Decisions & Changes tab design
  - docs/continuity/decisions.md — example of the file format being parsed
Depends on: D-04
Notes: None.

---

### D-09 · Review Flow

Status: Defined
Type: Logic
Phase: 4

Plain language description:
When a framework build session marks a slice as done and records a review URL, the companion automatically shows a Review button on that slice. The solo clicks it and sees the finished work in the browser. If the app was stopped, the companion starts it first — the solo never needs to open a terminal to review work.

Technical description:
SL-023: review_url read from slices table (populated at sync from backlog.md slice records). Review button rendered on Done slices with non-null review_url — opens URL in new tab. SL-024: port check on page render (GET to app port from tech-context.md, 500ms timeout). Start & Review button (amber) rendered when port not responding. /start-and-review POST route: reads start_command from tech-context.md, runs subprocess.Popen, polls port every 500ms for up to 10 seconds, redirects to review_url on success, returns error page on timeout.

Screens:
  - sprint-02-project-detail.html (affected — Progress tab slice rows, Backlog tab slice rows)
  - sprint-01-dashboard.html (affected — Slices bucket rows)

Acceptance criteria:
  1. Review button appears on Done slices with review_url in backlog.md — absent on all other slices
  2. Start & Review button appears when the project app's port is not responding — Review button appears when it is
  3. Start & Review successfully starts a stopped app and opens the review URL within 10 seconds

Self-verification checklist:
  - Add review_url to a real Done slice record, sync, confirm Review button appears on Progress tab
  - Stop a project app, confirm Start & Review appears; click it and confirm app starts and URL opens
  - Confirm error page renders correctly when app fails to start within 10 seconds

Builder confirmation:
Pending build

Slices: SL-023, SL-024
References:
  - sprint-02-project-detail.html — Progress tab slice row with Review/Start & Review button
  - docs/continuity/handoff.md — Start & Review is the one operational action; read-only boundary
Depends on: D-05 · Framework curator change (review_url in backlog slice records, start_command in tech-context.md)
Notes: SL-023 builds as soon as Phase 3 is accepted. SL-024 waits on the framework curator change. Build SL-023 first. When the curator change lands, build SL-024.

---

## Slice Detail

---

### SL-001 · App Startup and Server

Status: Done
Phase: 1
Deliverable: D-01

Plain language description:
The companion app starts automatically when the Mac logs in and runs silently in the background. When the solo opens their browser and goes to the companion's local address, the app is already there — no manual launch required.

Technical description:
Flask server on a fixed port (8710 — next available in the ~/Apps suite). LaunchAgent plist registered at ~/Library/LaunchAgents/com.scotth.solocompanion.plist, same pattern as the existing app suite. Server entry point at app.py. Routes defined for: / (dashboard), /project/<name> (project detail). No external packages beyond Flask.

Design anchor: sprint-01-dashboard.html — full app shell
Data anchor: N/A — infrastructure slice, no data consumed
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
  ✓ LaunchAgent reloaded — process listening on 127.0.0.1:8710 (verified via lsof)
  ✓ http://localhost:8710/ returns HTTP 200 (525 bytes, placeholder dashboard)
  ✓ http://localhost:8710/project/test returns HTTP 200 (529 bytes, name-aware placeholder)
  ✓ companion.log shows clean Flask startup — no errors, both routes hit successfully
  ✓ Stack: Python stdlib + Flask only — no external packages added
  ✓ app.py minimal — single docstring, no dead code, no premature abstraction
  ✓ Solo browser sign-off — confirmed 2026-04-28 (both routes render correctly)

Depends on: none
Notes: Port 8710 confirmed free before build. Flask runs from ~/Apps/.venv/bin/python3 (venv carries Flask; system python3 does not). Plist copied to ~/Library/LaunchAgents/ and loaded.
Distribution note: plist has Scott's username hardcoded in app path and python path. Before first public release, an install script must generate the plist dynamically from the installing user's home directory. companion.db is excluded from git — derived data, populated fresh from each user's own framework files on first run.

---

### SL-002 · Sync on Open — Project Discovery

Status: Done
Phase: 1
Deliverable: D-01

Plain language description:
Every time the solo opens the companion app, it reads the framework's project registry to discover all active projects and their locations on disk. The solo never has to tell the companion where projects live — it finds them automatically.

Technical description:
On each request to / (dashboard), trigger a sync pass. Read ~/Developer/engineering-playbook/projects.md — parse the markdown table to extract project name and path for every registered project. Store discovered projects in SQLite projects table. Record sync timestamp. If a project path no longer exists on disk, mark it inactive rather than deleting — preserves history. Framework path is set once at install time (config file or environment variable).

Design anchor: sprint-01-dashboard.html — last synced timestamp, sidebar project list
Data anchor: N/A — infrastructure slice, no data consumed (writes to SQLite, does not read from it)
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
  ✓ projects table created on init_db; schema is 5 columns (id, name, path, last_synced, is_active)
  ✓ config.py reads framework_path from config.json with sensible default — supports distribution without hardcoded paths
  ✓ sync.discover_projects() parses projects.md table, reconciles inserts/updates, marks missing-path projects inactive
  ✓ Both projects from projects.md (player-evaluation, solo-companion) populated correctly with ISO sync timestamp
  ✓ Inactive marking logic in place — projects whose path no longer exists on disk → is_active = 0; projects no longer present in projects.md → is_active = 0 (history preserved)
  ✓ Dashboard placeholder shows synced project count + list + last-synced time, confirming sync ran on request
  ✓ Solo browser sign-off — confirmed 2026-04-28

Depends on: SL-001
Notes: Sync runs on every dashboard request in Phase 1 — no file watcher. This keeps the implementation simple and covers the primary use case (open app to orient before a session).

---

### SL-003 · Sync — Parse Framework Files and Populate SQLite

Status: Done
Phase: 1
Deliverable: D-01

Plain language description:
After discovering which projects exist, the companion reads each project's framework files and turns them into structured data the app can display. This is what makes the dashboard and project detail screens show real information — not just project names.

Technical description:
For each active project path, read and parse the following files:
  - docs/backlog.md → phases, deliverables, slices — every field per records-spec.md
  - docs/continuity/handoff.md → current phase context, "Open right now" items (flag source), "Outstanding questions" section (questions table)
  - docs/continuity/current-phase.md → current phase name and status
  - docs/continuity/decisions.md → decision log entries (full structure: decision, why, alternatives, tradeoffs)
  - docs/continuity/changes.md → change log entries (when present)
  - docs/continuity/questions.md → outstanding questions (when present)
  - docs/process/to-be-*.md → existence check only (surfaces in Materials)
  - docs/process/as-is-*.md → existence check only
  - docs/discovery-brief.md → existence check only
  - docs/design/sprint-*.html → existence check only (surfaces in Materials)

Parsing approach: section-header anchored at the document level (`## Phase Records`, `## Deliverable Records`, `## Slice Detail`, `## Decisions and Change Log`); within each record block, field-anchored extraction — every labeled field defined in records-spec.md is captured, no matter its position. List-typed fields (References, Done criteria, Acceptance criteria, Self-verification checklist, Builder confirmation, Screens) preserved as ordered lists, stored as JSON-encoded TEXT. Missing optional fields stored as NULL.

Format compatibility: projects whose backlog.md does not match records-spec.md (e.g., legacy table-only backlogs without per-record sections) are marked inactive in the projects table at parse time and skipped for content sync. The companion does not interpret legacy formats — onboarding to the new schema is a separate workstream.

SQLite schema (canonical fields per records-spec.md; 17 spec fields per slice):
  projects(id, name, path, last_synced, is_active)

  phases(id, project_id, name, status,
         plain_description, technical_description,
         question_answered, deliverables_list, process_steps_completed,
         proves_de_risks, out_of_scope, blocked_by, definition_of_done,
         acceptance_criteria, self_verification, builder_confirmation, notes)

  deliverables(id, project_id, deliverable_id, name, status, type, phase,
               plain_description, technical_description, screens,
               acceptance_criteria, self_verification, builder_confirmation,
               slices_list, references, depends_on, notes)

  slices(id, project_id, slice_id, name, status, phase, deliverable_ref,
         plain_description, technical_description,
         design_anchor, data_anchor, process_anchor,
         references, done_criteria, self_verification, builder_confirmation,
         depends_on, notes, distribution_note,
         is_blocked, is_flagged, flagged_reason, review_url, last_modified)

  materials(id, project_id, phase_name, name, type, file_path)
  decisions(id, project_id, title, phase, date, body, why, alternatives, tradeoffs, status)
  changes(id, project_id, title, phase, date, was_value, became_value, why, affects)
  questions(id, project_id, text, surfaced_during, blocking, who_can_answer, status, answer)
  flags(id, project_id, text, object_type, object_id, flagged_reason)

Note: list-typed columns (references, done_criteria, acceptance_criteria,
self_verification, builder_confirmation, screens, slices_list, deliverables_list,
process_steps_completed) stored as JSON-encoded TEXT. Empty lists → '[]'.
Project color is computed at render time from the project name (deterministic
hash, SL-004) — not persisted in the projects table.

Flagged item derivation rules (applied at parse time):
  1. Any slice with status In Progress whose file last-modified is more than 3 days ago → flagged, reason: "stale progress"
  2. Items in handoff.md "Open right now" section → flagged, reason: text of the item
  3. Items in handoff.md "Outstanding questions" section → questions table

Blocked item rule: any slice with status Blocked in backlog.md.

Design anchor: sprint-01-dashboard.html — Needs Attention section, bucket data
Data anchor: N/A — this slice writes the data layer; nothing reads from SQLite yet
Process anchor: Dashboard loads — syncs from framework files → C (main path) · infrastructure

References:
  - ~/Developer/engineering-playbook/docs/records-spec.md — canonical backlog record format. Every field defined here is captured for every record. No omissions.
  - docs/design/deferred-decisions.md — flagging derivation rules; line 25 confirms overlays render full detail (drives the schema completeness requirement)
  - docs/design/sprint-01-dashboard.html — overlay design specifies sectioned full-detail layout per record type, which the schema must support

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
  ✓ parsers.py written with section-anchored, field-anchored extraction covering all 17 slice fields, 15 phase fields, 15 deliverable fields
  ✓ sync.py extended with sync_project_content() — destructive per-project wipe + re-insert on every sync
  ✓ db.py schema updated to full records-spec.md spec (9 tables, all spec fields, JSON-encoded list columns)
  ✓ Verified via direct SQLite query: solo-companion → 4 phases / 9 deliverables / 24 slices / 12 materials / 7 decisions
  ✓ SL-001 full record confirmed: all 17 fields populated including JSON lists for references, done_criteria, self_verification, builder_confirmation
  ✓ player-evaluation correctly marked is_active=0 (legacy format, missing required section headers)
  ✓ Dashboard placeholder shows per-project content counts as proof of population

Depends on: SL-001, SL-002
Notes: This is the most complex slice in the build. The markdown parsing must be robust to minor formatting variations in the framework files — the framework does not enforce rigid formatting. Use section-header anchoring (## Section Name) rather than line-number-based parsing. When a section is not found, treat as empty — not an error.

---

### SL-004 · Sidebar — Project List, Recency, and Navigation

Status: Done
Phase: 2
Deliverable: D-02

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
  ✓ Persistent sidebar at 200px — Views section (Dashboard, Activity Feed) + Projects section
  ✓ Color assigned via deterministic hash (sum of char codes mod 8, 8-color palette)
  ✓ Recency derived from filesystem mtime scan of project directory
  ✓ Active project highlighted with color-matched left border
  ✓ /feed route added as placeholder
  ✓ _sidebar_html() + _page() layout wrapper used by all three routes

Depends on: SL-002, SL-003
Notes: Activity Feed route (/feed) renders a placeholder in Phase 1. Do not build the feed — just a page that says it's coming. The sidebar nav item should still appear and be clickable so the sidebar is complete.

---

### SL-005 · Dashboard Top Bar

Status: Done
Phase: 2
Deliverable: D-02

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
  ✓ Top bar renders: page title, active project count, relative sync time, Refresh button
  ✓ _relative_synced() returns "just now" / "Xm ago" / "Xh ago" / "Xd ago" / "Xw ago" / "never"
  ✓ POST /sync triggers discover_projects() and redirects 302 to / — confirmed via curl
  ✓ Sync timestamp updates after each refresh click

Depends on: SL-002, SL-003
Notes: None.

---

### SL-006 · Needs Attention — Blocked Card

Status: Done
Phase: 2
Deliverable: D-02

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
  ✓ _blocked_card() queries slices WHERE is_blocked=1 ORDER BY last_modified ASC
  ✓ Each row: slice_id (monospace), notes/name (reason), color dot, project name, open duration
  ✓ Empty state verified: card absent from DOM when no blocked slices
  ✓ Card renders verified: set SL-011 to Blocked in backlog, confirmed card appeared with correct row
  ✓ _open_duration() returns "today" / "Nd" / "Nw" from last_modified ISO timestamp

Depends on: SL-003, SL-011
Notes: Empty state means the card is not rendered — not rendered with a "no blocked items" message. The dashboard should feel clean when everything is unblocked.

---

### SL-007 · Needs Attention — Flagged Card

Status: Done
Phase: 2
Deliverable: D-02

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
  ✓ _flagged_card() unions flags table + slices WHERE is_flagged=1 (covers both derivation sources)
  ✓ Each row: reason text, slice_id badge (if object_type=slice), project color dot + name
  ✓ Empty state verified: card absent from DOM when flags table empty and no flagged slices
  ✓ Card renders verified: added Open right now item to handoff.md, confirmed card appeared with correct row
  ✓ Amber theme (#F59E0B / rgba(217,119,6)) distinct from red blocked card

Depends on: SL-003, SL-011
Notes: "Outstanding questions" items appear in the questions table and surface on the project detail Action tab, not in the Flagged card on the dashboard. The dashboard Flagged card shows stale progress and open handoff items only.

---

### SL-008 · Dashboard — Phases Bucket

Status: Done
Phase: 2
Deliverable: D-02

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
  ✓ _phases_bucket() queries phases WHERE status='In Progress', shared _bucket_section() container
  ✓ Phase number extracted from "Phase N · Name" to match slices.phase = "N"
  ✓ Progress bar: done/total slices per project+phase, color-matched to project
  ✓ Empty state: "No phases in progress." message when query returns zero rows
  ✓ Verified: Phase 2 set to In Progress → row rendered with "4/10" and progress bar
  ✓ _bucket_section() helper introduced for Deliverables + Slices buckets to reuse

Depends on: SL-003, SL-013
Notes: None.

---

### SL-009 · Dashboard — Deliverables Bucket with Project Filter

Status: Ready
Phase: 2
Deliverable: D-02

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
Phase: 2
Deliverable: D-02

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
Phase: 2
Deliverable: D-03

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
Phase: 2
Deliverable: D-03

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
Phase: 2
Deliverable: D-03

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
Phase: 3
Deliverable: D-04

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
Phase: 3
Deliverable: D-04

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
Phase: 3
Deliverable: D-05

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
Phase: 3
Deliverable: D-05

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
Phase: 3
Deliverable: D-05

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
Phase: 3
Deliverable: D-06

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
Phase: 3
Deliverable: D-07

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
Phase: 3
Deliverable: D-07

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
Phase: 3
Deliverable: D-08

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
Phase: 4
Deliverable: D-09

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
Phase: 4
Deliverable: D-09

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

### 2026-04-28 — Build plan approved (4 phases, 9 deliverables, 24 slices)
Decision: Four-phase tracer-bullet build plan locked: Phase 1 Foundation (SL-001–003), Phase 2 Dashboard (SL-004–013), Phase 3 Project Detail (SL-014–022), Phase 4 Review Flow (SL-023–024).
Reason: Tracer-bullet sequencing — each phase answers one question and proves one assumption before the next begins. Foundation first because nothing else runs without reliable parsing. Dashboard second because it proves the data model in real UI. Project Detail third as the deepest read surface. Review Flow fourth as it depends on framework format changes not yet made.
Impact: All 24 slice records updated with phase and deliverable assignments.
Confirmed by: Solo

### 2026-04-28 — SL-003 schema corrected to records-spec.md (full field capture)
Decision: SL-003's SQLite schema rewritten to capture every field defined in `~/Developer/engineering-playbook/docs/records-spec.md` for phases, deliverables, and slices — including all descriptions, anchors, criteria lists, references, builder confirmation, and notes. Slice records carry all 17 spec fields (16 standard + optional distribution_note); phases and deliverables carry all 15 each. List-typed fields stored as JSON-encoded TEXT.
Reason: The original SL-003 schema captured only structural metadata (IDs, names, status, derived flags) and was the root cause of the failed Phase 1–3 build. Sync truncated 80%+ of framework content; overlays in SL-011/012/013 — which the design contract (`sprint-01-dashboard.html`) and `deferred-decisions.md` line 25 explicitly call out as "full detail" — had no data to render. A multi-hour overlay debug session in the prior session was patches trying to add fields the schema never held. Aligning the schema with the canonical records-spec.md eliminates the failure mode structurally rather than adding fields field-by-field.
Impact:
- SL-003 spec — schema section rewritten; technical description specifies field-anchored extraction; references updated to call out records-spec.md, deferred-decisions.md line 25, and sprint-01-dashboard.html as the design contract.
- SL-011, SL-012, SL-013 specs — unchanged; they already call for full-detail overlays. The corrected schema makes them buildable as written.
- D-01 (Sync Layer) acceptance — unchanged ("data populates SQLite correctly"); the corrected schema delivers that literally instead of partially.
- Phase 1 boundary — unchanged.
- Format compatibility rule added: projects whose backlog.md does not match records-spec.md are marked inactive at parse time. Player-evaluation falls in this category until onboarded.
Confirmed by: Solo
