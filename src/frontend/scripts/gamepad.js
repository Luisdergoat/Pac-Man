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

// MARK: readDirection
function readDirection(pad) {
    const pressed = i => pad.buttons[i] && pad.buttons[i].pressed;
    if (pressed(BTN.UP)) return "up";
    if (pressed(BTN.DOWN)) return "down";
    if (pressed(BTN.LEFT)) return "left";
    if (pressed(BTN.RIGHT)) return "right";

    const x = pad.axes[0] || 0;
    const y = pad.axes[1] || 0;
    if (Math.max(Math.abs(x), Math.abs(y)) < STICK_DEADZONE) return null;
    if (Math.abs(x) > Math.abs(y)) return x > 0 ? "right" : "left";
    return y > 0 ? "down" : "up";
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
        const direction = readDirection(pad);
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
