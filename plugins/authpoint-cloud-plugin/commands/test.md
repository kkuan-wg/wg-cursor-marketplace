---
name: test
description: Run pytest with coverage and flake8 with flexible scope (changed files, all files, or specific directory, anything)
---

# Run Python Tests with Coverage

Execute pytest tests with coverage report and flake8 validation with flexible scope control.

## Usage

```bash
/test              # Analyze only changed files (default)
/test all          # Analyze all files in the project
/test <directory>  # Analyze specific directory (e.g., /test api, /test domain)
```

## What This Does

1. ✅ Runs pytest with coverage (generates `results.xml` and coverage report)
2. ✅ Runs flake8 validation with **120 character line limit** (generates `pep8.out`)
3. ✅ Shows uncovered lines based on scope:
   - **No parameter**: Only changed files (git diff)
   - **all**: All files in the project
   - **<directory>**: Specific directory (e.g., `api`, `domain`, `adapter`)
4. ✅ Generates detailed coverage report

## Configuration

- **Line length limit:** 120 characters (not 80)
- **Coverage target:** 90%+ lines, 85%+ branches
- **Test framework:** pytest
- **Linter:** flake8
- **Cache behavior:** Always clears cache (`--cache-clear`) to force fresh test runs

## Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| *(none)* | Analyze only changed files | `/test` |
| `all` | Analyze all files | `/test all` |
| `<directory>` | Analyze specific directory | `/test api` |
| `<directory>` | Multiple levels | `/test src/domain` |

## Requirements

- Must be in a project with `/application` directory
- Must have pytest, pytest-cov, and flake8 installed
- Git repository (to detect changed files, only for default mode)

## Commands

```bash
# Parse parameters
SCOPE="${1:-changed}"  # Default: changed files
TEST_DIR="${2:-}"      # Optional: specific test directory

# Navigate to application directory
cd application

echo "================================================"
echo "🧪 Running Tests with Coverage..."
echo "================================================"

# Determine test scope
if [ "$SCOPE" = "all" ]; then
    echo "📊 Scope: ALL FILES"
    TEST_PATH="tests/"
elif [ -n "$SCOPE" ] && [ "$SCOPE" != "changed" ]; then
    echo "📊 Scope: DIRECTORY '$SCOPE'"
    TEST_PATH="tests/$SCOPE"
    if [ ! -d "$TEST_PATH" ]; then
        echo "❌ Directory 'tests/$SCOPE' not found!"
        exit 1
    fi
else
    echo "📊 Scope: CHANGED FILES ONLY"
    TEST_PATH="tests/"
fi

echo ""

# Run pytest with coverage (clear cache to force re-run)
if [ "$SCOPE" = "all" ] || [ "$SCOPE" != "changed" ]; then
    # Run all tests or specific directory
    python -m pytest "$TEST_PATH" --cache-clear --cov-report xml --cov-report term --junitxml results.xml
else
    # Run all tests but report only changed files
    python -m pytest --cache-clear --cov-report xml --cov-report term --junitxml results.xml
fi

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Tests failed!"
    exit 1
fi

echo ""
echo "================================================"
echo "📋 Running Flake8 (PEP 8 Validation)..."
echo "================================================"
echo ""

# Run flake8 with 120 character line limit (clear cache to force re-run)
if [ "$SCOPE" = "all" ] || [ "$SCOPE" != "changed" ]; then
    python -m pytest "$TEST_PATH" --cache-clear --flake8 --flake8-max-line-length=120 --junitxml pep8.out
else
    python -m pytest --cache-clear --flake8 --flake8-max-line-length=120 --junitxml pep8.out
fi

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Flake8 validation failed!"
    exit 1
fi

echo ""
echo "================================================"
echo "📊 Coverage Report"
echo "================================================"
echo ""

# Generate coverage report based on scope
if [ "$SCOPE" = "all" ]; then
    echo "Coverage for ALL files:"
    python -m coverage report --show-missing
    
    echo ""
    echo "📝 Files with less than 100% coverage:"
    python -m coverage report --show-missing | grep -v "100%" | grep -v "TOTAL" | grep -v "^-" | grep -v "^Name"
    
elif [ "$SCOPE" != "changed" ]; then
    echo "Coverage for directory '$SCOPE':"
    python -m coverage report --show-missing --include="src/$SCOPE/*"
    
    echo ""
    echo "📝 Files with less than 100% coverage in '$SCOPE':"
    python -m coverage report --show-missing --include="src/$SCOPE/*" | grep -v "100%" | grep -v "TOTAL" | grep -v "^-" | grep -v "^Name"
    
else
    # Get list of changed Python files (excluding tests)
    CHANGED_FILES=$(git diff --name-only HEAD | grep "\.py$" | grep -v "test" | grep -v "__pycache__")
    
    if [ -z "$CHANGED_FILES" ]; then
        echo "ℹ️  No Python files changed (excluding tests)"
        echo ""
        echo "💡 Tip: Use '/test all' to see coverage for all files"
    else
        echo "Changed files:"
        echo "$CHANGED_FILES" | sed 's/^/  📄 /'
        echo ""
        
        # Generate coverage report for changed files
        python -m coverage report --show-missing $(echo $CHANGED_FILES | tr '\n' ' ')
        
        echo ""
        echo "📝 Lines missing coverage in changed files:"
        MISSING=$(python -m coverage report --show-missing $(echo $CHANGED_FILES | tr '\n' ' ') | grep -v "100%" | grep -v "TOTAL" | grep -v "^-" | grep -v "^Name")
        
        if [ -z "$MISSING" ]; then
            echo "  ✅ All changed files have 100% coverage!"
        else
            echo "$MISSING" | sed 's/^/  /'
        fi
    fi
fi

echo ""
echo "================================================"
echo "✅ All Tests Passed!"
echo "================================================"
echo ""
echo "📄 Reports generated:"
echo "  ✓ results.xml (test results)"
echo "  ✓ pep8.out (flake8 validation)"
echo "  ✓ coverage.xml (coverage report)"
echo ""
echo "💡 Tips:"
echo "  - Run 'python -m coverage html' for detailed HTML report"
echo "  - Use '/test all' to analyze all files"
echo "  - Use '/test <directory>' to analyze specific directory"
```

