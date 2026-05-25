---
name: validate-specs
description: Validate SSOT spec.md files for structure, REQ numbering, references, and type scoping (Code vs Infra). Run against the ai-tool-authpoint-spec repo.
---

# Validate SSOT Spec Files

Runs `validate_specs.py` — a deterministic validator for `spec.md` files — against the `ai-tool-authpoint-spec` repo.

Checks performed on every `ssot/**/domain/**/specs/**/spec.md`:

- **Title & metadata** — `# Title` present, followed by blockquote with `Spec ID`, `Type`, `AWS Services`
- **REQ numbering** — requirements are sequential starting at `REQ-1` with no gaps
- **References section** — every bullet contains a valid MCP tool call; relative paths resolve to real files (unless marked `expected`)
- **Type scoping** — Code specs don't mention infra tokens; Infra specs don't express business logic
- **Scenario bullets** — GIVEN/WHEN/THEN bullets must not contain MUST/MUST NOT

## Usage

```
/validate-specs                          # scan entire repo (uses AUTHPOINT_SPEC_REPO env var or prompts)
/validate-specs --root <path>            # scan specific repo root
/validate-specs --files <path/spec.md>   # validate one or more specific files
/validate-specs --json                   # output results as JSON
```

## Requirements

- Python 3.11+
- The `ai-tool-authpoint-spec` repo cloned locally
- `AUTHPOINT_SPEC_REPO` environment variable set to its path (or pass `--root` explicitly)

## Commands

```bash
# Determine repo root
SPEC_REPO="${AUTHPOINT_SPEC_REPO:-}"

if [ -z "$SPEC_REPO" ]; then
  echo "❌ AUTHPOINT_SPEC_REPO is not set."
  echo "   Set it to the path of your ai-tool-authpoint-spec clone, e.g.:"
  echo "   export AUTHPOINT_SPEC_REPO=~/Projects/ai-tool-authpoint-spec"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VALIDATOR="$SCRIPT_DIR/scripts/validate_specs.py"

echo "================================================"
echo "Validating SSOT spec files..."
echo "Root: $SPEC_REPO"
echo "================================================"
echo ""

python "$VALIDATOR" --root "$SPEC_REPO" "$@"

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
  echo "================================================"
  echo "✅ All specs passed validation."
  echo "================================================"
elif [ $EXIT_CODE -eq 2 ]; then
  echo "================================================"
  echo "⚠️  No spec.md files found under $SPEC_REPO"
  echo "   Check that AUTHPOINT_SPEC_REPO points to the correct repo."
  echo "================================================"
else
  echo "================================================"
  echo "❌ Validation failed. Fix the errors above before merging."
  echo "================================================"
fi

exit $EXIT_CODE
```

## PowerShell Version (Windows)

```powershell
# Determine repo root
$specRepo = $env:AUTHPOINT_SPEC_REPO

if (-not $specRepo) {
    Write-Host "❌ AUTHPOINT_SPEC_REPO is not set." -ForegroundColor Red
    Write-Host "   Set it to the path of your ai-tool-authpoint-spec clone, e.g.:" -ForegroundColor Yellow
    Write-Host "   `$env:AUTHPOINT_SPEC_REPO = 'C:\Projects\ai-tool-authpoint-spec'" -ForegroundColor Yellow
    exit 1
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$validator = Join-Path $scriptDir "scripts\validate_specs.py"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Validating SSOT spec files..." -ForegroundColor Cyan
Write-Host "Root: $specRepo" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

python $validator --root $specRepo $args

$exitCode = $LASTEXITCODE

Write-Host ""
if ($exitCode -eq 0) {
    Write-Host "================================================" -ForegroundColor Green
    Write-Host "✅ All specs passed validation." -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Green
} elseif ($exitCode -eq 2) {
    Write-Host "================================================" -ForegroundColor Yellow
    Write-Host "⚠️  No spec.md files found under $specRepo" -ForegroundColor Yellow
    Write-Host "   Check that AUTHPOINT_SPEC_REPO points to the correct repo." -ForegroundColor Yellow
    Write-Host "================================================" -ForegroundColor Yellow
} else {
    Write-Host "================================================" -ForegroundColor Red
    Write-Host "❌ Validation failed. Fix the errors above before merging." -ForegroundColor Red
    Write-Host "================================================" -ForegroundColor Red
}

exit $exitCode
```

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | All specs passed |
| `1` | One or more validation errors found |
| `2` | No `spec.md` files found to validate |

## Examples

### Validate entire spec repo

```bash
/validate-specs
```

### Validate a single spec file

```bash
/validate-specs --files ssot/folklore/domain/oidc/specs/aaas-30040-saml-user-cache-consumer/spec.md
```

### JSON output (for CI integration)

```bash
/validate-specs --json
```
