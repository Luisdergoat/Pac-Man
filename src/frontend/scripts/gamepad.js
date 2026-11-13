import { state, MOVE_INTERVAL_MS } from "./state.js";
import { handleKeydown } from "./controls.js";

// Controller support via the browser Gamepad API.
// XInput controllers (Xbox, most PC pads) use the "standard" mapping:
//   0 A | 1 B | 2 X | 3 Y | 8 Back/View | 9 Start | 12-15 D-pad up/down/left/right
//
// In game:  D-pad / left stick = move, Start = pause, Back = menu (Esc),
//           Y = restart (R), X = skip level (Space)
// In menus: D-pad / left stick = select button, A = press, B = back

const BTN = { A: 0, B: 1, X: 2, Y: 3, BACK: 8, START: 9, UP: 12, DOWN: 13, LEFT: 14, RIGHT: 15 };
const STICK_DEADZONE = 0.5;
const AXIS_DOMINANCE = 0.6;    // share one axis needs (60 %) to win over the other
const REPEAT_DELAY_MS = 220;

const previous = {};           // button/direction -> was pressed last frame
let heldDirection = null;
let heldSince = 0;
let lastRepeat = 0;
let focusIndex = 0;
let lastScreenId = null;
let usingPad = false;          // only show the menu highlight while the controller is in use

// MARK: sendKey
// Reuses the keyboard handler so controller and keyboard behave identically.
function sendKey(key) {
    handleKeydown({ key, preventDefault() {} });
}

// MARK: readHat
// Many non-"standard" arcade sticks report all 8 directions on one "hat" axis
// (usually axis 9): -1 up, then clockwise in steps of 2/7, anything > 1 = neutral.
function readHat(pad) {
    if (pad.mapping === "standard" || pad.axes.length < 10) return null;
    const v = pad.axes[9];
    if (v === undefined || v < -1.05 || v > 1.05) return null;
    const step = Math.round((v + 1) / (2 / 7)) % 8;           // 0 = up, 2 = right, 4 = down, 6 = left
    const angle = step * Math.PI / 4;
    return { x: Math.round(Math.sin(angle)), y: Math.round(-Math.cos(angle)) };
}

// MARK: readVector
// Combines D-pad, hat and left stick into one x/y vector (-1..1, y down).
function readVector(pad) {
    const pressed = i => pad.buttons[i] && pad.buttons[i].pressed;
    const dx = (pressed(BTN.RIGHT) ? 1 : 0) - (pressed(BTN.LEFT) ? 1 : 0);
    const dy = (pressed(BTN.DOWN) ? 1 : 0) - (pressed(BTN.UP) ? 1 : 0);
    if (dx || dy) return { x: dx, y: dy };

    const hat = readHat(pad);
    if (hat && (hat.x || hat.y)) return hat;

    return { x: pad.axes[0] || 0, y: pad.axes[1] || 0 };
}

// MARK: readDirection
// Turns an 8-way / analog input into one of the 4 game directions.
// - Below STICK_DEADZONE nothing happens.
// - If one axis makes up at least AXIS_DOMINANCE of the input (e.g. 60 % right,
//   40 % down), that axis wins even if the stick is not held perfectly straight.
// - Real diagonals (8-way stick, both axes ~equal) keep the current direction if it
//   is part of the diagonal, otherwise they choose the turn (the axis you are not
//   moving on). That lets you "pre-hold" a corner, like in the arcade.
function readDirection(pad, current) {
    const { x, y } = readVector(pad);
    const ax = Math.abs(x);
    const ay = Math.abs(y);
    if (Math.hypot(x, y) < STICK_DEADZONE) return null;

    const horizontal = x > 0 ? "right" : "left";
    const vertical = y > 0 ? "down" : "up";
    const share = Math.max(ax, ay) / (ax + ay);

    if (share >= AXIS_DOMINANCE) return ax > ay ? horizontal : vertical;

    // Near-diagonal: decide based on what we are already doing.
    if (current === horizontal || current === vertical) return current;
    if (current === "left" || current === "right") return vertical;
    if (current === "up" || current === "down") return horizontal;
    return ax >= ay ? horizontal : vertical;
}

// MARK: activeScreen
function activeScreen() {
    const exitMenu = document.getElementById("exit-menu-screen");
    if (!exitMenu.classList.contains("hidden")) return exitMenu;
    return document.querySelector(".screen:not(.hidden)");
}

