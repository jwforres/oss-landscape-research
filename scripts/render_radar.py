#!/usr/bin/env python3
"""
Growth Radar Chart Renderer

Template script for rendering the executive scatter chart.
Reads project data from projects-enriched.json and produces growth-radar.png.

Usage:
    python render_radar.py --input projects-enriched.json --output growth-radar.png

The script expects projects-enriched.json to contain an array of objects with:
    - name: str
    - stars: float (in thousands, e.g., 71.6 = 71,600 stars)
    - growth_score: int (0-100 composite momentum score)
    - category: str
    - is_new: bool (launched within last 12 months)
    - label_dx: int (horizontal label offset in points, default 0)
    - label_dy: int (vertical label offset in points, default 12)
    - note: str (optional, displayed in callout or tooltip context)

After first render, visually inspect and adjust label_dx/label_dy values
in the JSON to resolve overlaps. Expect 2-4 iterations.
"""

import argparse
import json
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ── Theme constants ──
BG = '#0f172a'
CHART_BG = '#141c30'
GRID = '#1e293b'
AXIS_COLOR = '#94a3b8'
LABEL_COLOR = '#e2e8f0'
QUADRANT_COLOR = '#4a5568'

# Default category palette — override or extend as needed
DEFAULT_PALETTE = {
    "Category A": "#60a5fa",
    "Category B": "#f87171",
    "Category C": "#c4b5fd",
    "Category D": "#34d399",
    "Category E": "#fbbf24",
    "Category F": "#22d3ee",
    "Category G": "#f472b6",
    "Category H": "#fb923c",
    "Category I": "#a5b4fc",
    "Category J": "#cbd5e1",
}


def load_data(path):
    with open(path) as f:
        data = json.load(f)

    # Build category palette from unique categories in data
    categories = list(dict.fromkeys(p["category"] for p in data))
    palette_colors = list(DEFAULT_PALETTE.values())
    palette = {}
    for i, cat in enumerate(categories):
        palette[cat] = palette_colors[i % len(palette_colors)]

    return data, palette


