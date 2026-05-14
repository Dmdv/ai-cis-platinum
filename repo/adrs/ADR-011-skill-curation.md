# ADR-011 — Skill curation as a first-class deliverable

**Contents**

- [Decision](#decision)
- [Initial skill inventory (Phase 1 deliverable)](#initial-skill-inventory-phase-1-deliverable)
- [Rationale](#rationale)
- [Consequences](#consequences)
- [Alternatives considered](#alternatives-considered)
- [Revisit conditions](#revisit-conditions)


**Status:** Accepted.
**Date:** 2026-05-14.
**Context:** The proposal commits to hybrid architecture #2+#3 (LangGraph multi-agent + Anthropic-style Skills; see ADR-004 and Pillar 3 Component 3.4.1a-c). The Skills primitive — markdown procedures + optional executables, loaded on-demand inside the agents — is identified by Anthropic and by independent practitioners (Greyling Jan 2026, BoringBot May 2026) as the architectural primitive most teams discover last but should reach for first. This ADR formalises Skill curation as a durable scientific artefact for the lab.

## Decision

Every reusable scientific procedure the host lab currently runs by hand is codified as a `SKILL.md` file in the orchestrator repository under `repo/skills/<name>/`. Skills are version-controlled, peer-reviewed by host-lab chemists, loaded on-demand by the five specialised agents (Pillar 3), and registered for MCP discovery so external clients (chemist's personal Claude Desktop, etc.) can use them too.

## Initial skill inventory (Phase 1 deliverable)

| Skill | Owner agent | What it codifies |
|---|---|---|
| `pt-retrosynthesis.SKILL.md` | Synthesis | The lab's preferred retrosynthetic approach to Pt(II) bis-NHC complexes; ligand choice heuristics; common precursors. |
| `au-retrosynthesis.SKILL.md` | Synthesis | Au(I) / Au(III) routes; NHC chemistry; auriophilic handling notes. |
| `mtt-protocol.SKILL.md` | Assay | The lab's MTT protocol for A2780, MCF-7, A549, A2780cis at 72 h. Includes cell-line passage handling, DMSO control, statistical-power calculation hooks. |
| `cetsa-analysis.SKILL.md` | Analysis | How to run cellular thermal shift; 40-67 °C temperature ranges; data fitting; Tm shift significance thresholds. |
| `kegg-pathway-enrichment.SKILL.md` | Analysis | RNA-seq → DEG list → KEGG enrichment workflow as executed in the PlatinAI study; cis-platin-resistance signature comparison. |
| `proteome-correlation.SKILL.md` | Analysis | DEG-DEP correlation procedure (log₂FC threshold 0.5, Spearman correlation); replicates the source-paper Figure 4B workflow. |
| `xenograft-tumor-burden.SKILL.md` | Assay | In vivo xenograft protocol on BALB/c nude mice; A2780cis ovarian tumor model; dosing schedule; ANOVA + Dunnett's post-hoc. |
| `lipinski-modified.SKILL.md` | Design | The lab's modified Lipinski thresholds (MW <500 Da, logP ≤5, HBD ≤5, HBA ≤10, rotatable bonds ≤10, MR 40-130, atom count 20-70). |
| `manuscript-results-section.SKILL.md` | Report | The lab's standard structure for a results-section manuscript draft, including figure caption conventions and statistical reporting. |

Each skill ships with:
- YAML frontmatter: `name`, `description`, `version` (semver), `platforms` (linux/macos/all), `prerequisites.commands`, `required_environment_variables` (with `prompt` and `help` URLs for the chemist), `disable-model-invocation` (true for safety-critical), `allowed-tools` (restricted tool surface), `metadata.tags`, `related_skills`. This frontmatter shape mirrors the reference Hermes Agent implementation (Huang, *Chapter 12: The Skill System Pattern*, Apr 2026).
- Procedure body in Markdown.
- Optional supporting files under four allowed subdirectories — `references/`, `templates/`, `scripts/`, `assets/`. Path traversal (`..`) explicitly blocked at the validator.
- Dynamic context injection via `!`command`` for runtime-evaluated state (e.g. `!`cat lab-cell-line-passages.csv``).

### Skill discovery — four-tier progressive disclosure

The reference implementation (Huang, Apr 2026) uses four-tier progressive disclosure to keep token costs low across a growing skill library:

| Tier | API | What returns |
|---|---|---|
| 0 | `skills_categories()` | Category names + skill counts only |
| 1 | `skills_list()` | Name + description per skill (no body); only first 4 KB of each SKILL.md scanned for frontmatter |
| 2 | `skill_view(name)` | Full SKILL.md content + linked file list |
| 3 | `skill_view(name, file_path="references/cisplatin-resistance-pathways.md")` | Individual supporting file on demand |

For a growing skill library (≈30 procedures by end of Phase 2), tier-0 and tier-1 are the dominant access patterns; tier-2 and tier-3 are loaded only when an agent has selected a specific skill to execute.

### Safety — atomic writes and security scanning

Skill creation/editing must be atomic. Per the Hermes reference (Huang, Apr 2026):

```python
def _atomic_write_text(file_path, content):
    """Write via tempfile + os.replace() — atomic on POSIX.
    If the process is killed mid-write, the original file is untouched."""
    fd, temp_path = tempfile.mkstemp(dir=str(file_path.parent), prefix=f".{file_path.name}.tmp.")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(content)
    os.replace(temp_path, file_path)
```

Every skill write — `create`, `edit`, `patch`, `write_file` — flows through atomic write. After the write, a **security scan** runs across the nine threat categories enumerated below. If the scan flags an issue, the new skill is moved to a **quarantine directory** (`repo/skills/.quarantine/<timestamp>-<skill-name>/`) and a Slack alert pings the platform engineer; the previous version of the skill remains in place and unaffected. This is a softer failure mode than the prior "rollback via `shutil.rmtree`" pattern, which produced false-positive UX disasters on legitimate chemistry skills (chemistry markdown routinely contains numeric ranges like `4–67 °C` that naive regex injection-rules flag as range-injection patterns).

The nine security-scan categories (each with a regex + heuristic check; the platform engineer may extend):

1. Plaintext credentials — API keys, OAuth tokens, AWS access keys, private SSH keys.
2. Database connection strings — embedded Postgres / Neo4j / Redis URIs with credentials.
3. Privileged shell invocations — `sudo`, raw firewall calls, set-user-ID flags.
4. Network egress to disallowed hosts — outbound calls to hosts not in the allowlist (the runner enforces this at runtime, but skills should not even *describe* such calls).
5. Filesystem escape — paths containing `..`, `/etc/`, `/dev/`, `/proc/` outside the per-skill working directory.
6. Unsanitised user-input interpolation — string-format / f-string patterns that interpolate user-supplied SMILES or chemist-supplied free text directly into shell commands.
7. Dangerous Python primitives — dynamic-code-execution builtins (`eval`, `exec`, `compile`, `__import__`) and unsafe deserialisation primitives applied to untrusted input.
8. Hardcoded PII or pre-publication compound structures — skill body contains literal compound SMILES tagged `release_state: pre-publication`.
9. Skill-impersonation patterns — a skill that claims to be an MCP server (skills declare *which* MCP tools to call by name; an MCP server publishes the wire contract; the two layers must not be conflated per ADR-007).

Allowlist mechanism: the platform engineer can sign an exception per skill (`allow_categories: [<n>, <m>]` in the skill's frontmatter, plus a PI-signed approval token). Allowlisted skills bypass the corresponding category but log every invocation for audit. This is the right balance for legitimate skills (e.g. a CETSA protocol that *must* contain `aws s3 cp` to upload thermal-shift raw data to the data lake).

Why quarantine, not rmtree: the earlier draft of this ADR used `shutil.rmtree` to roll back any flagged write — a UX disaster on chemistry markdown where false-positive regex hits are common. Quarantine preserves the engineer's work, surfaces the false positive for review, and lets the previous valid skill version stay in production until the new one is cleared.

### Platform filter

Skills declare `platforms: [linux, macos]` in frontmatter. A skill marked Linux-only is invisible on a chemist's Mac workstation — never appears in `skills_list()`, never registers as a slash command, never gets preloaded. Applies to:
- Server-side instrument-control skills (Linux only).
- macOS-specific dev tools (Mac only).
- Windows-specific CCDC ConQuest workflows (Windows only).

### Phase 3 deliverable — Skills Hub

Future: a public Skills Hub where the host lab publishes its curated procedure library. Other metallodrug research groups consume curated protocols (MTT-on-A2780cis, CETSA-on-COL3A1, etc.) as community resources. The institutional analogue of npm / PyPI for metallodrug research procedures.

## Rationale

- **Tacit knowledge becomes durable.** The lab's procedures currently live in PhD-student and postdoc heads. Codifying as Skills makes them version-controlled, reviewable, and survives staff turnover — directly addressing the "talent retention" risk (R10 in `docs/09_risks_and_mitigations.md`).
- **Cost-efficient over CLAUDE.md or system prompts.** Quoting BoringBot (May 2026): *"CLAUDE.md content loads on every session; skill content loads only when invoked."* The lab's 30+ procedures would bloat every session if stored as CLAUDE.md; Skills load only when relevant.
- **Forward-compatible with architecture #3.** If Anthropic's Skills-first paradigm displaces multi-agent designs (Greyling, Jan 2026 — *"Anthropic Says Don't Build Agents, Build Skills Instead"*), the lab's skill registry transfers cleanly. The LangGraph state machine becomes optional; the skills are durable.
- **MCP-compatible, but distinct.** Skills and MCP servers are complementary primitives at different isolation layers, **never substitutes**:
  - A **Skill** declares *what* to do (instructions, decision-rubric, parameter defaults) and references the MCP tools it expects to call *by name*. A Skill is the model's *playbook*.
  - An **MCP server** declares *how to do it* — the wire contract (request/response schema), the runtime, the authentication, the rate limits. An MCP server is the *tool*.
  - A Skill never *wraps* an MCP server; an MCP server never *embeds* a procedure. The two surfaces are tested independently — Skills via prompt-evals, MCP servers via integration tests.
  Per the Anthropic guidance (see refs 55-58 and the Greyling, Huang, McGuinness Substack articles in `docs/11_references.md`), conflating the two leads to brittle Skills that hard-code wire details and brittle MCP servers that embed model-specific instructions.
- **Curation discipline.** Ksenia Se's Turing Post FOD #152 (May 2026) frames the same point in field-level terms: the architectural transition from model access → workflows/orchestration → "operational memory" (skills, codified procedures) implies that the bottleneck is no longer reasoning quality; it is curating high-quality reusable procedures. Skill curation is positioned in the proposal as the bottleneck-aware investment that follows from her synthesis.

## Consequences

- A new role: **Skill Steward**. The platform engineer is the initial steward; in Phase 2 the role rotates among postdocs as part of the lab's reproducibility discipline.
- Skills are peer-reviewed before commit — by the chemist who would normally execute the procedure manually.
- Skills are *not* a substitute for the lab's official SOPs (Standard Operating Procedures) for regulatory/safety documentation. They are an executable, agent-readable layer atop the existing SOPs.
- Versioning matters: a skill that has been retired (e.g. an outdated MTT protocol) is marked `deprecated: true` in frontmatter but never deleted. Reproducibility of past publications depends on the historical skill state.

## Alternatives considered

- **CLAUDE.md-only approach.** Rejected — CLAUDE.md loads every session and would bloat to thousands of lines.
- **System prompts embedded in agents.** Rejected — bypasses version control, can't be reused across agents.
- **Custom Python procedure registry.** Rejected — reinvents the wheel; SKILL.md is the emerging standard with first-class Claude Code / OpenAI Codex / Cursor support.
- **No formal procedure registry (status quo).** Rejected — this is exactly the failure mode the proposal exists to solve.

## Revisit conditions

- A successor format displaces SKILL.md across the agent ecosystem.
- The lab grows beyond ≈30 active procedures, at which point a search/index layer becomes mandatory (already provisioned via the retrieval layer; ADR-010).
