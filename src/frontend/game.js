const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const MOVE_INTERVAL_MS = 80

const mazeBgTemplate = document.getElementById("maze-bg-template");

// MARK: injectHeroMazeBackground
function injectHeroMazeBackground(hero) {
    hero.prepend(mazeBgTemplate.content.cloneNode(true));
}

document.querySelectorAll(".pacman-hero").forEach(injectHeroMazeBackground);

let tileSize = 28;
let grid = [];
let gums = [];
let super_gums = [];
let player = { row: 0, col: 0 };
let ghost = [];
let lives = 3;
let score = 0;
let level = 1;
let edible = false;
let roundId = 0; // ID der aktuellen Runde, um alte Ticks zu ignorieren

let gameOverHandled = false;
let awaitingRoundStart = false;
let pauseHandled = false
let lastMoveTime = 0;

let playerDirection = 0; // Blickrichtung in Radiant, 0 = rechts
let mouthOpen = true;

const DIRECTION_ANGLES = {
    right: 0,
    down: Math.PI / 2,
    left: Math.PI,
    up: -Math.PI / 2,
};
const cheat_list = [
    "up",
    "up",
    "down",
    "down",
    "left",
    "right",
    "left",
    "right",
]
let cheat_check = structuredClone(cheat_list);

// MARK: renderTop3
function renderTop3(scores) {
    document.getElementById("top-highscore-value").textContent =
        scores.length ? scores[0].score : "00";

    const list = document.getElementById("top3-list");
    list.innerHTML = "";
    scores.slice(0, 3).forEach((entry, i) => {
        const row = document.createElement("div");
        row.className = "top3-row";
        row.innerHTML = `
            <span class="top3-rank">${i + 1}</span>
            <span class="top3-name">${entry.name}</span>
            <span class="top3-level">LV ${entry.level || 1}</span>
            <span class="top3-score">${entry.score}</span>
        `;
        list.appendChild(row);
    });
}

// MARK: renderScoreboard
function renderScoreboard(scores) {
    const list = document.getElementById("scoreboard-list");
    list.innerHTML = "";
    if (!scores.length) {
        list.innerHTML = `<div class="scoreboard-empty">Noch keine Eintr&auml;ge</div>`;
        return;
    }
    scores.forEach((entry, i) => {
        const row = document.createElement("div");
        row.className = "scoreboard-row";
        const rank = i + 1;
        row.innerHTML = `
            <span class="scoreboard-rank rank-${rank}">${rank}</span>
            <span class="scoreboard-name">${entry.name}</span>
            <span class="scoreboard-level">LV ${entry.level || 1}</span>
            <span class="scoreboard-score">${entry.score}</span>
        `;
        list.appendChild(row);
    });
}

// MARK: refreshHighscores
function refreshHighscores() {
    fetch("/highscores")
        .then(res => res.json())
        .then(scores => {
            renderTop3(scores);
            renderScoreboard(scores);
        })
        .catch(() => {});
}

// MARK: showScreen
function showScreen(id) {
    document.querySelectorAll(".screen").forEach(el => el.classList.add("hidden"));
    document.getElementById(id).classList.remove("hidden");
}

// MARK: hideAllScreens
function hideAllScreens() {
    document.querySelectorAll(".screen").forEach(el => el.classList.add("hidden"));
}

// MARK: startLoadingAnimation
function startLoadingAnimation() {
    const fill = document.getElementById("loading-bar-fill");
    fill.classList.remove("running", "complete");
    void fill.offsetWidth; // erzwingt einen Reflow, damit der Browser width:0% erst "sieht"
    fill.classList.add("running");
}

// MARK: finishLoadingAnimation
function finishLoadingAnimation() {
    const fill = document.getElementById("loading-bar-fill");
    fill.classList.remove("running");
    fill.classList.add("complete");
}

// MARK: fitCanvasToWindow
function fitCanvasToWindow() {
    const rows = grid.length;
    const cols = grid[0].length;
    const reservedForText = 150;
    const maxWidth = window.innerWidth * 0.9;
    const maxHeight = (window.innerHeight - reservedForText) * 0.9;
    tileSize = Math.floor(Math.min(maxWidth / cols, maxHeight / rows));
    canvas.width = cols * tileSize;
    canvas.height = rows * tileSize;
}

