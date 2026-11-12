# AGENTS.md

Guidance for AI coding agents working in this repository. Humans: see
[CONTRIBUTING.md](CONTRIBUTING.md). Everything here is public; never paste
embargoed advisory details, private tracker IDs, or audit logs with real
customer data into issues, PRs, commits, or reviews.

## What this repository is

OWASP CRS (Core Rule Set) is a set of generic attack-detection rules written in
SecLang for OWASP ModSecurity (v2 and libmodsecurity3), OWASP Coraza, and
compatible WAF engines. Rules are deployed in production WAFs worldwide: a wrong
regex is either a bypass (false negative) or an outage (false positive). Human
review is mandatory; agents assist, they do not decide. Read
[AI-CONTRIBUTIONS.md](AI-CONTRIBUTIONS.md) before contributing.

The project uses anomaly scoring: detection rules add to `tx.*_score` and
`tx.inbound_anomaly_score_plN`; the 949 (request) and 959 (response) rules
decide whether to block. Rules are grouped in paranoia levels (PL1-PL4); PL1
runs by default and must be nearly free of false positives.

## Layout

| Path | Contents |
|------|----------|
| `rules/*.conf` | The rule files. Name prefix carries the ID range (`REQUEST-942-...` holds `942xxx`). Rule order inside a file is by paranoia level, not ID. |
| `rules/*.data` | Word lists loaded by `@pmFromFile` (scanner UAs, shell commands, restricted files, error strings). |
| `rules/*.conf.example` | 900 and 999 exclusion templates users copy. Not loaded by the engine as shipped. |
| `crs-setup.conf.example` | User configuration template (paranoia level, thresholds, allowed methods, etc.). |
| `regex-assembly/*.ra` | Sources for the regexes in `rules/*.conf`, compiled by `crs-toolchain`. `include/` holds shared fragments, `exclude/` false-positive exclusions, `generators/` scripts for some lists. |
| `tests/regression/tests/<RULE-FILE>/<ruleid>.yaml` | go-ftw tests, one file per rule. |
| `tests/regression/*-overrides.yaml` | Engine-specific test overrides CI passes to go-ftw (`httpd`, `nginx`, `coraza`). |
| `tests/docker-compose.yml` | Test stack: `modsec2-apache`, `modsec3-nginx`, `coraza-caddy` (plus `-debug` variants) and the `backend` reflector. All share port 80, so run one engine at a time. |
| `plugins/` | Empty plugin slots; real plugins live in their own repos. |
| `crs-linter.toml` | Linter config, including `approved_tags`. New tags go here first. |
| `CHANGES.md`, `KNOWN_BUGS.md`, `SECURITY.md`, `BACKPORT_POLICY.md` | Changelog, caveats, supported versions, LTS policy. |

ID blocks: 901 init, 905 exceptions, 911 methods, 913 scanners, 920 protocol
enforcement, 921 protocol attack, 922 multipart, 930 LFI, 931 RFI, 932 RCE,
933 PHP, 934 generic, 941 XSS, 942 SQLi, 943 session fixation, 944 Java,
949 inbound blocking, 950-956 response leakage, 959 outbound blocking,
980 correlation. Detection rules start at `9xx100` in steps of 10; a stricter
sibling takes the next digit (`9xx161` for `9xx160`). `9xx011-9xx018` are the
paranoia-level skip rules. See CONTRIBUTING.md "ID Numbering Scheme".

## Related repositories (github.com/coreruleset)

| Repo | Relationship |
|------|--------------|
| `crs-toolchain` | Compiles `.ra` files into rule regexes, renumbers tests, bumps versions. Version pinned in `.github/workflows/lint.yaml` and `.pre-commit-config.yaml`. |
| `go-ftw` | Runs the YAML regression tests. Version pinned in `.github/workflows/test.yml` (`GO_FTW_VERSION`). |
| `ftw-tests-schema` | Spec for the test YAML format. Tests here use v2. |
| `crs-linter` | Checks rule formatting, tags, versions, test coverage. Version pinned in `lint.yaml` (`CRS_LINTER_VERSION`). |
| `secrules_parsing` | SecLang parser the lint workflow uses for syntax checks. |
| `modsecurity-crs-docker`, `coraza-crs-docker` | Build the engine images the test stack runs (`owasp/modsecurity-crs`, `ghcr.io/coreruleset/coraza-crs`). Image digests are pinned in `tests/docker-compose.yml`. |
| `albedo` | HTTP reflector used as the test backend (`/get`, `/post`, `/reflect`, ...). |
| `documentation` | Source of https://coreruleset.org/docs/. Rule or config changes that affect users need a docs PR there. |
| `plugin-registry`, `*-plugin` | Plugins (app exclusions, DoS, antivirus, ...) use the `9xxxxxx` ID space and are tested with `crs-plugin-test-action`. |
| `crslang` | Next-generation rule language. Not used by this repo yet. |

