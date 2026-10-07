import Foundation

/// One paper in the library, laid out the way the researcher-pal skill expects:
/// ~/researcher-pal/papers/<slug>/{paper.pdf, concept_graph.md, animations/, exercises/, ideas/}
struct Paper: Identifiable, Hashable {
    /// A research paper, or a case study of a real incident built the same way (from sources instead of a PDF).
    enum Kind: String { case paper, caseStudy }

    var slug: String
    var title: String
    var directory: URL
    var hasPDF: Bool
    var conceptGraph: URL?
    var animations: [URL]
    var exercises: [URL]
    var ideas: URL?
    /// What the learner typed to add it (an arXiv ID, DOI, link or title), when it wasn't a PDF.
    var source: String?
    var downloading = false
    var kind = Kind.paper
    /// A case study's numbered sources (sources.md).
    var sources: URL?

    var id: String { kind.rawValue + "/" + slug }
    /// Its concept map, animations and exercises have been built.
    var isLearned: Bool { conceptGraph != nil }

    var status: String {
        if downloading { return "downloading…" }
        if kind == .caseStudy && !isLearned { return "not built yet" }
        if !isLearned { return hasPDF || source != nil ? "not studied yet" : "no paper file" }
        var parts = ["concept map"]
        if !animations.isEmpty { parts.append("\(animations.count) animation\(animations.count == 1 ? "" : "s")") }
        if !exercises.isEmpty { parts.append("\(exercises.count) exercise\(exercises.count == 1 ? "" : "s")") }
        if ideas != nil { parts.append("ideas") }
        return parts.joined(separator: " · ")
    }
}

@MainActor
final class Library: ObservableObject {
    @Published private(set) var papers: [Paper] = []
    @Published var root: URL
    /// Folders whose paper is being downloaded right now.
    @Published private(set) var downloading: Set<String> = []

    /// The skill's downloader, from the install step's link in ~/.claude/skills.
    var fetchScript: URL {
        fm.homeDirectoryForCurrentUser.appendingPathComponent(".claude/skills/researcher-pal/scripts/fetch_paper.py")
    }

    enum FetchResult {
        case added(Paper)
        case failed(String)
    }

    private let fm = FileManager.default

    init() {
        root = fm.homeDirectoryForCurrentUser.appendingPathComponent("researcher-pal/papers")
        try? fm.createDirectory(at: root, withIntermediateDirectories: true)
        refresh()
    }

    var knowledgeGraph: URL {
        root.deletingLastPathComponent().appendingPathComponent("knowledge_graph.md")
    }

    /// Case studies of real incidents, next to the papers folder.
    var caseStudiesRoot: URL {
        root.deletingLastPathComponent().appendingPathComponent("case-studies")
    }

    func refresh() {
        let list = { (folder: URL) in (try? self.fm.contentsOfDirectory(at: folder, includingPropertiesForKeys: [.isDirectoryKey])) ?? [] }
        let all = list(root).compactMap { load($0) } + list(caseStudiesRoot).compactMap { load($0, kind: .caseStudy) }
        papers = all.sorted { $0.title.localizedCaseInsensitiveCompare($1.title) == .orderedAscending }
    }

    private func load(_ dir: URL, kind: Paper.Kind = .paper) -> Paper? {
        var isDir: ObjCBool = false
        guard fm.fileExists(atPath: dir.path, isDirectory: &isDir), isDir.boolValue,
              !dir.lastPathComponent.hasPrefix(".") else { return nil }
        let graph = dir.appendingPathComponent("concept_graph.md")
        let hasGraph = fm.fileExists(atPath: graph.path)
        let animations = (try? fm.contentsOfDirectory(at: dir.appendingPathComponent("animations"),
                                                      includingPropertiesForKeys: nil))?
            .filter { $0.pathExtension == "html" && !$0.lastPathComponent.hasPrefix("_") }
            .sorted { $0.lastPathComponent < $1.lastPathComponent } ?? []
        let exercises = (try? fm.contentsOfDirectory(at: dir.appendingPathComponent("exercises"),
                                                     includingPropertiesForKeys: nil))?
            .filter { $0.hasDirectoryPath && !$0.lastPathComponent.hasPrefix("_") }
            .sorted { $0.lastPathComponent < $1.lastPathComponent } ?? []
        let ideas = dir.appendingPathComponent("ideas/ideas.md")
        // .source holds what was typed; .arxiv is the older form, from before any link or title was accepted.
        let source = [".source", ".arxiv"].lazy
            .compactMap { try? String(contentsOf: dir.appendingPathComponent($0), encoding: .utf8) }
            .map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }.first
        let downloaded = (try? Data(contentsOf: dir.appendingPathComponent("source.json")))
            .flatMap { try? JSONSerialization.jsonObject(with: $0) as? [String: Any] }?["title"] as? String

