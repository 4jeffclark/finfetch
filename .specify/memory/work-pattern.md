# FinFetch Development Work Pattern Guide

## Overview

This document provides detailed implementation patterns, file organization, and operational guidelines for FinFetch development. This is implementation guidance referenced from the [FinFetch Constitution](constitution.md) for detailed procedures and patterns.

**Note**: For governance principles and non-negotiable rules, see the [FinFetch Constitution](constitution.md). This document contains implementation details and "how-to" guidance.

## File Organization Patterns

### Test Runner Structure
```
[number]-[descriptive-name].bat    # Test runner file
inputs\[number]-[descriptive-name]\  # Runner-specific inputs
outputs\[number]-[descriptive-name]\ # Runner-specific outputs
```

**Session Examples:**
- `01-baseline-data-collection.bat` → `inputs\01-baseline-data-collection\`, `outputs\01-baseline-data-collection\`
- `02-multi-source-aggregation.bat` → `inputs\02-multi-source-aggregation\`, `outputs\02-multi-source-aggregation\`

**Key Trigger Points:**
- **User Approval**: Implementation only begins after explicit user approval
- **Test Environment**: User provides test environment for each feature and runner
- **Feature Development**: Design documents created ahead of implementation on improvised basis

### Documentation Structure
```
test/dev/
├── backlog/                      # Cross-session design backlog
│   ├── [FEATURE]_DESIGN.md       # Future feature designs
│   └── [FEATURE]_IMPLEMENTATION.md # Future implementation tracking
├── [session-folder]/            # Current session work
│   └── notes/
│       ├── [FEATURE]_DESIGN.md   # Active session designs
│       ├── [FEATURE]_IMPLEMENTATION.md # Active implementation tracking
│       └── [ANALYSIS]_REPORT.md  # Session-specific analysis
└── [other-sessions]/
```

**Current Session Examples:**
- `backlog/YAHOO_FINANCE_INTEGRATION_DESIGN.md` + `backlog/YAHOO_FINANCE_INTEGRATION_IMPLEMENTATION.md` (backlog)
- `backlog/DATA_AGGREGATION_ENGINE_DESIGN.md` + `backlog/DATA_AGGREGATION_ENGINE_IMPLEMENTATION.md` (backlog)
- `notes/POLYGON_INTEGRATION_SUMMARY.md` (20251024Baseline session)

## Naming Conventions

### Test Runners
- **Format**: `[number]-[descriptive-name].bat`
- **Numbering**: Sequential (01, 02, 03...)
- **Descriptive name**: Use kebab-case, descriptive of the test purpose
- **Session Examples**: 
  - `01-baseline-data-collection.bat`
  - `02-multi-source-aggregation.bat`
  - `03-data-processing-pipeline.bat`

### Folder Names
- **Input/Output folders**: Match runner name exactly (without .bat extension)
- **Helper scripts**: Use descriptive names in `helper-scripts/` folder
- **Common configs**: Use descriptive names in `inputs/common/` folder

### Documentation Files
- **Design files**: `[FEATURE]_DESIGN.md` (UPPERCASE with underscores)
- **Implementation files**: `[FEATURE]_IMPLEMENTATION.md` (UPPERCASE with underscores)
- **Feature names**: Use UPPERCASE with underscores for consistency

## Development Workflow

### 1. Feature Development Cycle
```
Design → User Approval → Implementation → Testing → Documentation → Integration
```

**Design Phase:**
- Create `[FEATURE]_DESIGN.md` in `backlog/` folder for future work
- Define architecture, CLI interface, and specifications
- Include sequence diagrams and implementation phases
- **Note**: Design documents start in backlog, moved to session when work begins

**User Approval Phase:**
- User reviews design and approves implementation
- User indicates when to begin acting on design document
- **Note**: Implementation only begins after explicit user approval

**Implementation Phase:**
- Move `[FEATURE]_DESIGN.md` from `backlog/` to current session `notes/` folder
- Create `[FEATURE]_IMPLEMENTATION.md` in current session `notes/` folder
- Use sequence diagram as implementation roadmap
- Track progress with status indicators ([✅] [🔄] [❌] [⚠️])

**Testing Phase:**
- Create test runner: `[number]-[descriptive-name].bat`
- Follow self-documentation pattern for inputs/outputs
- Use helper scripts from `helper-scripts/` folder
- **Note**: User provides test environment for each feature and runner

**Documentation Phase:**
- Update implementation status in `[FEATURE]_IMPLEMENTATION.md`
- Ensure all test data is preserved in organized folders
- Document any deviations or issues encountered

### 2. Test Runner Development
**Before creating a new runner:**
1. Determine the test purpose and scope
2. Choose appropriate number and descriptive name
3. Plan input/output organization
4. Identify required helper scripts

**When creating the runner:**
1. Follow established batch file patterns
2. Implement self-documentation folder structure
3. Use helper scripts from `helper-scripts/` folder
4. Include comprehensive error handling and progress feedback

**After running tests:**
1. Verify inputs/outputs are properly organized
2. Update any documentation with results
3. Preserve test data for future reference

## Helper Scripts Management

### Location and Organization
- **All helper scripts** go in `helper-scripts/` folder
- **Copy from previous sessions** rather than recreating
- **Use descriptive names** that indicate purpose
- **Keep scripts generic** for reuse across different test runners

### Common Helper Scripts
- `create_test_data.py` - Generate test financial data
- `validate_data_sources.py` - Validate data source connectivity
- `calculate_metrics.py` - Financial metrics calculations
- `[future-scripts].py` - Additional utilities as needed

### Usage Pattern
```batch
python -u helper-scripts\[script-name].py [parameters]
```

## Configuration Management

### Common Configurations
- **Location**: `inputs/common/` folder
- **Purpose**: Shared configuration files used by multiple test runners
- **Naming**: Use descriptive names with version dates when relevant

### Runner-Specific Configurations
- **Location**: `inputs\[runner-name]/` folder
- **Purpose**: Specific configurations or copies used by individual test runners
- **Organization**: Copy from `common/` folder when needed for specific tests

## Session-Specific Error Handling

### Batch File Standards
- **Progress indicators**: Show current operation and completion status
- **Error handling**: Comprehensive error checking with clear messages
- **User guidance**: Provide actionable error messages and next steps
- **Echo statement syntax**: Avoid parentheses in echo statements to prevent syntax errors (use -d instead of (-d))

### Debug Level Usage
- **Level 0**: Essential feedback (always visible)
- **Level 1**: Additional details for troubleshooting
- **Level 2**: Trace-level information for deep debugging

## Session Integration Patterns

### Code Reuse Patterns
- **Import from existing modules** rather than duplicating code
- **Follow established conventions** from similar functionality
- **Reference working patterns** (e.g., data source API calls)
- **Maintain consistency** with existing codebase structure

### Testing Integration
- **Regression testing**: Always validate existing functionality
- **Feature testing**: Test new functionality thoroughly
- **Integration testing**: Ensure new features work with existing code
- **User validation**: Wait for user feedback before proceeding

## Session Documentation Maintenance

### Design Documents
- **Keep comprehensive**: Include all architectural decisions and specifications
- **Maintain accuracy**: Update as implementation evolves
- **Include examples**: Provide clear usage examples and CLI interfaces
- **Version control**: Track changes and decisions over time

### Implementation Documents
- **Track progress**: Use sequence diagrams as implementation roadmaps
- **Status indicators**: Clear visual indicators for implementation status
- **Decision log**: Document implementation decisions and rationale
- **Issue tracking**: Record problems encountered and solutions applied

## Session Quality Assurance

### Code Quality
- **Refactor early**: Avoid duplication, extract common functionality
- **Consistent patterns**: Use established codebase conventions
- **Error handling**: Comprehensive error scenarios and user guidance
- **Testing**: Thorough testing at all levels (unit, integration, user)

### Documentation Quality
- **Self-documenting**: Each file should be clear and complete
- **Historical record**: Preserve complete development history
- **Easy lookup**: Organize for quick reference and understanding
- **Future reference**: Enable easy understanding for future development

## Backlog Management Workflow

### Design Lifecycle
1. **Backlog Creation**: Create `[FEATURE]_DESIGN.md` in `test/dev/backlog/` folder
2. **Session Planning**: Move design from `backlog/` to session `notes/` when work begins
3. **Implementation Tracking**: Create `[FEATURE]_IMPLEMENTATION.md` in session `notes/` folder
4. **Completion**: Archive or move completed work as appropriate

### Backlog Organization
- **Cross-session**: Backlog applies across all sessions, not session-specific
- **Flat structure**: No subfolders in backlog, rely on file naming conventions
- **Clear separation**: Backlog vs. active session work is clearly distinguished
- **Easy transition**: Simple file move operation to transition from backlog to active work

## Session Continuity

### Context Discovery for AI Agents
**When starting work on this session folder, AI agents should:**

1. **Review Previous Sessions**: Examine the last 2-3 sessions in `../` (parent directory)
   - **Naming pattern**: Sessions named by start date (e.g., `20251024Baseline`, `20251025-data-sources`)
   - **Purpose**: Understand evolution of development patterns and decisions
   - **Key files**: Review `session-notes.md` and implementation documents
   - **Instruction**: Review the last 2-3 sessions to understand development evolution

2. **Review Source Implementation**: Examine current state of the subject module
   - **Core Module**: Review `src/finfetch/` for current implementation
   - **Related Modules**: Check `src/` for any related functionality
   - **Purpose**: Understand existing codebase before implementing new features
   - **Instruction**: Review the state of implementation in the source folder of the entry point that is the subject of the session

3. **Understand Current Session Context**:
   - **Active designs**: Review all `notes/[FEATURE]_DESIGN.md` files (current session work)
   - **Active implementation**: Check `notes/[FEATURE]_IMPLEMENTATION.md` files (current session work)
   - **Backlog designs**: Review `../backlog/[FEATURE]_DESIGN.md` files for future work
   - **Test infrastructure**: Understand available test runners and helper scripts

### Handoff Preparation
- **Complete documentation**: All design and implementation decisions documented
- **Test data preserved**: All inputs/outputs organized for future reference
- **Status clear**: Current state and next steps clearly defined
- **Dependencies noted**: External dependencies and requirements documented

### Future Development
- **Easy restart**: New developers can quickly understand current state
- **Pattern consistency**: Established patterns can be followed for new features
- **Historical context**: Previous decisions and rationale are preserved
- **Test infrastructure**: Reusable test patterns and helper scripts available

