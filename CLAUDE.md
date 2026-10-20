# CLAUDE.md

## Commands

- Rule syntax: `secrules-parser -c --output-type github -f rules/*.conf`
- Rule lint: `crs-linter --output=github -r crs-setup.conf.example -r 'rules/*.conf' -c crs-linter.toml -T 'tests/regression/tests/' -d "$(pwd)"`
- Rules built from `regex-assembly/`: regenerate with `crs-toolchain regex update --all`, format with `crs-toolchain regex format --all`.
- Assembly checks: `crs-toolchain regex format -aco github`, `crs-toolchain regex compare -ao github`, `crs-toolchain util renumber-tests -cao github`
- Regression tests: start `modsec2-apache` (or `modsec3-nginx`) from `tests/docker-compose.yml`, then `ftw check -d tests/regression/tests` and `ftw run -d tests/regression/tests --overrides tests/regression/httpd-overrides.yaml` (`nginx-overrides.yaml` for nginx).
- YAML lint: `yamllint -c .yamllint.yml tests/regression/tests`
