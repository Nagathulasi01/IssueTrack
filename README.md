# IssueTrack – Smart Issue & Bug Tracking System

A lightweight, modular, and portfolio-ready bug tracking system engineered with **FastAPI**, **SQLite**, and **vanilla HTML/CSS/JavaScript**.

---

## 📌 Project Overview

**IssueTrack** is a full-stack software defect and task tracking application designed to streamline internal engineering issue management. It provides complete ticket lifecycle tracking—from creation and developer assignment to status and priority filtering, partial updates, and permanent deletion.

The application adheres to clean architecture principles: strict separation between API routing, data validation, database persistence, and a decoupled, responsive frontend dashboard.

---

## 🎯 Problem Statement

Modern software teams need responsive, lightweight tracking systems that do not burden infrastructure with heavy memory footprints, container orchestration, or complex third-party subscriptions. Heavy tools like Jira often suffer from high latency, steep learning curves, and resource bloat.

**IssueTrack** addresses this by delivering a self-contained, high-performance tracking system that:
1. Runs entirely on local infrastructure with zero cloud database fees.
2. Utilizes Python's built-in SQLite engine with Write-Ahead Logging (WAL) for high-efficiency concurrent reading.
3. Enforces strict schema validation at the HTTP boundary via Pydantic to maintain database integrity.
4. Provides an interactive web dashboard with zero framework dependencies (pure HTML, CSS, and ES6+ JavaScript).

---

## ✨ Features

### 1. Issue Lifecycle Management
- **Create:** File new issues with validated title (3–120 characters), description, priority, initial status, and assigned developer.
- **Read:** Retrieve paginated lists of issues ordered descending by ID, or inspect individual issues by ID.
- **Update:** Full or partial updates (supports inline status changes or modal-based editing without overwriting untouched fields).
- **Delete:** Safely remove issues with confirmation modals and verified database deletion.

### 2. Search & Filtering
- **Keyword Substring Search:** Case-insensitive search on issue titles.
- **Status Filtering:** Filter issues by `Open`, `In Progress`, or `Resolved`.
- **Priority Filtering:** Filter issues by `High`, `Medium`, or `Low`.
- **Combined Queries:** Combine search keywords with status and priority filters simultaneously.

### 3. Live Dashboard Metrics
- **Aggregate Summary Cards:** Visual counters for Total, Open, In Progress, and Resolved issues.
- **Interactive Metric Filtering:** Clicking any metric card immediately filters the table to matching tickets.
- **Single-Query Aggregation:** Dashboard metrics are computed in $O(1)$ database execution time using conditional SQL aggregation.

### 4. Enterprise-Grade API Design
- **100% Parameterized Queries:** Every database interaction uses SQL bind parameters (`?`), eliminating SQL injection vulnerabilities.
- **Standard HTTP Semantics:** Returns proper status codes (`200 OK`, `201 Created`, `404 Not Found`, `422 Unprocessable Entity`, `500 Internal Server Error`).
- **Healthcheck & Status Monitoring:** Continuous `/health` endpoint validating service and database connectivity with live header status indicator.

---

## 🛠️ Technology Stack

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Backend Framework** | FastAPI (Python 3.12) | Asynchronous, high performance, automatic OpenAPI documentation, clean dependency injection. |
| **Data Validation** | Pydantic v2 | Strict schema constraints, type coercion, whitespace normalization, and clear validation errors. |
| **Database** | SQLite3 | Built into Python standard library, zero external server processes, minimal disk/RAM footprint. |
| **Concurrency Mode** | WAL (Write-Ahead Logging) | Enables concurrent read operations while a write transaction is executing. |
| **ASGI Server** | Uvicorn | Lightweight, lightning-fast ASGI server implementation. |
| **Frontend UI** | HTML5, CSS3, Vanilla JavaScript | Zero build steps (no npm/Webpack/React overhead), responsive CSS variables, accessible modals, and toast alerts. |
| **Testing** | Pytest + HTTPX (`TestClient`) | 38 automated test cases running against an isolated in-memory/temporary test database. |
| **CI/CD** | GitHub Actions | Automated linting and test execution on push and pull requests. |

