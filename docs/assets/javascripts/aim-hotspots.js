/* Hover a node of a flowchart image, see that node's animation.
 *
 * The chart is someone else's work, reproduced under credit and not modified. So the interaction
 * is a separate layer: transparent buttons positioned over the image in percentages, which is why
 * they stay on their nodes as the image scales. The page supplies the boxes as JSON, measured by
 * colour segmentation of the image rather than placed by hand.
 *
 * The animations are fetched and injected INLINE, never used as <img src>. An SVG served as a file
 * renders in a document of its own, where this page's stylesheet and its [data-md-color-scheme]
 * never reach, so it would lose its colours and stop following the light and dark toggle. See
 * extensions/aim_figures.py, which splices figures at build time for the same reason. Fetching
 * keeps the page light: one figure arrives when a reader asks for it, not forty-eight up front.
 *
 * Hover alone would be a desktop-only feature invisible to a keyboard and useless on a phone, so
 * every hotspot is a real button: Tab reaches it, Enter and Space open it, a tap opens it. Hover
 * and focus preview, a click pins so the pointer can leave, Escape and a second click unpin.
 *
 * A reader without JavaScript keeps the image and its credit, and loses only the hovering. */
(function () {
  "use strict";

  const cache = new Map();

  const figureUrl = (map, key) =>
    new URL(map.getAttribute("data-figures") + key + ".svg", document.baseURI).href;

  // The chart's own words are the description, because they are what the reader pointed at. Above
  // them sits only what kind of node it is, which the chart says in colour and this panel cannot.
  function frame(node, tail) {
    const kind = document.createElement("p");
    kind.className = "aim-hotspot-kind";
    kind.textContent = tail ? `${node.kind} — ${tail}` : node.kind;
    const says = document.createElement("p");
    says.className = "aim-hotspot-says";
    says.textContent = node.says;
    return [kind, says];
  }

  function show(map, panel, key, node) {
    panel.setAttribute("data-node", key);
    const url = figureUrl(map, key);
    panel.textContent = "";
    panel.append(...frame(node, ""));
    if (cache.has(url)) {
      panel.insertAdjacentHTML("beforeend", cache.get(url));
      return;
    }
    fetch(url).then((response) => {
      if (!response.ok) throw new Error(String(response.status));
      return response.text();
    }).then((svg) => {
      cache.set(url, svg);
      // A slow fetch that lands after the reader has moved on must not overwrite what they moved to.
      if (panel.getAttribute("data-node") === key) panel.insertAdjacentHTML("beforeend", svg);
    }).catch(() => {
      if (panel.getAttribute("data-node") === key) {
        panel.textContent = "";
        panel.append(...frame(node, "This drawing could not be loaded."));
      }
    });
  }

  function build(map) {
    const img = map.querySelector("img");
    const data = map.querySelector("script.aim-hotspot-data");
    const panel = map.querySelector(".aim-hotspot-panel");
    if (!img || !data || !panel) return;

    let nodes;
    try {
      nodes = JSON.parse(data.textContent);
    } catch {
      return;
    }

    const layer = document.createElement("div");
    layer.className = "aim-hotspot-layer";
    let pinned = null;

    function unpin() {
      if (!pinned) return;
      pinned.removeAttribute("data-pinned");
      pinned = null;
      map.removeAttribute("data-pinned");
    }

    for (const [key, node] of Object.entries(nodes)) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "aim-hotspot";
      const [left, top, width, height] = node.box;
      Object.assign(button.style, {
        left: `${left}%`, top: `${top}%`, width: `${width}%`, height: `${height}%`,
      });
      // The button is a transparent rectangle, so its name is the only thing announcing it.
      button.setAttribute("aria-label", node.says);
      button.title = node.says;

      const preview = () => {
        if (!pinned) show(map, panel, key, node);
      };
      button.addEventListener("mouseenter", preview);
      button.addEventListener("focus", preview);
      button.addEventListener("click", () => {
        const wasPinned = pinned === button;
        unpin();
        if (wasPinned) return;
        pinned = button;
        button.setAttribute("data-pinned", "");
        map.setAttribute("data-pinned", "");
        show(map, panel, key, node);
      });
      layer.append(button);
    }

    map.addEventListener("keydown", (event) => {
      if (event.key === "Escape") unpin();
    });

    // The layer has to be the size of the image and nothing else. Laid over the <figure> it would
    // include the caption, so every box would be measured against a taller container and the lower
    // nodes would sit below the picture. Wrapping the image gives the percentages the right box.
    const wrap = document.createElement("span");
    wrap.className = "aim-hotspot-frame";
    img.replaceWith(wrap);
    wrap.append(img, layer);
    // Said once, so the panel is not an unexplained empty box before anything is pointed at.
    panel.textContent = "Point at a node above to see what it says and what it looks like.";
    map.setAttribute("data-ready", "");
  }

  const run = () => document.querySelectorAll(".aim-hotspot-map").forEach(build);

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run);
  } else {
    run();
  }
})();
