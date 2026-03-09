---
name: oss-landscape-research
description: Automatically produce a comprehensive emerging open-source AI infrastructure landscape report with verified growth metrics, adversarial review, and an executive growth radar PNG. No user input required — scope, audience, and methodology are predefined. Designed for Claude Code where subagents enable adversarial review. Use this skill when asked to update the AI OSS landscape report, refresh the open-source AI radar, generate the quarterly AI infrastructure scan, or any variation of "run the landscape research." Also trigger on phrases like "update the OSS report", "refresh the AI radar", "run the landscape scan", or "what's new in open-source AI."
---

# OSS Landscape Research — Automated

Fully automated pipeline that produces an emerging open-source AI infrastructure landscape report and executive growth radar chart. No user input required.

## Fixed Scope

These parameters are hardcoded and do not change between runs:

- **Domain**: Emerging open-source AI infrastructure (LLM inference, agents, training, observability, standards, developer tooling, GPU optimization, models, RAG, voice/multimodal)
- **Audience**: Platform engineering leadership evaluating open-source AI projects for enterprise adoption
- **Scope boundaries**:
  - **In scope**: Projects with significant growth or launch in the last 12 months. Infrastructure and developer tooling layer. Enterprise-relevant projects.
  - **Out of scope**: Mature incumbents with flat growth curves (e.g., LangChain, llama.cpp). Application-layer wrappers and chat UIs (e.g., Open WebUI, Lobe Chat). Consumer tools (e.g., Deep-Live-Cam). Diffusion/image-video generation (e.g., ComfyUI, AUTOMATIC1111) — different audience and maturity profile.
- **Corporate flags**: Always flag Red Hat / IBM involvement (contributor, commercial backer, or significant upstream investment). Note the nature of involvement (e.g., "primary commercial backer", "upstream kernel contributions", "joint project with AMD").
- **Time horizon**: Projects with significant activity in the last 12 months from the current date.

## Output directory

All output files go into a dated run directory: `runs/YYYY-MM-DD/` (using the current date). Create this directory at the start of the run. If a directory for today's date already exists, append a sequence number (e.g., `runs/2026-03-04-2/`).

All checkpoint and deliverable file references below are relative to this run directory. Scripts and reference files remain at the workspace root — only outputs are dated.

## Execution

Run all 7 phases sequentially. Do not prompt the user between phases. If a phase requires judgment calls (e.g., whether to accept an adversarial review suggestion), apply the rejection criteria defined in that phase and document the decision in the checkpoint file.

```
Phase 0: Setup                   → runs/YYYY-MM-DD/ (create output directory)
Phase 1: Initial Scan           → runs/YYYY-MM-DD/projects-raw.json
Phase 2: License Verification   → runs/YYYY-MM-DD/projects-licensed.json
Phase 3: Growth Metrics          → runs/YYYY-MM-DD/projects-enriched.json
Phase 4: Report Draft            → runs/YYYY-MM-DD/report-draft.md
Phase 5: Adversarial Review      → runs/YYYY-MM-DD/review-feedback.json
Phase 6: Gap Fill & Final Report → runs/YYYY-MM-DD/report-final.md
Phase 7: Growth Radar PNG        → runs/YYYY-MM-DD/growth-radar.png
```

---

## Phase 1: Initial Scan

Search for candidate projects across these source types, in order:

1. **GitHub Octoverse** (latest annual report) — fastest-growing repos by contributor count in AI/ML topics
2. **GitHub Trending** — current trending repos in `machine-learning`, `llm`, `ai`, `deep-learning`, `agents` topics
3. **Domain-specific rankings** — JS Rising Stars (automation/AI category), ODSC top repos, Runa Capital ROSS Index
4. **Conference proceedings** — KubeCon, GTC, PyTorch Conference, PyCon — projects presented or announced
5. **Foundation project lists** — CNCF, LF AI & Data, PyTorch Foundation member projects
6. **Absolute star leaders** — Search for the most-starred GitHub repos created or reaching major milestones in the last 12 months across AI/ML topics. This catches projects that grow explosively but don't appear in topic-filtered trending lists due to unconventional categorization. Any AI-related repo with >50K stars that isn't already in the candidate list must be evaluated — it cannot be silently skipped.
7. **Viral launches** — Search for GitHub repos created in the last 30 days with >5K stars. Any repo matching this velocity threshold must be evaluated regardless of topic tags or categorization. This catches projects that grow explosively from creator reputation, social media virality, or major announcements before any ranking list indexes them.

For each candidate project, record: name, GitHub URL, current star count, one-line description, primary language, tentative category.

### Category taxonomy

Assign projects to these categories. Add new categories only if the adversarial review (Phase 5) identifies a gap that doesn't fit any existing one.

