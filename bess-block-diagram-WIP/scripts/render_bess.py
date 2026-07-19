# -*- coding: utf-8 -*-
"""
Grid-art renderer for the BESS block diagram.
Builds ONE grid model per configuration from topology.py, then emits it two ways:
  - a PIL PNG (visual proof / preview)
  - the golden xlsx sheet (blocks = merged cells, harness runs = colored fill
    cells, labels = colored text, plus a legend)
Both emitters read the same model, so the PNG faithfully previews the workbook.

Layout = bus-with-taps (how real single-lines draw shared site harnesses):
  - Site column at far left (SC, AUX-XFMR, AC-BUS, MTR, MV-XFMR, and AC-CMB in
    the extended build).
  - Vertical harness trunks just right of the site column: COMMS (blue) off SC,
    AUX (green) off AUX-XFMR, AC (black) off AC-BUS, and a short AC-CMB trunk.
  - Power-block clusters stacked vertically to the right. Each cluster is wired
    locally: DC star racks->DCC (red), DCC->PCS (red), BMS daisy chain (blue),
    head BMS->PCS (blue). Site harnesses tap into each PCS/DCC from the trunks.
"""
import topology as T

# harness colors (match the harness-rules doc key)
COL = {
    "DC-PWR": "C0392B",   # red
    "AC-PWR": "111111",   # black
    "COMMS":  "2A5DB0",   # blue
    "AUX-24V":"1E8449",   # green
}
BLOCK_FILL = {
    "SC":"1E2D56","AUXX":"1E8449","MVX":"5A5A5A","MTR":"6B4E9E","BUS":"2C3E50",
    "CMB":"8A5A2B","PCS":"2A5DB0","DCC":"C0392B","RK":"E8EDF5","BMS":"EAF2EA",
}
BLOCK_TEXT_LIGHT = {"SC","AUXX","MVX","MTR","BUS","CMB","PCS","DCC"}  # white text


class Grid:
    def __init__(self):
        self.blocks=[]          # dict(r0,c0,r1,c1,label,type)
        self.lines={}           # (r,c) -> color hex  (colored fill = line segment)
        self.labels=[]          # dict(r,c,text,color)
        self.maxr=0; self.maxc=0

    def _bump(self,r,c):
        self.maxr=max(self.maxr,r); self.maxc=max(self.maxc,c)

    def block(self,r,c,h,w,label,typ):
        self.blocks.append(dict(r0=r,c0=c,r1=r+h-1,c1=c+w-1,label=label,type=typ))
        self._bump(r+h-1,c+w-1)
        return dict(r=r,c=c,h=h,w=w,label=label)

    def hline(self,r,c0,c1,color):
        for c in range(min(c0,c1),max(c0,c1)+1):
            self.lines[(r,c)]=color; self._bump(r,c)

    def vline(self,c,r0,r1,color):
        for r in range(min(r0,r1),max(r0,r1)+1):
            self.lines[(r,c)]=color; self._bump(r,c)

    def label(self,r,c,text,color):
        self.labels.append(dict(r=r,c=c,text=text,color=color)); self._bump(r,c)


# ---- geometry constants (grid cells) ----
BH=3            # block height in cells
SITE_W=12       # site block width
PCS_W=12
RK_W=12
BMS_W=12

