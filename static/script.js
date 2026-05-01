function loadDashboard() {
    fetch('/dashboard_data')
        .then(res => res.json())
        .then(data => {
            document.getElementById("users").innerText = data.total_users;
            document.getElementById("sessions").innerText = data.active_sessions;
            document.getElementById("threats").innerText = data.threat_count;
        });
}


// 👥 TOTAL USERS
function loadUsers() {
    fetch('/get_users')
        .then(res => res.json())
        .then(data => {

            let table = document.querySelector("#resultTable tbody");
            table.innerHTML = "";

            data.forEach(user => {
                let row = `<tr>
                    <td>${user.username}</td>
                    <td>-</td>
                    <td>-</td>
                    <td>-</td>
                </tr>`;
                table.innerHTML += row;
            });
        });
}


// 🚨 THREATS ONLY
function loadThreats() {
    fetch('/detect')
        .then(res => res.json())
        .then(data => {

            let table = document.querySelector("#resultTable tbody");
            table.innerHTML = "";

            data.forEach(item => {

                let color = "black";

                if (item.action.includes("Upload") || item.action.includes("Access")) {
                    color = "red";
                }

                let row = `<tr style="color:${color};">
                    <td>${item.user}</td>
                    <td>${item.action}</td>
                    <td>${item.date}</td>
                    <td>${item.time}</td>
                </tr>`;

                table.innerHTML += row;
            });
        });
}


// 🔍 SCAN SYSTEM (same as threats)
function detectThreats() {
    loadThreats();
}


// Load dashboard on start
window.onload = loadDashboard;