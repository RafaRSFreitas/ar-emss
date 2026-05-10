// static/api.js

function getAuthHeaders() {
  const token = localStorage.getItem("token");

  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`
  };
}

export async function getFaults() {
  const res = await fetch("/api/faults", {
    headers: getAuthHeaders()
  });

  const data = await res.json();

  if (!res.ok) throw new Error(JSON.stringify(data));

  return data;
}

export async function addFault(title, location, severity) {
  const res = await fetch("/api/faults", {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({ title, location, severity })
  });

  const data = await res.json();

  if (!res.ok) throw new Error(JSON.stringify(data));

  return data;
}

export async function updateFault(fault_id, status) {
  const res = await fetch(`/api/faults/${fault_id}`, {
    method: "PATCH",
    headers: getAuthHeaders(),
    body: JSON.stringify({ status })
  });

  const data = await res.json();

  if (!res.ok) throw new Error(JSON.stringify(data));

  return data;
}