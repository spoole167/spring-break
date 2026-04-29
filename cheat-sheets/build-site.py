#!/usr/bin/env python3
"""
Website generator for Spring Boot 4.0 Migration cheat-sheets.

Reads all YAML cards + the existing special HTML pages and produces a
self-contained site/ folder ready to drop on any static host.

Usage:
    python build-site.py                  # generates site/
    python build-site.py --out /tmp/site  # custom output dir

Site structure:
    site/
      index.html          home page  (cover content)
      sizing.html         effort / sizing methodology
      tier1.html          Tier 1 landing + card index
      tier2.html          Tier 2 landing + card index
      tier3.html          Tier 3 landing + card index
      next-steps.html     CTA / what's next
      cards/
        {id}.html         one page per card, with nav
"""

import argparse
import sys
from pathlib import Path

# ── dependency check ──────────────────────────────────────────────────────────
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
        f"Error: missing packages: {', '.join(_missing)}\n"
        f"  pip install -r requirements.txt",
        file=sys.stderr,
    )
    sys.exit(1)

# ── constants ─────────────────────────────────────────────────────────────────

TIER_COLORS   = {1: "#c0392b", 2: "#e67e22", 3: "#8e44ad"}
TIER_BG       = {1: "#fdf2f2", 2: "#fef9f2", 3: "#faf2fd"}
TIER_BORDER   = {1: "#f0d0d0", 2: "#f5e0c0", 3: "#e0d0f0"}
TIER_LABELS   = {1: "Won't Build", 2: "Won't Run", 3: "Wrong Results"}
TIER_SUBTITLES= {1: "Compilation & Dependency Failures",
                 2: "Runtime & Startup Failures",
                 3: "Subtle Behavioural Changes"}

HERE = Path(__file__).parent

# ── shared nav + CSS injected into every page ─────────────────────────────────

NAV_CSS = """
<style>
  /* ── Screen overrides: strip print dimensions ── */
  * { margin: 0; padding: 0; box-sizing: border-box; }
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@400;500;600;700&display=swap');

  body {
    font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
    background: #f5f5f5;
    color: #1a1a1a;
    width: auto !important;
    height: auto !important;
    min-height: 100vh;
  }

  .site-nav {
    background: #1a1a1a;
    padding: 0 24px;
    display: flex;
    align-items: center;
    gap: 0;
    flex-wrap: wrap;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
  }

  .site-nav .nav-brand {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    font-weight: 700;
    color: #fff;
    text-decoration: none;
    padding: 14px 20px 14px 0;
    margin-right: 8px;
    border-right: 1px solid #444;
    white-space: nowrap;
  }

  .site-nav a.nav-link {
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    font-weight: 500;
    color: #ccc;
    text-decoration: none;
    padding: 14px 14px;
    transition: color 0.15s;
    white-space: nowrap;
  }

  .site-nav a.nav-link:hover { color: #fff; }

  .site-nav a.nav-link.tier1 { color: #e87b72; }
  .site-nav a.nav-link.tier2 { color: #f0a45a; }
  .site-nav a.nav-link.tier3 { color: #b980d6; }
  .site-nav a.nav-link.tier1:hover { color: #ff9992; }
  .site-nav a.nav-link.tier2:hover { color: #ffc07a; }
  .site-nav a.nav-link.tier3:hover { color: #d4a0f0; }

  .site-nav .nav-spacer { flex: 1; }

  .site-content {
    max-width: 900px;
    margin: 0 auto;
    padding: 32px 24px 64px;
  }

  /* card page layout */
  .page {
    width: auto !important;
    height: auto !important;
    max-width: 860px;
    margin: 0 auto;
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    padding: 32px 36px 28px !important;
  }

  .card-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 860px;
    margin: 0 auto 16px;
    font-size: 13px;
  }

  .card-nav a {
    color: #2563eb;
    text-decoration: none;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
  }

  .card-nav a:hover { text-decoration: underline; }

  .card-nav .tier-back {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    padding: 5px 12px;
    border-radius: 4px;
    font-weight: 600;
  }

  .card-nav-bottom {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 860px;
    margin: 20px auto 0;
    padding-top: 16px;
    border-top: 1px solid #e5e7eb;
    font-size: 13px;
  }

  .card-nav-bottom a {
    color: #2563eb;
    text-decoration: none;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .card-nav-bottom a:hover { text-decoration: underline; }

  .footer { max-width: 860px; margin: 0 auto; }

  @media (max-width: 640px) {
    .site-content { padding: 16px 12px 40px; }
    .page { padding: 20px 16px 20px !important; }
    .card-nav, .card-nav-bottom { flex-direction: column; gap: 8px; align-items: flex-start; }
  }
</style>
"""

