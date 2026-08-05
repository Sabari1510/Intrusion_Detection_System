const API_BASE_URL = "http://127.0.0.1:8000";

// Detailed descriptions for attack types
const ATTACK_DESCRIPTIONS = {
    "BENIGN": {
        title: "Benign Network Traffic",
        desc: "Normal user activity and standard network operational traffic. No malicious patterns or anomalies detected. System is secure."
    },
    "DDoS": {
        title: "Distributed Denial of Service (DDoS)",
        desc: "A distributed resource exhaustion attack aiming to make the service unavailable by flooding the network with massive, coordinated volumes of packets from multiple compromised sources."
    },
    "PortScan": {
        title: "Port Scanning Activity",
        desc: "A reconnaissance attack attempting to probe host system ports to map active services, open doors, and identify potentially vulnerable targets for exploitation."
    },
    "Bot": {
        title: "Botnet Infection",
        desc: "Malicious activity indicates that this system is communicating with a Command & Control (C2) server, acting as part of an infected botnet fleet to execute remote directives."
    },
    "FTP-Patator": {
        title: "FTP Brute Force (Patator)",
        desc: "An automated password guessing attack targeting the File Transfer Protocol (FTP) service to gain unauthorized administrative access."
    },
    "SSH-Patator": {
        title: "SSH Brute Force (Patator)",
        desc: "A dictionary or brute-force credential-guessing attack targeting the Secure Shell (SSH) port to hijack remote terminal console access."
    },
    "DoS Hulk": {
        title: "DoS Hulk Web Flooder",
        desc: "A high-volume Denial of Service attack targeting web applications, utilizing dynamic request headers to bypass caching and exhaust web server worker threads."
    },
    "DoS GoldenEye": {
        title: "DoS GoldenEye Layer 7 Flooder",
        desc: "An application-layer DoS attack that keeps HTTP keep-alive connections open and issues highly concurrent requests to exhaust target server resources."
    },
    "DoS slowloris": {
        title: "DoS Slowloris Connection Exhaustion",
        desc: "A stealthy DoS attack that keeps multiple connections to the target web server open indefinitely by sending partial HTTP requests, starving legitimate users."
    },
    "DoS Slowhttptest": {
        title: "DoS Slow HTTP Test",
        desc: "Similar to Slowloris, this exploits thread limits by sending slow HTTP headers or POST bodies, forcing the web server to keep sockets open."
    },
    "Infiltration": {
        title: "Network Infiltration Threat",
        desc: "A highly critical event indicating a remote intruder has compromised an internal asset (typically via software vulnerability or social engineering) and is executing lateral movement."
    },
    "Web Attack - Brute Force": {
        title: "Web Password Brute Force",
        desc: "An attack seeking unauthorized web application portal entry by testing hundreds of username/password combinations automatically against login forms."
    },
    "Web Attack - XSS": {
        title: "Cross-Site Scripting (XSS)",
        desc: "A code injection attack where malicious scripts are injected into trusted web applications, targeting end-user browsers to steal cookies or session tokens."
    },
    "Web Attack - SQL Injection": {
        title: "SQL Database Injection",
        desc: "A critical web database attack injecting malicious SQL queries into user input fields to read, manipulate, or destroy backend databases."
    },
    "Heartbleed": {
        title: "Heartbleed Vulnerability Exploit",
        desc: "An exploit targeting a critical flaw in OpenSSL's heartbeat extension, allowing attackers to dump active server memory packets containing sensitive keys or user data."
    }
};