## Examples

### Example 1: Default (Changed Files Only)

```bash
/test
```

**Output:**
```
🧪 Running Tests with Coverage...
📊 Scope: CHANGED FILES ONLY

============================= test session starts ==============================
collected 150 items
tests/test_service.py ..................                                  [ 12%]
======================== 150 passed in 5.23s ===============================

📋 Running Flake8 (PEP 8 Validation)...
======================== 50 passed in 2.15s ================================

📊 Coverage Report
Changed files:
  📄 src/domain/service.py
  📄 src/adapter/db_repository.py

Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
src/domain/service.py                45      5    89%   23-27, 45
src/adapter/db_repository.py         32      2    94%   67-68

📝 Lines missing coverage in changed files:
  src/domain/service.py                45      5    89%   23-27, 45
  src/adapter/db_repository.py         32      2    94%   67-68

✅ All Tests Passed!
```

### Example 2: All Files

```bash
/test all
```

**Output:**
```
🧪 Running Tests with Coverage...
📊 Scope: ALL FILES

============================= test session starts ==============================
collected 150 items
tests/ ..........................................                         [100%]
======================== 150 passed in 5.23s ===============================

📊 Coverage Report
Coverage for ALL files:

Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
src/domain/service.py                45      5    89%   23-27, 45
src/adapter/db_repository.py         32      2    94%   67-68
src/adapter/api_invoker.py           28      0   100%
src/port/repository.py               15      0   100%
---------------------------------------------------------------
TOTAL                               120      7    94%

📝 Files with less than 100% coverage:
  src/domain/service.py                45      5    89%   23-27, 45
  src/adapter/db_repository.py         32      2    94%   67-68

✅ All Tests Passed!
```

### Example 3: Specific Directory

```bash
/test api
```

**Output:**
```
🧪 Running Tests with Coverage...
📊 Scope: DIRECTORY 'api'

============================= test session starts ==============================
collected 45 items
tests/api/ ..........................................                     [100%]
======================== 45 passed in 2.15s ================================

📊 Coverage Report
Coverage for directory 'api':

Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
src/api/handler.py                   23      3    87%   45-47
src/api/validator.py                 18      0   100%
---------------------------------------------------------------
TOTAL                                41      3    93%

📝 Files with less than 100% coverage in 'api':
  src/api/handler.py                   23      3    87%   45-47

✅ All Tests Passed!
```

### Example 4: Nested Directory

```bash
/test src/domain
```

