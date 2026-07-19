# -*- coding: utf-8 -*-
"""
Input file 4: decision-flow graph of the rule engine (clean reference for the
user to redraw by hand). Shows the engine as branching true/false decision
diamonds along a spine, with R5 decomposed into TWO gates (score, then dti) that
the rules table hides as one row. Terminals are the five outcomes. This exposes
the branch/path structure the model must cover; it does not restate the table.
"""
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
import math

NAVY=HexColor("#1F385C"); INK=HexColor("#111111"); GREY=HexColor("#666666")
TRUE_C=HexColor("#B23A2E"); FALSE_C=HexColor("#2A5DB0")
DEC_FILL=HexColor("#EAF0FA"); TERM_DECLINE=HexColor("#F7D9D5"); TERM_APP=HexColor("#DCEEDF")
TERM_REF=HexColor("#FBF0D5")
W,H=landscape(letter)
c=canvas.Canvas("inputs/LPQ-482-FLOW_Decision_Flow_Graph.pdf", pagesize=landscape(letter))

def title():
    c.setStrokeColor(NAVY); c.setLineWidth(1.4); c.rect(24,24,W-48,H-48)
    bx,by,bw,bh=W-24-300,24,300,60
    c.setLineWidth(1.0); c.setStrokeColor(INK); c.rect(bx,by,bw,bh)
    c.line(bx,by+40,bx+bw,by+40); c.line(bx+200,by,bx+200,by+40)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",10); c.drawString(bx+8,by+46,"DECISION FLOW - RULE ENGINE")
    c.setFillColor(INK); c.setFont("Helvetica",8)
    c.drawString(bx+8,by+26,"LoanPreQual  |  Release 2.4"); c.drawString(bx+8,by+14,"HAND SKETCH - PATH MAP")
    c.setFont("Helvetica-Bold",8); c.drawString(bx+208,by+26,"DWG"); c.setFont("Helvetica",8)
    c.drawString(bx+208,by+14,"LPQ-482-FLOW"); c.drawString(bx+208,by+2,"REV 1")
    c.setFillColor(GREY); c.setFont("Helvetica",8); c.drawString(40,H-40,"QUALITY ASSURANCE - TEST DESIGN")
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",13); c.drawString(40,H-58,"RULE ENGINE DECISION FLOW (applies to VALID records only)")

def diamond(cx,cy,w,h,label,sub=None):
    c.setLineWidth(1.4); c.setStrokeColor(INK); c.setFillColor(DEC_FILL)
    p=c.beginPath(); p.moveTo(cx,cy+h/2); p.lineTo(cx+w/2,cy); p.lineTo(cx,cy-h/2); p.lineTo(cx-w/2,cy); p.close()
    c.drawPath(p,stroke=1,fill=1)
    c.setFillColor(INK); c.setFont("Helvetica-Bold",8.5); c.drawCentredString(cx,cy+(3 if sub else -3),label)
    if sub:
        c.setFont("Helvetica",7); c.setFillColor(GREY); c.drawCentredString(cx,cy-7,sub)

def term(cx,cy,label,fill):
    w,h=104,30
    c.setLineWidth(1.4); c.setStrokeColor(INK); c.setFillColor(fill)
    c.rect(cx-w/2,cy-h/2,w,h,stroke=1,fill=1)
    c.setFillColor(INK); c.setFont("Helvetica-Bold",8.5); c.drawCentredString(cx,cy-3,label)

def line(x1,y1,x2,y2,color,width=1.6):
    c.setStrokeColor(color); c.setLineWidth(width); c.line(x1,y1,x2,y2)

def arrow(x,y,ang,color):
    c.setFillColor(color); a=math.radians(ang)
    p=c.beginPath(); p.moveTo(x,y)
    p.lineTo(x-8*math.cos(a-0.4),y-8*math.sin(a-0.4)); p.lineTo(x-8*math.cos(a+0.4),y-8*math.sin(a+0.4)); p.close()
    c.drawPath(p,fill=1,stroke=0)

def lbl(x,y,t,color,size=7.5,bold=True,center=True):
    c.setFillColor(color); c.setFont("Helvetica-Bold" if bold else "Helvetica",size)
    (c.drawCentredString if center else c.drawString)(x,y,t)

title()

# spine of decision diamonds (top to bottom), false-exit continues down, true-exit branches right
spine_x=210
top=H-118
dy=56
dw,dh=118,44
nodes=[
 ("D1","emp = Unemployed?","R1"),
 ("D2","score < 620?","R2"),
 ("D3","DTI > 43.0?","R3"),
 ("D4","loan > 5x income?","R4"),
 ("D5","score >= 720?","R5 gate 1"),
 ("D6","DTI <= 36.0?","R5 gate 2"),
 ("D7","score >= 660?","R6"),
]
ys=[top-i*dy for i in range(len(nodes))]

# entry (placed left of the spine so it never sits on D1)
lbl(spine_x-4, top+40, "VALID RECORD", INK, 9)
lbl(spine_x-4, top+30, "(all fields passed validation)", GREY, 7.5, bold=False)
line(spine_x, top+26, spine_x, top+dh/2, INK); arrow(spine_x, top+dh/2, 270, INK)