def nav_html(active="", prefix=""):
    """Shared nav bar. prefix = relative path back to root (e.g. '../')."""
    return f"""<nav class="site-nav">
  <a class="nav-brand" href="{prefix}index.html">Spring Boot 4.0<br>Migration Guide</a>
  <a class="nav-link tier1" href="{prefix}tier1.html">Tier 1 · Won't Build</a>
  <a class="nav-link tier2" href="{prefix}tier2.html">Tier 2 · Won't Run</a>
  <a class="nav-link tier3" href="{prefix}tier3.html">Tier 3 · Wrong Results</a>
  <a class="nav-link" href="{prefix}sizing.html">Effort Sizing</a>
  <span class="nav-spacer"></span>
  <a class="nav-link" href="{prefix}next-steps.html">Next Steps →</a>
</nav>"""

# ── load + group cards ────────────────────────────────────────────────────────

def load_all_cards():
    cards_dir = HERE / "cards"
    cards = []
    for p in sorted(cards_dir.glob("*.yaml")):
        with open(p) as f:
            c = yaml.safe_load(f)
            c["_path"] = p
        cards.append(c)
    return cards

def group_by_tier(cards):
    groups = {1: [], 2: [], 3: []}
    for c in cards:
        t = int(c.get("tier", 1))
        groups.setdefault(t, []).append(c)
    return groups

# ── generate index.html (home) ────────────────────────────────────────────────

def build_index(cards, out_dir):
    groups = group_by_tier(cards)
    total = len(cards)

    tier_rows = ""
    for t in [1, 2, 3]:
        color = TIER_COLORS[t]
        label = TIER_LABELS[t]
        count = len(groups.get(t, []))
        tier_rows += f"""
      <a class="tier-box" href="tier{t}.html" style="border-left:4px solid {color}">
        <span class="tier-box-label" style="color:{color}">Tier {t} · {label}</span>
        <span class="tier-box-count">{count} cards →</span>
      </a>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Spring Boot 4.0 Migration Guide</title>
{NAV_CSS}
<style>
  .hero {{ background:#1a1a1a; color:#fff; padding:56px 24px 48px; text-align:center; }}
  .hero .series {{ font-family:'JetBrains Mono',monospace; font-size:12px; color:#888;
    text-transform:uppercase; letter-spacing:1.5px; margin-bottom:16px; }}
  .hero h1 {{ font-family:'JetBrains Mono',monospace; font-size:clamp(28px,5vw,48px);
    font-weight:700; line-height:1.2; margin-bottom:12px; }}
  .hero .sub {{ font-size:18px; color:#aaa; font-weight:400; }}
  .home-content {{ max-width:800px; margin:0 auto; padding:40px 24px 64px; }}
  .tier-grid {{ display:flex; flex-direction:column; gap:12px; margin:32px 0; }}
  .tier-box {{ display:flex; justify-content:space-between; align-items:center;
    background:#fff; border-radius:6px; padding:18px 20px;
    text-decoration:none; color:#1a1a1a;
    box-shadow:0 1px 4px rgba(0,0,0,0.07);
    transition: box-shadow 0.15s; }}
  .tier-box:hover {{ box-shadow:0 4px 12px rgba(0,0,0,0.12); }}
  .tier-box-label {{ font-family:'JetBrains Mono',monospace; font-size:15px; font-weight:700; }}
  .tier-box-count {{ font-size:14px; color:#666; }}
  .stat-row {{ display:flex; gap:12px; margin:32px 0 0; }}
  .stat-box {{ flex:1; background:#fff; border-radius:6px; padding:20px;
    text-align:center; box-shadow:0 1px 4px rgba(0,0,0,0.07); }}
  .stat-num {{ font-family:'JetBrains Mono',monospace; font-size:32px; font-weight:700; }}
  .stat-lbl {{ font-size:11px; text-transform:uppercase; letter-spacing:.5px; color:#666; margin-top:4px; }}
  .effort-box {{ background:#fff; border-radius:6px; padding:20px 24px;
    margin:16px 0; box-shadow:0 1px 4px rgba(0,0,0,0.07); text-align:center;
    font-size:15px; color:#333; }}
  .effort-box strong {{ font-size:20px; color:#1a1a1a; }}
  .page-links {{ display:flex; gap:12px; margin-top:32px; flex-wrap:wrap; }}
  .page-link {{ flex:1; min-width:180px; background:#fff; border-radius:6px; padding:16px 18px;
    text-decoration:none; color:#1a1a1a; box-shadow:0 1px 4px rgba(0,0,0,0.07);
    transition:box-shadow 0.15s; }}
  .page-link:hover {{ box-shadow:0 4px 12px rgba(0,0,0,0.12); }}
  .page-link-title {{ font-weight:600; font-size:14px; margin-bottom:4px; }}
  .page-link-desc {{ font-size:13px; color:#666; }}
</style>
</head>
<body>
{nav_html()}
<div class="hero">
  <div class="series">spring-boot 3.5 → 4.0</div>
  <h1>Spring Boot 4.0<br>Migration Guide</h1>
  <div class="sub">{total} Breaking Changes You Need to Fix</div>
</div>
<div class="home-content">
  <div class="stat-row">
    <div class="stat-box"><div class="stat-num" style="color:{TIER_COLORS[1]}">{len(groups[1])}</div><div class="stat-lbl">Won't Build</div></div>
    <div class="stat-box"><div class="stat-num" style="color:{TIER_COLORS[2]}">{len(groups[2])}</div><div class="stat-lbl">Won't Run</div></div>
    <div class="stat-box"><div class="stat-num" style="color:{TIER_COLORS[3]}">{len(groups[3])}</div><div class="stat-lbl">Wrong Results</div></div>
  </div>
  <div class="effort-box">
    Estimated total migration effort: <strong>200–500 hours</strong> depending on codebase size
  </div>

  <div class="tier-grid">{tier_rows}
  </div>

  <div class="page-links">
    <a class="page-link" href="sizing.html">
      <div class="page-link-title">📊 Effort Sizing</div>
      <div class="page-link-desc">S/M/L estimates, OpenRewrite coverage, hidden-complexity callouts</div>
    </a>
    <a class="page-link" href="next-steps.html">
      <div class="page-link-title">🚀 Next Steps</div>
      <div class="page-link-desc">Your options: migrate now, incrementally, or stay on 3.5 safely</div>
    </a>
  </div>
</div>
</body>
</html>"""

    (out_dir / "index.html").write_text(html, encoding="utf-8")
    print("  index.html")

