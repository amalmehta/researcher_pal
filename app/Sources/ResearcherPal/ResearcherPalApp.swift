import SwiftUI
import UniformTypeIdentifiers

@main
struct ResearcherPalApp: App {
    @StateObject private var library = Library()

    var body: some Scene {
        WindowGroup {
            ContentView().environmentObject(library)
        }
        .defaultSize(width: 1180, height: 760)
        .commands {
            CommandGroup(after: .newItem) {
                Button("Add Paper…") { NotificationCenter.default.post(name: .addPaper, object: nil) }
                    .keyboardShortcut("o")
                Button("Refresh Library") { library.refresh() }
                    .keyboardShortcut("r")
            }
        }
        Settings { SettingsView() }
    }
}

extension Notification.Name {
    static let addPaper = Notification.Name("addPaper")
}

// MARK: - main window

struct ContentView: View {
    @EnvironmentObject private var library: Library
    @StateObject private var runner = ClaudeRunner()
    @State private var selection: Paper.ID?
    @State private var referenceField = ""
    @State private var dropTargeted = false
    @State private var error: String?

    private var selected: Paper? { library.papers.first { $0.id == selection } }

    var body: some View {
        NavigationSplitView {
            sidebar
        } detail: {
            if selection == CareerView.selectionID {
                CareerView(runner: runner)
            } else if let selected {
                PaperView(paper: selected, runner: runner)
                    .id(selected.id)
            } else {
                EmptyLibraryView(dropTargeted: dropTargeted)
            }
        }
        .navigationTitle("Researcher Pal")
        .onDrop(of: [.fileURL, .url, .plainText], isTargeted: $dropTargeted) { providers in
            handleDrop(providers)
        }
        .onReceive(NotificationCenter.default.publisher(for: .addPaper)) { _ in openPanel() }
        .onReceive(Timer.publish(every: 4, on: .main, in: .common).autoconnect()) { _ in
            library.refresh()
        }
        .alert("Couldn't add that paper", isPresented: Binding(get: { error != nil }, set: { if !$0 { error = nil } })) {
            Button("OK", role: .cancel) { error = nil }
        } message: { Text(error ?? "") }
    }

    private var sidebar: some View {
        VStack(spacing: 0) {
            List(selection: $selection) {
                Section {
                    Label("Career fit", systemImage: "sparkles").tag(CareerView.selectionID)
                }
                Section("Papers") {
                    ForEach(library.papers.filter { $0.kind == .paper }, content: row)
                }
                if library.papers.contains(where: { $0.kind == .caseStudy }) {
                    Section("Case studies") {
                        ForEach(library.papers.filter { $0.kind == .caseStudy }, content: row)
                    }
                }
            }
            Divider()
            VStack(alignment: .leading, spacing: 8) {
                Text("Add a paper").font(.caption.weight(.semibold)).foregroundStyle(.secondary)
                HStack(spacing: 6) {
                    TextField("arXiv ID, DOI, link or title", text: $referenceField)
                        .textFieldStyle(.roundedBorder)
                        .onSubmit(addReference)
                    Button(action: addReference) {
                        Image(systemName: "arrow.down.circle.fill").font(.system(size: 18))
                    }
                    .buttonStyle(.borderless)
                    .disabled(referenceField.isEmpty)
                    .help("Download an open-access copy")
                }
                HStack(spacing: 4) {
                    Button("Choose a PDF…", action: openPanel).buttonStyle(.link)
                    Text("or drop one anywhere").foregroundStyle(.tertiary)
                }
                .font(.caption)
            }
            .padding(.horizontal, 14).padding(.vertical, 12)
        }
        .navigationSplitViewColumnWidth(min: 240, ideal: 280)
    }

