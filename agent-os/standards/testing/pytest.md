# Testing Standards

## Test Structure

- Place tests in `tests/` directory
- Use descriptive function names: `test_<functionality>_<scenario>`
- Organize test module names to match the module being tested
- Test both the happy path and edge cases
- Use `tests/conftest.py` and fixtures as appropriate (but only when useful)
- When you create fixtures, write tests for those fixtures

## Coverage

- Don't write too many tests
- But try to keep coverage at 100% as part of final verification
- Prefer unit tests but where needed write

