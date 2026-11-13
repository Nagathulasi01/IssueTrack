"""
IssueTrack Comprehensive Automated Test Suite
Pytest-based test suite verifying all CRUD operations, data validation,
search, filtering, error handling, status codes, and test database isolation.
"""

import pytest


# ============================================================================
# 1. ISSUE CREATION TESTS
# ============================================================================

class TestIssueCreation:
    """Test suite covering issue creation, defaults, and field assignments."""

    def test_create_issue_with_all_fields(self, client):
        """Verify successful issue creation with all fields explicitly provided."""
        payload = {
            "title": "Payment gateway timeout on checkout",
            "description": "Users report 504 gateway timeout when selecting UPI payment option.",
            "status": "In Progress",
            "priority": "High",
            "assigned_to": "Ananya Verma"
        }
        response = client.post("/api/issues", json=payload)
        assert response.status_code == 201

        data = response.json()
        assert data["id"] == 1
        assert data["title"] == payload["title"]
        assert data["description"] == payload["description"]
        assert data["status"] == "In Progress"
        assert data["priority"] == "High"
        assert data["assigned_to"] == "Ananya Verma"
        assert "created_at" in data
        assert "updated_at" in data
        assert data["created_at"] == data["updated_at"]

    def test_create_issue_with_default_values(self, client):
        """Verify that omitting optional fields correctly applies default values."""
        payload = {
            "title": "Fix navbar alignment on mobile view"
        }
        response = client.post("/api/issues", json=payload)
        assert response.status_code == 201

        data = response.json()
        assert data["title"] == payload["title"]
        assert data["description"] == ""
        assert data["status"] == "Open"          # Default status
        assert data["priority"] == "Medium"      # Default priority
        assert data["assigned_to"] == "Unassigned"  # Default assignee

    def test_create_issue_strips_whitespace(self, client):
        """Verify that leading/trailing whitespaces in title and assignee are trimmed."""
        payload = {
            "title": "   Database query needs index on user_id   ",
            "assigned_to": "   Rohit Sharma   "
        }
        response = client.post("/api/issues", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Database query needs index on user_id"
        assert data["assigned_to"] == "Rohit Sharma"


# ============================================================================
# 2. ISSUE RETRIEVAL TESTS
# ============================================================================

class TestIssueRetrieval:
    """Test suite covering issue retrieval (all, by ID, empty state, pagination)."""

    def test_get_all_issues_empty_database(self, client):
        """Verify that requesting issues on an empty database returns an empty list and 200 OK."""
        response = client.get("/api/issues")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_all_issues_multiple_records(self, client):
        """Verify retrieving multiple issues sorted by newest ID first."""
        client.post("/api/issues", json={"title": "First issue logged"})
        client.post("/api/issues", json={"title": "Second issue logged"})
        client.post("/api/issues", json={"title": "Third issue logged"})

        response = client.get("/api/issues")
        assert response.status_code == 200
        issues = response.json()
        assert len(issues) == 3
        # Should be ordered descending by ID
        assert issues[0]["id"] == 3
        assert issues[1]["id"] == 2
        assert issues[2]["id"] == 1

    def test_get_all_issues_pagination(self, client):
        """Verify limit and offset query parameters for pagination."""
        for i in range(1, 6):
            client.post("/api/issues", json={"title": f"Batch Issue {i}"})

        # Fetch limit 2, offset 0
        res_page1 = client.get("/api/issues?limit=2&offset=0")
        assert res_page1.status_code == 200
        page1 = res_page1.json()
        assert len(page1) == 2
        assert page1[0]["id"] == 5
        assert page1[1]["id"] == 4

        # Fetch limit 2, offset 2
        res_page2 = client.get("/api/issues?limit=2&offset=2")
        assert res_page2.status_code == 200
        page2 = res_page2.json()
        assert len(page2) == 2
        assert page2[0]["id"] == 3
        assert page2[1]["id"] == 2

    def test_get_issue_by_valid_id(self, client):
        """Verify retrieving a single issue by primary key ID."""
        created = client.post("/api/issues", json={
            "title": "Bug in policy claim upload",
            "description": "File upload crashes when PDF is password protected.",
            "status": "Open",
            "priority": "High",
            "assigned_to": "Kavya Rao"
        }).json()

        response = client.get(f"/api/issues/{created['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created["id"]
        assert data["title"] == "Bug in policy claim upload"
        assert data["description"] == "File upload crashes when PDF is password protected."
        assert data["status"] == "Open"
        assert data["priority"] == "High"
        assert data["assigned_to"] == "Kavya Rao"


# ============================================================================
# 3. ISSUE UPDATE TESTS
# ============================================================================

class TestIssueUpdate:
    """Test suite covering full and partial issue updates."""

    def test_update_all_fields(self, client):
        """Verify updating all fields of an existing issue."""
        created = client.post("/api/issues", json={
            "title": "Incorrect premium calculation",
            "description": "GST calculation is off by 1 rupee.",
            "status": "Open",
            "priority": "Medium",
            "assigned_to": "Rahul Mehta"
        }).json()

        update_payload = {
            "title": "Fixed premium calculation rounding error",
            "description": "Rounded cents before applying 18% GST.",
            "status": "Resolved",
            "priority": "Low",
            "assigned_to": "Rahul Mehta (Lead)"
        }
        response = client.put(f"/api/issues/{created['id']}", json=update_payload)
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == created["id"]
        assert data["title"] == update_payload["title"]
        assert data["description"] == update_payload["description"]
        assert data["status"] == "Resolved"
        assert data["priority"] == "Low"
        assert data["assigned_to"] == "Rahul Mehta (Lead)"
        assert data["created_at"] == created["created_at"]
        assert data["updated_at"] >= created["updated_at"]

    def test_partial_update_status_only(self, client):
        """Verify updating only status leaves other fields untouched."""
        created = client.post("/api/issues", json={
            "title": "Race condition in OTP dispatch",
            "description": "Rapid clicks trigger multiple SMS.",
            "status": "Open",
            "priority": "High",
            "assigned_to": "Deepak Verma"
        }).json()

        response = client.put(f"/api/issues/{created['id']}", json={"status": "In Progress"})
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "In Progress"
        assert data["title"] == created["title"]
        assert data["description"] == created["description"]
        assert data["priority"] == "High"
        assert data["assigned_to"] == "Deepak Verma"

    def test_partial_update_priority_only(self, client):
        """Verify updating only priority leaves other fields untouched."""
        created = client.post("/api/issues", json={
            "title": "Cosmetic typo on checkout button",
            "status": "Open",
            "priority": "Low"
        }).json()

        response = client.put(f"/api/issues/{created['id']}", json={"priority": "Medium"})
        assert response.status_code == 200
        assert response.json()["priority"] == "Medium"
        assert response.json()["status"] == "Open"

    def test_update_with_empty_payload_returns_existing(self, client):
        """Verify sending an empty JSON body in PUT returns existing record without error."""
        created = client.post("/api/issues", json={
            "title": "Minor styling glitch on footer"
        }).json()

        response = client.put(f"/api/issues/{created['id']}", json={})
        assert response.status_code == 200
        assert response.json()["title"] == "Minor styling glitch on footer"


# ============================================================================
# 4. ISSUE DELETION TESTS
# ============================================================================

class TestIssueDeletion:
    """Test suite covering issue deletion and data removal verification."""

    def test_delete_issue_success(self, client):
        """Verify successful deletion returns 200 OK and subsequent lookup returns 404."""
        created = client.post("/api/issues", json={
            "title": "Temporary issue to be deleted"
        }).json()
        issue_id = created["id"]

        # Delete issue
        del_resp = client.delete(f"/api/issues/{issue_id}")
        assert del_resp.status_code == 200
        del_data = del_resp.json()
        assert del_data["id"] == issue_id
        assert "successfully deleted" in del_data["message"].lower()

        # Verify lookup returns 404
        get_resp = client.get(f"/api/issues/{issue_id}")
        assert get_resp.status_code == 404

        # Verify list no longer contains the issue
        list_resp = client.get("/api/issues")
        assert len(list_resp.json()) == 0

    def test_delete_already_deleted_issue_returns_404(self, client):
        """Verify attempting to delete an already deleted issue returns 404."""
        created = client.post("/api/issues", json={
            "title": "Double deletion test issue"
        }).json()
        issue_id = created["id"]

        # First deletion -> 200
        assert client.delete(f"/api/issues/{issue_id}").status_code == 200
        # Second deletion -> 404
        assert client.delete(f"/api/issues/{issue_id}").status_code == 404


# ============================================================================
# 5. DATA VALIDATION & ERROR HANDLING TESTS
# ============================================================================

class TestDataValidation:
    """Test suite covering input validation and 422 Unprocessable Entity responses."""

    def test_missing_required_title(self, client):
        """Verify that omitting required title field returns 422."""
        response = client.post("/api/issues", json={
            "description": "Missing title",
            "status": "Open"
        })
        assert response.status_code == 422

    def test_title_too_short(self, client):
        """Verify that title under 3 characters is rejected with 422."""
        response = client.post("/api/issues", json={"title": "AB"})
        assert response.status_code == 422

    def test_title_whitespace_only(self, client):
        """Verify that title with only spaces is rejected with 422."""
        response = client.post("/api/issues", json={"title": "     "})
        assert response.status_code == 422

    def test_title_exceeds_max_length(self, client):
        """Verify that title longer than 120 characters is rejected with 422."""
        long_title = "A" * 121
        response = client.post("/api/issues", json={"title": long_title})
        assert response.status_code == 422

    def test_invalid_status_enum(self, client):
        """Verify that status outside (Open, In Progress, Resolved) returns 422."""
        response = client.post("/api/issues", json={
            "title": "Valid title",
            "status": "Closed"  # Not a valid status
        })
        assert response.status_code == 422

    def test_invalid_priority_enum(self, client):
        """Verify that priority outside (Low, Medium, High) returns 422."""
        response = client.post("/api/issues", json={
            "title": "Valid title",
            "priority": "Critical"  # Not a valid priority
        })
        assert response.status_code == 422

    def test_update_with_invalid_title(self, client):
        """Verify that updating with an invalid short title returns 422."""
        created = client.post("/api/issues", json={"title": "Valid Initial Title"}).json()
        response = client.put(f"/api/issues/{created['id']}", json={"title": "X"})
        assert response.status_code == 422

    def test_update_with_invalid_status(self, client):
        """Verify that updating with an invalid status returns 422."""
        created = client.post("/api/issues", json={"title": "Valid Initial Title"}).json()
        response = client.put(f"/api/issues/{created['id']}", json={"status": "Archived"})
        assert response.status_code == 422

    def test_non_integer_issue_id_in_path(self, client):
        """Verify that non-numeric ID in path parameter returns 422."""
        response = client.get("/api/issues/not-a-number")
        assert response.status_code == 422


# ============================================================================
# 6. NONEXISTENT ID / 404 NOT FOUND TESTS
# ============================================================================

class TestNonexistentResourceHandling:
    """Test suite verifying 404 Not Found handling for invalid IDs."""

    def test_get_nonexistent_issue_returns_404(self, client):
        """Verify GET on nonexistent ID returns 404 with error detail."""
        response = client.get("/api/issues/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_nonexistent_issue_returns_404(self, client):
        """Verify PUT on nonexistent ID returns 404 with error detail."""
        response = client.put("/api/issues/99999", json={"title": "New Title"})
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_delete_nonexistent_issue_returns_404(self, client):
        """Verify DELETE on nonexistent ID returns 404 with error detail."""
        response = client.delete("/api/issues/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


# ============================================================================
# 7. SEARCH AND FILTERING TESTS
# ============================================================================

class TestSearchAndFiltering:
    """Test suite covering search, status filter, priority filter, and combinations."""

    @pytest.fixture(autouse=True)
    def seed_test_issues(self, client):
        """Seeds a diverse set of issues for filtering and search assertions."""
        client.post("/api/issues", json={"title": "Crash on mobile payment screen", "status": "Open", "priority": "High"})
        client.post("/api/issues", json={"title": "Payment webhook retry backoff", "status": "In Progress", "priority": "High"})
        client.post("/api/issues", json={"title": "Database connection pool leak", "status": "In Progress", "priority": "Medium"})
        client.post("/api/issues", json={"title": "Update FAQ terms link on footer", "status": "Resolved", "priority": "Low"})
        client.post("/api/issues", json={"title": "Optimize payment quote API latency", "status": "Resolved", "priority": "High"})

    def test_search_by_title_substring(self, client):
        """Verify substring search matching multiple records case-insensitively."""
        response = client.get("/api/issues?search=payment")
        assert response.status_code == 200
        results = response.json()
        assert len(results) == 3
        for item in results:
            assert "payment" in item["title"].lower()

    def test_search_no_matches(self, client):
        """Verify search with no matches returns empty list and 200 OK."""
        response = client.get("/api/issues?search=nonexistent_xyz_keyword")
        assert response.status_code == 200
        assert response.json() == []

    def test_filter_by_status_open(self, client):
        """Verify filtering by status=Open."""
        response = client.get("/api/issues?status=Open")
        assert response.status_code == 200
        results = response.json()
        assert len(results) == 1
        assert results[0]["title"] == "Crash on mobile payment screen"

    def test_filter_by_status_in_progress(self, client):
        """Verify filtering by status=In Progress."""
        response = client.get("/api/issues?status=In Progress")
        assert response.status_code == 200
        results = response.json()
        assert len(results) == 2
        for item in results:
            assert item["status"] == "In Progress"

    def test_filter_by_status_resolved(self, client):
        """Verify filtering by status=Resolved."""
        response = client.get("/api/issues?status=Resolved")
        assert response.status_code == 200
        results = response.json()
        assert len(results) == 2
        for item in results:
            assert item["status"] == "Resolved"

    def test_filter_by_priority_high(self, client):
        """Verify filtering by priority=High."""
        response = client.get("/api/issues?priority=High")
        assert response.status_code == 200
        results = response.json()
        assert len(results) == 3
        for item in results:
            assert item["priority"] == "High"

    def test_filter_by_priority_low(self, client):
        """Verify filtering by priority=Low."""
        response = client.get("/api/issues?priority=Low")
        assert response.status_code == 200
        results = response.json()
        assert len(results) == 1
        assert results[0]["title"] == "Update FAQ terms link on footer"

    def test_combined_search_status_priority(self, client):
        """Verify combined search, status, and priority query filters."""
        # search "payment", status "In Progress", priority "High"
        response = client.get("/api/issues?search=payment&status=In Progress&priority=High")
        assert response.status_code == 200
        results = response.json()
        assert len(results) == 1
        assert results[0]["title"] == "Payment webhook retry backoff"


# ============================================================================
# 8. METRICS AND AGGREGATION TESTS
# ============================================================================

class TestMetricsAndStats:
    """Test suite covering aggregate summary counts on /api/issues/stats."""

    def test_stats_on_empty_database(self, client):
        """Verify stats endpoint returns all zeroes when no issues exist."""
        response = client.get("/api/issues/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["open"] == 0
        assert data["in_progress"] == 0
        assert data["resolved"] == 0
        assert data["high_priority"] == 0
        assert data["medium_priority"] == 0
        assert data["low_priority"] == 0

    def test_stats_with_mixed_issues(self, client):
        """Verify stats counts match actual distributions across status and priority."""
        client.post("/api/issues", json={"title": "Issue 1", "status": "Open", "priority": "High"})
        client.post("/api/issues", json={"title": "Issue 2", "status": "Open", "priority": "Medium"})
        client.post("/api/issues", json={"title": "Issue 3", "status": "In Progress", "priority": "High"})
        client.post("/api/issues", json={"title": "Issue 4", "status": "Resolved", "priority": "Low"})
        client.post("/api/issues", json={"title": "Issue 5", "status": "Resolved", "priority": "High"})

        response = client.get("/api/issues/stats")
        assert response.status_code == 200
        stats = response.json()
        assert stats["total"] == 5
        assert stats["open"] == 2
        assert stats["in_progress"] == 1
        assert stats["resolved"] == 2
        assert stats["high_priority"] == 3
        assert stats["medium_priority"] == 1
        assert stats["low_priority"] == 1


# ============================================================================
# 9. HEALTH AND STATIC ASSET DELIVERY TESTS
# ============================================================================

class TestSystemAndDelivery:
    """Test suite covering healthcheck and static frontend asset delivery."""

    def test_healthcheck_endpoint(self, client):
        """Verify health check returns status healthy and database connected."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"

    def test_dashboard_html_served_at_root(self, client):
        """Verify that GET / returns the dashboard HTML with required markup."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        assert "IssueTrack" in response.text
        assert "Engineering Issue Board" in response.text

    def test_static_css_and_js_served(self, client):
        """Verify static CSS stylesheet and JavaScript client are served with 200 OK."""
        css_resp = client.get("/static/css/style.css")
        assert css_resp.status_code == 200
        assert "var(--bg-app)" in css_resp.text

        js_resp = client.get("/static/js/app.js")
        assert js_resp.status_code == 200
        assert "createIssue" in js_resp.text
