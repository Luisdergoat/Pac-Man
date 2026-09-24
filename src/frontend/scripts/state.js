export const canvas = document.getElementById("gameCanvas");
export const ctx = canvas.getContext("2d");
export const MOVE_INTERVAL_MS = 80;

export const mazeBgTemplate = document.getElementById("maze-bg-template");

export const DIRECTION_ANGLES = {
    right: 0,
    down: Math.PI / 2,
    left: Math.PI,
    up: -Math.PI / 2,
};

export const cheat_list = [
    "up",
    "up",
    "down",
    "down",
    "left",
    "right",
    "left",
    "right",
];

export const KEY_TO_DIRECTION = {
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

export const socket = new WebSocket(`ws://${window.location.host}/ws`);

export const state = {
    tileSize: 28,
    grid: [],
    gums: [],
    super_gums: [],
    player: { row: 0, col: 0 },
    ghost: [],
    lives: 3,
    score: 0,
    level: 1,
    edible: false,
    roundId: 0, // ID der aktuellen Runde, um alte Ticks zu ignorieren

    gameOverHandled: false,
    awaitingRoundStart: false,
    pauseHandled: false,
    lastMoveTime: 0,

    playerDirection: 0, // Blickrichtung in Radiant, 0 = rechts
    mouthOpen: true,

    cheat_check: structuredClone(cheat_list),
};
