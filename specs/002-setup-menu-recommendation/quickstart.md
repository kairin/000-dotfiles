# Quickstart: Setup Menu Recommendation Guidance

## 1. Run The Focused Tests

```bash
uv run python -m unittest tests.test_machine_summary tests.test_setup_script tests.test_docs
```

Expected result: the tests cover missing-tools, safe-changes-pending,
blockers-present, auth-guidance-only, protected/manual-only, and fully-current
recommendation states.

## 2. Run The Full Test Suite

```bash
uv run python -m unittest discover -s tests
```

Expected result: all existing setup, manifest, project-init, docs, and workflow
tests still pass.

## 3. Verify Fresh-Machine Recommendation

Run `./setup` in an environment where one or more baseline developer tools are
missing.

Expected result:

- The summary shows missing tools.
- The menu includes `Recommended next step: 1. ...`.
- Only option 1 has `[recommended]`.
- Declining the tool install prompt returns to a refreshed summary and menu
  without writing files.

## 4. Verify Configured-Machine Recommendation

Run `./setup` in an environment where developer tools are present and at least
one safe non-protected dotfile or font action is pending.

Expected result:

- The summary names pending safe changes.
- The menu includes `Recommended next step: 2. ...`.
- Only option 2 has `[recommended]`.
- Safe apply still requires explicit confirmation and backups.

## 5. Verify No-Action Recommendation

Run `./setup` in an environment where tools are present, safe dotfiles and fonts
are current, no blockers exist, and no auth guidance remains.

Expected result:

- The summary states that setup is current.
- The menu recommends option 5, exit without writing.
- Choosing option 5 exits without writes.

## 6. Verify Documentation Alignment

Review these files after implementation:

- `README.md`
- `docs/getting-started.md`
- `tests/test_docs.py`

Expected result: documented menu labels and recommendation states match the
actual setup output, including the fresh-machine transition from option 1 to
option 2.
