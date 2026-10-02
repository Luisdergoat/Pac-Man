import { canvas, ctx, state, cheat_list, socket, MOVE_INTERVAL_MS, KEY_TO_DIRECTION } from "./state.js";
import { showScreen, startLoadingAnimation, openExitMenuScreen, resumeFromExitMenu } from "./screens.js";
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
    if (input !== state.cheat_check[0]) {
        state.cheat_check = structuredClone(cheat_list);
    }
    if (input === state.cheat_check[0]) {
        state.cheat_check.shift();
        if (state.cheat_check.length === 0) {
            state.cheat_check = structuredClone(cheat_list);
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
    canvas.classList.add("hidden");
    document.getElementById("scoreboard").classList.add("hidden");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    showScreen("start-screen");
}

// MARK: confirmExit
export function confirmExit() {
    state.gameClosed = true;
    socket.send(JSON.stringify({ action: "exit_game" }));
    showScreen("game-closed-screen");
}

// MARK: handleKeydown
export function handleKeydown(event) {
    if (state.gameClosed) {
        return;
    }

    const exitMenuOpen = !document.getElementById("exit-menu-screen").classList.contains("hidden");
    if (event.key === "Escape") {
        if (exitMenuOpen) {
            resumeFromExitMenu();
        } else {
            openExitMenuScreen();
        }
        return;
    }
    if (exitMenuOpen) {
        return;
    }

    // Game keys only work while the canvas is shown. Menus, the game over
    // overlay (name input) and the loading screen must not trigger actions.
    // Only "p" is still allowed to leave the pause screen.
    const screenOpen = document.querySelector(".screen:not(.hidden)") !== null;
    const pauseOpen = !document.getElementById("pause-screen").classList.contains("hidden");
    if (event.key === "p" || event.key === "P") {
        if (!screenOpen || pauseOpen) {
            socket.send(JSON.stringify({ action: "pause_toggle" }));
        }
        return;
    }
    if (screenOpen) {
        return;
    }
    if (event.key === " " || event.key.startsWith("Arrow")) {
        event.preventDefault();
    }

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
    if (event.key === " ") {
        socket.send(JSON.stringify({ action: "skip_level"}));
    }
}
