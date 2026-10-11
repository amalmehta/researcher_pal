import SwiftUI
import WebKit

/// The conversation, rendered like the concept map: the assistant's Markdown with headings, lists, tables, code and
/// math; your messages as labeled bubbles; the assistant's tool steps collapsed into a quiet "N steps" line; errors
/// and the per-turn summary clearly marked. New messages are appended without reloading, so the page doesn't jump.
struct TranscriptView: NSViewRepresentable {
    let items: [ClaudeRunner.Item]
    let emptyHint: String

    func makeCoordinator() -> Coordinator { Coordinator() }

    func makeNSView(context: Context) -> WKWebView {
        let view = WKWebView(frame: .zero, configuration: WKWebViewConfiguration())
        view.navigationDelegate = context.coordinator
        view.setValue(false, forKey: "drawsBackground")
        context.coordinator.view = view
        context.coordinator.reload(items: items, hint: emptyHint)
        return view
    }

    func updateNSView(_ view: WKWebView, context: Context) {
        context.coordinator.update(items: items, hint: emptyHint)
    }

    final class Coordinator: NSObject, WKNavigationDelegate {
        weak var view: WKWebView?
        private var shown: [UUID] = []
        private var loaded = false
        private var pending: [ClaudeRunner.Item] = []

        func update(items: [ClaudeRunner.Item], hint: String) {
            // A new conversation (or a cleared one) starts over; otherwise only the new messages are added.
            if items.count < shown.count || zip(items, shown).contains(where: { $0.id != $1 }) {
                reload(items: items, hint: hint)
                return
            }
            let fresh = Array(items.dropFirst(shown.count))
            guard !fresh.isEmpty else { return }
            shown += fresh.map(\.id)
            if loaded { append(fresh) } else { pending += fresh }
        }

        func reload(items: [ClaudeRunner.Item], hint: String) {
            shown = items.map(\.id)
            pending = items
            loaded = false
            view?.loadHTMLString(TranscriptView.page(hint: hint), baseURL: nil)
        }

        private func append(_ items: [ClaudeRunner.Item]) {
            let payload = items.map { ["kind": "\($0.kind)", "text": $0.shown] }
            guard let data = try? JSONSerialization.data(withJSONObject: payload),
                  let json = String(data: data, encoding: .utf8) else { return }
            view?.evaluateJavaScript("add(\(json))")
        }

        func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
            loaded = true
            if !pending.isEmpty { append(pending) }
            pending = []
        }

