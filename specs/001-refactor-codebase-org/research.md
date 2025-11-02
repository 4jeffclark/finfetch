# Research: Codebase Organization Refactoring

**Feature**: Codebase Organization Refactoring  
**Date**: 2025-01-27  
**Purpose**: Resolve technical unknowns and establish best practices for Python package reorganization

## Research Tasks

### Task 1: Python Package Structure Best Practices

**Decision**: Use `src/` layout with build configuration files at project root

**Rationale**: 
- Python packaging standards (PEP 517, PEP 518) recommend build configuration files (`pyproject.toml`, `setup.py`) at project root
- `src/` layout prevents accidental imports of development code and enforces proper package installation
- This structure is widely adopted in the Python ecosystem and aligns with setuptools documentation

**Alternatives Considered**:
- Flat layout (package in root): Rejected - violates packaging best practices and can cause import issues
- Namespace packages: Not applicable - single package name `finfetch`

**References**:
- PEP 517: Build System Independence
- PEP 518: Specifying Build Dependencies for Python Projects
- setuptools documentation: src-layout

### Task 2: CLI File Consolidation Strategy

**Decision**: Consolidate `cli.py` and `cli_simple.py` by keeping `cli.py` as the primary CLI and removing `cli_simple.py`

**Rationale**:
- `cli.py` is the more complete implementation with debug levels, proper logging, and full feature set
- `cli_simple.py` appears to be a baseline/legacy implementation with minimal functionality
- Single CLI entry point reduces maintenance burden and eliminates confusion
- Entry point in `pyproject.toml` already references `finfetch.cli:main`

**Alternatives Considered**:
- Keep both CLIs: Rejected - violates requirement for single unified CLI (FR-003)
- Create new consolidated CLI: Rejected - unnecessary complexity when `cli.py` is already complete

**Implementation Notes**:
- Entry point `finfetch.cli:main` must remain unchanged
- All functionality from `cli_simple.py` must be verified as present in `cli.py` before removal
- Update any references to `cli_simple` in documentation or scripts

### Task 3: Legacy File Handling (`rars.py`)

**Decision**: Move `rars.py` to `test/dev/20251024Baseline/helper-scripts/` if it contains useful development utilities, or remove if it's obsolete

**Rationale**:
- `rars.py` is a development script (contains hardcoded API keys, development/test code)
- Should not exist in production code paths (`src/finfetch/` or `src/`)
- If preserved, belongs in development/test directories
- Script contains Polygon API test code that may be useful for reference

**Alternatives Considered**:
- Keep in `src/`: Rejected - violates requirement to remove from production code paths (FR-004)
- Delete entirely: Considered but risky if script contains useful patterns or test utilities
- Move to test helpers: Selected - preserves utility while removing from production paths

**Implementation Notes**:
- Review `rars.py` for any imports or dependencies that may break when moved
- Update any scripts that reference `rars.py` if needed

### Task 4: Build Configuration File Migration

**Decision**: Move `pyproject.toml` and `setup.py` from `src/` to project root, updating paths as needed

**Rationale**:
- Build configuration files belong at project root per Python packaging standards
- Both files contain correct package directory configurations (`where = ["src"]`, `package_dir={"": "src"}`)
- Path references in these files are already correct and will continue to work after move
- No code changes needed - only file relocation

**Alternatives Considered**:
- Keep in `src/`: Rejected - violates Python packaging best practices and FR-001
- Consolidate to only `pyproject.toml`: Considered but `setup.py` may be needed for backward compatibility

**Implementation Notes**:
- Update `pyproject.toml` path references if any (currently references `README.md` which should remain accessible)
- Verify `setup.py` package discovery paths remain correct
- Test `pip install -e .` after relocation

### Task 5: Import Path and Entry Point Preservation

**Decision**: Maintain all existing import paths and entry points without modification

**Rationale**:
- Package structure (`src/finfetch/`) remains unchanged
- Import statements (`from finfetch import ...`) continue to work
- Entry points (`finfetch.cli:main`) continue to work
- Only file relocation - no code structure changes

**Alternatives Considered**:
- Restructure package: Rejected - would break imports and violate "no functionality changes" requirement

**Implementation Notes**:
- Verify imports after reorganization
- Test package installation
- Test CLI entry point execution
- Run all existing tests to ensure no breakage

## Summary of Decisions

1. **Package Structure**: Maintain `src/` layout, move build files to root ✅
2. **CLI Consolidation**: Keep `cli.py`, remove `cli_simple.py` ✅
3. **Legacy Files**: Move `rars.py` to test helpers or remove ✅
4. **Build Configuration**: Move `pyproject.toml` and `setup.py` to root ✅
5. **Imports/Entry Points**: Preserve all existing paths ✅

**Status**: All research complete - ready for Phase 1 design