    private func row(_ paper: Paper) -> some View {
        HStack(alignment: .top, spacing: 9) {
            Image(systemName: paper.kind == .caseStudy ? "exclamationmark.shield" : (paper.isLearned ? "doc.text.fill" : "doc.text"))
                .font(.system(size: 13))
                .foregroundStyle(paper.isLearned ? Color.accentColor : Color.secondary)
                .frame(width: 16)
                .padding(.top, 1)
            VStack(alignment: .leading, spacing: 3) {
                Text(paper.title)
                    .font(.system(size: 13, weight: .medium))
                    .lineLimit(3)
                    .fixedSize(horizontal: false, vertical: true)
                if paper.downloading {
                    Text("Downloading…").font(.caption).foregroundStyle(.secondary)
                } else if !paper.isLearned {
                    Text(paper.kind == .caseStudy ? "Not built yet" : "Not analyzed yet").font(.caption).foregroundStyle(.secondary)
                } else {
                    HStack(spacing: 10) {
                        if !paper.animations.isEmpty { Label("\(paper.animations.count)", systemImage: "play.rectangle") }
                        if !paper.exercises.isEmpty { Label("\(paper.exercises.count)", systemImage: "pencil.and.list.clipboard") }
                    }
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .labelStyle(CompactLabel())
                }
            }
        }
        .padding(.vertical, 4)
        .help(paper.title)
        .tag(paper.id)
        .contextMenu {
            Button("Show in Finder") { NSWorkspace.shared.activateFileViewerSelecting([paper.directory]) }
            Button("Move to Trash", role: .destructive) { try? library.delete(paper) }
        }
    }

    private func openPanel() {
        let panel = NSOpenPanel()
        panel.allowedContentTypes = [.pdf]
        panel.allowsMultipleSelection = true
        guard panel.runModal() == .OK else { return }
        for url in panel.urls { add { try library.addPDF(at: url) } }
    }

    private func addReference() {
        let text = referenceField.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty else { return }
        referenceField = ""
        addReference(text)
    }

    /// Selects the new paper at once (shown as downloading), then follows it if the folder is renamed after its
    /// title, or explains why there was nothing to download.
    private func addReference(_ text: String) {
        add {
            try library.addReference(text) { result in
                switch result {
                case .added(let paper): selection = paper.id
                case .failed(let why): error = why
                }
            }
        }
    }

    private func add(_ work: () throws -> Paper) {
        do {
            selection = try work().id
        } catch {
            self.error = error.localizedDescription
        }
    }

    private func handleDrop(_ providers: [NSItemProvider]) -> Bool {
        for provider in providers {
            if provider.hasItemConformingToTypeIdentifier(UTType.fileURL.identifier) {
                _ = provider.loadObject(ofClass: URL.self) { url, _ in
                    guard let url, url.pathExtension.lowercased() == "pdf" else { return }
                    Task { @MainActor in add { try library.addPDF(at: url) } }
                }
            } else {
                _ = provider.loadObject(ofClass: NSString.self) { text, _ in
                    // A dropped link or DOI (dropped plain text is too easy to drop by accident to treat as a title).
                    guard let text = (text as? String)?.trimmingCharacters(in: .whitespacesAndNewlines),
                          text.hasPrefix("http") || text.range(of: #"^(doi:\s*)?10\.\d{4,9}/\S+$"#, options: .regularExpression) != nil
                            || Library.arxivID(from: text) != nil else { return }
                    Task { @MainActor in addReference(text) }
                }
            }
        }
        return true
    }
}

struct EmptyLibraryView: View {
    let dropTargeted: Bool

    var body: some View {
        VStack(spacing: 14) {
            Image(systemName: dropTargeted ? "doc.fill.badge.plus" : "doc.text.magnifyingglass")
                .font(.system(size: 44))
                .foregroundStyle(.secondary)
            Text("Drop a paper in").font(.title2)
            Text("A PDF, or an arXiv ID, DOI, link or title. Researcher Pal builds a concept map, animations and\nexercises, then tutors you through them.")
                .multilineTextAlignment(.center)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(dropTargeted ? Color.accentColor.opacity(0.08) : Color.clear)
    }
}

/// An icon and a short value, close together (sidebar counts).
struct CompactLabel: LabelStyle {
    func makeBody(configuration: Configuration) -> some View {
        HStack(spacing: 3) { configuration.icon; configuration.title }
    }
}

// MARK: - one paper

struct PaperView: View {
    let paper: Paper
    @ObservedObject var runner: ClaudeRunner
    @EnvironmentObject private var library: Library
    @AppStorage("model") private var model = ClaudeRunner.defaultModel
    @AppStorage("permissionMode") private var permissionMode = "acceptEdits"
    @AppStorage("commands") private var commands = ClaudeRunner.CommandPolicy.ask.rawValue
    @AppStorage("maxBudgetUSD") private var maxBudget = 10.0
    @State private var tab = Tab.overview
    @State private var animation: URL?
    @State private var exercise: URL?
    @State private var replyText = ""
    @State private var exporting = false
    @State private var exportError: String?

