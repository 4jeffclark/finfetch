# Feature Specification: Codebase Organization Refactoring

**Feature Branch**: `001-refactor-codebase-org`  
**Created**: 2025-01-27  
**Status**: Draft  
**Input**: User description: "Refactor codebase organization to follow Python packaging best practices and speckit conventions. Reorganize files into proper locations: move pyproject.toml and setup.py from src/ to project root, consolidate duplicate CLI files (cli.py and cli_simple.py), remove or relocate legacy files (rars.py), ensure proper Python package structure. Maintain all existing functionality - no feature changes, only structural organization improvements."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Install and Use Package After Reorganization (Priority: P1)

Developers must be able to install the FinFetch package from its new structure without any changes to the installation process. The package must continue to function identically after reorganization.

**Why this priority**: This is the most critical scenario - the reorganization must not break existing workflows or installations. Without this, the refactoring fails its primary goal.

**Independent Test**: Can be fully tested by running `pip install -e .` from project root and executing `finfetch --help` to verify CLI functionality remains intact, demonstrating that package installation and entry points work correctly.

**Acceptance Scenarios**:

1. **Given** the project root contains `pyproject.toml` and `setup.py`, **When** a developer runs `pip install -e .`, **Then** the package installs successfully and the `finfetch` command is available
2. **Given** the package is installed, **When** a developer runs `finfetch --help`, **Then** the CLI displays help information and all commands function as before
3. **Given** the codebase is reorganized, **When** a developer imports `from finfetch import FinFetch`, **Then** the import succeeds and the class functions identically to before reorganization

---

### User Story 2 - Development Workflow Consistency (Priority: P2)

Developers must be able to continue their development workflow without disruption. All imports, test execution, and development tools must continue to work from the reorganized structure.

**Why this priority**: Maintaining developer productivity is essential - if development workflows break, the refactoring introduces friction rather than improvement.

**Independent Test**: Can be fully tested by running `pytest` from project root and executing existing test runners (e.g., `test/dev/20251024Baseline/00-finfetch-baseline-test.bat`) to verify all tests pass and outputs are generated correctly.

**Acceptance Scenarios**:

1. **Given** the codebase is reorganized, **When** a developer runs `pytest` from project root, **Then** all existing tests pass without modification
2. **Given** existing test runners are executed, **When** tests complete, **Then** all outputs are generated correctly and match expected formats
3. **Given** development tools (mypy, black, flake8) are executed, **When** code quality checks run, **Then** they operate on the correct file locations and report results accurately

---

### User Story 3 - Code Organization Clarity (Priority: P3)

The codebase structure must follow Python packaging best practices, with build configuration files at project root, a single unified CLI entry point, and no legacy files in production code paths.

**Why this priority**: While not breaking existing functionality, this improves maintainability, onboarding, and aligns with community standards.

**Independent Test**: Can be fully tested by reviewing the project structure and verifying that `pyproject.toml` and `setup.py` are in root, only one CLI file exists in the package, and legacy files are removed or relocated to appropriate locations (e.g., test/dev directories).

**Acceptance Scenarios**:

1. **Given** the reorganization is complete, **When** a developer examines the project root, **Then** `pyproject.toml` and `setup.py` are present in the root directory
2. **Given** the reorganization is complete, **When** a developer examines `src/` (package root), **Then** only one CLI file exists (either `cli.py` or consolidated version), and no legacy files like `rars.py` are present in production code paths
3. **Given** legacy files exist, **When** reorganization is complete, **Then** they are either removed or relocated to appropriate locations (e.g., `test/dev/` for development artifacts)

---

### Edge Cases

- **EC-001**: What happens when multiple CLI files have conflicting entry point definitions?
  - **Resolution**: Verify `cli.py` has the correct entry point (`finfetch.cli:main`) before removing `cli_simple.py`. If conflicts exist, resolve by updating entry point in `pyproject.toml` to match `cli.py`.
- **EC-002**: How does the system handle relative imports that may break when moving build configuration files?
  - **Resolution**: Verify `pyproject.toml` and `setup.py` use absolute or package-relative paths. Path references like `readme = "README.md"` remain valid when files move to root.
- **EC-003**: What if test runners or helper scripts reference files by absolute paths that change during reorganization?
  - **Resolution**: Test runners must use relative paths from project root or be updated to reference new file locations. Verify all test runners function after reorganization (FR-009).
- **EC-004**: How does the reorganization handle package discovery when moving configuration files?
  - **Resolution**: Package discovery settings in `pyproject.toml` (`where = ["src"]`, `package_dir = {"": "src"}`) remain correct after moving files to root. Verify package discovery still works after file moves.

## Requirements *(mandatory)*

### Prerequisites

Before beginning reorganization:

- **P-001**: Work must be performed on a feature branch (`001-refactor-codebase-org`)
- **P-002**: All current changes must be committed to the feature branch before starting file moves
- **P-003**: Backup verification: Ensure Git can restore original file locations using `git checkout HEAD -- <file>` if needed
- **P-004**: Verify current package installation works: Execute `pip install -e .` from project root and confirm `finfetch --help` functions

