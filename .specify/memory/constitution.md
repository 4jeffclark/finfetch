# FinFetch Constitution

## Core Principles

### I. Modular Architecture with Abstract Base Classes
**All components must inherit from abstract base classes to ensure consistent interfaces and extensibility.**
- Data sources must implement `BaseDataSource` from `sources.base`
- Processors must implement `BaseProcessor` from `processors.base`
- Analyzers must implement `BaseAnalyzer` from `analysis.base`
- Base classes define required interfaces and ensure compatibility with the FinFetch orchestration system
- All implementations must be self-contained and independently testable

### II. Async-First Design
**All I/O operations, especially data collection, must be async by default.**
- Data source collection methods must be `async` and use `asyncio`
- Use `asyncio.gather()` for concurrent data collection from multiple sources
- Implement proper rate limiting and throttling for API calls
- Synchronous interfaces should wrap async implementations only when necessary
- Non-blocking operations are prioritized for scalability

### III. Dual Interface: CLI and Library
**FinFetch must provide both a command-line interface and a programmatic library interface.**
- CLI interface uses Click for command definition (`cli.py`)
- All functionality accessible via `finfetch <command> [options]`
- Library interface enables composition: `from finfetch import FinFetch, DataSource, Processor`
- CLI commands map directly to library methods
- Support for both human-readable and machine-readable (JSON, CSV) output formats

### IV. Data Integrity and Validation (NON-NEGOTIABLE)
**All financial data must be validated using structured data models before processing or storage.**
- Use Pydantic models (`core.data_models`) for all data structures
- Validate all data at source boundaries before processing
- Implement comprehensive error handling for data source failures
- Maintain data lineage and source attribution
- Never process or store invalid or unvalidated financial data

### V. Extensibility Through Plugin Architecture
**New data sources, processors, and analyzers must be easily addable without modifying core code.**
- Use dependency injection for component registration
- Components register themselves via `add_source()`, `add_processor()`, `add_analyzer()`
- No core code changes required to add new sources or processors
- Follow established patterns in existing implementations
- Maintain backward compatibility when extending interfaces

### VI. Structured Logging and Observability
**All components must use structured logging for monitoring and debugging.**
- Use `utils.logger.get_logger()` for consistent logging
- Implement configurable debug levels (0-4) for CLI output
- Essential feedback must be visible at level 0 (clean mode) - users need to know what's happening
- Test console output with debug off to ensure users aren't left blind
- Use debug levels consistently - level 0 for essential info, level 1+ for troubleshooting
- Provide actionable error messages and clear next steps
- Detailed logging for troubleshooting at higher levels
- Never log sensitive financial data or API keys in plain text

## Development Workflow Standards

### Design → Approval → Implementation Cycle (User-Driven Development)
**All feature development follows a structured workflow with explicit user approval gates.**
- The user always runs tests and provides results - never assume outcomes
- Wait for user feedback before proceeding to next development phase
- Use user results to guide debugging and refinement rather than making assumptions
- Never proceed without explicit user approval for implementation

**Workflow Steps:**
1. **Design Phase**: Create design documents in `test/dev/backlog/` before implementation
2. **User Approval**: Wait for explicit user approval before beginning implementation
3. **Implementation**: Move designs to session `notes/` and implement following design
4. **Testing**: Create structured test runners and validate functionality (user runs tests and provides results)
5. **Documentation**: Update implementation status and preserve test data

See `.specify/memory/work-pattern.md` for detailed implementation procedures and workflow patterns.

### Start with Working Code
**Always begin with existing, working code patterns when available.**
- Always begin with existing, working code patterns when available
- Follow established codebase conventions rather than inventing new approaches
- Reference similar functionality to understand proven patterns
- Never reinvent what already works well in the codebase
- Always use existing infrastructure rather than creating new patterns
- Avoid creating untested helper scripts unless absolutely necessary for debugging
- Keep all work within established frameworks to maintain consistency and traceability
- Maintain consistency across similar components

### Self-Documenting Development
**All development work must be documented for future reference.**
- Create a complete historical record of all development work for future reference
- Maintain comprehensive documentation that allows looking back to understand what was implemented and where development left off
- Use consistent naming conventions throughout
- Organize work for easy lookup and future reference