---

## 🏛️ Architecture Explanation

IssueTrack follows a standard **Layered Architecture (Separation of Concerns)**:

```
[ Browser / Vanilla JS Client ]
              │ (HTTP JSON Requests)
              ▼
[ FastAPI Application (main.py) ]  ─── Handles CORS, Lifespan Startup, Static Asset Mounting
              │
              ▼
[ Routers (routers/issues.py) ]   ─── Maps HTTP Methods, Query Params, Status Codes
              │
              ▼
[ Models / Schemas (models.py) ]  ─── Validates Payloads & Types with Pydantic
              │
              ▼
[ Data Access Layer (crud.py) ]   ─── Executes Parameterized SQL Queries
              │
              ▼
[ SQLite Database (database.py) ] ─── WAL Mode Connection Factory & Performance Indexes
```

1. **Presentation Layer (`static/`):** Semantic HTML5, responsive CSS stylesheet, and a vanilla JavaScript client using `fetch()` and DOM manipulation.
2. **Controller Layer (`app/routers/issues.py`):** Translates incoming requests into business actions, handles query parameters, and returns standard HTTP responses.
3. **Validation Layer (`app/models.py`):** Intercepts malformed data before database execution and returns structured `422 Unprocessable Entity` responses.
4. **Data Access Layer (`app/crud.py`):** Houses all raw SQL logic using parameterized queries (`?`). Decouples SQL queries from API routes.
5. **Persistence Layer (`app/database.py`):** Configures SQLite connection pooling with `check_same_thread=False` and enables Write-Ahead Logging (`PRAGMA journal_mode = WAL;`).

---

## 📂 Project Folder Structure

```
DevGuard/
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions CI workflow configuration
├── app/
│   ├── __init__.py            # App package identifier
│   ├── crud.py                # Data access layer (parameterized SQL queries)
│   ├── database.py            # SQLite connection setup, WAL mode, schema & indexes
│   ├── main.py                # FastAPI app initialization, CORS, static routes, healthcheck
│   ├── models.py              # Pydantic schemas (validation, enums, response formats)
│   └── routers/
│       ├── __init__.py        # Routers package identifier
│       └── issues.py          # REST API endpoints (/api/issues)
├── static/
│   ├── css/
│   │   └── style.css          # Custom, responsive dark-mode styling (0 external CSS libraries)
│   ├── js/
│   │   └── app.js             # Vanilla JS client (API interactions, modal logic, toasts)
│   └── index.html             # Dashboard UI (metric cards, filters, tables, modals)
├── tests/
│   ├── __init__.py            # Tests package identifier
│   ├── conftest.py            # Pytest test fixtures, isolated DB setup/teardown
│   └── test_issues.py         # 38 automated unit, API, & integration test cases
├── .gitignore                 # Excludes DB files, virtual environments, pycache, secrets
├── requirements.txt           # Minimal dependencies manifest
└── README.md                  # Comprehensive documentation & setup guide
```

---

## 💻 Installation Instructions for Windows

### Prerequisites
- Python 3.10 or higher (Python 3.12 recommended).
- PowerShell or Windows Command Prompt.

### Step 1: Open Terminal in Project Directory
Navigate to the project root directory:
```powershell
cd d:\DevGuard
```

### Step 2: Create and Activate Virtual Environment (Optional but Recommended)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*(If execution of scripts is restricted in PowerShell, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

---

## 🚀 How to Start the FastAPI Server

Start the application with Uvicorn:

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Once started:
- **Web Dashboard:** Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.
- **Interactive Swagger Documentation:** Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).
- **Alternative ReDoc Documentation:** Open [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc).
- **Healthcheck Endpoint:** Open [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health).

---

## 🧪 How to Run Tests

Run the complete test suite using Pytest:

```powershell
python -m pytest tests/ -v
```

