import { canvas, state, DIRECTION_ANGLES } from "./state.js";
import { draw, fitCanvasToWindow } from "./rendering.js";
import { showScreen, hideAllScreens, finishLoadingAnimation } from "./screens.js";

// MARK: handleSocketMessage
export function handleSocketMessage(event) {
    const data = JSON.parse(event.data);

    if (state.awaitingRoundStart && data.round_id === state.roundId) {
        return; // Ignoriere alte Ticks, die vor dem Start der neuen Runde empfangen wurden
    }
    state.roundId = data.round_id;

    state.grid = data.grid;
    if (data.player.row !== state.player.row || data.player.col !== state.player.col) {
        const dRow = data.player.row - state.player.row;
        const dCol = data.player.col - state.player.col;
        if (dCol > 0) state.playerDirection = DIRECTION_ANGLES.right;
        else if (dCol < 0) state.playerDirection = DIRECTION_ANGLES.left;
        else if (dRow > 0) state.playerDirection = DIRECTION_ANGLES.down;
        else if (dRow < 0) state.playerDirection = DIRECTION_ANGLES.up;
        state.mouthOpen = !state.mouthOpen;
    }
    state.player = data.player;
    state.ghost = data.ghosts;
    state.lives = data.lives;
    state.score = data.score;
    state.level = data.level;
    state.edible = data.edible;
    state.gums = data.gums;
    state.super_gums = data.super_gums;
    if (state.awaitingRoundStart) {
        state.awaitingRoundStart = false;
        fitCanvasToWindow();
        finishLoadingAnimation();
        setTimeout(() => {
            document.getElementById("scoreboard").classList.remove("hidden");
            canvas.classList.remove("hidden");
            hideAllScreens();
        }, 250);
    }

    if (data.game_over) {
        if (!state.gameOverHandled) {
            state.gameOverHandled = true;
            document.getElementById("overlay-score").textContent = state.score;
            document.getElementById("overlay-level").textContent = state.level;
            showScreen("overlay");
        }
    } else if (state.gameOverHandled) {
        state.gameOverHandled = false;
    }
    if (data.paused) {
        if (!state.pauseHandled) {
            state.pauseHandled = true;
            showScreen("pause-screen");
        }
    } else if (state.pauseHandled) {
        state.pauseHandled = false;
        hideAllScreens();
    }

    document.getElementById("level").textContent = state.level;
    document.getElementById("score").textContent = state.score;
    document.getElementById("lives").textContent = state.lives;
    draw();
}
