import Foundation

/// The page every Markdown document is shown in: the concept map tab, Ideas, Sources, exercise READMEs, Career fit,
/// and the downloadable breakdown. Markdown with math (KaTeX), headings you can link to, and concept maps drawn as a
/// readable map of cards instead of a full Mermaid diagram squeezed to the page width.
enum DocumentPage {
    /// One page from one or more Markdown documents, shown in order. `print` lays it out for a PDF: no controls,
    /// nothing dimmed, every section open.
    /// `frames` are snapshots of animations, keyed by file name, placed wherever a document says
    /// `<!--FRAMES:name.html-->`; they travel separately so the Markdown and math passes never touch the SVG.
    static func html(documents: [String], title: String, print: Bool = false, frames: [String: Any] = [:]) -> String {
        let json = { (value: Any) in
            String(data: (try? JSONSerialization.data(withJSONObject: value)) ?? Data("null".utf8), encoding: .utf8) ?? "null"
        }
        return template
            .replacingOccurrences(of: "<!--TITLE-->", with: escape(title))
            .replacingOccurrences(of: "/*PRINT*/false", with: print ? "true" : "false")
            .replacingOccurrences(of: "/*FRAMES*/{}", with: json(frames))
            .replacingOccurrences(of: "/*DOCS*/[]", with: json(documents))
    }

    static func escape(_ text: String) -> String {
        text.replacingOccurrences(of: "&", with: "&amp;").replacingOccurrences(of: "<", with: "&lt;")
            .replacingOccurrences(of: ">", with: "&gt;")
    }

