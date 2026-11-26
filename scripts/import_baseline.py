"""Import the approved opening unit into an empty baseline; preserve reviewed edits."""
import hashlib
import html
import json
import posixpath
import subprocess
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
deck = ROOT / "marchev_risk_all_2019.pptx"
pdf = ROOT / "extracted" / deck.with_suffix(".pdf").name
manifest = ROOT / "manifests/sources.json"
groups = [(1, 3, "index", "Някои идеи за риска"),
          (4, 17, "chapters/introduction", "Въведение"),
          (18, 32, "chapters/risk", "Какво е РИСК?")]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def paragraphs(node):
    return ["".join(t.text or "" for t in p.iter() if t.tag.endswith("}t"))
            for p in node.findall(".//{*}p")]


def relationships(package, path):
    folder, name = posixpath.split(path)
    rels = posixpath.join(folder, "_rels", name + ".rels")
    return {r.get("Id"): r for r in ET.fromstring(package.read(rels))}


def main():
    if manifest.exists() or any((ROOT / (name + ".qmd")).exists() for _, _, name, _ in groups):
        raise SystemExit("Existing baseline found. Generate in a fresh checkout and review the diff.")
    checksum = digest(deck.read_bytes())
    if (ROOT / "reports/original.sha256").read_text().split()[0] != checksum:
        raise SystemExit("Source changed. Review before importing.")
    images = ROOT / "assets/images"
    subprocess.run(["pdftoppm", "-f", "1", "-l", "32", "-scale-to", "1440",
                    "-png", str(pdf), str(images / "slide")], check=True)
    records = []
    with zipfile.ZipFile(deck) as package:
        presentation = ET.fromstring(package.read("ppt/presentation.xml"))
        links = relationships(package, "ppt/presentation.xml")
        ordered = [links[next(v for k,v in s.attrib.items() if k.endswith("}id"))].get("Target")
                   for s in presentation.find("{*}sldIdLst")]
        for first, last, name, title in groups:
            lines = ["# " + title, ""]
            for i in range(first, last + 1):
                path = "ppt/" + ordered[i-1]
                slide = ET.fromstring(package.read(path))
                raw = paragraphs(slide)
                body = [s.strip() for s in raw if s.strip() and s.strip() not in
                        {"3.12.2023 г.", "<number>"} and not s.startswith("Creative commons")]
                heading = body[0] if body and len(body[0]) < 66 else f"Слайд {i}"
                lines.extend([f"## {html.escape(heading)} {{#slide-{i:03}}}", ""])
                for s in body[int(bool(body) and body[0] == heading):]:
                    lines.extend(["<p>" + html.escape(s) + "</p>", ""])
                asset = next(images.glob(f"slide-*{i:03}.png"))
                prefix = "../" if "/" in name else ""
                lines.extend([f"![{html.escape(heading)} · слайд {i}]({prefix}assets/images/{asset.name}){{.slide}}", ""])
                deps = []
                for r in relationships(package, path).values():
                    target = r.get("Target")
                    kind = r.get("Type").split("/")[-1]
                    item = {"type":kind, "target":target}
                    if r.get("TargetMode") == "External":
                        if target.startswith(("https://","http://")):
                            lines.extend([f"<{target}>", ""])
                    else:
                        data = package.read(posixpath.normpath(posixpath.join("ppt/slides",target)))
                        item["sha256"] = digest(data)
                        if kind == "notesSlide":
                            item["private_notes"] = paragraphs(ET.fromstring(data))
                    deps.append(item)
                records.append(dict(slide=i, xml=path, anchor=f"{name}.qmd#slide-{i:03}",
                                    asset=asset.name, sha256=digest(asset.read_bytes()), dependencies=deps,
                                    shapes=[n.attrib for n in slide.findall(".//{*}cNvPr")],
                                    animation=slide.find("{*}timing") is not None,
                                    status="transformed; visual review pending"))
            (ROOT / (name + ".qmd")).write_text("\n".join(lines), encoding="utf8")
    manifest.write_text(json.dumps(dict(source=deck.name,sha256=checksum,slides=records),
                                   ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
