// static/api.js
export async function getFaults() {
    const res = await fetch("/api/faults");
    return res.json();
}

export async function addFault(title, location, severity) {
    const res = await fetch("/api/faults", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, location, severity })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(JSON.stringify(data));
    return data;
}