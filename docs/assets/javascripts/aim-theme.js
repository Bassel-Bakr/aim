/* Aim colour theme.
 *
 * A reader picks one colour; this file derives the site's colour tokens for both schemes from it
 * and writes them over the stylesheet's defaults. With nothing picked it writes nothing, so the
 * stylesheet stays the default palette. Myth and NOTE blocks are not derived: their red and yellow
 * mean the same thing whatever colour is picked. See specs/2026-09-13-theme-picker-design.md.
 *
 * Three parts, in order: colour maths, derivation, and wiring. The first two are pure and load in
 * Node for tests; wiring runs only where there is a document. */
(function (global) {
  "use strict";

  /* -------------------------------------------------------------------------------------------
   * Colour maths: sRGB, OKLCH, contrast, gamut
   * ---------------------------------------------------------------------------------------- */

  function parseHex(hex) {
    const match = /^#?([0-9a-f]{6})$/i.exec(String(hex).trim());
    if (!match) return null;
    const n = parseInt(match[1], 16);
    return [(n >> 16) & 255, (n >> 8) & 255, n & 255].map((v) => v / 255);
  }

  function byteHex(v) {
    const byte = Math.round(Math.min(1, Math.max(0, v)) * 255);
    return byte.toString(16).padStart(2, "0");
  }

  /* A six-digit hex string, or eight digits when an alpha is given. */
  function toHex(rgb, alpha) {
    return `#${rgb.map(byteHex).join("")}${alpha === undefined ? "" : byteHex(alpha)}`;
  }

  function toLinear(v) { return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }
  function fromLinear(v) { return v <= 0.0031308 ? v * 12.92 : 1.055 * Math.pow(v, 1 / 2.4) - 0.055; }

  function rgbToOklch(rgb) {
    const [r, g, b] = rgb.map((v) => toLinear(v));
    const l = Math.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b);
    const m = Math.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b);
    const s = Math.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b);
    const L = 0.2104542553 * l + 0.793617785 * m - 0.0040720468 * s;
    const A = 1.9779984951 * l - 2.428592205 * m + 0.4505937099 * s;
    const B = 0.0259040371 * l + 0.7827717662 * m - 0.808675766 * s;
    return { l: L, c: Math.hypot(A, B), h: (Math.atan2(B, A) * 180 / Math.PI + 360) % 360 };
  }

  /* Linear sRGB for an OKLCH colour, unclamped, so the caller can tell whether it is in gamut. */
  function oklchToLinear(L, C, H) {
    const rad = H * Math.PI / 180, A = C * Math.cos(rad), B = C * Math.sin(rad);
    const l = Math.pow(L + 0.3963377774 * A + 0.2158037573 * B, 3);
    const m = Math.pow(L - 0.1055613458 * A - 0.0638541728 * B, 3);
    const s = Math.pow(L - 0.0894841775 * A - 1.291485548 * B, 3);
    return [
      4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
      -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
      -0.0041960863 * l - 0.7034186147 * m + 1.707614701 * s
    ];
  }

  function inGamut(lin) {
    return lin.every((v) => v >= -1e-4 && v <= 1 + 1e-4);
  }

  /* An sRGB colour at this lightness and hue, with chroma reduced until it fits the gamut. */
  function fit(L, C, H) {
    const lightness = Math.min(1, Math.max(0, L));
    let lin = oklchToLinear(lightness, C, H);
    if (!inGamut(lin)) {
      let lo = 0, hi = C;
      for (let i = 0; i < 24; i++) {
        const mid = (lo + hi) / 2;
        if (inGamut(oklchToLinear(lightness, mid, H))) lo = mid; else hi = mid;
      }
      lin = oklchToLinear(lightness, lo, H);
    }
    return lin.map((v) => fromLinear(Math.min(1, Math.max(0, v))));
  }

  function luminance(rgb) {
    const [r, g, b] = rgb;
    return 0.2126 * toLinear(r) + 0.7152 * toLinear(g) + 0.0722 * toLinear(b);
  }

  function contrast(a, b) {
    const x = luminance(a), y = luminance(b);
    return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05);
  }

  /* -------------------------------------------------------------------------------------------
   * Derivation
   * ---------------------------------------------------------------------------------------- */

  const DEFAULT_SEED = "#9c3522";
  /* The accent aim.css sets for each scheme. Brick applies no override, so its swatch shows these
   * rather than a derived approximation of them. */
  const DEFAULT_ACCENT = { light: "#9c3522", dark: "#e38268" };
  const TEXT_CONTRAST = 4.5;
  const WHITE = [1, 1, 1];
  const NIGHT_FG = parseHex("#e8eaf0");

  const PRESETS = [
    { name: "Brick", seed: "#9c3522" },
    { name: "Teal", seed: "#1f7a78" },
    { name: "Forest", seed: "#3f7a3a" },
    { name: "Cobalt", seed: "#2f5fb3" },
    { name: "Violet", seed: "#6f4bb0" },
    { name: "Rose", seed: "#b0406e" },
    { name: "Amber", seed: "#a8680f" },
    { name: "Slate", seed: "#4f6272" }
  ];

  function isDefault(seed) {
    return typeof seed === "string" && seed.trim().toLowerCase() === DEFAULT_SEED;
  }

  /* The first colour from a starting lightness, stepping 0.01 in one direction, that reaches
   * 4.5:1 against every background. When lightness runs out, chroma halves and the walk restarts,
   * down to grey; null when even grey cannot pass. The walk always runs at the chroma it is given
   * first, so a grey seed, whose chroma is already near zero, is tried rather than skipped. */
  function guard(L, C, H, backgrounds, step) {
    for (let chroma = C; ; chroma /= 2) {
      for (let l = L; l >= 0 && l <= 1; l += step) {
        const rgb = fit(l, chroma, H);
        const passes = backgrounds.every((bg) => contrast(rgb, bg) >= TEXT_CONTRAST);
        if (passes) return rgb;
      }
      if (chroma < 0.004) return null;
    }
  }

  /* The ink with more contrast on a solid colour, or null if neither reaches 4.5:1. */
  function tagInk(tag, night) {
    const best = contrast(night, tag) >= contrast(NIGHT_FG, tag) ? night : NIGHT_FG;
    return contrast(best, tag) >= TEXT_CONTRAST ? best : null;
  }

  /* Token values for both schemes, or null when the seed cannot produce a readable palette. */
  function derive(seed) {
    const rgb = parseHex(seed);
    if (!rgb) return null;
    const { h, c } = rgbToOklch(rgb);
    // Tints scale with the seed's own colourfulness, so a grey seed gives neutral chrome and pages.
    const tint = Math.min(1, c / 0.05);

    const chrome = fit(0.915, 0.012 * tint, h);
    const lAccent = guard(0.48, Math.min(c, 0.14), h, [WHITE, chrome], -0.01);
    const lHeading = guard(0.38, Math.min(c, 0.12), h, [WHITE], -0.01);

    const page = fit(0.15, 0.008 * tint, h);
    const night = fit(0.16, 0.008 * tint, h);
    const dAccent = guard(0.71, Math.min(c, 0.13), h, [page, night], 0.01);
    const dHeading = guard(0.8, Math.min(c, 0.1), h, [page], 0.01);

    if (!lAccent || !lHeading || !dAccent || !dHeading) return null;
    // Ink for text set on the solid accent: the dark scheme's hero button.
    const dOnAccent = tagInk(dAccent, night);
    if (!dOnAccent) return null;

    return {
      light: {
        "--aim-accent": toHex(lAccent),
        "--aim-heading": toHex(lHeading),
        "--md-accent-fg-color--transparent": toHex(lAccent, 0.08),
        "--aim-chrome": toHex(chrome)
      },
      dark: {
        "--aim-accent": toHex(dAccent),
        "--aim-heading": toHex(dHeading),
        "--md-accent-fg-color--transparent": toHex(dAccent, 0.12),
        "--md-default-bg-color": toHex(page),
        "--aim-night": toHex(night),
        "--aim-night-accent": toHex(dAccent),
        // aim.css sets these at :root from night and the accent, and var() resolves there, before
        // the scheme block, so they are written again here or they keep the default night.
        "--aim-chrome": toHex(night),
        "--aim-chrome-accent": toHex(dAccent),
        "--aim-chrome-on-accent": toHex(dOnAccent),
        "--aim-chrome-on-hover": toHex(night)
      }
    };
  }

  const SCHEMES = {
    light: '[data-md-color-scheme="default"][data-md-color-primary]',
    dark: '[data-md-color-scheme="slate"][data-md-color-primary]'
  };

  /* The derived tokens as a stylesheet: one block per scheme, on the selectors aim.css uses. */
  function toCss(tokens) {
    return Object.entries(SCHEMES).map(([scheme, selector]) => {
      const lines = Object.entries(tokens[scheme]).map(([name, value]) => `  ${name}: ${value};`);
      return `${selector} {\n${lines.join("\n")}\n}`;
    }).join("\n");
  }

  const api = global.aimTheme = {
    PRESETS: PRESETS,
    DEFAULT_SEED: DEFAULT_SEED,
    derive: derive,
    isDefault: isDefault,
    toCss: toCss,
    /* Exposed for tests: contrast between two six-digit hex colours, and an in-gamut hex colour
     * for an OKLCH lightness, chroma and hue. */
    contrast: (a, b) => contrast(parseHex(a), parseHex(b)),
    oklchHex: (L, C, H) => toHex(fit(L, C, H))
  };

  if (typeof document === "undefined") return;

  /* -------------------------------------------------------------------------------------------
   * Wiring: storage, painting, and the picker
   * ---------------------------------------------------------------------------------------- */

  const STORAGE_KEY = "aim.theme.seed";
  const STYLE_ID = "aim-theme";

  /* The saved seed, lower-cased, or null. Storage can throw in private windows or when a browser
   * blocks site data; that reads as nothing saved. A malformed value is removed. */
  function readSeed() {
    try {
      const seed = localStorage.getItem(STORAGE_KEY);
      if (seed === null) return null;
      if (parseHex(seed)) return seed.trim().toLowerCase();
      localStorage.removeItem(STORAGE_KEY);
    } catch { /* storage unavailable */ }
    return null;
  }

  function writeSeed(seed) {
    try {
      if (seed === null) localStorage.removeItem(STORAGE_KEY);
      else localStorage.setItem(STORAGE_KEY, seed);
    } catch { /* storage unavailable: the choice lasts until the page is left */ }
  }

  /* Write the tokens into one <style> at the end of <head>, or remove it for the default. */
  function paint(tokens) {
    let style = document.getElementById(STYLE_ID);
    if (!tokens) {
      if (style) style.remove();
      return;
    }
    if (!style) {
      style = document.createElement("style");
      style.id = STYLE_ID;
      document.head.append(style);
    }
    style.textContent = toCss(tokens);
  }

  let active = DEFAULT_SEED;
  const listeners = [];

  function notify() {
    listeners.forEach((listener) => listener(active));
  }

  /* Re-colour the site from a seed and remember it. Brick is the default, so it clears instead.
   * Returns false, changing nothing, when the seed cannot produce a readable palette. */
  function apply(seed) {
    if (isDefault(seed)) {
      reset();
      return true;
    }
    const tokens = derive(seed);
    if (!tokens) return false;
    active = seed.trim().toLowerCase();
    paint(tokens);
    writeSeed(active);
    notify();
    return true;
  }

  function reset() {
    active = DEFAULT_SEED;
    paint(null);
    writeSeed(null);
    notify();
  }

  api.apply = apply;
  api.reset = reset;

  // Runs in <head>, before the body is parsed, so a saved colour is in place before first paint.
  const saved = readSeed();
  if (saved && !isDefault(saved)) {
    const tokens = derive(saved);
    if (tokens) {
      active = saved;
      paint(tokens);
    } else {
      writeSeed(null);
    }
  }

  /* An element with its attributes set and its children appended; a string child becomes text. */
  function element(tag, attributes = {}, children = []) {
    const node = document.createElement(tag);
    for (const [name, value] of Object.entries(attributes)) node.setAttribute(name, value);
    node.append(...children);
    return node;
  }

  /* Which way an arrow key moves through the swatches. A Map rather than an object literal, so a
   * key name that happens to match something on Object.prototype cannot read as a step. */
  const ARROW_STEPS = new Map([
    ["ArrowRight", 1], ["ArrowDown", 1], ["ArrowLeft", -1], ["ArrowUp", -1]
  ]);

  function buildPicker(anchor) {
    const button = element("button", {
      type: "button",
      class: "md-header__button md-icon aim-theme-picker__button",
      "aria-label": "Change colour",
      "aria-haspopup": "dialog",
      "aria-expanded": "false",
      "aria-controls": "aim-theme-panel"
    }, [element("span", { class: "aim-theme-picker__dot", "aria-hidden": "true" })]);

    // Each swatch shows the accent the site will actually use, per scheme, not the raw seed: the
    // derivation adjusts a seed until it is readable, so the seed itself can differ visibly.
    const swatches = PRESETS.map(({ name, seed }) => {
      const tokens = isDefault(seed) ? null : derive(seed);
      const light = tokens ? tokens.light["--aim-accent"] : DEFAULT_ACCENT.light;
      const dark = tokens ? tokens.dark["--aim-accent"] : DEFAULT_ACCENT.dark;
      return element("button", {
        type: "button",
        role: "radio",
        class: "aim-theme-picker__swatch",
        style: `--aim-swatch-light: ${light}; --aim-swatch-dark: ${dark}`,
        "aria-label": name,
        title: name,
        "data-seed": seed
      });
    });
    const group = element("div", {
      role: "radiogroup",
      "aria-label": "Preset colours",
      class: "aim-theme-picker__swatches"
    }, swatches);

    const custom = element("input", { type: "color", class: "aim-theme-picker__input" });
    const customLabel = element("label", { class: "aim-theme-picker__custom" }, ["Custom", custom]);
    const message = element("p", { class: "aim-theme-picker__message", role: "status", hidden: "" });
    const resetButton = element("button", { type: "button", class: "aim-theme-picker__reset" }, ["Reset"]);

    const panel = element("div", {
      id: "aim-theme-panel",
      class: "aim-theme-picker__panel",
      role: "dialog",
      "aria-label": "Site colour",
      hidden: ""
    }, [group, customLabel, message, resetButton]);

    const wrapper = element("div", { class: "md-header__option aim-theme-picker" }, [button, panel]);
    anchor.after(wrapper);

    function sync(seed) {
      let preset = null;
      for (const swatch of swatches) {
        const checked = swatch.getAttribute("data-seed") === seed;
        if (checked) preset = swatch;
        swatch.setAttribute("aria-checked", String(checked));
        swatch.tabIndex = -1;
      }
      (preset || swatches[0]).tabIndex = 0;
      customLabel.toggleAttribute("data-active", !preset);
      custom.value = seed;
    }

    function open() {
      panel.hidden = false;
      button.setAttribute("aria-expanded", "true");
      const checked = swatches.find((swatch) => swatch.tabIndex === 0);
      checked.focus();
    }

    function close(returnFocus) {
      panel.hidden = true;
      message.hidden = true;
      button.setAttribute("aria-expanded", "false");
      if (returnFocus) button.focus();
    }

    function choose(seed) {
      message.hidden = true;
      if (!apply(seed)) {
        message.textContent = "That colour can't be made readable. Try a different one.";
        message.hidden = false;
      }
    }

    button.addEventListener("click", () => {
      if (panel.hidden) open(); else close(false);
    });

    swatches.forEach((swatch, index) => {
      swatch.addEventListener("click", () => choose(swatch.getAttribute("data-seed")));
      swatch.addEventListener("keydown", (event) => {
        const step = ARROW_STEPS.get(event.key);
        if (!step) return;
        event.preventDefault();
        const next = swatches[(index + step + swatches.length) % swatches.length];
        next.focus();
        choose(next.getAttribute("data-seed"));
      });
    });

    custom.addEventListener("input", () => choose(custom.value));
    resetButton.addEventListener("click", () => {
      message.hidden = true;
      reset();
    });

    panel.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        event.preventDefault();
        close(true);
      }
    });

    document.addEventListener("click", (event) => {
      if (!panel.hidden && !wrapper.contains(event.target)) close(false);
    });

    listeners.push(sync);
    sync(active);
  }

  document.addEventListener("DOMContentLoaded", () => {
    // The light/dark toggle's form. If a theme upgrade renames it, there is simply no picker.
    const anchor = document.querySelector('.md-header__option[data-md-component="palette"]');
    if (anchor) buildPicker(anchor);
  });
})(typeof globalThis !== "undefined" ? globalThis : this);
