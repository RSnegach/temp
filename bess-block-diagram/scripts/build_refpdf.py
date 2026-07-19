# -*- coding: utf-8 -*-
"""
Input file 3: one power-block wiring reference (PDF, used directly).
Shows the internal wiring grammar of a single power block plus the labeled
stubs where it ties up to the site section. The model generalizes this one
block to the full system at both build scales. No values, no full system.
No semicolons and no em dashes anywhere in the text.
"""
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
import math

NAVY=HexColor("#1E2D56"); INK=HexColor("#111111"); GREY=HexColor("#5A6472")
RED=HexColor("#C0392B"); BLACK=HexColor("#111111"); BLUE=HexColor("#2A5DB0"); GREEN=HexColor("#1E8449")
W,H=landscape(letter)
c=canvas.Canvas("inputs/BX-SE-SK-104_Power_Block_Wiring.pdf", pagesize=landscape(letter))

def frame():
    c.setStrokeColor(NAVY); c.setLineWidth(1.4); c.rect(24,24,W-48,H-48)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",14); c.drawString(40,H-52,"POWER BLOCK WIRING REFERENCE  (BX-SE-SK-104)")
    c.setFillColor(GREY); c.setFont("Helvetica",9); c.drawString(40,H-68,"Typical of one power block. Every power block is wired identically. Site section is not shown, see the labeled stubs.")

def box(x,y,w,h,label,sub=None,fill="#FFFFFF",tcol=INK):
    c.setLineWidth(1.4); c.setStrokeColor(INK); c.setFillColor(HexColor(fill))
    c.rect(x,y,w,h,stroke=1,fill=1)
    c.setFillColor(tcol); c.setFont("Helvetica-Bold",9)
    c.drawCentredString(x+w/2,y+h/2+(2 if sub else -3),label)
    if sub:
        # sublabel matches the main-label color (white on the dark PCS/DCC boxes)
        subcol = tcol if tcol!=INK else GREY
        c.setFont("Helvetica",7); c.setFillColor(subcol); c.drawCentredString(x+w/2,y+h/2-8,sub)

def line(x1,y1,x2,y2,color,wid=1.8,dash=None):
    c.setStrokeColor(color); c.setLineWidth(wid)
    if dash: c.setDash(*dash)
    c.line(x1,y1,x2,y2); c.setDash()

def arrow(x,y,ang,color):
    c.setFillColor(color); a=math.radians(ang)
    p=c.beginPath(); p.moveTo(x,y)
    p.lineTo(x-8*math.cos(a-0.4),y-8*math.sin(a-0.4)); p.lineTo(x-8*math.cos(a+0.4),y-8*math.sin(a+0.4)); p.close()
    c.drawPath(p,fill=1,stroke=0)

def tag(x,y,t,color,size=8,bold=True,center=False):
    c.setFillColor(color); c.setFont("Helvetica-Bold" if bold else "Helvetica",size)
    (c.drawCentredString if center else c.drawString)(x,y,t)

frame()

# PCS and DCC near the left spine, racks + BMS to the right
pcs=(150,410,96,42); dcc=(150,300,96,42)
box(*pcs,"PCS","inverter",fill="#2A5DB0",tcol=HexColor("#FFFFFF"))
box(*dcc,"DCC","DC combiner",fill="#C0392B",tcol=HexColor("#FFFFFF"))

rack_x=420; bms_x=560; rw,rh=92,38; gap=16
ys=[]
for i in range(4):
    y=470-i*(rh+gap); ys.append(y)
    box(rack_x,y,rw,rh,f"RACK {i+1}",fill="#E8EDF5")
    box(bms_x,y,rw,rh,f"BMS {i+1}",fill="#EAF2EA")

# DC-PWR (red): each rack -> DCC (star), DCC -> PCS
gather=350
for y in ys:
    line(rack_x, y+rh/2, gather, y+rh/2, RED)