    // Raw strings (#"""…"""#), so the CSS and JavaScript below read exactly as they run.
    private static let template = #"""
    <!doctype html>
    <html><head><meta charset="utf-8"><title><!--TITLE--></title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
    <script src="https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"></script>
    <style>
    """# + css + #"""
    </style></head>
    <body><main id="out"></main>
    <script>
    """# + script + #"""
    </script></body></html>
    """#

    private static let css = #"""
    :root { color-scheme: light dark;
      --bg: #ffffff; --ink: #1d1f23; --dim: #646b75; --line: #e4e6ea; --card: #f6f7f9; --accent: #2563eb;
      --prereq: #e9edf1; --prereq-edge: #8a99a8; --core: #e3edfc; --core-edge: #2f6fd8;
      --novel: #fdf1d8; --novel-edge: #c98411; --known: #e2f5e8; --known-edge: #2e9a52; --sel: #2563eb; --dep: #c2410c; }
    @media (prefers-color-scheme: dark) { :root {
      --bg: #0f1114; --ink: #ece8df; --dim: #9aa1a9; --line: #2a2f37; --card: #171a1f; --accent: #58c4dd;
      --prereq: #1d2228; --prereq-edge: #6b7a88; --core: #16243a; --core-edge: #5b93ec;
      --novel: #2f2614; --novel-edge: #e2a33a; --known: #142a1d; --known-edge: #4cbf71; --sel: #58c4dd; --dep: #f59e6b; } }
    /* Typeset like a LaTeX article: KaTeX's Computer Modern faces for text and math alike, so prose and
       equations read as one. The map, labels and controls stay in the system font. */
    body { margin: 0; background: var(--bg); color: var(--ink);
           font: 17.5px/1.62 "KaTeX_Main", "Latin Modern Roman", "CMU Serif", Georgia, serif;
           font-kerning: normal; text-rendering: optimizeLegibility; }
    main { max-width: 760px; margin: 0 auto; padding: 32px 36px 90px; }
    main p, main li { text-align: justify; hyphens: auto; -webkit-hyphens: auto; }
    h1 { font-size: 30px; line-height: 1.2; margin: 0 0 16px; font-weight: 700; letter-spacing: -.01em; }
    h2 { font-size: 23px; margin: 2.2em 0 .55em; padding-top: .75em; border-top: 1px solid var(--line); font-weight: 700; }
    h3 { font-size: 19px; margin: 2em 0 .45em; font-weight: 700; }
    h4 { font-size: 17.5px; margin: 1.5em 0 .35em; font-weight: 700; font-style: italic; }
    p { margin: .6em 0; } ul, ol { padding-left: 1.5em; } li { margin: .25em 0; }
    .katex { font-size: 1.08em; }
    .katex-display { margin: 1.1em 0; }
    .katex-display > .katex { font-size: 1.2em; }
    table, .cmap, .views button, .zoom button { font-family: -apple-system, BlinkMacSystemFont, sans-serif; }
    table .katex { font-size: 1.05em; }
    th, td, table { text-align: left; }
    a { color: var(--accent); text-decoration: none; } a:hover { text-decoration: underline; }
    strong { font-weight: 650; }
    code { font: 12.5px ui-monospace, SFMono-Regular, Menlo, monospace; background: var(--card);
           border: 1px solid var(--line); border-radius: 4px; padding: 1px 5px; }
    pre { background: var(--card); border: 1px solid var(--line); border-radius: 8px; padding: 12px 14px; overflow-x: auto; }
    pre code { background: none; border: 0; padding: 0; }
    blockquote { margin: 1em 0; padding: .2em 0 .2em 14px; border-left: 3px solid var(--line); color: var(--dim); }
    table { border-collapse: collapse; width: 100%; font-size: 14.5px; margin: 1.1em 0; }
    th, td { text-align: left; vertical-align: top; padding: 7px 14px 7px 0; border-bottom: 1px solid var(--line); }
    th { color: var(--dim); font-size: 11.5px; font-weight: 600; text-transform: uppercase; letter-spacing: .06em; }
    img { max-width: 100%; border-radius: 6px; }
    .katex-display { overflow-x: auto; overflow-y: hidden; padding: 2px 0; }
    .doc + .doc { margin-top: 3em; }

    /* ---- the concept map ---- */
    .cmap { margin: 1.2em 0 1.6em; }
    .cmap-bar { display: flex; flex-wrap: wrap; gap: 10px 18px; align-items: center; justify-content: space-between; }
    .legend { display: flex; flex-wrap: wrap; gap: 6px 14px; font-size: 12.5px; color: var(--dim); }
    .legend span::before { content: ""; display: inline-block; width: 10px; height: 10px; border-radius: 3px;
                           margin-right: 6px; vertical-align: -1px; border: 1.5px solid var(--edge); background: var(--fill); }
    .views button, .zoom button { font: 12.5px -apple-system, sans-serif; color: var(--ink); background: var(--card);
            border: 1px solid var(--line); padding: 4px 11px; cursor: pointer; }
    .views button:first-child { border-radius: 6px 0 0 6px; } .views button:last-child { border-radius: 0 6px 6px 0; }
    .views button.on { background: var(--accent); color: #fff; border-color: var(--accent); }
    .cmap-info { margin: 12px 0 6px; padding: 10px 14px; border-radius: 8px; background: var(--card);
                 border: 1px solid var(--line); font-size: 13.5px; min-height: 1.6em; }
    .cmap-info .chip { display: inline-block; margin: 2px 3px; padding: 1px 8px; border-radius: 10px; cursor: pointer;
                       border: 1px solid var(--line); font-size: 12.5px; }
    .cmap-info .chip.pre { border-color: var(--sel); } .cmap-info .chip.post { border-color: var(--dep); }
    .cmap-cards { position: relative; }
    .cmap-links { position: absolute; inset: 0; pointer-events: none; overflow: visible; }
    .csec { margin: 16px 0 4px; }
    .csec h5 { margin: 0 0 8px; font-size: 12px; text-transform: uppercase; letter-spacing: .07em; color: var(--dim); font-weight: 600; }
    .cgrid { display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 8px; }
    .ccard { position: relative; text-align: left; font: 13.5px/1.35 -apple-system, sans-serif; color: var(--ink);
             background: var(--fill); border: 1.5px solid var(--edge); border-radius: 9px; padding: 9px 11px 8px;
             cursor: pointer; transition: opacity .15s, box-shadow .15s; }
    .ccard .meta { display: block; margin-top: 4px; font-size: 11.5px; color: var(--dim); }
    .ccard .anim { float: right; font-size: 12px; margin-left: 6px; }
    .k-prereq { --fill: var(--prereq); --edge: var(--prereq-edge); }
    .k-core { --fill: var(--core); --edge: var(--core-edge); }
    .k-novel { --fill: var(--novel); --edge: var(--novel-edge); }
    .k-known { --fill: var(--known); --edge: var(--known-edge); }
    .k-other { --fill: var(--card); --edge: var(--line); }
    .cmap.focus .ccard { opacity: .28; }
    .cmap.focus .ccard.sel, .cmap.focus .ccard.pre, .cmap.focus .ccard.post { opacity: 1; }
    .ccard.sel { box-shadow: 0 0 0 3px var(--sel); }
    .ccard.pre { box-shadow: 0 0 0 2px var(--sel); } .ccard.post { box-shadow: 0 0 0 2px var(--dep); }
    .cmap-diagram { border: 1px solid var(--line); border-radius: 10px; background: #f8f8f6; overflow: auto; max-height: 75vh; }
    .cmap-diagram .zoom { position: sticky; top: 0; left: 0; z-index: 2; display: flex; gap: 4px; padding: 6px; }
    .cmap-diagram .zoom button { border-radius: 6px; }
    .cmap-diagram .mermaid { padding: 10px 16px 16px; }
    .cmap-diagram svg { max-width: none !important; height: auto; }

    /* Snapshots of the animations, in the breakdown. */
    .anim-frames { margin: 1.2em 0 1.4em; }
    .anim-frames .anim-title { font: 600 12px -apple-system, sans-serif; text-transform: uppercase; letter-spacing: .07em;
                               color: var(--dim); margin-bottom: 6px; }
    .anim-frames .frame { margin: 0 0 12px; break-inside: avoid; }
    .anim-frames svg { display: block; width: 100%; height: auto; border-radius: 8px; }
    .anim-frames figcaption { font-size: .9em; color: var(--dim); margin-top: 5px; text-align: left; }

    @media print {
      * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
      body { background: #fff; color: #111; font-size: 11.5pt; line-height: 1.5; }
      main { max-width: none; padding: 0; }
      h1 { font-size: 22pt; } h2 { font-size: 15pt; } h3 { font-size: 12.5pt; } h4 { font-size: 11.5pt; }
      table { font-size: 9.5pt; }
      .anim-frames svg { width: 88%; margin: 0 auto; }
      .views, .cmap-info, .cmap-links, .cmap-diagram { display: none !important; }
      .ccard { break-inside: avoid; } h2, h3 { break-after: avoid; } table, pre, .katex-display { break-inside: avoid; }
      a { color: inherit; }
    }
    """#

    private static let script = #"""
    const DOCS = /*DOCS*/[];
    const PRINT = /*PRINT*/false;
    const FRAMES = /*FRAMES*/{};
    const out = document.getElementById("out");
    const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

    // GitHub-style heading anchors, so the coverage table's links (#sdpa-scaled-dot-product-attention) land.
    function slug(text) {
      return text.trim().toLowerCase().replace(/[^\p{L}\p{N}_\- ]/gu, "").replace(/ /g, "-");
    }

    // Math is set aside before Markdown runs (so _ and * inside it stay math), then typeset with KaTeX.
    function renderMarkdown(text) {
      const math = [];
      const keep = (t, display) => "@@M" + (math.push([t, display]) - 1) + "@@";
      const src = text.replace(/\$\$([\s\S]+?)\$\$/g, (m, t) => keep(t, true))
                      .replace(/(?<![\w$\\])\$([^$\n]+?)\$(?![\w$])/g, (m, t) => keep(t, false));
      const html = window.marked ? marked.parse(src, { mangle: false })
                                 : "<pre>" + esc(src) + "</pre>";
      return html.replace(/@@M(\d+)@@/g, (m, i) => {
        const [tex, display] = math[+i];
        if (!window.katex) return esc(display ? "$$" + tex + "$$" : "$" + tex + "$");
        try { return katex.renderToString(tex, { displayMode: display, throwOnError: false }); }
        catch (e) { return esc(tex); }
      });
    }

    // ---------------------------------------------------------------- reading a Mermaid flowchart
    function parseFlowchart(src) {
      const nodes = new Map(), edges = [], groups = [], classOf = {};
      let current = null;
      const arrow = /\s*(?:-{2,}>|-{3,}|={2,}>|-\.+->|-\.+-|--\s*\|[^|]*\|\s*>?|-->\s*\|[^|]*\|)\s*/;
      for (const raw of src.split("\n")) {
        const line = raw.replace(/%%.*$/, "").trim();
        if (!line || /^(flowchart|graph)\b/.test(line) || /^(classDef|style|linkStyle|click)\s/.test(line)) continue;
        let m = line.match(/^class\s+([\w,\s]+?)\s+(\w+)\s*;?$/);
        if (m) { m[1].split(",").forEach(id => classOf[id.trim()] = m[2]); continue; }
        m = line.match(/^subgraph\s+(\w+)(?:\s*\[\s*"([^"]*)"\s*\])?/);
        if (m) { current = { id: m[1], title: m[2] || m[1], ids: [] }; groups.push(current); continue; }
        if (line === "end") { current = null; continue; }
        const labels = [];
        const masked = line.replace(/"[^"]*"/g, s => { labels.push(s.slice(1, -1)); return '"@' + (labels.length - 1) + '"'; });
        const chain = [];
        for (const part of masked.split(arrow)) {
          const ids = [];
          for (const chunk of part.split(/\s*&\s*/)) {
            const mm = chunk.match(/^([A-Za-z_]\w*)\s*(?:[\[\(\{>]+\s*"@(\d+)"\s*[\]\)\}]*)?\s*(?::::(\w+))?/);
            if (!mm) continue;
            const id = mm[1];
            ids.push(id);
            if (!nodes.has(id)) nodes.set(id, { id, label: id, cls: null });
            const node = nodes.get(id);
            if (mm[2] !== undefined) node.label = labels[+mm[2]].replace(/#quot;/g, '"').replace(/#lt;/g, "<").replace(/#gt;/g, ">");
            if (mm[3]) node.cls = mm[3];
            if (current && mm[2] !== undefined && !current.ids.includes(id)) current.ids.push(id);
          }
          chain.push(ids);
        }
        for (let i = 0; i + 1 < chain.length; i++) for (const a of chain[i]) for (const b of chain[i + 1]) edges.push([a, b]);
      }
      for (const [id, cls] of Object.entries(classOf)) if (nodes.has(id)) nodes.get(id).cls = cls;
      return { nodes, edges, groups };
    }

    // ---------------------------------------------------------------- the readable map
    const KINDS = { prereq: "Prerequisite", core: "Established idea", novel: "New in this paper", known: "You know this" };
    let mermaidReady = false;
    // SVG text labels: Mermaid's HTML labels are measured from the page and can come out as zero, which collapses
    // the whole layout into a 16x16 box.
    function initMermaid() {
      if (mermaidReady || !window.mermaid) return;
      mermaid.initialize({ startOnLoad: false, theme: "neutral", flowchart: { curve: "basis", useMaxWidth: false, htmlLabels: false } });
      mermaidReady = true;
    }

    function conceptMap(pre, source) {
      const { nodes, edges, groups } = parseFlowchart(source);
      const needs = id => edges.filter(e => e[1] === id).map(e => e[0]);
      const leadsTo = id => edges.filter(e => e[0] === id).map(e => e[1]);
      const kind = n => (n.cls in KINDS) ? n.cls : "other";
      const grouped = new Set(groups.flatMap(g => g.ids));
      const rest = [...nodes.keys()].filter(id => !grouped.has(id));
      const sections = groups.filter(g => g.ids.length).concat(rest.length ? [{ title: groups.length ? "Other" : "", ids: rest }] : []);
      const used = new Set([...nodes.values()].map(kind));

      const wrap = document.createElement("div");
      wrap.className = "cmap";
      wrap.innerHTML =
        '<div class="cmap-bar"><div class="legend">' +
          Object.entries(KINDS).filter(([k]) => used.has(k))
            .map(([k, name]) => '<span class="k-' + k + '">' + name + "</span>").join("") +
          (source.includes("🎬") ? "<span style='--fill:none;--edge:transparent'>🎬 has an animation</span>" : "") +
        '</div><div class="views"><button class="on" data-view="cards">Map</button><button data-view="diagram">Full diagram</button></div></div>' +
        '<div class="cmap-info">Click a concept to see what it builds on and what builds on it.</div>' +
        '<div class="cmap-cards"><svg class="cmap-links"></svg>' +
          sections.map(s => '<div class="csec">' + (s.title ? "<h5>" + esc(s.title) + "</h5>" : "") + '<div class="cgrid">' +
            s.ids.map(id => {
              const n = nodes.get(id);
              const animated = n.label.includes("🎬");
              const label = n.label.replace(/\s*🎬\s*/g, " ").trim();
              const a = needs(id).length, b = leadsTo(id).length;
              const meta = [a ? "builds on " + a : "", b ? "leads to " + b : ""].filter(Boolean).join(" · ") || "standalone";
              return '<button class="ccard k-' + kind(n) + '" data-id="' + esc(id) + '">' +
                (animated ? '<span class="anim" title="Has an animation">🎬</span>' : "") + esc(label) +
                '<span class="meta">' + meta + "</span></button>";
            }).join("") + "</div></div>").join("") +
        '</div><div class="cmap-diagram" hidden><div class="zoom"><button data-z="out">−</button><button data-z="in">+</button>' +
        '<button data-z="fit">Fit</button></div><div class="mermaid"></div></div>';
      pre.replaceWith(wrap);
      if (PRINT) return;

      const info = wrap.querySelector(".cmap-info");
      const svg = wrap.querySelector(".cmap-links");
      const cards = id => wrap.querySelector('.ccard[data-id="' + CSS.escape(id) + '"]');
      const name = id => esc(nodes.get(id).label.replace(/\s*🎬\s*/g, " ").trim());
      let selected = null;

      function entryHeading(id) {
        return [...document.querySelectorAll("h3, h4")].find(h => h.textContent.trim().startsWith(id + ":"));
      }
      function drawLinks() {
        svg.innerHTML = "";
        if (!selected) return;
        const box = wrap.querySelector(".cmap-cards").getBoundingClientRect();
        const centre = el => { const r = el.getBoundingClientRect(); return [r.left - box.left + r.width / 2, r.top - box.top + r.height / 2]; };
        const line = (from, to, colour) => {
          const [x1, y1] = centre(from), [x2, y2] = centre(to);
          const bend = Math.max(30, Math.abs(y2 - y1) / 2);
          const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
          path.setAttribute("d", "M" + x1 + "," + y1 + " C" + x1 + "," + (y1 + bend) + " " + x2 + "," + (y2 - bend) + " " + x2 + "," + y2);
          path.setAttribute("fill", "none");
          path.setAttribute("stroke", getComputedStyle(document.documentElement).getPropertyValue(colour));
          path.setAttribute("stroke-width", "2");
          path.setAttribute("opacity", ".7");
          svg.appendChild(path);
        };
        const me = cards(selected);
        needs(selected).forEach(id => cards(id) && line(cards(id), me, "--sel"));
        leadsTo(selected).forEach(id => cards(id) && line(me, cards(id), "--dep"));
      }
      function select(id) {
        selected = id;
        wrap.classList.toggle("focus", !!id);
        wrap.querySelectorAll(".ccard").forEach(c => c.classList.remove("sel", "pre", "post"));
        if (!id) { info.innerHTML = "Click a concept to see what it builds on and what builds on it."; drawLinks(); return; }
        cards(id).classList.add("sel");
        needs(id).forEach(p => cards(p) && cards(p).classList.add("pre"));
        leadsTo(id).forEach(d => cards(d) && cards(d).classList.add("post"));
        const chips = (ids, cls) => ids.length ? ids.map(x => '<span class="chip ' + cls + '" data-id="' + esc(x) + '">' + name(x) + "</span>").join("") : "<em>nothing here</em>";
        const heading = entryHeading(id);
        info.innerHTML = "<strong>" + name(id) + "</strong>" + (KINDS[kind(nodes.get(id))] ? " <span style='color:var(--dim)'>· " + KINDS[kind(nodes.get(id))] + "</span>" : "") +
          (heading ? ' · <a href="#' + heading.id + '">read the entry ↓</a>' : "") +
          "<br><span style='color:var(--dim)'>Builds on:</span> " + chips(needs(id), "pre") +
          "<br><span style='color:var(--dim)'>Leads to:</span> " + chips(leadsTo(id), "post");
        drawLinks();
      }
      wrap.addEventListener("click", e => {
        const card = e.target.closest(".ccard, .chip");
        if (card) { select(card.dataset.id === selected ? null : card.dataset.id); return; }
        const view = e.target.closest("[data-view]");
        if (view) {
          wrap.querySelectorAll("[data-view]").forEach(b => b.classList.toggle("on", b === view));
          const diagram = view.dataset.view === "diagram";
          wrap.querySelector(".cmap-cards").hidden = diagram;
          info.hidden = diagram;
          wrap.querySelector(".cmap-diagram").hidden = !diagram;
          if (diagram && window.mermaid && !wrap.dataset.drawn) {
            wrap.dataset.drawn = "1";
            initMermaid();
            const host = wrap.querySelector(".cmap-diagram .mermaid");
            mermaid.render("cmap-" + Math.random().toString(36).slice(2), source).then(({ svg }) => {
              host.innerHTML = svg;
              const s = host.querySelector("svg");
              const fit = wrap.querySelector(".cmap-diagram").clientWidth - 40;
              const natural = s.viewBox.baseVal.width;
              s.style.width = Math.min(natural, Math.max(fit, 200)) + "px";  // start fitted, never blown up
            }).catch(err => { host.textContent = "The diagram couldn't be drawn: " + err.message; });
          }
          return;
        }
        const zoom = e.target.closest("[data-z]");
        if (zoom) {
          const s = wrap.querySelector(".cmap-diagram svg");
          if (!s) return;
          const natural = s.viewBox.baseVal.width || s.getBoundingClientRect().width;
          const now = s.getBoundingClientRect().width;
          const fit = wrap.querySelector(".cmap-diagram").clientWidth - 40;
          const next = zoom.dataset.z === "fit" ? fit : zoom.dataset.z === "in" ? now * 1.25 : now / 1.25;
          s.style.width = Math.max(200, Math.min(natural * 2, next)) + "px";
          return;
        }
        if (!e.target.closest(".cmap-info a")) select(null);
      });
      window.addEventListener("resize", drawLinks);
    }

    // ---------------------------------------------------------------- the page
    out.innerHTML = DOCS.map(d => '<article class="doc">' + renderMarkdown(d) + "</article>").join("");
    const seen = {};
    out.querySelectorAll("h1, h2, h3, h4, h5, h6").forEach(h => {
      const base = slug(h.textContent);
      h.id = seen[base] ? base + "-" + seen[base] : base;
      seen[base] = (seen[base] || 0) + 1;
    });
    out.querySelectorAll("pre > code.language-mermaid").forEach(code => {
      const src = code.textContent;
      if (/^\s*(flowchart|graph)\b/.test(src)) conceptMap(code.parentElement, src);
      else { const div = document.createElement("div"); div.className = "mermaid"; div.textContent = src; code.parentElement.replaceWith(div); }
    });
    if (window.mermaid && document.querySelector("main > .doc .mermaid:not(.cmap .mermaid)")) {
      initMermaid();
      mermaid.run({ querySelector: "main > .doc .mermaid:not(.cmap .mermaid)" });
    }
    // Animation snapshots go where a document left <!--FRAMES:name.html-->.
    const walker = document.createTreeWalker(out, NodeFilter.SHOW_COMMENT);
    const markers = [];
    while (walker.nextNode()) markers.push(walker.currentNode);
    for (const marker of markers) {
      const m = marker.nodeValue.trim().match(/^FRAMES:(.+)$/);
      const data = m && FRAMES[m[1]];
      if (!data) continue;
      const fig = document.createElement("figure");
      fig.className = "anim-frames";
      fig.innerHTML = '<div class="anim-title">🎬 ' + esc(data.title) + " · from the animation</div>" +
        data.frames.map(f => '<div class="frame">' + f.svg + "<figcaption>" +
          renderMarkdown("**Step " + f.step + " of " + f.of + ".** " + f.caption).replace(/^\s*<p>|<\/p>\s*$/g, "") +
          "</figcaption></div>").join("");
      marker.replaceWith(fig);
    }
    if (location.hash) { const t = document.getElementById(decodeURIComponent(location.hash.slice(1))); t && t.scrollIntoView(); }
    """#
}
