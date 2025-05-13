You working on the StarryNight codebase and need to assist with testing.

Here's the testing plan:

# StarryNight Testing Context
- This is a living project with ongoing implementation
- Please review recent git commits to understand current progress
- Follow the specified session goals and focus on concrete, focused tests
- Create meaningful commit messages documenting what was tested

# Testing Organization & Strategy
- Test structure should mirror source code (algorithms/, cli/, etc.)
- Key principles: test independence, mock dependencies, focus on high-value tests
- Follow Arrange-Act-Assert pattern
- Use small, representative data samples (<100KB) stored in tests/fixtures/
- Use parameterization for testing variations

# Best Practices to Follow
- Use descriptive test names: test_<function_name>_<scenario_description>
- Add docstrings explaining test purpose
- Focus on testing complex logic, critical paths, and edge cases
- Include proper type annotations
- Use specific exception types
- Make precise assertions

# Anti-patterns to Avoid
- DO NOT test private methods directly; test through public interfaces
- DO NOT create brittle tests with exact string/data structure matches
- DO NOT duplicate tests across multiple levels
- DO NOT over-mock with complex chains
- DO NOT test every possible input; focus on boundaries and representative values

# Workflow
- Code Quality: Run pre-commit checks before committing
  - `pre-commit run --files <path>`
  - `pre-commit run <hook-id> --files <path>`
- Commit Messages: Use semantic prefixes (test:, fix:, feat:, docs:, refactor:)
- Always run tests with UV: `uv run pytest`
