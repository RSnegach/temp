"""
Render a hand-drawn-style marked-up inspection sketch (reference version). An
inspector's bring-up note on the 4-hole mounting pattern: true-position crosses,
the measured hole centers offset from them, the dev arrows, and handwritten notes
on which holes looked marginal. This is a REFERENCE render; the final submission
uses a photographed redraw in its place.

Deliberately loose and annotated, not a clean CAD drawing. Uses a handwriting-ish
font if available, wobbled strokes, and margin notes. No numbers here that are not
also in the CMM report (the sketch flags, it does not re-specify).
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

# try to find a casual/handwriting font; fall back to default
def pick_font():
    prefer = ["Comic Sans MS", "Segoe Print", "Ink Free", "Bradley Hand", "Comic Neue"]
    avail = {f.name for f in fm.fontManager.ttflist}
    for p in prefer:
        if p in avail:
            return p
    return None

HAND = pick_font()

def wob(x, y, n=40, amp=0.012):
    """wobble a straight segment into a hand-drawn-looking line."""
    xs = np.linspace(x[0], x[1], n)
    ys = np.linspace(y[0], y[1], n)
    rng = np.random.default_rng(7)
    xs = xs + rng.normal(0, amp, n)
    ys = ys + rng.normal(0, amp, n)
    return xs, ys

def hand_circle(ax, cx, cy, r, lw=1.6):
    t = np.linspace(0, 2 * np.pi, 120)
    rng = np.random.default_rng(int(abs(cx * 100 + cy * 7)))
    rr = r * (1 + rng.normal(0, 0.02, t.size))
    ax.plot(cx + rr * np.cos(t), cy + rr * np.sin(t), color="#1a1a1a", lw=lw)

def txt(ax, x, y, s, size=12, rot=0, color="#1a1a1a"):
    kw = dict(fontsize=size, color=color, rotation=rot, ha="left", va="center")
    if HAND: kw["fontfamily"] = HAND
    ax.text(x, y, s, **kw)

def cross(ax, cx, cy, s=0.16, lw=1.1, color="#333333"):
    xs, ys = wob((cx - s, cx + s), (cy, cy)); ax.plot(xs, ys, color=color, lw=lw)
    xs, ys = wob((cx, cx), (cy - s, cy + s)); ax.plot(xs, ys, color=color, lw=lw)

def main(out="inspection_sketch_reference.png"):
    fig, ax = plt.subplots(figsize=(11, 8), dpi=150)
    ax.set_xlim(0, 11); ax.set_ylim(0, 8); ax.axis("off")
    ax.set_facecolor("#fbfaf6"); fig.patch.set_facecolor("#fbfaf6")

    # title / header scribble
    txt(ax, 0.5, 7.6, "BRKT-4471  bring-up  -  4X mtg hole pattern", size=16)
    txt(ax, 0.5, 7.2, "ser 4471-0007   datums A|B(M)|C   pos dia0.20(M)", size=11.5)
    txt(ax, 8.3, 7.55, "sheet: my notes", size=11, color="#555555")

    # bracket outline (loose)
    box = [(1.0, 1.4), (9.6, 1.4), (9.6, 6.4), (1.0, 6.4), (1.0, 1.4)]
    for i in range(len(box) - 1):
        xs, ys = wob((box[i][0], box[i+1][0]), (box[i][1], box[i+1][1]), amp=0.02)
        ax.plot(xs, ys, color="#1a1a1a", lw=1.8)

    # datum B center hole
    hand_circle(ax, 5.3, 3.9, 0.5)
    cross(ax, 5.3, 3.9, s=0.6)
    txt(ax, 5.55, 4.55, "B datum hole", size=11)
    txt(ax, 4.15, 3.2, "B meas 10.04  (dep 0.04 -> shift!)", size=10.5, color="#204020")

    # 4 holes: true position cross + measured center offset + arrow
    holes = {
        "H1": (2.6, 5.3, 0.10, 0.08, "looks ok, small offset"),
        "H2": (8.0, 5.3, 0.16, 0.11, "at MMC -> NO bonus, tight"),
        "H3": (2.6, 2.5, 0.22, 0.16, "big offset, but LMC bonus"),
        "H4": (8.0, 2.5, 0.26, 0.19, "worst one - flag for MRB?"),
    }
    for hid, (hx, hy, ox, oy, note) in holes.items():
        cross(ax, hx, hy, s=0.34)                        # true position
        hand_circle(ax, hx + ox, hy + oy, 0.30)          # measured hole (offset)
        # dev arrow from true pos to measured center
        ax.annotate("", xy=(hx + ox, hy + oy), xytext=(hx, hy),
                    arrowprops=dict(arrowstyle="->", color="#a02020", lw=1.6))
        txt(ax, hx - 0.35, hy - 0.62, hid, size=13)
        txt(ax, hx - 0.35, hy - 0.92, note, size=9.5, color="#5a2a2a")

    # legend / key scribble, lower-left, not filled
    txt(ax, 0.6, 0.95, "key:  + = true posn    O = measured hole    ->  = center dev", size=10.5)
    txt(ax, 0.6, 0.6, "note: dev arrows exaggerated for clarity, read CMM report for values", size=9.5, color="#555555")

    # a couple of margin call-outs
    txt(ax, 9.7, 4.6, "R1 bore", size=10.5, rot=90, color="#333333")
    txt(ax, 0.15, 4.2, "A = back face (primary)", size=10, rot=90, color="#333333")

    fig.savefig(out, bbox_inches="tight", facecolor=fig.get_facecolor())
    print("wrote", out, "| hand font:", HAND)

if __name__ == "__main__":
    main()
