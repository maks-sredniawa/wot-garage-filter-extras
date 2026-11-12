import { ModelObserver } from "../../libs/model.js";

const MODEL_NAME = "maksforge_garage_filter_extras.FilterToggleView";
const OURS_ATTR = "data-mfgfe-toggle";
const SPECIALS_ROW = '[class*="FilterPopover_toggleContainer"]';
const SPECIAL_ICON = '[class*="FilterPopover_specialsIcons"]';

const model = ModelObserver(MODEL_NAME);

function send(command, args) {
    const target = model.model;
    if (target && typeof target[command] === "function") target[command](args);
}

function log(level, msg) {
    try { send("onJsLog", { level: level, msg: String(msg) }); } catch (e) {}
}

function el(className) {
    const node = document.createElement("div");
    node.className = className;
    return node;
}

function findSpecialsRow() {
    const rows = document.querySelectorAll(SPECIALS_ROW);
    for (let i = 0; i < rows.length; i++) {
        if (rows[i].querySelector(SPECIAL_ICON)) return rows[i];
    }
    return null;
}

function isUpscaled() {
    return parseFloat(getComputedStyle(document.documentElement).fontSize) > 1;
}

function buildToggle() {
    const toggle = el("mfgfe-toggle");
    toggle.setAttribute(OURS_ATTR, "nonPremium");
    toggle.appendChild(el("mfgfe-border"));
    toggle.appendChild(el("mfgfe-background"));
    toggle.appendChild(el("mfgfe-bulb"));
    toggle.appendChild(el("mfgfe-overlay"));
    const content = el("mfgfe-content");
    content.appendChild(el("mfgfe-icon"));
    toggle.appendChild(content);
    toggle.addEventListener("click", function (event) {
        event.stopPropagation();
        try { engine.call("PlaySound", "play"); } catch (e) {}
        send("onToggleNonPremium");
    });
    return toggle;
}

function setClass(node, className, on) {
    if (on) node.classList.add(className);
    else node.classList.remove(className);
}

function render(toggle) {
    const state = model.model || {};
    toggle.style.display = state.visible ? "" : "none";
    setClass(toggle, "mfgfe-toggle--on", !!state.onlyNonPremium);
    setClass(toggle.querySelector(".mfgfe-icon"), "mfgfe-icon--upscale", isUpscaled());
}

function ensureToggle() {
    const row = findSpecialsRow();
    if (!row) return;
    let toggle = row.querySelector("[" + OURS_ATTR + "]");
    if (!toggle) {
        toggle = buildToggle();
        row.appendChild(toggle);
        log("info", "non-premium toggle added to the filter popup");
    }
    render(toggle);
}

let scheduled = false;

function scheduleEnsure() {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(function () {
        scheduled = false;
        ensureToggle();
    });
}

function start() {
    if (window.__mfgfeFilterToggle) return;
    window.__mfgfeFilterToggle = true;
    model.onUpdate(scheduleEnsure);
    model.subscribe();
    new MutationObserver(scheduleEnsure).observe(document.body, { childList: true, subtree: true });
    ensureToggle();
    log("info", "filter popup watcher started");
}

engine.whenReady.then(function () {
    try { start(); } catch (e) { log("error", "start failed: " + e); }
});
