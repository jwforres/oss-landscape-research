# Entry Format Reference

Every project entry in the report follows this exact structure. Do not deviate from it — consistency across 30+ entries is what makes the report scannable.

## Template

```markdown
### [Project Name] [🔴 if Red Hat/IBM flagged]
**License:** [SPDX identifier]

**Why it's notable:** [2-4 sentences. First sentence: what it does in plain terms. Second sentence: why it matters — the strategic "so what" for the target audience. Optional third/fourth: key differentiator, architectural insight, or competitive context. Write for someone who has never heard of this project but understands the domain.]

**Growth & Community:** [emoji] **[Key metric with before/after and time range.]** [2-4 supporting data points: forks, contributors, release cadence, installs, deployment scale, conference mentions, rankings. End with an editorial signal — what the growth pattern means.]

**Notable contributor(s):** [Primary org/person] ([role: creator, sole steward, primary commercial, etc.]). [1-2 sentences of strategic context about the contributor relationship.]

**Area:** [Category] / [Subcategory]
```

## Growth tier emojis

- 📈 **Strong verified growth**: Two+ timestamped data points showing >25% growth over 6+ months, OR Octoverse/Rising Stars top-10, OR strong deployment metrics
- 📊 **Moderate or hard-to-quantify**: Growth signals exist but lack clean before/after numbers
- ⚡ **Too new for trends**: Launched within last 6 months — note trajectory, not percentage

## Writing rules

### "Why it's notable"
- Lead with WHAT, follow with WHY
- Use analogies to known patterns when helpful (e.g., "Think of it as USB-C for AI")
- Name competitors or alternatives to establish context
- Don't just describe features — explain strategic significance
- Bad: "A fast inference engine with many features"
- Good: "The most widely deployed open-source LLM inference engine, now processing trillions of tokens daily across 400,000+ GPUs. Its PagedAttention innovation solved the memory fragmentation problem that made LLM serving expensive."

### "Growth & Community"
- ALWAYS lead with the most impressive verifiable number in bold
- Include time range for every growth claim (e.g., "49K → 72K stars, Jun 2025 → Mar 2026")
- Raw star counts alone are insufficient — pair with at least one other signal
- End with editorial interpretation: what does this growth pattern signal?
- Bad: "Growing fast with many stars"
- Good: "📈 **49.2K → 71.6K stars (Jun 2025 → Mar 2026, +46% in 9 months).** 13.8K forks / 1,822 contributors. Named one of the 10 fastest-growing repos by contributor count in GitHub's 2025 Octoverse. Stars understate momentum — production deployment on 400K+ GPUs is the real signal."

### "Notable contributor(s)"
- Always identify the primary controlling org/person
- Include role descriptor in parentheses
- Add strategic context: why does this contributor relationship matter?
- Flag corporate risks if relevant (single-vendor control, CLA requirements, license change history)

### "Area"
- Use format: "Category / Subcategory"
- Subcategory should be specific enough to distinguish from other projects in the same category
- Examples: "Inference & Serving / Disaggregated Inference", "Standards / Agent-Tool Interoperability"

## Red Hat / IBM flags

If a project has Red Hat, IBM, or Neural Magic involvement (contributor, commercial backer, upstream investment):
- Add 🔴 after the project name in the `###` heading: `### vLLM 🔴`
- In Notable contributor(s), describe the nature of involvement
- Examples:
  - `**Notable contributors:** Red Hat/Neural Magic (primary commercial), NVIDIA, AMD...`
  - `**Notable contributors:** IBM Research, AMD, Red Hat (joint upstream contributions)...`

## Structural formatting

- Use `---` horizontal rules between categories
- Use `##` for category headings
- Use `###` for project names
- Bold all field labels
- One blank line between fields within an entry
- Two blank lines between entries within a category