        return Paper(
            slug: dir.lastPathComponent,
            title: title(graph: hasGraph ? graph : nil, slug: dir.lastPathComponent, downloaded: downloaded, source: source),
            directory: dir,
            hasPDF: fm.fileExists(atPath: dir.appendingPathComponent("paper.pdf").path),
            conceptGraph: hasGraph ? graph : nil,
            animations: animations,
            exercises: exercises,
            ideas: fm.fileExists(atPath: ideas.path) ? ideas : nil,
            source: source,
            downloading: downloading.contains(dir.lastPathComponent),
            kind: kind,
            sources: fm.fileExists(atPath: dir.appendingPathComponent("sources.md").path)
                ? dir.appendingPathComponent("sources.md") : nil
        )
    }

    /// The concept graph's first heading is the paper's real title; then the downloaded paper's; then what was typed.
    private func title(graph: URL?, slug: String, downloaded: String?, source: String?) -> String {
        if let graph, let text = try? String(contentsOf: graph, encoding: .utf8),
           let heading = text.split(separator: "\n").first(where: { $0.hasPrefix("# ") }) {
            var name = heading.dropFirst(2).trimmingCharacters(in: .whitespaces)
            for suffix in [": concept graph", " concept graph"] where name.lowercased().hasSuffix(suffix) {
                name = String(name.dropLast(suffix.count))
            }
            return name
        }
        if let downloaded, !downloaded.isEmpty { return downloaded }
        if let source { return Self.arxivID(from: source).map { "arXiv " + $0 } ?? source }
        return slug.replacingOccurrences(of: "-", with: " ").capitalized
    }

    // MARK: - adding papers

    /// A folder name for `name`: lowercase words joined by hyphens, at most 60 characters.
    static func baseSlug(_ name: String) -> String {
        // Cut to length first, then trim, so a cut that lands on a hyphen doesn't leave one at the end.
        return String(name.lowercased()
            .replacingOccurrences(of: "[^a-z0-9]+", with: "-", options: .regularExpression)
            .prefix(60))
            .trimmingCharacters(in: CharacterSet(charactersIn: "-"))
    }

    /// `baseSlug`, made unique among the folders that already exist.
    func slug(from name: String) -> String {
        let trimmed = Self.baseSlug(name)
        var candidate = trimmed.isEmpty ? "paper" : trimmed
        var n = 2
        while fm.fileExists(atPath: root.appendingPathComponent(candidate).path) {
            candidate = "\(trimmed)-\(n)"
            n += 1
        }
        return candidate
    }

    @discardableResult
    func addPDF(at url: URL) throws -> Paper {
        let name = url.deletingPathExtension().lastPathComponent
        let dir = root.appendingPathComponent(slug(from: name))
        try fm.createDirectory(at: dir, withIntermediateDirectories: true)
        try fm.copyItem(at: url, to: dir.appendingPathComponent("paper.pdf"))
        refresh()
        return paper(in: dir)
    }

    /// The paper in folder `dir`, matched by name (a listed folder's URL ends in "/", so URLs don't compare equal),
    /// or a placeholder if it isn't listed yet.
    private func paper(in dir: URL) -> Paper {
        papers.first { $0.kind == .paper && $0.slug == dir.lastPathComponent } ?? Paper(
            slug: dir.lastPathComponent, title: dir.lastPathComponent, directory: dir,
            hasPDF: fm.fileExists(atPath: dir.appendingPathComponent("paper.pdf").path), conceptGraph: nil,
            animations: [], exercises: [], ideas: nil)
    }

    /// Adds a paper from anything that identifies it: an arXiv ID or link, a DOI, a link to its page, or its title.
    /// The folder appears at once (as "downloading…"); `done` gets the paper once the skill's downloader has fetched
    /// an open-access copy, or the downloader's explanation when it couldn't (no open copy, or several papers
    /// matched a title), in which case the folder is removed again.
    func addReference(_ raw: String, done: @escaping (FetchResult) -> Void) throws -> Paper {
        let text = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        let name = Self.arxivID(from: text).map { "arxiv-" + $0 } ?? text
        let dir = root.appendingPathComponent(slug(from: name))
        try fm.createDirectory(at: dir, withIntermediateDirectories: true)
        try text.write(to: dir.appendingPathComponent(".source"), atomically: true, encoding: .utf8)
        guard fm.fileExists(atPath: fetchScript.path) else {
            // No downloader installed: the skill fetches the paper itself when it is studied.
            refresh()
            done(.added(paper(in: dir)))
            return paper(in: dir)
        }
        downloading.insert(dir.lastPathComponent)
        refresh()
        runFetch(text, into: dir) { [weak self] status, output in
            guard let self else { return }
            self.downloading.remove(dir.lastPathComponent)
            if status == 0 {
                done(.added(self.settle(dir)))
            } else {
                try? self.fm.removeItem(at: dir)
                self.refresh()
                done(.failed(Self.explanation(output, status: status)))
            }
        }
        return paper(in: dir)
    }

    /// After a download: rename the folder after the paper's real title (when it was named after an ID or link).
    private func settle(_ dir: URL) -> Paper {
        refresh()
        let paper = paper(in: dir)
        // Already named after the title (the learner typed it): leave it.
        guard !dir.lastPathComponent.hasPrefix(Self.baseSlug(paper.title)) else { return paper }
        let target = root.appendingPathComponent(slug(from: paper.title))
        guard (try? fm.moveItem(at: dir, to: target)) != nil else { return paper }
        refresh()
        return self.paper(in: target)
    }

    private func runFetch(_ text: String, into dir: URL, done: @escaping (Int32, String) -> Void) {
        // A login shell, so python3 is the same one Terminal finds.
        let quote = { (s: String) in "'" + s.replacingOccurrences(of: "'", with: "'\\''") + "'" }
        let task = Process()
        task.executableURL = URL(fileURLWithPath: "/bin/zsh")
        task.arguments = ["-lc", "exec python3 " + [fetchScript.path, text, "--out", dir.appendingPathComponent("paper.pdf").path]
            .map(quote).joined(separator: " ")]
        let pipe = Pipe()
        task.standardOutput = pipe
        task.standardError = pipe
        task.standardInput = FileHandle.nullDevice
        task.terminationHandler = { finished in
            let output = String(decoding: pipe.fileHandleForReading.readDataToEndOfFile(), as: UTF8.self)
            let status = finished.terminationStatus
            DispatchQueue.main.async { done(status, output) }
        }
        do {
            try task.run()
        } catch {
            DispatchQueue.main.async { done(-1, "Could not run python3: \(error.localizedDescription)") }
        }
    }

    /// The part of the downloader's report worth showing: candidates for an ambiguous title, otherwise the verdict
    /// and what was tried.
    static func explanation(_ output: String, status: Int32) -> String {
        let lines = output.split(separator: "\n", omittingEmptySubsequences: true).map(String.init)
            .filter { !$0.hasPrefix("Looking up") }
        if status == 4, let start = lines.firstIndex(where: { $0.contains("doesn't pick out one paper") }) {
            return lines[start...].joined(separator: "\n")
        }
        return lines.suffix(12).joined(separator: "\n")
    }

    static func arxivID(from text: String) -> String? {
        let patterns = [#"arxiv\.org/(?:abs|pdf)/([\w.\-/]+?)(?:v\d+)?(?:\.pdf)?$"#,
                        #"arxiv[:\s]+([\w.\-/]+)"#,
                        #"^\s*(\d{4}\.\d{4,5})(?:v\d+)?\s*$"#,
                        #"^\s*([a-z\-]+/\d{7})(?:v\d+)?\s*$"#]
        for pattern in patterns {
            if let match = text.range(of: pattern, options: [.regularExpression, .caseInsensitive]) {
                let hit = String(text[match])
                if let inner = hit.range(of: #"([\w.\-]+/\d{7}|\d{4}\.\d{4,5})"#, options: .regularExpression) {
                    return String(hit[inner])
                }
            }
        }
        return nil
    }

    func delete(_ paper: Paper) throws {
        try fm.trashItem(at: paper.directory, resultingItemURL: nil)
        refresh()
    }
}