term_x=470
for i,(nid,q,rule) in enumerate(nodes):
    cy=ys[i]
    diamond(spine_x,cy,dw,dh,f"{nid}: {q}",rule)
    # FALSE exit downward to next node (except after D7)
    if nid!="D7":
        ny=ys[i+1]
        # D5 false skips D6 and goes straight to D7 (score<720 cannot be prime)
        if nid=="D5":
            # false: go down-left around D6 to D7
            lx=spine_x-90
            line(spine_x-dw/2, cy, lx, cy, FALSE_C)
            line(lx, cy, lx, ys[6], FALSE_C)
            line(lx, ys[6], spine_x-dw/2, ys[6], FALSE_C); arrow(spine_x-dw/2, ys[6], 0, FALSE_C)
            lbl(lx, (cy+ys[6])/2, "F", FALSE_C, 8)
            lbl(lx-2, (cy+ys[6])/2-10, "(not prime)", FALSE_C, 6.5, bold=False)
            # true exit downward to D6
            line(spine_x, cy-dh/2, spine_x, ys[5]+dh/2, TRUE_C); arrow(spine_x, ys[5]+dh/2, 270, TRUE_C)
            lbl(spine_x+10, (cy+ys[5])/2, "T", TRUE_C, 8, center=False)
        else:
            line(spine_x, cy-dh/2, spine_x, ny+dh/2, FALSE_C); arrow(spine_x, ny+dh/2, 270, FALSE_C)
            lbl(spine_x+10, (cy+ny)/2, "F", FALSE_C, 8, center=False)

# TRUE exits to terminals on the right
def true_to(cy, tx, ty, label, fill):
    line(spine_x+dw/2, cy, tx-52, ty, TRUE_C)
    arrow(tx-52, ty, 0, TRUE_C)
    term(tx, ty, label, fill)
    lbl((spine_x+dw/2+tx-52)/2, (cy+ty)/2+4, "T", TRUE_C, 8)

true_to(ys[0], term_x, ys[0], "DECLINE (R1)", TERM_DECLINE)
true_to(ys[1], term_x, ys[1], "DECLINE (R2)", TERM_DECLINE)
true_to(ys[2], term_x, ys[2], "DECLINE (R3)", TERM_DECLINE)
true_to(ys[3], term_x, ys[3], "DECLINE (R4)", TERM_DECLINE)
# D6 true -> APPROVE_PRIME ; D6 false -> continues to D7 (false path down)
true_to(ys[5], term_x, ys[5], "APPROVE_PRIME (R5)", TERM_APP)
# D6 FALSE -> down to D7
line(spine_x, ys[5]-dh/2, spine_x, ys[6]+dh/2, FALSE_C); arrow(spine_x, ys[6]+dh/2, 270, FALSE_C)
lbl(spine_x+10,(ys[5]+ys[6])/2,"F",FALSE_C,8,center=False)
# D7 true -> APPROVE_STANDARD ; false -> REFER
true_to(ys[6], term_x, ys[6], "APPROVE_STANDARD (R6)", TERM_APP)
line(spine_x, ys[6]-dh/2, spine_x, ys[6]-dh/2-24, FALSE_C)
line(spine_x, ys[6]-dh/2-24, term_x-52, ys[6]-dh/2-24, FALSE_C); arrow(term_x-52, ys[6]-dh/2-24, 0, FALSE_C)
term(term_x, ys[6]-dh/2-24, "REFER (R7 default)", TERM_REF)
lbl(spine_x+10, ys[6]-dh/2-14, "F", FALSE_C, 8, center=False)

# legend
lx,ly=980,470
c.setFillColor(HexColor("#FFF6EC")); c.setStrokeColor(HexColor("#E89B4F")); c.setLineWidth(1.0)
c.rect(lx,ly,190,120,stroke=1,fill=1)
lbl(lx+95,ly+104,"KEY",INK,9)
line(lx+14,ly+86,lx+42,ly+86,TRUE_C,2.2); lbl(lx+50,ly+83,"T = condition true",INK,8,bold=False,center=False)
line(lx+14,ly+68,lx+42,ly+68,FALSE_C,2.2); lbl(lx+50,ly+65,"F = condition false",INK,8,bold=False,center=False)
c.setFillColor(DEC_FILL); c.rect(lx+14,ly+44,20,12,stroke=1,fill=1); lbl(lx+50,ly+46,"decision (diamond)",INK,8,bold=False,center=False)
c.setFillColor(TERM_APP); c.rect(lx+14,ly+24,20,12,stroke=1,fill=1); lbl(lx+50,ly+26,"outcome (terminal)",INK,8,bold=False,center=False)
lbl(lx+95,ly+8,"R5 = two gates (D5 then D6)",NAVY,7,center=True)

# note (right side, above the key box, clear of everything)
c.setFillColor(GREY); c.setFont("Helvetica-Oblique",8)
nx,ny=980,700
c.drawString(nx,ny,"Evaluated top to bottom; the first true")
c.drawString(nx,ny-11,"branch wins. R5 is two sequential gates:")
c.drawString(nx,ny-22,"score gate (D5) then DTI gate (D6).")
c.drawString(nx,ny-37,"Validation runs BEFORE this graph. A record")
c.drawString(nx,ny-48,"that fails validation is rejected and never")
c.drawString(nx,ny-59,"enters the flow. Every diamond has T and F exits.")

c.showPage(); c.save()
print("saved inputs/LPQ-482-FLOW_Decision_Flow_Graph.pdf")
