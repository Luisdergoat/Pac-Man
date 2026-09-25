import { canvas, ctx, state, cheat_list, socket, MOVE_INTERVAL_MS, KEY_TO_DIRECTION } from "./state.js";
import { showScreen, startLoadingAnimation } from "./screens.js";
import { refreshHighscores } from "./highscores.js";

// MARK: beginRound
export function beginRound() {
    state.gameOverHandled = false;
    state.awaitingRoundStart = true;
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
export function check_input_cheat(input) {
    const expected_input = state.cheat_check[0];
    if (input !== expected_input) {
        state.cheat_check = structuredClone(cheat_list);
    }
    if (input === expected_input) {
        state.cheat_check.shift();
        if (state.cheat_check.length === 0) {
            return true;
        }
    }
    return false;
}

// MARK: submitPlayerName
export function submitPlayerName() {
    const name = document.getElementById("name-input").value || "Player";
    socket.send(JSON.stringify({ action: "submit_name", name }));
    document.getElementById("submit-name-btn").disabled = true;
    setTimeout(refreshHighscores, 400);
}

// MARK: resumeGame
export function resumeGame() {
    socket.send(JSON.stringify({ action: "pause_toggle" }));
}

// MARK: leaveToMenu
export function leaveToMenu() {
    state.pauseHandled = false;
    socket.send(JSON.stringify({ action: "leave_to_menu" }));
    showScreen("start-screen");
}

// MARK: handleKeydown
export function handleKeydown(event) {
    const direction = KEY_TO_DIRECTION[event.key];
    let cheatActivated = false;
    if (direction) {
        const now = Date.now();
        cheatActivated = check_input_cheat(direction);
        if (cheatActivated) {
            cheatActivated = false;
            socket.send(JSON.stringify({ action: "cheat_activate" }));
        }
        if (now - state.lastMoveTime >= MOVE_INTERVAL_MS) {
            state.lastMoveTime = now;
            socket.send(JSON.stringify({ action: "move", direction }));
        }
    }
    if (event.key === "r" || event.key === "R") {
        if (!state.gameOverHandled) {
        beginRound();
        }
    }
    if (event.key === "p" || event.key === "P") {
        socket.send(JSON.stringify({ action: "pause_toggle" }));
    }
    if (event.key === " ") {
        socket.send(JSON.stringify({ action: "skip_level"}));
    }
}
