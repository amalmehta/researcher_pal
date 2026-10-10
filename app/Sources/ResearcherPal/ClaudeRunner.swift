import Foundation

/// Drives the `claude` CLI that is already installed on this Mac, in headless streaming mode, and turns its
/// NDJSON output into a transcript. No API key: it uses the CLI's own login.
///
/// The app is the CLI's permission host (`--permission-prompt-tool stdio`): when the assistant wants to do
/// something that needs approval (run a command, write outside the paper's folder), the CLI asks over stdin/stdout
/// and the app shows the request. Without a host, a headless CLI denies every such request on its own, so the
/// skills could not download a paper, extract its text or run an exercise's tests.
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

    /// Sonnet by default: tutoring and research on material that's already built and checked don't need Opus,
    /// and it costs about a fifth as much. Opus stays one click away in Settings.
    nonisolated static let defaultModel = "sonnet"

    struct Settings {
        var model: String = ClaudeRunner.defaultModel
        var permissionMode: String = "acceptEdits"
        var commands: CommandPolicy = .ask
        var maxBudgetUSD: Double = 10
        /// Folders outside the paper's own that the assistant may write without asking (the knowledge graph's).
        var extraDirectories: [URL] = []
    }

    enum CommandPolicy: String, CaseIterable {
        case ask, always, never
    }

    /// Something the assistant is waiting for the user to allow or deny.
    struct PermissionRequest: Identifiable {
        let id: String              // the CLI's request_id
        let title: String
        let summary: String         // the command, file or URL, shown verbatim
        let detail: String?         // the assistant's own explanation, when it gave one
        let tool: String
        fileprivate let input: [String: Any]
    }

    enum Decision { case allow, allowAll, deny }

    @Published private(set) var items: [Item] = []
    @Published private(set) var isRunning = false
    @Published private(set) var sessionID: String?
    @Published private(set) var costUSD: Double = 0
    @Published private(set) var needsLogin = false
    @Published private(set) var lastError: String?
    @Published private(set) var permissionRequests: [PermissionRequest] = []

    /// "Allow all" lasts for the rest of the conversation, replies included, and ends with clear().
    private var allowAll = false

    /// One claude process. Output is kept as bytes until a whole line has arrived: a pipe read can end in the
    /// middle of a multi-byte character, and decoding that piece on its own would lose it.
    private struct Run {
        let id = UUID()
        let process: Process
        let input: FileHandle
        var out = Data()
        var err = Data()
        var openStreams = 2
        var exitStatus: Int32?
    }

    /// The run in progress. Callbacks carry their run's id, so a stopped run's late output and exit are ignored.
    private var current: Run?

    var canReply: Bool { !isRunning && sessionID != nil }

    init() {
        // Answering a CLI that has just exited writes to a closed pipe. Ignore SIGPIPE so that write fails
        // quietly instead of the signal killing the app.
        signal(SIGPIPE, SIG_IGN)
    }

    func clear() {
        items = []
        sessionID = nil
        costUSD = 0
        needsLogin = false
        lastError = nil
        permissionRequests = []
        allowAll = false
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
        permissionRequests = []
    }

    /// Answers one of the assistant's permission requests. "Allow all" also answers every other open request.
    func answer(_ request: PermissionRequest, _ decision: Decision) {
        guard permissionRequests.contains(where: { $0.id == request.id }) else { return }
        if decision == .allowAll {
            allowAll = true
            permissionRequests.forEach { respond(to: $0, allow: true) }
        } else {
            respond(to: request, allow: decision == .allow)
        }
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

        // The prompt goes in on stdin as a stream-json message, so stdin stays open for permission answers.
        var arguments = ["-p", "--input-format", "stream-json", "--output-format", "stream-json", "--verbose",
                         "--permission-prompt-tool", "stdio",
                         "--permission-mode", settings.permissionMode,
                         "--model", settings.model,
                         "--add-dir", directory.path]
        for extra in settings.extraDirectories {
            arguments += ["--add-dir", extra.path]
        }
        if settings.maxBudgetUSD > 0 {
            arguments += ["--max-budget-usd", String(format: "%.2f", settings.maxBudgetUSD)]
        }
        // Every run, replies included: the skills are written for a terminal, so say where they are.
        arguments += ["--append-system-prompt", Self.appContext]
        switch settings.commands {
        case .ask: break
        case .always: arguments += ["--allowedTools", "Bash"]
        case .never: arguments += ["--disallowedTools", "Bash"]
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

        let input = Pipe(), out = Pipe(), err = Pipe()
        task.standardInput = input
        task.standardOutput = out
        task.standardError = err

        let run = Run(process: task, input: input.fileHandleForWriting)
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
            send(["type": "user", "message": ["role": "user", "content": prompt]])
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
        case "control_request":
            guard let requestID = event["request_id"] as? String,
                  let request = event["request"] as? [String: Any] else { return }
            if request["subtype"] as? String == "can_use_tool" {
                ask(requestID, request)
            } else {
                // Nothing else the CLI can ask a host for is needed here; say so rather than leave it waiting.
                send(["type": "control_response", "response": [
                    "subtype": "error", "request_id": requestID,
                    "error": "Researcher Pal doesn't handle \(request["subtype"] as? String ?? "this request")."]])
            }
        case "control_cancel_request":
            // The CLI no longer needs an answer (the turn ended, say).
            if let requestID = event["request_id"] as? String {
                permissionRequests.removeAll { $0.id == requestID }
            }
        case "result":
            // The turn is over: closing stdin lets the CLI exit. A reply starts a new process with --resume.
            try? current?.input.close()
            if let id = event["session_id"] as? String { sessionID = id }
            costUSD = event["total_cost_usd"] as? Double ?? costUSD
            // A failed API call (an expired login, say) still reports subtype "success"; is_error is what says
            // the run failed.
            let subtype = event["subtype"] as? String ?? "success"
            let failed = event["is_error"] as? Bool == true || subtype != "success"
            if failed {
                var reasons = (event["errors"] as? [String]) ?? []
                if let text = event["result"] as? String, !text.isEmpty { reasons.insert(text, at: 0) }
                for reason in reasons {
                    // The failure usually arrived as the assistant's last message already: show it once, as an error.
                    if let last = items.last, last.kind == .assistant, last.text == reason {
                        items.removeLast()
                    }
                    append(Item(kind: .error, text: reason))
                }
            }
            let turns = event["num_turns"] as? Int ?? 0
            let summary = "\(turns) turn\(turns == 1 ? "" : "s") · $\(String(format: "%.2f", costUSD))"
            append(Item(kind: failed ? .error : .result, text: (failed ? "Failed · " : "Done · ") + summary))
        default:
            break
        }
    }

    private func ask(_ requestID: String, _ request: [String: Any]) {
        let tool = request["tool_name"] as? String ?? "tool"
        let input = request["input"] as? [String: Any] ?? [:]
        // The title is the app's own plain question; the assistant's explanation (the CLI's description, or
        // the command's) goes underneath, once.
        let summary = Self.summary(tool: tool, input: input, display: request["display_name"] as? String)
        let explanation = (request["description"] as? String) ?? (input["description"] as? String)
        let pending = PermissionRequest(
            id: requestID,
            title: Self.title(tool: tool, input: input),
            summary: summary,
            detail: explanation == summary ? nil : explanation,
            tool: tool, input: input)
        if allowAll {
            respond(to: pending, allow: true, wasAsked: false)
        } else {
            permissionRequests.append(pending)
        }
    }

    private func respond(to request: PermissionRequest, allow: Bool, wasAsked: Bool = true) {
        permissionRequests.removeAll { $0.id == request.id }
        let answer: [String: Any] = allow
            ? ["behavior": "allow", "updatedInput": request.input]
            : ["behavior": "deny", "message": "The user declined this in Researcher Pal."]
        send(["type": "control_response", "response": ["subtype": "success", "request_id": request.id, "response": answer]])
        if allow {
            append(Item(kind: .tool, text: (wasAsked ? "Allowed: " : "Allowed (allow all): ") + request.summary))
        } else {
            append(Item(kind: .error, text: "Declined: " + request.summary))
        }
    }

    /// Writes one JSON message to the CLI's stdin.
    private func send(_ message: [String: Any]) {
        guard let input = current?.input,
              var data = try? JSONSerialization.data(withJSONObject: message, options: [.withoutEscapingSlashes]) else { return }
        data.append(UInt8(ascii: "\n"))
        try? input.write(contentsOf: data)
    }

    private static func title(tool: String, input: [String: Any]) -> String {
        switch tool {
        case "Bash": return "Run a command?"
        case "Write", "Edit", "MultiEdit", "NotebookEdit": return "Change a file?"
        case "Read", "Glob", "Grep": return "Read files outside this paper's folder?"
        case "WebFetch", "WebSearch": return "Use the web?"
        default: return "Use \(tool)?"
        }
    }

    private static func summary(tool: String, input: [String: Any], display: String?) -> String {
        for key in ["command", "file_path", "notebook_path", "path", "url", "query", "pattern"] {
            if let value = input[key] as? String { return value }
        }
        if let data = try? JSONSerialization.data(withJSONObject: input, options: [.sortedKeys, .withoutEscapingSlashes]),
           let json = String(data: data, encoding: .utf8), json != "{}" {
            return "\(display ?? tool) \(json.prefix(400))"
        }
        return display ?? tool
    }

    /// A run is over once the process has exited and both pipes have been read to the end, so the last lines
    /// of output (usually the result) are always shown before the run is marked finished.
    private func finishIfDone() {
        guard let run = current, run.openStreams == 0, let status = run.exitStatus else { return }
        current = nil
        isRunning = false
        permissionRequests = []
        if status != 0 && status != 15 && !needsLogin {
            lastError = "The assistant exited with status \(status)"
            append(Item(kind: .error, text: lastError!))
        }
    }

    /// What the assistant needs to know to talk well inside the app rather than a terminal.
    static let appContext = """
    You are running inside Researcher Pal, a Mac app, not a terminal. Its purpose is to make a researcher's life \
    easier with explanations that are easy to read without losing any depth or nuance. Write every message that way: \
    open with the point in one or two plain sentences, then give the full detail underneath under short bold labels \
    or a list: the exact equation, what each symbol means, the assumption it rests on, the caveat, and where it is in \
    the paper (section, equation, figure). Simplify the wording, never the content: no condition, caveat or number is \
    dropped to make a message shorter; move it below the summary instead. Define each symbol the first time it \
    appears. The chat panel renders Markdown fully (headings, lists, tables, code, and math in $...$ or $$...$$), so \
    use structure that helps scanning, but keep each message focused on one thing and ask one question at a time, \
    waiting for the answer before the next. A paper's material is in the app's tabs: Concept map, Animations, \
    Exercises, and Ideas (Sources for a case study). Point to those tabs by name. Don't list file paths, and don't \
    tell the person to open files in a browser or run commands in a terminal; run commands yourself when needed \
    (the app asks them for permission). The one exception: when they need to write code, name the single file to \
    edit (e.g. exercises/02_mla/impl.py); they edit it in their own editor, and you offer to run its tests.
    """

    /// A step in plain words ("Read concept_graph.md", "Ran: run the exercise's tests"), not the raw tool call.
    static func describe(tool part: [String: Any]) -> String {
        let name = part["name"] as? String ?? "tool"
        let input = part["input"] as? [String: Any] ?? [:]
        let string = { (key: String) in (input[key] as? String).map { String($0.prefix(110)) } }
        let file = { (key: String) in string(key).map { URL(fileURLWithPath: $0).lastPathComponent } }
        switch name {
        case "Read": return "Read " + (file("file_path") ?? "a file")
        case "Write": return "Wrote " + (file("file_path") ?? "a file")
        case "Edit", "MultiEdit", "NotebookEdit": return "Edited " + (file("file_path") ?? file("notebook_path") ?? "a file")
        case "Bash": return "Ran: " + (string("description") ?? string("command") ?? "a command")
        case "Glob", "Grep": return "Searched files" + (string("pattern").map { " for " + $0 } ?? "")
        case "Skill": return "Opened the " + (string("skill") ?? "") + " skill"
        case "WebSearch": return "Searched the web: " + (string("query") ?? "")
        case "WebFetch": return "Read " + (string("url").flatMap { URL(string: $0)?.host } ?? "a web page")
        case "TodoWrite": return "Updated its plan"
        case "Task", "Agent": return "Started a helper" + (string("description").map { ": " + $0 } ?? "")
        default: return name
        }
    }

    private static func quote(_ argument: String) -> String {
        "'" + argument.replacingOccurrences(of: "'", with: "'\\''") + "'"
    }
}
