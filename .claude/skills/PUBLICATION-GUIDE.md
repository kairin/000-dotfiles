# Marketplace Publication Guide

**Goal:** Make your three skills available globally via https://code.claude.com/docs/en/plugin-marketplaces

**Status:** Skills are tested and ready. Choose your publication path below.

---

## Two Publication Paths

### Path 1: Contribute to claude-plugins-official (Recommended)

**Pros:**
- Official Anthropic marketplace
- Automatic discovery in claude.ai/customize/skills
- Available to all Claude Code users
- Vetted by Anthropic team
- Free distribution

**Cons:**
- Requires PR review process (1-2 weeks)
- Must follow Anthropic's guidelines
- Less control over versioning

**Steps:**

1. **Fork the repository**
   ```bash
   gh repo fork https://github.com/anthropics/claude-plugins-official
   ```

2. **Add your skills**
   ```bash
   cd claude-plugins-official
   
   # Copy skills to official structure
   mkdir -p skills/quality-pipeline
   mkdir -p skills/setup-claude-code
   mkdir -p skills/dotfiles-apply
   
   cp ~/Apps/000-dotfiles-main/.claude/skills/quality-pipeline/SKILL.md skills/quality-pipeline/
   cp ~/Apps/000-dotfiles-main/.claude/skills/setup-claude-code/SKILL.md skills/setup-claude-code/
   cp ~/Apps/000-dotfiles-main/.claude/skills/dotfiles-apply/SKILL.md skills/dotfiles-apply/
   ```

3. **Validate against schema**
   ```bash
   ./scripts/validate-skill-schema.sh skills/quality-pipeline/SKILL.md
   ./scripts/validate-skill-schema.sh skills/setup-claude-code/SKILL.md
   ./scripts/validate-skill-schema.sh skills/dotfiles-apply/SKILL.md
   ```

4. **Create PR**
   ```bash
   git add skills/quality-pipeline/ skills/setup-claude-code/ skills/dotfiles-apply/
   git commit -m "Add dotfiles quality pipeline skills: quality-pipeline, setup-claude-code, dotfiles-apply"
   gh pr create --repo anthropics/claude-plugins-official \
     --title "Add dotfiles quality pipeline skills" \
     --body "Three tested skills for dotfiles project:

- quality-pipeline: 7-stage validation before pushing
- setup-claude-code: One-time global Claude Code setup
- dotfiles-apply: Safe doctor/plan/apply workflow

All skills tested with RED-GREEN TDD methodology."
   ```

5. **Wait for review** (Anthropic team)

6. **After merge** — Skills automatically available to all users:
   - `claude.ai/customize/skills` shows them
   - `/skill install quality-pipeline` works
   - Auto-discoverable in Claude Code

---

### Path 2: Private/Team Registry (If Org-Specific)

**Pros:**
- Full control over distribution
- Can iterate faster
- Team-only or organization-only
- Immediate publication

**Cons:**
- No official Anthropic vetting
- Requires hosting your own registry
- Limited discovery (must share link)

**Steps:**

1. **Structure as a plugin** (instead of individual skills)
   ```
   dotfiles-quality-gate-plugin/
     plugin.json
     skills/
       quality-pipeline/SKILL.md
       setup-claude-code/SKILL.md
       dotfiles-apply/SKILL.md
     hooks/
       hooks.json
     README.md
   ```

2. **Create plugin.json**
   ```json
   {
     "name": "dotfiles-quality-gate",
     "version": "0.1.0",
     "description": "Complete quality pipeline for dotfiles: validation, setup, and application",
     "author": "kairin",
     "skills": [
       { "name": "quality-pipeline", "id": "quality-pipeline" },
       { "name": "setup-claude-code", "id": "setup-claude-code" },
       { "name": "dotfiles-apply", "id": "dotfiles-apply" }
     ],
     "mcp": {
       "required": ["github", "codacy"],
       "optional": []
     }
   }
   ```

3. **Publish to GitHub Releases**
   ```bash
   # Tag and release
   git tag v0.1.0
   git push origin v0.1.0
   
   # GitHub Actions auto-creates release artifact
   # Users install via URL: github.com/kairin/000-dotfiles/releases/tag/v0.1.0
   ```

