"""Method diagram: the 2x2 ablation grid, drawn with Graphviz (editable source in figures/src/)."""
import subprocess

import data

rows = data.runs()
warmup = rows["baseline"][0]["warmup_steps"]
no_warmup = rows["no_warmup"][0]["warmup_steps"]

DOT = """digraph ablation {
  graph [margin=0, pad=0.02, bgcolor="transparent"];
  node [shape=plaintext, fontname="Times-Roman", fontsize=10];
  grid [label=<
    <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="5" COLOR="#555555">
      <TR>
        <TD BORDER="0"></TD>
        <TD BORDER="0"><B>scaled</B><BR/>QK<SUP>T</SUP>/&#8730;d<SUB>k</SUB></TD>
        <TD BORDER="0"><B>unscaled</B><BR/>QK<SUP>T</SUP></TD>
      </TR>
      <TR>
        <TD BORDER="0" ALIGN="RIGHT"><B>warmup</B><BR/>w = %(warmup)d</TD>
        <TD BGCOLOR="#E8F1FA">Baseline</TD>
        <TD BGCOLOR="#E8F1FA">No scaling</TD>
      </TR>
      <TR>
        <TD BORDER="0" ALIGN="RIGHT"><B>no warmup</B><BR/>w = %(no_warmup)d</TD>
        <TD BGCOLOR="#FBEDE3">No warmup</TD>
        <TD BGCOLOR="#FBEDE3">Neither</TD>
      </TR>
    </TABLE>>];
}
""" % {"warmup": warmup, "no_warmup": no_warmup}

src = data.VENUE_DIR / "figures" / "src" / "ablation_grid.dot"
src.parent.mkdir(parents=True, exist_ok=True)
src.write_text(DOT)
subprocess.run(["dot", "-Tpdf", "-o", str(data.VENUE_DIR / "figures" / "ablation_grid.pdf"), str(src)], check=True)
print("wrote ablation_grid.pdf")
