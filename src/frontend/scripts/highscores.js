// MARK: renderTop3
export function renderTop3(scores) {
    document.getElementById("top-highscore-value").textContent =
        scores.length ? scores[0].score : "00";

    const list = document.getElementById("top3-list");
    list.innerHTML = "";
    scores.slice(0, 3).forEach((entry, i) => {
        const row = document.createElement("div");
        row.className = "top3-row";
        row.innerHTML = `
            <span class="top3-rank">${i + 1}</span>
            <span class="top3-name">${entry.name}</span>
            <span class="top3-level">LV ${entry.level || 1}</span>
            <span class="top3-score">${entry.score}</span>
        `;
        list.appendChild(row);
    });
}

// MARK: renderScoreboard
export function renderScoreboard(scores) {
    const list = document.getElementById("scoreboard-list");
    list.innerHTML = "";
    if (!scores.length) {
        list.innerHTML = `<div class="scoreboard-empty">Noch keine Eintr&auml;ge</div>`;
        return;
    }
    scores.forEach((entry, i) => {
        const row = document.createElement("div");
        row.className = "scoreboard-row";
        const rank = i + 1;
        row.innerHTML = `
            <span class="scoreboard-rank rank-${rank}">${rank}</span>
            <span class="scoreboard-name">${entry.name}</span>
            <span class="scoreboard-level">LV ${entry.level || 1}</span>
            <span class="scoreboard-score">${entry.score}</span>
        `;
        list.appendChild(row);
    });
}

// MARK: refreshHighscores
export function refreshHighscores() {
    fetch("/highscores")
        .then(res => res.json())
        .then(scores => {
            renderTop3(scores);
            renderScoreboard(scores);
        })
        .catch(() => {});
}
