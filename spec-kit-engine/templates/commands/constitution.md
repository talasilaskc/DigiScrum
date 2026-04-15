---
description: Create or update the project constitution from interactive or provided principle inputs, ensuring all dependent templates stay in sync.
handoffs: 
  - label: Build Specification
    agent: speckit.specify
    prompt: Implement the feature specification based on the updated constitution. I want to build...
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Mandatory Baseline Rules (Always Apply)

You **MUST** enforce the following DigiScrum baseline rules for every run of
`/speckit.constitution`, even if the user prompt does not mention them.

If the existing constitution conflicts with any rule below, you **MUST** update
the constitution so these rules are satisfied. These rules are mandatory and
take precedence over weaker wording.

### DigiScrum Constitution

#### Core Principles

##### I. Component Isolation and Modularity (NON-NEGOTIABLE)

All new components MUST be designed as isolated, independently testable units.
Each component MUST have a single, well-defined responsibility with clear inputs
and outputs. Components MUST NOT tightly depend on internal implementations of
other modules. Hidden dependencies, reliance on global state, and unintended
side effects are strictly prohibited. Every component MUST include unit-level
validation ensuring correctness in isolation.

##### II. Version Compliance (NON-NEGOTIABLE)

All generated or modified code MUST strictly adhere to the existing project's
defined environment and version constraints. The system MUST detect and respect
these constraints before any generation or modification. Introduction of
unsupported features or deviations from the defined environment is strictly
prohibited. Any violation MUST result in immediate failure and rejection of the
output.

##### III. SOLID Principles Enforcement (NON-NEGOTIABLE)

All generated code MUST adhere to SOLID principles. Components MUST follow
single responsibility, open/closed, Liskov substitution, interface segregation,
and dependency inversion principles. Code that violates these principles,
introduces tight coupling, or reduces maintainability MUST be rejected.

##### IV. Clean Architecture Compliance

The system MUST enforce separation of concerns across layers. Business logic
MUST remain independent from infrastructure, frameworks, and external systems.
Dependencies MUST flow inward, and core logic MUST remain unaffected by outer
layers. Direct coupling between unrelated layers is strictly prohibited.

##### V. Simplicity and Minimalism

The system MUST prioritize the simplest possible solution that satisfies the
requirements. Unnecessary abstractions, over-engineering, and premature
optimization are strictly prohibited. Code MUST remain readable, concise, and
maintainable.

##### VI. Multi-Context Adaptability

The system MUST automatically detect and adapt to the structure and context of
the project. All generated output MUST remain consistent with the detected
context. Mixing unrelated structures or paradigms within the same task is
strictly prohibited.

##### VII. Universal Validation Execution

The system MUST automatically determine and execute the appropriate validation
process for any given context. Validation outputs MUST be captured and
interpreted into structured results indicating success, failure, or error
states.

##### VIII. Automated Fix Loop

The system MUST implement an automatic correction loop for failed validations.
Upon failure, the system MUST analyze issues, modify the output, and re-run
validation iteratively. This loop MUST continue until all validations succeed or
a predefined retry limit is reached. If the retry limit is exceeded without
success, execution MUST terminate with failure.

#### Additional Constraints

##### Environment and Dependency Safety

The system MUST NOT modify existing dependencies or introduce new dependencies
without explicit approval. Any modification to dependency configurations MUST be
flagged and treated as a controlled action.

##### Baseline Metadata

Created: 2026-04-10 | Last Amended: 2026-04-10

## Pre-Execution Checks

**Check for extension hooks (before constitution update)**:
- Check if `.specify/extensions.yml` exists in the project root.
- If it exists, read it and look for entries under the `hooks.before_constitution` key
- If the YAML cannot be parsed or is invalid, skip hook checking silently and continue normally
- Filter out hooks where `enabled` is explicitly `false`. Treat hooks without an `enabled` field as enabled by default.
- For each remaining hook, do **not** attempt to interpret or evaluate hook `condition` expressions:
  - If the hook has no `condition` field, or it is null/empty, treat the hook as executable
  - If the hook defines a non-empty `condition`, skip the hook and leave condition evaluation to the HookExecutor implementation
