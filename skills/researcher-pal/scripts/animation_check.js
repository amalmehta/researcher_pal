/* Runs one researcher-pal animation without a browser and reports what a viewer would see go wrong.
   check_learning.py assembles: [this file up to the split marker] + the page's own scripts + _player.js +
   [the rest of this file], and runs it with node or JavaScriptCore (built into macOS).

   Checks: init() and every draw() call run without throwing (the player catches draw() errors and paints
   them on the canvas, so a browser console stays clean while the viewer sees an error); no NaN/undefined/
   Infinity reaches an SVG attribute; consecutive steps look different; every slider changes the picture. */

// ---------------------------------------------------------------- a document just big enough for the player
const __out = (typeof console !== "undefined" && console.log) ? (s => console.log(s)) : (s => print(s));
class __Node {
  constructor(tag) {
    this.tag = tag; this.attrs = {}; this.children = []; this.style = {}; this.hidden = false;
    this.textContent = ""; this.innerHTML = ""; this.value = ""; this.className = ""; this.parentNode = null;
  }
  setAttribute(k, v) { this.attrs[k] = String(v); }
  getAttribute(k) { return this.attrs[k]; }
  appendChild(c) { this.children.push(c); c.parentNode = this; return c; }
  removeChild(c) { this.children.splice(this.children.indexOf(c), 1); c.parentNode = null; return c; }
  get firstChild() { return this.children[0] || null; }
  addEventListener() {}
  insertAdjacentHTML() {}
  querySelector() { return new __Node("query"); }
  closest() { return new __Node("closest"); }
  blur() {}
  focus() {}
  // A canvas that records what is drawn on it, so two different drawings give two different images.
  getContext() {
    const calls = this.__calls = this.__calls || [];
    return new Proxy({}, {
      get: (target, key) => key in target ? target[key]
        : key === "measureText" ? (s => ({ width: String(s).length * 7 }))
        : key === "createImageData" || key === "getImageData"
          ? ((...a) => { const w = a.length > 2 ? a[2] : a[0], h = a.length > 2 ? a[3] : a[1];
                         return { width: w, height: h, data: new Uint8ClampedArray(Math.max(0, w * h * 4)) }; })
        : key === "putImageData"
          ? (img => { let h = 0; for (let i = 0; i < img.data.length; i++) h = (h * 31 + img.data[i]) | 0; calls.push("pixels" + h); })
        : (...a) => { calls.push(String(key) + JSON.stringify(a)); },
      set: (target, key, value) => { calls.push(String(key) + "=" + value); return true; },
    });
  }
  toDataURL() {
    let h = 0;
    for (const c of (this.__calls || []).join("|")) h = (h * 31 + c.charCodeAt(0)) | 0;
    return "data:image/png;fingerprint," + h + "," + (this.__calls || []).length;
  }
}
const __byId = {};
const __ready = [];
const document = {
  body: new __Node("body"),
  title: "",
  getElementById: id => (__byId[id] = __byId[id] || new __Node("#" + id)),
  createElementNS: (ns, tag) => new __Node(tag),
  createElement: tag => new __Node(tag),
  addEventListener: (type, fn) => { if (type === "DOMContentLoaded") __ready.push(fn); },
};
const window = globalThis;
globalThis.document = document;
globalThis.requestAnimationFrame = () => 0;
globalThis.cancelAnimationFrame = () => {};
if (typeof performance === "undefined") globalThis.performance = { now: () => Date.now() };
if (typeof console === "undefined") globalThis.console = { log: print, error: () => {}, warn: () => {} };
else console.error = () => {};  // the player logs caught draw() errors; this check reports them itself
// @@SPLIT@@
// ---------------------------------------------------------------- the checks
(function () {
  const errors = [], warnings = [], unpinned = [];
  const stage = document.getElementById("stage");
  const picture = () => {
    const walk = n => n.tag + JSON.stringify(n.attrs) + (n.textContent || "") + (n.innerHTML || "") +
      "[" + n.children.map(walk).join(",") + "]";
    return walk(stage);
  };
  const bad = [];
  const scan = n => {
    for (const k in n.attrs) if (/NaN|undefined|Infinity/.test(n.attrs[k])) bad.push(n.tag + " " + k + "=" + n.attrs[k]);
    n.children.forEach(scan);
  };
  // One frame, drawn exactly as the player's render() draws it, but with errors surfaced.
  const frame = (step, raw) => {
    while (stage.firstChild) stage.removeChild(stage.firstChild);
    draw({ S, C, step, p: smooth(raw), raw, params, lerp, clamp, smooth, during, fmt, mix });
    scan(stage);
    return picture();
  };

  for (const k of ["title", "source", "equation"]) if (!CONFIG[k]) warnings.push("CONFIG." + k + " is empty");
  if (!STEPS.length) errors.push("STEPS is empty");
  STEPS.forEach((s, i) => {
    if (!(s.duration > 0)) errors.push("step " + (i + 1) + " has no positive duration");
    if (!s.caption) warnings.push("step " + (i + 1) + " has no caption");
  });
  PARAMS.forEach(pm => {
    if (!(pm.min <= pm.value && pm.value <= pm.max)) errors.push("slider " + pm.id + ": default " + pm.value + " outside [" + pm.min + ", " + pm.max + "]");
    const missing = pm.paperValue === undefined || pm.paperValue === null;
    // Selector sliders (which token, which position) and seeds have no value in the paper: noted, not a problem.
    if (missing) {
      unpinned.push(pm.id);
    } else if (!missing && !(pm.min <= pm.paperValue && pm.paperValue <= pm.max)) {
      errors.push("slider " + pm.id + ": paperValue " + pm.paperValue + " outside its range");
    }
  });

  try { __ready.forEach(fn => fn()); } catch (e) { errors.push("init() threw: " + e.message); }

  const ends = [];
  const seen = new Set();
  STEPS.forEach((s, i) => {
    for (const raw of [0, 0.5, 1]) {
      try {
        const pic = frame(i, raw);
        seen.add(pic);
        if (raw === 1) ends[i] = pic;
      } catch (e) {
        errors.push("draw() throws at step " + (i + 1) + " (" + Math.round(raw * 100) + "% through): " + e.message);
      }
    }
  });
  for (let i = 1; i < STEPS.length; i++) {
    if (ends[i] !== undefined && ends[i] === ends[i - 1]) warnings.push("step " + (i + 1) + " ends looking exactly like step " + i);
  }

  PARAMS.forEach(pm => {
    const original = params[pm.id];
    let changes = false;
    for (const v of [pm.min, pm.max]) {
      for (let i = 0; i < STEPS.length && !changes; i++) {
        try {
          params[pm.id] = original;
          const before = frame(i, 1);
          params[pm.id] = v;
          if (frame(i, 1) !== before) changes = true;
        } catch (e) {
          errors.push("draw() throws with slider " + pm.id + " = " + v + " at step " + (i + 1) + ": " + e.message);
          break;
        }
      }
    }
    params[pm.id] = original;
    if (!changes) errors.push("slider " + pm.id + " doesn't change the picture at its min or max, at any step");
  });

  if (bad.length) errors.push("bad SVG attribute values, e.g. " + Array.from(new Set(bad)).slice(0, 3).join("; "));
  __out("RESULT " + JSON.stringify({ errors, warnings, unpinned, steps: STEPS.length, sliders: PARAMS.length, pictures: seen.size }));
})();
