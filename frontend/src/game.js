const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");


let size = 51;
let speed = 15;
let tileSize = 28;
let grid = [];


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
function draw(){
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (let row = 0; row < grid.length; row++){
        for (let col = 0; col < grid[row].length; col++){
            if (grid[row][col] === 1){
                ctx.fillStyle = "blue";
                ctx.fillRect(col * tileSize, row * tileSize, tileSize, tileSize);
            }
        }
    }
    ghost.forEach(g => {
        ctx.fillStyle = g.color;
        ctx.fillRect(g.col * tileSize, g.row * tileSize, tileSize, tileSize);
    });
    ctx.fillStyle = "black";
    ctx.fillRect(player.col * tileSize, player.row * tileSize, size, size);
}

const socket = new WebSocket(`ws://${window.location.host}/ws`);

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.grid) {
        grid = data.grid;
        fitCanvasToWindow();
    }
    player = data.player;
    ghost = data.ghosts;
    lives = data.lives;
    score = data.score;
    draw();
};

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
});
