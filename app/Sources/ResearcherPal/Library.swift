import Foundation

/// One paper in the library, laid out the way the researcher-pal skill expects:
/// ~/researcher-pal/papers/<slug>/{paper.pdf, concept_graph.md, animations/, exercises/, ideas/}
struct Paper: Identifiable, Hashable {
    var slug: String
    var title: String
    var directory: URL
    var hasPDF: Bool
    var conceptGraph: URL?
    var animations: [URL]
    var exercises: [URL]
    var ideas: URL?
    var arxivID: String?

    var id: String { slug }
    var isLearned: Bool { conceptGraph != nil }

    var status: String {
        if !isLearned { return hasPDF || arxivID != nil ? "not studied yet" : "no paper file" }
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

    private let fm = FileManager.default

    init() {
        root = fm.homeDirectoryForCurrentUser.appendingPathComponent("researcher-pal/papers")
        try? fm.createDirectory(at: root, withIntermediateDirectories: true)
        refresh()
    }

    var knowledgeGraph: URL {
        root.deletingLastPathComponent().appendingPathComponent("knowledge_graph.md")
    }

    func refresh() {
        let dirs = (try? fm.contentsOfDirectory(at: root, includingPropertiesForKeys: [.isDirectoryKey])) ?? []
        papers = dirs.compactMap(load).sorted { $0.title.localizedCaseInsensitiveCompare($1.title) == .orderedAscending }
    }

    private func load(_ dir: URL) -> Paper? {
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
        let arxiv = try? String(contentsOf: dir.appendingPathComponent(".arxiv"), encoding: .utf8)

        return Paper(
            slug: dir.lastPathComponent,
            title: title(graph: hasGraph ? graph : nil, slug: dir.lastPathComponent),
            directory: dir,
            hasPDF: fm.fileExists(atPath: dir.appendingPathComponent("paper.pdf").path),
            conceptGraph: hasGraph ? graph : nil,
            animations: animations,
            exercises: exercises,
            ideas: fm.fileExists(atPath: ideas.path) ? ideas : nil,
            arxivID: arxiv?.trimmingCharacters(in: .whitespacesAndNewlines)
        )
    }

    /// The concept graph's first heading is the paper's real title; fall back to the folder name.
    private func title(graph: URL?, slug: String) -> String {
        if let graph, let text = try? String(contentsOf: graph, encoding: .utf8),
           let heading = text.split(separator: "\n").first(where: { $0.hasPrefix("# ") }) {
            var name = heading.dropFirst(2).trimmingCharacters(in: .whitespaces)
            for suffix in [": concept graph", " concept graph"] where name.lowercased().hasSuffix(suffix) {
                name = String(name.dropLast(suffix.count))
            }
            return name
        }
        return slug.replacingOccurrences(of: "-", with: " ").capitalized
    }

    // MARK: - adding papers

    func slug(from name: String) -> String {
        let base = name.lowercased()
            .replacingOccurrences(of: "[^a-z0-9]+", with: "-", options: .regularExpression)
            .trimmingCharacters(in: CharacterSet(charactersIn: "-"))
        let trimmed = String(base.prefix(60))
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
        return papers.first { $0.directory == dir } ?? Paper(slug: dir.lastPathComponent, title: name,
                                                             directory: dir, hasPDF: true, conceptGraph: nil,
                                                             animations: [], exercises: [], ideas: nil, arxivID: nil)
    }

    /// Accepts "1706.03762", "arXiv:1706.03762", or any arxiv.org URL.
    @discardableResult
    func addArxiv(_ raw: String) throws -> Paper {
        let id = Self.arxivID(from: raw) ?? raw.trimmingCharacters(in: .whitespacesAndNewlines)
        let dir = root.appendingPathComponent(slug(from: "arxiv-" + id))
        try fm.createDirectory(at: dir, withIntermediateDirectories: true)
        try id.write(to: dir.appendingPathComponent(".arxiv"), atomically: true, encoding: .utf8)
        refresh()
        return papers.first { $0.directory == dir } ?? Paper(slug: dir.lastPathComponent, title: "arXiv " + id,
                                                             directory: dir, hasPDF: false, conceptGraph: nil,
                                                             animations: [], exercises: [], ideas: nil, arxivID: id)
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
