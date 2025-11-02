# Quick Start: Codebase Organization Refactoring

**Feature**: Codebase Organization Refactoring  
**Date**: 2025-01-27  

## Overview

This quickstart guide outlines the codebase reorganization changes and how to verify the reorganization is complete and functional.

## What Changed

### File Relocations

1. **Build Configuration Files** → Moved to project root
   - `src/pyproject.toml` → `./pyproject.toml`
   - `src/setup.py` → `./setup.py`

2. **CLI Consolidation** → Single unified CLI
   - `src/cli.py` → `src/finfetch/cli.py` (kept)
   - `src/cli_simple.py` → *(removed)*

3. **Legacy Files** → Removed from production paths
   - `src/rars.py` → `test/dev/20251024Baseline/helper-scripts/rars.py` (moved) or *(removed)*

## Verification Steps

### Step 1: Verify Build Configuration Location

```bash
# Check that build files are in project root
ls pyproject.toml setup.py
```

**Expected**: Both files exist in project root

### Step 2: Verify Package Installation

```bash
# Install package from project root
pip install -e .

# Verify installation
pip show finfetch
```

**Expected**: Package installs successfully, shows package metadata

### Step 3: Verify CLI Entry Point

```bash
# Test CLI command
finfetch --help

# Test specific command
finfetch config --show
```

**Expected**: CLI displays help and commands execute successfully

### Step 4: Verify Package Imports

```python
# Test package imports
python -c "from finfetch import FinFetch; print('Import successful')"
```

**Expected**: Import succeeds without errors

### Step 5: Verify Test Execution

```bash
# Run existing tests
pytest test/

# Run baseline test runner
test/dev/20251024Baseline/00-finfetch-baseline-test.bat
```

**Expected**: All tests pass, test runners execute successfully

### Step 6: Verify File Structure

```bash
# Check that only one CLI exists
ls src/finfetch/cli*.py

# Check that legacy files are removed from src/
ls src/*.py | grep -v __init__
```

**Expected**: Only `cli.py` exists in `src/finfetch/`, no legacy files in `src/`

## Rollback Procedure

If reorganization causes issues:

1. **Revert file moves**:
   ```bash
   git checkout HEAD -- src/pyproject.toml src/setup.py
   git mv pyproject.toml src/
   git mv setup.py src/
   ```

2. **Restore CLI files**:
   ```bash
   git checkout HEAD -- src/cli_simple.py
   ```

3. **Restore legacy files**:
   ```bash
   git checkout HEAD -- src/rars.py
   ```

4. **Verify rollback**:
   ```bash
   pip install -e .
   finfetch --help
   ```

## Success Criteria Verification

| Criteria | Verification Method |
|----------|-------------------|
| SC-001: Package installs | `pip install -e .` succeeds |
| SC-002: CLI works | `finfetch --help` displays commands |
| SC-003: Tests pass | `pytest` reports 100% pass rate |
| SC-004: Test runners work | Baseline test runner executes successfully |
| SC-005: Build files in root | File system inspection confirms location |
| SC-006: Single CLI file | File system inspection confirms only `cli.py` |
| SC-007: No legacy files in src/ | File system inspection confirms `rars.py` removed |
| SC-008: Imports work | Python import test succeeds |
| SC-009: Code quality tools work | `mypy`, `black`, `flake8` execute from root |
| SC-010: Package metadata preserved | Compare version, dependencies before/after |

## Troubleshooting

### Issue: Package installation fails

**Check**: Verify `pyproject.toml` paths are correct:
```toml
[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-dir]
"" = "src"
```

### Issue: CLI command not found

**Check**: Verify entry point in `pyproject.toml`:
```toml
[project.scripts]
finfetch = "finfetch.cli:main"
```

### Issue: Import errors after reorganization

**Check**: Verify package structure:
```bash
python -c "import sys; print(sys.path)"
pip show -f finfetch
```

## Next Steps

After successful reorganization:

1. ✅ Verify all success criteria (SC-001 through SC-010)
2. ✅ Update any documentation referencing old file locations
3. ✅ Commit changes to feature branch
4. ✅ Proceed with `/speckit.tasks` to create implementation tasks

