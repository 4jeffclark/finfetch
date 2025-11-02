# Implementation Plan: Codebase Organization Refactoring

**Branch**: `001-refactor-codebase-org` | **Date**: 2025-01-27 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/001-refactor-codebase-org/spec.md`

**Note**: This plan focuses on structural reorganization without feature changes. This is an organizational refactoring to align with Python packaging best practices.

## Summary

Reorganize FinFetch codebase structure to follow Python packaging best practices and speckit conventions. Move build configuration files (`pyproject.toml`, `setup.py`) from `src/` to project root, consolidate duplicate CLI files (`cli.py` and `cli_simple.py`), remove or relocate legacy files (`rars.py`), and ensure proper Python package structure. All existing functionality must remain intact - this is purely structural improvement.

## Technical Context

**Language/Version**: Python >= 3.8, < 4.0  
**Primary Dependencies**: Click >= 8.0.0, Pydantic >= 1.10.0, pandas, numpy, aiohttp, asyncio-throttle  
**Storage**: N/A (package organization only)  
**Testing**: pytest >= 7.0.0  
**Target Platform**: Python package (OS-independent)  
**Project Type**: Single Python package with src-layout  
**Performance Goals**: N/A (no runtime changes)  
**Constraints**: 
- Must maintain all existing functionality
- Must preserve package imports and entry points
- Must not break existing tests or workflows
- Zero feature changes - only file relocation  
**Scale/Scope**: Complete codebase reorganization affecting file structure, build configuration, and package discovery

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Compliance Analysis

**III. Dual Interface: CLI and Library** ✅
- Current: Both CLI and library interfaces exist
- Impact: CLI consolidation must preserve CLI functionality; library interface unaffected
- Compliance: Maintained - CLI consolidation preserves dual interface capability

**Technology Stack Constraints** ✅
- Current: Package structure follows src-layout pattern
- Impact: Moving build files to root aligns with Python packaging standards
- Compliance: Improved - better alignment with Python packaging conventions

**Package Structure** ✅
- Current: Source code in `src/` directory; main package `finfetch`
- Impact: File reorganization maintains existing structure; improves discoverability
- Compliance: Maintained and improved

**Start with Working Code** ✅
- Current: Using existing working codebase structure
- Impact: Reorganization follows proven Python packaging patterns
- Compliance: Maintained

**Self-Documenting Development** ✅
- Current: Maintaining documentation and organization
- Impact: Improved organization enhances maintainability
- Compliance: Enhanced

### Gate Evaluation

**PASS** - No constitution violations. Reorganization improves compliance with Python packaging best practices while maintaining all constitution principles.

## Project Structure

### Documentation (this feature)

```text
specs/001-refactor-codebase-org/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (N/A - organizational only)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (N/A - no API changes)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root - AFTER reorganization)

```text
finfetch/                                    # Project root
├── pyproject.toml                           # Build configuration (MOVED from src/)
├── setup.py                                 # Setup script (MOVED from src/)
├── README.md                                # Project documentation
├── LICENSE                                  # License file
├── requirements.txt                         # Dependency requirements
├── .specify/                                # Speckit configuration
│   └── memory/
│       ├── constitution.md
│       └── work-pattern.md
├── src/                                     # Source code (UNCHANGED location)
│   └── finfetch/                            # Main package
│       ├── __init__.py
│       ├── cli.py                           # Unified CLI (CONSOLIDATED from cli.py + cli_simple.py)
│       ├── core/
│       │   ├── __init__.py
│       │   ├── finfetch.py
│       │   └── data_models.py
│       ├── sources/
│       ├── processors/
│       ├── analysis/
│       ├── utils/
│       └── config/
├── test/                                    # Tests (UNCHANGED)
│   ├── automated-tests/
│   └── dev/
│       └── 20251024Baseline/
│           └── helper-scripts/
│               └── rars.py                  # Legacy file (MOVED here if preserved)
└── specs/                                   # Speckit feature specs
    └── 001-refactor-codebase-org/
```

**Structure Decision**: Single Python package with src-layout. Build configuration files moved to project root following Python packaging standards. CLI files consolidated into single `cli.py`. Legacy files relocated to test/dev directories if preserved.

## Complexity Tracking

> **No violations - this section is empty as no constitution violations exist**

## Phase 0: Outline & Research ✅

**Status**: Complete

**Research Findings** (see [research.md](research.md)):
- Python package structure best practices confirmed (src-layout with build files at root)
- CLI consolidation strategy determined (keep `cli.py`, remove `cli_simple.py`)
- Legacy file handling strategy determined (move `rars.py` to test helpers)
- Build configuration migration strategy confirmed (move to root, update paths if needed)
- Import/entry point preservation strategy confirmed (no changes needed)

**All NEEDS CLARIFICATION markers resolved**: N/A (no clarifications needed)

## Phase 1: Design & Contracts ✅

**Status**: Complete

### Data Model

**Document**: [data-model.md](data-model.md)

**Summary**:
- File system structure changes documented
- File relocation mapping provided
- Validation rules aligned with functional requirements
- State transitions defined

### API Contracts

**Status**: N/A - Organizational refactoring with no API changes

**Note**: No contracts directory created as this feature involves file reorganization only, not API changes.

### Quickstart Guide

**Document**: [quickstart.md](quickstart.md)

**Summary**:
- Step-by-step verification procedures
- Success criteria validation checklist
- Rollback procedures documented
- Troubleshooting guide included

### Agent Context Update

**Status**: N/A - No new technologies introduced

**Note**: This organizational refactoring does not introduce new technologies, frameworks, or patterns. Existing technology stack remains unchanged.

## Constitution Check - Post-Design ✅

**Re-evaluation**: All constitution principles maintained

**III. Dual Interface: CLI and Library** ✅
- CLI consolidation preserves CLI functionality
- Library interface completely unchanged
- **Compliance**: Maintained

**Technology Stack Constraints** ✅
- All dependencies remain unchanged
- Package structure improved to align with standards
- **Compliance**: Enhanced

**Package Structure** ✅
- `src/` layout maintained
- Build configuration improved
- **Compliance**: Enhanced

**Start with Working Code** ✅
- Following existing working patterns
- Using proven Python packaging conventions
- **Compliance**: Maintained

**Self-Documenting Development** ✅
- Complete documentation provided
- Verification procedures documented
- **Compliance**: Enhanced

**Gate Status**: ✅ **PASS** - All gates pass. Ready for Phase 2 (tasks generation).