    enum Tab: String, CaseIterable { case overview = "Overview", map = "Concept map", animations = "Animations", exercises = "Exercises", ideas = "Ideas", sources = "Sources" }

    /// A case study shows its sources where a paper shows its improvement ideas.
    private var tabs: [Tab] {
        paper.kind == .caseStudy ? [.overview, .map, .animations, .exercises, .sources] : [.overview, .map, .animations, .exercises, .ideas]
    }

    private var settings: ClaudeRunner.Settings {
        // The knowledge graph lives next to the papers folder and is shared by every paper.
        .init(model: model, permissionMode: permissionMode, commands: ClaudeRunner.CommandPolicy(rawValue: commands) ?? .ask,
              maxBudgetUSD: maxBudget, extraDirectories: [library.knowledgeGraph.deletingLastPathComponent()])
    }

    var body: some View {
        VStack(spacing: 0) {
            header
            Divider()
            content
        }
        .alert("Couldn't make the breakdown", isPresented: Binding(get: { exportError != nil }, set: { if !$0 { exportError = nil } })) {
            Button("OK", role: .cancel) { exportError = nil }
        } message: { Text(exportError ?? "") }
    }

    private var header: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack(alignment: .top, spacing: 18) {
                VStack(alignment: .leading, spacing: 5) {
                    Text(paper.kind == .caseStudy ? "CASE STUDY" : "PAPER")
                        .font(.caption2.weight(.semibold)).tracking(1).foregroundStyle(.secondary)
                    Text(paper.title)
                        .font(.system(size: 22, weight: .semibold, design: .serif))
                        .lineLimit(3)
                        .fixedSize(horizontal: false, vertical: true)
                        .textSelection(.enabled)
                    Text(details).font(.callout).foregroundStyle(.secondary)
                }
                Spacer(minLength: 12)
                actions
            }
            Picker("", selection: $tab) {
                ForEach(tabs, id: \.self) { Text($0.rawValue).tag($0) }
            }
            .pickerStyle(.segmented)
            .labelsHidden()
            .fixedSize()
        }
        .padding(.horizontal, 22).padding(.top, 18).padding(.bottom, 14)
    }

    /// "arXiv 2511.14759 · 4 animations · 9 exercises", or what's still to do.
    private var details: String {
        var parts: [String] = []
        if let origin = paper.origin { parts.append(origin) }
        if paper.downloading { parts.append("downloading…") }
        else if !paper.isLearned { parts.append(paper.kind == .caseStudy ? "not built yet" : "not analyzed yet") }
        else {
            parts.append("concept map")
            if !paper.animations.isEmpty { parts.append("\(paper.animations.count) animation\(paper.animations.count == 1 ? "" : "s")") }
            if !paper.exercises.isEmpty { parts.append("\(paper.exercises.count) exercise\(paper.exercises.count == 1 ? "" : "s")") }
        }
        return parts.joined(separator: " · ")
    }

