// --- DOM refs ---
const onServerBtn = document.getElementById("btn_server_on");
const offServerBtn = document.getElementById("btn_server_off");
const saveConfigBtn = document.getElementById("btn_save_config");
const status_lbl = document.getElementById("status_lbl");

// aimbot inputs
const scan_pattern = document.getElementById("scan_pattern");
const write_offset = document.getElementById("write_value_offset");
const head_offset = document.getElementById("head_offset");
const left_ear_offset = document.getElementById("left_ear_offset");
const right_ear_offset = document.getElementById("right_ear_offset");
const left_shoulder_offset = document.getElementById("left_shoulder_offset");
const right_shoulder_offset = document.getElementById("right_shoulder_offset");

// sniper controls + inputs
const patchSniperBtn = document.getElementById("patch-sniper");
const sniper_scan = document.getElementById("sniper_scan");
const sniper_replace = document.getElementById("sniper_replace");

// --- helpers ---
function safeSetStatus(text) {
    if (status_lbl) status_lbl.innerHTML = text;
}

function beep(duration = 200, frequency = 440, volume = 1) {
    try {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioCtx.createOscillator();
        const gainNode = audioCtx.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioCtx.destination);

        oscillator.type = 'sine';
        oscillator.frequency.value = frequency;
        gainNode.gain.value = volume;

        oscillator.start();
        setTimeout(() => oscillator.stop(), duration);
    } catch (e) {
        // ignore audio errors (autoplay policies etc)
        console.warn("beep error:", e);
    }
}

// --- tab control: request route AND load corresponding config ---
function tab_control(tab_name) {
    switch (tab_name) {
        case "tab_1":
            tab_request("/aimbot-config");
            loadAimbotConfig();
            break;
        case "tab_2":
            tab_request("/sniper-config");
            loadSniperConfig();
            break;
        case "tab_3":
            tab_request("/whitelist-service");
            break;
        case "tab_4":
            tab_request("/authentication-service");
            break;
        default:
            break;
    }
}

// simple GET tab request (fire-and-forget)
function tab_request(route) {
    fetch(route, { method: "GET" }).catch(err => console.warn("tab_request failed:", err));
}

// --- event listeners (only if element exists) ---
if (onServerBtn) {
    onServerBtn.addEventListener("click", () => {
        updateServerStatus('1');
        beep(200, 400);
    });
}
if (offServerBtn) {
    offServerBtn.addEventListener("click", () => {
        updateServerStatus('0');
        beep(200, 400);
    });
}
if (saveConfigBtn) {
    saveConfigBtn.addEventListener("click", () => {
        updateAimbotConfig(
            scan_pattern?.value || "",
            write_offset?.value || "",
            head_offset?.value || "",
            left_ear_offset?.value || "",
            right_ear_offset?.value || "",
            left_shoulder_offset?.value || "",
            right_shoulder_offset?.value || ""
        );
        beep(200, 300);
    });
}
if (patchSniperBtn) {
    patchSniperBtn.addEventListener("click", () => {
        updateSniperConfig(sniper_scan?.value || "", sniper_replace?.value || "");
        beep(200, 300);
    });
}

// --- loaders ---
async function loadAimbotConfig() {
    try {
        const response = await fetch(`/get-aimbot-config`, { method: "GET" });
        if (!response.ok) {
            safeSetStatus("status: Failed to load aimbot config");
            return;
        }
        const data = await response.json();
        const json_data = JSON.parse(data.response || "{}");

        if (scan_pattern) scan_pattern.value = json_data.scan_pattern ?? "";
        if (write_offset) write_offset.value = json_data.write_offset ?? "";
        if (head_offset) head_offset.value = json_data.head_offset ?? "";
        if (left_ear_offset) left_ear_offset.value = json_data.left_ear_offset ?? "";
        if (right_ear_offset) right_ear_offset.value = json_data.right_ear_offset ?? "";
        if (left_shoulder_offset) left_shoulder_offset.value = json_data.left_shoulder_offset ?? "";
        if (right_shoulder_offset) right_shoulder_offset.value = json_data.right_shoulder_offset ?? "";

        safeSetStatus("status: Aimbot values loaded");
    } catch (err) {
        console.error(err);
        safeSetStatus("status: Error loading aimbot config");
    }
}