def build_grid(n_blocks):
    g=Grid()
    # ---- trunk lane columns (between site column and clusters) ----
    site_c=2
    comms_trunk=site_c+SITE_W+2      # blue
    aux_trunk=comms_trunk+2          # green
    ac_trunk=aux_trunk+2             # black
    accmb_trunk=ac_trunk+2           # black (extended only)
    cluster_c=accmb_trunk+4          # clusters start here

    # ---- cluster geometry ----
    # within a cluster: PCS at (cr, cluster_c), DCC below it; racks column; BMS column
    rk_pitch=BH+2
    cluster_h=4*rk_pitch+2           # enough for 4 racks
    cluster_gap=4
    dcc_dc_lane=cluster_c+PCS_W+3    # red vertical gather lane for DC star
    rk_c=dcc_dc_lane+3
    bms_c=rk_c+RK_W+6
    bms_chain=bms_c-3                # blue vertical daisy lane

    has_cmb = n_blocks>T.BUS_FEEDER_POSITIONS

    # ---- power block clusters (top to bottom) ----
    first_cluster_r=6
    pcs_rows={}; dcc_rows={}; pcs_anchor={}
    for n in range(1,n_blocks+1):
        cr=first_cluster_r+(n-1)*(cluster_h+cluster_gap)
        pcs_r=cr
        dcc_r=cr+rk_pitch
        g.block(pcs_r,cluster_c,BH,PCS_W,f"PCS-{n:02d}","PCS")
        g.block(dcc_r,cluster_c,BH,PCS_W,f"DCC-{n:02d}","DCC")
        pcs_rows[n]=pcs_r; dcc_rows[n]=dcc_r
        pcs_mid=pcs_r+BH//2; dcc_mid=dcc_r+BH//2
        pcs_anchor[n]=pcs_mid

        # racks + bms
        rk_mid=[]; bms_mid=[]
        for i in range(4):
            rr=cr+i*rk_pitch
            g.block(rr,rk_c,BH,RK_W,f"RK-{n}-{i+1}","RK")
            g.block(rr,bms_c,BH,BMS_W,f"BMS-{n}-{i+1}","BMS")
            rk_mid.append(rr+BH//2); bms_mid.append(rr+BH//2)

        # DC star: each rack left edge -> red gather lane -> DCC right edge
        for i in range(4):
            g.hline(rk_mid[i], dcc_dc_lane, rk_c-1, COL["DC-PWR"])
        g.vline(dcc_dc_lane, min(rk_mid), max(rk_mid), COL["DC-PWR"])
        # connect gather lane to DCC (into DCC right edge at dcc_mid)
        g.vline(dcc_dc_lane, dcc_mid, min(rk_mid), COL["DC-PWR"])
        g.hline(dcc_mid, cluster_c+PCS_W, dcc_dc_lane, COL["DC-PWR"])
        # DC: DCC -> PCS (short vertical on the left third)
        dcpc=cluster_c+2
        g.vline(dcpc, pcs_r+BH, dcc_r-1, COL["DC-PWR"])
        g.hline(pcs_r+BH-1, cluster_c+1, dcpc, COL["DC-PWR"])   # stub into PCS bottom
        g.hline(dcc_r, cluster_c+1, dcpc, COL["DC-PWR"])        # stub into DCC top

        # COMMS daisy: consecutive BMS linked on the blue chain lane
        g.vline(bms_chain, bms_mid[0], bms_mid[3], COL["COMMS"])
        for i in range(4):
            g.hline(bms_mid[i], bms_chain, bms_c-1, COL["COMMS"])
        # head BMS (i=0) -> PCS: up to a top comms row, across to PCS right edge
        head_row=cr-2
        g.vline(bms_chain, head_row, bms_mid[0], COL["COMMS"])
        g.hline(head_row, cluster_c+PCS_W, bms_chain, COL["COMMS"])
        g.vline(cluster_c+PCS_W-1, pcs_r, head_row, COL["COMMS"])  # into PCS top-right
        # DC-PWR label in the blank row between racks 2 and 3 (guaranteed clear)
        g.label((rk_mid[1]+rk_mid[2])//2, dcc_dc_lane-2, "DC-PWR", COL["DC-PWR"])

        # ---- site harness taps into this cluster ----
        # AUX green: trunk -> PCS left, and trunk -> DCC left
        g.hline(pcs_mid, aux_trunk, cluster_c-1, COL["AUX-24V"])
        g.hline(dcc_mid, aux_trunk, cluster_c-1, COL["AUX-24V"])
        # COMMS blue: PCS -> comms trunk (uplink to SC)
        g.hline(pcs_r, comms_trunk, cluster_c-1, COL["COMMS"])
        # AC black: PCS -> ac trunk (blocks 1-3 or <=4) OR accmb trunk (4+ when cmb)
        ac_target = accmb_trunk if (has_cmb and n>T.DIRECT_BLOCK_LIMIT) else ac_trunk
        g.hline(pcs_mid, ac_target, cluster_c-1, COL["AC-PWR"])

    # ---- site column blocks ----
    # vertical order: SC, AUX-XFMR, AC-BUS, MTR, MV-XFMR, (AC-CMB)
    site_specs=[("SC-01","SC"),("AUX-XFMR","AUXX"),("AC-BUS","BUS"),
                ("MTR-01","MTR"),("MV-XFMR","MVX")]
    if has_cmb: site_specs.append(("AC-CMB","CMB"))
    # spread site blocks down the left over the full height
    total_h=g.maxr
    site_rows={}
    sr=6
    site_pitch=max(6,(total_h-6)//max(1,len(site_specs)))
    for i,(lab,typ) in enumerate(site_specs):
        rr=6+i*site_pitch
        g.block(rr,site_c,BH,SITE_W,lab,typ)
        site_rows[lab]=rr+BH//2

    # trunks (vertical) down the lanes, spanning the cluster range
    top=4; bot=g.maxr
    g.vline(comms_trunk, site_rows["SC-01"], bot-2, COL["COMMS"])
    g.vline(aux_trunk, site_rows["AUX-XFMR"], bot-2, COL["AUX-24V"])
    g.vline(ac_trunk, top+2, site_rows["AC-BUS"], COL["AC-PWR"])
    # connect trunks into their site blocks (from block right edge to lane)
    g.hline(site_rows["SC-01"], site_c+SITE_W, comms_trunk, COL["COMMS"])
    g.hline(site_rows["AUX-XFMR"], site_c+SITE_W, aux_trunk, COL["AUX-24V"])
    g.hline(site_rows["AC-BUS"], site_c+SITE_W, ac_trunk, COL["AC-PWR"])

    # AC trunk needs to actually reach every tap row: extend down to lowest AC tap
    lowest_ac = max(pcs_anchor[n] for n in range(1,n_blocks+1)
                    if not (has_cmb and n>T.DIRECT_BLOCK_LIMIT))
    g.vline(ac_trunk, site_rows["AC-BUS"], lowest_ac, COL["AC-PWR"])
    # comms trunk reach lowest PCS top
    g.vline(comms_trunk, site_rows["SC-01"], max(pcs_rows.values()), COL["COMMS"])
    # aux trunk reach lowest DCC
    g.vline(aux_trunk, site_rows["AUX-XFMR"], max(dcc_rows.values())+1, COL["AUX-24V"])

    # AC-CMB handling (extended): PCS4/5 -> accmb trunk -> AC-CMB -> AC-BUS
    if has_cmb:
        cmb_row=site_rows["AC-CMB"]
        hi_taps=[pcs_anchor[n] for n in range(1,n_blocks+1) if n>T.DIRECT_BLOCK_LIMIT]
        g.vline(accmb_trunk, min(hi_taps), max(hi_taps), COL["AC-PWR"])
        # accmb trunk down to AC-CMB block
        g.vline(accmb_trunk, min(hi_taps), cmb_row, COL["AC-PWR"])
        g.hline(cmb_row, site_c+SITE_W, accmb_trunk, COL["AC-PWR"])
        # AC-CMB -> AC-BUS (route along a dedicated lower path back to AC-BUS block)
        link_c=site_c+SITE_W//2
        g.vline(link_c, site_rows["AC-BUS"], cmb_row, COL["AC-PWR"])

    # site-level AC: AC-BUS -> MTR -> MV-XFMR ; COMMS: MTR -> SC
    busm=site_rows["AC-BUS"]; mtrm=site_rows["MTR-01"]; mvm=site_rows["MV-XFMR"]; scm=site_rows["SC-01"]
    linkc=site_c+SITE_W//2
    g.vline(linkc, busm, mtrm, COL["AC-PWR"])
    g.vline(linkc, mtrm, mvm, COL["AC-PWR"])
    # MTR -> SC comms: run left of the site column
    lc=site_c-1
    g.hline(mtrm, lc, site_c-1, COL["COMMS"])
    g.vline(lc, scm, mtrm, COL["COMMS"])
    g.hline(scm, lc, site_c-1, COL["COMMS"])

    return g, dict(site_c=site_c, comms_trunk=comms_trunk, aux_trunk=aux_trunk,
                   ac_trunk=ac_trunk, cluster_c=cluster_c)


# ============================ PIL emitter ============================
def render_png(g, path, title):
    from PIL import Image, ImageDraw, ImageFont
    CELL=13
    padL=10; padT=54; padR=10; padB=10
    Wpx=padL+(g.maxc+2)*CELL+padR
    Hpx=padT+(g.maxr+2)*CELL+padB
    img=Image.new("RGB",(Wpx,Hpx),"white"); d=ImageDraw.Draw(img)
    def font(sz,bold=False):
        try:
            return ImageFont.truetype("arialbd.ttf" if bold else "arial.ttf", sz)
        except Exception:
            return ImageFont.load_default()
    def hx(h): return tuple(int(h[i:i+2],16) for i in (0,2,4))
    # title
    d.text((padL,16), title, fill=hx("1E2D56"), font=font(20,True))
    def cx(c): return padL+c*CELL
    def cy(r): return padT+r*CELL
    # lines (colored fill cells)
    for (r,c),col in g.lines.items():
        d.rectangle([cx(c),cy(r),cx(c)+CELL-1,cy(r)+CELL-1], fill=hx(col))
    # blocks
    for b in g.blocks:
        x0,y0=cx(b["c0"]),cy(b["r0"]); x1,y1=cx(b["c1"])+CELL-1,cy(b["r1"])+CELL-1
        fill=hx(BLOCK_FILL[b["type"]])
        d.rectangle([x0,y0,x1,y1], fill=fill, outline=hx("111111"), width=2)
        tcol=(255,255,255) if b["type"] in BLOCK_TEXT_LIGHT else (17,17,17)
        f=font(12,True)
        tb=d.textbbox((0,0),b["label"],font=f)
        tw=tb[2]-tb[0]; th=tb[3]-tb[1]
        d.text(((x0+x1)/2-tw/2,(y0+y1)/2-th/2-2), b["label"], fill=tcol, font=f)
    # labels
    for lb in g.labels:
        if not lb["text"]: continue
        d.text((cx(lb["c"]),cy(lb["r"])-1), lb["text"], fill=hx(lb["color"]), font=font(11,True))
    # legend
    lx=Wpx-230; ly=padT+6
    d.rectangle([lx,ly,lx+210,ly+96], fill=hx("FFF6EC"), outline=hx("E89B4F"), width=1)
    d.text((lx+10,ly+6),"HARNESS KEY",fill=(17,17,17),font=font(12,True))
    for i,(k,lab) in enumerate([("DC-PWR","DC-PWR (red)"),("AC-PWR","AC-PWR (black)"),
                                 ("COMMS","COMMS (blue)"),("AUX-24V","AUX-24V (green)")]):
        yy=ly+28+i*17
        d.rectangle([lx+12,yy,lx+40,yy+8], fill=hx(COL[k]))
        d.text((lx+48,yy-3),lab,fill=(17,17,17),font=font(11))
    img.save(path)
    print("saved", path, img.size)


if __name__ == "__main__":
    gA,_=build_grid(T.STANDARD_BLOCKS)
    render_png(gA,"preview_standard.png","BESS Block Diagram - Standard Build (3 power blocks)")
    gB,_=build_grid(T.EXTENDED_BLOCKS)
    render_png(gB,"preview_extended.png","BESS Block Diagram - Extended Build (5 power blocks)")
    print("standard grid:", gA.maxr,"x",gA.maxc, "blocks", len(gA.blocks))
    print("extended grid:", gB.maxr,"x",gB.maxc, "blocks", len(gB.blocks))