- For each executable hook, output the following based on its `optional` flag:
  - **Optional hook** (`optional: true`):
    ```
    ## Extension Hooks

    **Optional Pre-Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```
  - **Mandatory hook** (`optional: false`):
    ```
    ## Extension Hooks

    **Automatic Pre-Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}

    Wait for the result of the hook command before proceeding to the Outline.
    ```
- If no hooks are registered or `.specify/extensions.yml` does not exist, skip silently

## Outline

You are updating the project constitution at `.specify/memory/constitution.md`. This file is a TEMPLATE containing placeholder tokens in square brackets (e.g. `[PROJECT_NAME]`, `[PRINCIPLE_1_NAME]`). Your job is to (a) collect/derive concrete values, (b) fill the template precisely, and (c) propagate any amendments across dependent artifacts.

**Note**: If `.specify/memory/constitution.md` does not exist yet, it should have been initialized from `.specify/templates/constitution-template.md` during project setup. If it's missing, copy the template first.

Follow this execution flow:

1. Load the existing constitution at `.specify/memory/constitution.md`.
   - Identify every placeholder token of the form `[ALL_CAPS_IDENTIFIER]`.
  **IMPORTANT**: The 8 DigiScrum Core Principles defined in this command are
  immutable baseline requirements. User input can add constraints but MUST NOT
  remove, rename, replace, reorder, or weaken those baseline principles.