    /// One prominent next step, the PDF, and everything else under More.
    @ViewBuilder private var actions: some View {
        HStack(spacing: 8) {
            if runner.isRunning {
                ProgressView().controlSize(.small)
                Button("Stop", role: .destructive) { runner.stop() }
            } else {
                // Built material is reused, never rebuilt: the tutor starts from what is already there.
                if paper.isLearned {
                    Button { tutor() } label: { Label("Learn with a tutor", systemImage: "graduationcap") }
                        .buttonStyle(.borderedProminent)
                } else if paper.kind == .paper {
                    Button { analyze() } label: { Label("Analyze this paper", systemImage: "sparkles") }
                        .buttonStyle(.borderedProminent)
                }
                if paper.isLearned {
                    if exporting {
                        ProgressView().controlSize(.small).padding(.horizontal, 8)
                    } else {
                        Button { download() } label: { Label("Download PDF", systemImage: "arrow.down.doc") }
                            .help("Save the whole analysis as one PDF: summary, map, concepts, key animation frames and exercises (no solutions)")
                    }
                }
                Menu {
                    if paper.kind == .paper {
                        Button("Suggest improvements") { improve() }.disabled(!paper.isLearned)
                    }
                    if paper.hasPDF {
                        Button("Open the paper's PDF") { NSWorkspace.shared.open(paper.directory.appendingPathComponent("paper.pdf")) }
                    }
                    Button("Show in Finder") { NSWorkspace.shared.activateFileViewerSelecting([paper.directory]) }
                } label: {
                    Label("More", systemImage: "ellipsis.circle")
                }
                .menuStyle(.borderlessButton)
                .fixedSize()
            }
        }
        .controlSize(.large)
    }

    @ViewBuilder private var content: some View {
        switch tab {
        case .overview:
            if paper.kind == .paper && !paper.isLearned && runner.items.isEmpty && !runner.isRunning {
                analyzePrompt
            } else if paper.isLearned && runner.items.isEmpty && !runner.isRunning, let summary = overviewPage() {
                WebPane(fileURL: summary, readAccess: paper.directory).id(summary)
            } else {
                RunPane(runner: runner, directory: paper.directory, replyText: $replyText, settings: settings)
            }
        case .map:
            WebPane(fileURL: paper.conceptGraph, readAccess: paper.directory)
        case .animations:
            animationViewer
        case .exercises:
            exerciseViewer
        case .ideas:
            WebPane(fileURL: paper.ideas, readAccess: paper.directory)
        case .sources:
            WebPane(fileURL: paper.sources, readAccess: paper.directory)
        }
    }

    /// The landing page of an analyzed paper: its summary from the concept graph, and where to go next. Written
    /// next to the material (like the other rendered pages) and refreshed each time it's shown.
    private func overviewPage() -> URL? {
        guard let graph = paper.conceptGraph, let text = try? String(contentsOf: graph, encoding: .utf8) else { return nil }
        // The first "## " section is the paper's summary ("The paper in five lines"); the "> **Source:**" quote
        // above it says which version the material follows.
        let parts = text.components(separatedBy: "\n## ")
        let intro = parts.first ?? ""
        let source = intro.split(separator: "\n", omittingEmptySubsequences: false)
            .drop { !$0.hasPrefix(">") }.prefix { $0.hasPrefix(">") }.joined(separator: "\n")
        let summary = parts.count > 1 ? "## " + parts[1] : ""
        var page = ["# \(paper.title)", "", source, "", summary, "", "## Where to go next", ""]
        page.append("- **Concept map:** every idea and equation, as a map of cards; click one to see what it builds on.")
        if !paper.animations.isEmpty {
            page.append("- **Animations:** \(paper.animations.count) interactive ones; drag the sliders to see what changes.")
        }
        if !paper.exercises.isEmpty {
            page.append("- **Exercises:** \(paper.exercises.count), in order, each building on the last.")
        }
        page.append("- **Learn with a tutor** (top right) walks you through it one exercise at a time, starting from what you already know.")
        page.append("- **Download PDF** saves the whole breakdown, typeset, with key frames from the animations.")
        let out = paper.directory.appendingPathComponent(".rp-overview.md")
        guard (try? page.joined(separator: "\n").write(to: out, atomically: true, encoding: .utf8)) != nil else { return nil }
        return out
    }

    private var nothingYet: some View {
        ContentUnavailableView("Nothing here yet", systemImage: "tray",
                               description: Text(paper.kind == .paper ? "Press “Analyze this paper” first." : "This case study hasn't been built yet."))
    }

