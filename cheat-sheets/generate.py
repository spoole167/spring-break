#!/usr/bin/env python3
"""
Cheat-sheet card generator.

Reads a YAML data file, stamps it into the HTML template,
and optionally converts to PDF via weasyprint.

Usage:
    python generate.py cards/jackson-group-id.yaml          # HTML + PDF
    python generate.py cards/jackson-group-id.yaml --html    # HTML only
    python generate.py cards/*.yaml                          # batch all cards
"""

import argparse
import html
import sys
from pathlib import Path

# Check required dependencies before doing anything else
_missing = []
try:
    import yaml
except ImportError:
    _missing.append("pyyaml")
try:
    from jinja2 import Template
except ImportError:
    _missing.append("jinja2")

if _missing:
    print(
        f"Error: missing required packages: {', '.join(_missing)}\n"
        f"Install them with:\n"
        f"  pip install {' '.join(_missing)}\n"
        f"Or install everything at once:\n"
        f"  pip install -r requirements.txt",
        file=sys.stderr,
    )
    sys.exit(1)

# Tier colour palettes
TIER_STYLES = {
    1: {
        "tier_color": "#c0392b",
        "scope_bg": "#fdf2f2",
        "scope_border": "#f0d0d0",
    },
    2: {
        "tier_color": "#e67e22",
        "scope_bg": "#fef9f2",
        "scope_border": "#f5e0c0",
    },
    3: {
        "tier_color": "#8e44ad",
        "scope_bg": "#faf2fd",
        "scope_border": "#e0d0f0",
    },
}

LOOP_LETTERS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")


def load_template():
    tpl_path = Path(__file__).parent / "template.html"
    return Template(tpl_path.read_text(encoding="utf-8"))