// Fallback local presets if API is offline
const LOCAL_PRESETS = {
    "BENIGN": {
        "Fwd IAT Std": 0.0, "Bwd IAT Min": 0.0, "Flow IAT Min": 4.0, "Bwd Packet Length Std": 0.0,
        "Bwd Packet Length Mean": 0.0, "Avg Bwd Segment Size": 0.0, "Idle Min": 0.0, "Bwd Packet Length Max": 0.0,
        "Idle Mean": 0.0, "Packet Length Std": 0.0, "Idle Max": 0.0, "Flow IAT Max": 4.0, "Max Packet Length": 6.0,
        "Fwd IAT Max": 0.0, "Packet Length Variance": 0.0, "Average Packet Size": 9.0, "Packet Length Mean": 6.0,
        "Active Min": 0.0, "FIN Flag Count": 0, "Active Std": 0.0, "Flow IAT Std": 0.0, "PSH Flag Count": 0,
        "Active Mean": 0.0, "Fwd IAT Total": 0.0, "ACK Flag Count": 1, "Flow Duration": 4.0, "Bwd IAT Std": 0.0,
        "Subflow Fwd Bytes": 6.0, "Flow IAT Mean": 4.0, "Min Packet Length": 6.0
    },
    "DDoS": {
        "Fwd IAT Std": 38.67, "Bwd IAT Min": 2.0, "Flow IAT Min": 1.0, "Bwd Packet Length Std": 128.5,
        "Bwd Packet Length Mean": 110.0, "Avg Bwd Segment Size": 110.0, "Idle Min": 0.0, "Bwd Packet Length Max": 350.0,
        "Idle Mean": 0.0, "Packet Length Std": 182.2, "Idle Max": 0.0, "Flow IAT Max": 2400.0, "Max Packet Length": 350.0,
        "Fwd IAT Max": 2300.0, "Packet Length Variance": 33200.0, "Average Packet Size": 95.0, "Packet Length Mean": 85.0,
        "Active Min": 0.0, "FIN Flag Count": 0, "Active Std": 0.0, "Flow IAT Std": 312.4, "PSH Flag Count": 1,
        "Active Mean": 0.0, "Fwd IAT Total": 4800.0, "ACK Flag Count": 0, "Flow Duration": 4900.0, "Bwd IAT Std": 14.5,
        "Subflow Fwd Bytes": 120.0, "Flow IAT Mean": 160.0, "Min Packet Length": 0.0
    },
    "PortScan": {
        "Fwd IAT Std": 0.0, "Bwd IAT Min": 0.0, "Flow IAT Min": 1.0, "Bwd Packet Length Std": 0.0,
        "Bwd Packet Length Mean": 0.0, "Avg Bwd Segment Size": 0.0, "Idle Min": 0.0, "Bwd Packet Length Max": 0.0,
        "Idle Mean": 0.0, "Packet Length Std": 0.0, "Idle Max": 0.0, "Flow IAT Max": 1.0, "Max Packet Length": 0.0,
        "Fwd IAT Max": 0.0, "Packet Length Variance": 0.0, "Average Packet Size": 0.0, "Packet Length Mean": 0.0,
        "Active Min": 0.0, "FIN Flag Count": 0, "Active Std": 0.0, "Flow IAT Std": 0.0, "PSH Flag Count": 0,
        "Active Mean": 0.0, "Fwd IAT Total": 0.0, "ACK Flag Count": 1, "Flow Duration": 1.0, "Bwd IAT Std": 0.0,
        "Subflow Fwd Bytes": 0.0, "Flow IAT Mean": 1.0, "Min Packet Length": 0.0
    },
    "Botnet": {
        "Fwd IAT Std": 124312.0, "Bwd IAT Min": 23.0, "Flow IAT Min": 2.0, "Bwd Packet Length Std": 456.2,
        "Bwd Packet Length Mean": 320.0, "Avg Bwd Segment Size": 320.0, "Idle Min": 4500000.0, "Bwd Packet Length Max": 1024.0,
        "Idle Mean": 5000000.0, "Packet Length Std": 395.0, "Idle Max": 5500000.0, "Flow IAT Max": 500000.0, "Max Packet Length": 1024.0,
        "Fwd IAT Max": 480000.0, "Packet Length Variance": 156000.0, "Average Packet Size": 210.0, "Packet Length Mean": 180.0,
        "Active Min": 23000.0, "FIN Flag Count": 0, "Active Std": 0.0, "Flow IAT Std": 94300.0, "PSH Flag Count": 1,
        "Active Mean": 23000.0, "Fwd IAT Total": 2400000.0, "ACK Flag Count": 0, "Flow Duration": 12000000.0, "Bwd IAT Std": 12040.0,
        "Subflow Fwd Bytes": 500.0, "Flow IAT Mean": 43500.0, "Min Packet Length": 0.0
    }
};

