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
        /// What the transcript shows: a short label for the long prompts the app writes.
        var label: String?
        var shown: String { label ?? text }
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

    /// One claude process. Output is kept as bytes until a whole line has arrived: a pipe read can end in the
    /// middle of a multi-byte character, and decoding that piece on its own would lose it.
    private struct Run {
        let id = UUID()
        let process: Process
        var out = Data()
        var err = Data()
        var openStreams = 2
        var exitStatus: Int32?
    }

    /// The run in progress. Callbacks carry their run's id, so a stopped run's late output and exit are ignored.
    private var current: Run?

    var canReply: Bool { !isRunning && sessionID != nil }

    func clear() {
        items = []
        sessionID = nil
        costUSD = 0
        needsLogin = false
        lastError = nil
    }

    /// Start a fresh conversation in `directory`.
    func start(prompt: String, label: String? = nil, in directory: URL, settings: Settings) {
        clear()
        run(prompt: prompt, label: label, in: directory, settings: settings, resume: nil)
    }

    /// Answer the assistant's question (the skills pause and ask) and continue the same session.
    func reply(_ text: String, in directory: URL, settings: Settings) {
        guard let sessionID else { return }
        run(prompt: text, label: nil, in: directory, settings: settings, resume: sessionID)
    }

    func stop() {
        current?.process.terminate()
        current = nil
        isRunning = false
    }

    /// Appends an item, watching every line for the "not logged in" failure: it can arrive on stderr, in a
    /// result, or as ordinary assistant text, and the banner has to show in all three cases.
    private func append(_ item: Item) {
        let text = item.text
        if text.contains("OAuth") || text.contains("/login")
            || text.localizedCaseInsensitiveContains("authentication_error")
            || text.localizedCaseInsensitiveContains("401") && text.localizedCaseInsensitiveContains("api error") {
            needsLogin = true
        }
        items.append(item)
    }

    private func run(prompt: String, label: String?, in directory: URL, settings: Settings, resume: String?) {
        guard !isRunning else { return }
        append(Item(kind: .user, text: prompt, label: label))
        isRunning = true
        lastError = nil

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

        // A login shell so the app picks up the same PATH (and therefore the same `claude`) as Terminal. `exec`
        // makes claude replace the shell, so Stop terminates claude itself rather than only its parent shell.
        // RESEARCHER_PAL_CLAUDE points at a specific binary instead.
        let claude = ProcessInfo.processInfo.environment["RESEARCHER_PAL_CLAUDE"] ?? "claude"
        let command = "exec " + ([claude] + arguments).map(Self.quote).joined(separator: " ")
        let task = Process()
        task.executableURL = URL(fileURLWithPath: "/bin/zsh")
        task.arguments = ["-lc", command]
        task.currentDirectoryURL = directory

        let out = Pipe(), err = Pipe()
        task.standardOutput = out
        task.standardError = err

        let run = Run(process: task)
        let id = run.id
        // The main queue is FIFO, so chunks are handled in the order they were read. An empty read is end of
        // file: remove the handler there, or Foundation keeps calling it with empty data.
        for (pipe, isError) in [(out, false), (err, true)] {
            pipe.fileHandleForReading.readabilityHandler = { [weak self] handle in
                let chunk = handle.availableData
                if chunk.isEmpty { handle.readabilityHandler = nil }
                DispatchQueue.main.async {
                    MainActor.assumeIsolated { self?.received(chunk, isError: isError, run: id) }
                }
            }
        }
        task.terminationHandler = { [weak self] finished in
            let status = finished.terminationStatus
            DispatchQueue.main.async {
                MainActor.assumeIsolated { self?.exited(status: status, run: id) }
            }
        }

        do {
            current = run
            try task.run()
        } catch {
            current = nil
            out.fileHandleForReading.readabilityHandler = nil
            err.fileHandleForReading.readabilityHandler = nil
            isRunning = false
            lastError = "Could not start claude: \(error.localizedDescription)"
            append(Item(kind: .error, text: lastError!))
        }
    }

    private func received(_ chunk: Data, isError: Bool, run id: UUID) {
        guard var run = current, run.id == id else { return }
        if chunk.isEmpty {
            run.openStreams -= 1
        } else if isError {
            run.err.append(chunk)
        } else {
            run.out.append(chunk)
        }
        // Whole lines only; at end of file, whatever is left is the last line.
        let lines = isError ? Self.takeLines(from: &run.err, all: chunk.isEmpty)
                            : Self.takeLines(from: &run.out, all: chunk.isEmpty)
        current = run
        if isError {
            let text = lines.joined(separator: "\n").trimmingCharacters(in: .whitespacesAndNewlines)
            if !text.isEmpty { append(Item(kind: .error, text: text)) }
        } else {
            lines.forEach { handle(line: $0.trimmingCharacters(in: .whitespaces)) }
        }
        finishIfDone()
    }

    private func exited(status: Int32, run id: UUID) {
        guard current?.id == id else { return }
        current?.exitStatus = status
        finishIfDone()
    }

    /// Splits complete lines off the front of `buffer`, decoding each one whole. With `all`, the unterminated
    /// rest counts as a line too.
    private static func takeLines(from buffer: inout Data, all: Bool) -> [String] {
        var lines: [String] = []
        while let newline = buffer.firstIndex(of: UInt8(ascii: "\n")) {
            lines.append(String(decoding: buffer[buffer.startIndex..<newline], as: UTF8.self))
            buffer.removeSubrange(buffer.startIndex...newline)
        }
        if all, !buffer.isEmpty {
            lines.append(String(decoding: buffer, as: UTF8.self))
            buffer.removeAll()
        }
        return lines
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
                    if !text.isEmpty { append(Item(kind: .assistant, text: text)) }
                case "tool_use":
                    append(Item(kind: .tool, text: Self.describe(tool: part)))
                default:
                    break
                }
            }
        case "result":
            if let id = event["session_id"] as? String { sessionID = id }
            costUSD = event["total_cost_usd"] as? Double ?? costUSD
            let subtype = event["subtype"] as? String ?? "done"
            if subtype != "success", let text = event["result"] as? String {
                append(Item(kind: .error, text: text))
            }
            let turns = event["num_turns"] as? Int ?? 0
            append(Item(kind: .result, text: "\(subtype) · \(turns) turns · $\(String(format: "%.2f", costUSD))"))
        default:
            break
        }
    }

    /// A run is over once the process has exited and both pipes have been read to the end, so the last lines
    /// of output (usually the result) are always shown before the run is marked finished.
    private func finishIfDone() {
        guard let run = current, run.openStreams == 0, let status = run.exitStatus else { return }
        current = nil
        isRunning = false
        if status != 0 && status != 15 && !needsLogin {
            lastError = "The assistant exited with status \(status)"
            append(Item(kind: .error, text: lastError!))
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
