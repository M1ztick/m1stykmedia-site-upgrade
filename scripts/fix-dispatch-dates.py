#!/usr/bin/env python3
"""
Correct every Dispatch `pubDate` from an authoritative source.

There are two sources of truth, applied in this order:

  1. **WordPress export** (`_imports/mistykmedia.WordPress.2026-06-03.xml`).
     For each article that was actually published on the WordPress site we use
     `wp:post_date` — the *site-local* timestamp, i.e. the date WordPress
     displayed to readers. (The original migration used `wp:post_date_gmt`,
     which pushed evening posts forward by a day and produced the off-by-one
     dates.) A verified slug→local-date table is embedded below so this script
     still works if the 1.2 MB export is not present; when the export *is*
     present it is parsed and cross-checked against that table.

  2. **Git first-appearance.** Articles written *after* the WordPress
     migration were never on WordPress, so the export has nothing to say about
     them. For those, the date the file was first added to this repository is
     the day the piece went live (the repo auto-deploys `main`). A
     post-migration article therefore may not be dated months before the commit
     that created it; when it is, we move it to that commit date. A generous
     grace window preserves dates authors set deliberately to the day of the
     event they cover (see GRACE_DAYS).

Run from the repo root:
    python3 scripts/fix-dispatch-dates.py            # apply
    python3 scripts/fix-dispatch-dates.py --check    # report only
"""

import argparse
import glob
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WP_XML = os.path.join(ROOT, "_imports", "mistykmedia.WordPress.2026-06-03.xml")

# Days of slack allowed between a post-migration article's current pubDate and
# the commit that first added it. Authors routinely write a piece and commit it
# days later, and some date an article to the day of the event it covers (e.g.
# `the-presidents-least-privilege-problem` is dated 2026-08-10, the day it
# cites, and was committed 2026-08-13). We must not clobber those.
#
# The observed gaps split cleanly into two clusters:
#   {0,1,1,1,2,3,6,8,14}  days  -> normal writing / commit lag, keep pubDate
#   {87,390,442,443}      days  -> article dated before it existed, correct it
# 30 days sits in the empty space between the two clusters.
GRACE_DAYS = 30

# ---- Authoritative output: collection dir -> {filename: wordpress slug} -----
# Only articles that were published on WordPress. Everything else in the
# repository was authored after the migration.
WORDPRESS_ARTICLES = {
    "src/content/dispatch": {
        "billionaire-buy-in-american-electoral-mythos.md": "billionaire-buy-in",
        "chatgpt-creates-throne-portrait-my-digital-transformation.md": "chatgpt-creates-throne-portrait-my-digital-transformation",
        "chatgpt-prompted-stand-up-comedian-hilarious.md": "chatgpt-prompted-stand-up-comedian-hilarious",
        "chinas-ai-sports-bots-a-cover-for-military-innovation.md": "chinas-ai-sports-bots-a-cover-for-military-innovation",
        "human-beats-ai-in-10-hour-coding-marathon-heres-how.md": "10-hour_ai_human_competition",
        "israeli-security-cabinets-decision-on-gaza.md": "israeli-security-cabinets-decision-on-gaza",
        "israels-starvation-of-palestine-40000-babies-at-risk.md": "israeli_war_crimes_infants_starve_in_gaza",
        "metas-troubling-history-with-user-privacy.md": "metas-troubling-history-with-user-privacy",
        "project-2025-the-conspiracy-that-isnt-a-theory.md": "introduction-to-project-2025",
        "the-agentic-ai-era-and-the-new-geopolitical-order.md": "agentic-ai-era-and-the-new-geopolitical-order",
        "the-ai-misalignment-dilemna-the-need-for-global-regulations.md": "the-ai-misalignment-dilemna-and-the-need-for-global-regulations",
        "the-epstein-jail-video-pt-2-the-dojs-smoking-gun.md": "the-epstein-jail-video-pt-2-the-dojs-smoking-gun",
        "the-justice-departments-selective-incompetence.md": "the-justice-departments-selective-incompetence",
        "the-two-party-system-and-the-convergence-of-power.md": "the-two-party-system-and-the-convergence-of-power",
        "the-uni-party-setup-authoritarianism-wasnt-a-glitch.md": "the-uni-party-setup-authoritarianism-wasnt-a-glitch",
        "tragedy-in-gaza-israeli-forces-kill-62-palestinians-many-while-seeking-aid.md": "tragedy-in-gaza-israeli-forces-kill-62-palestinians-many-while-seeking-aid",
        "trumps-crypto-empire-from-white-house-to-wallet.md": "trumps-crypto-empire-from-white-house-to-wallet",
    },
    "src/content/journey": {
        "sri-ramakrishna-unifying-the-divine.md": "sri-ramakrishna-unifying-the-divine",
        "western-esotericism-a-luminous-thread.md": "western-esotericism-a-luminous-thread",
    },
}

