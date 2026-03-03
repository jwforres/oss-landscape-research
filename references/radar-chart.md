# Growth Radar Chart Specification

The growth radar is a scatter chart plotting **Current Scale** (x-axis) vs. **Growth Momentum** (y-axis), with category color-coding and quadrant labels. It serves as a 5-second executive summary.

## Design spec

### Layout
- Figure size: 14 × 11 inches at 200 DPI (2800 × 2200 px)
- Background: `#0f172a` (dark slate)
- Chart area background: `#141c30`

### Vertical structure (top to bottom)
1. Header: subtitle (monospace, `#94a3b8`), title (24pt bold, `#f8fafc`), description (12pt, `#94a3b8`)
2. Legend: category color dots with labels, wrapping across 2 rows
3. Chart area: scatter plot with quadrant labels
4. Callout boxes: 3–4 highlight cards
5. Methodology note: small text explaining the axes

### Chart area
- X-axis: "Current Scale (GitHub Stars)" — linear, labeled in K (0K, 50K, 100K, etc.)
- Y-axis: "Growth Momentum" — composite score 0–100
- Quadrant dividers: dashed lines at x=median(stars), y=50
- Quadrant labels: `#4a5568` at 0.8 opacity, monospace bold, placed in corners
  - Top-right: LEADERS
  - Top-left: RISING FAST
  - Bottom-right: ESTABLISHED
  - Bottom-left: EARLY STAGE

### Dots
- Standard projects: circle, radius=80 scatter size, category color, white edge (0.8px)
- New projects (launched <12 months): larger radius=120, PLUS an outer ring (radius=300, same color, 0.35 opacity)
- Labels: 9.5pt semibold, `#e2e8f0`, positioned via per-project dx/dy offsets

### Color palette
Choose 8–12 distinct colors for categories. Requirements:
- All colors must pass WCAG AA contrast against `#141c30` background
- Adjacent categories in the legend should have visually distinct hues
- Use lighter/brighter variants (not dark/saturated) — this is a dark theme

Recommended starting palette:
```python
{
    "Category A": "#60a5fa",  # blue
    "Category B": "#f87171",  # red
    "Category C": "#c4b5fd",  # purple
    "Category D": "#34d399",  # green
    "Category E": "#fbbf24",  # amber
    "Category F": "#22d3ee",  # cyan
    "Category G": "#f472b6",  # pink
    "Category H": "#fb923c",  # orange
    "Category I": "#a5b4fc",  # indigo
    "Category J": "#cbd5e1",  # gray
}
```

### Callout boxes
- 3–4 boxes in a row below the chart
- Dark card background (`#161f35`), subtle border (`#2d3a50`)
- Structure: small monospace label, large colored project name, subtitle with metric
- Choose callouts that tell different stories:
  - Fastest absolute growth
  - Largest total gain
  - Highest percentage growth
  - A "stars don't tell the whole story" example (if one exists)

### Methodology note
- Small text (`9pt`, `#64748b`) at very bottom
- Brief: X = stars, Y = composite score, what's excluded and why

## Label deconfliction process

This is the most iteration-heavy part. Labels WILL overlap on first render.

### Step 1: Identify collision clusters
Projects are in a collision cluster if they're within ~15K stars on x AND ~10 points on y. Common patterns:
- Many small projects cluster at x=5–30K
- Projects at the same growth tier stack vertically

### Step 2: Assign offsets
For each project, set `dx` and `dy` in offset points (not data coordinates):
- `dy = +12` places label above dot
- `dy = -12` places label below dot
- `dx = +20` shifts label right
- `dx = -20` shifts label left
- Combine dx + dy for diagonal placement

### Step 3: Collision-breaking rules
- Within a cluster, alternate labels above/below
- If above/below isn't enough, shift horizontally in opposing directions
- Long names (e.g., "LlamaFactory") need more clearance than short ones (e.g., "MCP")
- Labels near chart edges should point inward

### Step 4: Visual verify and iterate
Render, inspect the PNG, identify remaining overlaps, adjust, re-render. Expect 2–4 iterations.

## Momentum score methodology

Document this in the chart's methodology note. The y-axis composite score (0–100) blends:

| Signal | Weight | Source |
|--------|--------|--------|
| Star velocity | 40% | Percentage growth over measurement period |
| Contributor velocity | 20% | Contributor growth, Octoverse ranking |
| Deployment signals | 20% | Docker pulls, SDK installs, GPU counts, prod users |
| Ecosystem adoption | 20% | Integration count, foundation membership, conf presence |

Special cases:
- **Projects <6 months old**: Score on trajectory slope, not percentage (avoids ∞% growth artifacts)
- **Standards/specs**: Score on adoption breadth (number of adopting projects/orgs), not repo stars
- **Governance bodies**: Exclude from chart entirely