**Output:**
```
🧪 Running Tests with Coverage...
📊 Scope: DIRECTORY 'src/domain'

============================= test session starts ==============================
collected 30 items
tests/src/domain/ ............................                           [100%]
======================== 30 passed in 1.85s ================================

📊 Coverage Report
Coverage for directory 'src/domain':

Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
src/domain/service.py                45      5    89%   23-27, 45
src/domain/validator.py              20      0   100%
---------------------------------------------------------------
TOTAL                                65      5    92%

✅ All Tests Passed!
```

## PowerShell Version (Windows)

If bash doesn't work, use PowerShell:

```powershell
param(
    [string]$Scope = "changed",
    [string]$TestDir = ""
)

# Navigate to application directory
cd application

$cyan = "Cyan"
$green = "Green"
$red = "Red"
$yellow = "Yellow"

Write-Host "================================================" -ForegroundColor $cyan
Write-Host "🧪 Running Tests with Coverage..." -ForegroundColor $cyan
Write-Host "================================================" -ForegroundColor $cyan

# Determine test scope
if ($Scope -eq "all") {
    Write-Host "📊 Scope: ALL FILES" -ForegroundColor $cyan
    $testPath = "tests/"
} elseif ($Scope -ne "changed") {
    Write-Host "📊 Scope: DIRECTORY '$Scope'" -ForegroundColor $cyan
    $testPath = "tests/$Scope"
    if (-not (Test-Path $testPath)) {
        Write-Host "❌ Directory 'tests/$Scope' not found!" -ForegroundColor $red
        exit 1
    }
} else {
    Write-Host "📊 Scope: CHANGED FILES ONLY" -ForegroundColor $cyan
    $testPath = "tests/"
}

Write-Host ""

# Run pytest with coverage (clear cache to force re-run)
if ($Scope -eq "all" -or $Scope -ne "changed") {
    python -m pytest $testPath --cache-clear --cov-report xml --cov-report term --junitxml results.xml
} else {
    python -m pytest --cache-clear --cov-report xml --cov-report term --junitxml results.xml
}

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Tests failed!" -ForegroundColor $red
    exit 1
}

Write-Host ""
Write-Host "================================================" -ForegroundColor $cyan
Write-Host "📋 Running Flake8 (PEP 8 Validation)..." -ForegroundColor $cyan
Write-Host "================================================" -ForegroundColor $cyan
Write-Host ""

# Run flake8 with 120 character line limit (clear cache to force re-run)
if ($Scope -eq "all" -or $Scope -ne "changed") {
    python -m pytest $testPath --cache-clear --flake8 --flake8-max-line-length=120 --junitxml pep8.out
} else {
    python -m pytest --cache-clear --flake8 --flake8-max-line-length=120 --junitxml pep8.out
}

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Flake8 validation failed!" -ForegroundColor $red
    exit 1
}

Write-Host ""
Write-Host "================================================" -ForegroundColor $cyan
Write-Host "📊 Coverage Report" -ForegroundColor $cyan
Write-Host "================================================" -ForegroundColor $cyan
Write-Host ""

# Generate coverage report based on scope
if ($Scope -eq "all") {
    Write-Host "Coverage for ALL files:" -ForegroundColor $cyan
    python -m coverage report --show-missing
    
    Write-Host ""
    Write-Host "📝 Files with less than 100% coverage:" -ForegroundColor $yellow
    $allCoverage = python -m coverage report --show-missing | Out-String
    $lessThan100 = $allCoverage -split "`n" | Where-Object { 
        $_ -notmatch "100%" -and 
        $_ -notmatch "TOTAL" -and 
        $_ -notmatch "^-" -and 
        $_ -notmatch "^Name" -and
        $_.Trim() -ne ""
    }
    
    if ($lessThan100.Count -eq 0) {
        Write-Host "  ✅ All files have 100% coverage!" -ForegroundColor $green
    } else {
        $lessThan100 | ForEach-Object { Write-Host "  $_" }
    }
    
} elseif ($Scope -ne "changed") {
    Write-Host "Coverage for directory '$Scope':" -ForegroundColor $cyan
    python -m coverage report --show-missing --include="src/$Scope/*"
    
    Write-Host ""
    Write-Host "📝 Files with less than 100% coverage in '$Scope':" -ForegroundColor $yellow
    $dirCoverage = python -m coverage report --show-missing --include="src/$Scope/*" | Out-String
    $lessThan100 = $dirCoverage -split "`n" | Where-Object { 
        $_ -notmatch "100%" -and 
        $_ -notmatch "TOTAL" -and 
        $_ -notmatch "^-" -and 
        $_ -notmatch "^Name" -and
        $_.Trim() -ne ""
    }
    
    if ($lessThan100.Count -eq 0) {
        Write-Host "  ✅ All files in '$Scope' have 100% coverage!" -ForegroundColor $green
    } else {
        $lessThan100 | ForEach-Object { Write-Host "  $_" }
    }
    
} else {
    # Get list of changed Python files (excluding tests)
    $changedFiles = git diff --name-only HEAD 2>$null | Where-Object { 
        $_ -match "\.py$" -and 
        $_ -notmatch "test" -and 
        $_ -notmatch "__pycache__"
    }
    
    if ($null -eq $changedFiles -or $changedFiles.Count -eq 0) {
        Write-Host "ℹ️  No Python files changed (excluding tests)" -ForegroundColor $yellow
        Write-Host ""
        Write-Host "💡 Tip: Use '/test all' to see coverage for all files" -ForegroundColor $cyan
    } else {
        Write-Host "Changed files:" -ForegroundColor $cyan
        $changedFiles | ForEach-Object { Write-Host "  📄 $_" }
        Write-Host ""
        
        # Generate coverage report for changed files
        $filesArray = $changedFiles | ForEach-Object { $_ }
        python -m coverage report --show-missing @filesArray
        
        Write-Host ""
        Write-Host "📝 Lines missing coverage in changed files:" -ForegroundColor $yellow
        $coverageOutput = python -m coverage report --show-missing @filesArray | Out-String
        $missingLines = $coverageOutput -split "`n" | Where-Object { 
            $_ -notmatch "100%" -and 
            $_ -notmatch "TOTAL" -and 
            $_ -notmatch "^-" -and
            $_ -notmatch "^Name" -and
            $_.Trim() -ne ""
        }
        
        if ($missingLines.Count -eq 0) {
            Write-Host "  ✅ All changed files have 100% coverage!" -ForegroundColor $green
        } else {
            $missingLines | ForEach-Object { Write-Host "  $_" }
        }
    }
}

