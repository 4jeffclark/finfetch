# FinFetch Documentation

This directory contains the documentation for the FinFetch project.

## Structure

- `api/` - API reference documentation
- `user_guide/` - User guide and tutorials
- `developer_guide/` - Developer documentation
- `examples/` - Code examples and use cases

## Building Documentation

To build the documentation:

```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Build HTML documentation
sphinx-build -b html docs docs/_build/html

# Or use the Makefile
make html
```

## Documentation Standards

- Use reStructuredText (RST) format for Sphinx documentation
- Include code examples for all major features
- Maintain consistent formatting and structure
- Update documentation with each release

## Contributing to Documentation

1. Follow the existing documentation structure
2. Use clear, concise language
3. Include code examples where appropriate
4. Test all code examples before committing
5. Update the index and navigation as needed
