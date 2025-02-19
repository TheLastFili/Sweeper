// script.js
document.addEventListener("DOMContentLoaded", () => {
    loadDate();
    loadTimers();
    setupThemeSelector();
});

let currentDate = new Date().toISOString().split("T")[0];
let timers = [];
const themes = {
    'light': {
        background: '#ffffff',
        text: '#000000',
        timerBg: '#f0f0f0'
    },
    'dark': {
        background: '#2d2d2d',
        text: '#ffffff',
        timerBg: '#3d3d3d'
    },
    'blue': {
        background: '#e6f3ff',
        text: '#002b4d',
        timerBg: '#cce6ff'
    }
};

// Date navigation functions
function loadDate() {
    document.getElementById("currentDate").textContent = `Active Day: ${currentDate}`;
}

function previousDay() {
    currentDate = new Date(new Date(currentDate).getTime() - 86400000).toISOString().split("T")[0];
    loadDate();
    loadTimers();
}

function nextDay() {
    currentDate = new Date(new Date(currentDate).getTime() + 86400000).toISOString().split("T")[0];
    loadDate();
    loadTimers();
}

// Theme functions
function setupThemeSelector() {
    const selector = document.getElementById('themeSelector');
    Object.keys(themes).forEach(theme => {
        const option = document.createElement('option');
        option.value = theme;
        option.textContent = theme.charAt(0).toUpperCase() + theme.slice(1);
        selector.appendChild(option);
    });
    selector.addEventListener('change', applyTheme);
}

function applyTheme() {
    const theme = themes[document.getElementById('themeSelector').value];
    document.body.style.backgroundColor = theme.background;
    document.body.style.color = theme.text;
    document.querySelectorAll('.timer').forEach(timer => {
        timer.style.backgroundColor = theme.timerBg;
    });
}

// Timer API functions
async function fetchTimers() {
    const response = await fetch(`/api/timers/${currentDate}`);
    return await response.json();
}

async function saveTimer(timer) {
    await fetch('/api/timer', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            date: currentDate,
            timer: timer
        })
    });
}

async function startTimerAPI(index) {
    await fetch('/api/timer/start', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            date: currentDate,
            index: index
        })
    });
}

async function stopTimerAPI(index) {
    const response = await fetch('/api/timer/stop', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            date: currentDate,
            index: index
        })
    });
    return await response.json();
}

// Timer management functions
async function loadTimers() {
    timers = await fetchTimers();
    renderTimers();
}

async function addTimer() {
    const newTimer = { 
        name: "New Timer", 
        start: null, 
        elapsed: 0,
        lastStarted: null 
    };
    timers.push(newTimer);
    await saveTimer(newTimer);
    renderTimers();
}

async function startTimer(index) {
    if (!timers[index].start) {
        const now = Date.now();
        timers[index].start = now;
        timers[index].lastStarted = now;
        await startTimerAPI(index);
        updateElapsedTime(index);
    }
}

async function stopTimer(index) {
    if (timers[index].start) {
        const response = await stopTimerAPI(index);
        timers[index].elapsed = response.elapsed;
        timers[index].start = null;
        renderTimers();
    }
}

async function resetTimer(index) {
    timers[index].elapsed = 0;
    timers[index].start = null;
    await saveTimer(timers[index]);
    renderTimers();
}

async function deleteTimer(index) {
    await fetch('/api/timer', {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            date: currentDate,
            index: index
        })
    });
    timers.splice(index, 1);
    renderTimers();
}

async function copyToNextDay(index) {
    const nextDate = new Date(new Date(currentDate).getTime() + 86400000)
        .toISOString().split("T")[0];
    
    const timerCopy = {
        name: timers[index].name,
        start: null,
        elapsed: 0,
        lastStarted: null
    };

    await fetch('/api/timer/copy', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            sourceDate: currentDate,
            targetDate: nextDate,
            timer: timerCopy
        })
    });
}

// Utility functions
function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours}h ${mins}m ${secs}s`;
}

function format15MinuteTime(seconds) {
    const totalMinutes = Math.ceil(seconds / 60 / 15) * 15;
    const hours = Math.floor(totalMinutes / 60);
    const mins = totalMinutes % 60;
    return `${hours}h ${mins}m`;
}

function getLastStartedTime(startTime) {
    if (!startTime) return 'Not started';
    const date = new Date(startTime);
    return date.toLocaleTimeString();
}

function updateName(index, name) {
    timers[index].name = name;
    saveTimer(timers[index]);
}

// UI rendering functions
function renderTimers() {
    const container = document.getElementById("timers");
    container.innerHTML = "";
    timers.forEach((timer, index) => {
        const timerDiv = document.createElement("div");
        timerDiv.className = "timer";
        timerDiv.innerHTML = `
            <input type="text" value="${timer.name}" onchange="updateName(${index}, this.value)">
            <button onclick="startTimer(${index})">Start</button>
            <button onclick="stopTimer(${index})">Stop</button>
            <button onclick="resetTimer(${index})">Reset</button>
            <button onclick="deleteTimer(${index})">Delete</button>
            <button onclick="copyToNextDay(${index})">Copy to Next Day</button>
            <p class="elapsed-time">Elapsed: ${formatTime(timer.elapsed)}</p>
            <p class="fifteen-min-time">Billable Time: ${format15MinuteTime(timer.elapsed)}</p>
            <p class="last-started">Last Started: ${getLastStartedTime(timer.lastStarted)}</p>
        `;
        container.appendChild(timerDiv);
        if (timer.start) updateElapsedTime(index);
    });
    applyTheme();
}

function updateElapsedTime(index) {
    if (timers[index].start) {
        const elapsedElement = document.getElementsByClassName("elapsed-time")[index];
        const fifteenMinElement = document.getElementsByClassName("fifteen-min-time")[index];
        const update = () => {
            if (!timers[index].start) return;
            const now = Math.floor((Date.now() - timers[index].start) / 1000) + timers[index].elapsed;
            elapsedElement.textContent = `Elapsed: ${formatTime(now)}`;
            fifteenMinElement.textContent = `Billable Time: ${format15MinuteTime(now)}`;
            requestAnimationFrame(update);
        };
        update();
    }
}

function generateReport() {
    fetch('/api/report')
        .then(response => response.json())
        .then(report => {
            let reportText = "Time Tracking Report:\n\n";
            Object.entries(report).forEach(([date, dayTimers]) => {
                reportText += `Date: ${date}\n`;
                dayTimers.forEach(timer => {
                    reportText += `  ${timer.name} - ${format15MinuteTime(timer.elapsed)}\n`;
                });
                reportText += '\n';
            });
            
            // Create and trigger download
            const blob = new Blob([reportText], { type: 'text/plain' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'time-tracking-report.txt';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        });
}