async function loadSniperConfig() {
    try {
        const response = await fetch(`/get-sniper-config`, { method: "GET" });
        if (!response.ok) {
            safeSetStatus("status: Failed to load sniper config");
            return;
        }

        const data = await response.json();
        const json_data = JSON.parse(data.response || "{}");

        if (sniper_scan) sniper_scan.value = json_data.scan_pattern ?? "";
        if (sniper_replace) sniper_replace.value = json_data.replace_pattern ?? "";

        console.log(json_data)
        safeSetStatus("status: Sniper values loaded");
    } catch (err) {
        console.error(err);
        safeSetStatus("status: Error loading sniper config");
    }
}

// --- updaters ---
async function updateServerStatus(status) {
    try {
        const response = await fetch(`/update-server-status?server_status=${encodeURIComponent(status)}`, { method: "GET" });
        const data = await response.json();
        safeSetStatus("status: " + (data.response ?? data.error ?? "Unknown"));
    } catch (err) {
        console.error(err);
        safeSetStatus("status: Failed to update server status");
    }
}

async function updateAimbotConfig(scan_pattern_val, write_offset_val, head_offset_val, left_ear_offset_val, right_ear_offset_val, left_shoulder_offset_val, right_shoulder_offset_val) {
    try {
        const params = new URLSearchParams({
            scan_pattern: scan_pattern_val,
            write_offset: write_offset_val,
            head_offset: head_offset_val,
            left_ear_offset: left_ear_offset_val,
            right_ear_offset: right_ear_offset_val,
            left_shoulder_offset: left_shoulder_offset_val,
            right_shoulder_offset: right_shoulder_offset_val
        });

        const response = await fetch(`/update-aimbot-config?${params.toString()}`, { method: "GET" });
        const data = await response.json();

        if (!response.ok) {
            safeSetStatus("status: " + (data.error ?? "Failed to update aimbot config"));
        } else {
            safeSetStatus("status: " + (data.response ?? "Aimbot updated"));
        }
    } catch (err) {
        console.error(err);
        safeSetStatus("status: Failed to update aimbot config");
    }
}

async function updateSniperConfig(sniper_scan_val, sniper_replace_val) {
    try {
        const params = new URLSearchParams({
            scan: sniper_scan_val,
            replace: sniper_replace_val
        });
        const response = await fetch(`/update-sniper-config?${params.toString()}`, { method: "GET" });
        const data = await response.json();

        if (!response.ok) {
            safeSetStatus("status: " + (data.error ?? "Failed to update sniper config"));
        } else {
            safeSetStatus("status: " + (data.response ?? "Sniper updated"));
        }
    } catch (err) {
        console.error(err);
        safeSetStatus("status: Failed to update sniper config");
    }
}

loadAimbotConfig();
loadSniperConfig();




document.getElementById("btn_generate_license").addEventListener("click", async () => {
    const licenseType = document.getElementById("license_type").value;
    const quantity = document.getElementById("quantity").value;

    if (!licenseType || !quantity) {
    alert("Please fill both fields!");
    return;
    }

    const response = await fetch(
    `/api/auth/generate-license?type=${licenseType}&quantity=${quantity}`
    );
    const result = await response.json();

    document.getElementById(
    "status_lbl"
    ).innerText = `status: ${result.status} - ${result.message}`;

    var keys = result.generated_keys;

    keys.forEach((element, key) => {
        var key = Object.keys(element)[0]
        document.getElementById("generated_keys").innerHTML += key + "\n"; 
    })
});