1. Agentic AI & Agent Frameworks
2. Inference & Serving Infrastructure
3. Open Source Models
4. RAG & Knowledge Systems
5. Voice & Multimodal AI
6. Developer Tools & Automation
7. GPU Optimization & Hardware Efficiency
8. AI-Assisted Development Tooling
9. Training & Fine-Tuning
10. Observability & Evaluation
11. Emerging Standards & Interoperability (always last before Key Trends)

### Inclusion criteria

Include a project if it meets ALL of:
- Genuinely open source (OSI-approved license, or open specification)
- Significant growth signal in the last 12 months (>25% star growth, OR Octoverse/Rising Stars listed, OR major deployment milestone, OR launched <12 months ago with >2K stars)
- Infrastructure or developer tooling layer (not end-user application)

### Exclusion criteria

Exclude if ANY apply:
- Mature incumbent with flat growth (>3 years old, <10% annual star growth, no major recent changes)
- **Project entering maintenance mode or being sunset** — check for: active "future of X" GitHub issues, announced successor project, maintainer statements about winding down, repo archived or redirected. Examples from prior runs: AutoGen (→ Microsoft Agent Framework), torchtune (→ successor repo).
- Application-layer wrapper or chat frontend — a project that **only** provides a UI on top of existing APIs/models with no independent infrastructure capabilities. Projects that expose agentic execution, plugin/skill systems, device integration, or workflow orchestration are infrastructure even if their primary interface is a chat UI.
- Consumer tool, not enterprise/developer infrastructure
- Diffusion/image-video generation (out of scope)
- Proprietary or source-available (BSL, SSPL, Commons Clause, etc.)

**Checkpoint**: Save `projects-raw.json`

---

## Phase 2: License Verification

For every project in `projects-raw.json`:

1. Fetch the actual LICENSE file from the GitHub repository (do not trust search snippets or README claims)
2. Record the SPDX identifier
3. Note any CLA requirements, dual licensing, or recent license changes
4. **Red Hat flag**: Search for Red Hat, IBM, or Neural Magic involvement — check:
   - Top contributors list
   - GitHub org membership
   - Partnership announcements
   - Conference co-presentations
   - Commercial distribution (e.g., "available in Red Hat OpenShift AI")

Record flag as: `"redhat_flag": "primary commercial backer"` or `"redhat_flag": "upstream kernel contributions with AMD"` or `"redhat_flag": null`

**Checkpoint**: Save `projects-licensed.json`

---

## Phase 3: Growth Metrics Enrichment

For each project that existed >6 months ago, find **three timestamped data points** to compute both overall growth and recent trajectory:
- **T0**: ~12 months ago (or project launch if newer)
- **T1**: ~6 months ago
- **T2**: current date

This enables computing two 6-month growth rates to detect acceleration or deceleration. Do not accept a single before/after pair as sufficient for pre-existing projects — a project that grew 50% overall but stalled in the last 6 months tells a very different story than one that grew 50% and is still accelerating.

For projects launched <6 months ago, two data points (launch + current) are acceptable.

### Data sources (priority order)

1. Star history via star-history.com or Runa ROSS Index
2. GitHub Octoverse fastest-growing lists
3. Package manager stats (npm downloads, PyPI downloads, Docker Hub pulls)
4. Domain rankings (JS Rising Stars, ODSC)
5. Project blog posts / changelogs with milestone numbers (often contain "we hit XK stars" with dates)
6. Conference presentation counts

### Required fields per project

```json
{
  "growth_tier": "📈|📊|⚡",
  "viral_launch": false,
  "growth_trajectory": "accelerating|steady|decelerating",
  "growth_data": {
    "stars_t0": 32000,
    "stars_t1": 58000,
    "stars_t2": 71600,
    "date_t0": "2025-03",
    "date_t1": "2025-09",
    "date_t2": "2026-03",
    "growth_pct_t0_t1": 81,
    "growth_pct_t1_t2": 23,
    "other_signals": ["Octoverse top-10", "400K+ GPU deployments"]
  },
  "notable_contributors": [
    { "name": "Red Hat/Neural Magic", "role": "primary commercial", "redhat": true }
  ],
  "notable_adopters": ["xAI", "AMD", "LinkedIn"]
}
```

### Growth trajectory rules

Compare `growth_pct_t0_t1` to `growth_pct_t1_t2`:
- **accelerating**: Recent 6mo growth rate is higher than prior 6mo
- **steady**: Recent rate is within 30% of prior rate (e.g., 25% → 20% = steady)
- **decelerating**: Recent rate dropped by more than 30% relative to prior rate (e.g., 38% → 9% = decelerating)