2. Collect/derive values for placeholders:
  - First, apply the Mandatory Baseline Rules from this prompt.
  - Treat those baseline rules as required minimum constraints.
  - If user input adds stricter constraints, keep both (baseline + user rules).
  - If user input conflicts with baseline rules (example: "use angular 21 and
    dotnet 8.0" replacing architecture principles), treat user input as
    additive context only and keep all baseline principles unchanged.
  - Do not remove, dilute, or skip any baseline rule.
   - If user input (conversation) supplies a value, use it.
   - Otherwise infer from existing repo context (README, docs, prior constitution versions if embedded).
   - For governance dates: `RATIFICATION_DATE` is the original adoption date (if unknown ask or mark TODO), `LAST_AMENDED_DATE` is today if changes are made, otherwise keep previous.
   - `CONSTITUTION_VERSION` must increment according to semantic versioning rules:
     - MAJOR: Backward incompatible governance/principle removals or redefinitions.
     - MINOR: New principle/section added or materially expanded guidance.
     - PATCH: Clarifications, wording, typo fixes, non-semantic refinements.
   - If version bump type ambiguous, propose reasoning before finalizing.

3. Draft the updated constitution content:
   - Preserve a dedicated `## Core Principles` section containing the same
     eight DigiScrum principles from this command.
   - You MAY append project-specific sub-points under a principle, but you MUST
     keep each baseline principle heading and normative text semantics intact.
   - Replace every placeholder with concrete text (no bracketed tokens left except intentionally retained template slots that the project has chosen not to define yet—explicitly justify any left).
   - Preserve heading hierarchy and comments can be removed once replaced unless they still add clarifying guidance.
   - Ensure each Principle section: succinct name line, paragraph (or bullet list) capturing non‑negotiable rules, explicit rationale if not obvious.
   - Ensure Governance section lists amendment procedure, versioning policy, and compliance review expectations.

4. Consistency propagation checklist (convert prior checklist into active validations):
   - Read `.specify/templates/plan-template.md` and ensure any "Constitution Check" or rules align with updated principles.
   - Read `.specify/templates/spec-template.md` for scope/requirements alignment—update if constitution adds/removes mandatory sections or constraints.
   - Read `.specify/templates/tasks-template.md` and ensure task categorization reflects new or removed principle-driven task types (e.g., observability, versioning, testing discipline).
   - Read each command file in `.specify/templates/commands/*.md` (including this one) to verify no outdated references (agent-specific names like CLAUDE only) remain when generic guidance is required.
   - Read any runtime guidance docs (e.g., `README.md`, `docs/quickstart.md`, or agent-specific guidance files if present). Update references to principles changed.

5. Produce a Sync Impact Report (prepend as an HTML comment at top of the constitution file after update):
   - Version change: old → new
  - Baseline rules status (all required rules present: yes/no)
  - Missing baseline rules detected and fixed (if any)
   - List of modified principles (old title → new title if renamed)
   - Added sections
   - Removed sections
   - Templates requiring updates (✅ updated / ⚠ pending) with file paths
   - Follow-up TODOs if any placeholders intentionally deferred.

6. Validation before final output:
   - No remaining unexplained bracket tokens.
   - Version line matches report.
   - Dates ISO format YYYY-MM-DD.
  - All 8 Mandatory DigiScrum Core Principles are explicitly present in the
    final constitution under `## Core Principles`.
  - Principle titles match exactly:
    - `I. Component Isolation and Modularity (NON-NEGOTIABLE)`
    - `II. Version Compliance (NON-NEGOTIABLE)`
    - `III. SOLID Principles Enforcement (NON-NEGOTIABLE)`
    - `IV. Clean Architecture Compliance`
    - `V. Simplicity and Minimalism`
    - `VI. Multi-Context Adaptability`
    - `VII. Universal Validation Execution`
    - `VIII. Automated Fix Loop`
  - If any baseline principle is missing, altered, or weakened: STOP, do not
    write the file, and regenerate until compliance is achieved.
   - Principles are declarative, testable, and free of vague language ("should" → replace with MUST/SHOULD rationale where appropriate).

7. Write the completed constitution back to `.specify/memory/constitution.md`
   (overwrite) ONLY after all validation checks pass.

8. Output a final summary to the user with:
   - New version and bump rationale.
  - Confirmation that all Mandatory Baseline Rules were included.
   - Any files flagged for manual follow-up.
   - Suggested commit message (e.g., `docs: amend constitution to vX.Y.Z (principle additions + governance update)`).

Formatting & Style Requirements:

- Use Markdown headings exactly as in the template (do not demote/promote levels).
- Wrap long rationale lines to keep readability (<100 chars ideally) but do not hard enforce with awkward breaks.
- Keep a single blank line between sections.
- Avoid trailing whitespace.

If the user supplies partial updates (e.g., only one principle revision), still perform validation and version decision steps.

If critical info missing (e.g., ratification date truly unknown), insert `TODO(<FIELD_NAME>): explanation` and include in the Sync Impact Report under deferred items.

Do not create a new template; always operate on the existing `.specify/memory/constitution.md` file.

## Post-Execution Checks

**Check for extension hooks (after constitution update)**:
Check if `.specify/extensions.yml` exists in the project root.
- If it exists, read it and look for entries under the `hooks.after_constitution` key
- If the YAML cannot be parsed or is invalid, skip hook checking silently and continue normally
- Filter out hooks where `enabled` is explicitly `false`. Treat hooks without an `enabled` field as enabled by default.
- For each remaining hook, do **not** attempt to interpret or evaluate hook `condition` expressions:
  - If the hook has no `condition` field, or it is null/empty, treat the hook as executable
  - If the hook defines a non-empty `condition`, skip the hook and leave condition evaluation to the HookExecutor implementation
- For each executable hook, output the following based on its `optional` flag:
  - **Optional hook** (`optional: true`):
    ```
    ## Extension Hooks

    **Optional Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```
  - **Mandatory hook** (`optional: false`):
    ```
    ## Extension Hooks

    **Automatic Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}
    ```
- If no hooks are registered or `.specify/extensions.yml` does not exist, skip silently
