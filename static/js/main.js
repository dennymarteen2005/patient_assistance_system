let lastAlertIds = new Set();
let lastAlertsStr = "";
let audioCtx = null;
let audioEnabled = false;

function initAudio(btn) {
    try {
        if(!audioCtx) {
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        }
        if (audioCtx.state === 'suspended') {
            audioCtx.resume();
        }
        audioEnabled = true;
        
        if (btn) {
            btn.innerHTML = "Audio Enabled [OK]";
            btn.style.backgroundColor = "var(--success)";
            btn.disabled = true;
            btn.style.opacity = "0.8";
            btn.style.cursor = "default";
        }
    } catch(e) {
        console.error("Audio block:", e);
        if (btn) {
            btn.innerHTML = "Audio Error";
            btn.style.backgroundColor = "var(--danger)";
        }
    }
}

function playBeep(frequency, duration, type='sine') {
    if (!audioEnabled || !audioCtx) return;
    if (audioCtx.state === 'suspended') audioCtx.resume();
    
    const oscillator = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();
    
    oscillator.type = type;
    oscillator.frequency.setValueAtTime(frequency, audioCtx.currentTime);
    
    gainNode.gain.setValueAtTime(0.1, audioCtx.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);
    
    oscillator.connect(gainNode);
    gainNode.connect(audioCtx.destination);
    
    oscillator.start();
    oscillator.stop(audioCtx.currentTime + duration);
}

function playNormalAlert() {
    playBeep(440, 0.5, 'sine');
    setTimeout(() => playBeep(440, 0.5, 'sine'), 600);
}

function playEmergencyAlert() {
    playBeep(880, 0.3, 'square');
    setTimeout(() => playBeep(1100, 0.3, 'square'), 300);
    setTimeout(() => playBeep(880, 0.3, 'square'), 600);
    setTimeout(() => playBeep(1100, 0.3, 'square'), 900);
}

function pollAlerts() {
    if (typeof dashboardType === 'undefined' || dashboardType === 'patient') return;

    fetch('/api/alerts')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('alerts-container');
            if(!container) return;
            
            const filteredAlerts = data.filter(filterAlerts);
            const currentIds = new Set(filteredAlerts.map(a => a.id));
            
            let newEmergency = false;
            let newNormal = false;
            
            filteredAlerts.forEach(alert => {
                if (!lastAlertIds.has(alert.id)) {
                    if (alert.alert_type.toLowerCase().includes('emergency')) {
                        newEmergency = true;
                    } else {
                        newNormal = true;
                    }
                }
            });
            
            if (newEmergency) playEmergencyAlert();
            else if (newNormal) playNormalAlert();
            
            lastAlertIds = currentIds;
            
            // Prevent flickering: only update DOM if data has changed
            const newAlertsStr = JSON.stringify(filteredAlerts);
            if (newAlertsStr === lastAlertsStr) {
                return;
            }
            lastAlertsStr = newAlertsStr;
            
            if (filteredAlerts.length === 0) {
                container.innerHTML = '<p class="text-muted" style="padding: 1rem;">No active alerts.</p>';
                return;
            }
            
            container.innerHTML = filteredAlerts.map(alert => `
                <div class="card alert-card ${alert.alert_type.toLowerCase().includes('emergency') ? 'emergency' : 'normal'}">
                    <div class="alert-header">
                        <span class="alert-type">${alert.alert_type}</span>
                        <span class="alert-time">${new Date(alert.timestamp).toLocaleTimeString()}</span>
                    </div>
                    <div class="patient-info">
                        <p><strong>Patient ID:</strong> ${alert.patient_id}</p>
                        <p><strong>Room:</strong> ${alert.room_no} | <strong>Bed:</strong> ${alert.bed_no}</p>
                        <p><strong>Ward:</strong> ${alert.ward_details}</p>
                    </div>
                    ${dashboardType !== 'family' ? `<button class="btn btn-resolve" onclick="resolveAlert(${alert.id})">Mark Resolved</button>` : ''}
                </div>
            `).join('');
        })
        .catch(error => console.error('Error fetching alerts:', error));
}

function resolveAlert(id) {
    fetch(`/api/resolve/${id}`, { method: 'POST' })
        .then(() => {
            // Force quick refresh
            lastAlertsStr = "";
            pollAlerts();
        })
        .catch(error => console.error('Error resolving alert:', error));
}

// Unconditionally poll every 2 seconds
setInterval(pollAlerts, 2000);
document.addEventListener('DOMContentLoaded', pollAlerts);
setTimeout(pollAlerts, 200);
