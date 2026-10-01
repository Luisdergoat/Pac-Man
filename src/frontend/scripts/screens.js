import { refreshHighscores } from "./highscores.js";
import { state } from "./state.js";

// MARK: showScreen
export function showScreen(id) {
    document.querySelectorAll(".screen").forEach(el => el.classList.add("hidden"));
    document.getElementById(id).classList.remove("hidden");
}

// MARK: hideAllScreens
export function hideAllScreens() {
    document.querySelectorAll(".screen").forEach(el => el.classList.add("hidden"));
}

// MARK: startLoadingAnimation
export function startLoadingAnimation() {
    const fill = document.getElementById("loading-bar-fill");
    fill.classList.remove("running", "complete");
    void fill.offsetWidth;
    fill.classList.add("running");
}

// MARK: finishLoadingAnimation
export function finishLoadingAnimation() {
    const fill = document.getElementById("loading-bar-fill");
    fill.classList.remove("running");
    fill.classList.add("complete");
}

// MARK: openSettingsScreen
export function openSettingsScreen() {
    showScreen("settings-screen");
}

// MARK: backToStartScreen
export function backToStartScreen() {
    showScreen("start-screen");
}

// MARK: openScoreboardScreen
export function openScoreboardScreen() {
    refreshHighscores();
    showScreen("scoreboard-screen");
}

// MARK: scoreboardBackToStartScreen
export function scoreboardBackToStartScreen() {
    showScreen("start-screen");
}
// MARK: openExitMenuScreen
export function openExitMenuScreen() {
    const currentlyVisible = document.querySelector(".screen:not(.hidden)");
    state.screenBeforeExit = currentlyVisible ? currentlyVisible.id : null;
    showScreen("exit-menu-screen");
}

// MARK: resumeFromExitMenu
export function resumeFromExitMenu() {
    if (state.screenBeforeExit) {
        showScreen(state.screenBeforeExit);
    } else {
        hideAllScreens();
    }
    state.screenBeforeExit = null;
}
