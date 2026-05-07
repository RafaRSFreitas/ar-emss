// static/main.js
import { getFaults, addFault } from "./api.js";
import { renderFaults } from "./ui.js";

const listEl = document.getElementById("list");
const msgEl = document.getElementById("msg");
const titleEl = document.getElementById("title");
const locationEl = document.getElementById("location");
const severityEl = document.getElementById("severity");
const addBtn = document.getElementById("addBtn");
const totalFaultsEl = document.getElementById("totalFaults");
const openFaultsEl = document.getElementById("openFaults");
const closedFaultsEl = document.getElementById("closedFaults");
const highSeverityFaultsEl = document.getElementById("highSeverityFaults");

function updateMetrics(faults) {
    totalFaultsEl.textContent = faults.length;
    openFaultsEl.textContent = faults.filter(fault => fault.status === "open").length;
    closedFaultsEl.textContent = faults.filter(fault => fault.status === "closed").length;
    highSeverityFaultsEl.textContent = faults.filter(fault => fault.severity === 3).length;
}

async function refresh() {
    const faults = await getFaults();
    renderFaults(listEl, faults);
    updateMetrics(faults);
}

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

// Initial load
refresh();