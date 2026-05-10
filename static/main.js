// static/main.js
import { getFaults, addFault } from "./api.js";
import { renderFaults } from "./ui.js";

const listEl = document.getElementById("list");
const msgEl = document.getElementById("msg");
const titleEl = document.getElementById("title");
const locationEl = document.getElementById("location");
const severityEl = document.getElementById("severity");
const addBtn = document.getElementById("addBtn");
const usernameEl = document.getElementById("username");
const passwordEl = document.getElementById("password");
const loginBtn = document.getElementById("loginBtn");
const loginMsg = document.getElementById("loginMsg");
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

loginBtn.addEventListener("click", async () => {
    loginMsg.textContent = "";

    try {
        const username = usernameEl.value.trim();
        const password = passwordEl.value.trim();

        const res = await fetch("/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username,
                password
            })
        });

        const data = await res.json();

        if (!res.ok) {
            throw new Error(data.detail || "Login failed");
        }

        localStorage.setItem("token", data.access_token);

        loginMsg.textContent = "Login successful";
    } catch (err) {
        loginMsg.textContent = "Error: " + err.message;
    }
});

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