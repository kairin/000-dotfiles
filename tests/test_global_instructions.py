from tests.helpers import DotfilesTestCase, REPO_ROOT


class GlobalInstructionTests(DotfilesTestCase):
    GLOBAL_INSTRUCTION_TEMPLATES = (
        REPO_ROOT / "claude" / "CLAUDE.md.template",
        REPO_ROOT / "gemini" / "GEMINI.md.template",
        REPO_ROOT / "codex" / "AGENTS.md.template",
        REPO_ROOT / "copilot" / "copilot-instructions.md.template",
    )

    REQUIRED_PHRASES = (
        "## Workspace, Hooks, And Publishing Rules",
        "`/home/kkk/Apps` is a workspace container",
        "Git hooks are installed per repository, not per AI tool",
        "Never run `git push origin main`",
        "For `/home/kkk/Apps/000-dotfiles`, use `./setup ship [<pr-number>]`",
        "Do not use `gh pr merge`, `gh api`, or direct REST merge calls",
    )

    def test_global_instruction_templates_share_workspace_hook_rules(self) -> None:
        for path in self.GLOBAL_INSTRUCTION_TEMPLATES:
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                text = path.read_text()
                for phrase in self.REQUIRED_PHRASES:
                    self.assertIn(phrase, text)

    def test_hook_trigger_map_documents_each_tool(self) -> None:
        docs = [
            REPO_ROOT / "README.md",
            REPO_ROOT / "AGENTS.md",
        ]
        phrases = (
            "Claude Code",
            "Gemini CLI",
            "Codex CLI",
            "Copilot CLI",
            "repo hook",
            ".git/hooks/pre-push",
        )
        for path in docs:
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                text = path.read_text()
                for phrase in phrases:
                    self.assertIn(phrase, text)

    def test_gemini_instructions_document_own_hook_surface(self) -> None:
        text = (REPO_ROOT / "gemini" / "GEMINI.md.template").read_text()
        phrases = (
            "Gemini CLI does not run Claude Code hooks automatically",
            "Use Gemini's own hook surface only if intentionally configured",
            "interactive `/hooks` slash command",
            "`gemini hooks --help`",
            "Do not use `gemini hooks list`",
            "Do not run `gemini hooks migrate` unless the user explicitly asks",
            "Main-branch push prevention is enforced by Git's repo hook",
        )
        for phrase in phrases:
            self.assertIn(phrase, text)
