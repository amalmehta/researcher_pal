#!/usr/bin/env python3
"""Render a paper's pages to PNG images and extract its text, so equations can be read from the page.

    python3 pdf_pages.py papers/<slug>/paper.pdf                 # every page
    python3 pdf_pages.py papers/<slug>/paper.pdf --pages 3-5     # some pages
    python3 pdf_pages.py papers/<slug>/paper.pdf --pages 5 --dpi 300 --bands 3   # zoom in on dense math

Writes papers/<slug>/pages/page-NNN.png and papers/<slug>/paper.txt (with "===== PAGE n =====" markers).
With --bands N, each page becomes N overlapping horizontal strips (page-NNN-b1.png, ...): image viewers shrink
a large whole-page image, so a strip is how small subscripts and exponents get read at full resolution.

Why both: extracted PDF text is fine for prose and for searching, but it is not a faithful copy of the math.
It flattens superscripts and subscripts and can drop symbols outright (on the Barabasi-Albert paper,
P(k) ~ k^-gamma comes out as "P (k)~ k gamma", minus sign gone). Equations, signs, exponents, indices and
numbers in math must be read from the page images (or the LaTeX source), never from paper.txt.

Backends: macOS's built-in PDFKit (via pdf_pages.swift, nothing to install), else poppler's pdftoppm and
pdftotext if they are installed. Standard library only.
"""
import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_DPI = 150


def parse_pages(spec, count):
    """'3-5' -> (3, 5); '7' -> (7, 7); None -> (1, count). Clamped to the document."""
    if not spec:
        return 1, count
    match = re.fullmatch(r"\s*(\d+)\s*(?:-\s*(\d+)\s*)?", spec)
    if not match:
        raise ValueError("pages must look like 4 or 3-7, not %r" % spec)
    first = int(match.group(1))
    last = int(match.group(2) or first)
    if first < 1 or last < first:
        raise ValueError("bad page range %r" % spec)
    if first > count:
        raise ValueError("the PDF has %d pages; page %d doesn't exist" % (count, first))
    return first, min(last, count)


def backend():
    if sys.platform == "darwin" and shutil.which("swift"):
        return "pdfkit"
    if shutil.which("pdftoppm") and shutil.which("pdftotext") and shutil.which("pdfinfo"):
        return "poppler"
    return None


def page_count_poppler(pdf):
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True, check=True).stdout
    return int(re.search(r"^Pages:\s+(\d+)", info, re.M).group(1))


def band_rows(height, bands, overlap=0.06):
    """Pixel (top, bottom) rows of each strip, top strip first; neighbours overlap by `overlap` of the page."""
    if bands == 1:
        return [(0, height)]
    strip = height * (1 + overlap * (bands - 1)) / bands
    step = strip - height * overlap
    return [(round(i * step), min(height, round(i * step + strip))) for i in range(bands)]


def render_pdfkit(pdf, out, dpi, pages, text_file, bands):
    # A first pass with an empty range only counts the pages, so --pages can be checked against the document.
    run = lambda first, last, txt: subprocess.run(
        ["swift", str(HERE / "pdf_pages.swift"), str(pdf), str(out), str(dpi), str(first), str(last), txt, str(bands)],
        capture_output=True, text=True)
    done = run(1, 0, "-")
    if done.returncode != 0:
        raise RuntimeError((done.stderr or done.stdout).strip() or "PDFKit could not open %s" % pdf)
    count = int(done.stdout.split()[-1])
    first, last = parse_pages(pages, count)
    done = run(first, last, str(text_file) if text_file else "-")
    if done.returncode != 0:
        raise RuntimeError((done.stderr or done.stdout).strip())
    return count, first, last


def render_poppler(pdf, out, dpi, pages, text_file, bands):
    count = page_count_poppler(pdf)
    first, last = parse_pages(pages, count)
    out.mkdir(parents=True, exist_ok=True)
    scratch = out / ".render"
    scratch.mkdir(exist_ok=True)
    for number in range(first, last + 1):
        info = subprocess.run(["pdfinfo", "-f", str(number), "-l", str(number), str(pdf)],
                              capture_output=True, text=True, check=True).stdout
        w_pt, h_pt = map(float, re.search(r"Page\s+\d+\s+size:\s+([\d.]+)\s+x\s+([\d.]+)", info).groups())
        width, height = round(w_pt * dpi / 72), round(h_pt * dpi / 72)
        for band, (top, bottom) in enumerate(band_rows(height, bands), 1):
            name = "page-%03d.png" % number if bands == 1 else "page-%03d-b%d.png" % (number, band)
            subprocess.run(["pdftoppm", "-r", str(dpi), "-f", str(number), "-l", str(number), "-x", "0", "-y", str(top),
                            "-W", str(width), "-H", str(bottom - top), "-png", "-singlefile", str(pdf),
                            str(scratch / "p")], check=True)
            (scratch / "p.png").rename(out / name)
    scratch.rmdir()
    if text_file:
        raw = subprocess.run(["pdftotext", "-layout", "-f", str(first), "-l", str(last), str(pdf), "-"],
                             capture_output=True, text=True, check=True).stdout
        chunks = raw.split("\f")
        text_file.write_text("".join("\n===== PAGE %d =====\n%s" % (first + i, chunk)
                                     for i, chunk in enumerate(chunks[:last - first + 1])))
    return count, first, last


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--out", type=Path, help="folder for page-NNN.png (default: pages/ next to the PDF)")
    parser.add_argument("--dpi", type=int, default=DEFAULT_DPI,
                        help="resolution (default %d; raise it for small subscripts)" % DEFAULT_DPI)
    parser.add_argument("--pages", help="a page or range, e.g. 4 or 3-7 (default: all)")
    parser.add_argument("--bands", type=int, default=1,
                        help="split each page into this many overlapping horizontal strips, to zoom in (default 1)")
    parser.add_argument("--text", type=Path, help="where to write the extracted text (default: paper.txt next to the PDF)")
    parser.add_argument("--no-text", action="store_true", help="only render images")
    args = parser.parse_args()

    if args.bands < 1 or args.bands > 8:
        sys.exit("--bands must be between 1 and 8")
    if not args.pdf.is_file():
        sys.exit("no such PDF: %s" % args.pdf)
    out = args.out or args.pdf.parent / "pages"
    text_file = None if args.no_text else (args.text or args.pdf.parent / "paper.txt")
    which = backend()
    if which is None:
        sys.exit("can't render pages here: needs macOS (PDFKit) or poppler (pdftoppm, pdftotext, pdfinfo). "
                 "Install poppler, or for an arXiv paper read equations from the LaTeX source instead.")
    try:
        count, first, last = (render_pdfkit if which == "pdfkit" else render_poppler)(
            args.pdf, out, args.dpi, args.pages, text_file, args.bands)
    except (ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        sys.exit("pdf_pages: %s" % exc)

    names = "page-NNN.png" if args.bands == 1 else "page-NNN-b1..b%d.png" % args.bands
    print("rendered pages %d-%d of %d at %d dpi with %s -> %s/%s" % (first, last, count, args.dpi, which, out, names))
    if text_file:
        print("text -> %s (prose and search only: equations, signs and exponents come from the images)" % text_file)


if __name__ == "__main__":
    main()
