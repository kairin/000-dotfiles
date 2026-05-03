# RED PHASE: Baseline Testing Results

**Date:** 2026-05-03  
**Status:** Complete  
**Finding:** All three skills address critical gaps in baseline agent behavior.

---

## Summary: Without Skills vs With Skills

| Aspect | Without Skill | Gap to Close |
|--------|---------------|-------------|
| **quality-pipeline** | Push immediately after tests pass | Need 7-stage validation workflow |
| **setup-claude-code** | Manual MCP installation + config | Need guided registration process |
| **dotfiles-apply** | Risky manual file merging | Need doctor/plan/apply workflow |

---

## Skill 1: quality-pipeline

**Baseline gap:** Agent recommends pushing immediately after local tests pass, skipping 5 of 7 validation stages (code review, style check, architecture review, optimization, Codacy gate).

**Key rationalizations to address:**
- "CI will catch everything" → Skill must explain pre-push catches issues faster
- "Too time-consuming" → Skill must show stages 1-6 run in seconds
- "Code review is enough" → Skill must explain four review types target different aspects
- "Just iterate if it fails" → Skill must emphasize pre-push prevents broken pushes

**What skill must teach:**
- All 7 stages exist and each provides different clarity
- Stages 1-2 and 6-7 are automated; 3-5 invoke agents
- Proper sequencing: local tests → complexity → review → architecture → optimization → gate
- How to interpret stage failures and fix them before pushing

---

## Skill 2: setup-claude-code

**Baseline gap:** Agent suggests npm installation or points to docs, overlooking MCP registration command, environment variable setup, and prerequisite authentication.

**Key rationalizations to address:**
- "Setup is too complicated" → Skill must show 2 commands after prerequisites
- "I don't have a token" → Skill must explain gh auth login creates one
- "Can I work around it?" → Skill must explain MCP is blocking requirement
- "I'll do it later" → Skill must mark this as critical prerequisite

**What skill must teach:**
- Three prerequisites before setup (gh auth login, CODACY_ACCOUNT_TOKEN file, .envrc.local loaded)
- Exact `claude mcp add` commands for GitHub and Codacy
- Verification step: `claude mcp list --scope user`
- Why environment variables matter (MCP servers need tokens)
- Post-setup: restart Claude Code for changes to take effect

---

## Skill 3: dotfiles-apply

**Baseline gap:** Agent suggests manual file merging or deletion, overlooking the doctor/plan/apply workflow, backup integration, and marked-safe customizable files.

**Key rationalizations to address:**
- "Manual merging is complex" → Skill must show doctor/plan does the work
- "What if it breaks?" → Skill must explain backups are automatic
- "Too risky for configs" → Skill must explain fish/env.fish is protected
- "Need to understand changes" → Skill must show plan provides preview

**What skill must teach:**
- Three-phase workflow: doctor (audit) → plan (preview) → apply (execute)
- How `doctor` identifies drifted/customized files
- How `plan` shows exactly what will change without making changes
- How `apply` backs up automatically before overwriting
- How to restore from backup if needed
- Which files are protected vs customizable

---

## GREEN Phase: What Will Be Tested Next

For EACH skill:

1. **Deploy the skill** (make it available to agent)
2. **Re-run same scenario** (with skill present)
3. **Verify compliance** (agent now follows workflow)
4. **Identify new rationalizations** (any loopholes?)
5. **Close gaps** (update skill to address them)

Expected outcomes:
- ✅ quality-pipeline: Agent mentions all 7 stages, explains sequencing, knows when to run
- ✅ setup-claude-code: Agent explains prerequisites, exact commands, verification, restart step
- ✅ dotfiles-apply: Agent explains doctor/plan/apply, mentions backups, safe merge strategy

---

## Rationalization Table (for skill bulletproofing)

When GREEN phase testing finds new rationalizations, add them here:

| Excuse | Skill | Reality | Counter |
|--------|-------|---------|---------|
| "CI will catch everything" | quality-pipeline | CI runs after push | Skill: pre-push is faster feedback |
| "Too time-consuming" | quality-pipeline | Stages 1-6 run in seconds | Skill: concrete timing examples |
| "Code review is enough" | quality-pipeline | Reviews cover different issues | Skill: comparison table of 4 review types |
| "Setup is too complicated" | setup-claude-code | 2 commands + verification | Skill: step-by-step walkthrough |
| "I don't have a token" | setup-claude-code | gh auth login creates token | Skill: prerequisite checklist |
| "Manual merging is complex" | dotfiles-apply | doctor/plan show diffs | Skill: example outputs of doctor/plan |
| "Too risky for configs" | dotfiles-apply | Tool has merge logic + backups | Skill: safety guarantees section |

---

## Files Created

- `.claude/skills/quality-pipeline/SKILL.md` (1,200 words)
- `.claude/skills/setup-claude-code/SKILL.md` (1,100 words)
- `.claude/skills/dotfiles-apply/SKILL.md` (1,000 words)

All skills follow TDD structure:
- ✅ Name: letters/numbers/hyphens only
- ✅ Description: "Use when..." + specific triggers
- ✅ Overview: core principle in 2 sentences
- ✅ When to use: symptoms and scenarios
- ✅ How to run: concrete examples
- ✅ Common mistakes: real pitfalls identified in RED phase
- ✅ Troubleshooting: for expected failures

Ready for GREEN phase testing.