        /// Links open in the browser, not inside the transcript.
        func webView(_ webView: WKWebView, decidePolicyFor action: WKNavigationAction,
                     decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
            if action.navigationType == .linkActivated, let url = action.request.url {
                NSWorkspace.shared.open(url)
                decisionHandler(.cancel)
            } else {
                decisionHandler(.allow)
            }
        }
    }

    static func page(hint: String) -> String {
        let escapedHint = hint.replacingOccurrences(of: "&", with: "&amp;").replacingOccurrences(of: "<", with: "&lt;")
        return """
        <!doctype html><html><head><meta charset="utf-8">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
        <script src="https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
        <style>
          :root { color-scheme: light dark; --ink: #1d1f23; --dim: #6b7280; --line: #e3e5e8; --card: #f6f7f9;
                  --you: #e8f0fe; --accent: #2563eb; --bad: #b42318; --bad-bg: #fdecea; --good: #15803d; }
          @media (prefers-color-scheme: dark) {
            :root { --ink: #ece8df; --dim: #9aa1a9; --line: #2a2f37; --card: #171a1f; --you: #1b2a44; --accent: #58c4dd;
                    --bad: #fc8b80; --bad-bg: #3a1d1b; --good: #83c167; } }
          body { margin: 0; padding: 18px 22px 28px; color: var(--ink); background: transparent;
                 font: 14.5px/1.6 -apple-system, BlinkMacSystemFont, "Helvetica Neue", sans-serif; }
          .hint { color: var(--dim); }
          .who { font-size: 11px; font-weight: 600; letter-spacing: .06em; text-transform: uppercase; color: var(--dim);
                 margin: 0 0 4px; }
          .msg { margin: 0 0 18px; }
          .you { margin-left: auto; max-width: 78%; }
          .you .bubble { background: var(--you); border-radius: 12px 12px 3px 12px; padding: 9px 13px; white-space: pre-wrap; }
          .you .who { text-align: right; }
          .assistant .body > :first-child { margin-top: 0; }
          .assistant .body > :last-child { margin-bottom: 0; }
          h1, h2, h3, h4 { line-height: 1.3; margin: 1.1em 0 .4em; }
          h1 { font-size: 19px; } h2 { font-size: 17px; } h3 { font-size: 15.5px; } h4 { font-size: 14.5px; }
          p { margin: .5em 0; } ul, ol { margin: .4em 0; padding-left: 1.4em; } li { margin: .2em 0; }
          strong { font-weight: 650; }
          a { color: var(--accent); text-decoration: none; } a:hover { text-decoration: underline; }
          code { font: 12.5px ui-monospace, SFMono-Regular, Menlo, monospace; background: var(--card);
                 border: 1px solid var(--line); border-radius: 4px; padding: 1px 5px; }
          pre { background: var(--card); border: 1px solid var(--line); border-radius: 8px; padding: 11px 13px; overflow-x: auto; }
          pre code { background: none; border: 0; padding: 0; }
          blockquote { margin: .6em 0; padding: .1em 0 .1em 12px; border-left: 3px solid var(--line); color: var(--dim); }
          table { border-collapse: collapse; margin: .7em 0; font-size: 13.5px; }
          th, td { border-bottom: 1px solid var(--line); padding: 6px 12px 6px 0; text-align: left; vertical-align: top; }
          th { font-size: 11.5px; text-transform: uppercase; letter-spacing: .05em; color: var(--dim); font-weight: 600; }
          .katex-display { margin: .7em 0; overflow-x: auto; overflow-y: hidden; }
          details.steps { margin: -8px 0 14px; color: var(--dim); font-size: 12.5px; }
          details.steps summary { cursor: pointer; list-style: none; }
          details.steps summary::before { content: "▸ "; } details.steps[open] summary::before { content: "▾ "; }
          details.steps ul { margin: 4px 0 0; padding-left: 1.2em; }
          .status { color: var(--dim); font-size: 12px; margin: -6px 0 22px; padding-bottom: 14px; border-bottom: 1px solid var(--line); }
          .status.ok::before { content: "✓ "; color: var(--good); }
          .status.bad { color: var(--bad); } .status.bad::before { content: "✕ "; }
          .error { background: var(--bad-bg); color: var(--bad); border-radius: 8px; padding: 8px 12px; margin: 0 0 14px;
                   white-space: pre-wrap; font-size: 13px; }
        </style></head>
        <body><div id="out"><p class="hint">\(escapedHint)</p></div>
        <script>
          const out = document.getElementById("out");
          const esc = s => s.replace(/[&<>]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
          // Math is set aside before Markdown runs (so _ and * inside it stay math), then typeset with KaTeX.
          function render(text) {
            const math = [];
            const keep = (t, display) => "@@M" + (math.push([t, display]) - 1) + "@@";
            let src = text.replace(/\\$\\$([\\s\\S]+?)\\$\\$/g, (m, t) => keep(t, true))
                          .replace(/(?<![\\w$\\\\])\\$([^$\\n]+?)\\$(?![\\w$])/g, (m, t) => keep(t, false));
            let html = window.marked ? marked.parse(src, { mangle: false, headerIds: false })
                                     : "<p>" + esc(src).replace(/\\n/g, "<br>") + "</p>";
            return html.replace(/@@M(\\d+)@@/g, (m, i) => {
              const [tex, display] = math[+i];
              if (!window.katex) return esc(display ? "$$" + tex + "$$" : "$" + tex + "$");
              try { return katex.renderToString(tex, { displayMode: display, throwOnError: false }); } catch (e) { return esc(tex); }
            });
          }
          function block(cls, inner) {
            const div = document.createElement("div");
            div.className = cls;
            div.innerHTML = inner;
            out.appendChild(div);
            return div;
          }
          function add(items) {
            const hint = out.querySelector(".hint");
            if (hint) hint.remove();
            for (const item of items) {
              const last = out.lastElementChild;
              if (item.kind === "tool") {
                // Consecutive steps share one quiet, expandable line.
                let group = last && last.matches("details.steps") ? last : null;
                if (!group) {
                  group = document.createElement("details");
                  group.className = "steps";
                  group.innerHTML = "<summary></summary><ul></ul>";
                  out.appendChild(group);
                }
                const li = document.createElement("li");
                li.textContent = item.text;
                group.querySelector("ul").appendChild(li);
                const n = group.querySelectorAll("li").length;
                group.querySelector("summary").textContent = n + (n === 1 ? " step" : " steps") + " · " + item.text;
              } else if (item.kind === "user") {
                block("msg you", '<p class="who">You</p><div class="bubble">' + esc(item.text) + "</div>");
              } else if (item.kind === "assistant") {
                block("msg assistant", '<p class="who">Researcher Pal</p><div class="body">' + render(item.text) + "</div>");
              } else if (item.kind === "result") {
                block("status ok", esc(item.text));
              } else if (item.text.startsWith("Failed ·")) {
                block("status bad", esc(item.text));
              } else {
                block("error", esc(item.text));
              }
            }
            window.scrollTo(0, document.body.scrollHeight);
          }
        </script></body></html>
        """
    }
}