    /// One animation at a time, full width, chosen by its real title.
    @ViewBuilder private var animationViewer: some View {
        let items = paper.animations
        if items.isEmpty {
            nothingYet
        } else {
            let current = animation.flatMap { items.contains($0) ? $0 : nil } ?? items[0]
            let index = items.firstIndex(of: current) ?? 0
            VStack(spacing: 0) {
                HStack(spacing: 10) {
                    Picker("", selection: Binding(get: { current }, set: { animation = $0 })) {
                        ForEach(items, id: \.self) { Text(Self.title(ofAnimation: $0)).tag($0) }
                    }
                    .labelsHidden()
                    .fixedSize()
                    Spacer()
                    Button { animation = items[index - 1] } label: { Image(systemName: "chevron.left") }
                        .disabled(index == 0)
                    Text("\(index + 1) of \(items.count)").font(.callout.monospacedDigit()).foregroundStyle(.secondary)
                    Button { animation = items[index + 1] } label: { Image(systemName: "chevron.right") }
                        .disabled(index + 1 == items.count)
                }
                .padding(.horizontal, 22).padding(.vertical, 8)
                Divider()
                WebPane(fileURL: current, readAccess: paper.directory).id(current)
            }
        }
    }

    /// The exercises in order, by their real titles; the first one is open from the start.
    @ViewBuilder private var exerciseViewer: some View {
        let items = paper.exercises.map { $0.appendingPathComponent("README.md") }
        if items.isEmpty {
            nothingYet
        } else {
            let current = exercise.flatMap { items.contains($0) ? $0 : nil } ?? items[0]
            HSplitView {
                List(items, id: \.self, selection: Binding(get: { current }, set: { exercise = $0 })) { item in
                    Text(Self.title(ofExercise: item)).lineLimit(2).padding(.vertical, 3).tag(item as URL?)
                }
                .frame(minWidth: 200, idealWidth: 250, maxWidth: 340)
                WebPane(fileURL: current, readAccess: paper.directory).id(current)
                    .frame(minWidth: 420)
            }
        }
    }

