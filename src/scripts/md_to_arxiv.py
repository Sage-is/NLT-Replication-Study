#!/usr/bin/env python3
"""Convert an Obsidian-flavored Markdown paper into an arXiv-ready LaTeX package.

arXiv requires LaTeX source (not Markdown, not author-compiled PDF-from-LaTeX),
compiling on their TeX Live with no shell-escape, all figures included, and an
abstract of at most 1,920 characters for the metadata field. This script takes
the vault Markdown as the source of truth and programmatically handles the
Obsidian/Notion-export quirks on every run, so the paper can keep being edited
in Obsidian and re-converted at will:

  * ``![[image.png]]`` embeds        -> figures resolved from the assets dir,
                                        with trailing italic lines folded into
                                        the LaTeX caption
  * Notion-mangled pipe tables       -> rows re-joined, separator row inserted
  * bogus autolinks (http://x.py/)   -> rewritten to repo blob URLs
  * relative links (./docs/x.md)     -> rewritten to repo blob URLs
  * LaTeX-hostile Unicode (x, >=, -) -> mapped to math/ASCII outside code fences
  * title / authors / date metadata  -> extracted from the header block
  * abstract                         -> extracted into \\begin{abstract}

Pipeline: preprocess -> pandoc -> postprocess .tex -> copy figures ->
compile check (if a TeX engine is installed) -> validate -> tarball.

Usage:
    python src/scripts/md_to_arxiv.py                 # defaults for this repo
    python src/scripts/md_to_arxiv.py --input PAPER.md --output-dir arxiv
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

ABSTRACT_METADATA_LIMIT = 1920  # arXiv abstract field hard limit (characters)

# Unicode that pdflatex's default utf8 setup cannot typeset. Applied outside
# code fences only. Characters LaTeX handles natively (curly quotes, em/en
# dashes, accented latin) are deliberately left alone.
UNICODE_MAP = {
    " ": " ",  # non-breaking space (Notion export artifact)
    "×": " $\\times$ ",  # multiplication sign
    "−": "-",  # minus sign
    "≥": "$\\geq$",  # greater-than-or-equal
    "≤": "$\\leq$",  # less-than-or-equal
    "Δ": "$\\Delta$",  # capital delta
    "†": "$\\dagger$",  # dagger (table footnote marker)
    "→": "$\\rightarrow$",
    "✓": "\\checkmark{}",
}

# Bogus autolinks produced by the Notion/Obsidian export, e.g.
# [evaluator.py](http://evaluator.py/) — the filename got autolinked as a host.
BOGUS_PY_LINK = re.compile(r"\]\(http://([A-Za-z0-9_.-]+\.py)/?\)")
# Relative or pseudo-relative links, e.g. (./assets/x.py) or (http://./docs/x.md)
RELATIVE_LINK = re.compile(r"\]\((?:http://)?\./([^)\s]+)\)")

OBSIDIAN_EMBED = re.compile(r"^!\[\[([^\]]+)\]\]\s*$")
ITALIC_LINE = re.compile(r"^\*[^*].*\*$")
FENCE = re.compile(r"^(```|~~~)")


def split_code_fences(lines: list[str]) -> list[tuple[bool, list[str]]]:
    """Split lines into (in_code_fence, chunk) runs so transforms can skip code."""
    chunks: list[tuple[bool, list[str]]] = []
    current: list[str] = []
    in_fence = False
    for line in lines:
        if FENCE.match(line.strip()):
            current.append(line)
            if in_fence:
                chunks.append((True, current))
                current = []
                in_fence = False
            else:
                if current[:-1]:
                    chunks.append((False, current[:-1]))
                current = [line]
                in_fence = True
            continue
        current.append(line)
    if current:
        chunks.append((in_fence, current))
    return chunks


def map_unicode(text: str) -> str:
    for src, dst in UNICODE_MAP.items():
        text = text.replace(src, dst)
    return text


def rewrite_links(text: str, repo_url: str, branch: str) -> str:
    blob = f"{repo_url.rstrip('/')}/blob/{branch}"
    text = BOGUS_PY_LINK.sub(lambda m: f"]({blob}/src/nlt/core/{m.group(1)})", text)
    text = RELATIVE_LINK.sub(lambda m: f"]({blob}/{m.group(1)})", text)
    return text


def repair_split_tables(lines: list[str]) -> list[str]:
    """Re-join pipe-table rows that a Notion export split across blank lines.

    A well-formed row has the same number of ``|`` separators as the header.
    When a row line ends with ``|`` but is short of the header's pipe count,
    subsequent fragment lines (cell text, blank lines, continuation ``| .. |``)
    are folded into it until the pipe count balances. A separator row
    (``|---|...``) is inserted after the header when missing.
    """
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|") and stripped.count("|") >= 3:
            header_pipes = stripped.count("|")
            table: list[str] = [stripped]
            i += 1
            # Collect the rest of the table region (rows, fragments, blanks).
            while i < len(lines):
                nxt = lines[i].strip()
                if not nxt:
                    # Blank line: part of a broken row only if the row below
                    # continues the table; peek ahead.
                    j = i + 1
                    while j < len(lines) and not lines[j].strip():
                        j += 1
                    if j < len(lines) and ("|" in lines[j] or _is_cell_fragment(lines[j])):
                        i = j
                        continue
                    break
                if "|" in nxt or _is_cell_fragment(lines[i]):
                    table.append(nxt)
                    i += 1
                    continue
                break
            out.extend(_rebuild_table(table, header_pipes))
            # Escape a footnote-marker line (e.g. "* Partial data. ...") right
            # after a table so pandoc doesn't render it as a one-item list.
            j = i
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and re.match(r"^\*\s+\S", lines[j].strip()) and not lines[j].strip().startswith("**"):
                lines[j] = "\\" + lines[j].lstrip()
            continue
        out.append(line)
        i += 1
    return out


def _is_cell_fragment(line: str) -> bool:
    """A short bare-text line (e.g. '+43.1pp') orphaned from a split table row."""
    s = line.strip()
    return bool(s) and "|" not in s and len(s) <= 40 and not s.startswith(("#", "-", "*", ">", "`"))


def _rebuild_table(raw: list[str], header_pipes: int) -> list[str]:
    rows: list[str] = []
    acc = ""
    for piece in raw:
        acc = f"{acc} {piece}".strip() if acc else piece
        if acc.count("|") >= header_pipes and acc.endswith("|"):
            rows.append(re.sub(r"\s+\|", " |", acc))
            acc = ""
    if acc:
        rows.append(acc)

    if len(rows) >= 2 and not re.match(r"^\|[\s:-]+\|", rows[1]):
        # Pandoc sizes columns from the separator row's dash proportions, so
        # give each column dashes proportional to its widest cell content.
        cells_per_row = [[c.strip() for c in r.strip("|").split("|")] for r in rows]
        ncols = len(cells_per_row[0])
        widths = [max((len(r[c]) for r in cells_per_row if len(r) > c), default=3) for c in range(ncols)]
        rows.insert(1, "|" + "|".join("-" * max(w, 3) for w in widths) + "|")
    return rows + [""]


def convert_embeds(lines: list[str], assets_dir: Path) -> tuple[list[str], list[str]]:
    """Turn ``![[img]]`` into pandoc figures; fold trailing italic lines into captions."""
    out: list[str] = []
    figures: list[str] = []
    i = 0
    while i < len(lines):
        m = OBSIDIAN_EMBED.match(lines[i].strip())
        if not m:
            out.append(lines[i])
            i += 1
            continue
        name = m.group(1)
        if not (assets_dir / name).exists():
            raise FileNotFoundError(f"embedded image not found: {assets_dir / name}")
        figures.append(name)
        caption_parts: list[str] = []
        j = i + 1
        while j < len(lines) and ITALIC_LINE.match(lines[j].strip()):
            caption_parts.append(lines[j].strip().strip("*").strip())
            j += 1
        caption = " ".join(caption_parts)
        out.append(f"![{caption}]({name}){{width=90%}}")
        out.append("")
        i = j
    return out, figures


def extract_header(lines: list[str]) -> tuple[dict[str, str], list[str]]:
    """Pull title (setext H1), subtitle (setext H2), and the Authors code fence."""
    meta: dict[str, str] = {}
    body = list(lines)

    for idx in range(len(body) - 1):
        if re.match(r"^=+\s*$", body[idx + 1]) and body[idx].strip():
            meta["title"] = body[idx].strip()
            body[idx] = body[idx + 1] = ""
            break
    for idx in range(len(body) - 1):
        if re.match(r"^-+\s*$", body[idx + 1]) and body[idx].strip() and "title" in meta:
            if body[idx].strip() != meta["title"]:
                meta["subtitle"] = body[idx].strip()
                body[idx] = body[idx + 1] = ""
                break

    for idx, line in enumerate(body[:40]):
        if FENCE.match(line.strip()):
            for end in range(idx + 1, min(idx + 12, len(body))):
                if FENCE.match(body[end].strip()):
                    block = body[idx + 1 : end]
                    if any("Authors:" in b for b in block):
                        for b in block:
                            if ":" in b:
                                key, _, val = b.partition(":")
                                meta[key.strip().lower()] = val.strip()
                        for k in range(idx, end + 1):
                            body[k] = ""
                    break
            if "authors" in meta:
                break
    return meta, body


def extract_abstract(lines: list[str]) -> tuple[str, list[str]]:
    """Take the first paragraph of the ``Abstract`` setext section as the abstract."""
    for idx in range(len(lines) - 1):
        if lines[idx].strip() == "Abstract" and re.match(r"^-+\s*$", lines[idx + 1]):
            start = idx + 2
            while start < len(lines) and not lines[start].strip():
                start += 1
            end = start
            while end < len(lines) and lines[end].strip():
                end += 1
            abstract = " ".join(l.strip() for l in lines[start:end])
            del lines[idx:end]
            return abstract, lines
    return "", lines


def preprocess(md: str, assets_dir: Path, repo_url: str, branch: str) -> tuple[str, dict[str, str], list[str]]:
    lines = md.splitlines()
    meta, lines = extract_header(lines)
    abstract, lines = extract_abstract(lines)
    meta["abstract"] = abstract

    processed: list[str] = []
    all_figures: list[str] = []
    for in_code, chunk in split_code_fences(lines):
        if in_code:
            processed.extend(chunk)
            continue
        text = "\n".join(chunk)
        text = map_unicode(text)
        text = rewrite_links(text, repo_url, branch)
        chunk_lines = repair_split_tables(text.splitlines())
        chunk_lines, figures = convert_embeds(chunk_lines, assets_dir)
        all_figures.extend(figures)
        processed.extend(chunk_lines)

    return "\n".join(processed) + "\n", meta, all_figures


def build_metadata_block(meta: dict[str, str]) -> str:
    def q(s: str) -> str:
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'

    out = ["---", f"title: {q(meta.get('title', 'Untitled'))}"]
    if meta.get("subtitle"):
        out.append(f"subtitle: {q(meta['subtitle'])}")
    if meta.get("authors"):
        out.append("author:")
        for a in [x.strip() for x in meta["authors"].split(",") if x.strip()]:
            out.append(f"  - {q(a)}")
    if meta.get("date"):
        out.append(f"date: {q(meta['date'])}")
    if meta.get("abstract"):
        out.append("abstract: |")
        out.append("  " + meta["abstract"])
    out += [
        "geometry: margin=1in",
        "fontsize: 11pt",
        "colorlinks: true",
        "linkcolor: blue",
        "urlcolor: blue",
        "---",
        "",
    ]
    return "\n".join(out)


def run_pandoc(md_path: Path, tex_path: Path) -> None:
    cmd = [
        "pandoc",
        str(md_path),
        "--from",
        "markdown+smart+link_attributes+pipe_tables+implicit_figures",
        "--to",
        "latex",
        "--standalone",
        "--shift-heading-level-by=-1",
        "--wrap=preserve",
        "-o",
        str(tex_path),
    ]
    subprocess.run(cmd, check=True)


def postprocess_tex(tex_path: Path, affiliation: str | None) -> None:
    tex = tex_path.read_text(encoding="utf-8")
    if affiliation:
        # Pandoc joins authors with \and, which the article class renders as
        # side-by-side boxes — a line break appended there lands inside the
        # LAST author's box, so the affiliation looks like it belongs to that
        # one author. Collapse the authors into a single comma-separated block
        # so the shared affiliation centers under the whole author line.
        tex = re.sub(
            r"\\author\{(.*?)\}",
            lambda m: "\\author{"
            + re.sub(r"\s*\\and\s*", ", ", m.group(1))
            + r" \\[4pt] \normalsize "
            + affiliation
            + "}",
            tex,
            count=1,
            flags=re.DOTALL,
        )
    tex_path.write_text(tex, encoding="utf-8")


def compile_check(build_dir: Path, tex_name: str) -> bool:
    engine = next((e for e in ("latexmk", "tectonic", "pdflatex") if shutil.which(e)), None)
    if engine is None:
        print(
            "! No TeX engine found - skipping compile check.\n"
            "  Install one to verify locally, e.g.:\n"
            "    brew install tectonic          (small, fast)\n"
            "    brew install --cask mactex-no-gui\n"
            "  arXiv will compile the package on their TeX Live either way.",
            file=sys.stderr,
        )
        return False
    if engine == "latexmk":
        cmd = ["latexmk", "-pdf", "-interaction=nonstopmode", tex_name]
        runs = 1
    elif engine == "tectonic":
        cmd = ["tectonic", tex_name]
        runs = 1
    else:
        cmd = ["pdflatex", "-interaction=nonstopmode", tex_name]
        runs = 2  # second pass resolves references
    for _ in range(runs):
        result = subprocess.run(cmd, cwd=build_dir, capture_output=True, text=True)
    if result.returncode != 0:
        tail = (result.stdout or result.stderr).splitlines()[-25:]
        print("! LaTeX compile FAILED:\n  " + "\n  ".join(tail), file=sys.stderr)
        return False
    print(f"Compile check passed with {engine}.")
    return True


def validate(meta: dict[str, str], build_dir: Path, figures: list[str]) -> list[str]:
    warnings: list[str] = []
    n = len(meta.get("abstract", ""))
    if n > ABSTRACT_METADATA_LIMIT:
        warnings.append(
            f"abstract is {n} chars; arXiv's metadata field allows {ABSTRACT_METADATA_LIMIT}. "
            "Shorten it before pasting into the submission form."
        )
    for fig in figures:
        if not (build_dir / fig).exists():
            warnings.append(f"figure missing from build dir: {fig}")
    total = sum(f.stat().st_size for f in build_dir.iterdir() if f.is_file())
    if total > 10 * 1024 * 1024:
        warnings.append(f"package is {total / 1e6:.1f} MB; consider compressing figures.")
    return warnings


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", default=str(PROJECT_ROOT / "REPLICATION_STUDY.md"))
    ap.add_argument("--assets-dir", default=str(PROJECT_ROOT / "assets"))
    ap.add_argument("--output-dir", default=str(PROJECT_ROOT / "arxiv"))
    ap.add_argument("--repo-url", default="https://github.com/Sage-is/NLT-Replication-Study")
    ap.add_argument("--branch", default="develop")
    ap.add_argument("--no-compile", action="store_true", help="skip the local compile check")
    args = ap.parse_args()

    if shutil.which("pandoc") is None:
        print("pandoc is required: brew install pandoc", file=sys.stderr)
        return 1

    src = Path(args.input)
    assets_dir = Path(args.assets_dir)
    out_dir = Path(args.output_dir)
    build_dir = out_dir / "build"
    build_dir.mkdir(parents=True, exist_ok=True)

    md, meta, figures = preprocess(src.read_text(encoding="utf-8"), assets_dir, args.repo_url, args.branch)
    pre_md = build_dir / "paper.pre.md"
    pre_md.write_text(build_metadata_block(meta) + md, encoding="utf-8")

    tex_path = build_dir / "main.tex"
    run_pandoc(pre_md, tex_path)
    postprocess_tex(tex_path, meta.get("affiliation"))

    for fig in figures:
        shutil.copy2(assets_dir / fig, build_dir / fig)

    compiled = False if args.no_compile else compile_check(build_dir, "main.tex")

    warnings = validate(meta, build_dir, figures)

    tarball = out_dir / "arxiv-submission.tar.gz"
    with tarfile.open(tarball, "w:gz") as tar:
        tar.add(tex_path, arcname="main.tex")
        for fig in figures:
            tar.add(build_dir / fig, arcname=fig)

    print(f"\nLaTeX source : {tex_path}")
    print(f"Figures      : {', '.join(figures)}")
    print(f"Tarball      : {tarball}")
    if compiled:
        print(f"PDF preview  : {build_dir / 'main.pdf'}")
    print(f"Abstract     : {len(meta.get('abstract', ''))} chars (limit {ABSTRACT_METADATA_LIMIT})")
    for w in warnings:
        print(f"WARNING: {w}", file=sys.stderr)

    print(
        "\nSubmission checklist (https://info.arxiv.org/help/submit_tex.html):\n"
        "  1. Upload arxiv-submission.tar.gz as the source package\n"
        "  2. Paste title, authors, and the abstract into the metadata form\n"
        "  3. Category suggestion: cs.CL (cross-list cs.AI / cs.SE)\n"
        "  4. Pick a license (arXiv non-exclusive is the default; CC BY 4.0 for max reuse)\n"
        "  5. Check the xkcd figure attribution (CC BY-NC 2.5) stays in the caption"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