## Testing Requirements

### Test-Driven Development
**Tests must be written and validated before considering features complete.**
- Use pytest for all testing (`test/automated-tests/`)
- Test runners follow structured naming: `[number]-[descriptive-name].bat`
- Test inputs and outputs stored in `inputs/` and `outputs/` directories
- Integration tests required for new data sources and processors
- User runs tests and provides results - never assume outcomes

### Test Coverage Standards
- Core functionality must have comprehensive test coverage
- Data source integrations require integration tests
- Processor outputs must be validated against expected results
- CLI commands must have end-to-end tests
- Coverage reporting via pytest-cov

## Code Quality Standards

### Type Safety
**Use type hints and static type checking to ensure code quality.**
- All functions must have type hints
- Use `mypy` for static type checking with strict settings
- Pydantic models provide runtime type validation
- Type hints required for all public APIs

### Code Formatting
**Maintain consistent code style across the project.**
- Use Black for code formatting (88 character line length)
- Use flake8 for linting
- Pre-commit hooks enforce code quality standards
- Follow PEP 8 with project-specific modifications

### Refactoring Principles
- Refactor common functionality early to avoid duplication
- Extract common functionality to avoid duplication
- Ensure consistency between related code paths
- Follow established patterns rather than creating new approaches
- Maintain code cleanliness and organization

## Financial Data Specific Requirements

### API Rate Limiting
**All data sources must implement rate limiting and throttling.**
- Respect API rate limits for all external services
- Implement exponential backoff for retry logic
- Use `asyncio-throttle` for concurrent request management
- Monitor and log rate limit violations

### Security and Compliance
**Financial data handling must follow security best practices.**
- Never log sensitive financial data or API keys in plain text
- Use environment variables or secure configuration for API keys
- Implement secure credential management
- Ensure audit trails for all data operations
- Follow financial data handling best practices

### Data Processing Standards
- All data processing must be idempotent where possible
- Maintain data lineage and source attribution
- Handle missing data gracefully with appropriate defaults
- Support data cleaning and normalization pipelines
- Provide data quality metrics and validation reports

## Technology Stack Constraints

### Core Dependencies
**Standard dependencies are required and must be compatible with the specified versions.**
- Python >= 3.8, < 4.0
- Core: pandas, numpy, requests
- Async: aiohttp, asyncio-throttle
- Validation: pydantic >= 1.10.0
- CLI: click >= 8.0.0
- Financial: yfinance, alpha-vantage, polygon-api-client, fredapi

### Package Structure
**Follow established package organization patterns.**
- Source code in `src/` directory
- Main package: `finfetch`
- Modules: `core/`, `sources/`, `processors/`, `analysis/`, `utils/`, `config/`
- Tests in `test/` directory
- Development work in `test/dev/` with session folders

## Governance

### Constitution Supremacy
**This constitution supersedes all other development practices and guidelines.**
- All PRs and code reviews must verify compliance with constitution principles
- Amendments require documentation, approval, and migration plan
- Complexity must be justified against constitution principles
- Deviations require explicit approval and documentation

### Amendment Process
**Changes to this constitution must follow a structured process.**
1. Propose amendment with justification
2. Review impact on existing codebase
3. Obtain approval from project maintainers
4. Update constitution with version number
5. Document migration requirements if needed

### Compliance Verification
- Code reviews must check constitution compliance
- Automated checks where possible (type checking, linting)
- Manual review for architecture and workflow compliance
- See `.specify/memory/work-pattern.md` for detailed implementation patterns and workflow procedures

### Reference Files and Implementation Guidance

**Constitution vs. Reference Files:**
- **Constitution** (this document): Contains non-negotiable principles, governance rules, and high-level requirements ("what" must happen)
- **Work Pattern** (`.specify/memory/work-pattern.md`): Contains detailed implementation guidance, file organization patterns, naming conventions, and procedural workflows ("how" to implement)

All development work must comply with constitution principles. Detailed implementation patterns and procedures are documented in the work pattern guide, which is referenced from the constitution.

**Version**: 1.1.0 | **Ratified**: 2025-01-27 | **Last Amended**: 2025-01-27