4. **Share installation link**
   ```bash
   # Users run:
   claude plugin install https://github.com/kairin/000-dotfiles/releases/download/v0.1.0/dotfiles-quality-gate.zip
   ```

---

## Recommended: Hybrid Approach

1. **Submit to claude-plugins-official** (official vetting, broad distribution)
2. **Also maintain in dotfiles repo** (local development, rapid iteration)

This gives you:
- Official marketplace presence for user discovery
- Local repo for bug fixes and updates
- Ability to iterate quickly while official process moves slower

**Workflow:**
```
Local development in ~/Apps/000-dotfiles-main/.claude/skills/
    ↓
Test with RED-GREEN methodology
    ↓
Push local changes to dotfiles repo
    ↓
When ready for release:
  - Copy to claude-plugins-official fork
  - Submit PR
  - Merge → Auto-available to all users
```

---

## Marketplace Discovery Optimization

Users will find your skills via:

1. **Direct search** (claude.ai/customize/skills)
   - Search: "quality pipeline" → finds quality-pipeline skill
   - Search: "dotfiles" → finds all three skills
   - Search: "setup claude code" → finds setup-claude-code skill

2. **Claude Code discovery**
   - Open dotfiles project
   - SessionStart hook suggests: "Run quality pipeline?"
   - User clicks → skill loads
   - `/quality-pipeline` slash command works

3. **Cross-references**
   - In CLAUDE.md: Link to `/quality-pipeline`
   - In README: "First time? Install quality-pipeline skill"
   - In setup script: Suggest `/setup-claude-code`

---

## What Happens After Publication

### For Users (Online)
1. Visit claude.ai/customize/skills
2. Search "quality pipeline" or "dotfiles"
3. Click "Install"
4. Skill available in all Claude sessions
5. Can invoke via `/quality-pipeline`, `/setup-claude-code`, `/dotfiles-apply`

### For Users (Local Claude Code)
1. Open dotfiles project
2. Skills auto-load from global registry
3. SessionStart hook prompts: "Run quality pipeline?"
4. Can invoke via slash commands or just reference the skill in prompts

### For You (Maintainer)
1. Bug fix in skill? Update `.claude/skills/quality-pipeline/SKILL.md`
2. Push to dotfiles repo
3. If published to official marketplace, submit PR with update
4. Users get update on next Claude Code restart

---

## Publication Checklist

- [x] Skills created with proper YAML frontmatter
- [x] Tested with RED-GREEN TDD methodology
- [x] Documentation complete (how-to, troubleshooting, common mistakes)
- [x] Keywords optimized for discovery
- [x] Cross-references between skills
- [x] Supporting files (if needed) included
- [ ] **Choose publication path** (Official marketplace vs private)
- [ ] **Commit and push to dotfiles repo**
- [ ] **If official: Fork and submit PR**
- [ ] **If private: Configure release/registry**
- [ ] **Share with team/users**
- [ ] **Monitor for feedback and iterate**

---

## Recommended Action

**Right now:**
1. Commit your three skills to dotfiles repo
2. Submit PR to claude-plugins-official

**Timeline:**
- Week 1: Skills in official marketplace (pending Anthropic review)
- Week 2+: Iterate on feedback, address known gaps (REFACTOR phase)

**Expected users:**
- Immediate: Your team (via dotfiles repo)
- 1-2 weeks: All Claude Code users (via official marketplace)

---

## Links

- **Official Marketplace Docs:** https://code.claude.com/docs/en/plugin-marketplaces
- **Claude Plugins Official Repo:** https://github.com/anthropics/claude-plugins-official
- **Skill Specification:** https://agentskills.io/specification
- **Discovery Best Practices:** (covered in superpowers:writing-skills)

---

## Next Steps

Choose your path:

```bash
# Path 1: Official Marketplace
gh repo fork https://github.com/anthropics/claude-plugins-official
# Follow steps above to add skills and create PR

# Path 2: Private Registry
# Create plugin.json, tag release, share link with team

# Both Paths: First commit to dotfiles repo
cd ~/Apps/000-dotfiles-main
git add .claude/skills/
git commit -m "Add three publishable skills: quality-pipeline, setup-claude-code, dotfiles-apply"
git push origin 20260503-024509-setup-fixes
```

Ready to publish?
