import { canvas, ctx, mazeBgTemplate, state } from "./state.js";

// MARK: injectHeroMazeBackground
export function injectHeroMazeBackground(hero) {
    hero.prepend(mazeBgTemplate.content.cloneNode(true));
}

// MARK: fitCanvasToWindow
export function fitCanvasToWindow() {
    const rows = state.grid.length;
    const cols = state.grid[0].length;
    const reservedForText = 150;
    const maxWidth = window.innerWidth * 0.9;
    const maxHeight = (window.innerHeight - reservedForText) * 0.9;
    state.tileSize = Math.floor(Math.min(maxWidth / cols, maxHeight / rows));
    canvas.width = cols * state.tileSize;
    canvas.height = rows * state.tileSize;
}

// MARK: drawPacman
export function drawPacman(cx, cy, radius, angle, open, isEdibleMode) {
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
export function drawGhost(x, y, size, color) {
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
export function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (let row = 0; row < state.grid.length; row++) {
        for (let col = 0; col < state.grid[row].length; col++) {
            if (state.grid[row][col] === 1) {
                ctx.fillStyle = "blue";
                ctx.fillRect(col * state.tileSize, row * state.tileSize, state.tileSize, state.tileSize);
            }
        }
    }
    ctx.fillStyle = "white";
    state.gums.forEach(([row, col]) => {
        ctx.beginPath();
        ctx.arc(col * state.tileSize + state.tileSize / 2, row * state.tileSize + state.tileSize / 2, state.tileSize / 6, 0, Math.PI * 2);
        ctx.fill();
    });
    state.super_gums.forEach(([row, col]) => {
        ctx.beginPath();
        ctx.arc(col * state.tileSize + state.tileSize / 2, row * state.tileSize + state.tileSize / 2, state.tileSize / 3, 0, Math.PI * 2);
        ctx.fill();
    });
    state.ghost.forEach(g => {
        if (!g.on_cooldown)
        {
            drawGhost(g.col * state.tileSize, g.row * state.tileSize, state.tileSize, g.color);
        }
    });
    drawPacman(
        state.player.col * state.tileSize + state.tileSize / 2,
        state.player.row * state.tileSize + state.tileSize / 2,
        state.tileSize / 2 * 0.9,
        state.playerDirection,
        state.mouthOpen,
        state.edible
    );
}
