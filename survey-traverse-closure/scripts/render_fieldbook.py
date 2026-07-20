"""
Render a photographed-style survey field book page (reference version). The RAW
artifact for the hardened traverse gate: the crew's handwritten notes, with the
data in MIXED conventions the analyst must normalize before any adjustment:

  - Course AB direction given as a QUADRANT BEARING (N64-07-45 E), not an azimuth.
  - Station C turn recorded as a DEFLECTION angle (71-01-56 R), not an interior
    angle. Interior = 180 - deflection.
  - Course CD distance recorded as a SLOPE distance (195.37 m) with a vertical
    (zenith from horizontal) angle of 5-00-00; horizontal = slope * cos(vert).
  - Other stations: normal interior angles. Other courses: horizontal distances.

The numbers reduce EXACTLY to the clean instance in traverse.py, so the golden
is unchanged; only the extraction/normalization burden is added.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

def pick_font():
    prefer = ["Comic Sans MS", "Segoe Print", "Ink Free", "Bradley Hand"]
    avail = {f.name for f in fm.fontManager.ttflist}
    for p in prefer:
        if p in avail: return p
    return None
HAND = pick_font()

def txt(ax, x, y, s, size=12, color="#15233a", rot=0, ha="left", bold=False):
    kw = dict(fontsize=size, color=color, rotation=rot, ha=ha, va="center")
    if HAND: kw["fontfamily"] = HAND
    if bold: kw["fontweight"] = "bold"
    ax.text(x, y, s, **kw)

def main(out="fieldbook_reference.png"):
    fig, ax = plt.subplots(figsize=(11, 8.5), dpi=150)
    ax.set_xlim(0, 11); ax.set_ylim(0, 8.5); ax.axis("off")
    ax.set_facecolor("#f3efe0"); fig.patch.set_facecolor("#f3efe0")

    # ruled lines (field-book look)
    for yy in [i*0.42 for i in range(4, 19)]:
        ax.plot([0.5, 10.5], [yy, yy], color="#c9c0a4", lw=0.6, zorder=0)
    ax.plot([2.0, 2.0], [1.6, 7.9], color="#d8b0a0", lw=0.8, zorder=0)  # margin rule

    txt(ax, 0.6, 8.15, "FIELD BOOK 12   pg 47    Parcel BLA-7   crew: RS/JM   wx: clear", size=11, bold=True)
    txt(ax, 0.6, 7.75, "CLOSED LOOP  A-B-C-D-E-A   (traverse right-hand interior)", size=10.5)

    # header row
    txt(ax, 0.6, 7.25, "STA", size=11, bold=True)
    txt(ax, 2.2, 7.25, "angle / direction", size=11, bold=True)
    txt(ax, 6.4, 7.25, "distance to next", size=11, bold=True)

    rows = [
        ("A", "int ang = 98-00-18",        "A->B  bearing  N 64-07-45 E"),
        ("",  "(ang right at A)",            "dist A-B = 199.75 m (horiz, EDM)"),
        ("B", "int ang = 104-16-21",        "dist B-C = 176.55 m (horiz)"),
        ("C", "DEFLECTION = 71-01-56  R",   "SLOPE dist C-D = 195.37 m"),
        ("",  "(recorded as defl, not int)", "  vert angle = 5-00-00 above horiz"),
        ("D", "int ang = 108-51-30",        "dist D-E = 136.50 m (horiz)"),
        ("E", "int ang = 119-54-13",        "dist E-A = 195.97 m (horiz)"),
    ]
    y = 6.8
    for sta, ang, dist in rows:
        if sta: txt(ax, 0.6, y, sta, size=12, bold=True)
        txt(ax, 2.2, y, ang, size=11)
        txt(ax, 6.4, y, dist, size=11)
        y -= 0.52

    # marginal notes, wobbly
    txt(ax, 0.6, 2.5, "note: AB direction from control monument MON-3 (fixed).", size=9.5, color="#5a3020")
    txt(ax, 0.6, 2.1, "note: C was booked as a deflection angle, turned to the RIGHT.", size=9.5, color="#5a3020")
    txt(ax, 0.6, 1.7, "note: C-D taped on a grade; reduce slope to horizontal before use.", size=9.5, color="#5a3020")
    txt(ax, 7.2, 2.3, "start coords A:", size=10, bold=True, color="#15233a")
    txt(ax, 7.2, 1.95, "N 1000.000", size=10, color="#15233a")
    txt(ax, 7.2, 1.65, "E 1000.000", size=10, color="#15233a")

    # little loop sketch top-right
    import numpy as np
    cx, cy, r = 9.2, 6.3, 0.9
    ang = np.linspace(0, 2*np.pi, 6)[:-1] + 0.3
    pts = [(cx + r*np.cos(a), cy + r*np.sin(a)) for a in ang]
    xs = [p[0] for p in pts] + [pts[0][0]]
    ys = [p[1] for p in pts] + [pts[0][1]]
    ax.plot(xs, ys, color="#15233a", lw=1.3)
    for lbl, p in zip("ABCDE", pts):
        txt(ax, p[0], p[1], lbl, size=10, bold=True, ha="center")

    fig.savefig(out, bbox_inches="tight", facecolor=fig.get_facecolor())
    print("wrote", out, "| font:", HAND)

if __name__ == "__main__":
    main()
