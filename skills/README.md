# BCM Skills

Reusable BCM Codex skills and the installer used to copy them into user scope.

## Files

- [bcm-direnv-codacy/SKILL.md](./bcm-direnv-codacy/SKILL.md)
- [bcm-github-cicd/SKILL.md](./bcm-github-cicd/SKILL.md)
- [install.sh](./install.sh)

## Install to user scope

Run the installer from this folder:

```bash
bash ./install.sh
```

Or copy the skill directories manually:

```bash
mkdir -p ~/.codex/skills
cp -R ./bcm-direnv-codacy ~/.codex/skills/
cp -R ./bcm-github-cicd ~/.codex/skills/
```