document.addEventListener("DOMContentLoaded", () => {
    const apiStatusBadge = document.getElementById("apiStatusBadge");
    const flowForm = document.getElementById("flowForm");
    const submitBtn = document.getElementById("submitBtn");
    const resultsPanel = document.getElementById("resultsPanel");
    const resultPlaceholder = document.getElementById("resultPlaceholder");
    const resultContent = document.getElementById("resultContent");
    const threatBadge = document.getElementById("threatBadge");
    const confidenceVal = document.getElementById("confidenceVal");
    const confidenceBar = document.getElementById("confidenceBar");
    const attackDescTitle = document.getElementById("attackDescTitle");
    const attackDescBody = document.getElementById("attackDescBody");
    const probabilityList = document.getElementById("probabilityList");

    // 1. Check API Connection
    checkApiConnection();

    // 2. Setup Accordion Toggle Logic
    setupAccordions();

    // 3. Setup Preset Loader buttons
    setupPresets();

    // 4. Setup Form submission
    flowForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        // Change submit btn state
        submitBtn.disabled = true;
        const spinner = submitBtn.querySelector(".loading-icon");
        const btnText = submitBtn.querySelector("span");
        spinner.style.display = "inline-block";
        btnText.innerHTML = " Analyzing Traffic...";

        // Collect form data matching dataset names exactly
        const data = {};
        const inputs = flowForm.querySelectorAll("input");
        inputs.forEach(input => {
            const val = parseFloat(input.value);
            data[input.name] = isNaN(val) ? 0 : val;
        });

        try {
            const response = await fetch(`${API_BASE_URL}/predict`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                throw new Error(`Prediction API returned status: ${response.status}`);
            }

            const result = await response.json();
            displayResult(result);
            
            // Scroll result panel into view on mobile
            if (window.innerWidth <= 1024) {
                resultsPanel.scrollIntoView({ behavior: 'smooth' });
            }

        } catch (error) {
            console.error("Prediction Error:", error);
            showError(error.message);
        } finally {
            submitBtn.disabled = false;
            spinner.style.display = "none";
            btnText.innerHTML = '<i class="fa-solid fa-magnifying-glass"></i> Predict Traffic Threat';
        }
    });

    // --- Helper Functions ---

    async function checkApiConnection() {
        try {
            const response = await fetch(API_BASE_URL);
            if (response.ok) {
                const statusDot = apiStatusBadge.querySelector(".status-dot");
                const statusLabel = apiStatusBadge.querySelector(".status-label");
                statusDot.className = "status-dot online";
                statusLabel.innerText = "API Server Connected";
            }
        } catch (error) {
            console.warn("API Connection failed. Using local fallback presets.");
            const statusDot = apiStatusBadge.querySelector(".status-dot");
            const statusLabel = apiStatusBadge.querySelector(".status-label");
            statusDot.className = "status-dot offline";
            statusLabel.innerText = "API Offline - Local Presets Active";
        }
    }

    function setupAccordions() {
        const headers = document.querySelectorAll(".accordion-header");
        headers.forEach(header => {
            header.addEventListener("click", () => {
                const item = header.parentElement;
                item.classList.toggle("expanded");
            });
        });
    }

    function setupPresets() {
        const presetBtns = document.querySelectorAll(".preset-btn");
        presetBtns.forEach(btn => {
            btn.addEventListener("click", async () => {
                const presetKey = btn.getAttribute("data-preset");
                let presetData = null;

                // Attempt to fetch from API
                try {
                    const response = await fetch(`${API_BASE_URL}/presets`);
                    if (response.ok) {
                        const presets = await response.json();
                        presetData = presets[presetKey];
                    }
                } catch (e) {
                    console.log("Failed to fetch presets from API, loading local constants.");
                }

                // Fallback to local presets if API load failed
                if (!presetData) {
                    presetData = LOCAL_PRESETS[presetKey];
                }

                if (presetData) {
                    populateForm(presetData);
                    // Add active state to button
                    presetBtns.forEach(b => b.classList.remove("active"));
                    btn.classList.add("active");
                }
            });
        });
    }

    function populateForm(data) {
        Object.entries(data).forEach(([fieldName, value]) => {
            const input = flowForm.querySelector(`[name="${fieldName}"]`);
            if (input) {
                input.value = value;
                // Add flash animation
                input.style.borderColor = "var(--color-primary)";
                setTimeout(() => {
                    input.style.borderColor = "";
                }, 800);
            }
        });
    }

    function displayResult(result) {
        // Remove old severity classes from results panel
        resultsPanel.className = `panel glass-panel results-panel ${result.severity}`;
        
        // Hide placeholder, show content
        resultPlaceholder.style.display = "none";
        resultContent.style.display = "block";
        
        // Set Badge and Confidence
        threatBadge.innerText = result.prediction;
        const confidencePct = (result.confidence * 100).toFixed(2);
        confidenceVal.innerText = `${confidencePct}%`;
        confidenceBar.style.width = `${confidencePct}%`;

        // Load Description
        const descData = ATTACK_DESCRIPTIONS[result.prediction] || {
            title: "Unknown Intrusion Type",
            desc: "The ensemble has classified the flow as an attack pattern, but no description details are available for this signature class."
        };
        attackDescTitle.innerText = descData.title;
        attackDescBody.innerText = descData.desc;

        // Render Probabilities
        probabilityList.innerHTML = "";
        
        // Sort probabilities descending
        const sortedProbs = Object.entries(result.probabilities)
            .sort((a, b) => b[1] - a[1]);
            
        sortedProbs.forEach(([className, probability]) => {
            const pct = (probability * 100).toFixed(2);
            if (probability < 0.0001) return; // Skip zero values for readability

            const row = document.createElement("div");
            row.className = `probability-row ${className === result.prediction ? 'high-prob' : ''}`;
            
            row.innerHTML = `
                <div class="prob-meta">
                    <span class="prob-name">${className}</span>
                    <span class="prob-val">${pct}%</span>
                </div>
                <div class="prob-row-bar-wrapper">
                    <div class="prob-row-bar-fill" style="width: ${pct}%"></div>
                </div>
            `;
            probabilityList.appendChild(row);
        });
    }

    function showError(message) {
        resultsPanel.className = `panel glass-panel results-panel danger`;
        resultPlaceholder.style.display = "none";
        resultContent.style.display = "block";
        
        threatBadge.innerText = "ERROR";
        confidenceVal.innerText = "N/A";
        confidenceBar.style.width = "0%";
        
        attackDescTitle.innerText = "Analysis Failed";
        attackDescBody.innerText = `The API returned an error: ${message}. Make sure the FastAPI backend is running via uvicorn (e.g. uvicorn api.main:app) and that models are trained.`;
        probabilityList.innerHTML = "";
    }
});