For projects <6 months old, set trajectory to `"accelerating"` by default (insufficient data).

### Growth tier rules

- **📈**: Recent 6mo growth >15% AND not in sharp deceleration (recent rate >50% of prior rate), OR Octoverse/Rising Stars top-10, OR >100K deployment-scale metric
- **📊**: Growth signals exist but recent trajectory is flat or decelerating, OR growth lacks clean data points
- **⚡**: Launched <6 months ago — score on trajectory slope, not percentage

**Viral launch flag 🔥**: Set `"viral_launch": true` for any project created within the last 30 days of the report run date AND with >5K stars. This flag is temporal — it highlights what just dropped, not historical virality. Projects from prior runs that were once viral do not carry the flag forward.

**Downgrade rule**: A project that qualified as 📈 based on overall numbers but has `growth_trajectory: "decelerating"` with recent 6mo growth <10% should be downgraded to 📊. This prevents the report from presenting stalling projects as fast-growing.

**Checkpoint**: Save `projects-enriched.json`

---

## Phase 4: Report Draft

Read `references/entry-format.md` for the exact entry format. Assemble the report with this structure:

```markdown
# Emerging Open Source AI Infrastructure — [Month Year]
> A landscape scan of [N] projects across [N] categories, focused on emerging and
> accelerating open-source projects relevant to enterprise AI platform teams.
> 🔴 = Red Hat / IBM involvement flagged. 🔥 = viral launch (<30 days old, >5K stars).

## [Category 1]
### [Project]
...

---

## Key Trends to Watch
1. ...

---

## Scope Note
[What's excluded and why]
```

### Writing rules

- Every entry must have: License, Why it's notable, Growth & Community, Notable contributor(s), Area
- Red Hat flagged projects: add 🔴 after the project name in the `###` heading
- Viral launch projects: add 🔥 after the project name in the `###` heading (after 🔴 if both apply)
- "Why it's notable" must explain WHAT it does AND WHY it matters — not just features
- Growth data must include specific numbers with date ranges
- **Growth trajectory is mandatory for pre-existing projects (>6 months old):** The Growth & Community section must state the recent trajectory direction and include both 6-month growth rates. Examples:
  - Decelerating: "Growth has sharply decelerated: ~50% in Mar–Sep 2025, slowing to ~11% in Sep 2025–Mar 2026."
  - Steady: "Growth remains steady at ~17-20% per 6-month period."
  - Accelerating: "Growth is accelerating: ~15% in Mar–Sep 2025, increasing to ~28% in Sep 2025–Mar 2026."
  - Always end with an editorial interpretation of what the trajectory means (competitive pressure, post-viral normalization, category maturation, etc.)
- Key Trends must reference specific projects from the report
- Standards section always goes last before Key Trends
- Include a Scope Note at the end explaining what's excluded (diffusion, mature incumbents, chat UIs, consumer tools, maintenance-mode projects)

**Checkpoint**: Save `report-draft.md`

---

## Phase 5: Adversarial Review

Spawn two independent subagent reviews. Each gets ONLY the report text — no research context.

```bash
# Review 1: Category gap analysis
cat report-draft.md | claude -p "$(cat references/adversarial-review-prompt.md)" > review-1.md

# Review 2: Project-level gap analysis  
cat report-draft.md | claude -p "$(cat references/adversarial-review-prompt-2.md)" > review-2.md
```

### Automated triage

After both reviews return, apply these rules without user input:

**Auto-accept** a suggestion if:
- Both reviewers independently flag the same project or category gap
- The suggested project has >20K GitHub stars AND fits the scope boundaries
- The gap is a missing infrastructure layer (e.g., no fine-tuning coverage, no observability)

**Auto-reject** a suggestion if:
- Project is a mature incumbent with flat growth (>3 years, <10% annual growth)
- Project is application-layer / chat UI / consumer tool
- Project is in diffusion/image-video generation
- Project has <2K stars and no other exceptional signal
- Suggestion duplicates a project already covered under a different name

**Flag for manual review** (append to checkpoint, note in final report):
- Borderline cases where reviewers disagree and the project has 5K–20K stars

**Checkpoint**: Save `review-feedback.json`:
```json
{
  "accepted": [
    { "project": "...", "category": "...", "new_category_needed": false, "rationale": "..." }
  ],
  "rejected": [
    { "project": "...", "reason": "..." }
  ],
  "flagged_for_review": [
    { "project": "...", "context": "..." }
  ],
  "structural_changes": ["moved Standards to end", "added Observability category"]
}
```

---

## Phase 6: Gap Fill & Final Report

### For each accepted gap:

1. Research using the same Phase 1–3 methodology (web search, license verify, growth metrics)
2. Write the entry in identical format to existing entries
3. Add to appropriate category, or create new category if `new_category_needed: true`

