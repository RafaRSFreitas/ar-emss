// static/ui.js
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
                Severity: ${f.severity} · 
                Status: ${f.status}
            </span>
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