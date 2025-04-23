# StarryNight MVP Issue Planning

## Test Fixtures

### #73: Create + Approve small test fixture FIX-S1 (-stitchcrop -qc)

**Description:**

Create and approve the small test fixture FIX-S1 (without stitchcrop and QC) that will serve as a baseline for validation.

**Tasks:**

- Define specifications for FIX-S1 test fixture
- Create test fixture with appropriate sample data
- Develop scripts for downloading/generating the test fixture
- Create YAML configuration files describing the test fixture
- Document the fixture's structure and content
- Review and approve the fixture with stakeholders

**Definition of Done:**

- Test fixture is clearly identified and documented
- Download/setup scripts are created and tested
- YAML configuration files are complete
- Fixture is approved by relevant stakeholders (@ErinWeisbart)
- Fixture is ready for validation (#71)

**Assignees:** @ErinWeisbart @shntnu @leoank

---

### #74: Create + Approve small test fixture FIX-S2 (+stitchcrop +qc)

**Description:**
Create and approve the small test fixture FIX-S2 (with stitchcrop and QC) that extends FIX-S1 to include these additional functionalities.

**Tasks:**
Same as #73

**Definition of Done:**
Same as #73

**Assignees:** @ErinWeisbart @shntnu @leoank

---

### #80: Create + Approve large test fixture FIX-L1 (+stitchcrop +qc)

**Description:**

Create and approve the large test fixture FIX-L1 (with stitchcrop and QC) that will consist of a full plate of data from which FIX-S1/S2 were derived.

**Tasks:**
Same as #73

**Definition of Done:**
Same as #73


**Assignees:** @ErinWeisbart @shntnu @leoank

---

### #91: Create + Approve large test fixture FIX-L2

**Description:**

Create and approve the large test fixture FIX-L2, likely a second full plate from the dataset.

**Tasks:**
Same as #73

**Definition of Done:**
Same as #73


**Assignees:** @ErinWeisbart @shntnu @leoank

---

### #71: Validate small test fixture FIX-S1 (-stitchcrop -qc)

**Description:**

Validate the small test fixture FIX-S1 (without stitchcrop and QC functionality) to ensure produces expected results.

**Tasks:**

- Run end-to-end tests with the FIX-S1
- Follow the multi-stage validation process outlined in `/docs/tester/README.md`
- Document test results and any discrepancies found
- Create validation report with screenshots/examples of correct output
- Address and resolve any issues identified during validation

**Definition of Done:**

- All tests pass successfully
- Validation report is complete and approved
- Any discrepancies are documented or resolved

**Assignees:** @shntnu @leoank

---

### #59: Validate small test fixture FIX-S2 (+stitchcrop +qc)

**Description:**

Validate the small test fixture FIX-S2 (with stitchcrop and QC functionality) to ensure it correctly implements these additional features and produces expected results.

**Tasks:**

Same as #71

**Definition of Done:**

Same as #71

**Assignees:** @ErinWeisbart @shntnu

---

### #83: Validate large test fixture FIX-L1 (+stitchcrop +qc)

**Description:**

Validate the large test fixture FIX-L1 (with stitchcrop and QC) to ensure it correctly handles a full plate of data.

**Tasks:**

Same as #71, additionally:

- Develop sampling strategy for validating large datasets
- Log processing time and resource requirements

**Definition of Done:**

Same as #71, additionally:

- Performance metrics are documented

**Assignees:** @ErinWeisbart @shntnu

---

### #84: Validate large test fixture FIX-L1/GUI (+stitchcrop +qc)

**Description:**

Validate the large test fixture FIX-L1 using the GUI interface rather than programmatically.

**Tasks:**

Same as #83, additionally

- Document any GUI-specific issues or discrepancies

**Definition of Done:**

Same as #83, additionally

- Any GUI-specific issues are documented or resolved

**Assignees:** @ErinWeisbart @shntnu

---

### #93: Validate large test fixture FIX-L2/GUI

**Description:**

Validate the large test fixture FIX-L2 using the GUI interface.

**Tasks:**

- Same as #84

**Definition of Done:**

- Same as #84

**Assignees:** @ErinWeisbart @bethac07

---

## Documentation

### #100: Create + Approve System Architecture overview

**Description:**

Create and approve comprehensive documentation of the StarryNight system architecture to help stakeholders understand the system design and components.

**Tasks:**

- Document system layers and components:
  - Algorithm Layer
  - CLI Layer
  - Module Layer
  - Pipeline Layer
  - Execution Layer
  - Configuration Layer
- Create architectural diagrams
- Document data and control flow
- Document extension points
- Define key terms and concepts
- Review and approve with stakeholders

**Definition of Done:**

- Architecture documentation is complete
- Diagrams clearly illustrate system components and relationships
- Extension points are well-defined
- Documentation is approved by stakeholders
- Documentation is integrated into the project documentation site

**Assignees:** @shntnu @bethac07 @leoank

---

### #98: Create + Approve System Maintenance Guide

(FIXME: THIS ISSUE NEEDS HEAVY EDITING)


**Description:**

Create and approve a maintenance guide for the StarryNight system to ensure C-lab engineers can maintain and extend the system.

**Tasks:**

- Document system dependencies and requirements
- Detail maintenance procedures:
  - Updating components
  - Troubleshooting common issues
  - Testing procedures
  - Deployment procedures
- Document monitoring and logging
- Create checklist for system health verification
- Review and approve with stakeholders

**Definition of Done:**

- Maintenance guide is complete
- Procedures are clear and actionable
- Guide is approved by stakeholders
- Guide is integrated into the project documentation site

**Assignees:** @bethac07 @shntnu @leoank

---

### #96: Create + Approve Workflow Implementation Guide

(FIXME: THIS ISSUE NEEDS HEAVY EDITING)

**Description:**

Create and approve a guide for implementing new workflows in StarryNight.

**Tasks:**

- Document workflow creation process:
  - Defining requirements
  - Creating modules
  - Composing pipelines
  - Testing workflows
- Provide examples of workflow implementation
- Document best practices
- Include sample code and templates
- Review and approve with stakeholders

**Definition of Done:**

- Workflow implementation guide is complete
- Examples demonstrate complete workflow creation
- Guide is approved by stakeholders
- Guide is integrated into the project documentation site

**Assignees:** @bethac07 @shntnu @leoank

---

### #94: Create + Approve AWS Deployment Roadmap

(FIXME: THIS ISSUE NEEDS HEAVY EDITING)

**Description:**

Create and approve a roadmap for deploying StarryNight on AWS.

**Tasks:**

- Document AWS deployment architecture:
  - Required services
  - System topology
  - Resource requirements
- Create deployment plan with milestones
- Document configuration requirements
- Address security considerations
- Include cost estimates
- Review and approve with stakeholders

**Definition of Done:**

- AWS deployment roadmap is complete
- Architecture is well-defined
- Plan has clear milestones
- Roadmap is approved by stakeholders
- Roadmap is integrated into the project documentation site

**Assignees:** @bethac07 @shntnu @leoank

---

## Code Walkthrough

(FIXME: THIS ISSUE NEEDS HEAVY EDITING)

### #99: Conduct + Validate Code Walkthrough sessions

**Description:**

Conduct code walkthrough sessions to ensure stakeholders understand the codebase and implementation.

**Tasks:**

- Schedule multiple walkthrough sessions
- Prepare walkthrough materials:
  - Overview of system components
  - Key implementation details
  - Example workflows
- Conduct sessions with stakeholders
- Document questions and clarifications
- Address any concerns raised during sessions
- Collect feedback for system improvements

**Prerequisites:**

- Documentation should be complete
- Test fixtures should be validated

**Definition of Done:**

- All scheduled walkthrough sessions are completed
- Stakeholders understand the codebase and implementation
- Questions and concerns are addressed
- Feedback is documented for future improvements
- Stakeholders approve the implementation approach

**Assignees:** @bethac07 @shntnu @leoank @ErinWeisbart
