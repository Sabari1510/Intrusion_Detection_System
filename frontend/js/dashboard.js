// =========================================
// Network Intrusion Detection System
// Dashboard JavaScript
// =========================================

// ----------------------------
// Dashboard Statistics
// ----------------------------

const totalPackets = 504473;
const normalTraffic = 419297;
const attackTraffic = 85176;
const accuracy = 99.68;

// Update Statistics Cards

document.getElementById("totalPackets").innerText = totalPackets.toLocaleString();
document.getElementById("normalTraffic").innerText = normalTraffic.toLocaleString();
document.getElementById("attackTraffic").innerText = attackTraffic.toLocaleString();

// ----------------------------
// Pie Chart
// ----------------------------

const pieCtx = document.getElementById("pieChart").getContext("2d");

new Chart(pieCtx, {

    type: "pie",

    data: {

        labels: [

            "Normal Traffic",

            "Attack Traffic"

        ],

        datasets: [{

            data: [

                normalTraffic,

                attackTraffic

            ],

            backgroundColor: [

                "#2ECC71",

                "#E74C3C"

            ],

            borderColor: "#ffffff",

            borderWidth: 2

        }]

    },

    options: {

        responsive: true,

        plugins: {

            legend: {

                position: "bottom",

                labels: {

                    color: "white",

                    font: {

                        size: 14

                    }

                }

            }

        }

    }

});

// ----------------------------
// Bar Chart
// ----------------------------

const barCtx = document.getElementById("barChart").getContext("2d");

new Chart(barCtx, {

    type: "bar",

    data: {

        labels: [

            "DDoS",

            "DoS Hulk",

            "PortScan",

            "FTP",

            "Bot"

        ],

        datasets: [{

            label: "Detected Attacks",

            data: [

                25603,

                34570,

                18164,

                1187,

                391

            ],

            backgroundColor: [

                "#3498DB",

                "#9B59B6",

                "#F39C12",

                "#1ABC9C",

                "#E67E22"

            ]

        }]

    },

    options: {

        responsive: true,

        scales: {

            y: {

                beginAtZero: true,

                ticks: {

                    color: "white"

                },

                grid: {

                    color: "#555"

                }

            },

            x: {

                ticks: {

                    color: "white"

                },

                grid: {

                    color: "#555"

                }

            }

        },

        plugins: {

            legend: {

                display: false

            }

        }

    }

});

// ----------------------------
// Simulated Live Prediction Table
// ----------------------------

const attackTypes = [

    "BENIGN",

    "DDoS",

    "DoS Hulk",

    "PortScan",

    "Bot",

    "FTP-Patator",

    "SSH-Patator"

];

function randomPrediction() {

    return attackTypes[Math.floor(Math.random() * attackTypes.length)];

}

// Update recent predictions every 5 seconds

setInterval(() => {

    const table = document.querySelector("tbody");

    const row = document.createElement("tr");

    const packetId = Math.floor(Math.random() * 9000 + 1000);

    const prediction = randomPrediction();

    const confidence = (95 + Math.random() * 5).toFixed(2);

    row.innerHTML = `

        <td>${packetId}</td>

        <td>${prediction}</td>

        <td>${confidence}%</td>

    `;

    table.prepend(row);

    // Keep only latest 5 rows

    while (table.rows.length > 5) {

        table.deleteRow(5);

    }

}, 5000);

// ----------------------------
// Welcome Message
// ----------------------------

console.log("=======================================");
console.log(" Network Intrusion Detection Dashboard ");
console.log(" Dashboard Loaded Successfully ");
console.log("=======================================");