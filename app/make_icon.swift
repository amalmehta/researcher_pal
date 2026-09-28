// Draws the app icon: a paper page with a small concept graph over it, in the animations' palette.
//
//   swift make_icon.swift out.png     # writes a 1024x1024 PNG; make_app.sh turns it into AppIcon.icns
import AppKit

let size: CGFloat = 1024
let out = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "icon.png"

func color(_ hex: UInt32, _ alpha: CGFloat = 1) -> CGColor {
    CGColor(srgbRed: CGFloat(hex >> 16 & 0xff) / 255, green: CGFloat(hex >> 8 & 0xff) / 255,
            blue: CGFloat(hex & 0xff) / 255, alpha: alpha)
}

let bgTop = color(0x1f242b), bgBottom = color(0x0e1013), line = color(0x2a2f37)
let ink = color(0xece8df), dim = color(0x9aa1a9)
let blue = color(0x58c4dd), yellow = color(0xf4d35e), green = color(0x83c167), red = color(0xfc6255)

let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: Int(size), pixelsHigh: Int(size), bitsPerSample: 8,
                           samplesPerPixel: 4, hasAlpha: true, isPlanar: false, colorSpaceName: .deviceRGB,
                           bytesPerRow: 0, bitsPerPixel: 0)!
NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: rep)
let ctx = NSGraphicsContext.current!.cgContext

// macOS icon grid: an 824-point rounded square centred on the 1024 canvas, with a soft drop shadow.
let tile = CGRect(x: 100, y: 100, width: 824, height: 824)
let tilePath = CGPath(roundedRect: tile, cornerWidth: 185, cornerHeight: 185, transform: nil)
ctx.saveGState()
ctx.setShadow(offset: CGSize(width: 0, height: -12), blur: 28, color: color(0x000000, 0.35))
ctx.addPath(tilePath)
ctx.setFillColor(bgBottom)
ctx.fillPath()
ctx.restoreGState()

ctx.saveGState()
ctx.addPath(tilePath)
ctx.clip()
let gradient = CGGradient(colorsSpace: CGColorSpace(name: CGColorSpace.sRGB), colors: [bgTop, bgBottom] as CFArray,
                          locations: [0, 1])!
ctx.drawLinearGradient(gradient, start: CGPoint(x: 0, y: tile.maxY), end: CGPoint(x: 0, y: tile.minY), options: [])
ctx.restoreGState()
ctx.addPath(tilePath)
ctx.setStrokeColor(line)
ctx.setLineWidth(4)
ctx.strokePath()

// The paper: a cream page, tilted a little, with a folded corner and lines of text.
ctx.saveGState()
ctx.translateBy(x: 470, y: 520)
ctx.rotate(by: 6 * .pi / 180)
let page = CGRect(x: -205, y: -265, width: 410, height: 530)
let fold: CGFloat = 90
let pagePath = CGMutablePath()
pagePath.move(to: CGPoint(x: page.minX, y: page.minY))
pagePath.addLine(to: CGPoint(x: page.maxX, y: page.minY))
pagePath.addLine(to: CGPoint(x: page.maxX, y: page.maxY - fold))
pagePath.addLine(to: CGPoint(x: page.maxX - fold, y: page.maxY))
pagePath.addLine(to: CGPoint(x: page.minX, y: page.maxY))
pagePath.closeSubpath()
ctx.saveGState()
ctx.setShadow(offset: CGSize(width: 0, height: -10), blur: 24, color: color(0x000000, 0.45))
ctx.addPath(pagePath)
ctx.setFillColor(ink)
ctx.fillPath()
ctx.restoreGState()

let corner = CGMutablePath()
corner.move(to: CGPoint(x: page.maxX, y: page.maxY - fold))
corner.addLine(to: CGPoint(x: page.maxX - fold, y: page.maxY - fold))
corner.addLine(to: CGPoint(x: page.maxX - fold, y: page.maxY))
corner.closeSubpath()
ctx.addPath(corner)
ctx.setFillColor(color(0xc9c4b8))
ctx.fillPath()

// Title bar and body text.
ctx.setFillColor(color(0x16181b))
ctx.fill(CGRect(x: page.minX + 45, y: page.maxY - 95, width: 210, height: 24))
ctx.setFillColor(dim)
for (i, width) in [300, 280, 310, 190, 300, 250, 300, 160].enumerated() {
    ctx.fill(CGRect(x: page.minX + 45, y: page.maxY - 155 - CGFloat(i) * 44, width: CGFloat(width) * 0.98, height: 14))
}
ctx.restoreGState()

// The concept graph, spilling off the page: nodes are ideas, edges are "needs".
let nodes: [(CGPoint, CGColor, CGFloat)] = [
    (CGPoint(x: 700, y: 690), yellow, 62),
    (CGPoint(x: 560, y: 470), blue, 74),
    (CGPoint(x: 790, y: 400), green, 56),
    (CGPoint(x: 660, y: 245), red, 52),
]
let edges = [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3)]
ctx.setLineCap(.round)
for (a, b) in edges {
    ctx.move(to: nodes[a].0)
    ctx.addLine(to: nodes[b].0)
}
ctx.setStrokeColor(color(0x0e1013))
ctx.setLineWidth(30)
ctx.strokePath()
for (a, b) in edges {
    ctx.move(to: nodes[a].0)
    ctx.addLine(to: nodes[b].0)
}
ctx.setStrokeColor(ink)
ctx.setLineWidth(14)
ctx.strokePath()
for (center, fill, radius) in nodes {
    let outer = CGRect(x: center.x - radius - 12, y: center.y - radius - 12, width: 2 * (radius + 12), height: 2 * (radius + 12))
    ctx.setFillColor(color(0x0e1013))
    ctx.fillEllipse(in: outer)
    ctx.setFillColor(fill)
    ctx.fillEllipse(in: outer.insetBy(dx: 12, dy: 12))
}

NSGraphicsContext.current = nil
try! rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: out))
print("wrote \(out)")