### Test Suite Execution Output
```text
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\DevGuard
collected 38 items

tests/test_issues.py::TestIssueCreation::test_create_issue_with_all_fields PASSED [  2%]
tests/test_issues.py::TestIssueCreation::test_create_issue_with_default_values PASSED [  5%]
tests/test_issues.py::TestIssueCreation::test_create_issue_strips_whitespace PASSED [  7%]
tests/test_issues.py::TestIssueRetrieval::test_get_all_issues_empty_database PASSED [ 10%]
tests/test_issues.py::TestIssueRetrieval::test_get_all_issues_multiple_records PASSED [ 13%]
tests/test_issues.py::TestIssueRetrieval::test_get_all_issues_pagination PASSED [ 15%]
tests/test_issues.py::TestIssueRetrieval::test_get_issue_by_valid_id PASSED [ 18%]
tests/test_issues.py::TestIssueUpdate::test_update_all_fields PASSED     [ 21%]
tests/test_issues.py::TestIssueUpdate::test_partial_update_status_only PASSED [ 23%]
tests/test_issues.py::TestIssueUpdate::test_partial_update_priority_only PASSED [ 26%]
tests/test_issues.py::TestIssueUpdate::test_update_with_empty_payload_returns_existing PASSED [ 28%]
tests/test_issues.py::TestIssueDeletion::test_delete_issue_success PASSED [ 31%]
tests/test_issues.py::TestIssueDeletion::test_delete_already_deleted_issue_returns_404 PASSED [ 34%]
tests/test_issues.py::TestDataValidation::test_missing_required_title PASSED [ 36%]
tests/test_issues.py::TestDataValidation::test_title_too_short PASSED    [ 39%]
tests/test_issues.py::TestDataValidation::test_title_whitespace_only PASSED [ 42%]
tests/test_issues.py::TestDataValidation::test_title_exceeds_max_length PASSED [ 44%]
tests/test_issues.py::TestDataValidation::test_invalid_status_enum PASSED [ 47%]
tests/test_issues.py::TestDataValidation::test_invalid_priority_enum PASSED [ 50%]
tests/test_issues.py::TestDataValidation::test_update_with_invalid_title PASSED [ 52%]
tests/test_issues.py::TestDataValidation::test_update_with_invalid_status PASSED [ 55%]
tests/test_issues.py::TestDataValidation::test_non_integer_issue_id_in_path PASSED [ 57%]
tests/test_issues.py::TestNonexistentResourceHandling::test_get_nonexistent_issue_returns_404 PASSED [ 60%]
tests/test_issues.py::TestNonexistentResourceHandling::test_update_nonexistent_issue_returns_404 PASSED [ 63%]
tests/test_issues.py::TestNonexistentResourceHandling::test_delete_nonexistent_issue_returns_404 PASSED [ 65%]
tests/test_issues.py::TestSearchAndFiltering::test_search_by_title_substring PASSED [ 68%]
tests/test_issues.py::TestSearchAndFiltering::test_search_no_matches PASSED [ 71%]
tests/test_issues.py::TestSearchAndFiltering::test_filter_by_status_open PASSED [ 73%]
tests/test_issues.py::TestSearchAndFiltering::test_filter_by_status_in_progress PASSED [ 76%]
tests/test_issues.py::TestSearchAndFiltering::test_filter_by_status_resolved PASSED [ 78%]
tests/test_issues.py::TestSearchAndFiltering::test_filter_by_priority_high PASSED [ 81%]
tests/test_issues.py::TestSearchAndFiltering::test_filter_by_priority_low PASSED [ 84%]
tests/test_issues.py::TestSearchAndFiltering::test_combined_search_status_priority PASSED [ 86%]
tests/test_issues.py::TestMetricsAndStats::test_stats_on_empty_database PASSED [ 89%]
tests/test_issues.py::TestMetricsAndStats::test_stats_with_mixed_issues PASSED [ 92%]
tests/test_issues.py::TestSystemAndDelivery::test_healthcheck_endpoint PASSED [ 94%]
tests/test_issues.py::TestSystemAndDelivery::test_dashboard_html_served_at_root PASSED [ 97%]
tests/test_issues.py::TestSystemAndDelivery::test_static_css_and_js_served PASSED [100%]

============================= 38 passed in 3.49s ==============================
```

