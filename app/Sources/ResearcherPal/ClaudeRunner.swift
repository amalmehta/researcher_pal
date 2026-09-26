import Foundation

/// Drives the `claude` CLI that is already installed on this Mac, in headless streaming mode, and turns its
/// NDJSON output into a transcript. No API key: it uses the CLI's own login.
@MainActor
final class ClaudeRunner: ObservableObject {
    struct Item: Identifiable {
        enum Kind { case user, assistant, tool, result, error }
        let id = UUID()
        let kind: Kind
        let text: String
    }

    struct Settings {
        var model: String = "opus"
        var permissionMode: String = "acceptEdits"
        var allowCommands: Bool = true
        var maxBudgetUSD: Double = 10
    }

    @Published private(set) var items: [Item] = []
    @Published private(set) var isRunning = false
    @Published private(set) var sessionID: String?
    @Published private(set) var costUSD: Double = 0
    @Published private(set) var needsLogin = false
    @Published private(set) var lastError: String?

    private var process: Process?
    private var buffer = ""

    var canReply: Bool { !isRunning && sessionID != nil }

    func clear() {
        items = []
        sessionID = nil
        costUSD = 0
        needsLogin = false
        lastError = nil
    }

    /// Start a fresh conversation in `directory`.
    func start(prompt: String, in directory: URL, settings: Settings) {
        clear()
        run(prompt: prompt, in: directory, settings: settings, resume: nil)
    }

    /// Answer the assistant's question (the skills pause and ask) and continue the same session.
    func reply(_ text: String, in directory: URL, settings: Settings) {
        guard let sessionID else { return }
        run(prompt: text, in: directory, settings: settings, resume: sessionID)
    }

    func stop() {
        process?.terminate()
        process = nil
        isRunning = false
    }

    private func run(prompt: String, in directory: URL, settings: Settings, resume: String?) {
        guard !isRunning else { return }
        items.append(Item(kind: .user, text: prompt))
        isRunning = true
        lastError = nil
        buffer = ""

        var arguments = ["-p", prompt,
                         "--output-format", "stream-json", "--verbose",
                         "--permission-mode", settings.permissionMode,
                         "--model", settings.model,
                         "--add-dir", directory.path]
        if settings.maxBudgetUSD > 0 {
            arguments += ["--max-budget-usd", String(format: "%.2f", settings.maxBudgetUSD)]
        }
        if !settings.allowCommands {
            arguments += ["--disallowedTools", "Bash"]
        }
        if let resume {
            arguments += ["--resume", resume]
        }

        // A login shell so the app picks up the same PATH (and therefore the same `claude`) as Terminal.
        let command = (["claude"] + arguments).map(Self.quote).joined(separator: " ")
        let task = Process()
        task.executableURL = URL(fileURLWithPath: "/bin/zsh")
        task.arguments = ["-lc", command]
        task.currentDirectoryURL = directory

        let out = Pipe(), err = Pipe()
        task.standardOutput = out
        task.standardError = err

        out.fileHandleForReading.readabilityHandler = { [weak self] handle in
            let chunk = handle.availableData
            guard !chunk.isEmpty, let text = String(data: chunk, encoding: .utf8) else { return }
            Task { @MainActor in self?.consume(text) }
        }
        err.fileHandleForReading.readabilityHandler = { [weak self] handle in
            let chunk = handle.availableData
            guard !chunk.isEmpty, let text = String(data: chunk, encoding: .utf8) else { return }
            Task { @MainActor in self?.consumeError(text) }
        }
        task.terminationHandler = { [weak self] finished in
            Task { @MainActor in self?.finish(status: finished.terminationStatus) }
        }

        do {
            try task.run()
            process = task
        } catch {
            isRunning = false
            lastError = "Could not start claude: \(error.localizedDescription)"
            items.append(Item(kind: .error, text: lastError!))
        }
    }

    private func consume(_ text: String) {
        buffer += text
        while let newline = buffer.firstIndex(of: "\n") {
            let line = String(buffer[buffer.startIndex..<newline])
            buffer = String(buffer[buffer.index(after: newline)...])
            handle(line: line.trimmingCharacters(in: .whitespaces))
        }
    }

    private func consumeError(_ text: String) {
        let trimmed = text.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }
        noticeLoginProblem(in: trimmed)
        items.append(Item(kind: .error, text: trimmed))
    }

    private func handle(line: String) {
        guard !line.isEmpty, let data = line.data(using: .utf8),
              let event = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else { return }

        switch event["type"] as? String {
        case "system":
            if let id = event["session_id"] as? String { sessionID = id }
        case "assistant":
            guard let message = event["message"] as? [String: Any],
                  let content = message["content"] as? [[String: Any]] else { return }
            for part in content {
                switch part["type"] as? String {
                case "text":
                    let text = (part["text"] as? String ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
                    if !text.isEmpty { items.append(Item(kind: .assistant, text: text)) }
                case "tool_use":
                    items.append(Item(kind: .tool, text: Self.describe(tool: part)))
                default:
                    break
                }
            }
        case "result":
            if let id = event["session_id"] as? String { sessionID = id }
            costUSD = event["total_cost_usd"] as? Double ?? costUSD
            let subtype = event["subtype"] as? String ?? "done"
            if subtype != "success", let text = event["result"] as? String {
                noticeLoginProblem(in: text)
                items.append(Item(kind: .error, text: text))
            }
            let turns = event["num_turns"] as? Int ?? 0
            items.append(Item(kind: .result, text: "\(subtype) · \(turns) turns · $\(String(format: "%.2f", costUSD))"))
        default:
            break
        }
    }

    private func noticeLoginProblem(in text: String) {
        if text.contains("OAuth") || text.localizedCaseInsensitiveContains("authentication_error")
            || text.contains("/login") {
            needsLogin = true
        }
    }

    private func finish(status: Int32) {
        isRunning = false
        process = nil
        if status != 0 && status != 15 && !needsLogin {
            lastError = "claude exited with status \(status)"
            items.append(Item(kind: .error, text: lastError!))
        }
    }

    private static func describe(tool part: [String: Any]) -> String {
        let name = part["name"] as? String ?? "tool"
        guard let input = part["input"] as? [String: Any] else { return name }
        for key in ["file_path", "path", "command", "pattern", "skill", "prompt"] {
            if let value = input[key] as? String {
                return "\(name): \(value.prefix(120))"
            }
        }
        return name
    }

    private static func quote(_ argument: String) -> String {
        "'" + argument.replacingOccurrences(of: "'", with: "'\\''") + "'"
    }
}
