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
            if let selected {
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
                Section("Papers") {
                    ForEach(library.papers) { paper in
                        VStack(alignment: .leading, spacing: 2) {
                            Text(paper.title).lineLimit(2)
                            Text(paper.status).font(.caption).foregroundStyle(.secondary)
                        }
                        .padding(.vertical, 2)
                        .tag(paper.id)
                        .contextMenu {
                            Button("Show in Finder") { NSWorkspace.shared.activateFileViewerSelecting([paper.directory]) }
                            Button("Move to Trash", role: .destructive) { try? library.delete(paper) }
                        }
                    }
                }
            }
            Divider()
            VStack(alignment: .leading, spacing: 8) {
                Button {
                    openPanel()
                } label: {
                    Label("Add PDF…", systemImage: "doc.badge.plus").frame(maxWidth: .infinity)
                }
                HStack(spacing: 6) {
                    TextField("arXiv ID, DOI, link or title", text: $referenceField)
                        .textFieldStyle(.roundedBorder)
                        .onSubmit(addReference)
                    Button("Add", action: addReference).disabled(referenceField.isEmpty)
                }
                Text("Downloads an open-access copy. Or drop a PDF anywhere in this window.")
                    .font(.caption2).foregroundStyle(.secondary)
            }
            .padding(12)
        }
        .navigationSplitViewColumnWidth(min: 240, ideal: 280)
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
            Text("A PDF, or an arXiv link. Researcher Pal builds a concept map, animations and exercises,\nthen suggests what would make the paper stronger.")
                .multilineTextAlignment(.center)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(dropTargeted ? Color.accentColor.opacity(0.08) : Color.clear)
    }
}

// MARK: - one paper

struct PaperView: View {
    let paper: Paper
    @ObservedObject var runner: ClaudeRunner
    @EnvironmentObject private var library: Library
    @AppStorage("model") private var model = "opus"
    @AppStorage("permissionMode") private var permissionMode = "acceptEdits"
    @AppStorage("commands") private var commands = ClaudeRunner.CommandPolicy.ask.rawValue
    @AppStorage("maxBudgetUSD") private var maxBudget = 10.0
    @State private var tab = Tab.overview
    @State private var animation: URL?
    @State private var exercise: URL?
    @State private var replyText = ""