// MARK: menuButtons
function menuButtons(screen) {
    return [...screen.querySelectorAll("button")].filter(b => !b.disabled && b.offsetParent !== null);
}

// MARK: setFocus
function setFocus(buttons) {
    document.querySelectorAll(".gamepad-focus").forEach(b => b.classList.remove("gamepad-focus"));
    if (buttons.length === 0) return;
    focusIndex = (focusIndex + buttons.length) % buttons.length;
    buttons[focusIndex].classList.add("gamepad-focus");
    buttons[focusIndex].focus({ preventScroll: true });
}

// MARK: clearFocus
function clearFocus() {
    document.querySelectorAll(".gamepad-focus").forEach(b => b.classList.remove("gamepad-focus"));
    if (document.activeElement && document.activeElement.tagName === "BUTTON") {
        document.activeElement.blur();
    }
}

// MARK: handleMenu
function handleMenu(screen, justPressed, direction, directionFired) {
    const buttons = menuButtons(screen);
    const screenChanged = screen.id !== lastScreenId;
    if (screenChanged) {
        lastScreenId = screen.id;
        focusIndex = 0;
    }
    if (directionFired && usingPad) {
        if (directionFired === "up" || directionFired === "left") focusIndex--;
        if (directionFired === "down" || directionFired === "right") focusIndex++;
    }
    if (!usingPad) {
        // First controller input only shows the highlight, it does not press anything yet.
        if (directionFired || Object.values(BTN).some(justPressed)) {
            usingPad = true;
            setFocus(buttons);
        }
        return;
    }
    if (screenChanged || directionFired || !buttons[focusIndex]?.classList.contains("gamepad-focus")) {
        setFocus(buttons);
    }

    if (justPressed(BTN.A) && buttons[focusIndex]) {
        buttons[focusIndex].click();
        return;
    }
    if (justPressed(BTN.B)) {
        const back = screen.querySelector("#settings-back-btn, #scoreboard-back-btn, #exit-resume-btn, #resume-btn");
        if (back) back.click();
        return;
    }
    if (justPressed(BTN.START)) sendKey("p");
    if (justPressed(BTN.BACK)) sendKey("Escape");
}

// MARK: pollGamepads
function pollGamepads() {
    const pads = navigator.getGamepads ? [...navigator.getGamepads()].filter(Boolean) : [];
    const pad = pads.find(p => p.mapping === "standard") || pads[0];

    if (pad && !state.gameClosed) {
        const now = Date.now();
        const current = {};
        pad.buttons.forEach((b, i) => { current[i] = b.pressed; });
        const justPressed = i => current[i] && !previous[i];

        // Direction with keyboard-like auto repeat: fire once, then repeat while held.
        const direction = readDirection(pad, heldDirection);
        let directionFired = null;
        if (direction !== heldDirection) {
            heldDirection = direction;
            heldSince = now;
            lastRepeat = now;
            directionFired = direction;
        } else if (direction && now - heldSince >= REPEAT_DELAY_MS && now - lastRepeat >= MOVE_INTERVAL_MS) {
            lastRepeat = now;
            directionFired = direction;
        }

        const screen = activeScreen();
        if (screen) {
            handleMenu(screen, justPressed, direction, directionFired);
        } else {
            clearFocus();
            lastScreenId = null;
            if (directionFired) sendKey(`Arrow${directionFired[0].toUpperCase()}${directionFired.slice(1)}`);
            if (justPressed(BTN.START)) sendKey("p");
            if (justPressed(BTN.BACK)) sendKey("Escape");
            if (justPressed(BTN.Y)) sendKey("r");
            if (justPressed(BTN.X)) sendKey(" ");
        }

        Object.assign(previous, current);
    }
    requestAnimationFrame(pollGamepads);
}

// MARK: initGamepad
export function initGamepad() {
    window.addEventListener("gamepadconnected", e => console.log(`Controller connected: ${e.gamepad.id}`));
    window.addEventListener("gamepaddisconnected", e => {
        console.log(`Controller disconnected: ${e.gamepad.id}`);
        clearFocus();
    });
    // Mouse users should not see a stale controller highlight.
    document.addEventListener("mousemove", () => {
        if (!usingPad) return;
        usingPad = false;
        clearFocus();
    });
    requestAnimationFrame(pollGamepads);
}
