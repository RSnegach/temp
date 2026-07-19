"""
Single source of truth for the BESS block-diagram task.
Implements the block taxonomy and the four harness connection rules, then
generates the complete block inventory and harness edge list for both build
configurations (standard = 3 power blocks, extended = 5 power blocks).

The input files (taxonomy doc, harness-rules doc, one-block sketch) describe
these rules in prose. The golden diagram renders exactly what this generator
produces. Running this file prints the deterministic counts used by the rubric.

Harness rules (mirror the File 2 prose):
  DC-PWR : within each power block, every Battery Rack home-runs to that block's
           DC Combiner (star, K links); each DC Combiner feeds its block's PCS
           (1 link).  Per block: K + 1.
  AC-PWR : each PCS makes one AC feeder. The AC Collection Bus is a 4-position
           feeder lineup. In a build of 4 or fewer power blocks, each PCS lands
           on its own bus position directly. In a larger build, positions 1-3
           are landed by power blocks 1-3, and the 4th position is occupied by
           an AC Combiner Panel (AC-CMB) that aggregates every power block
           numbered 4 and higher (each of those PCS feeds AC-CMB, and AC-CMB
           makes one feeder to the bus). Bus -> Metering -> MV step-up transformer.
  COMMS  : within each power block the K Rack BMS units form a daisy chain
           BMS-n-1 -> BMS-n-2 -> ... -> BMS-n-K (K-1 links); the head BMS-n-1
           reports to that block's PCS (1 link); each PCS home-runs to the Site
           Controller (1 link). Metering also home-runs to the Site Controller.
  AUX-24V: the Aux Transformer feeds each PCS and each DC Combiner in a star
           (2 per block) and the Site Controller (1). Racks, BMS, bus, metering,
           MV transformer and the AC Combiner Panel are NOT aux-fed.
"""

K_RACKS = 4          # racks (and rack BMS) per power block
STANDARD_BLOCKS = 3
EXTENDED_BLOCKS = 5
BUS_FEEDER_POSITIONS = 4   # AC collection bus lineup positions -> drives the extended exception
DIRECT_BLOCK_LIMIT = 3     # blocks 1..3 land on the bus directly; 4+ go via AC-CMB when a CMB exists

# block type keys and human labels
TYPES = {
    "SC":  "Site Controller",
    "AUXX":"Aux Transformer",
    "MVX": "MV Step-up Transformer",
    "MTR": "Revenue Metering",
    "BUS": "AC Collection Bus",
    "CMB": "AC Combiner Panel",
    "PCS": "Power Conversion System",
    "DCC": "DC Combiner",
    "RK":  "Battery Rack",
    "BMS": "Rack BMS",
}

HARNESSES = ["DC-PWR", "AC-PWR", "COMMS", "AUX-24V"]


def build(n_blocks):
    """Return (blocks, edges) for a build with n_blocks power blocks.

    blocks: list of dict(id, type, block=n or None, k=k or None)
    edges:  list of dict(a, b, harness)
    """
    blocks = []
    edges = []

    # ---- site-level singletons (exist once, regardless of scale) ----
    blocks.append(dict(id="SC-01",    type="SC",   block=None, k=None))
    blocks.append(dict(id="AUX-XFMR", type="AUXX", block=None, k=None))
    blocks.append(dict(id="MV-XFMR",  type="MVX",  block=None, k=None))
    blocks.append(dict(id="MTR-01",   type="MTR",  block=None, k=None))
    blocks.append(dict(id="AC-BUS",   type="BUS",  block=None, k=None))

    # AC Combiner Panel only exists when blocks exceed the bus feeder positions
    has_cmb = n_blocks > BUS_FEEDER_POSITIONS
    if has_cmb:
        blocks.append(dict(id="AC-CMB", type="CMB", block=None, k=None))

    # ---- per power block ----
    for n in range(1, n_blocks + 1):
        pcs = f"PCS-{n:02d}"
        dcc = f"DCC-{n:02d}"
        blocks.append(dict(id=pcs, type="PCS", block=n, k=None))
        blocks.append(dict(id=dcc, type="DCC", block=n, k=None))
        racks = []
        bmss = []
        for k in range(1, K_RACKS + 1):
            rk = f"RK-{n}-{k}"
            bms = f"BMS-{n}-{k}"
            blocks.append(dict(id=rk,  type="RK",  block=n, k=k))
            blocks.append(dict(id=bms, type="BMS", block=n, k=k))
            racks.append(rk); bmss.append(bms)

        # DC-PWR: rack -> DCC (star), DCC -> PCS
        for rk in racks:
            edges.append(dict(a=rk, b=dcc, harness="DC-PWR"))
        edges.append(dict(a=dcc, b=pcs, harness="DC-PWR"))

        # COMMS: BMS daisy chain, head -> PCS, PCS -> SC
        for i in range(len(bmss) - 1):
            edges.append(dict(a=bmss[i], b=bmss[i + 1], harness="COMMS"))
        edges.append(dict(a=bmss[0], b=pcs, harness="COMMS"))       # head uplink
        edges.append(dict(a=pcs, b="SC-01", harness="COMMS"))       # PCS home-run

        # AUX-24V: aux -> PCS, aux -> DCC
        edges.append(dict(a="AUX-XFMR", b=pcs, harness="AUX-24V"))
        edges.append(dict(a="AUX-XFMR", b=dcc, harness="AUX-24V"))

        # AC-PWR: PCS feeder. If a combiner exists, blocks 1..3 land on the bus
        # directly and blocks 4+ aggregate through the AC-CMB. With no combiner
        # (<=4 blocks), every PCS lands on the bus directly.
        if has_cmb and n > DIRECT_BLOCK_LIMIT:
            edges.append(dict(a=pcs, b="AC-CMB", harness="AC-PWR"))
        else:
            edges.append(dict(a=pcs, b="AC-BUS", harness="AC-PWR"))

    # ---- site-level harness edges (once) ----
    if has_cmb:
        edges.append(dict(a="AC-CMB", b="AC-BUS", harness="AC-PWR"))
    edges.append(dict(a="AC-BUS", b="MTR-01", harness="AC-PWR"))
    edges.append(dict(a="MTR-01", b="MV-XFMR", harness="AC-PWR"))
    edges.append(dict(a="MTR-01", b="SC-01", harness="COMMS"))
    edges.append(dict(a="AUX-XFMR", b="SC-01", harness="AUX-24V"))

    return blocks, edges