    enum Tab: String, CaseIterable { case overview = "Overview", map = "Concept map", animations = "Animations", exercises = "Exercises", ideas = "Ideas" }

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
    }

    private var header: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(alignment: .firstTextBaseline) {
                VStack(alignment: .leading, spacing: 2) {
                    Text(paper.title).font(.title2).lineLimit(2)
                    Text(paper.status).font(.caption).foregroundStyle(.secondary)
                }
                Spacer()
                if runner.isRunning {
                    ProgressView().controlSize(.small)
                    Button("Stop", role: .destructive) { runner.stop() }
                } else {
                    Button(paper.isLearned ? "Study again" : "Study this paper") { study() }
                        .buttonStyle(.borderedProminent)
                    Button("Suggest improvements") { improve() }
                        .disabled(!paper.isLearned)
                }
            }
            Picker("", selection: $tab) {
                ForEach(Tab.allCases, id: \.self) { Text($0.rawValue).tag($0) }
            }
            .pickerStyle(.segmented)
            .labelsHidden()
        }
        .padding(14)
    }

    @ViewBuilder private var content: some View {
        switch tab {
        case .overview:
            RunPane(runner: runner, paper: paper, replyText: $replyText, settings: settings)
        case .map:
            WebPane(fileURL: paper.conceptGraph, readAccess: paper.directory)
        case .animations:
            picker(items: paper.animations, selection: $animation, label: { $0.deletingPathExtension().lastPathComponent })
        case .exercises:
            picker(items: paper.exercises.map { $0.appendingPathComponent("README.md") },
                   selection: $exercise,
                   label: { $0.deletingLastPathComponent().lastPathComponent })
        case .ideas:
            WebPane(fileURL: paper.ideas, readAccess: paper.directory)
        }
    }

    @ViewBuilder
    private func picker(items: [URL], selection: Binding<URL?>, label: @escaping (URL) -> String) -> some View {
        if items.isEmpty {
            ContentUnavailableView("Nothing here yet", systemImage: "tray",
                                   description: Text("Run “Study this paper” first."))
        } else {
            HSplitView {
                List(items, id: \.self, selection: selection) { item in
                    Text(label(item).replacingOccurrences(of: "_", with: " "))
                        .tag(item as URL?)
                }
                .frame(minWidth: 180, idealWidth: 220, maxWidth: 320)
                WebPane(fileURL: selection.wrappedValue ?? items.first, readAccess: paper.directory)
                    .frame(minWidth: 400)
            }
        }
    }

    private func study() {
        // The downloaded or dropped PDF when there is one; otherwise what was typed, for the skill to fetch.
        let target = paper.hasPDF ? paper.directory.appendingPathComponent("paper.pdf").path : (paper.source ?? "this paper")
        let provenance = FileManager.default.fileExists(atPath: paper.directory.appendingPathComponent("source.json").path)
            ? " The PDF was downloaded; source.json beside it says from where, with the arXiv ID and LaTeX source link if it has them."
            : ""
        runner.start(prompt: """
        Help me learn \(target). Work inside \(paper.directory.path): put the concept graph, animations and \
        exercises there (papers/<slug> is this folder itself, so write concept_graph.md, animations/ and \
        exercises/ directly in it).\(provenance) Pause where the skill says to pause and ask me.
        """, label: "Study this paper", in: paper.directory, settings: settings)
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
    let paper: Paper
    @Binding var replyText: String
    let settings: ClaudeRunner.Settings

    var body: some View {
        VStack(spacing: 0) {
            if runner.needsLogin { loginBanner }
            ScrollViewReader { proxy in
                ScrollView {
                    LazyVStack(alignment: .leading, spacing: 10) {
                        if runner.items.isEmpty {
                            Text("Press “Study this paper” to begin. What Claude does appears here, and you can answer when it asks.")
                                .foregroundStyle(.secondary)
                                .padding(.top, 8)
                        }
                        ForEach(runner.items) { item in
                            row(item).id(item.id)
                        }
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(14)
                }
                .onChange(of: runner.items.count) {
                    if let last = runner.items.last { proxy.scrollTo(last.id, anchor: .bottom) }
                }
            }
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

    @ViewBuilder private func row(_ item: ClaudeRunner.Item) -> some View {
        switch item.kind {
        case .user:
            label(item.shown, icon: "person.fill", color: .accentColor)
        case .assistant:
            Text(item.shown).textSelection(.enabled)
        case .tool:
            label(item.shown, icon: "wrench.and.screwdriver", color: .secondary)
        case .result:
            label(item.shown, icon: "checkmark.circle", color: .green)
        case .error:
            label(item.shown, icon: "xmark.octagon", color: .red)
        }
    }

    private func label(_ text: String, icon: String, color: Color) -> some View {
        HStack(alignment: .top, spacing: 6) {
            Image(systemName: icon).foregroundStyle(color).font(.caption)
            Text(text).font(.callout).foregroundStyle(color == .secondary ? .secondary : .primary)
                .textSelection(.enabled)
        }
    }

    private func send() {
        guard runner.canReply, !replyText.isEmpty else { return }
        runner.reply(replyText, in: paper.directory, settings: settings)
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
    @AppStorage("model") private var model = "opus"
    @AppStorage("permissionMode") private var permissionMode = "acceptEdits"
    @AppStorage("commands") private var commands = ClaudeRunner.CommandPolicy.ask.rawValue
    @AppStorage("maxBudgetUSD") private var maxBudget = 10.0

    var body: some View {
        Form {
            Picker("Model", selection: $model) {
                Text("Opus (most capable)").tag("opus")
                Text("Sonnet (cheaper)").tag("sonnet")
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