def render(projects, palette, output_path, title="Open Source Growth Radar",
           subtitle="", description="", callouts=None, methodology_note=""):
    fig = plt.figure(figsize=(14, 11), facecolor=BG)
    ax = fig.add_axes([0.07, 0.18, 0.89, 0.53], facecolor=CHART_BG)

    # ── Quadrant lines ──
    max_stars = max(p["stars"] for p in projects) * 1.1
    ax.axvline(x=max_stars * 0.35, color=GRID, linestyle='--', linewidth=0.8, alpha=0.5)
    ax.axhline(y=50, color=GRID, linestyle='--', linewidth=0.8, alpha=0.5)

    # ── Plot dots ──
    for p in projects:
        color = palette.get(p["category"], "#888")
        s = 120 if p.get("is_new") else 80
        ax.scatter(p["stars"], p["growth_score"], c=color, s=s, alpha=0.9,
                   edgecolors='white', linewidths=0.8, zorder=5)
        if p.get("is_new"):
            ax.scatter(p["stars"], p["growth_score"], c='none', s=300,
                       edgecolors=color, linewidths=1, alpha=0.35, zorder=4)
        ax.annotate(p["name"],
                    xy=(p["stars"], p["growth_score"]),
                    xytext=(p.get("label_dx", 0), p.get("label_dy", 12)),
                    textcoords='offset points',
                    fontsize=9.5, fontweight='semibold', color=LABEL_COLOR,
                    ha='center', va='center', zorder=6)

    # ── Axes ──
    x_max = int((max_stars + 25) / 50) * 50  # Round up to nearest 50
    ax.set_xlim(0, x_max)
    ax.set_ylim(0, 100)
    ticks_x = list(range(0, x_max + 1, 50))
    ax.set_xticks(ticks_x)
    ax.set_xticklabels([f'{v}K' for v in ticks_x],
                        fontsize=11, color=AXIS_COLOR, fontfamily='monospace')
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_yticklabels(['0', '25', '50', '75', '100'],
                        fontsize=11, color=AXIS_COLOR, fontfamily='monospace')
    ax.set_xlabel('Current Scale (GitHub Stars)', fontsize=13, color=AXIS_COLOR, labelpad=12)
    ax.set_ylabel('Growth Momentum', fontsize=13, color=AXIS_COLOR, labelpad=12)
    ax.tick_params(axis='both', length=0)
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    for spine in ['bottom', 'left']:
        ax.spines[spine].set_color('#2d3a50')

    # ── Quadrant labels ──
    qx_right = x_max * 0.65
    qx_left = x_max * 0.15
    ax.text(qx_right, 97, 'LEADERS', fontsize=13, fontweight='bold', color=QUADRANT_COLOR,
            ha='center', va='top', fontfamily='monospace', alpha=0.8)
    ax.text(qx_left, 97, 'RISING FAST', fontsize=13, fontweight='bold', color=QUADRANT_COLOR,
            ha='center', va='top', fontfamily='monospace', alpha=0.8)
    ax.text(qx_right, 3, 'ESTABLISHED', fontsize=13, fontweight='bold', color=QUADRANT_COLOR,
            ha='center', va='bottom', fontfamily='monospace', alpha=0.8)
    ax.text(qx_left, 3, 'EARLY STAGE', fontsize=13, fontweight='bold', color=QUADRANT_COLOR,
            ha='center', va='bottom', fontfamily='monospace', alpha=0.8)

    # ── Header ──
    fig.text(0.07, 0.965, subtitle,
             fontsize=10, color=AXIS_COLOR, fontfamily='monospace', va='top')
    fig.text(0.07, 0.94, title,
             fontsize=24, fontweight='bold', color='#f8fafc', va='top')
    fig.text(0.07, 0.895, description,
             fontsize=12, color=AXIS_COLOR, va='top', linespacing=1.5)

    # ── Legend ──
    legend_y = 0.835
    cats = list(palette.items())
    for i, (cat, color) in enumerate(cats):
        x = 0.07 + (i % 5) * 0.185
        y = legend_y - (i // 5) * 0.025
        fig.patches.append(mpatches.FancyBboxPatch(
            (x, y - 0.004), 0.012, 0.012, boxstyle="round,pad=0.001",
            facecolor=color, edgecolor='none', transform=fig.transFigure,
            figure=fig, zorder=10))
        fig.text(x + 0.017, y + 0.002, cat, fontsize=11, color=LABEL_COLOR, va='center')

    # ── Callout boxes ──
    if callouts:
        n = len(callouts)
        box_w = 0.88 / n - 0.02
        for i, c in enumerate(callouts):
            x = 0.07 + i * (box_w + 0.02)
            box_h = 0.06
            box_y = 0.05
            rect = mpatches.FancyBboxPatch(
                (x, box_y), box_w, box_h,
                boxstyle="round,pad=0.006",
                facecolor='#161f35', edgecolor='#2d3a50', linewidth=0.8,
                transform=fig.transFigure, figure=fig, zorder=10)
            fig.patches.append(rect)
            fig.text(x + 0.012, box_y + box_h - 0.008, c["label"],
                     fontsize=7.5, color=AXIS_COLOR, fontfamily='monospace', va='top', zorder=11)
            fig.text(x + 0.012, box_y + box_h / 2 - 0.002, c["value"],
                     fontsize=14, fontweight='bold', color=c.get("accent", "#60a5fa"),
                     va='center', zorder=11)
            fig.text(x + 0.012, box_y + 0.008, c["sub"],
                     fontsize=9.5, color='#cbd5e1', va='bottom', zorder=11)

    # ── Methodology note ──
    if methodology_note:
        fig.text(0.07, 0.025, methodology_note,
                 fontsize=9, color='#64748b', va='bottom',
                 bbox=dict(boxstyle='square,pad=0', facecolor=BG, edgecolor='none'))

    plt.savefig(output_path, dpi=200, facecolor=BG, bbox_inches='tight', pad_inches=0.3)
    plt.close()
    print(f"Saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Render growth radar chart")
    parser.add_argument("--input", required=True, help="Path to projects JSON")
    parser.add_argument("--output", default="growth-radar.png", help="Output PNG path")
    parser.add_argument("--title", default="Open Source Growth Radar")
    parser.add_argument("--subtitle", default="")
    parser.add_argument("--callouts", default=None, help="Path to callouts JSON")
    args = parser.parse_args()

    projects, palette = load_data(args.input)

    callouts = None
    if args.callouts:
        with open(args.callouts) as f:
            callouts = json.load(f)

    render(
        projects, palette, args.output,
        title=args.title,
        subtitle=args.subtitle,
        description=(
            "Scale vs. momentum for emerging projects. Top-right = large and accelerating.\n"
            "Top-left = smaller but explosive trajectory. Ringed dots = launched in last 12 months."
        ),
        callouts=callouts,
        methodology_note=(
            "Methodology: X = GitHub stars. Y = composite growth score (0-100) blending "
            "star deltas, contributor velocity, deployment metrics, and ecosystem signals."
        ),
    )


if __name__ == "__main__":
    main()