def load_card(yaml_path: Path) -> dict:
    with open(yaml_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def escape_field(value):
    """HTML-escape a string, preserving None."""
    if value is None:
        return None
    return html.escape(str(value))


def escape_card(card: dict) -> dict:
    """HTML-escape fields that appear inside <pre> blocks or raw text.

    Fields like what_changed, fixes, scope_check, and watch_out
    intentionally contain inline HTML (<code>, <a>) and stay unescaped.
    """
    c = dict(card)

    # error_output goes inside <pre> — escape XML/HTML
    if "error_output" in c:
        c["error_output"] = escape_field(c["error_output"])

    # diffs go inside <pre> — escape removed/added/comment lines
    if "diffs" in c:
        escaped_diffs = []
        for d in c["diffs"]:
            escaped_diffs.append({
                "comment": escape_field(d.get("comment")),
                "removed": escape_field(d.get("removed")),
                "added": escape_field(d.get("added")),
            })
        c["diffs"] = escaped_diffs

    return c


def render_html(card: dict, template: Template, show_mitigation: bool = True) -> str:
    tier = int(card.get("tier", 1))
    styles = TIER_STYLES.get(tier, TIER_STYLES[1])

    safe_card = escape_card(card)
    ctx = {**safe_card, **styles, "loop_letters": LOOP_LETTERS,
           "show_mitigation": show_mitigation}
    return template.render(**ctx)


def write_html(html: str, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"  HTML → {out_path}")


def write_pdf(html_path: Path, pdf_path: Path):
    try:
        from weasyprint import HTML
    except ImportError:
        print("  [skip PDF] weasyprint not installed")
        return

    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    HTML(filename=str(html_path)).write_pdf(str(pdf_path))
    print(f"  PDF  → {pdf_path}")


def process_card(yaml_path: Path, template: Template, html_only: bool = False):
    card = load_card(yaml_path)
    card_id = card.get("id", yaml_path.stem)
    print(f"[{card_id}]")

    out_dir = yaml_path.parent.parent / "target"
    html_path = out_dir / f"{card_id}.html"
    pdf_path = out_dir / f"{card_id}.pdf"

    html = render_html(card, template)
    write_html(html, html_path)

    if not html_only:
        write_pdf(html_path, pdf_path)


def html_to_pdf(html_path: Path, pdf_path: Path):
    """Convert a standalone HTML file to PDF via WeasyPrint."""
    try:
        from weasyprint import HTML
    except ImportError:
        print(f"  [skip] weasyprint not installed for {html_path}")
        return
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    HTML(filename=str(html_path)).write_pdf(str(pdf_path))
    print(f"  PDF  → {pdf_path}")


def build_special_pages(out_dir: Path):
    """Generate PDFs for cover, tier dividers, and CTA end page."""
    base = Path(__file__).parent
    specials = [
        ("cover", base / "cover.html"),
        ("sizing-summary", base / "sizing-summary.html"),
        ("divider-tier1", base / "divider-tier1.html"),
        ("divider-tier2", base / "divider-tier2.html"),
        ("divider-tier3", base / "divider-tier3.html"),
        ("cta-end", base / "cta-end.html"),
    ]
    paths = {}
    for name, html_path in specials:
        if html_path.exists():
            pdf_path = out_dir / f"{name}.pdf"
            print(f"[{name}]")
            html_to_pdf(html_path, pdf_path)
            paths[name] = pdf_path
        else:
            print(f"  [skip] {html_path.name} not found")
    return paths


def merge_pdfs(pdf_paths: list, out_path: Path):
    """Merge individual PDFs into one combined document."""
    try:
        from pypdf import PdfWriter
    except ImportError:
        try:
            from PyPDF2 import PdfWriter
        except ImportError:
            print("  [skip merge] pypdf/PyPDF2 not installed")
            return

    writer = PdfWriter()
    for p in pdf_paths:
        if p.exists():
            writer.append(str(p))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    writer.write(str(out_path))
    writer.close()
    print(f"\n  MERGED → {out_path} ({len(pdf_paths)} pages)")


# Tier sort order for the merged PDF
TIER_ORDER = {1: 0, 2: 1, 3: 2}
TIER_NAMES = {1: "Won't Build", 2: "Won't Run", 3: "Wrong Results"}


def main():
    parser = argparse.ArgumentParser(
        description="Generate cheat-sheet cards.\n\n"
                    "Default (no args): generate all cards in cards/ as HTML + PDF "
                    "and merge into all-cards.pdf.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("files", nargs="*", type=Path,
                        help="YAML card files (default: all cards in cards/)")
    parser.add_argument("--html", action="store_true", help="HTML only, skip PDF")
    parser.add_argument("--merge", type=str, default=None,
                        help="Merge all PDFs into one file (e.g. --merge all-cards.pdf)")
    args = parser.parse_args()

    # Default: all cards in cards/ directory
    if not args.files:
        cards_dir = Path(__file__).parent / "cards"
        args.files = sorted(cards_dir.glob("*.yaml"))
        if not args.files:
            print("No YAML files found in cards/", file=sys.stderr)
            sys.exit(1)
        # Default merge filename when running in all-cards mode
        if args.merge is None and not args.html:
            args.merge = "all-cards.pdf"

    template = load_template()
    generated_pdfs = []  # (tier, id, path) for sorting

    for f in args.files:
        if not f.exists():
            print(f"[skip] {f} not found", file=sys.stderr)
            continue
        card = load_card(f)
        process_card(f, template, html_only=args.html)

        if not args.html:
            card_id = card.get("id", f.stem)
            tier = int(card.get("tier", 1))
            out_dir = f.parent.parent / "target"
            generated_pdfs.append((tier, card_id, out_dir / f"{card_id}.pdf"))

    if args.merge and generated_pdfs:
        import tempfile, shutil
        # Sort by tier, then alphabetically within tier
        generated_pdfs.sort(key=lambda x: (TIER_ORDER.get(x[0], 9), x[1]))
        out_dir = generated_pdfs[0][2].parent

        # Re-render cards without mitigation footer for the merged PDF
        tmp_dir = Path(tempfile.mkdtemp(prefix="merge_"))
        print("\n[merge] Rendering cards without mitigation footer...")
        merge_card_pdfs = []  # (tier, id, tmp_pdf_path)
        for tier, card_id, _ in generated_pdfs:
            yaml_path = Path(__file__).parent / "cards" / f"{card_id}.yaml"
            if yaml_path.exists():
                card = load_card(yaml_path)
                html_str = render_html(card, template, show_mitigation=False)
                tmp_html = tmp_dir / f"{card_id}.html"
                tmp_pdf = tmp_dir / f"{card_id}.pdf"
                tmp_html.write_text(html_str, encoding="utf-8")
                write_pdf(tmp_html, tmp_pdf)
                merge_card_pdfs.append((tier, card_id, tmp_pdf))

        # Build special pages (cover, dividers, CTA)
        special = build_special_pages(out_dir)

        # Assemble final page order: cover → [divider → cards] per tier → CTA
        ordered_pdfs = []

        if "cover" in special:
            ordered_pdfs.append(special["cover"])

        if "sizing-summary" in special:
            ordered_pdfs.append(special["sizing-summary"])

        for tier_num in [1, 2, 3]:
            divider_key = f"divider-tier{tier_num}"
            if divider_key in special:
                ordered_pdfs.append(special[divider_key])
            for t, _, p in merge_card_pdfs:
                if t == tier_num:
                    ordered_pdfs.append(p)

        if "cta-end" in special:
            ordered_pdfs.append(special["cta-end"])

        merge_pdfs(ordered_pdfs, out_dir / args.merge)

        # Clean up temp files
        shutil.rmtree(tmp_dir, ignore_errors=True)

    print("\nDone.")


if __name__ == "__main__":
    main()
