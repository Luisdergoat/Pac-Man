import { socket } from "./scripts/state.js";
import { injectHeroMazeBackground } from "./scripts/rendering.js";
import { refreshHighscores } from "./scripts/highscores.js";
import {
    openSettingsScreen,
    backToStartScreen,
    openScoreboardScreen,
    scoreboardBackToStartScreen,
} from "./scripts/screens.js";
import { handleSocketMessage } from "./scripts/socket-handlers.js";
import {
    beginRound,
    submitPlayerName,
    resumeGame,
    leaveToMenu,
    handleKeydown,
} from "./scripts/controls.js";

document.querySelectorAll(".pacman-hero").forEach(injectHeroMazeBackground);

socket.onmessage = handleSocketMessage;

document.getElementById("game-start-btn").addEventListener("click", beginRound);
document.getElementById("restart-btn").addEventListener("click", backToStartScreen);
document.getElementById("settings-btn").addEventListener("click", openSettingsScreen);
document.getElementById("settings-back-btn").addEventListener("click", backToStartScreen);
document.getElementById("scoreboard-btn").addEventListener("click", openScoreboardScreen);
document.getElementById("scoreboard-back-btn").addEventListener("click", scoreboardBackToStartScreen);
document.getElementById("submit-name-btn").addEventListener("click", submitPlayerName);
document.getElementById("resume-btn").addEventListener("click", resumeGame);
document.getElementById("menu-btn").addEventListener("click", leaveToMenu);
document.addEventListener("keydown", handleKeydown);

refreshHighscores();