> **Note on Test Isolation:** Tests use `tests/test_issues.db` via an automated fixture. Running tests will never overwrite or erase your development database (`issuetrack.db`).

---

## 📡 API Endpoint Documentation

All endpoints return data formatted in JSON.

### Endpoints Overview

| Method | Endpoint | Query Parameters | Description | Status Code |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | None | Serves the web dashboard HTML interface | `200 OK` |
| `GET` | `/health` | None | Service & database connectivity health check | `200 OK` |
| `POST` | `/api/issues` | None | Create a new issue | `201 Created` |
| `GET` | `/api/issues` | `search`, `status`, `priority`, `limit`, `offset` | List issues with optional search & filters | `200 OK` |
| `GET` | `/api/issues/stats`| None | Summary counts for dashboard metric cards | `200 OK` |
| `GET` | `/api/issues/{id}`| Path: `id` (int) | Retrieve detailed information for an issue | `200 OK` / `404` |
| `PUT` | `/api/issues/{id}`| Path: `id` (int) | Update issue (full or partial fields) | `200 OK` / `404` |
| `DELETE`| `/api/issues/{id}`| Path: `id` (int) | Permanently delete an issue | `200 OK` / `404` |

### Sample Payloads

#### Create Issue Request (`POST /api/issues`):
```json
{
  "title": "Payment gateway timeout on checkout",
  "description": "Users report 504 gateway timeout when selecting UPI payment option.",
  "status": "Open",
  "priority": "High",
  "assigned_to": "Ananya Verma"
}
```

#### Successful Response (`201 Created`):
```json
{
  "id": 1,
  "title": "Payment gateway timeout on checkout",
  "description": "Users report 504 gateway timeout when selecting UPI payment option.",
  "status": "Open",
  "priority": "High",
  "assigned_to": "Ananya Verma",
  "created_at": "2026-11-13 10:15:00",
  "updated_at": "2026-11-13 10:15:00"
}
```

#### Dashboard Stats Response (`GET /api/issues/stats`):
```json
{
  "total": 5,
  "open": 2,
  "in_progress": 1,
  "resolved": 2,
  "low_priority": 1,
  "medium_priority": 2,
  "high_priority": 2
}
```

---

## 📸 Screenshots

To view the user interface components in your browser, start the server and navigate to `http://127.0.0.1:8000/`.

### UI Highlights:
1. **Header & Health Indicator:** Live pulsing green dot signaling active SQLite and FastAPI connectivity.
2. **Metric Summary Grid:** 4 prominent cards displaying counts for Total, Open, In Progress, and Resolved issues.
3. **Interactive Search & Filter Controls:** Substring search bar with instant debounce and dropdown selectors for status and priority.
4. **Issue Management Table:** High-contrast priority and status badges, developer avatar initials, and action buttons.
5. **Issue Creation & Edit Modals:** Clean floating dialogs with real-time field validation and character counters.
6. **Toast Feedback:** Floating notifications on successful creation, status changes, and deletions.

*(To add screenshot images to your GitHub repository, place image files in a `docs/screenshots/` folder and link them here using `![Dashboard Preview](docs/screenshots/dashboard.png)`)*

---

## 🔮 Future Improvements

1. **Authentication & RBAC:** Implement JWT-based user authentication and Role-Based Access Control (`Admin`, `Developer`, `Reporter`).
2. **Full-Text Search (FTS5):** Migrate search queries to SQLite's native `FTS5` extension for tokenized search and BM25 relevance scoring.
3. **Database Migration Tooling:** Integrate Alembic to manage database schema migrations as the data model expands.
4. **Audit Trail & Activity Log:** Track an immutable history table logging who changed what issue attribute and when.
5. **File Attachments:** Support uploading crash logs and diagnostic screenshots stored in local storage or S3-compatible buckets.