def counts(blocks, edges):
    bt = {}
    for b in blocks:
        bt[b["type"]] = bt.get(b["type"], 0) + 1
    et = {}
    for e in edges:
        et[e["harness"]] = et.get(e["harness"], 0) + 1
    return bt, et


def report(name, n_blocks):
    blocks, edges = build(n_blocks)
    bt, et = counts(blocks, edges)
    print(f"\n=== {name}  ({n_blocks} power blocks, K={K_RACKS}) ===")
    print("  blocks by type:")
    for t in ["SC","AUXX","MVX","MTR","BUS","CMB","PCS","DCC","RK","BMS"]:
        if t in bt:
            print(f"    {t:5s} {TYPES[t]:26s} {bt[t]}")
    print(f"  TOTAL BLOCKS: {len(blocks)}")
    print("  edges by harness:")
    for h in HARNESSES:
        print(f"    {h:8s} {et.get(h,0)}")
    print(f"  TOTAL EDGES: {len(edges)}")
    return blocks, edges


if __name__ == "__main__":
    report("STANDARD (Version A)", STANDARD_BLOCKS)
    report("EXTENDED (Version B)", EXTENDED_BLOCKS)

    # spot-check specific adjacencies used in the rubric
    print("\n--- spot checks (extended) ---")
    _, e5 = build(EXTENDED_BLOCKS)
    def has(a, b, h): return any(x["a"]==a and x["b"]==b and x["harness"]==h for x in e5)
    print("  RK-5-4 -> DCC-05 (DC-PWR):", has("RK-5-4","DCC-05","DC-PWR"))
    print("  BMS-3-1 -> BMS-3-2 (COMMS daisy):", has("BMS-3-1","BMS-3-2","COMMS"))
    print("  BMS-3-1 -> PCS-03 (COMMS head uplink):", has("BMS-3-1","PCS-03","COMMS"))
    print("  PCS-04 -> AC-CMB (AC exception):", has("PCS-04","AC-CMB","AC-PWR"))
    print("  PCS-05 -> AC-CMB (AC exception):", has("PCS-05","AC-CMB","AC-PWR"))
    print("  PCS-03 -> AC-BUS (direct):", has("PCS-03","AC-BUS","AC-PWR"))
    print("  AC-CMB -> AC-BUS:", has("AC-CMB","AC-BUS","AC-PWR"))
    print("  AUX-XFMR -> BMS-1-1 should be FALSE:", has("AUX-XFMR","BMS-1-1","AUX-24V"))
    # confirm no rack/bms is aux-fed
    aux_targets = {x["b"] for x in e5 if x["harness"]=="AUX-24V"}
    bad = [t for t in aux_targets if t.startswith("RK-") or t.startswith("BMS-")]
    print("  aux-fed racks/bms (should be []):", bad)
