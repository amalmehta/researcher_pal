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
    @State private var arxivField = ""
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
        .alert("Could not add that", isPresented: Binding(get: { error != nil }, set: { if !$0 { error = nil } })) {
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
                    TextField("arXiv ID or link", text: $arxivField)
                        .textFieldStyle(.roundedBorder)
                        .onSubmit(addArxiv)
                    Button("Add", action: addArxiv).disabled(arxivField.isEmpty)
                }
                Text("or drop a PDF anywhere in this window")
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

    private func addArxiv() {
        let text = arxivField
        guard !text.isEmpty else { return }
        add { try library.addArxiv(text) }
        arxivField = ""
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
                    guard let text = text as? String, Library.arxivID(from: text) != nil else { return }
                    Task { @MainActor in add { try library.addArxiv(text) } }
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
    @AppStorage("allowCommands") private var allowCommands = true
    @AppStorage("maxBudgetUSD") private var maxBudget = 10.0
    @State private var tab = Tab.overview
    @State private var animation: URL?
    @State private var exercise: URL?
    @State private var replyText = ""

    enum Tab: String, CaseIterable { case overview = "Overview", map = "Concept map", animations = "Animations", exercises = "Exercises", ideas = "Ideas" }

    private var settings: ClaudeRunner.Settings {
        .init(model: model, permissionMode: permissionMode, allowCommands: allowCommands, maxBudgetUSD: maxBudget)
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
        let target = paper.arxivID.map { "arXiv \($0)" } ?? paper.directory.appendingPathComponent("paper.pdf").path
        runner.start(prompt: """
        Help me learn \(target). Work inside \(paper.directory.path): put the concept graph, animations and \
        exercises there (papers/<slug> is this folder itself, so write concept_graph.md, animations/ and \
        exercises/ directly in it). Pause where the skill says to pause and ask me.
        """, in: paper.directory, settings: settings)
    }

    private func improve() {
        runner.start(prompt: """
        Suggest improvements for the paper in \(paper.directory.path), in learned-paper mode. Write the report \
        to \(paper.directory.path)/ideas/ideas.md. Stop at the ranked list and ask me before applying or running anything.
        """, in: paper.directory, settings: settings)
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
            Text("Claude Code is not logged in. Open Terminal, run `claude`, then `/login`, and try again.")
                .font(.callout)
            Spacer()
        }
        .padding(10)
        .background(Color.orange.opacity(0.12))
    }

    @ViewBuilder private func row(_ item: ClaudeRunner.Item) -> some View {
        switch item.kind {
        case .user:
            label(item.text, icon: "person.fill", color: .accentColor)
        case .assistant:
            Text(item.text).textSelection(.enabled)
        case .tool:
            label(item.text, icon: "wrench.and.screwdriver", color: .secondary)
        case .result:
            label(item.text, icon: "checkmark.circle", color: .green)
        case .error:
            label(item.text, icon: "xmark.octagon", color: .red)
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

// MARK: - settings

struct SettingsView: View {
    @AppStorage("model") private var model = "opus"
    @AppStorage("permissionMode") private var permissionMode = "acceptEdits"
    @AppStorage("allowCommands") private var allowCommands = true
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
            Toggle("Let it run commands (needed for coded exercises)", isOn: $allowCommands)
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
