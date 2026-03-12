#!/usr/bin/env python3
"""
Compare two landscape runs and produce a markdown summary of changes.

Usage:
    python compare_runs.py --previous runs/2026-03-04/projects-enriched.json \
                           --current  runs/2026-03-11/projects-enriched.json \
                           --output   runs/2026-03-11/changes.md
"""

import argparse
import json
import re
import sys
from datetime import datetime


def normalize(name):
    return name.lower().replace(' ', '').replace('-', '').replace('_', '')


def extract_date_label(path):
    """Try to extract a date from a runs/YYYY-MM-DD/ path."""
    match = re.search(r'(\d{4}-\d{2}-\d{2})', path)
    if match:
        d = datetime.strptime(match.group(1), '%Y-%m-%d')
        return d.strftime('%B %d').replace(' 0', ' ')  # "March 4"
    return "Previous"


def main():
    parser = argparse.ArgumentParser(description="Compare two landscape runs")
    parser.add_argument("--previous", required=True, help="Path to previous projects-enriched.json")
    parser.add_argument("--current", required=True, help="Path to current projects-enriched.json")
    parser.add_argument("--output", required=True, help="Output markdown file")
    args = parser.parse_args()

    with open(args.previous) as f:
        old_list = json.load(f)
    with open(args.current) as f:
        new_list = json.load(f)

    old_data = {p['name']: p for p in old_list}
    new_data = {p['name']: p for p in new_list}

    prev_label = extract_date_label(args.previous)
    curr_label = extract_date_label(args.current)

    # Detect renames via normalized name matching
    old_norm = {normalize(k): k for k in old_data}
    new_norm = {normalize(k): k for k in new_data}

    renames = {}
    for nk, nv in new_norm.items():
        if nk in old_norm and old_norm[nk] != nv:
            renames[old_norm[nk]] = nv

    # Build canonical old set (using new names for renamed projects)
    old_canonical = {}
    for name, p in old_data.items():
        canon = renames.get(name, name)
        old_canonical[canon] = p

    new_set = set(new_data.keys())
    old_set = set(old_canonical.keys())

    added = sorted(new_set - old_set, key=lambda n: new_data[n]['stars'], reverse=True)
    removed = sorted(old_set - new_set, key=lambda n: old_canonical[n].get('stars', 0), reverse=True)
    common = new_set & old_set

    # Star movers (common projects with >=2K change)
    movers = []
    for name in common:
        old_s = old_canonical[name].get('stars', 0)
        new_s = new_data[name]['stars']
        diff = new_s - old_s
        if abs(diff) >= 2.0:
            movers.append((name, old_s, new_s, diff))
    movers.sort(key=lambda x: abs(x[3]), reverse=True)

    # Tier changes
    tier_changes = []
    for name in common:
        old_tier = old_canonical[name].get('growth_tier', '')
        new_tier = new_data[name].get('growth_tier', '')
        if old_tier != new_tier:
            tier_changes.append((name, old_tier, new_tier, new_data[name]['stars']))

    # Category changes
    cat_changes = []
    for name in common:
        old_cat = old_canonical[name].get('category', '')
        new_cat = new_data[name].get('category', '')
        if old_cat != new_cat:
            cat_changes.append((name, old_cat, new_cat))

    # Build markdown
    lines = []
    lines.append(f"## Notable Changes Since Last Report ({prev_label} \u2192 {curr_label})\n")
    lines.append(f"**{len(added)} projects added, {len(removed)} removed"
                 f"{f', {len(renames)} renamed' if renames else ''}.**"
                 f" Net: {len(old_data)} \u2192 {len(new_data)} projects.\n")

    # New entries
    if added:
        lines.append("### New entries to watch\n")
        for name in added[:10]:  # Top 10 by stars
            p = new_data[name]
            lines.append(f"- **{name}** ({p['stars']:.1f}K stars) \u2014 {p['category']}")
        if len(added) > 10:
            rest = [new_data[n]['name'] for n in added[10:]]
            lines.append(f"- Also added: {', '.join(rest)}")
        lines.append("")

    # Removals
    if removed:
        lines.append("### Notable removals\n")
        for name in removed[:10]:
            p = old_canonical[name]
            lines.append(f"- **{name}** ({p.get('stars', '?')}K stars) \u2014 {p['category']}")
        if len(removed) > 10:
            rest = [old_canonical[n]['name'] if 'name' in old_canonical[n] else n for n in removed[10:]]
            lines.append(f"- Also removed: {', '.join(rest)}")
        lines.append("")

    # Fastest movers
    if movers:
        lines.append("### Fastest movers (existing projects)\n")
        lines.append(f"| Project | {prev_label} | {curr_label} | Change |")
        lines.append("|---------|-------|--------|--------|")
        for name, old_s, new_s, diff in movers[:8]:
            lines.append(f"| {name} | {old_s:.0f}K | {new_s:.0f}K | {diff:+.1f}K |")
        lines.append("")

    # Tier changes
    if tier_changes:
        lines.append("### Tier changes\n")
        for name, old_t, new_t, stars in tier_changes:
            lines.append(f"- **{name}**: {old_t}\u2192{new_t} ({stars:.1f}K stars)")
        lines.append("")

    # Category changes
    if cat_changes:
        lines.append("### Category reclassifications\n")
        for name, old_c, new_c in cat_changes:
            lines.append(f"- **{name}**: {old_c} \u2192 {new_c}")
        lines.append("")

    output = "\n".join(lines)

    with open(args.output, 'w') as f:
        f.write(output)

    print(f"Saved: {args.output}")
    print(f"  Added: {len(added)}, Removed: {len(removed)}, "
          f"Renames: {len(renames)}, Movers: {len(movers)}, "
          f"Tier changes: {len(tier_changes)}")


if __name__ == "__main__":
    main()