Security reports go through GitHub Security Advisories on this repo
(see `SECURITY.md`). Fixes for advisories are developed in private forks and
land here as normal-looking commits; do not speculate about them publicly.

## Branches and versions

- `main` is the development branch. Every rule carries the same
  `ver:'OWASP_CRS/X.Y.Z-dev'`; copy it from a neighbouring rule. The linter
  derives the expected string from git tags.
- `lts/v4.25.x` is the long-term-support line. Only security, regression,
  critical false-positive and engine-compatibility fixes are backported
  (`BACKPORT_POLICY.md`). Other false-positive fixes, comment corrections and
  `.data` additions need approval from two core developers. New rules, PL
  changes and refactors never go there, unless a security fix requires the
  refactor.
- `v3.3/master` and older are end of life. Do not target them.
- Releases are tagged `vX.Y.Z` from a `chore: release vX.Y.Z` commit that bumps
  versions with `crs-toolchain chore update-copyright` and updates `CHANGES.md`.

## Making changes

### Rules

- Copy the shape of a neighbouring rule in the same file. Actions must appear
  in the order given in CONTRIBUTING.md; always write `@rx` explicitly; quote
  action lists; use numeric phases; 4-space indentation; no tabs.
- Every detection rule needs `msg`, `logdata`, the `application-`,
  `language-`, `platform-`, `attack-` and `paranoia-level/N` tags, `OWASP_CRS`
  and its `OWASP_CRS/<CATEGORY>` tag, a `capec/` tag, `ver`, `severity`, and the
  score `setvar`s for its own PL. Tags must exist in `crs-linter.toml`.
- Regexes must be RE2-compatible (Coraza is Go): no lookaround, backreferences,
  atomic groups or possessive quantifiers. Use `(?i)` rather than `t:lowercase`
  on `@rx` rules. Follow CONTRIBUTING.md on anchoring, capture groups and
  catastrophic backtracking.
- Before adding a pattern for a claimed false negative, check what already
  catches the payload. Rules overlap heavily; the test container runs at
  `BLOCKING_PARANOIA: 4`, so one request shows every rule that fires. Map each
  firing rule to its `paranoia-level` tag. If the payload is caught at the PL
  the report is about, say so and stop (for a blocking report, also check
  that the anomaly scores of PL1 through that PL, summed, reach the blocking
  threshold). If it is caught only at a higher PL, that is a paranoia-level
  policy question for the maintainers, not a bug to fix with a new PL1
  pattern.
- Do not pick rule IDs, paranoia levels or anomaly severities on your own.
  Propose them and let a maintainer confirm.
- Comments precede a chain, never sit between chained rules. Keep example
  lists in comments short (2-3 items).

### Regex assembly

Never hand-edit a compiled regex in `rules/*.conf` when a `.ra` source exists;
`pre-commit.ci` regenerates from the source and silently reverts the edit.

```bash
crs-toolchain regex compare 942140   # generated vs. rule file
crs-toolchain regex update 942140    # write generated regex into the rule file
crs-toolchain regex format --all     # format .ra files
```

In `.ra` files: `##!+ i` sets case-insensitivity (no inline `(?i)`); `{{name}}`
only expands `##!> define` variables; shared fragments come from
`regex-assembly/include/` via `##!> include`; never put multi-byte UTF-8
characters inside `[...]`; write `\s`, not `\s\x0b` (the toolchain expands it).

### Tests

- Every new rule or branch gets positive tests (attack detected) and negative
  tests (legitimate input not detected). Fill the `comment` field with the
  expected behaviour.
- Format is go-ftw v2. `POST` defaults to
  `application/x-www-form-urlencoded`; with that content type `data` must be
  URL-encoded (set `Content-Type` for XML or JSON bodies). `data`
  is a Go template: a literal `{{` breaks the test; use `encoded_data`.
  Quote string fields such as `version: "HTTP/1.1"`. Raw CR/LF in headers
  need `encoded_request`.
- A test ID is `<ruleid>-<n>`. After deleting tests run
  `crs-toolchain util renumber-tests <ruleid>`.
- `expect_ids` is satisfied by a PCRE limit-exceeded error line that carries
  the rule ID. Regression tests for ReDoS fixes must assert a real match of
  that rule, e.g. `match_regex: 'Warning\. (Pattern match|Matched).*\[id "942140"\]'`.
- Prove each test that demonstrates the change fails on the target branch
  without the change (`main`, or the LTS branch for a backport): a positive
  test for a new detection, or the negative test for a false-positive fix.
  Other negative tests pass on both and need no proof.

Run the stack and the tests the way CI does:

