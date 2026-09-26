#!/usr/bin/env bash
# Build ResearcherPal.app. Run from anywhere:
#
#   app/make_app.sh            # release build into app/build/ResearcherPal.app
#   app/make_app.sh --run      # build, then open it
#
# Needs Xcode's Swift toolchain. The app itself needs the `claude` CLI on your PATH.
set -euo pipefail
cd "$(dirname "$0")"

CONFIG=release
APP="build/ResearcherPal.app"

echo "== building"
swift build -c "$CONFIG"
BIN="$(swift build -c "$CONFIG" --show-bin-path)/ResearcherPal"

echo "== assembling $APP"
rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
cp "$BIN" "$APP/Contents/MacOS/ResearcherPal"

cat > "$APP/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleName</key><string>Researcher Pal</string>
  <key>CFBundleDisplayName</key><string>Researcher Pal</string>
  <key>CFBundleIdentifier</key><string>com.researcherpal.app</string>
  <key>CFBundleExecutable</key><string>ResearcherPal</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleShortVersionString</key><string>1.0</string>
  <key>CFBundleVersion</key><string>1</string>
  <key>LSMinimumSystemVersion</key><string>14.0</string>
  <key>NSHighResolutionCapable</key><true/>
  <key>NSHumanReadableCopyright</key><string>MIT licensed</string>
  <key>CFBundleDocumentTypes</key>
  <array>
    <dict>
      <key>CFBundleTypeName</key><string>PDF document</string>
      <key>CFBundleTypeRole</key><string>Viewer</string>
      <key>LSItemContentTypes</key><array><string>com.adobe.pdf</string></array>
    </dict>
  </array>
</dict>
</plist>
PLIST

# Ad-hoc signature: enough for this Mac, not for distribution.
codesign --force --sign - "$APP" >/dev/null 2>&1 || echo "   (codesign skipped)"

echo "== done: $(cd "$(dirname "$APP")" && pwd)/$(basename "$APP")"
[ "${1:-}" = "--run" ] && open "$APP"
exit 0
