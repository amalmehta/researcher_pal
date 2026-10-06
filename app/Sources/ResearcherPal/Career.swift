import SwiftUI

/// "Where would I thrive?": the companies and roles you'd love and your best fit (ikigai), made by the career-fit skill
/// from your library and a short profile you write here. Lives in ~/researcher-pal/{profile.md, career/careers.md}.
struct CareerView: View {
    static let selectionID = "career"

    @ObservedObject var runner: ClaudeRunner
    @EnvironmentObject private var library: Library
    @AppStorage("model") private var model = "opus"
    @AppStorage("permissionMode") private var permissionMode = "acceptEdits"
    @AppStorage("commands") private var commands = ClaudeRunner.CommandPolicy.ask.rawValue
    @AppStorage("maxBudgetUSD") private var maxBudget = 10.0
    @State private var tab = Tab.fit
    @State private var profile = ""
    @State private var savedProfile = ""
    @State private var replyText = ""

    enum Tab: String, CaseIterable { case fit = "Best fit", profile = "About me", run = "Run" }

    private var home: URL { library.root.deletingLastPathComponent() }
    private var profileURL: URL { home.appendingPathComponent("profile.md") }
    private var folder: URL { home.appendingPathComponent("career") }
    private var report: URL { folder.appendingPathComponent("careers.md") }

    private var settings: ClaudeRunner.Settings {
        // Reads the whole library (papers, case studies, knowledge graph); writes only into career/.
        .init(model: model, permissionMode: permissionMode, commands: ClaudeRunner.CommandPolicy(rawValue: commands) ?? .ask,
              maxBudgetUSD: maxBudget, extraDirectories: [home])
    }

    /// The report's own "As of" date, so it's clear how old the openings are.
    private var status: String {
        guard let text = try? String(contentsOf: report, encoding: .utf8) else {
            return "Not made yet: fill in About me, then press Find my fit."
        }
        if let range = text.range(of: #"As of \d{4}-\d{2}-\d{2}"#, options: .regularExpression) {
            return String(text[range]) + " · openings change weekly, so refresh before acting on one"
        }
        return "Made earlier"
    }

    private var profileIsBlank: Bool {
        // The template's headings and comments alone don't count as a profile.
        profile.replacingOccurrences(of: #"<!--[\s\S]*?-->"#, with: "", options: .regularExpression)
            .split(separator: "\n").filter { !$0.hasPrefix("#") && !$0.trimmingCharacters(in: .whitespaces).isEmpty }
            .isEmpty
    }

    var body: some View {
        VStack(spacing: 0) {
            header
            Divider()
            switch tab {
            case .fit:
                WebPane(fileURL: FileManager.default.fileExists(atPath: report.path) ? report : nil, readAccess: home)
            case .profile:
                profileEditor
            case .run:
                RunPane(runner: runner, directory: folder,
                        emptyHint: "Press “Find my fit” to begin. The search runs here, and you can answer when it asks.",
                        replyText: $replyText, settings: settings)
            }
        }
        .onAppear(perform: loadProfile)
    }

    private var header: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(alignment: .firstTextBaseline) {
                VStack(alignment: .leading, spacing: 2) {
                    Text("Career fit").font(.title2)
                    Text(status).font(.caption).foregroundStyle(.secondary)
                }
                Spacer()
                if runner.isRunning {
                    ProgressView().controlSize(.small)
                    Button("Stop", role: .destructive) { runner.stop() }
                } else {
                    Button(FileManager.default.fileExists(atPath: report.path) ? "Refresh" : "Find my fit") { findFit() }
                        .buttonStyle(.borderedProminent)
                        .disabled(profileIsBlank)
                        .help(profileIsBlank ? "Fill in About me first" : "Research companies and roles that fit you, with sources")
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

    private var profileEditor: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("A few lines about you: background, skills, what you want and don't, where you can work. It stays on this Mac: web searches use keywords only.")
                .font(.caption).foregroundStyle(.secondary)
            TextEditor(text: $profile)
                .font(.system(.body, design: .monospaced))
                .border(Color.secondary.opacity(0.3))
            HStack {
                Spacer()
                if profile != savedProfile { Text("Unsaved changes").font(.caption).foregroundStyle(.orange) }
                Button("Save", action: saveProfile).disabled(profile == savedProfile)
                    .keyboardShortcut("s", modifiers: .command)
            }
        }
        .padding(14)
    }

    private func loadProfile() {
        if let text = try? String(contentsOf: profileURL, encoding: .utf8) {
            profile = text
            savedProfile = text
            return
        }
        // First visit: start from the skill's template (or a built-in copy if the skill isn't installed).
        let template = FileManager.default.homeDirectoryForCurrentUser
            .appendingPathComponent(".claude/skills/career-fit/references/profile_template.md")
        profile = (try? String(contentsOf: template, encoding: .utf8)) ?? """
        # About me

        ## Background

        ## Skills

        ## Experience level

        ## What I want

        ## What I don't want

        ## Where I can work

        """
        tab = .profile
    }

    private func saveProfile() {
        try? profile.write(to: profileURL, atomically: true, encoding: .utf8)
        savedProfile = profile
    }

    private func findFit() {
        if profile != savedProfile { saveProfile() }
        try? FileManager.default.createDirectory(at: folder, withIntermediateDirectories: true)
        tab = .run
        runner.start(prompt: """
        Use the career-fit skill to find the companies and roles I'd love and my best fit. My profile is \
        \(profileURL.path); my library is \(library.root.path) and \(library.caseStudiesRoot.path); my knowledge \
        graph is \(library.knowledgeGraph.path). Write the report to \(report.path) and check it with the skill's checker.
        """, label: "Find my fit", in: folder, settings: settings)
    }
}