    /// An animation's own <title>, without the " · researcher-pal" suffix.
    static func title(ofAnimation url: URL) -> String {
        if let html = try? String(contentsOf: url, encoding: .utf8),
           let range = html.range(of: #"<title>[^<]*</title>"#, options: .regularExpression) {
            let title = html[range].replacingOccurrences(of: #"</?title>"#, with: "", options: .regularExpression)
                .replacingOccurrences(of: " · researcher-pal", with: "").trimmingCharacters(in: .whitespaces)
            if !title.isEmpty { return title }
        }
        return url.deletingPathExtension().lastPathComponent.replacingOccurrences(of: "_", with: " ").capitalized
    }

    /// An exercise README's first heading ("01 · Sparse success reward").
    static func title(ofExercise readme: URL) -> String {
        if let text = try? String(contentsOf: readme, encoding: .utf8),
           let heading = text.split(separator: "\n").first(where: { $0.hasPrefix("# ") }) {
            return heading.dropFirst(2).trimmingCharacters(in: .whitespaces)
        }
        return readme.deletingLastPathComponent().lastPathComponent.replacingOccurrences(of: "_", with: " ")
    }

    private func download() {
        let panel = NSSavePanel()
        panel.allowedContentTypes = [.pdf]
        panel.canCreateDirectories = true
        panel.directoryURL = FileManager.default.urls(for: .downloadsDirectory, in: .userDomainMask).first
        let safeTitle = paper.title.replacingOccurrences(of: "[/:]", with: "-", options: .regularExpression)
        panel.nameFieldStringValue = "\(safeTitle) - breakdown.pdf"
        guard panel.runModal() == .OK, let url = panel.url else { return }
        exporting = true
        Breakdown.export(paper, to: url) { result in
            exporting = false
            switch result {
            case .success(let pdf): NSWorkspace.shared.open(pdf)
            case .failure(let error): exportError = error.localizedDescription
            }
        }
    }

    /// The first thing to do with a new paper: one button, shown big until the material exists.
    private var analyzePrompt: some View {
        VStack(spacing: 14) {
            Image(systemName: "sparkles.rectangle.stack").font(.system(size: 40)).foregroundStyle(.secondary)
            Text("Analyze this paper").font(.title2.weight(.semibold))
            Text("""
            Builds a concept map of every idea and equation, interactive animations of the key ones, and exercises \
            that rebuild the method, all checked before you see them. It runs on its own without asking you \
            questions; when it's done, press “Learn with a tutor” to work through it.
            """)
                .multilineTextAlignment(.center).foregroundStyle(.secondary).frame(maxWidth: 520)
            Button { analyze() } label: { Text("Analyze this paper").padding(.horizontal, 10).padding(.vertical, 4) }
                .buttonStyle(.borderedProminent).controlSize(.large)
            Text("A long paper can take a while and costs more than a tutoring turn. The model is set in Settings.")
                .font(.caption).foregroundStyle(.tertiary)
        }
        .padding(30)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }

    /// Builds the paper's material in one go, the way the library papers were built: no pause for questions and no
    /// tutoring (that's "Learn with a tutor", afterwards), and done only when the skill's checker passes.
    private func analyze() {
        // The downloaded or dropped PDF when there is one; otherwise what was typed, for the skill to fetch.
        let target = paper.hasPDF ? paper.directory.appendingPathComponent("paper.pdf").path : (paper.source ?? "this paper")
        let provenance = FileManager.default.fileExists(atPath: paper.directory.appendingPathComponent("source.json").path)
            ? " The PDF was downloaded; source.json beside it says from where, with the arXiv ID and LaTeX source link if it has them."
            : ""
        runner.start(prompt: """
        Use the researcher-pal skill to analyze \(target) and build its learning material in \(paper.directory.path) \
        (papers/<slug> is this folder itself, so write concept_graph.md, animations/ and exercises/ directly in it).\
        \(provenance) Do steps 1-4, 6 and 8. Don't stop at step 5 to ask me anything: assume I know nothing yet and \
        want the whole paper. Skip step 7; I'll start learning afterwards with "Learn with a tutor". It's done when \
        the skill's check_learning.py reports no FAIL. Then tell me in a few lines what you built and anything I \
        should know about the paper.
        """, label: "Analyze this paper", in: paper.directory, settings: settings)
    }

    private func tutor() {
        let what = paper.kind == .caseStudy
            ? "the case study in \(paper.directory.path). It's a real incident: sources.md lists its sources, and the facts must stay within them."
            : "the paper in \(paper.directory.path)."
        runner.start(prompt: """
        Use the researcher-pal skill to tutor me on \(what) Its material is already built and checked: concept_graph.md, \
        animations/, and exercises/ with hidden reference solutions in .solutions/. Don't rebuild or rewrite any of it. \
        Start at step 5: show me the overview, ask what I already know and where I want to start, then run the tutor \
        loop (step 7) one exercise at a time, recording what I learn in the knowledge graph.
        """, label: "Learn with a tutor", in: paper.directory, settings: settings)
    }

    private func improve() {
        runner.start(prompt: """
        Suggest improvements for the paper in \(paper.directory.path), in learned-paper mode. Write the report \
        to \(paper.directory.path)/ideas/ideas.md. Stop at the ranked list and ask me before applying or running anything.
        """, label: "Suggest improvements", in: paper.directory, settings: settings)
    }
}

// MARK: - the run transcript

struct RunPane: View {
    @ObservedObject var runner: ClaudeRunner
    let directory: URL
    var emptyHint = "Press “Learn with a tutor” to begin. The conversation appears here, and you answer in the box below."
    @Binding var replyText: String
    let settings: ClaudeRunner.Settings

    var body: some View {
        VStack(spacing: 0) {
            if runner.needsLogin { loginBanner }
            TranscriptView(items: runner.items, emptyHint: emptyHint)
            ForEach(runner.permissionRequests) { request in
                PermissionCard(request: request) { runner.answer(request, $0) }
            }
            Divider()
            HStack(spacing: 8) {
                TextField(runner.canReply ? "Answer Claude…" : "Start a run first", text: $replyText)
                    .textFieldStyle(.roundedBorder)
                    .disabled(!runner.canReply)
                    .onSubmit(send)
                Button("Send", action: send).disabled(!runner.canReply || replyText.isEmpty)
                if runner.costUSD > 0 {
                    Text(String(format: "$%.2f", runner.costUSD))
                        .font(.caption.monospacedDigit()).foregroundStyle(.secondary)
                }
            }
            .padding(10)
        }
    }

