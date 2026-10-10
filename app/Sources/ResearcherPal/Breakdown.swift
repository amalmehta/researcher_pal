import AppKit
import WebKit

/// "Download breakdown": one PDF of everything built for a paper or case study (summary, concept map, coverage,
/// every concept with its equations, the animations, every exercise's instructions; never the solutions), rendered
/// by the same page the app uses, laid out for print.
@MainActor
final class Breakdown: NSObject, WKNavigationDelegate {
    enum Failure: LocalizedError {
        case nothingBuilt, renderFailed(String)
        var errorDescription: String? {
            switch self {
            case .nothingBuilt: return "This paper hasn't been analyzed yet, so there's nothing to download."
            case .renderFailed(let why): return "The breakdown couldn't be made: \(why)"
            }
        }
    }

    /// Exports run one at a time; the exporter keeps itself alive until it finishes.
    private static var running: Breakdown?

    private let paper: Paper
    private let page: URL
    private let destination: URL
    private let done: (Result<URL, Error>) -> Void
    private var window: NSWindow?
    private var webView: WKWebView?
    /// First each animation is opened to capture its key frames, then the breakdown page is printed.
    private var pendingAnimations: [URL] = []
    private var frames: [String: Any] = [:]
    private var printing = false

    static func export(_ paper: Paper, to destination: URL, done: @escaping (Result<URL, Error>) -> Void) {
        guard running == nil else { return }
        guard paper.conceptGraph != nil else { return done(.failure(Failure.nothingBuilt)) }
        // Written next to the material so its relative images resolve; removed when the export ends.
        let page = paper.directory.appendingPathComponent(".rp-breakdown.html")
        let exporter = Breakdown(paper: paper, page: page, destination: destination, done: done)
        running = exporter
        exporter.start()
    }

    private init(paper: Paper, page: URL, destination: URL, done: @escaping (Result<URL, Error>) -> Void) {
        self.paper = paper
        self.page = page
        self.destination = destination
        self.done = done
    }

    // MARK: - what goes in

    /// `framed` names the animations that have snapshots: each is placed under the first concept that links it.
    static func documents(for paper: Paper, framed: Set<String> = []) -> [String] {
        var docs = [front(paper)]
        if let graph = paper.conceptGraph, let text = try? String(contentsOf: graph, encoding: .utf8) {
            docs.append(placeFrames(in: dropTitle(text), framed: framed))
        }
        if !paper.animations.isEmpty {
            docs.append("## Animations\n\nThese are interactive in Researcher Pal (the Animations tab): play them, step " +
                        "through them, and drag the sliders to see what changes." +
                        (framed.isEmpty ? "" : " Key frames from each appear above, under the concept they explain.") + "\n\n" +
                        paper.animations.map { "- **\(animationTitle($0))** (`\($0.lastPathComponent)`)" }.joined(separator: "\n"))
        }
        if !paper.exercises.isEmpty {
            var section = "## Exercises\n\nIn order, each building on the last. Coded exercises have a stub to complete " +
                "(`impl.py`) and tests that pass once it's right; worked problems are answered in `answer.md`. " +
                "Solutions are not included.\n"
            for folder in paper.exercises {
                if let readme = try? String(contentsOf: folder.appendingPathComponent("README.md"), encoding: .utf8) {
                    section += "\n" + demote(readme, by: 2) + "\n"
                }
            }
            docs.append(section)
        }
        if let sources = paper.sources, let text = try? String(contentsOf: sources, encoding: .utf8) {
            docs.append(demote(text, by: 1))
        }
        return docs
    }

