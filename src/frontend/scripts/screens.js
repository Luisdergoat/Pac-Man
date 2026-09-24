import { refreshHighscores } from "./highscores.js";

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
    void fill.offsetWidth; // erzwingt einen Reflow, damit der Browser width:0% erst "sieht"
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
