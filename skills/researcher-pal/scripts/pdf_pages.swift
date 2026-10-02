// Renders PDF pages to PNG and extracts their text, with macOS's built-in PDFKit (no installs needed).
// Called by pdf_pages.py; run that instead.
//
//   swift pdf_pages.swift <paper.pdf> <out-dir> <dpi> <first-page> <last-page> <text-file or "-"> <bands>
//
// With bands > 1 each page is split into that many overlapping horizontal strips (page-NNN-b1.png, ...), so a
// dense region can be read at a higher effective resolution than a whole page allows.
import AppKit
import PDFKit

let args = CommandLine.arguments
guard args.count == 8, let doc = PDFDocument(url: URL(fileURLWithPath: args[1])) else {
    FileHandle.standardError.write("usage: pdf_pages.swift <pdf> <out-dir> <dpi> <first> <last> <text-file|-> <bands>\n".data(using: .utf8)!)
    exit(2)
}
let outDir = URL(fileURLWithPath: args[2])
let scale = CGFloat(Double(args[3])!) / 72
let first = max(1, Int(args[4])!), last = min(doc.pageCount, Int(args[5])!)
let bands = max(1, Int(args[7])!)
let overlap: CGFloat = 0.06  // of the page height, so a line cut by one strip's edge is whole in the next
try FileManager.default.createDirectory(at: outDir, withIntermediateDirectories: true)

var text = ""
// An empty range (last < first) renders nothing: pdf_pages.py uses that to count the pages.
for number in (first <= last ? Array(first...last) : []) {
    let page = doc.page(at: number - 1)!
    text += "\n===== PAGE \(number) =====\n" + (page.string ?? "")

    let box = page.bounds(for: .mediaBox)
    let strip = bands == 1 ? box.height : box.height * (1 + overlap * CGFloat(bands - 1)) / CGFloat(bands)
    for band in 0..<bands {
        // PDF y runs upward, so band 0 (the top strip) is the one whose bottom edge is highest.
        let top = box.height - CGFloat(band) * (strip - box.height * overlap)
        let bottom = max(0, top - strip)
        // Draw into a bitmap of exactly the requested pixel size (NSImage would double it on a Retina screen).
        let width = Int((box.width * scale).rounded()), height = Int(((top - bottom) * scale).rounded())
        let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: width, pixelsHigh: height, bitsPerSample: 8,
                                   samplesPerPixel: 4, hasAlpha: true, isPlanar: false, colorSpaceName: .deviceRGB,
                                   bytesPerRow: 0, bitsPerPixel: 0)!
        NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: rep)
        let ctx = NSGraphicsContext.current!.cgContext
        ctx.setFillColor(CGColor(gray: 1, alpha: 1))
        ctx.fill(CGRect(x: 0, y: 0, width: width, height: height))
        ctx.scaleBy(x: scale, y: scale)
        ctx.translateBy(x: 0, y: -bottom)
        page.draw(with: .mediaBox, to: ctx)
        NSGraphicsContext.current = nil
        let name = bands == 1 ? String(format: "page-%03d.png", number) : String(format: "page-%03d-b%d.png", number, band + 1)
        try rep.representation(using: .png, properties: [:])!.write(to: outDir.appendingPathComponent(name))
    }
}
if args[6] != "-" {
    try text.write(toFile: args[6], atomically: true, encoding: .utf8)
}
print(doc.pageCount)
