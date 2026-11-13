/**
 * IssueTrack – Vanilla JavaScript Application Client
 * Modern ES6+ architecture connecting dashboard UI to FastAPI backend.
 */

(() => {
  "use strict";

  // Application State
  const state = {
    issues: [],
    stats: { total: 0, open: 0, in_progress: 0, resolved: 0 },
    filters: {
      search: "",
      status: "",
      priority: ""
    },
    activeEditIssue: null,
    pendingDeleteId: null,
    debounceTimer: null,
    isLoading: false
  };

  // DOM Element Selectors
  const elements = {
    // API Status
    apiStatusDot: document.getElementById("apiStatusDot"),
    apiStatusText: document.getElementById("apiStatusText"),

    // Metric Cards
    statTotal: document.getElementById("statTotal"),
    statOpen: document.getElementById("statOpen"),
    statProgress: document.getElementById("statProgress"),
    statResolved: document.getElementById("statResolved"),
    cardTotal: document.getElementById("cardTotal"),
    cardOpen: document.getElementById("cardOpen"),
    cardProgress: document.getElementById("cardProgress"),
    cardResolved: document.getElementById("cardResolved"),

    // Controls
    searchInput: document.getElementById("searchInput"),
    statusFilter: document.getElementById("statusFilter"),
    priorityFilter: document.getElementById("priorityFilter"),
    resetFiltersBtn: document.getElementById("resetFiltersBtn"),
    refreshBtn: document.getElementById("refreshBtn"),
    issuesCountLabel: document.getElementById("issuesCountLabel"),
    activeFilterBadge: document.getElementById("activeFilterBadge"),

    // Table & States
    issuesTableBody: document.getElementById("issuesTableBody"),
    loadingOverlay: document.getElementById("loadingOverlay"),
    emptyState: document.getElementById("emptyState"),
    emptyStateDesc: document.getElementById("emptyStateDesc"),
    emptyStateActionBtn: document.getElementById("emptyStateActionBtn"),

    // Modals
    createModal: document.getElementById("createModal"),
    createIssueForm: document.getElementById("createIssueForm"),
    createTitle: document.getElementById("createTitle"),
    createDescription: document.getElementById("createDescription"),
    createPriority: document.getElementById("createPriority"),
    createStatus: document.getElementById("createStatus"),
    createAssignedTo: document.getElementById("createAssignedTo"),
    createSubmitBtn: document.getElementById("createSubmitBtn"),
    openCreateModalBtn: document.getElementById("openCreateModalBtn"),

    editModal: document.getElementById("editModal"),
    editIssueForm: document.getElementById("editIssueForm"),
    editIssueId: document.getElementById("editIssueId"),
    editTitle: document.getElementById("editTitle"),
    editDescription: document.getElementById("editDescription"),
    editPriority: document.getElementById("editPriority"),
    editStatus: document.getElementById("editStatus"),
    editAssignedTo: document.getElementById("editAssignedTo"),
    editSubmitBtn: document.getElementById("editSubmitBtn"),

    deleteModal: document.getElementById("deleteModal"),
    deleteIssueIdText: document.getElementById("deleteIssueIdText"),
    deleteIssueTitleText: document.getElementById("deleteIssueTitleText"),
    confirmDeleteBtn: document.getElementById("confirmDeleteBtn"),

    toastContainer: document.getElementById("toastContainer")
  };

  // =========================================================================
  // API CLIENT METHODS
  // =========================================================================

  const API = {
    /**
     * Checks server health and database status
     */
    async checkHealth() {
      try {
        const res = await fetch("/health");
        if (!res.ok) throw new Error("API returned non-200");
        const data = await res.json();
        return data.status === "healthy";
      } catch (err) {
        return false;
      }
    },

    /**
     * Fetches issues filtered by search keyword, status, and priority
     */
    async getIssues(params = {}) {
      const query = new URLSearchParams();
      if (params.search) query.append("search", params.search);
      if (params.status) query.append("status", params.status);
      if (params.priority) query.append("priority", params.priority);

      const url = `/api/issues?${query.toString()}`;
      const res = await fetch(url);
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || `Failed to fetch issues (${res.status})`);
      }
      return await res.json();
    },

    /**
     * Fetches aggregate issue statistics
     */
    async getStats() {
      const res = await fetch("/api/issues/stats");
      if (!res.ok) throw new Error("Failed to fetch statistics");
      return await res.json();
    },

    /**
     * Creates a new issue
     */
    async createIssue(payload) {
      const res = await fetch("/api/issues", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        const message = Array.isArray(errorData.detail)
          ? errorData.detail.map(d => d.msg).join(", ")
          : (errorData.detail || "Failed to create issue");
        throw new Error(message);
      }
      return await res.json();
    },

    /**
     * Updates an issue by ID
     */
    async updateIssue(id, payload) {
      const res = await fetch(`/api/issues/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        const message = Array.isArray(errorData.detail)
          ? errorData.detail.map(d => d.msg).join(", ")
          : (errorData.detail || "Failed to update issue");
        throw new Error(message);
      }
      return await res.json();
    },

    /**
     * Deletes an issue by ID
     */
    async deleteIssue(id) {
      const res = await fetch(`/api/issues/${id}`, {
        method: "DELETE"
      });
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || "Failed to delete issue");
      }
      return await res.json();
    }
  };

  // =========================================================================
  // UI HELPERS & NOTIFICATIONS
  // =========================================================================

  function showLoading(show) {
    state.isLoading = show;
    if (elements.loadingOverlay) {
      if (show) {
        elements.loadingOverlay.classList.remove("hidden");
      } else {
        elements.loadingOverlay.classList.add("hidden");
      }
    }
  }

  function showToast(message, type = "success") {
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;

    const icon = type === "success" ? "✓" : type === "error" ? "✕" : "ℹ";
    toast.innerHTML = `
      <span style="font-weight: bold; font-size: 1.1rem;">${icon}</span>
      <span>${escapeHtml(message)}</span>
    `;

    elements.toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateY(10px)";
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }

  function escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function getInitials(name) {
    if (!name || name === "Unassigned") return "UA";
    const parts = name.trim().split(/\s+/);
    if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  }

  function formatDate(isoStr) {
    if (!isoStr) return "-";
    try {
      // Handles both "YYYY-MM-DD HH:MM:SS" and ISO format
      const date = new Date(isoStr.replace(" ", "T") + "Z");
      return date.toLocaleDateString(undefined, {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit"
      });
    } catch {
      return isoStr;
    }
  }

  // =========================================================================
  // MODAL MANAGEMENT
  // =========================================================================

  function openModal(modal) {
    if (!modal) return;
    modal.classList.add("open");
    // Focus first text input if available
    const firstInput = modal.querySelector("input:not([type=hidden]), textarea");
    if (firstInput) {
      setTimeout(() => firstInput.focus(), 100);
    }
  }

  function closeModal(modal) {
    if (!modal) return;
    modal.classList.remove("open");
  }

  // Bind close buttons and backdrop clicks
  document.querySelectorAll("[data-close-modal]").forEach(btn => {
    btn.addEventListener("click", () => {
      const modalId = btn.getAttribute("data-close-modal");
      closeModal(document.getElementById(modalId));
    });
  });

  document.querySelectorAll(".modal-backdrop").forEach(backdrop => {
    backdrop.addEventListener("click", (e) => {
      if (e.target === backdrop) {
        closeModal(backdrop);
      }
    });
  });

  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      document.querySelectorAll(".modal-backdrop.open").forEach(closeModal);
    }
  });

  // =========================================================================
  // RENDERING METHODS
  // =========================================================================

  function renderStats(stats) {
    elements.statTotal.textContent = stats.total ?? 0;
    elements.statOpen.textContent = stats.open ?? 0;
    elements.statProgress.textContent = stats.in_progress ?? 0;
    elements.statResolved.textContent = stats.resolved ?? 0;

    // Highlight card corresponding to active filter
    [elements.cardTotal, elements.cardOpen, elements.cardProgress, elements.cardResolved].forEach(card => {
      card.classList.remove("active");
    });

    if (!state.filters.status) {
      elements.cardTotal.classList.add("active");
    } else if (state.filters.status === "Open") {
      elements.cardOpen.classList.add("active");
    } else if (state.filters.status === "In Progress") {
      elements.cardProgress.classList.add("active");
    } else if (state.filters.status === "Resolved") {
      elements.cardResolved.classList.add("active");
    }
  }

  function renderIssues(issues) {
    elements.issuesTableBody.innerHTML = "";
    elements.issuesCountLabel.textContent = `Showing ${issues.length} issue${issues.length === 1 ? "" : "s"}`;

    if (issues.length === 0) {
      elements.emptyState.style.display = "block";
      if (state.filters.search || state.filters.status || state.filters.priority) {
        elements.emptyStateDesc.textContent = "No issues match your active search and filter criteria.";
        elements.emptyStateActionBtn.textContent = "Clear Active Filters";
      } else {
        elements.emptyStateDesc.textContent = "No issues have been created yet. Start by logging your first bug or task.";
        elements.emptyStateActionBtn.textContent = "Create New Issue";
      }
      return;
    }

    elements.emptyState.style.display = "none";

    issues.forEach(issue => {
      const tr = document.createElement("tr");
      tr.id = `issue-row-${issue.id}`;

      // Status Badge Style
      const statusClass = issue.status === "Open"
        ? "badge-status-open"
        : issue.status === "In Progress"
        ? "badge-status-inprogress"
        : "badge-status-resolved";

      // Priority Badge Style
      const priorityClass = issue.priority === "High"
        ? "badge-priority-high"
        : issue.priority === "Medium"
        ? "badge-priority-medium"
        : "badge-priority-low";

      const initials = getInitials(issue.assigned_to);

      tr.innerHTML = `
        <td class="issue-id">#${issue.id}</td>
        <td class="issue-title-cell">
          <a class="issue-title-link" data-action="edit" data-id="${issue.id}">${escapeHtml(issue.title)}</a>
          ${issue.description ? `<div class="issue-desc-excerpt" title="${escapeHtml(issue.description)}">${escapeHtml(issue.description)}</div>` : ""}
        </td>
        <td>
          <span class="badge ${priorityClass}">
            ${escapeHtml(issue.priority)}
          </span>
        </td>
        <td>
          <select class="filter-select badge ${statusClass}" data-action="quick-status" data-id="${issue.id}" style="padding: 0.25rem 0.5rem; font-size: 0.78rem;">
            <option value="Open" ${issue.status === "Open" ? "selected" : ""}>Open</option>
            <option value="In Progress" ${issue.status === "In Progress" ? "selected" : ""}>In Progress</option>
            <option value="Resolved" ${issue.status === "Resolved" ? "selected" : ""}>Resolved</option>
          </select>
        </td>
        <td>
          <div class="developer-tag">
            <span class="developer-avatar">${initials}</span>
            <span>${escapeHtml(issue.assigned_to || "Unassigned")}</span>
          </div>
        </td>
        <td>
          <span class="date-text" title="${escapeHtml(issue.created_at)}">
            ${formatDate(issue.created_at)}
          </span>
        </td>
        <td class="actions-cell">
          <button class="btn btn-secondary btn-sm btn-icon" data-action="edit" data-id="${issue.id}" title="Edit Issue">
            ✏️
          </button>
          <button class="btn btn-outline-danger btn-sm btn-icon" data-action="delete" data-id="${issue.id}" data-title="${escapeHtml(issue.title)}" title="Delete Issue">
            🗑️
          </button>
        </td>
      `;

      elements.issuesTableBody.appendChild(tr);
    });
  }

  // =========================================================================
  // DATA REFRESH & COORDINATION
  // =========================================================================

  async function loadData() {
    showLoading(true);
    try {
      const [issues, stats] = await Promise.all([
        API.getIssues(state.filters),
        API.getStats()
      ]);

      state.issues = issues;
      state.stats = stats;

      renderStats(stats);
      renderIssues(issues);
    } catch (err) {
      console.error("Data load failure:", err);
      showToast(`Error: ${err.message}`, "error");
    } finally {
      showLoading(false);
    }
  }

  async function updateHealthBadge() {
    const isOnline = await API.checkHealth();
    if (isOnline) {
      elements.apiStatusDot.className = "status-indicator online";
      elements.apiStatusText.textContent = "API & SQLite Online";
    } else {
      elements.apiStatusDot.className = "status-indicator offline";
      elements.apiStatusText.textContent = "API Offline";
    }
  }

  // =========================================================================
  // EVENT LISTENERS & USER ACTIONS
  // =========================================================================

  // Search Input with 300ms Debounce
  elements.searchInput.addEventListener("input", (e) => {
    clearTimeout(state.debounceTimer);
    state.debounceTimer = setTimeout(() => {
      state.filters.search = e.target.value.trim();
      loadData();
    }, 300);
  });

  // Status Filter Dropdown
  elements.statusFilter.addEventListener("change", (e) => {
    state.filters.status = e.target.value;
    loadData();
  });

  // Priority Filter Dropdown
  elements.priorityFilter.addEventListener("change", (e) => {
    state.filters.priority = e.target.value;
    loadData();
  });

  // Reset Filters Button
  elements.resetFiltersBtn.addEventListener("click", () => {
    state.filters = { search: "", status: "", priority: "" };
    elements.searchInput.value = "";
    elements.statusFilter.value = "";
    elements.priorityFilter.value = "";
    loadData();
  });

  // Empty State Action
  elements.emptyStateActionBtn.addEventListener("click", () => {
    if (state.filters.search || state.filters.status || state.filters.priority) {
      elements.resetFiltersBtn.click();
    } else {
      openModal(elements.createModal);
    }
  });

  // Metric Cards Click (Quick Filter by Status)
  [
    { card: elements.cardTotal, status: "" },
    { card: elements.cardOpen, status: "Open" },
    { card: elements.cardProgress, status: "In Progress" },
    { card: elements.cardResolved, status: "Resolved" }
  ].forEach(({ card, status }) => {
    card.addEventListener("click", () => {
      state.filters.status = status;
      elements.statusFilter.value = status;
      loadData();
    });
  });

  // Refresh Button
  elements.refreshBtn.addEventListener("click", () => {
    elements.refreshBtn.disabled = true;
    elements.refreshBtn.textContent = "⏳ Refreshing...";
    loadData().finally(() => {
      elements.refreshBtn.disabled = false;
      elements.refreshBtn.textContent = "🔄 Refresh Data";
    });
  });

  // Open Create Modal Button
  elements.openCreateModalBtn.addEventListener("click", () => {
    elements.createIssueForm.reset();
    openModal(elements.createModal);
  });

  // Create Issue Form Submit
  elements.createIssueForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const title = elements.createTitle.value.trim();
    if (title.length < 3) {
      showToast("Title must be at least 3 characters", "error");
      elements.createTitle.focus();
      return;
    }

    const payload = {
      title: title,
      description: elements.createDescription.value.trim(),
      priority: elements.createPriority.value,
      status: elements.createStatus.value,
      assigned_to: elements.createAssignedTo.value.trim() || "Unassigned"
    };

    elements.createSubmitBtn.disabled = true;
    elements.createSubmitBtn.textContent = "Creating...";

    try {
      const created = await API.createIssue(payload);
      showToast(`Issue #${created.id} created successfully!`, "success");
      closeModal(elements.createModal);
      elements.createIssueForm.reset();
      await loadData();
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      elements.createSubmitBtn.disabled = false;
      elements.createSubmitBtn.textContent = "Create Issue";
    }
  });

  // Table Event Delegation (Edit, Delete, Quick Status)
  elements.issuesTableBody.addEventListener("click", (e) => {
    const editBtn = e.target.closest('[data-action="edit"]');
    const deleteBtn = e.target.closest('[data-action="delete"]');

    if (editBtn) {
      const id = parseInt(editBtn.getAttribute("data-id"), 10);
      const issue = state.issues.find(i => i.id === id);
      if (issue) {
        populateEditModal(issue);
        openModal(elements.editModal);
      }
    }

    if (deleteBtn) {
      const id = parseInt(deleteBtn.getAttribute("data-id"), 10);
      const title = deleteBtn.getAttribute("data-title") || "";
      state.pendingDeleteId = id;
      elements.deleteIssueIdText.textContent = `#${id}`;
      elements.deleteIssueTitleText.textContent = title;
      openModal(elements.deleteModal);
    }
  });

  // Quick Status Change on inline select
  elements.issuesTableBody.addEventListener("change", async (e) => {
    const quickSelect = e.target.closest('[data-action="quick-status"]');
    if (!quickSelect) return;

    const id = parseInt(quickSelect.getAttribute("data-id"), 10);
    const newStatus = quickSelect.value;

    try {
      await API.updateIssue(id, { status: newStatus });
      showToast(`Issue #${id} updated to ${newStatus}`, "success");
      await loadData();
    } catch (err) {
      showToast(err.message, "error");
      await loadData(); // Revert select UI
    }
  });

  // Edit Issue Setup & Submit
  function populateEditModal(issue) {
    state.activeEditIssue = issue;
    elements.editIssueId.value = issue.id;
    elements.editTitle.value = issue.title;
    elements.editDescription.value = issue.description || "";
    elements.editPriority.value = issue.priority;
    elements.editStatus.value = issue.status;
    elements.editAssignedTo.value = issue.assigned_to || "";
  }

  elements.editIssueForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = parseInt(elements.editIssueId.value, 10);
    const title = elements.editTitle.value.trim();

    if (title.length < 3) {
      showToast("Title must be at least 3 characters", "error");
      elements.editTitle.focus();
      return;
    }

    const payload = {
      title: title,
      description: elements.editDescription.value.trim(),
      priority: elements.editPriority.value,
      status: elements.editStatus.value,
      assigned_to: elements.editAssignedTo.value.trim() || "Unassigned"
    };

    elements.editSubmitBtn.disabled = true;
    elements.editSubmitBtn.textContent = "Saving...";

    try {
      await API.updateIssue(id, payload);
      showToast(`Issue #${id} updated successfully!`, "success");
      closeModal(elements.editModal);
      await loadData();
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      elements.editSubmitBtn.disabled = false;
      elements.editSubmitBtn.textContent = "Save Changes";
    }
  });

  // Confirm Delete
  elements.confirmDeleteBtn.addEventListener("click", async () => {
    if (!state.pendingDeleteId) return;
    const id = state.pendingDeleteId;

    elements.confirmDeleteBtn.disabled = true;
    elements.confirmDeleteBtn.textContent = "Deleting...";

    try {
      await API.deleteIssue(id);
      showToast(`Issue #${id} was deleted successfully.`, "info");
      closeModal(elements.deleteModal);
      state.pendingDeleteId = null;
      await loadData();
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      elements.confirmDeleteBtn.disabled = false;
      elements.confirmDeleteBtn.textContent = "Yes, Delete";
    }
  });

  // =========================================================================
  // INITIALIZATION
  // =========================================================================

  document.addEventListener("DOMContentLoaded", () => {
    updateHealthBadge();
    loadData();

    // Check health periodically every 30 seconds
    setInterval(updateHealthBadge, 30000);
  });

})();

