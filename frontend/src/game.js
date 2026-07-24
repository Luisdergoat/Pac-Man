const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

let tileSize = 28;
let grid = [];
let gums = [];
let super_gums = [];
let player = { row: 0, col: 0 };
let ghost = [];
let lives = 3;
let score = 0;

let gameOverHandled = false;
let awaitingRoundStart = false;

function showScreen(id) {
    document.querySelectorAll(".screen").forEach(el => el.classList.add("hidden"));
    document.getElementById(id).classList.remove("hidden");
}

function hideAllScreens() {
    document.querySelectorAll(".screen").forEach(el => el.classList.add("hidden"));
}

function startLoadingAnimation() {
    const fill = document.getElementById("loading-bar-fill");
    fill.classList.remove("running", "complete");
    void fill.offsetWidth; // erzwingt einen Reflow, damit der Browser width:0% erst "sieht"
    fill.classList.add("running");
}

function finishLoadingAnimation() {
    const fill = document.getElementById("loading-bar-fill");
    fill.classList.remove("running");
    fill.classList.add("complete");
}

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
        ctx.fillStyle = g.color;
        ctx.fillRect(g.col * tileSize, g.row * tileSize, tileSize, tileSize);
    });
    ctx.fillStyle = "white";
    ctx.fillRect(player.col * tileSize, player.row * tileSize, tileSize, tileSize);
}

const socket = new WebSocket(`ws://${window.location.host}/ws`);

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);

    grid = data.grid;
    player = data.player;
    ghost = data.ghosts;
    lives = data.lives;
    score = data.score;
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
            document.getElementById("overlay-score").textContent = `Score: ${score}`;
            showScreen("overlay");
        }
    } else if (gameOverHandled) {
        gameOverHandled = false;
    }

    document.getElementById("score").textContent = `Score: ${score}`;
    document.getElementById("lives").textContent = `Lives: ${lives}`;
    draw();
};

function beginRound() {
    gameOverHandled = false;
    awaitingRoundStart = true;
    document.getElementById("name-input").value = "";
    document.getElementById("submit-name-btn").disabled = false;
    showScreen("loading-screen");
    startLoadingAnimation();
    socket.send(JSON.stringify({ action: "restart" }));
}

document.getElementById("game-start-btn").addEventListener("click", beginRound);
document.getElementById("restart-btn").addEventListener("click", beginRound);

document.getElementById("settings-btn").addEventListener("click", () => {
    showScreen("settings-screen");
});

document.getElementById("settings-back-btn").addEventListener("click", () => {
    showScreen("start-screen");
});

document.getElementById("submit-name-btn").addEventListener("click", () => {
    const name = document.getElementById("name-input").value || "Player";
    socket.send(JSON.stringify({ action: "submit_name", name }));
    document.getElementById("submit-name-btn").disabled = true;
});

const KEY_TO_DIRECTION = {
    w: "up",
    a: "left",
    s: "down",
    d: "right",
};

document.addEventListener("keydown", (event) => {
    const direction = KEY_TO_DIRECTION[event.key];
    if (direction) {
        socket.send(JSON.stringify({ action: "move", direction }));
    }
    if (event.key === "r" || event.key === "R") {
        beginRound();
    }
});