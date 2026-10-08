"""Extract plain text from pdf/mhtml/docx/xlsx/pages sources into an output dir."""
import email
import io
import re
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET
from email import policy
from html.parser import HTMLParser
from pathlib import Path

SKIP_TAGS = {"script", "style", "noscript", "svg", "head"}
BLOCK_TAGS = {"p", "div", "br", "li", "h1", "h2", "h3", "h4", "h5", "h6", "tr", "section", "article", "td", "th"}


class TextHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in SKIP_TAGS:
            self.skip += 1
        if tag in BLOCK_TAGS:
            self.parts.append("\n")
        if tag in {"h1", "h2", "h3", "h4"}:
            self.parts.append("#" * int(tag[1]) + " ")
        if tag == "li":
            self.parts.append("- ")

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS and self.skip:
            self.skip -= 1
        if tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def clean(text):
    text = re.sub(r"[ \t\xa0]+", " ", text)
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
    return text.strip()


def from_mhtml(path):
    msg = email.message_from_bytes(path.read_bytes(), policy=policy.default)
    for part in msg.walk():
        if part.get_content_type() == "text/html":
            p = TextHTML()
            p.feed(part.get_payload(decode=True).decode("utf-8", errors="replace"))
            return clean("".join(p.parts))
    return ""


def from_pdf(path):
    return subprocess.run(["pdftotext", "-layout", str(path), "-"], capture_output=True, text=True, check=True).stdout


W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def from_docx(path):
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    out = []
    for el in root.find(W + "body"):
        if el.tag == W + "p":
            style = el.find(f"{W}pPr/{W}pStyle")
            prefix = "## " if style is not None and "Heading" in (style.get(W + "val") or "") else ""
            out.append(prefix + "".join(t.text or "" for t in el.iter(W + "t")))
        elif el.tag == W + "tbl":
            for row in el.iter(W + "tr"):
                cells = ["".join(t.text or "" for t in c.iter(W + "t")) for c in row.iter(W + "tc")]
                out.append(" | ".join(cells))
            out.append("")
    return clean("\n".join(out))


S = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def cell_value(c, shared):
    v, f, is_ = c.find(S + "v"), c.find(S + "f"), c.find(S + "is")
    if c.get("t") == "s" and v is not None:
        val = shared[int(v.text)]
    elif is_ is not None:
        val = "".join(t.text or "" for t in is_.iter(S + "t"))
    else:
        val = v.text if v is not None else ""
    if f is not None and f.text:
        val = f"{val} [={f.text}]"
    return val


def from_xlsx(path):
    with zipfile.ZipFile(path) as z:
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")).iter(S + "si"):
                shared.append("".join(t.text or "" for t in si.iter(S + "t")))
        names = [s.get("name") for s in ET.fromstring(z.read("xl/workbook.xml")).iter(S + "sheet")]
        sheets = [n for n in z.namelist() if re.match(r"xl/worksheets/sheet\d+\.xml", n)]
        sheets.sort(key=lambda n: int(re.search(r"(\d+)", n.split("/")[-1]).group(1)))
        out = []
        for name, sheet in zip(names, sheets):
            out.append(f"### SHEET: {name}")
            for row in ET.fromstring(z.read(sheet)).iter(S + "row"):
                vals = [f"{c.get('r')}: {val}" for c in row.iter(S + "c") if (val := cell_value(c, shared))]
                if vals:
                    out.append(" | ".join(vals))
        return "\n".join(out)


def read_varint(data, pos):
    value, shift = 0, 0
    while True:
        b = data[pos]
        pos += 1
        value |= (b & 0x7F) << shift
        shift += 7
        if not b & 0x80:
            return value, pos


def snappy_decompress(data):
    _, pos = read_varint(data, 0)
    out = bytearray()
    while pos < len(data):
        tag = data[pos]
        pos += 1
        kind = tag & 3
        if kind == 0:
            ln = tag >> 2
            if ln >= 60:
                nb = ln - 59
                ln = int.from_bytes(data[pos:pos + nb], "little")
                pos += nb
            ln += 1
            out += data[pos:pos + ln]
            pos += ln
            continue
        if kind == 1:
            ln = ((tag >> 2) & 7) + 4
            off = ((tag >> 5) << 8) | data[pos]
            pos += 1
        elif kind == 2:
            ln = (tag >> 2) + 1
            off = int.from_bytes(data[pos:pos + 2], "little")
            pos += 2
        else:
            ln = (tag >> 2) + 1
            off = int.from_bytes(data[pos:pos + 4], "little")
            pos += 4
        for _ in range(ln):
            out.append(out[-off])
    return bytes(out)


def iwa_decode(raw):
    out, pos = bytearray(), 0
    while pos < len(raw):
        ln = int.from_bytes(raw[pos + 1:pos + 4], "little")
        out += snappy_decompress(raw[pos + 4:pos + 4 + ln])
        pos += 4 + ln
    return bytes(out)


def from_pages(path):
    """path is a .pages directory or a zip that contains Index.zip."""
    if path.is_dir():
        index = zipfile.ZipFile(path / "Index.zip")
    else:
        outer = zipfile.ZipFile(path)
        name = next(n for n in outer.namelist() if n.endswith("Index.zip"))
        index = zipfile.ZipFile(io.BytesIO(outer.read(name)))
    data = iwa_decode(index.read("Index/Document.iwa"))
    runs = re.findall(rb"(?:[\x20-\x7e\n]|[\xc2-\xf4][\x80-\xbf]+){30,}", data)
    return "\n".join(r.decode("utf-8", "ignore") for r in runs)


HANDLERS = {".pdf": from_pdf, ".mhtml": from_mhtml, ".docx": from_docx, ".xlsx": from_xlsx}

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for arg in sys.argv[2:]:
        src = Path(arg)
        handler = HANDLERS.get(src.suffix.lower(), from_pages)
        try:
            text = handler(src)
        except Exception as exc:  # report and continue with the remaining files
            print(f"FAIL {src}: {exc!r}", file=sys.stderr)
            continue
        rel = src.parent.name + "__" + src.stem
        target = out_dir / (re.sub(r"[^\w.-]+", "_", rel)[:120] + ".txt")
        target.write_text(text)
        print(f"{len(text):>8}  {target.name}")