# ---- Embedded authoritative slug -> site-local post date -------------------
# Extracted from the WordPress export (`wp:post_date`, not `..._gmt`). Kept in
# the script so it is reproducible without the 1.2 MB import file; when the
# export is present it is verified against these values.
WORDPRESS_LOCAL_DATES = {
    "metas-troubling-history-with-user-privacy": "2025-07-18",
    "chinas-ai-sports-bots-a-cover-for-military-innovation": "2025-07-18",
    "chatgpt-creates-throne-portrait-my-digital-transformation": "2025-07-18",
    "10-hour_ai_human_competition": "2025-07-20",
    "israeli_war_crimes_infants_starve_in_gaza": "2025-07-26",
    "trumps-crypto-empire-from-white-house-to-wallet": "2025-07-27",
    "the-epstein-jail-video-pt-2-the-dojs-smoking-gun": "2025-07-31",
    "tragedy-in-gaza-israeli-forces-kill-62-palestinians-many-while-seeking-aid": "2025-08-03",
    "israeli-security-cabinets-decision-on-gaza": "2025-08-10",
    "the-two-party-system-and-the-convergence-of-power": "2025-08-22",
    "the-uni-party-setup-authoritarianism-wasnt-a-glitch": "2025-08-31",
    "chatgpt-prompted-stand-up-comedian-hilarious": "2025-09-11",
    "the-ai-misalignment-dilemna-and-the-need-for-global-regulations": "2025-09-28",
    "agentic-ai-era-and-the-new-geopolitical-order": "2025-11-25",
    "the-justice-departments-selective-incompetence": "2025-11-29",
    "western-esotericism-a-luminous-thread": "2025-12-05",
    "billionaire-buy-in": "2026-02-13",
    "sri-ramakrishna-unifying-the-divine": "2026-02-24",
    "introduction-to-project-2025": "2026-03-18",
}


def parse_export(path):
    """slug -> site-local post date (YYYY-MM-DD) for every published post."""
    xml = open(path, encoding="utf-8").read()
    out = {}
    for item in re.findall(r"<item>[\s\S]*?</item>", xml):
        if "<wp:post_type><![CDATA[post]]></wp:post_type>" not in item:
            continue
        if "<wp:status><![CDATA[trash]]></wp:status>" in item:
            continue
        slug = re.search(r"<wp:post_name><!\[CDATA\[(.*?)\]\]></wp:post_name>", item)
        date = re.search(r"<wp:post_date><!\[CDATA\[(.*?)\]\]></wp:post_date>", item)
        if slug and date:
            out[slug.group(1).strip()] = date.group(1).strip()[:10]
    return out


def first_commit_date(rel_path):
    """Date the file was first added to this repository, or ''."""
    try:
        out = subprocess.run(
            ["git", "log", "--follow", "--diff-filter=A", "--format=%as", "--", rel_path],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout.strip().split("\n")
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""
    dates = sorted(d for d in out if d)
    return dates[0] if dates else ""


def days_between(later, earlier):
    from datetime import date
    yl, ml, dl = map(int, later.split("-"))
    ye, me, de = map(int, earlier.split("-"))
    return (date(yl, ml, dl) - date(ye, me, de)).days


def current_pubdate(text):
    m = re.search(r"^pubDate:\s*(.*)$", text, re.M)
    return m.group(1).strip().strip('"').strip("'")[:10] if m else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report only, do not write")
    args = ap.parse_args()

    wp_dates = dict(WORDPRESS_LOCAL_DATES)
    if os.path.exists(WP_XML):
        live = parse_export(WP_XML)
        for slug, want in WORDPRESS_LOCAL_DATES.items():
            if slug in live and live[slug] != want:
                sys.exit(f"export disagrees with embedded table for {slug}: "
                         f"{live[slug]} != {want}")
        wp_dates.update(live)

    changes, rows = [], []
    for rel_dir, mapping in WORDPRESS_ARTICLES.items():
        files = sorted(os.path.basename(p)
                       for p in glob.glob(os.path.join(ROOT, rel_dir, "*.md")))
        for name in files:
            path = os.path.join(ROOT, rel_dir, name)
            rel_path = os.path.join(rel_dir, name)
            text = open(path, encoding="utf-8").read()
            current = current_pubdate(text)

            slug = mapping.get(name)
            if slug:
                if slug not in wp_dates:
                    sys.exit(f"{name}: slug not found in WordPress data: {slug}")
                target, source = wp_dates[slug], "wordpress-local"
            else:
                first = first_commit_date(rel_path)
                if not first:
                    rows.append((name, current, current, "unverifiable"))
                    continue
                if days_between(first, current) > GRACE_DAYS:
                    target, source = first, "git-first-commit"
                else:
                    target, source = current, "unchanged"

            if target != current:
                if not args.check:
                    text = re.sub(r"^pubDate:.*$", f"pubDate: {target}",
                                  text, count=1, flags=re.M)
                    open(path, "w", encoding="utf-8").write(text)
                changes.append((name, current, target, source))
            rows.append((name, current, target, source))

    w = max(len(r[0]) for r in rows)
    print(f"{'file'.ljust(w)}  current     new         source")
    print("-" * (w + 34))
    for name, cur, new, src in rows:
        print(f"{name.ljust(w)}  {cur}  {new}  {src}"
              f"{'  *CHANGED' if cur != new else ''}")
    print()
    print(f"{len(changes)} of {len(rows)} dates corrected "
          f"({'check only' if args.check else 'written'}).")


if __name__ == "__main__":
    main()
