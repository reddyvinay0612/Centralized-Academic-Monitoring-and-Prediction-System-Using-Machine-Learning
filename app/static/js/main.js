/**
 * CAMPS-ML Client-Side Interactivity & Async Handlers
 */

document.addEventListener("DOMContentLoaded", function () {
    // 1. Fetch unread notification count
    fetchUnreadNotifications();

    // Poll every 30 seconds
    setInterval(fetchUnreadNotifications, 30000);
});

function fetchUnreadNotifications() {
    const badge = document.getElementById("notification-badge");
    const container = document.getElementById("notification-list-container");

    if (!badge || !container) return;

    fetch("/api/notifications/unread")
        .then(res => res.json())
        .then(data => {
            if (data.count > 0) {
                badge.textContent = data.count;
                badge.classList.remove("d-none");
            } else {
                badge.classList.add("d-none");
            }

            if (data.alerts && data.alerts.length > 0) {
                container.innerHTML = data.alerts.map(a => `
                    <div class="notification-item d-flex justify-content-between align-items-start">
                        <div>
                            <span class="badge bg-${a.severity === 'critical' ? 'danger' : 'warning'} text-uppercase" style="font-size: 0.65rem;">${a.severity}</span>
                            <div class="fw-bold mt-1">${a.title}</div>
                            <div class="text-muted small">${a.message}</div>
                            <div class="text-muted" style="font-size: 0.7rem;">${a.created_at}</div>
                        </div>
                        <button class="btn btn-sm btn-link text-muted p-0 ms-2" onclick="markRead(${a.id})">&times;</button>
                    </div>
                `).join("");
            } else {
                container.innerHTML = '<div class="text-center text-muted py-3 small">No unread notifications</div>';
            }
        })
        .catch(err => console.log("Notification fetch error:", err));
}

function markRead(alertId) {
    fetch(`/api/notifications/${alertId}/read`, { method: "POST" })
        .then(res => res.json())
        .then(() => fetchUnreadNotifications());
}
