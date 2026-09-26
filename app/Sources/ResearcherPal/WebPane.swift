import SwiftUI
import WebKit

/// Shows a local file: an animation as-is, or a Markdown file rendered to HTML next to it.
struct WebPane: NSViewRepresentable {
    let fileURL: URL?
    let readAccess: URL

    func makeNSView(context: Context) -> WKWebView {
        let configuration = WKWebViewConfiguration()
        configuration.defaultWebpagePreferences.allowsContentJavaScript = true
        let view = WKWebView(frame: .zero, configuration: configuration)
        view.setValue(false, forKey: "drawsBackground")
        load(in: view)
        return view
    }

    func updateNSView(_ view: WKWebView, context: Context) {
        guard context.coordinator.shown != fileURL else { return }
        context.coordinator.shown = fileURL
        load(in: view)
    }

    func makeCoordinator() -> Coordinator { Coordinator() }

    final class Coordinator {
        var shown: URL?
    }

    private func load(in view: WKWebView) {
        guard let fileURL else {
            view.loadHTMLString(Self.placeholder, baseURL: nil)
            return
        }
        let target: URL
        if fileURL.pathExtension == "md" {
            guard let rendered = try? Self.renderMarkdown(at: fileURL) else {
                view.loadHTMLString(Self.placeholder, baseURL: nil)
                return
            }
            target = rendered
        } else {
            target = fileURL
        }
        view.loadFileURL(target, allowingReadAccessTo: readAccess)
    }

    /// Writes a sibling HTML file so relative images, diagrams and links keep working.
    static func renderMarkdown(at url: URL) throws -> URL {
        let markdown = try String(contentsOf: url, encoding: .utf8)
        let json = String(data: try JSONSerialization.data(withJSONObject: [markdown], options: []),
                          encoding: .utf8) ?? "[\"\"]"
        let html = template.replacingOccurrences(of: "/*MARKDOWN*/[]", with: json)
        let out = url.deletingLastPathComponent()
            .appendingPathComponent(".rp-" + url.deletingPathExtension().lastPathComponent + ".html")
        try html.write(to: out, atomically: true, encoding: .utf8)
        return out
    }

    private static let placeholder = """
    <body style="margin:0;background:#0e1013;color:#9aa1a9;font:14px -apple-system;\
    display:flex;align-items:center;justify-content:center;height:100vh">Nothing to show yet.</body>
    """

    /// Mermaid, KaTeX and a Markdown renderer come from CDNs; the app needs the network for Claude anyway.
    private static let template = """
    <!doctype html>
    <html><head><meta charset="utf-8">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
    <script src="https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"></script>
    <style>
      :root { color-scheme: dark; }
      body { margin: 0; padding: 28px 34px 80px; background: #0e1013; color: #ece8df;
             font: 15px/1.65 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
      .wrap { max-width: 860px; margin: 0 auto; }
      h1 { font-size: 30px; line-height: 1.15; margin: 0 0 18px; }
      h2 { font-size: 22px; margin: 2em 0 .5em; padding-top: .6em; border-top: 1px solid #2a2f37; }
      h3 { font-size: 17px; margin: 1.6em 0 .4em; }
      a { color: #58c4dd; }
      code { font: 12.5px ui-monospace, Menlo, monospace; background: #171a1f; padding: 2px 5px; border-radius: 4px; }
      pre { background: #171a1f; padding: 14px 16px; border-radius: 8px; overflow-x: auto; }
      pre code { background: none; padding: 0; }
      blockquote { margin: 1.2em 0; padding-left: 14px; border-left: 2px solid #2a2f37; color: #9aa1a9; }
      table { border-collapse: collapse; width: 100%; font-size: 14px; margin: 14px 0; }
      th, td { text-align: left; vertical-align: top; padding: 7px 14px 7px 0; border-bottom: 1px solid #2a2f37; }
      th { color: #9aa1a9; font-size: 12px; text-transform: uppercase; letter-spacing: .06em; }
      img { max-width: 100%; background: #fff; border-radius: 6px; }
      .mermaid { background: #f5f4f0; color: #16181b; border-radius: 8px; padding: 16px; overflow-x: auto; }
    </style></head>
    <body><div class="wrap" id="out"></div>
    <script>
      const source = /*MARKDOWN*/[];
      const math = [];
      let text = source[0]
        .replace(/\\$\\$([\\s\\S]+?)\\$\\$/g, (m, t) => "@@M" + (math.push([t, true]) - 1) + "@@")
        .replace(/(?<![\\w$])\\$([^$\\n]+?)\\$(?![\\w$])/g, (m, t) => "@@M" + (math.push([t, false]) - 1) + "@@");
      let html = marked.parse(text, { mangle: false, headerIds: true });
      html = html.replace(/@@M(\\d+)@@/g, (m, i) => {
        const [tex, display] = math[+i];
        try { return katex.renderToString(tex, { displayMode: display, throwOnError: false }); }
        catch (e) { return m; }
      });
      html = html.replace(/<pre><code class="language-mermaid">([\\s\\S]*?)<\\/code><\\/pre>/g,
        (m, code) => '<div class="mermaid">' + code + '</div>');
      document.getElementById("out").innerHTML = html;
      mermaid.initialize({ startOnLoad: true, theme: "neutral" });
    </script></body></html>
    """
}