    /// Title, where it came from, and when this breakdown was made.
    private static func front(_ paper: Paper) -> String {
        var lines = ["# \(paper.title)", ""]
        let json = (try? Data(contentsOf: paper.directory.appendingPathComponent("source.json")))
            .flatMap { try? JSONSerialization.jsonObject(with: $0) as? [String: Any] } ?? [:]
        var source: [String] = []
        if let arxiv = json["arxiv"] as? String { source.append("arXiv [\(arxiv)](https://arxiv.org/abs/\(arxiv))") }
        if let doi = json["doi"] as? String, !doi.lowercased().contains("arxiv") { source.append("DOI [\(doi)](https://doi.org/\(doi))") }
        let kind = paper.kind == .caseStudy ? "Case study" : "Paper breakdown"
        let date = DateFormatter.localizedString(from: Date(), dateStyle: .long, timeStyle: .none)
        lines.append("> **\(kind)** made with Researcher Pal on \(date)." + (source.isEmpty ? "" : " Source: " + source.joined(separator: " · ") + "."))
        lines.append("> Contents: the concept map and coverage, every concept with its equations and nuances" +
                     (paper.animations.isEmpty ? "" : ", the animations") +
                     (paper.exercises.isEmpty ? "" : ", and the exercises (without solutions)") +
                     (paper.sources == nil ? "" : ", and the sources") + ".")
        return lines.joined(separator: "\n")
    }

    /// The concept graph's own "# Title: concept graph" line; the front page already has the title.
    private static func dropTitle(_ markdown: String) -> String {
        var lines = markdown.split(separator: "\n", omittingEmptySubsequences: false).map(String.init)
        if let first = lines.firstIndex(where: { !$0.trimmingCharacters(in: .whitespaces).isEmpty }), lines[first].hasPrefix("# ") {
            lines.remove(at: first)
        }
        return lines.joined(separator: "\n")
    }

