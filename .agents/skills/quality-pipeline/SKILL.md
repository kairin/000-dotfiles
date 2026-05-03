---
name: quality-pipeline
description: Use when about to push feature branch code and need automated validation across tests, complexity checks, code review, style conventions, architecture analysis, and Codacy quality gates
tags: [validation, code-review, quality-gates, pre-push, automation]
---

# Quality Pipeline

## Overview

A 7-stage automated validation workflow that runs **before pushing to remote**, catching issues locally at zero cost. Each stage builds on the previous one, providing progressive clarity: tests → code quality → style → architecture → local optimization → final Codacy gate.

The pipeline chains together multiple specialized tools (unit tests, complexity analysis, GitHub MCP, Codacy MCP, code review agents) into a single orchestrated flow.

## When to Use

Use this skill when:
- About to push feature branch changes to remote
- Want to fail fast before expensive GitHub Actions runs
- Need code review feedback before creating PR
- Integrating multiple quality tools (tests, linting, code review, security)
- Team wants consistent pre-push validation

**NOT for:**
- Main/master branch (already in CI)
- One-off fixes that are obviously safe
- Emergency hotfixes (use `git push --no-verify` if needed)

## The 7 Stages

```
Stage 1: Local Pre-Push       → Unit tests + complexity + type checks (git hook)
Stage 2: GitHub MCP           → Push + PR creation
Stage 3: Code Review          → Logic errors + security vulnerabilities
Stage 4: PR Conventions       → Style guide + test coverage compliance
Stage 5: Architecture         → Design patterns + feature completeness
Stage 6: Local Optimization   → File size analysis + import chain depth
Stage 7: Codacy Gate          → Remote quality gate (final verdict)
```

Each stage must pass before continuing. Stages 1-2 and 6-7 run automatically. Stages 3-5 invoke specialized agents.

## How to Run

### Manual Invocation
```bash
./scripts/quality-pipeline.sh         # Full pipeline
./scripts/quality-pipeline.sh 123     # With existing PR #123
```

### Automatic (via Hook)
When you open the project in Claude Code:
- SessionStart hook prompts: "Run quality pipeline?"
- Select yes
- Pipeline executes automatically

### From Claude Code
Invoke the skill:
```
/quality-pipeline
```

## Quick Reference: Stage Responsibilities

| Stage | Blocks? | Tool | Output |
|-------|---------|------|--------|
| 1. Tests | ✓ Hard | `unittest discover` | Pass/fail |
| 2. GitHub MCP | ✓ Hard | `gh pr create` | PR URL + number |
| 3. Code Review | ⚠ Pending | superpowers:code-reviewer | Issues found |
| 4. Style Check | ⚠ Pending | pr-review-toolkit | Convention violations |
| 5. Architecture | ⚠ Pending | feature-dev | Design issues |
| 6. Local Opt | ✓ Auto | Desktop Commander | Optimization suggestions |
| 7. Codacy | ✓ Hard | Codacy MCP | Quality gate: pass/fail |

## Common Mistakes

**Skipping the pipeline because "it's just a small change"**
- Reality: Small changes introduce subtle bugs (test coverage gaps, complexity creep)
- Fix: Always run pipeline, no exceptions

**Running only stages 1-2 and skipping code review (stages 3-5)**
- Reality: Tests pass but code quality issues slip through
- Fix: Run full pipeline; at minimum wait for human code review

**Interpreting "pending" (⚠) agents as "not required"**
- Reality: Pending agents are awaiting implementation; if available, they provide critical feedback
- Fix: When agents are available, require them (don't make them optional)

**Using `--no-verify` to bypass the hook**
- Reality: Bypassing local validation leads to failures in CI
- Fix: Fix the issue properly; only use `--no-verify` for emergency hotfixes

**Running pipeline once and assuming subsequent pushes are safe**
- Reality: Each push introduces new code
- Fix: Run pipeline before every push

## Expected Output

```
╔════════════════════════════════════════════════════════════════╗
║        Comprehensive Quality Pipeline - 7 Stages               ║
╚════════════════════════════════════════════════════════════════╝

[STAGE 1/7] LOCAL PRE-PUSH VALIDATION
────────────────────────────────────────────────────────────
✓ All unit tests passed
✓ Modified files meet complexity standards
⚠ 2 functions lack return type annotations (warning only)

[STAGE 2/7] GITHUB MCP - PUSH & PR CREATION
────────────────────────────────────────────────────────────
✓ Push successful (hook validation passed)
✓ PR #162 created: https://github.com/kairin/000-dotfiles/pull/162

[STAGE 3/7] CODE REVIEW - BUG & SECURITY ANALYSIS
────────────────────────────────────────────────────────────
⟳ Code review (pending manual review or agent)

[STAGE 7/7] CODACY MCP - REMOTE QUALITY GATE (FINAL)
────────────────────────────────────────────────────────────
✓ Codacy quality gate: PASS
═══════════════════════════════════════════════════════════════

✓ PIPELINE COMPLETE
Ready to merge!
```

## Implementation Notes

The pipeline is implemented as a bash script (`.scripts/quality-pipeline.sh`) that:
1. Checks git status and modified files
2. Runs local validation (stages 1-2, 6)
3. Invokes GitHub MCP for PR operations
4. Dispatches subagents for code review (stages 3-5) if available
5. Polls Codacy for quality gate status
6. Reports summary with next actions

To understand the full implementation, see:
- `.git/hooks/pre-push` — Local validation rules
- `.claude/settings.json` — SessionStart hook that prompts user
- `scripts/quality-pipeline.sh` — The orchestration script
- Codebase conventions in `CLAUDE.md`

## Troubleshooting

**"Stage 1 failed: Unit tests did not pass"**
- Cause: Test failures on current branch
- Fix: `uv run python -m unittest discover -s tests` (run locally, fix failures)

**"Stage 2 failed: Failed to create PR"**
- Cause: PR already exists or gh not authenticated
- Fix: `gh auth status` (verify login); if PR exists, script uses it

**"Stage 7 timeout: Codacy gate still running"**
- Cause: Codacy analysis takes time (normal)
- Fix: Wait 5-10 minutes, check PR status with `gh pr view <number> --web`

**"I need to skip stages 3-5 because agents aren't ready"**
- Correct: Stages 3-5 are currently placeholders waiting for agent implementation
- Use stages 1-2, 6-7 for now; stages 3-5 will auto-enable when agents are available

## Real-World Impact

Before pipeline:
- Push code → GitHub Actions runs → 5 min wait → Codacy fails → Fix locally → Repush → Another 5 min
- Result: 15-30 min per cycle, expensive cloud runs

After pipeline:
- Run locally → Fix immediately → Push once → All checks pass in CI
- Result: 2-3 min cycle, zero wasted cloud resources