# ── generate tier landing pages ───────────────────────────────────────────────

def build_tier_page(tier_num, cards, out_dir):
    color   = TIER_COLORS[tier_num]
    label   = TIER_LABELS[tier_num]
    subtitle= TIER_SUBTITLES[tier_num]
    bg      = TIER_BG[tier_num]
    border  = TIER_BORDER[tier_num]

    # Load divider HTML for the description + subsystem index
    divider_src = HERE / f"divider-tier{tier_num}.html"
    divider_desc = ""
    divider_index = ""
    if divider_src.exists():
        raw = divider_src.read_text(encoding="utf-8")
        # Extract the description paragraph
        import re
        m = re.search(r'<p class="description">(.*?)</p>', raw, re.DOTALL)
        if m:
            divider_desc = m.group(1).strip()
        # Extract subsystem blocks
        subsystem_blocks = re.findall(
            r'<div class="subsystem">(.*?)</div>\s*</div>', raw, re.DOTALL)
        for block in re.findall(r'<div class="subsystem">(.*?(?:</ul>))\s*</div>', raw, re.DOTALL):
            divider_index += f'<div class="subsystem">{block}</div>\n'

    # Build card grid
    card_items = ""
    for c in cards:
        cid     = c.get("id", "")
        title   = c.get("title", cid)
        oneliner= c.get("oneliner", "").strip()
        effort  = c.get("effort", "")
        openrewrite = c.get("openrewrite", False)

        badges = f'<span class="cb-effort cb-effort-{effort}">{effort}</span>'
        if openrewrite:
            badges += '<span class="cb-openrewrite">⚙ OpenRewrite</span>'

        card_items += f"""
    <a class="card-item" href="cards/{cid}.html">
      <div class="ci-title">{title}</div>
      <div class="ci-oneliner">{oneliner}</div>
      <div class="ci-badges">{badges}</div>
    </a>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tier {tier_num}: {label} — Spring Boot 4.0 Migration</title>
{NAV_CSS}
<style>
  .tier-hero {{ background:{color}; color:#fff; padding:48px 24px 40px; }}
  .tier-hero .tier-badge-lg {{ font-family:'JetBrains Mono',monospace; font-size:13px;
    font-weight:700; background:rgba(255,255,255,0.2); display:inline-block;
    padding:4px 14px; border-radius:4px; margin-bottom:14px; letter-spacing:.5px; }}
  .tier-hero h1 {{ font-family:'JetBrains Mono',monospace; font-size:clamp(24px,4vw,40px);
    font-weight:700; line-height:1.2; margin-bottom:8px; }}
  .tier-hero .tier-sub {{ font-size:16px; opacity:.85; }}
  .tier-body {{ max-width:900px; margin:0 auto; padding:32px 24px 64px; }}
  .tier-description {{ background:#fff; border-radius:6px; padding:20px 24px;
    margin-bottom:28px; box-shadow:0 1px 4px rgba(0,0,0,0.07); font-size:15px;
    line-height:1.6; color:#333; border-left:4px solid {color}; }}
  .subsystem-index {{ background:#fff; border-radius:6px; padding:20px 24px;
    margin-bottom:32px; box-shadow:0 1px 4px rgba(0,0,0,0.07); }}
  .subsystem-index h3 {{ font-family:'JetBrains Mono',monospace; font-size:11px;
    text-transform:uppercase; letter-spacing:1px; color:#999; margin-bottom:16px; }}
  .subsystem {{ margin-bottom:12px; }}
  .subsystem-name {{ font-size:13px; font-weight:700; color:{color}; margin-bottom:4px; }}
  .card-list {{ font-size:13px; line-height:1.7; color:#444; padding-left:16px; }}
  .card-list li {{ list-style:none; position:relative; padding-left:12px; }}
  .card-list li::before {{ content:"•"; position:absolute; left:0; color:{color}; }}
  .cards-heading {{ font-family:'JetBrains Mono',monospace; font-size:13px;
    font-weight:700; color:#555; text-transform:uppercase; letter-spacing:.5px;
    margin-bottom:16px; }}
  .card-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr));
    gap:12px; }}
  .card-item {{ background:#fff; border-radius:6px; padding:16px 18px;
    text-decoration:none; color:#1a1a1a; box-shadow:0 1px 4px rgba(0,0,0,0.07);
    border-top:3px solid {color}; display:flex; flex-direction:column; gap:8px;
    transition:box-shadow 0.15s; }}
  .card-item:hover {{ box-shadow:0 4px 12px rgba(0,0,0,0.12); }}
  .ci-title {{ font-size:14px; font-weight:700; line-height:1.3; }}
  .ci-oneliner {{ font-size:12px; color:#555; line-height:1.45; flex:1; }}
  .ci-badges {{ display:flex; gap:6px; flex-wrap:wrap; margin-top:4px; }}
  .cb-effort {{ font-family:'JetBrains Mono',monospace; font-size:10px; font-weight:700;
    padding:2px 7px; border-radius:3px; text-transform:uppercase; }}
  .cb-effort-S {{ background:#d4edda; color:#155724; }}
  .cb-effort-M {{ background:#fff3cd; color:#856404; }}
  .cb-effort-L {{ background:#f8d7da; color:#721c24; }}
  .cb-openrewrite {{ font-family:'JetBrains Mono',monospace; font-size:10px;
    background:#e0eaff; color:#1e40af; padding:2px 7px; border-radius:3px; font-weight:600; }}
</style>
</head>
<body>
{nav_html()}
<div class="tier-hero">
  <div style="max-width:900px;margin:0 auto">
    <div class="tier-badge-lg">TIER {tier_num}</div>
    <h1>{label}</h1>
    <div class="tier-sub">{subtitle}</div>
  </div>
</div>
<div class="tier-body">
  <div class="tier-description">{divider_desc or f"These {len(cards)} changes affect your codebase at the {label.lower()} level."}</div>

  {"<div class='subsystem-index'><h3>Subsystem Index</h3>" + divider_index + "</div>" if divider_index else ""}

  <div class="cards-heading">{len(cards)} Cards in This Tier</div>
  <div class="card-grid">{card_items}
  </div>
</div>
</body>
</html>"""

    (out_dir / f"tier{tier_num}.html").write_text(html, encoding="utf-8")
    print(f"  tier{tier_num}.html  ({len(cards)} cards)")

