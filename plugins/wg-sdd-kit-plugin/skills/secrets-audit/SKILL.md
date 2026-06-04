---
name: secrets-audit
description: >-
  Scan for hardcoded secrets (gitleaks/trufflehog) plus AI review of config files.
  Stack-agnostic paths. PR gate and periodic sweep. Never commit secret values in output.
---

# secrets-audit

Find **hardcoded secrets, credentials, and sensitive config** in the working tree and git history. Complements Snyk/CI; does not replace vault/Secrets Manager discipline.

**Invoke:** `@wg-sdd-kit-plugin/skills/secrets-audit/SKILL.md`

---

## When to run

- Before **every PR merge** (incremental scan).
- **Monthly** full-history sweep.
- With team PR checklist / security gate.

---

## Tooling

### gitleaks

```bash
gitleaks detect --source . --report-format json --report-path gitleaks-report.json
gitleaks detect --source . --log-opts="HEAD~100..HEAD" --report-format json --report-path gitleaks-history-report.json
```

### trufflehog

```bash
trufflehog git file://. --json > trufflehog-report.json
trufflehog git file://. --since-commit=<base-sha> --json > trufflehog-incremental.json
```

Install via `winget install gitleaks`, `brew install gitleaks`, or project docs.

---

## AI-assisted config review

After automated scans, manually review likely secret carriers **for this repo's stack**:

| Area | Examples |
| --- | --- |
| Env files | `.env`, `.env.*`, `local.settings.json` |
| Python | `settings.py`, `pyproject.toml`, Pydantic `BaseSettings` defaults |
| .NET | `appsettings*.json`, `launchSettings.json`, user secrets |
| Node/Angular | `environment*.ts`, `proxy.conf.json`, `.npmrc` auth |
| JVM | `application*.yml`, `bootstrap.properties` |
| CI/CD | GitHub Actions, Jenkins credentials blocks, Helm values |
| Infra | Terraform vars, K8s Secrets manifests (names only in docs) |

Flag: API keys, passwords, private keys, connection strings with credentials, OAuth client secrets, webhook signing keys.

**Never** paste live secret values into chat or markdown output — report **file:line** and **type** only.

---

## Output format

```markdown
## Secrets audit — {date / PR}

| Severity | Type | Location | Action |
| --- | --- | --- | --- |
| BLOCKER | AWS access key | path:line | Rotate + remove from history |
| SUGGESTION | Test password in fixture | path:line | Move to env / secret store |

### Tools run
- gitleaks: PASS / N findings
- trufflehog: ...
```

---

## Remediation guidance

- Rotate exposed credentials immediately.
- Move to **AWS Secrets Manager**, **Vault**, or team standard; load via env/SSM at runtime.
- Add/prevent with **gitleaks** in CI and `.gitignore` for local `.env`.
- History leaks: follow org policy (BFG, git filter-repo, credential revocation).

---

## After running

Resolve BLOCKERs before merge. Document accepted test doubles in threat model or team wiki if they are intentional non-production values.