    /// After the bullet list holding the first "**Animation:**" link to each framed animation, leave a marker the
    /// page replaces with that animation's key frames.
    private static func placeFrames(in markdown: String, framed: Set<String>) -> String {
        var lines = markdown.split(separator: "\n", omittingEmptySubsequences: false).map(String.init)
        var placed = Set<String>()
        var i = 0
        while i < lines.count {
            let line = lines[i]
            let names = line.contains("**Animation:**")
                ? matches(of: #"animations/([\w.\-]+\.html)"#, in: line)
                    .reduce(into: [String]()) { if !$0.contains($1) { $0.append($1) } }  // link text and URL both match
                    .filter { framed.contains($0) && !placed.contains($0) }
                : []
            if !names.isEmpty {
                var end = i + 1
                while end < lines.count, lines[end].hasPrefix("- ") || lines[end].hasPrefix("  ") { end += 1 }
                lines.insert(contentsOf: [""] + names.map { "<!--FRAMES:\($0)-->" } + [""], at: end)
                placed.formUnion(names)
                i = end + names.count + 2
            } else {
                i += 1
            }
        }
        return lines.joined(separator: "\n")
    }

    private static func matches(of pattern: String, in text: String) -> [String] {
        guard let regex = try? NSRegularExpression(pattern: pattern) else { return [] }
        return regex.matches(in: text, range: NSRange(text.startIndex..., in: text)).compactMap {
            Range($0.range(at: 1), in: text).map { String(text[$0]) }
        }
    }

    private static func animationTitle(_ url: URL) -> String {
        guard let html = try? String(contentsOf: url, encoding: .utf8),
              let range = html.range(of: #"<title>([^<]*)</title>"#, options: .regularExpression) else {
            return url.deletingPathExtension().lastPathComponent.replacingOccurrences(of: "_", with: " ")
        }
        return String(html[range]).replacingOccurrences(of: #"</?title>"#, with: "", options: .regularExpression)
            .replacingOccurrences(of: " · researcher-pal", with: "")
    }

    /// Pushes a document's headings down `levels`, so an exercise's "# 01 · …" sits under "## Exercises".
    private static func demote(_ markdown: String, by levels: Int) -> String {
        var inFence = false
        return markdown.split(separator: "\n", omittingEmptySubsequences: false).map { line -> String in
            if line.hasPrefix("```") { inFence.toggle() }
            guard !inFence, line.hasPrefix("#") else { return String(line) }
            let hashes = line.prefix { $0 == "#" }.count
            return String(repeating: "#", count: min(6, hashes + levels)) + line.dropFirst(hashes)
        }.joined(separator: "\n")
    }

    // MARK: - rendering

    /// Jumps the player to the middle and the last step and copies out the drawing each time.
    private static let captureScript = #"""
    (() => {
      const steps = [...new Set([Math.floor((STEPS.length - 1) / 2), STEPS.length - 1])];
      const frames = steps.map(k => {
        t = starts[k] + STEPS[k].duration * 0.999; playing = false; stopAt = null; render();
        const svg = document.getElementById("stage").cloneNode(true);
        svg.removeAttribute("id");
        return { svg: svg.outerHTML, caption: STEPS[k].caption, step: k + 1, of: STEPS.length };
      });
      return JSON.stringify({ title: CONFIG.title, frames });
    })()
    """#

    private func start() {
        // Printing needs the page in a window; this one stays off screen.
        let frame = NSRect(x: -20000, y: -20000, width: 800, height: 1100)
        let window = NSWindow(contentRect: frame, styleMask: [.borderless], backing: .buffered, defer: false)
        let view = WKWebView(frame: NSRect(origin: .zero, size: frame.size), configuration: WKWebViewConfiguration())
        view.navigationDelegate = self
        view.appearance = NSAppearance(named: .aqua)  // paper is white, whatever the app's appearance
        window.contentView = view
        window.orderBack(nil)
        self.window = window
        self.webView = view
        pendingAnimations = paper.animations
        next()
    }

    /// The next animation to capture, or, once they're all done, the breakdown page itself.
    private func next() {
        guard let webView else { return }
        if let animation = pendingAnimations.first {
            pendingAnimations.removeFirst()
            webView.loadFileURL(animation, allowingReadAccessTo: paper.directory)
            return
        }
        printing = true
        let html = DocumentPage.html(documents: Self.documents(for: paper, framed: Set(frames.keys)),
                                     title: paper.title, print: true, frames: frames)
        do {
            try html.write(to: page, atomically: true, encoding: .utf8)
            webView.loadFileURL(page, allowingReadAccessTo: paper.directory)
        } catch {
            finish(.failure(error))
        }
    }

    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        if printing {
            // Give KaTeX and the map a moment to lay out after the page's own scripts run.
            DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) { [self] in self.print() }
            return
        }
        // An animation: let its deferred scripts (KaTeX, the player) start, then copy out its key frames. A page
        // that can't be captured is left out of the PDF rather than stopping it.
        guard let name = webView.url?.lastPathComponent else { return next() }
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) { [self] in
            webView.evaluateJavaScript(Self.captureScript) { [self] value, _ in
                if let json = value as? String, let data = json.data(using: .utf8),
                   let parsed = try? JSONSerialization.jsonObject(with: data) {
                    frames[name] = parsed
                }
                next()
            }
        }
    }

    func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
        failed(error)
    }

    func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
        failed(error)
    }

    /// An animation that won't load is left out; the breakdown page itself failing ends the export.
    private func failed(_ error: Error) {
        if printing { finish(.failure(Failure.renderFailed(error.localizedDescription))) } else { next() }
    }

    private func print() {
        guard let webView, let window else { return }
        let info = NSPrintInfo()
        info.paperSize = NSSize(width: 612, height: 792)  // US Letter; A4 users can still print it fine
        info.topMargin = 46; info.bottomMargin = 46; info.leftMargin = 50; info.rightMargin = 50
        info.horizontalPagination = .fit
        info.verticalPagination = .automatic
        info.isVerticallyCentered = false
        info.jobDisposition = .save
        info.dictionary()[NSPrintInfo.AttributeKey.jobSavingURL] = destination
        let operation = webView.printOperation(with: info)
        operation.showsPrintPanel = false
        operation.showsProgressPanel = false
        operation.view?.frame = webView.bounds
        // Modal, not run(): WebKit draws the pages asynchronously on the main thread, so a print that blocks the
        // main thread waits on itself forever.
        operation.runModal(for: window, delegate: self, didRun: #selector(printed(_:success:contextInfo:)), contextInfo: nil)
    }

    @objc private func printed(_ operation: NSPrintOperation, success: Bool, contextInfo: UnsafeMutableRawPointer?) {
        // The callback can arrive off the main thread; closing the hidden window there crashes AppKit.
        let made = success && FileManager.default.fileExists(atPath: destination.path)
        DispatchQueue.main.async { [self] in
            finish(made ? .success(destination) : .failure(Failure.renderFailed("printing to PDF didn't finish")))
        }
    }

    private func finish(_ result: Result<URL, Error>) {
        try? FileManager.default.removeItem(at: page)
        window?.orderOut(nil)
        window = nil
        webView = nil
        Breakdown.running = nil
        done(result)
    }
}