line(gather, ys[0]+rh/2, gather, ys[3]+rh/2, RED)
line(gather, dcc[1]+dcc[3]/2, gather, ys[3]+rh/2, RED)
line(dcc[0]+dcc[2], dcc[1]+dcc[3]/2, gather, dcc[1]+dcc[3]/2, RED)
line(dcc[0]+dcc[2]/2, dcc[1]+dcc[3], pcs[0]+pcs[2]/2, pcs[1], RED)
tag(gather-40, ys[3]-16, "DC-PWR  rack to DCC (star), DCC to PCS", RED, 8)

# COMMS (blue): BMS daisy chain, head BMS1 -> PCS
chain=bms_x+rw+16
line(chain, ys[0]+rh/2, chain, ys[3]+rh/2, BLUE)
for y in ys:
    line(bms_x+rw, y+rh/2, chain, y+rh/2, BLUE)
head_y=ys[0]+rh+22
line(chain, ys[0]+rh/2, chain, head_y, BLUE)
line(chain, head_y, pcs[0]+pcs[2]/2, head_y, BLUE)
line(pcs[0]+pcs[2]/2, head_y, pcs[0]+pcs[2]/2, pcs[1]+pcs[3], BLUE)
tag(chain+6, (ys[1]+ys[2])/2+rh/2, "COMMS", BLUE, 8)
tag(bms_x-6, ys[0]+rh+30, "COMMS  BMS daisy chain, head BMS to PCS", BLUE, 8)

# Three site stubs drop to the bottom in three separate lanes so labels do not
# collide. COMMS runs left out of the PCS then turns down like the AUX lane.
aux_x=60; comms_x=110; ac_x=300; stub_y=160

# AUX-24V (green): stubs into PCS and DCC, then down its own lane
line(pcs[0], pcs[1]+pcs[3]/2, aux_x, pcs[1]+pcs[3]/2, GREEN, dash=(4,3))
line(dcc[0], dcc[1]+dcc[3]/2, aux_x, dcc[1]+dcc[3]/2, GREEN, dash=(4,3))
line(aux_x, pcs[1]+pcs[3]/2, aux_x, stub_y, GREEN, dash=(4,3))
arrow(aux_x,stub_y,270,GREEN)
tag(aux_x, stub_y-12, "AUX-24V", GREEN, 8, center=True)
tag(aux_x, stub_y-22, "from AUX-XFMR", GREEN, 7, center=True, bold=False)

# COMMS (blue): out the PCS left edge, run left, then turn down its own lane.
# Tip sits lower than the AUX lane so the two labels never collide.
comms_y=stub_y-46
line(pcs[0], pcs[1]+8, comms_x, pcs[1]+8, BLUE)
line(comms_x, pcs[1]+8, comms_x, comms_y, BLUE)
arrow(comms_x,comms_y,270,BLUE)
tag(comms_x, comms_y-12, "COMMS", BLUE, 8, center=True)
tag(comms_x, comms_y-22, "to Site Controller", BLUE, 7, center=True, bold=False)

# AC-PWR (black): from PCS right edge down its own lane to AC-BUS
line(pcs[0]+pcs[2], pcs[1]+pcs[3]-10, ac_x, pcs[1]+pcs[3]-10, BLACK)
line(ac_x, pcs[1]+pcs[3]-10, ac_x, stub_y, BLACK)
arrow(ac_x,stub_y,270,BLACK)
tag(ac_x, stub_y-12, "AC-PWR", BLACK, 8, center=True)
tag(ac_x, stub_y-22, "to AC-BUS", BLACK, 7, center=True, bold=False)

# legend (lower and to the left, plain white fill with a neutral border)
lx,ly=430,55
c.setFillColor(HexColor("#FFFFFF")); c.setStrokeColor(HexColor("#8899AA")); c.setLineWidth(1.0)
c.rect(lx,ly,190,110,stroke=1,fill=1)
tag(lx+10,ly+92,"HARNESS KEY",INK,9)
for i,(lab,col) in enumerate([("DC-PWR red",RED),("AC-PWR black",BLACK),("COMMS blue",BLUE),("AUX-24V green",GREEN)]):
    yy=ly+72-i*18
    line(lx+12,yy,lx+40,yy,col,2.4)
    tag(lx+48,yy-3,lab,INK,8,bold=False)

c.showPage(); c.save()
print("saved inputs/BX-SE-SK-104_Power_Block_Wiring.pdf")
