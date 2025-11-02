# Data Model: Codebase Organization Refactoring

**Feature**: Codebase Organization Refactoring  
**Date**: 2025-01-27  

**Note**: This feature is an organizational refactoring with no data model changes. The structure below documents the file system organization changes.

## File System Structure

### Entities

#### BuildConfiguration
- **Location**: Project root (after reorganization)
- **Attributes**:
  - `pyproject.toml`: Package metadata, dependencies, build configuration
  - `setup.py`: Setuptools setup script (backward compatibility)
- **Relationships**: Referenced by package build tools, defines package structure

#### PackageStructure
- **Location**: `src/finfetch/` (unchanged)
- **Attributes**:
  - Package modules: `core/`, `sources/`, `processors/`, `analysis/`, `utils/`, `config/`
  - CLI entry point: `cli.py` (consolidated)
- **Relationships**: Contains all package code, imported by users

#### LegacyFiles
- **Location**: `test/dev/20251024Baseline/helper-scripts/` or removed
- **Attributes**:
  - `rars.py`: Development/test script (moved from `src/`)
- **Relationships**: Not part of package, development utilities only

## File Location Changes

### Files to Move

| Source | Destination | Reason |
|--------|-------------|--------|
| `src/pyproject.toml` | `./pyproject.toml` | Build configuration belongs at root (FR-001) |
| `src/setup.py` | `./setup.py` | Build configuration belongs at root (FR-001) |
| `src/rars.py` | `test/dev/20251024Baseline/helper-scripts/rars.py` | Legacy file removal from production (FR-004) |

### Files to Consolidate

| Source | Destination | Action |
|--------|-------------|--------|
| `src/cli.py` | `src/finfetch/cli.py` | Keep as primary CLI (FR-003) |
| `src/cli_simple.py` | *(removed)* | Consolidate into `cli.py` (FR-003) |

### Files to Remove

| File | Reason |
|------|--------|
| `src/cli_simple.py` | Duplicate CLI - consolidated into `cli.py` (FR-003) |
| `src/rars.py` | Legacy development script (FR-004) - moved or removed |

## Validation Rules

- **FR-001**: Build configuration files MUST exist in project root
- **FR-002**: Package structure MUST maintain `src/` layout
- **FR-003**: Only one CLI file MUST exist in package (`src/finfetch/cli.py`)
- **FR-004**: No legacy files (`rars.py`) in production code paths
- **FR-005**: All imports continue to work (`from finfetch import ...`)
- **FR-006**: CLI entry point continues to work (`finfetch --help`)

## State Transitions

### Before Reorganization
```
Project Root/
├── src/
│   ├── pyproject.toml      # ❌ Wrong location
│   ├── setup.py            # ❌ Wrong location
│   ├── cli.py              # ⚠️ Duplicate
│   ├── cli_simple.py       # ⚠️ Duplicate
│   ├── rars.py             # ❌ Legacy file
│   └── finfetch/           # ✅ Correct location
```

### After Reorganization
```
Project Root/
├── pyproject.toml          # ✅ Correct location
├── setup.py                # ✅ Correct location
└── src/
    └── finfetch/
        └── cli.py          # ✅ Single unified CLI
```