// MARK: drawPacman
function drawPacman(cx, cy, radius, angle, open, isEdibleMode) {
    const mouthAngle = open ? 0.24 * Math.PI : 0.02 * Math.PI;
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(angle);
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.arc(0, 0, radius, mouthAngle, Math.PI * 2 - mouthAngle);
    ctx.closePath();
    ctx.fillStyle = isEdibleMode ? "#00e5ff" : "#ffd400";
    ctx.fill();
    ctx.restore();
}

// MARK: drawGhost
function drawGhost(x, y, size, color) {
    const r = size / 2;
    const cx = x + r;
    const domeCenterY = y + r;
    const feet = 4;
    const step = size / feet;

    ctx.save();
    ctx.beginPath();
    ctx.arc(cx, domeCenterY, r, Math.PI, 0, false);
    ctx.lineTo(x + size, y + size);
    for (let i = feet; i >= 1; i--) {
        const fx = x + i * step;
        const midX = fx - step / 2;
        ctx.quadraticCurveTo(midX, y + size - size * 0.18, fx - step, y + size);
    }
    ctx.closePath();
    ctx.fillStyle = color;
    ctx.fill();

    const eyeR = size * 0.13;
    const eyeY = y + size * 0.42;
    [cx - size * 0.18, cx + size * 0.18].forEach(ex => {
        ctx.beginPath();
        ctx.fillStyle = "#ffffff";
        ctx.arc(ex, eyeY, eyeR, 0, Math.PI * 2);
        ctx.fill();
        ctx.beginPath();
        ctx.fillStyle = "#1b3bff";
        ctx.arc(ex + eyeR * 0.3, eyeY, eyeR * 0.5, 0, Math.PI * 2);
        ctx.fill();
    });
    ctx.restore();
}

// MARK: draw
function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (let row = 0; row < grid.length; row++) {
        for (let col = 0; col < grid[row].length; col++) {
            if (grid[row][col] === 1) {
                ctx.fillStyle = "blue";
                ctx.fillRect(col * tileSize, row * tileSize, tileSize, tileSize);
            }
        }
    }
    ctx.fillStyle = "white";
    gums.forEach(([row, col]) => {
        ctx.beginPath();
        ctx.arc(col * tileSize + tileSize / 2, row * tileSize + tileSize / 2, tileSize / 6, 0, Math.PI * 2);
        ctx.fill();
    });
    super_gums.forEach(([row, col]) => {
        ctx.beginPath();
        ctx.arc(col * tileSize + tileSize / 2, row * tileSize + tileSize / 2, tileSize / 3, 0, Math.PI * 2);
        ctx.fill();
    });
    ghost.forEach(g => {
        drawGhost(g.col * tileSize, g.row * tileSize, tileSize, g.color);
    });
    drawPacman(
        player.col * tileSize + tileSize / 2,
        player.row * tileSize + tileSize / 2,
        tileSize / 2 * 0.9,
        playerDirection,
        mouthOpen,
        edible
    );
}

const socket = new WebSocket(`ws://${window.location.host}/ws`);

// MARK: handleSocketMessage
function handleSocketMessage(event) {
    const data = JSON.parse(event.data);

    if (awaitingRoundStart && data.round_id === roundId) {
        return; // Ignoriere alte Ticks, die vor dem Start der neuen Runde empfangen wurden
    }
    roundId = data.round_id;

    grid = data.grid;
    if (data.player.row !== player.row || data.player.col !== player.col) {
        const dRow = data.player.row - player.row;
        const dCol = data.player.col - player.col;
        if (dCol > 0) playerDirection = DIRECTION_ANGLES.right;
        else if (dCol < 0) playerDirection = DIRECTION_ANGLES.left;
        else if (dRow > 0) playerDirection = DIRECTION_ANGLES.down;
        else if (dRow < 0) playerDirection = DIRECTION_ANGLES.up;
        mouthOpen = !mouthOpen;
    }
    player = data.player;
    ghost = data.ghosts;
    lives = data.lives;
    score = data.score;
    level = data.level;
    edible = data.edible;
    gums = data.gums;
    super_gums = data.super_gums;
    if (awaitingRoundStart) {
        awaitingRoundStart = false;
        fitCanvasToWindow();
        finishLoadingAnimation();
        setTimeout(() => {
            document.getElementById("scoreboard").classList.remove("hidden");
            canvas.classList.remove("hidden");
            hideAllScreens();
        }, 250);
    }

    if (data.game_over) {
        if (!gameOverHandled) {
            gameOverHandled = true;
            document.getElementById("overlay-score").textContent = score;
            document.getElementById("overlay-level").textContent = level;
            showScreen("overlay");
        }
    } else if (gameOverHandled) {
        gameOverHandled = false;
    }
    if (data.paused) {
        if (!pauseHandled) {
            pauseHandled = true;
            showScreen("pause-screen");
        }
    } else if (pauseHandled) {
        pauseHandled = false;
        hideAllScreens();
    }

    document.getElementById("level").textContent = level;
    document.getElementById("score").textContent = score;
    document.getElementById("lives").textContent = lives;
    draw();
}

