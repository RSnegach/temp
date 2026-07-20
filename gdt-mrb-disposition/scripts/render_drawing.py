"""
Render the inspection drawing as a PNG: bracket outline, feature callouts with
GD&T feature control frames, datum feature symbols, size callouts, notes, and a
title block. This is the RAW artifact handed to the gate model, so the frames
must be legible and the MMC / RFS distinction unambiguous.

GD&T symbols are drawn as geometric primitives (not font glyphs) so nothing
renders as a missing-glyph box:
  position  = circle with a full crosshair (circled plus)
  MMC       = circle with letter 'M' inside  (modifier)
  profile   = half-circle arc resting on a baseline
  flatness  = parallelogram
Compartment width is sized to its text so nothing overflows or overlaps.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Arc, Polygon

DIA = "⌀"   # diameter sign renders fine in DejaVu Sans

# ---- symbol primitives, each drawn centered in a compartment box ----
def sym_position(ax, cx, cy, r=0.10):
    ax.add_patch(Circle((cx, cy), r, fill=False, lw=1.3, ec="black"))
    ax.plot([cx - r * 1.7, cx + r * 1.7], [cy, cy], lw=1.1, color="black")
    ax.plot([cx, cx], [cy - r * 1.7, cy + r * 1.7], lw=1.1, color="black")

def sym_mmc(ax, cx, cy, r=0.13):
    ax.add_patch(Circle((cx, cy), r, fill=False, lw=1.2, ec="black"))
    ax.text(cx, cy - 0.005, "M", ha="center", va="center", fontsize=9,
            fontweight="bold")

def sym_profile(ax, cx, cy, r=0.12):
    ax.add_patch(Arc((cx, cy - 0.02), r * 2, r * 2, theta1=0, theta2=180, lw=1.3))
    ax.plot([cx - r, cx + r], [cy - 0.02, cy - 0.02], lw=1.2, color="black")

def sym_flatness(ax, cx, cy, w=0.20, h=0.13):
    pts = [(cx - w/2, cy - h/2), (cx - w/2 + 0.06, cy + h/2),
           (cx + w/2, cy + h/2), (cx + w/2 - 0.06, cy - h/2)]
    ax.add_patch(Polygon(pts, closed=True, fill=False, lw=1.3, ec="black"))

CHARW = 0.083   # width per text char at fontsize 10.5 in axis units
H = 0.40        # frame height

def _text_w(s):
    return max(0.55, len(s) * CHARW + 0.18)

def fcf(ax, x, y, comps):
    """comps: list of ('sym', name) or ('text', 'string') or ('textmod', 'txt','M').
    A 'textmod' compartment prints text then a small MMC circle after it."""
    cx = x
    boxes = []
    for kind, *payload in comps:
        if kind == "sym":
            name = payload[0]
            w = 0.55
            ax.add_patch(Rectangle((cx, y), w, H, fill=False, lw=1.5, ec="black"))
            mid = (cx + w/2, y + H/2)
            if name == "position": sym_position(ax, *mid)
            elif name == "profile": sym_profile(ax, *mid)
            elif name == "flatness": sym_flatness(ax, *mid)
            boxes.append((cx, w)); cx += w
        elif kind == "text":
            s = payload[0]; w = _text_w(s)
            ax.add_patch(Rectangle((cx, y), w, H, fill=False, lw=1.5, ec="black"))
            ax.text(cx + w/2, y + H/2, s, ha="center", va="center", fontsize=10.5)
            boxes.append((cx, w)); cx += w
        elif kind == "textmod":
            s, mod = payload[0], payload[1]
            w = _text_w(s) + 0.30
            ax.add_patch(Rectangle((cx, y), w, H, fill=False, lw=1.5, ec="black"))
            ax.text(cx + (w - 0.30)/2, y + H/2, s, ha="center", va="center", fontsize=10.5)
            sym_mmc(ax, cx + w - 0.17, y + H/2)
            boxes.append((cx, w)); cx += w
    return x, y, cx - x, H

def datum_flag(ax, x, y, letter, down=False):
    ax.add_patch(Rectangle((x, y), 0.40, 0.36, fill=False, lw=1.5, ec="black"))
    ax.text(x + 0.20, y + 0.18, letter, ha="center", va="center",
            fontsize=12, fontweight="bold")
    if not down:
        ax.fill([x + 0.20 - 0.10, x + 0.20 + 0.10, x + 0.20],
                [y + 0.36, y + 0.36, y + 0.36 + 0.20], color="black")
    else:
        ax.fill([x + 0.20 - 0.10, x + 0.20 + 0.10, x + 0.20],
                [y, y, y - 0.20], color="black")

def main(out="drawing_bracket.png"):
    fig, ax = plt.subplots(figsize=(14, 9.5), dpi=150)
    ax.set_xlim(0, 15); ax.set_ylim(0, 9.5); ax.axis("off")

    # ---- bracket body ----
    ax.add_patch(Rectangle((1.1, 2.1), 6.6, 4.6, fill=False, lw=2.0, ec="black"))
    holes = {"H1": (2.3, 5.4), "H2": (6.4, 5.4), "H3": (2.3, 3.2), "H4": (6.4, 3.2)}
    for hid, (hx, hy) in holes.items():
        ax.add_patch(Circle((hx, hy), 0.32, fill=False, lw=1.6, ec="black"))
        ax.plot([hx - 0.46, hx + 0.46], [hy, hy], lw=0.6, color="black")
        ax.plot([hx, hx], [hy - 0.46, hy + 0.46], lw=0.6, color="black")
        ax.text(hx, hy - 0.58, hid, ha="center", va="top", fontsize=9, style="italic")
    ax.add_patch(Circle((4.35, 4.4), 0.40, fill=False, lw=1.6, ec="black"))
    ax.text(4.35, 3.82, "B datum hole", ha="center", va="top", fontsize=8, style="italic")
    ax.add_patch(Circle((5.5, 2.9), 0.25, fill=False, lw=1.4, ec="black"))
    ax.text(5.5, 2.52, "C datum hole", ha="center", va="top", fontsize=8, style="italic")
    ax.add_patch(Circle((3.2, 2.85), 0.28, fill=False, lw=1.8, ec="black"))
    ax.add_patch(Circle((3.2, 2.85), 0.20, fill=False, lw=0.8, ec="black"))
    ax.text(3.2, 2.42, "P1 pin", ha="center", va="top", fontsize=8, style="italic")
    ax.add_patch(Circle((6.7, 4.4), 0.48, fill=False, lw=1.8, ec="black"))
    ax.text(6.7, 3.78, "R1 bore", ha="center", va="top", fontsize=8, style="italic")
    ax.add_patch(Circle((1.75, 2.7), 0.19, fill=False, lw=1.4, ec="black"))
    ax.text(1.75, 2.36, "H5", ha="center", va="top", fontsize=8, style="italic")

    datum_flag(ax, 0.45, 4.1, "A")
    ax.text(0.3, 3.85, "A = back face", fontsize=7.5, ha="left")
    datum_flag(ax, 4.15, 6.85, "B")
    datum_flag(ax, 5.9, 1.7, "C", down=True)

    ax.text(4.35, 4.98, f"B: {DIA}10.00 to 10.06", fontsize=8, ha="center")
    ax.text(5.5, 3.3, f"C: {DIA}6.00 to 6.05", fontsize=8, ha="center")

    # ---- feature control frames (right column), each with a leader ----
    FX = 8.6
    def label(y, s): ax.text(FX, y + 0.46, s, fontsize=8.5)

    label(6.55, "4X mounting holes  H1 H2 H3 H4   (size " + DIA + "8.00 to 8.10)")
    fcf(ax, FX, 6.55, [("sym","position"), ("textmod", f"{DIA}0.20","M"),
                       ("text","A"), ("textmod","B","M"), ("text","C")])
    ax.annotate("", xy=(6.4, 5.6), xytext=(8.6, 6.75), arrowprops=dict(arrowstyle="->", lw=0.9))

    label(5.35, "P1 dowel pin, EXTERNAL   (size " + DIA + "12.00 to 11.90)")
    fcf(ax, FX, 5.35, [("sym","position"), ("textmod", f"{DIA}0.15","M"), ("text","A")])
    ax.annotate("", xy=(3.45, 2.9), xytext=(8.6, 5.55), arrowprops=dict(arrowstyle="->", lw=0.9))

    label(4.15, "R1 precision bore   (size " + DIA + "20.00 to 20.08)")
    fcf(ax, FX, 4.15, [("sym","position"), ("text", f"{DIA}0.10"), ("text","A"), ("text","B")])
    ax.annotate("", xy=(7.15, 4.5), xytext=(8.6, 4.35), arrowprops=dict(arrowstyle="->", lw=0.9))

    label(2.95, "H5 clearance hole   (size " + DIA + "5.00 to 5.06)")
    fcf(ax, FX, 2.95, [("sym","position"), ("textmod", f"{DIA}0.25","M"), ("text","A")])
    ax.annotate("", xy=(1.92, 2.7), xytext=(8.6, 3.15), arrowprops=dict(arrowstyle="->", lw=0.9))

    label(1.75, "S1 profile of top contour")
    fcf(ax, FX, 1.75, [("sym","profile"), ("text","0.30"), ("text","A")])

    label(0.7, "F1 flatness, datum A face")
    fcf(ax, FX, 0.7, [("sym","flatness"), ("text","0.05")])

    # ---- notes ----
    notes = ("NOTES:\n"
             "1. Dimensions in millimeters.  Interpret per ASME Y14.5.\n"
             "2. Position tolerance value is the diameter of the tolerance zone.\n"
             "3. Datums B and C are features of size.  A circled M after a value or\n"
             "   datum letter means that reference is taken at MMC (max material).\n"
             "4. A position callout with no modifier is regardless of feature size (RFS).")
    ax.text(1.1, 1.75, notes, fontsize=7.8, va="top", family="DejaVu Sans")

    # ---- title block ----
    ax.add_patch(Rectangle((0.4, 0.2), 14.2, 0.42, fill=False, lw=1.2))
    ax.text(0.6, 0.41, "BRKT-4471   MOUNTING BRACKET, TRANSMISSION",
            fontsize=10, fontweight="bold", va="center")
    ax.text(10.7, 0.41, "REV C  |  SHEET 1 OF 1  |  MATL A356-T6",
            fontsize=8.5, va="center")

    fig.savefig(out, bbox_inches="tight", facecolor="white")
    print("wrote", out)

if __name__ == "__main__":
    main()
