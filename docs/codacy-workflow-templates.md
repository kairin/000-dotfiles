# Codacy workflow templates

Reusable CI snippets for repositories in `codacy-rollout.json`. Keep repository
names, job names, and test commands aligned with the inventory before enforcing
the checks in GitHub rulesets.

## Python uv + coverage.py

```yaml
jobs:
  codacy-safety-net:
    runs-on: ubuntu-latest
    env:
      CODACY_ACCOUNT_TOKEN: ${{ secrets.CODACY_ACCOUNT_TOKEN }}
      CODACY_API_TOKEN: ${{ secrets.CODACY_ACCOUNT_TOKEN }}
      CODACY_ORGANIZATION_PROVIDER: gh
      CODACY_USERNAME: kairin
      CODACY_PROJECT_NAME: 000-dotfiles
    steps:
      - uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd
      - uses: astral-sh/setup-uv@08807647e7069bb48b6ef5acd8ec9567f424441b
      - run: uv run --with coverage coverage run -m unittest discover -s tests
      - run: uv run --with coverage coverage xml
      - if: ${{ env.CODACY_ACCOUNT_TOKEN != '' }}
        run: bash <(curl -Ls https://coverage.codacy.com/get.sh) report -r coverage.xml
```

## Node npm/Vitest coverage

```yaml
jobs:
  node-validation:
    runs-on: ubuntu-latest
    env:
      CODACY_ACCOUNT_TOKEN: ${{ secrets.CODACY_ACCOUNT_TOKEN }}
      CODACY_API_TOKEN: ${{ secrets.CODACY_ACCOUNT_TOKEN }}
      CODACY_ORGANIZATION_PROVIDER: gh
      CODACY_USERNAME: kairin
      CODACY_PROJECT_NAME: my-node-repo
    steps:
      - uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd
      - uses: actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020
        with:
          node-version: 22
          cache: npm
      - run: npm ci
      - run: npm test -- --coverage
      - if: ${{ env.CODACY_ACCOUNT_TOKEN != '' }}
        run: bash <(curl -Ls https://coverage.codacy.com/get.sh) report -r coverage/lcov.info
```

## Mixed Node + Python

```yaml
jobs:
  graph-obsidian-validation:
    runs-on: ubuntu-latest
    env:
      CODACY_ACCOUNT_TOKEN: ${{ secrets.CODACY_ACCOUNT_TOKEN }}
      CODACY_API_TOKEN: ${{ secrets.CODACY_ACCOUNT_TOKEN }}
      CODACY_ORGANIZATION_PROVIDER: gh
      CODACY_USERNAME: kairin
      CODACY_PROJECT_NAME: graph-obsidian
    steps:
      - uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd
      - uses: actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020
        with:
          node-version: 22
          cache: npm
      - uses: astral-sh/setup-uv@08807647e7069bb48b6ef5acd8ec9567f424441b
      - run: npm ci
      - run: npm test -- --coverage
      - run: uv run --with coverage coverage run -m unittest discover -s tests
      - run: uv run --with coverage coverage xml
      - if: ${{ env.CODACY_ACCOUNT_TOKEN != '' }}
        run: bash <(curl -Ls https://coverage.codacy.com/get.sh) report -r coverage/lcov.info
      - if: ${{ env.CODACY_ACCOUNT_TOKEN != '' }}
        run: bash <(curl -Ls https://coverage.codacy.com/get.sh) report -r coverage.xml
```