### Rollback Procedure

If reorganization causes failures or breaks functionality:

- **RB-001**: Restore build configuration files: `git checkout HEAD -- src/pyproject.toml src/setup.py`
- **RB-002**: Move restored files back: Manually move `pyproject.toml` and `setup.py` from root back to `src/` if they were moved
- **RB-003**: Restore CLI files: `git checkout HEAD -- src/cli_simple.py` if it was removed
- **RB-004**: Restore legacy files: `git checkout HEAD -- src/rars.py` if it was moved or removed
- **RB-005**: Verify rollback: Execute `pip install -e .` and `finfetch --help` to confirm original functionality restored

### Functional Requirements

- **FR-001**: Build configuration files (`pyproject.toml` and `setup.py`) MUST be located in the project root directory
- **FR-002**: Package structure MUST follow Python packaging best practices with `src/` layout for source code (package root is `src/` via `package_dir = {"": "src"}` mapping, not `src/finfetch/`). Standards: PEP 517 (Build System Independence), PEP 518 (Specifying Build Dependencies), and setuptools src-layout documentation
- **FR-003**: A single, unified CLI entry point MUST exist in the package (consolidate `cli.py` and `cli_simple.py`)
- **FR-004**: Legacy files (`rars.py`) MUST be removed from production code paths (the `src/` directory) or relocated to appropriate development/test directories. **Decision criteria**: If file contains useful development/test utilities (e.g., test scripts, helper functions), relocate to `test/dev/20251024Baseline/helper-scripts/`. If file is obsolete or unused, remove entirely. Review file contents during implementation to determine usefulness.
- **FR-005**: All package imports MUST continue to work identically after reorganization (e.g., `from finfetch import FinFetch`)
- **FR-006**: CLI entry points MUST function identically after reorganization (e.g., `finfetch --help` must work)
- **FR-007**: Package installation MUST succeed using standard Python installation commands (`pip install -e .`)
- **FR-008**: All existing tests MUST pass without modification after reorganization
- **FR-009**: Test runners and helper scripts MUST continue to function after reorganization
- **FR-010**: Code quality tools (mypy, black, flake8) MUST continue to operate correctly from new file locations
- **FR-011**: Package metadata (version, dependencies, entry points) MUST be preserved during reorganization
- **FR-012**: No functionality changes are permitted - only structural organization improvements

### Key Entities *(include if feature involves data)*

- **Package Structure**: Represents the physical organization of Python package files and directories, including build configuration, source code, and entry points. The package root is `src/` (via `package_dir = {"": "src"}` mapping), meaning `src/cli.py` becomes `finfetch.cli` when the package is installed
- **CLI Entry Point**: Represents the command-line interface that users interact with, defined by package entry points and Click command groups
- **Build Configuration**: Represents files that define package metadata, dependencies, and build settings (`pyproject.toml`, `setup.py`)

## Clarifications

### Session 2025-01-27

- Q: What is the actual package structure location - `src/` as package root via `package_dir` mapping or `src/finfetch/` as a subdirectory? → A: Package is at `src/` (package root) via `package_dir = {"": "src"}` mapping. Files like `src/cli.py` become `finfetch.cli` when installed. No `src/finfetch/` subdirectory exists - the package root is directly in `src/`.
- Q: Should prerequisites and rollback procedures be documented in the specification? → A: Yes, document prerequisites (Git branch, backup verification) and basic rollback procedure (git checkout to restore original file locations if reorganization fails).
- Q: How should "production code paths" be explicitly defined? → A: "Production code paths" means the `src/` directory (package root) - all files that become part of the installed package when users install finfetch.
- Q: Should "Python packaging best practices" in FR-002 reference specific PEP standards? → A: Yes, reference PEP 517 (Build System Independence) and PEP 518 (Specifying Build Dependencies) explicitly in FR-002.
- Q: How should "appropriately relocated" decision criteria be defined for legacy files? → A: If file contains useful development/test utilities → relocate to `test/dev/20251024Baseline/helper-scripts/`. If file is obsolete/unused → remove entirely. Review file contents to determine usefulness before deciding.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Package installs successfully from project root using `pip install -e .` within 30 seconds
- **SC-002**: CLI command `finfetch --help` executes successfully and displays all expected commands
- **SC-003**: All existing automated tests pass without modification (100% test pass rate)
- **SC-004**: All existing test runners execute successfully and generate outputs in expected locations
- **SC-005**: Build configuration files are located in project root (verified by file system inspection)
- **SC-006**: Only one CLI file exists in the package source code directory
- **SC-007**: No legacy files (`rars.py`) exist in production code paths (defined as the `src/` directory, which is the package root and contains all files that become part of the installed package)
- **SC-008**: All package imports function correctly (verified by import test: `from finfetch import FinFetch`)
- **SC-009**: Code quality tools execute successfully from project root (mypy, black, flake8 complete without path errors)
- **SC-010**: Package metadata (name, version, dependencies) matches original values after reorganization
