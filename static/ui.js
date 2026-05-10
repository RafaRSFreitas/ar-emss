export function renderFaults(container, faults) {
    if (!faults.length) {
        container.innerHTML = "<p class='muted'>No faults reported yet.</p>";
        return;
    }

    container.innerHTML = faults.map(f => `
        <div class="card">
            <strong>#${f.id} – ${escapeHtml(f.title)}</strong><br/>
            <span class="muted">
                Location: ${escapeHtml(f.location)} · 
                Severity: ${f.severity === 1 ? "Low" : f.severity === 2 ? "Medium" : "High"} · 
                Status: ${f.status === "closed" ? "resolved" : f.status}
            </span>

            <div style="margin-top:10px; display:flex; gap:8px; flex-wrap:wrap;">
                ${
                    f.status === "open"
                    ? `<button class="statusBtn" data-id="${f.id}" data-next="closed">Resolve</button>`
                    : `<button class="statusBtn" data-id="${f.id}" data-next="open">Reopen</button>`
                }
                <button class="deleteBtn" data-id="${f.id}" style="background:#ffe6e6; color:#cc3333; border:1px solid #cc3333;">Delete</button>
            </div>
        </div>
    `).join("");
}

function escapeHtml(str) {
    return String(str)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}