# ── generate card pages ───────────────────────────────────────────────────────

import html as htmllib

def render_card_site(card, prev_card, next_card):
    """Render a single card as a self-contained website page."""
    tier       = int(card.get("tier", 1))
    color      = TIER_COLORS[tier]
    scope_bg   = TIER_BG[tier]
    scope_border = TIER_BORDER[tier]
    cid        = card.get("id", "")
    title      = card.get("title", cid)
    tier_label = card.get("tier_label", TIER_LABELS[tier])
    series     = card.get("series", "spring-boot 3.5 → 4.0")
    effort     = card.get("effort", "")
    openrewrite= card.get("openrewrite", False)
    oneliner   = (card.get("oneliner") or "").strip()
    error_output = htmllib.escape(str(card.get("error_output") or "").strip())
    what_changed = (card.get("what_changed") or "").strip()
    why_changed  = (card.get("why_changed") or "").strip()
    verify       = (card.get("verify") or "").strip()
    scope_check  = (card.get("scope_check") or "").strip()
    further_info = (card.get("further_info") or "").strip()
    watch_out    = card.get("watch_out") or []
    fixes        = card.get("fixes") or []
    diffs        = card.get("diffs") or []
    footer_links = card.get("footer_links") or []

    LOOP_LETTERS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    # diffs block
    diffs_html = ""
    for d in diffs:
        comment = htmllib.escape(str(d.get("comment") or ""))
        removed = htmllib.escape(str(d.get("removed") or "").rstrip())
        added   = htmllib.escape(str(d.get("added") or "").rstrip())
        diffs_html += f"""{'<span class="comment">' + comment + '</span>' + chr(10) if comment else ""}<span class="removed">{removed}</span>\n<span class="added">{added}</span>\n\n"""

    # fixes block
    fixes_html = ""
    for i, fix in enumerate(fixes):
        letter = LOOP_LETTERS[i] if i < len(LOOP_LETTERS) else str(i+1)
        fixes_html += f"""<div class="fix-option">
      <span class="fix-num">{letter}</span>
      <div><span class="fix-label">{fix.get('label','')}</span> {(fix.get('text') or '').strip()}</div>
    </div>"""

    # watch_out block
    watch_html = ""
    if watch_out:
        watch_html = "<h2>Watch Out</h2>" + "".join(f"<p>{w.strip()}</p>" for w in watch_out)

    # further info + footer links
    further_html = ""
    if footer_links or further_info:
        links_str = " · ".join(f'<a href="{l["url"]}">{l["text"]}</a>' for l in footer_links)
        further_html = f"""<div class="further-info">
    <div class="further-info-header">Further Info</div>
    <div class="further-info-links">{links_str}</div>
    {"<div class='further-info-facts'>" + further_info + "</div>" if further_info else ""}
  </div>"""

    # prev/next nav
    prev_link = f'<a href="{prev_card["id"]}.html">← {prev_card["title"]}</a>' if prev_card else '<span></span>'
    next_link = f'<a href="{next_card["id"]}.html">{next_card["title"]} →</a>' if next_card else '<span></span>'
    back_link = f'<a class="tier-back" href="../tier{tier}.html" style="background:{scope_bg};color:{color};border:1px solid {scope_border}">← Tier {tier}: {TIER_LABELS[tier]}</a>'

    badges = ""
    if effort:
        badges += f'<span class="effort-badge effort-{effort}">Effort: {effort}</span>'
    if openrewrite:
        badges += '<span class="openrewrite-badge">⚙ OpenRewrite</span>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Spring Boot 4.0 Migration</title>
{NAV_CSS}
<style>
  /* ── card-specific styles (from template.html, adapted for screen) ── */
  body {{ background:#f5f5f5; }}
  .site-content {{ max-width:900px; margin:0 auto; padding:24px 24px 64px; }}
  .page {{ font-family:'Inter','Helvetica Neue',Arial,sans-serif; color:#1a1a1a; }}
  .topbar {{ display:flex; justify-content:space-between; align-items:center;
    margin-bottom:8px; padding-bottom:8px; border-bottom:2px solid {color}; }}
  .tier-badge {{ font-family:'JetBrains Mono',monospace; font-size:11px; font-weight:700;
    color:#fff; background:{color}; padding:3px 10px; border-radius:3px;
    text-transform:uppercase; letter-spacing:.5px; }}
  .series-label {{ font-size:11px; color:#999; font-family:'JetBrains Mono',monospace; }}
  h1 {{ font-size:clamp(18px,3vw,26px); font-weight:700; line-height:1.3;
    margin:10px 0 6px; }}
  .oneliner {{ font-size:14px; color:#444; line-height:1.5; margin-bottom:12px; }}
  .meta-badges {{ display:flex; gap:8px; margin-bottom:16px; flex-wrap:wrap; }}
  .effort-badge {{ font-family:'JetBrains Mono',monospace; font-size:10px; font-weight:700;
    padding:2px 8px; border-radius:3px; text-transform:uppercase; }}
  .effort-S {{ background:#d4edda; color:#155724; }}
  .effort-M {{ background:#fff3cd; color:#856404; }}
  .effort-L {{ background:#f8d7da; color:#721c24; }}
  .openrewrite-badge {{ font-family:'JetBrains Mono',monospace; font-size:10px;
    background:#e0eaff; color:#1e40af; padding:2px 8px; border-radius:3px; font-weight:700; }}
  h2 {{ font-size:13px; font-weight:700; text-transform:uppercase; letter-spacing:.4px;
    color:{color}; margin:18px 0 6px; }}
  p {{ font-size:14px; line-height:1.6; margin-bottom:10px; }}
  pre {{ background:#1e1e1e; border-radius:6px; padding:14px 16px; overflow-x:auto;
    margin:10px 0 16px; font-family:'JetBrains Mono',monospace; font-size:12px;
    line-height:1.55; white-space:pre-wrap; word-break:break-all; }}
  .comment {{ color:#6a9955; display:block; }}
  .removed {{ color:#f97171; display:block; }}
  .added   {{ color:#4ec9b0; display:block; }}
  .fix-options {{ display:flex; flex-direction:column; gap:10px; margin:8px 0 14px; }}
  .fix-option {{ display:flex; gap:10px; align-items:flex-start; font-size:14px; line-height:1.5; }}
  .fix-num {{ font-family:'JetBrains Mono',monospace; font-size:11px; font-weight:700;
    color:#fff; background:{color}; width:20px; height:20px; border-radius:50%;
    display:flex; align-items:center; justify-content:center; flex-shrink:0; margin-top:2px; }}
  .fix-label {{ font-weight:700; }}
  .verify-box {{ background:#f0fdf4; border:1px solid #86efac; border-radius:6px;
    padding:10px 14px; font-size:13px; margin:12px 0; }}
  .scope-box {{ background:{scope_bg}; border:1px solid {scope_border}; border-radius:6px;
    padding:10px 14px; font-size:13px; margin:12px 0; }}
  .further-info {{ background:#f8f9fa; border:1px solid #e2e4e7; border-radius:6px;
    padding:12px 16px; margin-top:16px; font-size:13px; }}
  .further-info-header {{ font-family:'JetBrains Mono',monospace; font-size:10px;
    font-weight:700; text-transform:uppercase; letter-spacing:.5px; color:#999;
    margin-bottom:6px; }}
  .further-info-links a {{ color:#2563eb; text-decoration:none; margin-right:8px; }}
  .further-info-links a:hover {{ text-decoration:underline; }}
  .further-info-facts {{ margin-top:8px; color:#555; line-height:1.5; }}
  .footer {{ margin-top:20px; padding-top:12px; border-top:1px solid #e5e7eb; font-size:12px; }}
  .footer-mitigation {{ color:#555; margin-bottom:8px; line-height:1.5; }}
  .footer-mitigation a {{ color:#2563eb; text-decoration:none; }}
  .footer-links {{ display:flex; justify-content:space-between; font-size:12px; flex-wrap:wrap; gap:6px; }}
  .footer-links a {{ color:#2563eb; text-decoration:none; }}
</style>
</head>
<body>
{nav_html(prefix="../")}
<div class="site-content">
  <div class="card-nav">
    {back_link}
    <a href="../index.html">Home</a>
  </div>

  <div class="page">
    <div class="topbar">
      <span class="tier-badge">Tier {tier} · {tier_label}</span>
      <span class="series-label">{series}</span>
    </div>

    <h1>{title}</h1>
    <div class="oneliner">{oneliner}</div>

    <div class="meta-badges">{badges}</div>

    <h2>What You'll See</h2>
    <pre><span class="comment">{error_output}</span></pre>

    <h2>What Changed</h2>
    <p>{what_changed}</p>

    <pre>{diffs_html.rstrip()}</pre>

    {"<h2>Why This Changed</h2><p>" + why_changed + "</p>" if why_changed else ""}

    <h2>How to Fix</h2>
    <div class="fix-options">{fixes_html}</div>

    {"<div class='verify-box'><strong>✓ Verify:</strong> " + verify + "</div>" if verify else ""}
    {"<div class='scope-box'><strong>Scope check:</strong> " + scope_check + "</div>" if scope_check else ""}

    {watch_html}

    {further_html}

    <div class="footer">
      <div class="footer-mitigation">
        <strong>Not ready to migrate?</strong>
        Pin 3.5 and track CVEs · migrate incrementally with <a href="https://docs.openrewrite.org/recipes/java/spring/boot4">OpenRewrite</a> · <a href="https://www.herodevs.com/support/spring-nes">HeroDevs NES</a> for security patches
      </div>
      <div class="footer-links">
        <div><a href="https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide">Spring Boot 4.0 Migration Guide</a></div>
        <div><a href="https://www.herodevs.com/support/spring-nes">herodevs.com/support/spring-nes</a></div>
      </div>
    </div>
  </div>

  <div class="card-nav-bottom">
    {prev_link}
    {next_link}
  </div>
</div>
</body>
</html>"""


def build_card_pages(cards, out_dir):
    cards_out = out_dir / "cards"
    cards_out.mkdir(exist_ok=True)
    for i, card in enumerate(cards):
        prev_card = cards[i - 1] if i > 0 else None
        next_card = cards[i + 1] if i < len(cards) - 1 else None
        html = render_card_site(card, prev_card, next_card)
        cid = card.get("id", card["_path"].stem)
        (cards_out / f"{cid}.html").write_text(html, encoding="utf-8")
    print(f"  cards/  ({len(cards)} files)")

# ── generate sizing.html ──────────────────────────────────────────────────────

def build_sizing(out_dir):
    src = HERE / "sizing-summary.html"
    if not src.exists():
        print("  [skip] sizing-summary.html not found")
        return

    raw = src.read_text(encoding="utf-8")
    # Extract everything inside <body>...</body>
    import re
    m = re.search(r'<body>(.*?)</body>', raw, re.DOTALL)
    body = m.group(1).strip() if m else raw

    # Strip the print-only @page and fixed dimension CSS from the source
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Migration Effort Sizing — Spring Boot 4.0</title>
{NAV_CSS}
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@400;500;600;700&display=swap');
  body {{ background:#f5f5f5; }}
  .sizing-wrapper {{ max-width:900px; margin:0 auto; padding:32px 24px 64px; }}
  .page {{ background:#fff; border-radius:8px; box-shadow:0 2px 12px rgba(0,0,0,0.08);
    padding:32px 36px !important; margin-bottom:24px;
    width:auto !important; height:auto !important; }}
  .page:last-child {{ margin-bottom:0; }}
  .footer-line {{ position:static !important; border-top:1px solid #ddd; padding-top:10px;
    margin-top:24px; display:flex; justify-content:space-between; font-size:12px; color:#999; }}
  .footer-line a {{ color:#2563eb; text-decoration:none; }}
  h1 {{ font-family:'JetBrains Mono',monospace; font-size:clamp(20px,3vw,28px);
    font-weight:700; margin-bottom:6px; }}
  h2 {{ font-family:'JetBrains Mono',monospace; font-size:11px; font-weight:700;
    text-transform:uppercase; letter-spacing:.4px; color:#c0392b;
    margin-top:20px; margin-bottom:8px; }}
  p {{ font-size:14px; line-height:1.6; margin-bottom:10px; }}
  .subtitle {{ font-size:14px; color:#555; margin-bottom:16px; }}
  .sizing-grid {{ display:flex; gap:12px; margin:12px 0 16px; flex-wrap:wrap; }}
  .sizing-card {{ flex:1; min-width:160px; border:1px solid #e0e0e0; border-radius:6px;
    padding:14px; text-align:center; }}
  .sizing-card .badge {{ font-family:'JetBrains Mono',monospace; font-size:10px;
    font-weight:700; display:inline-block; padding:2px 8px; border-radius:3px;
    text-transform:uppercase; margin-bottom:6px; }}
  .sizing-card.s .badge {{ background:#d4edda; color:#155724; }}
  .sizing-card.m .badge {{ background:#fff3cd; color:#856404; }}
  .sizing-card.l .badge {{ background:#f8d7da; color:#721c24; }}
  .sizing-card .hours {{ font-family:'JetBrains Mono',monospace; font-size:22px;
    font-weight:700; display:block; margin:4px 0; }}
  .sizing-card .desc {{ font-size:12px; color:#666; line-height:1.4; }}
  .sizing-card .count {{ font-family:'JetBrains Mono',monospace; font-size:11px;
    color:#999; margin-top:6px; }}
  .source-table {{ width:100%; border-collapse:collapse; font-size:13px; margin:10px 0; }}
  .source-table th {{ font-family:'JetBrains Mono',monospace; font-size:11px;
    text-transform:uppercase; letter-spacing:.3px; text-align:left; padding:6px 8px;
    border-bottom:2px solid #333; color:#555; }}
  .source-table td {{ padding:7px 8px; border-bottom:1px solid #eee; line-height:1.4; }}
  .coverage-bar {{ background:#f0f0f0; border-radius:4px; height:28px; position:relative;
    margin:8px 0 12px; overflow:hidden; }}
  .coverage-fill {{ background:#1a56db; height:100%; border-radius:4px 0 0 4px;
    display:flex; align-items:center; padding-left:10px; }}
  .coverage-fill span {{ font-family:'JetBrains Mono',monospace; font-size:11px;
    font-weight:700; color:#fff; }}
  .coverage-remainder {{ position:absolute; right:10px; top:50%; transform:translateY(-50%);
    font-family:'JetBrains Mono',monospace; font-size:11px; color:#666; }}
  .tier-coverage {{ display:flex; gap:10px; margin:8px 0; flex-wrap:wrap; }}
  .tier-cov-item {{ flex:1; min-width:180px; font-size:12px; line-height:1.5; padding:8px 10px; border-radius:4px; }}
  .tier-cov-1 {{ background:#fdf2f2; border-left:3px solid #c0392b; }}
  .tier-cov-2 {{ background:#fef9f2; border-left:3px solid #e67e22; }}
  .tier-cov-3 {{ background:#faf2fd; border-left:3px solid #8e44ad; }}
  .callout-table {{ width:100%; border-collapse:collapse; font-size:13px; margin:10px 0; }}
  .callout-table th {{ font-family:'JetBrains Mono',monospace; font-size:11px;
    text-transform:uppercase; text-align:left; padding:6px 8px;
    border-bottom:2px solid #333; color:#555; }}
  .callout-table td {{ padding:7px 8px; border-bottom:1px solid #eee; line-height:1.4; vertical-align:top; }}
  .card-name {{ font-weight:600; white-space:nowrap; }}
  .risk-tag {{ font-family:'JetBrains Mono',monospace; font-size:10px; font-weight:700;
    padding:1px 5px; border-radius:2px; text-transform:uppercase; }}
  .risk-high {{ background:#f8d7da; color:#721c24; }}
  .risk-mod {{ background:#fff3cd; color:#856404; }}
  .badge-inline {{ font-family:'JetBrains Mono',monospace; font-size:10px; font-weight:700;
    padding:1px 5px; border-radius:2px; display:inline-block; }}
  .badge-s {{ background:#d4edda; color:#155724; }}
  .badge-m {{ background:#fff3cd; color:#856404; }}
  .note-box {{ background:#f8f9fa; border:1px solid #e2e4e7; border-radius:4px;
    padding:12px 16px; margin-top:16px; font-size:13px; line-height:1.55; color:#555; }}
  .note-box strong {{ color:#1a1a1a; }}
</style>
</head>
<body>
{nav_html()}
<div class="sizing-wrapper">
{body}
</div>
</body>
</html>"""

    (out_dir / "sizing.html").write_text(html, encoding="utf-8")
    print("  sizing.html")

# ── generate next-steps.html ──────────────────────────────────────────────────

def build_next_steps(out_dir):
    src = HERE / "cta-end.html"
    if not src.exists():
        print("  [skip] cta-end.html not found")
        return

    raw = src.read_text(encoding="utf-8")
    import re
    m = re.search(r'<body>(.*?)</body>', raw, re.DOTALL)
    body = m.group(1).strip() if m else raw

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Next Steps — Spring Boot 4.0 Migration</title>
{NAV_CSS}
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@400;500;600;700&display=swap');
  body {{ background:#f5f5f5; }}
  .ns-wrapper {{ max-width:860px; margin:0 auto; padding:32px 24px 64px; }}
  .page {{ background:#fff; border-radius:8px; box-shadow:0 2px 12px rgba(0,0,0,0.08);
    padding:36px 40px !important; width:auto !important; height:auto !important; }}
  .risk-headline {{ font-family:'JetBrains Mono',monospace; font-size:clamp(20px,3vw,28px);
    font-weight:700; margin-bottom:20px; }}
  .stat-row {{ display:flex; gap:12px; margin-bottom:20px; flex-wrap:wrap; }}
  .stat-box {{ flex:1; min-width:140px; background:#fafafa; border-radius:6px;
    padding:18px; text-align:center; border:1px solid #e0e0e0; }}
  .stat-number {{ font-family:'JetBrains Mono',monospace; font-size:40px; font-weight:700; line-height:1.1; }}
  .stat-label {{ font-size:11px; text-transform:uppercase; letter-spacing:.5px; color:#555; margin-top:6px; font-weight:600; }}
  .stat-box.red .stat-number {{ color:#c0392b; }}
  .stat-box.orange .stat-number {{ color:#e67e22; }}
  .stat-box.purple .stat-number {{ color:#8e44ad; }}
  .risk-paragraph {{ font-size:15px; line-height:1.6; color:#333; margin-bottom:16px; }}
  .divider {{ border:none; border-top:2px solid #1a1a1a; margin:24px 0; }}
  .option {{ margin-bottom:20px; }}
  .option-header {{ font-family:'JetBrains Mono',monospace; font-size:15px;
    font-weight:700; margin-bottom:6px; }}
  .option p {{ font-size:14px; line-height:1.6; color:#444; }}
  .option.nes {{ background:#f8f4fc; border:1px solid #d5c4e0; border-left:4px solid #8e44ad;
    border-radius:6px; padding:16px 20px; }}
  .option.nes .option-header {{ color:#8e44ad; }}
  .cta-section {{ background:#fff; border:1px solid #d0d0d0; border-radius:6px;
    padding:20px 24px; margin-top:20px; }}
  .cta-title {{ font-family:'JetBrains Mono',monospace; font-size:18px; font-weight:700;
    margin-bottom:10px; }}
  .cta-links {{ font-size:14px; line-height:1.8; }}
  .cta-links a {{ color:#2563eb; text-decoration:none; font-weight:500; }}
  .url {{ font-family:'JetBrains Mono',monospace; font-size:13px; }}
  .cta-note {{ margin-top:10px; font-size:13px; color:#666; font-style:italic; }}
  .footer {{ display:none; }}
</style>
</head>
<body>
{nav_html()}
<div class="ns-wrapper">
<div class="page">
{body}
</div>
</div>
</body>
</html>"""

    (out_dir / "next-steps.html").write_text(html, encoding="utf-8")
    print("  next-steps.html")

# ── main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Build static website from cheat-sheet cards")
    parser.add_argument("--out", type=Path, default=HERE / "site",
                        help="Output directory (default: cheat-sheets/site/)")
    args = parser.parse_args()

    out_dir = args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "cards").mkdir(exist_ok=True)

    print(f"Building site → {out_dir}/")

    cards = load_all_cards()
    groups = group_by_tier(cards)

    build_index(cards, out_dir)
    for tier_num in [1, 2, 3]:
        build_tier_page(tier_num, groups.get(tier_num, []), out_dir)
    build_card_pages(cards, out_dir)
    build_sizing(out_dir)
    build_next_steps(out_dir)

    total = sum(len(g) for g in groups.values())
    print(f"\nDone. {total} card pages + 6 site pages → {out_dir}/")
    print(f"Open: {out_dir}/index.html")

if __name__ == "__main__":
    main()
