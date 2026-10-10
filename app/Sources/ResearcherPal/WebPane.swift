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
        let html = DocumentPage.html(documents: [markdown], title: url.deletingPathExtension().lastPathComponent)
        let out = url.deletingLastPathComponent()
            .appendingPathComponent(".rp-" + url.deletingPathExtension().lastPathComponent + ".html")
        try html.write(to: out, atomically: true, encoding: .utf8)
        return out
    }

    private static let placeholder = """
    <body style="margin:0;background:#0e1013;color:#9aa1a9;font:14px -apple-system;\
    display:flex;align-items:center;justify-content:center;height:100vh">Nothing to show yet.</body>
    """

}
