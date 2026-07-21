# -*- coding: utf-8 -*-
"""
Hand-drawn one-power-block wiring reference (reference render). This REPLACES the
clean vector PDF as the only wiring reference the solver gets, so it must carry
the full one-block wiring grammar:

  DC-PWR (red):   each of the 4 racks runs individually to the DC combiner
                  (a star, not a loop), and the DC combiner runs to the PCS.
  COMMS  (blue):  the 4 rack BMS are a DAISY CHAIN BMS1-BMS2-BMS3-BMS4; the head
                  BMS1 runs to the PCS; the PCS uplinks to the Site Controller.
  AUX-24V (green):the aux transformer feeds the PCS and the DC combiner (2 stubs).
  AC-PWR (black): the PCS feeds the AC collection bus.
  Plus the three labeled site stubs (to AC-BUS, to Site Controller, from AUX-XFMR).

Deliberately loose pen-and-paper look: handwriting font, wobbled strokes, a
hand-ruled harness key, and a couple of margin notes. This is a REFERENCE render;
the shipped input is a photographed redraw of the same content. The topology it
shows is identical to topology.py, so the golden is unchanged.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import Rectangle

def pick_font():
    prefer = ["Comic Sans MS", "Segoe Print", "Ink Free", "Bradley Hand", "Comic Neue"]
    avail = {f.name for f in fm.fontManager.ttflist}
    for p in prefer:
        if p in avail:
            return p
    return None
HAND = pick_font()

INK = "#1a1a1a"
RED = "#b02a20"; BLACK = "#111111"; BLUE = "#204a9a"; GREEN = "#1c7a3e"

_rng = np.random.default_rng(11)

def _wob(x1, y1, x2, y2, amp=0.9, n=24):
    xs = np.linspace(x1, x2, n); ys = np.linspace(y1, y2, n)
    # perpendicular jitter so lines look hand-drawn but stay readable
    dx, dy = x2 - x1, y2 - y1
    L = max(1e-6, (dx*dx + dy*dy) ** 0.5)
    px, py = -dy / L, dx / L
    j = _rng.normal(0, amp, n); j[0] = j[-1] = 0
    return xs + px * j, ys + py * j

def seg(ax, x1, y1, x2, y2, color, lw=2.0, dash=False, amp=0.9):
    xs, ys = _wob(x1, y1, x2, y2, amp=amp)
    kw = dict(color=color, lw=lw, solid_capstyle="round")
    if dash:
        kw["dashes"] = (4, 3)
    ax.plot(xs, ys, **kw)

def poly(ax, pts, color, lw=2.0, dash=False, amp=0.9):
    for i in range(len(pts) - 1):
        seg(ax, pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], color, lw, dash, amp=amp)

def hand_box(ax, x, y, w, h, label, sub=None, lw=2.0):
    # four wobbled edges
    poly(ax, [(x,y),(x+w,y),(x+w,y+h),(x,y+h),(x,y)], INK, lw=lw, amp=0.6)
    ax.text(x+w/2, y+h/2+(3 if sub else 0), label, ha="center", va="center",
            fontsize=12, fontweight="bold", color=INK,
            fontfamily=HAND if HAND else None)
    if sub:
        ax.text(x+w/2, y+h/2-9, sub, ha="center", va="center", fontsize=8,
                color="#555", fontfamily=HAND if HAND else None)

def arrow(ax, x, y, ang, color):
    a = np.radians(ang)
    for da in (-0.42, 0.42):
        ax.plot([x, x - 12*np.cos(a+da)], [y, y - 12*np.sin(a+da)],
                color=color, lw=2.0, solid_capstyle="round")

def txt(ax, x, y, s, size=11, color=INK, bold=True, rot=0, ha="left"):
    ax.text(x, y, s, fontsize=size, color=color, rotation=rot, ha=ha, va="center",
            fontweight="bold" if bold else "normal",
            fontfamily=HAND if HAND else None)

def main(png="previews/refsketch_preview.png", pdf="inputs/BX-SE-SK-104_Power_Block_Wiring.pdf"):
    fig, ax = plt.subplots(figsize=(13, 9.2), dpi=150)
    ax.set_xlim(0, 1300); ax.set_ylim(0, 920); ax.axis("off")
    ax.set_facecolor("#f7f4ea"); fig.patch.set_facecolor("#f7f4ea")

    # header
    txt(ax, 55, 872, "PWR BLOCK WIRING  -  typ. 1 of N   (SK-104)", size=19)
    txt(ax, 55, 842, "one power block, wired identical every block. site NOT shown - see stubs.",
        size=11, color="#555", bold=False)

    # ---- blocks ----
    # left spine: PCS over DCC
    pcs = (150, 560, 120, 60); dcc = (150, 420, 120, 60)
    hand_box(ax, *pcs, "PCS", "inverter")
    hand_box(ax, *dcc, "DCC", "DC comb")
    # racks + BMS columns
    rack_x, bms_x, rw, rh, gap = 560, 800, 120, 52, 26
    ys = []
    for i in range(4):
        y = 640 - i*(rh+gap); ys.append(y)
        hand_box(ax, rack_x, y, rw, rh, f"RACK {i+1}")
        hand_box(ax, bms_x, y, rw, rh, f"BMS {i+1}")
    rmid = [y + rh/2 for y in ys]

    # ---- DC-PWR (red): each rack -> gather lane -> DCC ; DCC -> PCS ----
    gather = 470
    for y in rmid:
        seg(ax, rack_x, y, gather, y, RED)
    seg(ax, gather, rmid[0], gather, rmid[3], RED)              # gather spine
    seg(ax, gather, rmid[3], dcc[0]+dcc[2], dcc[1]+dcc[3]/2, RED)  # into DCC right
    # DCC -> PCS (up the left)
    seg(ax, dcc[0]+dcc[2]/2, dcc[1]+dcc[3], pcs[0]+pcs[2]/2, pcs[1], RED)
    txt(ax, 470, 300, "DC-PWR: each rack -> DCC (star), DCC -> PCS", size=10, color=RED)

    # ---- COMMS (blue): BMS daisy chain, head BMS1 -> PCS ----
    chain = bms_x + rw + 30
    # short stubs out of each BMS to the chain lane
    for y in rmid:
        seg(ax, bms_x+rw, y, chain, y, BLUE)
    # chain spine linking consecutive BMS (the daisy)
    seg(ax, chain, rmid[0], chain, rmid[3], BLUE)
    # head BMS1 -> up and across to PCS top-right
    head_y = rmid[0] + 70
    seg(ax, chain, rmid[0], chain, head_y, BLUE)
    seg(ax, chain, head_y, pcs[0]+pcs[2]-10, head_y, BLUE)
    seg(ax, pcs[0]+pcs[2]-10, head_y, pcs[0]+pcs[2]-10, pcs[1]+pcs[3], BLUE)
    txt(ax, chain+8, (rmid[1]+rmid[2])/2, "daisy", size=10, color=BLUE)
    txt(ax, 720, head_y+16, "COMMS: BMS1-BMS2-BMS3-BMS4 chain, head BMS1 -> PCS", size=10, color=BLUE)

    # ---- AUX-24V (green dashed): AUX-XFMR -> PCS and DCC ----
    aux_x = 60
    seg(ax, pcs[0], pcs[1]+pcs[3]/2, aux_x, pcs[1]+pcs[3]/2, GREEN, dash=True)
    seg(ax, dcc[0], dcc[1]+dcc[3]/2, aux_x, dcc[1]+dcc[3]/2, GREEN, dash=True)
    seg(ax, aux_x, pcs[1]+pcs[3]/2, aux_x, 210, GREEN, dash=True)
    arrow(ax, aux_x, 210, 270, GREEN)
    txt(ax, aux_x-8, 196, "AUX-24V", size=10, color=GREEN, ha="left")
    txt(ax, aux_x-8, 180, "from AUX-XFMR", size=8, color=GREEN, bold=False)

    # ---- COMMS site stub: PCS -> Site Controller ----
    comms_x = 320
    seg(ax, pcs[0]+8, pcs[1], comms_x, pcs[1], BLUE)
    seg(ax, comms_x, pcs[1], comms_x, 165, BLUE)
    arrow(ax, comms_x, 165, 270, BLUE)
    txt(ax, comms_x-8, 151, "COMMS", size=10, color=BLUE)
    txt(ax, comms_x-8, 135, "to Site Controller", size=8, color=BLUE, bold=False)

    # ---- AC-PWR site stub: PCS -> AC-BUS ----
    ac_x = 210
    seg(ax, pcs[0]+pcs[2], pcs[1]+10, ac_x+120, pcs[1]+10, BLACK)
    seg(ax, ac_x+120, pcs[1]+10, ac_x+120, 235, BLACK)
    arrow(ax, ac_x+120, 235, 270, BLACK)
    txt(ax, ac_x+112, 221, "AC-PWR", size=10, color=BLACK)
    txt(ax, ac_x+112, 205, "to AC-BUS", size=8, color=BLACK, bold=False)

    # ---- margin notes (crew hand) ----
    txt(ax, 560, 250, "note: racks NOT looped - each its own run to DCC", size=9, color="#5a3020", bold=False)
    txt(ax, 560, 232, "note: BMS chained in series, only head talks to PCS", size=9, color="#5a3020", bold=False)
    txt(ax, 560, 214, "note: aux feeds PCS + DCC only (not racks/BMS)", size=9, color="#5a3020", bold=False)

    # ---- hand-ruled harness key ----
    kx, ky = 980, 120
    poly(ax, [(kx,ky),(kx+250,ky),(kx+250,ky+150),(kx,ky+150),(kx,ky)], INK, lw=1.6, amp=0.4)
    txt(ax, kx+14, ky+130, "HARNESS KEY", size=11)
    for i,(lab,col) in enumerate([("DC-PWR  red",RED),("AC-PWR  black",BLACK),
                                   ("COMMS  blue",BLUE),("AUX-24V  green",GREEN)]):
        yy = ky+100 - i*26
        seg(ax, kx+16, yy, kx+64, yy, col, lw=2.6, dash=(col==GREEN))
        txt(ax, kx+76, yy, lab, size=9, color=INK, bold=False)

    fig.savefig(png, bbox_inches="tight", facecolor=fig.get_facecolor())
    # wrap the PNG full-page into the PDF (photographed-sketch as the input file)
    from PIL import Image
    im = Image.open(png).convert("RGB")
    im.save(pdf, "PDF", resolution=150.0)
    print("saved", png, "and", pdf, "| hand font:", HAND)

if __name__ == "__main__":
    main()
