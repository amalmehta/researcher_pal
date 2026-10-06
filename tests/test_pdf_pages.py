"""Tests for researcher-pal's pdf_pages.py: page ranges, strip geometry, and a real render when a backend exists."""
import struct
import subprocess
import sys
from pathlib import Path

import pytest

import pdf_pages as pp

SCRIPT = Path(pp.__file__)


def test_parse_pages():
    assert pp.parse_pages(None, 11) == (1, 11)
    assert pp.parse_pages("4", 11) == (4, 4)
    assert pp.parse_pages(" 3 - 7 ", 11) == (3, 7)
    assert pp.parse_pages("9-40", 11) == (9, 11)  # clamped to the document
    for bad in ("0", "5-3", "a", "3-", "12"):
        with pytest.raises(ValueError):
            pp.parse_pages(bad, 11)


def test_band_rows_cover_the_page_with_overlap():
    assert pp.band_rows(1650, 1) == [(0, 1650)]
    rows = pp.band_rows(3300, 3)
    assert rows[0][0] == 0 and rows[-1][1] == 3300
    for (_, end), (start, _) in zip(rows, rows[1:]):
        assert start < end, "neighbouring strips must overlap so no line is only ever cut in half"
    heights = {end - start for start, end in rows}
    assert max(heights) - min(heights) <= 1


def two_page_pdf(path):
    """A minimal valid PDF, 612x792 pt, with one line of text per page. Written by hand: no libraries."""
    objects = ["<< /Type /Catalog /Pages 2 0 R >>",
               "<< /Type /Pages /Kids [3 0 R 5 0 R] /Count 2 >>"]
    for n, words in ((4, "First page P(k) ~ k^-3"), (6, "Second page")):
        objects.append("<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents %d 0 R "
                       "/Resources << /Font << /F1 7 0 R >> >> >>" % n)
        stream = "BT /F1 24 Tf 72 700 Td (%s) Tj ET" % words
        objects.append("<< /Length %d >>\nstream\n%s\nendstream" % (len(stream), stream))
    objects.append("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    out, offsets = b"%PDF-1.4\n", []
    for i, body in enumerate(objects, 1):
        offsets.append(len(out))
        out += ("%d 0 obj\n%s\nendobj\n" % (i, body)).encode()
    xref = len(out)
    out += ("xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)).encode()
    out += "".join("%010d 00000 n \n" % o for o in offsets).encode()
    out += ("trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objects) + 1, xref)).encode()
    path.write_bytes(out)


def png_size(path):
    data = path.read_bytes()[:24]
    assert data[:8] == b"\x89PNG\r\n\x1a\n", path
    return struct.unpack(">II", data[16:24])


@pytest.mark.skipif(pp.backend() is None, reason="needs macOS PDFKit or poppler")
def test_renders_pages_text_and_bands(tmp_path):
    pdf = tmp_path / "paper.pdf"
    two_page_pdf(pdf)
    done = subprocess.run([sys.executable, str(SCRIPT), str(pdf), "--dpi", "72"], capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    assert sorted(p.name for p in (tmp_path / "pages").iterdir()) == ["page-001.png", "page-002.png"]
    assert png_size(tmp_path / "pages" / "page-001.png") == (612, 792)
    text = (tmp_path / "paper.txt").read_text()
    assert "===== PAGE 1 =====" in text and "===== PAGE 2 =====" in text
    assert "First page" in text and "Second page" in text

    done = subprocess.run([sys.executable, str(SCRIPT), str(pdf), "--pages", "2", "--dpi", "144", "--bands", "3",
                           "--no-text", "--out", str(tmp_path / "zoom")], capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    strips = sorted((tmp_path / "zoom").iterdir())
    assert [p.name for p in strips] == ["page-002-b1.png", "page-002-b2.png", "page-002-b3.png"]
    sizes = [png_size(p) for p in strips]
    assert all(w == 1224 for w, _ in sizes)
    assert sum(h for _, h in sizes) > 1584, "strips overlap, so together they're taller than the page"


@pytest.mark.skipif(pp.backend() is None, reason="needs macOS PDFKit or poppler")
def test_rejects_a_page_past_the_end(tmp_path):
    pdf = tmp_path / "paper.pdf"
    two_page_pdf(pdf)
    done = subprocess.run([sys.executable, str(SCRIPT), str(pdf), "--pages", "5"], capture_output=True, text=True)
    assert done.returncode != 0 and "has 2 pages" in done.stderr