socket.onmessage = handleSocketMessage;

// MARK: beginRound
function beginRound() {
    gameOverHandled = false;
    awaitingRoundStart = true;
    document.getElementById("name-input").value = "";
    document.getElementById("submit-name-btn").disabled = false;
    canvas.classList.add("hidden");
    document.getElementById("scoreboard").classList.add("hidden");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    showScreen("loading-screen");
    startLoadingAnimation();
    socket.send(JSON.stringify({ action: "restart" }));
}

// MARK: check_input_cheat
function check_input_cheat(input) {
    expected_input = cheat_check[0];
    if (input !== expected_input) {
        cheat_check = structuredClone(cheat_list);
    }
    if (input === expected_input) {
        cheat_check.shift();
        if (cheat_check.length === 0) {
            return true;
        }
    }
    return false;
}
document.getElementById("game-start-btn").addEventListener("click", beginRound);
document.getElementById("restart-btn").addEventListener("click", beginRound);

// MARK: openSettingsScreen
function openSettingsScreen() {
    showScreen("settings-screen");
}

document.getElementById("settings-btn").addEventListener("click", openSettingsScreen);

// MARK: backToStartScreen
function backToStartScreen() {
    showScreen("start-screen");
}

document.getElementById("settings-back-btn").addEventListener("click", backToStartScreen);

// MARK: openScoreboardScreen
function openScoreboardScreen() {
    refreshHighscores();
    showScreen("scoreboard-screen");
}

document.getElementById("scoreboard-btn").addEventListener("click", openScoreboardScreen);

// MARK: scoreboardBackToStartScreen
function scoreboardBackToStartScreen() {
    showScreen("start-screen");
}

document.getElementById("scoreboard-back-btn").addEventListener("click", scoreboardBackToStartScreen);

// MARK: submitPlayerName
function submitPlayerName() {
    const name = document.getElementById("name-input").value || "Player";
    socket.send(JSON.stringify({ action: "submit_name", name }));
    document.getElementById("submit-name-btn").disabled = true;
    setTimeout(refreshHighscores, 400);
}

document.getElementById("submit-name-btn").addEventListener("click", submitPlayerName);

// MARK: resumeGame
function resumeGame() {
    socket.send(JSON.stringify({ action: "pause_toggle" }));
}

document.getElementById("resume-btn").addEventListener("click", resumeGame);

// MARK: leaveToMenu
function leaveToMenu() {
    pauseHandled = false;
    socket.send(JSON.stringify({ action: "leave_to_menu" }));
    showScreen("start-screen");
}

document.getElementById("menu-btn").addEventListener("click", leaveToMenu);

const KEY_TO_DIRECTION = {
    w: "up",
    a: "left",
    s: "down",
    d: "right",
    W: "up",
    A: "left",
    S: "down",
    D: "right",
    right: "right",
    left: "left",
    down: "down",
    up: "up",
};

// MARK: handleKeydown
function handleKeydown(event) {
    const direction = KEY_TO_DIRECTION[event.key];
    let cheatActivated = false;
    if (direction) {
        const now = Date.now();
        cheatActivated = check_input_cheat(direction);
        if (cheatActivated) {
            socket.send(JSON.stringify({ action: "cheat_activate" }));
        }
        if (now - lastMoveTime >= MOVE_INTERVAL_MS) {
            lastMoveTime = now;
            socket.send(JSON.stringify({ action: "move", direction }));
        }
    }
    if (event.key === "r" || event.key === "R") {
        beginRound();
    }
    if (event.key === "p" || event.key === "P") {
        socket.send(JSON.stringify({ action: "pause_toggle" }));
    }
}

document.addEventListener("keydown", handleKeydown);

refreshHighscores();