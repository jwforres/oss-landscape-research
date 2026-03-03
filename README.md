# OSS Landscape Research

A [Claude Code skill](https://docs.anthropic.com/en/docs/claude-code) that automatically produces a comprehensive open-source AI infrastructure landscape report with verified growth metrics, adversarial review, and an executive growth radar chart.

## What it does

Runs a 7-phase automated pipeline:

1. **Initial Scan** — searches GitHub Octoverse, trending repos, ROSS Index, conference proceedings, and foundation project lists for candidate projects
2. **License Verification** — fetches actual LICENSE files and verifies OSI-approved licenses
3. **Growth Metrics** — collects three-point star history (T0/T1/T2) to compute growth trajectory (accelerating, steady, or decelerating)
4. **Report Draft** — assembles a categorized markdown report with structured entries
5. **Adversarial Review** — spawns two independent Claude subagents to find category gaps and missing projects
6. **Gap Fill & Final Report** — researches accepted gaps, applies structural fixes, runs validation checklist
7. **Growth Radar PNG** — renders an executive scatter chart (scale vs. momentum) with label deconfliction

No user input required between phases. Outputs are `report-final.md` and `growth-radar.png`.

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI installed
- Python 3 with `matplotlib` (`pip install matplotlib`)

## Usage

From the project root, run Claude Code and invoke the skill:

```
claude
> /oss-landscape-research
```

Or trigger it with natural language:

```
> update the AI OSS landscape report
> refresh the AI radar
> run the landscape scan
```

## Project structure

```
.claude/skills/oss-landscape-research/
  SKILL.md              # Skill definition (7-phase pipeline)
references/
  entry-format.md       # Report entry template
  adversarial-review-prompt.md    # Subagent prompt 1: category gaps
  adversarial-review-prompt-2.md  # Subagent prompt 2: project gaps
  radar-chart.md        # Chart rendering spec
scripts/
  render_radar.py       # matplotlib scatter chart renderer
```

Generated outputs (gitignored):

```
projects-raw.json       # Phase 1 checkpoint
projects-licensed.json  # Phase 2 checkpoint
projects-enriched.json  # Phase 3 checkpoint (single source of truth)
report-draft.md         # Phase 4 checkpoint
review-feedback.json    # Phase 5 checkpoint
report-final.md         # Final deliverable
growth-radar.png        # Final deliverable
```
