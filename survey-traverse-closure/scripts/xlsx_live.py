# -*- coding: utf-8 -*-
"""
Helper to add LIVE formula cells to an openpyxl workbook while also injecting a
cached result value into the saved XML, so the value is visible without opening
Excel and Excel still recalculates the real formula on open.

Cached values are emitted as fixed-decimal strings (num) or integers (int) or
escaped text (str), so there are never trailing floating-point tails in the
stored <v>. Compute the cached value the same way the formula does so the two
agree; on open Excel recomputes and the number format keeps the display clean.
"""
import zipfile, shutil, re


def set_excel_fingerprint(path, application="Microsoft Excel", creator="Engineering"):
    """Scrub generator fingerprints: set the docProps/app.xml Application tag and
    the docProps/core.xml creator/lastModifiedBy so neither names openpyxl.
    Namespace-free string edits, safe."""
    zin = zipfile.ZipFile(path, "r")
    tmp = path + ".tmp"
    out = zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED)
    for it in zin.infolist():
        data = zin.read(it.filename)
        if it.filename == "docProps/app.xml":
            t = data.decode("utf-8")
            if "<Application>" in t:
                t = re.sub(r"<Application>.*?</Application>",
                           f"<Application>{application}</Application>", t)
            data = t.encode("utf-8")
        elif it.filename == "docProps/core.xml":
            t = data.decode("utf-8")
            # tolerate inline namespace attrs on the tags (e.g. <dc:creator xmlns:dc="...">)
            t = re.sub(r"(<dc:creator\b[^>]*>).*?(</dc:creator>)", rf"\g<1>{creator}\g<2>", t)
            t = re.sub(r"(<cp:lastModifiedBy\b[^>]*>).*?(</cp:lastModifiedBy>)", rf"\g<1>{creator}\g<2>", t)
            data = t.encode("utf-8")
        out.writestr(it, data)
    out.close(); zin.close()
    shutil.move(tmp, path)


def normalize_decimals(path, max_dp=6):
    """Rewrite every numeric <v> in the worksheets to its shortest clean decimal,
    removing binary float tails like 84.93000000000001 -> 84.93. Integer values
    and text values are left untouched. Lossless when the intended precision is
    within max_dp (verify before calling)."""
    zin = zipfile.ZipFile(path, "r")
    def fix(txt):
        def repl(m):
            v = m.group(1)
            if not re.fullmatch(r"-?\d+\.\d+", v):   # only plain decimals
                return m.group(0)
            f = round(float(v), max_dp)
            s = f"{f:.{max_dp}f}".rstrip("0").rstrip(".")
            if s in ("", "-0"):
                s = "0"
            return f"<v>{s}</v>"
        return re.sub(r"<v>([^<]+)</v>", repl, txt)
    tmp = path + ".tmp"
    out = zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED)
    for it in zin.infolist():
        data = zin.read(it.filename)
        if re.match(r"xl/worksheets/sheet\d+\.xml", it.filename):
            data = fix(data.decode("utf-8")).encode("utf-8")
        out.writestr(it, data)
    out.close(); zin.close()
    shutil.move(tmp, path)


class LiveCells:
    """Accumulates (sheet_title, coord) -> (formula_registered, cached, kind, dp)."""
    def __init__(self):
        self.reg = {}   # (title, coord) -> (cached_value, kind, dp)

    def set(self, ws, coord, formula, cached, kind="num", dp=2,
            number_format=None, font=None, fill=None, align=None, border=None):
        c = ws[coord]
        c.value = formula                      # the live formula
        if number_format: c.number_format = number_format
        if font: c.font = font
        if fill: c.fill = fill
        if align: c.alignment = align
        if border: c.border = border
        self.reg[(ws.title, coord)] = (cached, kind, dp)
        return c

    def _emit(self, cached, kind, dp):
        if kind == "int":
            return str(int(round(cached)))
        if kind == "str":
            return None  # handled by caller (needs t="str")
        return f"{cached:.{dp}f}"

    def inject(self, path):
        """Post-process the saved xlsx: append <v> to each registered formula cell."""
        zin = zipfile.ZipFile(path, "r")
        wbxml = zin.read("xl/workbook.xml").decode("utf-8")
        rels = zin.read("xl/_rels/workbook.xml.rels").decode("utf-8")
        # sheet name -> r:id
        name_rid = {}
        for tag in re.findall(r"<sheet\b[^>]*?/?>", wbxml):
            nm = re.search(r'\bname="([^"]+)"', tag)
            rid = re.search(r'r:id="([^"]+)"', tag)
            if nm and rid:
                name_rid[nm.group(1)] = rid.group(1)
        rid_target = {}
        for tag in re.findall(r"<Relationship\b[^>]*?/?>", rels):
            i = re.search(r'\bId="([^"]+)"', tag)
            t = re.search(r'\bTarget="([^"]+)"', tag)
            if i and t:
                rid_target[i.group(1)] = t.group(1)
        title_to_file = {}
        for name, rid in name_rid.items():
            tgt = rid_target.get(rid, "")
            if tgt.startswith("/"): tgt = tgt[1:]
            elif not tgt.startswith("xl/"): tgt = "xl/" + tgt.lstrip("./")
            title_to_file[name] = tgt

        per_file = {}
        for (title, coord), (cached, kind, dp) in self.reg.items():
            f = title_to_file.get(title)
            if not f:
                raise RuntimeError(f"sheet {title!r} not found; have {list(title_to_file)}")
            per_file.setdefault(f, {})[coord] = (cached, kind, dp)

        def esc(s):
            return (s.replace("&", "&amp;").replace("<", "&lt;")
                     .replace(">", "&gt;").replace('"', "&quot;"))

        def patch(txt, cmap):
            def repl(m):
                cell = m.group(0)
                cm = re.search(r'\br="([A-Z]+\d+)"', cell)
                if not cm or cm.group(1) not in cmap:
                    return cell
                if "<f>" not in cell and "<f " not in cell:
                    return cell
                cached, kind, dp = cmap[cm.group(1)]
                cell = re.sub(r"<v>.*?</v>", "", cell, flags=re.S)   # drop any stale v
                if kind == "str":
                    open_tag = re.match(r"<c\b[^>]*>", cell).group(0)
                    if ' t="' not in open_tag:
                        cell = cell.replace(open_tag, open_tag[:-1] + ' t="str">', 1)
                    v = f"<v>{esc(str(cached))}</v>"
                else:
                    v = f"<v>{self._emit(cached, kind, dp)}</v>"
                return cell.replace("</c>", v + "</c>", 1)
            return re.sub(r"<c\b[^>]*>.*?</c>", repl, txt, flags=re.S)

        tmp = path + ".tmp"
        out = zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED)
        for it in zin.infolist():
            data = zin.read(it.filename)
            if it.filename in per_file:
                data = patch(data.decode("utf-8"), per_file[it.filename]).encode("utf-8")
            out.writestr(it, data)
        out.close(); zin.close()
        shutil.move(tmp, path)
        return len(self.reg), len(per_file)
