# -*- coding: utf-8 -*-
"""
Input file 4: 49-site wafer map reference (clean, for the user to redraw by hand).
Shows the polar site layout, notch reference, edge-exclusion ring, site numbering,
and radial zones. No measured values. Drawn from the same coordinates the engine
uses, so it is geometrically faithful.
"""
import wafer as W
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
import math

NAVY=HexColor("#15324B"); INK=HexColor("#111111"); GREY=HexColor("#666666")
EXCL=HexColor("#C0392B"); INCL=HexColor("#2A6B4F"); LT=HexColor("#AAAAAA")
W_PT,H_PT=letter  # portrait 612 x 792
c=canvas.Canvas("inputs/SP-RS-045_Wafer_Map_Reference.pdf", pagesize=letter)

# frame + title
c.setStrokeColor(NAVY); c.setLineWidth(1.4); c.rect(24,24,W_PT-48,H_PT-48)
c.setFillColor(GREY); c.setFont("Helvetica",8); c.drawString(40,H_PT-42,"PROCESS ENGINEERING - METROLOGY")
c.setFillColor(NAVY); c.setFont("Helvetica-Bold",14); c.drawString(40,H_PT-62,"49-SITE Rs WAFER MAP  (SP-RS-045)")
c.setFillColor(GREY); c.setFont("Helvetica",9); c.drawString(40,H_PT-78,"150 mm wafer, notch at bottom. Site layout reference only - no values.")

# wafer circle centered (sized to leave a clear band below for the legends)
cx,cy=W_PT/2, 500
scale=2.55   # mm -> pt (75mm -> ~191pt radius)
Rpx=W.WAFER_RADIUS_MM*scale
# wafer body
c.setStrokeColor(INK); c.setLineWidth(1.6); c.setFillColor(HexColor("#F4F7F9"))
c.circle(cx,cy,Rpx,stroke=1,fill=1)
# edge exclusion ring (dashed red at r=72)
c.setDash(4,3); c.setStrokeColor(EXCL); c.setLineWidth(1.2)
c.circle(cx,cy,W.EXCL_RADIUS*scale,stroke=1,fill=0); c.setDash()
# notch at bottom
c.setFillColor(INK); c.setStrokeColor(INK)
p=c.beginPath(); p.moveTo(cx-8,cy-Rpx); p.lineTo(cx+8,cy-Rpx); p.lineTo(cx,cy-Rpx+12); p.close()
c.setFillColor(HexColor("#F4F7F9")); c.drawPath(p,stroke=1,fill=1)
c.setFillColor(INK); c.setFont("Helvetica-Bold",8); c.drawCentredString(cx,cy-Rpx-14,"NOTCH (0 deg ref, -y)")

# ring guide circles (faint)
c.setStrokeColor(HexColor("#DDDDDD")); c.setLineWidth(0.7)
for (r,nn,off) in W.RINGS[1:]:
    c.circle(cx,cy,r*scale,stroke=1,fill=0)

# sites
for s in W.SITES:
    x=cx+s["x"]*scale; y=cy+s["y"]*scale
    excl=s["excluded"]
    col=EXCL if excl else INCL
    c.setFillColor(HexColor("#FFFFFF")); c.setStrokeColor(col); c.setLineWidth(1.3)
    rad=7
    c.circle(x,y,rad,stroke=1,fill=1)
    c.setFillColor(col); c.setFont("Helvetica-Bold",6)
    c.drawCentredString(x,y-2.2,str(s["site"]))

# legend box (lower-left, in the clear band below the wafer)
lx,ly=44,150
c.setFillColor(HexColor("#FFF6EC")); c.setStrokeColor(HexColor("#E89B4F")); c.setLineWidth(1.0)
c.rect(lx,ly,300,150,stroke=1,fill=1)
c.setFillColor(INK); c.setFont("Helvetica-Bold",10); c.drawString(lx+12,ly+132,"KEY")
def keyrow(yy,color,txt):
    c.setStrokeColor(color); c.setLineWidth(1.3); c.setFillColor(HexColor("#FFFFFF"))
    c.circle(lx+24,yy,7,stroke=1,fill=1); c.setFillColor(color); c.setFont("Helvetica-Bold",6); c.drawCentredString(lx+24,yy-2.2,"n")
    c.setFillColor(INK); c.setFont("Helvetica",8.5); c.drawString(lx+42,yy-3,txt)
keyrow(ly+108,INCL,"Included site (radius <= 72 mm)")
keyrow(ly+86,EXCL,"Edge-excluded site (radius > 72 mm)")
c.setDash(4,3); c.setStrokeColor(EXCL); c.setLineWidth(1.2); c.line(lx+14,ly+64,lx+36,ly+64); c.setDash()
c.setFillColor(INK); c.setFont("Helvetica",8.5); c.drawString(lx+42,ly+61,"3 mm edge-exclusion boundary")
c.setFont("Helvetica",8); c.setFillColor(GREY)
c.drawString(lx+12,ly+40,"Rings: center=1, R1=8, R2=12, R3=12, R4=16.")
c.drawString(lx+12,ly+28,"Sites numbered center outward, ring by ring,")
c.drawString(lx+12,ly+16,"CCW from the notch reference.")

# radial zone note (lower-right, in the clear band)
rx=W_PT-260; ry=270
c.setFillColor(NAVY); c.setFont("Helvetica-Bold",9); c.drawString(rx,ry,"RADIAL ZONES")
c.setFillColor(GREY); c.setFont("Helvetica",8.5)
for i,t in enumerate(["Center: site 1","Mid: rings 1-2 (sites 2-21)",
                      "Outer included: ring 3 (sites 22-33)","Edge excluded: ring 4 (sites 34-49)"]):
    c.drawString(rx,ry-16-i*14,t)

c.setFillColor(GREY); c.setFont("Helvetica-Oblique",8)
c.drawString(44,64,"Exact site x/y and radius are in the Site_Map sheet of the measurement export. This sketch shows layout and the")
c.drawString(44,52,"exclusion ring only; measured Rs values are not shown here.")

c.showPage(); c.save()
print("saved inputs/SP-RS-045_Wafer_Map_Reference.pdf")
