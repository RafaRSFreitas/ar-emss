import { getFaults, addFault, updateFaultStatus, deleteFault } from "./api.js";
import { renderFaults } from "./ui.js";

// --- DOM elements -------------------------------------------------
const loginOverlay = document.getElementById("loginOverlay");
const dashboard    = document.getElementById("dashboard");
const usernameEl   = document.getElementById("username");
const passwordEl   = document.getElementById("password");
const loginBtn     = document.getElementById("loginBtn");
const loginMsg     = document.getElementById("loginMsg");

const listEl       = document.getElementById("list");
const msgEl        = document.getElementById("msg");
const titleEl      = document.getElementById("title");
const locationEl   = document.getElementById("location");
const severityEl   = document.getElementById("severity");
const addBtn       = document.getElementById("addBtn");
const logoutBtn    = document.getElementById("logoutBtn");

const totalFaultsEl        = document.getElementById("totalFaults");
const openFaultsEl         = document.getElementById("openFaults");
const closedFaultsEl       = document.getElementById("closedFaults");
const highSeverityFaultsEl = document.getElementById("highSeverityFaults");

const loadingSpinner = document.getElementById("loadingSpinner");

// --- Metrics helper -----------------------------------------------
function updateMetrics(faults) {
  totalFaultsEl.textContent = faults.length;
  openFaultsEl.textContent = faults.filter(f => f.status === "open").length;
  closedFaultsEl.textContent = faults.filter(f => f.status === "closed").length;
  highSeverityFaultsEl.textContent = faults.filter(f => f.severity === 3).length;
}

// --- Refresh faults (only when authenticated) ---------------------
async function refresh() {
  loadingSpinner.style.display = "block";
  try {
    const faults = await getFaults();
    renderFaults(listEl, faults);
    updateMetrics(faults);
  } catch (err) {
    if (err.message.includes("401") || err.message.includes("403")) {
      forceLogin();
    } else {
      msgEl.textContent = "Error: " + err.message;
    }
  } finally {
    loadingSpinner.style.display = "none";
  }
}

// --- Status & Delete button handler ---------------------------------
listEl.addEventListener("click", async (e) => {
  const statusBtn = e.target.closest(".statusBtn");
  const delBtn = e.target.closest(".deleteBtn");

  if (statusBtn) {
    const faultId = parseInt(statusBtn.dataset.id, 10);
    const nextStatus = statusBtn.dataset.next;

    try {
      msgEl.textContent = "";
      statusBtn.disabled = true;

      await updateFaultStatus(faultId, nextStatus);
      await refresh();
    } catch (err) {
      msgEl.textContent = "Error: " + err.message;
      if (err.message === "Login required") {
        forceLogin();
      }
    } finally {
      statusBtn.disabled = false;
    }
  }

  if (delBtn) {
    const faultId = parseInt(delBtn.dataset.id, 10);

    if (!confirm("Are you sure you want to delete this fault?")) return;

    try {
      msgEl.textContent = "";
      setFaultCardError(faultId, "");
      delBtn.disabled = true;

      await deleteFault(faultId);
      await refresh();
    } catch (err) {
      setFaultCardError(faultId, err.message);
      if (err.message === "Login required") {
        forceLogin();
      }
    } finally {
      delBtn.disabled = false;
    }
  }
});

// --- Authentication gatekeeper ------------------------------------
function parseJwt(token) {
  if (!token) return null;
  try {
    const payload = token.split('.')[1];
    if (!payload) return null;
    const base64 = payload.replace(/-/g, '+').replace(/_/g, '/');
    const decoded = atob(base64.padEnd(base64.length + (4 - (base64.length % 4)) % 4, '='));
    return JSON.parse(decoded);
  } catch (err) {
    console.error('parseJwt error:', err);
    return null;
  }
}

function isSupervisor() {
  const token = localStorage.getItem('token');
  const payload = parseJwt(token);
  const role = String(payload?.role || '').toLowerCase();
  return role === 'admin' || role === 'supervisor';
}

function updateNavLinks() {
  const dashboardLink = document.getElementById('dashboardLink');
  if (!dashboardLink) return;
  const isAdmin = isSupervisor();
  dashboardLink.style.display = isAdmin ? 'inline' : 'none';
  console.log('updateNavLinks payload:', parseJwt(localStorage.getItem('token')), 'showDashboard:', isAdmin);
}

function setFaultCardError(faultId, message) {
  const errorEl = document.getElementById(`faultError-${faultId}`);
  if (!errorEl) return;
  if (message) {
    errorEl.textContent = message;
    errorEl.style.display = "block";
  } else {
    errorEl.textContent = "";
    errorEl.style.display = "none";
  }
}

function showLogin() {
  loginOverlay.style.display = "flex";
  dashboard.style.display = "none";
  localStorage.removeItem("token");
}

function showApp() {
  loginOverlay.style.display = "none";
  dashboard.style.display = "block";
  updateNavLinks();
}

async function checkAuth() {
  const token = localStorage.getItem("token");
  if (!token) {
    showLogin();
    return;
  }
  try {
    await getFaults();
    showApp();
    loadingSpinner.style.display = "block";   // show spinner while first data loads
    await refresh();                          // refresh() will hide it when done
  } catch (err) {
    showLogin();
  }
}

function forceLogin() {
  showLogin();
}

// --- Login and logout buttons -------------------------------------------------
logoutBtn.addEventListener("click", () => {
    localStorage.removeItem("token");
    showLogin();
});

document.getElementById("loginForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  loginMsg.textContent = "";                                                
  try {
    const username = usernameEl.value.trim();
    const password = passwordEl.value.trim();

    const res = await fetch("/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Login failed");

    localStorage.setItem("token", data.access_token);
    showApp();
    await refresh();
  } catch (err) {
    loginMsg.textContent = "Error: " + err.message;
  }
});

// --- Report fault -------------------------------------------------
addBtn.addEventListener("click", async () => {
  msgEl.textContent = "";
  try {
    const title = titleEl.value.trim();
    const location = locationEl.value.trim();
    const severity = parseInt(severityEl.value);
    const created = await addFault(title, location, severity);
    msgEl.textContent = "Created: " + JSON.stringify(created, null, 2);
    titleEl.value = "";
    locationEl.value = "";
    severityEl.value = "1";
    await refresh();
  } catch (err) {
    msgEl.textContent = "Error: " + err.message;
  }
});

// --- Initialisation -----------------------------------------------
checkAuth();