Write-Host ""
Write-Host "================================================" -ForegroundColor $green
Write-Host "✅ All Tests Passed!" -ForegroundColor $green
Write-Host "================================================" -ForegroundColor $green
Write-Host ""
Write-Host "📄 Reports generated:" -ForegroundColor $cyan
Write-Host "  ✓ results.xml (test results)"
Write-Host "  ✓ pep8.out (flake8 validation)"
Write-Host "  ✓ coverage.xml (coverage report)"
Write-Host ""
Write-Host "💡 Tips:" -ForegroundColor $cyan
Write-Host "  - Run 'python -m coverage html' for detailed HTML report"
Write-Host "  - Use '/test all' to analyze all files"
Write-Host "  - Use '/test <directory>' to analyze specific directory"
```

## Troubleshooting

### Error: "No module named pytest"

```bash
# Install dependencies
pip install pytest pytest-cov pytest-flake8 flake8
```

### Error: "Not a git repository"

```bash
# Initialize git if needed
git init
git add .
git commit -m "Initial commit"
```

### Error: "application directory not found"

```bash
# Make sure you're in the project root
ls application/  # Should show tests/ and src/
```

### Tests Not Re-running (Using Cached Results)

**Problem:** Pytest uses cache and shows "passed" without actually running tests.

**Solution:** The command now uses `--cache-clear` automatically to force fresh runs every time.

**Manual clear:**
```bash
# Clear pytest cache manually
cd application
rm -rf .pytest_cache/

# Or use pytest directly
python -m pytest --cache-clear
```

**Why this happens:**
- Pytest caches test results for speed
- If code hasn't changed, it reuses previous results
- `--cache-clear` forces pytest to ignore cache and run everything fresh

## Tips

### Generate HTML Coverage Report

```bash
# After running /test
cd application
python -m coverage html
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
```

### Run Tests for Specific File

```bash
cd application
python -m pytest tests/test_service.py -v
```

### Check Coverage for Specific Module

```bash
cd application
python -m coverage report --include="src/domain/*"
```

## Integration with CI/CD

This command generates the same outputs as CI/CD:
- `results.xml` → JUnit test results
- `pep8.out` → Flake8 validation results
- `coverage.xml` → Coverage report

Use these files in Jenkins/GitHub Actions/GitLab CI.
