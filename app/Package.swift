// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "ResearcherPal",
    platforms: [.macOS(.v14)],
    targets: [
        .executableTarget(
            name: "ResearcherPal",
            path: "Sources/ResearcherPal",
            swiftSettings: [.swiftLanguageMode(.v5)]
        )
    ]
)