    private var loginBanner: some View {
        HStack(spacing: 10) {
            Image(systemName: "exclamationmark.triangle.fill").foregroundStyle(.orange)
            VStack(alignment: .leading, spacing: 2) {
                Text("Not logged in").font(.callout.weight(.medium))
                Text("Run `claude` in Terminal, type /login, finish in the browser, then try again.")
                    .font(.caption).foregroundStyle(.secondary)
            }
            Spacer()
            Button("Open Terminal") {
                NSWorkspace.shared.open(URL(fileURLWithPath: "/System/Applications/Utilities/Terminal.app"))
            }
        }
        .padding(10)
        .background(Color.orange.opacity(0.14))
    }

    private func send() {
        guard runner.canReply, !replyText.isEmpty else { return }
        runner.reply(replyText, in: directory, settings: settings)
        replyText = ""
    }
}

/// The assistant is waiting: it wants to run a command or touch a file, and the user decides.
struct PermissionCard: View {
    let request: ClaudeRunner.PermissionRequest
    let decide: (ClaudeRunner.Decision) -> Void

    var body: some View {
        HStack(alignment: .top, spacing: 10) {
            Image(systemName: "hand.raised.fill").foregroundStyle(.orange)
            VStack(alignment: .leading, spacing: 6) {
                Text(request.title).font(.callout.weight(.medium))
                Text(request.summary)
                    .font(.system(.callout, design: .monospaced))
                    .lineLimit(6)
                    .textSelection(.enabled)
                if let detail = request.detail {
                    Text(detail).font(.caption).foregroundStyle(.secondary)
                }
                HStack {
                    Button("Allow") { decide(.allow) }.buttonStyle(.borderedProminent)
                    Button("Allow all") { decide(.allowAll) }
                        .help("Allow this and everything else the assistant asks for in this conversation")
                    Button("Deny", role: .destructive) { decide(.deny) }
                }
                .controlSize(.small)
            }
            Spacer(minLength: 0)
        }
        .padding(10)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.orange.opacity(0.10))
    }
}

// MARK: - settings

struct SettingsView: View {
    @AppStorage("model") private var model = ClaudeRunner.defaultModel
    @AppStorage("permissionMode") private var permissionMode = "acceptEdits"
    @AppStorage("commands") private var commands = ClaudeRunner.CommandPolicy.ask.rawValue
    @AppStorage("maxBudgetUSD") private var maxBudget = 10.0

    var body: some View {
        Form {
            Picker("Model", selection: $model) {
                Text("Sonnet (default: fast, about a fifth of Opus's price)").tag("sonnet")
                Text("Opus (most capable, for the hardest papers)").tag("opus")
            }
            Picker("File changes", selection: $permissionMode) {
                Text("Write files without asking").tag("acceptEdits")
                Text("Ask every time").tag("default")
            }
            Picker("Commands", selection: $commands) {
                Text("Ask me each time").tag(ClaudeRunner.CommandPolicy.ask.rawValue)
                Text("Run without asking").tag(ClaudeRunner.CommandPolicy.always.rawValue)
                Text("Never").tag(ClaudeRunner.CommandPolicy.never.rawValue)
            }
            Text("Studying a paper runs commands: downloading it, reading its text, and testing the exercises.")
                .font(.caption).foregroundStyle(.secondary)
            HStack {
                Text("Stop a run at")
                TextField("", value: $maxBudget, format: .currency(code: "USD")).frame(width: 90)
            }
            Text("Runs use the Claude Code login already on this Mac, so there is no API key to set.")
                .font(.caption).foregroundStyle(.secondary)
        }
        .padding(20)
        .frame(width: 460)
    }
}
