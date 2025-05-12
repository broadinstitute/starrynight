# StarryNight Testing Plan

This document provides guidance for systematic testing of the StarryNight codebase.

> **Note to AI assistants**: This is a living document maintained across multiple sessions. The user will regularly update this file with implementation progress.
>
> Key guidelines for AI assistants:
> - Review git commit history at the start of each session to understand recent progress
> - Read this document for overall testing strategy and examples
> - Follow the current session goals set by the human
> - Prefer concrete, focused tests over trying to test everything
> - Use the provided mocking patterns and test examples as starting points
> - Create meaningful commit messages that document what was tested

## Quick Reference

- **Code Quality**:
  - Run pre-commit checks: `pre-commit run --files <path>`
  - Run specific pre-commit hook: `pre-commit run <hook-id> --files <path>`

- **Test Organization**: Mirror source code structure (algorithms/, cli/, etc.)
- **Key Principles**: Test independence, mock dependencies, focus on high-value tests
- **Test Pattern**: Follow Arrange-Act-Assert structure

## Test Data Strategy

- Use small, representative data samples (<100KB)
- Store test images in `tests/fixtures/` directory
- Use parameterization for testing variations
- Create focused fixtures for specific test requirements

## Best Practices

### Writing Effective Tests
- Use descriptive test names: `test_<function_name>_<scenario_description>`
- Follow Arrange-Act-Assert pattern
- Add docstrings to test functions that explain the purpose of the test
- Focus on testing complex logic and critical paths
- Test boundary conditions and edge cases
- Include proper type annotations for fixtures and functions
- Use specific exception types instead of generic `Exception` when testing error cases
- Make assertions as specific and precise as possible
- Avoid print statements in tests

### Anti-patterns to Avoid

1. **Testing Implementation Details**
   - ❌ Testing private methods directly
   - ✅ Test the observable behavior through public interfaces

2. **Brittle Tests**
   - ❌ Asserting exact string matches or data structures
   - ✅ Test for key properties that should remain stable

3. **Test Duplication**
   - ❌ Testing the same functionality at multiple levels
   - ✅ Test each behavior once at the appropriate level

4. **Over-mocking**
   - ❌ Creating complex mock chains that mirror implementation
   - ✅ Mock external dependencies but use real implementations when practical

5. **Exhaustive Input Testing**
   - ❌ Testing every possible input combination
   - ✅ Test boundaries, representative values, and error cases


## Code Quality and Pre-commit Workflow

StarryNight uses pre-commit hooks to ensure code quality and consistency:

1. **Linting with Ruff**:
   - Checks for Python best practices and code style
   - Enforces modern type annotations (use `dict` instead of `typing.Dict`)
   - Catches common errors and anti-patterns

2. **Formatting with Ruff Format**:
   - Automatically formats code according to project standards
   - Ensures consistent whitespace and line formatting

3. **Pre-commit Workflow**:
   - Always run pre-commit checks before committing: `pre-commit run --files <path>`
   - Fix any issues identified by the hooks
   - Rerun pre-commit checks to verify all issues are resolved

## Commit Workflow

When making commits to the repository:

1. Ensure all tests pass: `uv run pytest <path_to_test>`
2. Run pre-commit checks: `pre-commit run --files <path>`
3. Use semantic commit messages with type prefixes:
   - `test:` for test-related changes
   - `fix:` for bug fixes
   - `feat:` for new features
   - `docs:` for documentation
   - `refactor:` for code refactoring
4. Include a brief description of the change
5. Add bullet points for significant changes

## Session Workflow

AI assistants should:
1. Review git commit history at the start of each session to understand what has been implemented
2. Focus on the goals specified by the user at the beginning of each session
3. Create meaningful commit messages that document what was tested and implemented
4. Run all tests and pre-commit checks before committing changes
5. Run all tests with UV: `uv run pytest`