```bash
docker compose -f tests/docker-compose.yml up -d modsec2-apache   # or modsec3-nginx
# CI downloads the go-ftw release binary as `ftw`; use that name if you install it the same way.
go-ftw run -d tests/regression/tests/REQUEST-942-APPLICATION-ATTACK-SQLI -i "^942140-" \
  --log-file tests/logs/modsec2-apache/error.log \
  --overrides tests/regression/httpd-overrides.yaml   # nginx-overrides.yaml for nginx
```

Restart the container after switching branches; it keeps the rules it started
with. Coraza is not run in CI but can be tested with `coraza-caddy`.

### Lint

Run the same linter version and arguments as `.github/workflows/lint.yaml`:

```bash
CRS_LINTER_VERSION=$(grep -oE "CRS_LINTER_VERSION: '[0-9.]+'" .github/workflows/lint.yaml | grep -oE '[0-9.]+')
uvx --from "crs-linter==${CRS_LINTER_VERSION}" crs-linter --output=github \
  -r crs-setup.conf.example -r 'rules/*.conf' -c crs-linter.toml \
  -T tests/regression/tests/ -d "$(pwd)"
```

Lint the whole rule set, not one file; single-file runs report false
"TX variable not set" errors because the 901 rules define those variables.
`pre-commit run --all-files` covers YAML lint, whitespace and regex regeneration.

## Pull requests

- One problem per PR, based on `main` (or `lts/v4.25.x` for a backport).
- Title must be a Conventional Commit; `check-pr-title.yaml` rejects others.
  Include the rule ID when a single rule changes:
  `fix(942100): ...`, `feat(932380): ...`, `chore(tests): ...`, `docs: ...`.
- Body follows `.github/pull_request_template.md`: "Proposed changes" (what
  and why, link the issue with `Fixes #N`), the PR checklist, "Further
  comments" when the design needs explaining, and the **AI Disclosure**
  section. That section is mandatory under AI-CONTRIBUTIONS.md whenever an AI
  tool materially helped: name the tool and model, say what it generated or
  assisted with, and list the verification actually performed (tests run,
  payload corpora checked, ReDoS analysis). Vague entries are not accepted;
  PRs with undisclosed AI content may be closed.
- Do not add commit trailers, signatures or session links; do not credit
  yourself as co-author.
- Labels drive the generated release notes (`.github/release.yml`):
  `release:new-detection`, `release:new-feature`, `release:important`,
  `release:breaking`, `release:remove-rules`, `release:fix`,
  `release:refactor`, `release:ignore`. A merged PR that must reach the LTS
  line gets the label of the next point release, e.g. `backport:lts-4.25.3`;
  a core developer adds it, agents only propose it.
- Linking another PR as a dependency (`depends on #N` in the body) blocks
  merge until it lands (`check-pr-dependencies.yaml`).
- CodeRabbit reviews every PR automatically (`.coderabbit.yaml`). Address or
  answer each of its comments before requesting a human review; maintainers
  will not start reviewing while bot findings are unresolved. Push back on
  findings that are wrong (e.g. requests to restore `t:lowercase`), with a
  reply explaining why.

CI on every PR:

- `regression (modsec2-apache)` and `regression (modsec3-nginx)`: the go-ftw suite.
- `lint`: yamllint, SecLang parse, crs-linter, `.ra` formatting, every `.ra`
  compiling to the regex currently in `rules/`, and gap-free test numbering.
- `regression (eng, 2023, 10K, 1)`: the quantitative false-positive run
  against a natural-language corpus; results are posted as a PR comment. This
  is the FP gate for any widened pattern.
- `pre-commit.ci` may push an autofix commit to the branch.
- Issues and PRs are marked stale after 90 days without activity and closed
  90 days later.

## Backports to LTS

Cherry-pick each merged PR individually (`git cherry-pick -x`) onto a branch
from `lts/v4.25.x`, reference `cherry-pick of #NNNN` in the message, add the
`CHANGES.md` entry in the same PR, and label the backport PR
`backport:release-lts-4.25.x` and `release:ignore`. Regenerate conflicting
regexes from the merged `.ra` with `crs-toolchain regex update` instead of
merging the compiled strings by hand. Expect test-ID collisions at the end of
test files; keep the LTS-side tests first and renumber.

## Things agents get wrong here

- Inventing SecLang directives or actions. Check the ModSecurity v2 and v3
  reference manuals and Coraza docs; the three engines differ.
- Treating a `regexploit` or online checker label as proof of ReDoS. The real
  signal is PCRE2 exceeding its match limit; test with `pcre2test`. RE2
  engines are immune by construction.
- "Fixing" a ReDoS by adding a repeated group that keeps the old match set.
  PCRE2 backtrack points per group pass can exceed the match limit, which is a
  bypass.
- Adding a pattern for a payload without first checking which rules already
  catch it and at which paranoia level.
- Touching `rules/*.conf` regexes without the `.ra` source.
- Submitting tests whose payloads do not actually trigger the rule, or
  negative tests that are too simple to prove anything.