### Structural adjustments to always apply:

- Standards/interoperability section goes last (before Key Trends) — it's cross-cutting
- If new categories were added, insert in logical order (concrete → abstract)
- Add new Key Trends entries for any newly covered areas
- Update project count and category count in header
- Verify every entry has all required fields (License, Why notable, Growth, Contributors, Area)
- Verify every Red Hat–flagged project has 🔴 in its heading

### Final validation checklist

Run through before saving — do not skip:
- [ ] Every project has License field
- [ ] Every project has "Why it's notable" with WHAT + WHY
- [ ] Every project has Growth & Community with emoji tier and timestamped numbers
- [ ] Every project has Notable contributor(s) with role descriptor
- [ ] Every project has Area tag
- [ ] All Red Hat/IBM flags are marked with 🔴
- [ ] Standards section is last before Key Trends
- [ ] Key Trends reference specific projects from the report by name
- [ ] Scope Note explains exclusions
- [ ] No duplicate projects
- [ ] Category count in header matches actual categories
- [ ] Project count in header matches actual projects
- [ ] Every pre-existing project (>6 months old) has growth trajectory stated in its Growth & Community section (two 6-month rates + editorial interpretation)
- [ ] No project in maintenance mode or being sunset is included (search for "maintenance mode", "archived", "successor" in recent GitHub issues/discussions for any project with decelerating growth)
- [ ] Growth tier emoji (📈/📊/⚡) is consistent with trajectory — no 📈 on projects with recent 6mo growth <10%

**Checkpoint**: Save `report-final.md` — this is the primary deliverable.

---

## Phase 7: Growth Radar PNG

Generate the executive scatter chart. Read `references/radar-chart.md` for the full rendering spec.

### Data extraction from projects-enriched.json

A project is **plottable** if it has a current star count AND at least one scoreable growth signal.

**Exclude** from chart:
- Governance bodies (e.g., AAIF, Linux Foundation projects without their own repo)
- Upstream contributions that live in another project's repo (e.g., IBM Triton kernels in vLLM)
- Projects with `growth_tier: "⚡"` AND no deployment/adoption signals beyond raw stars

### Momentum score (y-axis, 0–100)

| Signal | Weight | How to score |
|--------|--------|-------------|
| Star velocity | 40% | Map growth % to 0–40 scale (0%→0, 25%→10, 50%→20, 100%→30, >200%→40) |
| Contributor velocity | 20% | Octoverse top-10 = 20. Otherwise scale by contributor growth rate. |
| Deployment signals | 20% | Docker pulls, GPU counts, SDK installs, production users. Scale logarithmically. |
| Ecosystem adoption | 20% | Integration count, foundation membership, conf presentations. |

Special cases:
- Projects <6 months old: score on trajectory slope, cap at 95 (leave room above for proven leaders)
- Standards/specs: score on adoption breadth (# of adopting projects × 4, cap at 20 for that component)

### Render

```bash
python scripts/render_radar.py \
  --input runs/YYYY-MM-DD/projects-enriched.json \
  --output runs/YYYY-MM-DD/growth-radar.png \
  --title "Open Source AI: Growth Radar" \
  --subtitle "[N] Projects · [N] Categories · [Month Year]"
```

### Label deconfliction

After first render, visually inspect the PNG. Identify overlapping labels — projects within ~15K stars on x AND ~10 points on y will collide. Update `label_dx` and `label_dy` values in the JSON and re-render. Expect 2–4 iterations. See `references/radar-chart.md` for the full deconfliction procedure.

### Callouts

Select 3–4 callouts that tell different stories. Always use this pattern:
1. **Fastest to scale** — highest absolute star gain in shortest time
2. **Largest annual gain** — most stars added in the last 12 months
3. **Biggest percentage growth** — highest growth rate among established projects (>10K stars baseline)
4. **"Stars ≠ adoption"** — project where deployment metrics dramatically exceed star trajectory

Save callouts as `callouts.json` in the run directory and pass to the render script.

**Output**: `growth-radar.png` at 200 DPI.

---

## Deliverables

Two files, produced automatically:

1. **`report-final.md`** — Categorized landscape report with verified growth metrics and Red Hat flags
2. **`growth-radar.png`** — Executive scatter chart at 200 DPI, suitable for embedding in Google Docs or slides

## Context management

- Each research phase (1, 3, 6) involves many web searches. Checkpoint to JSON after each phase.
- If context fills during Phase 3, batch: research 8–10 projects, save checkpoint, continue with remaining.
- Adversarial review subagents get clean context by design — this is critical for catching blind spots.
- `projects-enriched.json` is the single source of truth. Report and radar are both generated from it.
