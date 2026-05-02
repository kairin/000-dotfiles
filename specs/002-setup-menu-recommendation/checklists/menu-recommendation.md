# Menu Recommendation Requirements Checklist: Setup Menu Recommendation Guidance

**Purpose**: Validate requirement quality for the `./setup` machine-menu recommendation flow before task generation
**Created**: 2026-05-02
**Feature**: [spec.md](../spec.md)

## Recommendation Decision Completeness

- [x] CHK001 Are all machine setup states that can affect the recommended option explicitly enumerated? [Completeness, Spec §FR-001, Contract §State-To-Recommendation]
- [x] CHK002 Are priority rules defined for cases where blockers, missing tools, safe changes, auth guidance, and manual items overlap? [Completeness, Research §Recommendation Priority Order]
- [x] CHK003 Is the "exactly one recommended option" requirement tied to every evaluated state, including current and manual-only states? [Clarity, Spec §FR-001, Spec §FR-007]
- [x] CHK004 Are requirements defined for how unverified tools differ from missing, installed, and unsupported tools? [Gap, Spec §FR-004, Data Model §Machine Setup State]
- [x] CHK005 Are requirements defined for deciding whether auth guidance is the only useful remaining action? [Gap, Spec §FR-008, Data Model §Machine Setup State]

## Scenario Coverage

- [x] CHK006 Are primary fresh-machine and configured-machine flows both covered with independent scenarios? [Coverage, Spec §User Story 1, Spec §User Story 2]
- [x] CHK007 Are recovery requirements complete for canceled tool installation and partial or unsuccessful tool installation outcomes? [Coverage, Spec §User Story 2, Edge Cases]
- [x] CHK008 Are exception requirements defined for audit or plan failures that prevent safe apply? [Coverage, Spec §FR-006, Edge Cases]
- [x] CHK009 Are protected/manual-only scenarios clearly distinguished from safe-change scenarios? [Clarity, Spec §FR-013, Contract §Safety Contract]
- [x] CHK010 Are fully-current/no-action scenarios specified with enough detail to prevent recommending a no-op apply path? [Completeness, Spec §FR-007, SC-004]
- [x] CHK011 Are non-recommended user choices explicitly allowed without weakening the recommended path? [Consistency, Spec §FR-012, Contract §Safety Contract]

## Requirement Clarity

- [x] CHK012 Is "visible in plain text" defined well enough to avoid relying on color, cursor position, or styling? [Clarity, Spec §FR-002, SC-007]
- [x] CHK013 Is "short reason near the menu" specific enough to guide placement and wording without ambiguity? [Ambiguity, Spec §FR-003, Contract §Recommendation Rendering]
- [x] CHK014 Are stable menu option labels specific enough to prevent documentation and output from drifting? [Clarity, Spec §FR-011, Contract §Stable Menu Options]
- [x] CHK015 Is "same audited machine status" defined with clear source data boundaries? [Ambiguity, Spec §FR-014, Data Model §Machine Setup State]
- [x] CHK016 Are "safe non-protected dotfile or font actions" defined consistently across spec, plan, and contract? [Consistency, Spec §FR-005, Plan §Summary, Contract §State-To-Recommendation]

## Acceptance Criteria Quality

- [x] CHK017 Are success criteria measurable for each recommendation state without depending on terminal styling? [Measurability, SC-001, SC-007]
- [x] CHK018 Do success criteria cover negative cases where no other option may be marked recommended? [Completeness, SC-001, SC-002]
- [x] CHK019 Are documentation-alignment success criteria traceable to specific documented examples? [Traceability, SC-008, Spec §Grounding Context]
- [x] CHK020 Is the refreshed-menu success criterion specific about which actions require a refreshed summary and recommendation? [Clarity, SC-006, Contract §Fresh-Machine Session Contract]

## Consistency And Safety

- [x] CHK021 Are explicit confirmation, backup, and protected-file requirements consistent with the existing constitution gates? [Consistency, Spec §FR-013, Plan §Constitution Check]
- [x] CHK022 Are requirements clear that protected/manual files remain visible but are not counted as safe writable changes? [Clarity, Data Model §Machine Setup State, Contract §Safety Contract]
- [x] CHK023 Are scope boundaries consistent across spec and plan, especially excluding project-folder menus? [Consistency, Spec §Assumptions, Plan §Technical Context]
- [x] CHK024 Are dependency and lock-file assumptions documented clearly enough to avoid unintended tooling changes? [Assumption, Plan §Technical Context, Plan §Constitution Check]

## Documentation And Contract Alignment

- [x] CHK025 Are README and getting-started requirements explicit about the transition from option 1 to option 2 in the fresh-machine flow? [Completeness, Spec §User Story 3, Contract §Fresh-Machine Session Contract]
- [x] CHK026 Are documentation examples required to use the same option numbers and recommendation wording as the contract? [Consistency, Spec §FR-015, Contract §Stable Menu Options]
- [x] CHK027 Does the data model define enough fields to support every state listed in the contract? [Coverage, Data Model §Machine Setup State, Contract §State-To-Recommendation]
- [x] CHK028 Are traceability references available from each user story to functional requirements and success criteria? [Traceability, Spec §User Scenarios, Spec §Functional Requirements, Spec §Success Criteria]

## Incomplete Audit Fallback

- [x] CHK029 Is the incomplete/failed status-audit fallback explicitly treated as a first-class recommendation state across the spec, plan, and contract? [Completeness, Spec §FR-017, Plan §Summary, Contract §State-To-Recommendation]
- [x] CHK030 Is the fallback reason for incomplete or failed status audits specific enough to distinguish "audit incomplete" from the other option 3 reasons? [Clarity, Spec §FR-017, Spec §SC-009]
- [x] CHK031 Are all status-command failure modes that can suppress recommendation confidence identified as in-scope or intentionally excluded? [Coverage, Spec §Edge Cases, Data Model §Machine Setup State]

## Recommendation Language And Traceability

- [x] CHK032 Is the phrase "recommended action" used consistently for the highlighted menu item, summary output, and documentation examples? [Consistency, Spec §Grounding Context, Contract §Recommendation Rendering]
- [x] CHK033 Are the stable option labels and the "Recommended next step" line described with enough precision to avoid alternate wording across docs? [Clarity, Spec §FR-003, Contract §Stable Menu Options]
- [x] CHK034 Are the machine-state inputs that drive recommendation selection named clearly enough to trace from contract to implementation tasks? [Traceability, Spec §FR-014, Tasks T004-T007]

## Scenario And Acceptance Coverage

- [x] CHK035 Are acceptance scenarios defined for both the stale-state case and the refreshed-state case after tool install/cancel, including the incomplete-audit fallback? [Coverage, Spec §User Story 1, Spec §User Story 2]
- [x] CHK036 Are success criteria measurable for the incomplete-audit fallback without relying on implementation-specific command names or shell behavior? [Measurability, Spec §SC-009]
