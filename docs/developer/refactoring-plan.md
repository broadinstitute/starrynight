# StarryNight Documentation Refactoring Plan

This document outlines a phased approach to refactoring the StarryNight documentation and code organization, with an emphasis on separating documentation from implementation code.

## Current Issues

The current documentation structure has several issues:

1. **Mixed Code and Documentation**: Implementation code (Python scripts, notebooks, test fixtures) lives within the `/docs/` directory
2. **Unclear Organization**: Some directories like `tester/` contain primarily code rather than documentation
3. **Scattered References**: Tools and scripts are referenced from documentation but not properly organized
4. **Duplicate Guidelines**: Multiple CLAUDE.md files with overlapping information

## Refactoring Goals

1. Keep true documentation in `/docs/` directory
2. Move implementation code to appropriate directories (`/tests/`, `/scripts/`, `/examples/`)
3. Maintain references and functionality during transition
4. Improve overall project organization

## Phase 1: Essential Documentation Cleanup (Highest Priority)

1. **Clean up CLAUDE.md files**
   - Keep main `/docs/CLAUDE.md` as the primary documentation guideline
   - Remove or consolidate duplicate CLAUDE.md files in subdirectories

2. **Add Temporary "Future Organization" Notes**
   - Add a note in `/docs/developer/assets/pcpip-notebooks/` about future move
   - Add a comment in `/docs/developer/pcpip-specs.md` line 930 about future location:
     ```markdown
     Location: [`pcpip-notebooks`](https://github.com/broadinstitute/starrynight/tree/main/docs/developer/assets/pcpip-notebooks)

     > **NOTE:** These notebooks are temporarily located in `/docs/developer/assets/pcpip-notebooks/` but should be moved to `/examples/notebooks/` in the future.
     ```

## Phase 2: Tester Directory Migration (Next Priority)

1. **Create Target Directory Structure**
   ```
   /tests/
   ├── pcpip-fixtures/
   ├── pcpip-generators/
   ├── pcpip-validation/
   └── tools/
   ```

2. **Move Core Test Tools First**
   - Move `/docs/tester/compare_structures.py` → `/tests/tools/`
   - Move `/docs/tester/verify_file_structure.py` → `/tests/tools/`
   - Test that these work in new location

3. **Move Test Fixtures Next**
   - Move `/docs/tester/assets/pcpip-create-fixture/` → `/tests/pcpip-fixtures/`
   - Extract any documentation from README.md files
   - Update any internal path references
   - Test functionality after move

4. **Move Remaining Test Components**
   | Source | Destination |
   |--------|-------------|
   | `/docs/tester/assets/pcpip-generate-dummy-structures/` | `/tests/pcpip-generators/` |
   | `/docs/tester/assets/pcpip-test/` | `/tests/pcpip-validation/` |
   | `/docs/tester/assets/pcpip-pipelines/` | `/tests/pcpip-pipelines/` |
   | `/docs/tester/minimal/` | `/tests/fixtures/minimal/` |
   | `/docs/tester/minimal-output-example/` | `/tests/fixtures/minimal-output-example/` |

## Phase 3: Test Scripts Migration (Lower Priority)

1. **Keep Test Scripts with Tests**
   - Move `/docs/tester/run_pcpip.sh` → `/tests/tools/` or `/tests/`
   - Update path references
   - Test execution

   > **Note:** Since this script is only for testing purposes, it belongs with the test code rather than in a general scripts directory.

## Future Work (Not Immediate)

1. **Handle pcpip-notebooks Properly**
   - Create `/examples/notebooks/`
   - Move notebooks from `/docs/developer/assets/pcpip-notebooks/`
   - Update references in pcpip-specs.md

2. **Update Documentation Structure**
   - Improve navigation between docs
   - Add better index pages

## Testing Strategy

After each migration step:

1. Run any tests that might be affected
2. Verify that documentation references still work
3. Ensure that moved scripts can still be executed
4. Document any path references that needed to be updated

## Completion Criteria

The refactoring will be considered complete when:

1. All implementation code is moved out of `/docs/`
2. Documentation references are updated to point to new locations
3. All tests and scripts function correctly in their new locations
4. `/docs/` contains only actual documentation
