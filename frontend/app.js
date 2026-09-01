const API = "/api";
let alerts = [];
let selectedAlertId = null;
let currentFilter = "all";
let ws = null;

async function fetchJSON(path) {
  const res = await fetch(`${API}${path}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

async function loadStore() {
  const store = await fetchJSON("/store");
  document.getElementById("store-phone").textContent = store.phone;
  document.title = `${store.name} — Loss Prevention`;
}

async function loadStats() {
  const stats = await fetchJSON("/stats");
  document.getElementById("stat-critical").textContent = stats.critical_alerts;
  document.getElementById("stat-open").textContent = stats.open_alerts;
  document.getElementById("stat-customer").textContent = stats.customer_alerts_today;
  document.getElementById("stat-employee").textContent = stats.employee_alerts_today;
  document.getElementById("stat-zones").textContent = stats.zones_monitored;
  document.getElementById("stat-cameras").textContent = stats.cameras_online;
}

async function loadZones() {
  const zones = await fetchJSON("/zones");
  const list = document.getElementById("zone-list");
  list.innerHTML = zones
    .map(
      (z) => `
    <li class="zone-item">
      <span>${z.name}</span>
      <span class="risk-${z.risk_level}">${z.risk_level} · ${z.cameras.length} cam</span>
    </li>`
    )
    .join("");
}

async function loadAlerts() {
  alerts = await fetchJSON("/alerts?limit=50");
  renderAlerts();
}

function renderAlerts() {
  const list = document.getElementById("alert-list");
  const filtered =
    currentFilter === "all"
      ? alerts
      : alerts.filter((a) => a.side === currentFilter);

  if (!filtered.length) {
    list.innerHTML = '<li class="empty-state">No alerts yet. Run the demo simulator to generate sample incidents.</li>';
    return;
  }

  list.innerHTML = filtered
    .map(
      (a) => `
    <li class="alert-item tier-${a.tier} ${a.id === selectedAlertId ? "selected" : ""}" data-id="${a.id}">
      <div class="alert-item-header">
        <span class="alert-title">${a.title}</span>
        <span class="side-tag side-${a.side}">${a.side}</span>
      </div>
      <div class="alert-meta">${a.zone_name} · ${a.tier} · ${formatTime(a.created_at)}</div>
    </li>`
    )
    .join("");

  list.querySelectorAll(".alert-item").forEach((el) => {
    el.addEventListener("click", () => selectAlert(el.dataset.id));
  });
}

function selectAlert(id) {
  selectedAlertId = id;
  const alert = alerts.find((a) => a.id === id);
  if (!alert) return;

  renderAlerts();

  const detail = document.getElementById("alert-detail");
  detail.classList.remove("empty");
  detail.innerHTML = `
    <div class="detail-row"><div class="label">Title</div><div class="value">${alert.title}</div></div>
    <div class="detail-row"><div class="label">Description</div><div class="value">${alert.description}</div></div>
    <div class="detail-row"><div class="label">Zone</div><div class="value">${alert.zone_name}</div></div>
    <div class="detail-row"><div class="label">Tier / Side</div><div class="value">${alert.tier} · ${alert.side}</div></div>
    <div class="detail-row"><div class="label">Status</div><div class="value">${alert.status}</div></div>
    ${alert.employee_id ? `<div class="detail-row"><div class="label">Employee ID</div><div class="value">${alert.employee_id}</div></div>` : ""}
    ${alert.pos_transaction_id ? `<div class="detail-row"><div class="label">POS Transaction</div><div class="value">${alert.pos_transaction_id}</div></div>` : ""}
    <div class="detail-actions">
      <button class="primary" onclick="updateStatus('${alert.id}', 'acknowledged')">Acknowledge</button>
      <button onclick="updateStatus('${alert.id}', 'resolved')">Resolve</button>
      <button onclick="updateStatus('${alert.id}', 'false_positive')">False Positive</button>
    </div>
  `;
}

async function updateStatus(id, status) {
  await fetch(`${API}/alerts/${id}/status?status=${status}`, { method: "PATCH" });
  await refresh();
  selectAlert(id);
}

function formatTime(iso) {
  return new Date(iso).toLocaleString("en-US", {
    timeZone: "America/Los_Angeles",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function connectWebSocket() {
  const proto = location.protocol === "https:" ? "wss" : "ws";
  ws = new WebSocket(`${proto}://${location.host}/api/ws/alerts`);
  const status = document.getElementById("connection-status");

  ws.onopen = () => {
    status.textContent = "Live";
    status.className = "badge badge-ok";
  };
  ws.onclose = () => {
    status.textContent = "Reconnecting";
    status.className = "badge badge-off";
    setTimeout(connectWebSocket, 3000);
  };
  ws.onmessage = async (evt) => {
    const msg = JSON.parse(evt.data);
    if (msg.type === "new_alert" || msg.type === "alert_updated") {
      await refresh();
      if (msg.type === "new_alert") selectAlert(msg.alert.id);
    }
  };
}

async function refresh() {
  await Promise.all([loadStats(), loadAlerts()]);
}

document.querySelectorAll(".filter-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".filter-btn").forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    currentFilter = btn.dataset.filter;
    renderAlerts();
  });
});

async function init() {
  try {
    await loadStore();
    await loadZones();
    await refresh();
    connectWebSocket();
  } catch (err) {
    console.error(err);
    document.getElementById("alert-list").innerHTML =
      '<li class="empty-state">Unable to connect to API. Start the server with: uvicorn backend.main:app --reload</li>';
  }
}

init();
