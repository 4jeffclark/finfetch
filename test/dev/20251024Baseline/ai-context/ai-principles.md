# FinFetch AI Development Principles

## Core AI Working Principles

### 1. Start with Working Code
- **Always begin with existing, working code patterns** when available
- **Follow established codebase conventions** rather than inventing new approaches
- **Reference similar functionality** to understand proven patterns
- **Never reinvent** what already works well in the codebase

### 2. User-Driven Development Cycle
- **The user always runs tests and provides results** - never assume outcomes
- **Wait for user feedback** before proceeding to next development phase
- **Use user results to guide debugging and refinement** rather than making assumptions
- **Never proceed without explicit user approval** for implementation

### 3. Structured Development Approach
- **Always use existing infrastructure** rather than creating new patterns
- **Avoid creating untested helper scripts** unless absolutely necessary for debugging
- **Keep all work within established frameworks** to maintain consistency and traceability
- **Follow the design → user approval → implementation cycle**

### 4. Self-Documenting Work
- **Create a complete historical record** of all development work for future reference
- **Maintain comprehensive documentation** that allows looking back to understand what was implemented and where development left off
- **Use consistent naming conventions** throughout the session
- **Organize work for easy lookup** and future reference

## Debug and Feedback Management
- **Essential feedback must be visible regardless of debug level** - users need to know what's happening
- **Test console output with debug off** to ensure users aren't left blind
- **Use debug levels consistently** - level 0 for essential info, level 1+ for troubleshooting
- **Provide actionable error messages** and clear next steps

## Code Quality
- **Refactor common functionality early** to avoid duplication
- **Ensure consistency** between related code paths
- **Follow established patterns** rather than creating new approaches
- **Maintain code cleanliness** and organization

## Financial Data Specific Principles

### 5. Data Integrity and Validation
- **Always validate financial data** before processing or storage
- **Implement comprehensive error handling** for data source failures
- **Use structured data models** (Pydantic) for type safety
- **Maintain data lineage** and source attribution

### 6. Performance and Scalability
- **Design for async operations** from the start for financial data collection
- **Implement rate limiting** and throttling for API calls
- **Use efficient data structures** for large financial datasets
- **Plan for horizontal scaling** of data collection operations

### 7. Security and Compliance
- **Never log sensitive financial data** in plain text
- **Implement secure credential management** for API keys
- **Follow financial data handling best practices**
- **Ensure audit trails** for all data operations

### 8. Extensibility and Modularity
- **Design plugin architecture** for new data sources
- **Use dependency injection** for data source management
- **Implement standardized interfaces** for data processors
- **Maintain backward compatibility** when possible
