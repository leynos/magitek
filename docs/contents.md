# Documentation contents

- [Documentation contents](contents.md) – this index and the reading order.
- [README](../README.md) – product purpose, current status, and review entry
  points.

## Problem and vocabulary

- [Terms of reference](terms-of-reference.md) – users, scope, verifiable
  outcomes, constraints, and unresolved questions.
- [Context](context.md) – domain language, evidence categories, and the
  relationship between Magitek and its consumers.

## Design and delivery

- [Technical design](magitek-design.md) – ownership, protocol behaviour,
  resource admission, failure semantics, and qualification gates.
- [GIST roadmap](roadmap.md) – Goals, Ideas, Steps, and Tasks, with explicit
  prerequisites and acceptance criteria.
- [ADR 0001](adrs/adr-0001-reuse-wireframe-for-budgeting-and-stream-parsing.md)
  – planned reuse of Wireframe for budgeting and stream parsing, with its
  adoption gates.
- [ADR 0002](adrs/adr-0002-support-application-owned-acp-host-ports.md) –
  application-owned ports, provisional adapters, and later qualification.

## Contract artefacts

- [Resource-policy schema](contracts/resource-policy.schema.json) – the
  proposed data shape, finite ranges, and required policy groups.
- [Resource-policy example](contracts/resource-policy.example.json) – an
  illustrative profile for design validation; values are not release defaults.

## Project guidance

- [Developer guide](developers-guide.md) – local commands, prerequisites, CI,
  test lanes, compiler configuration, and administration.
- [Repository layout](repository-layout.md) – files and ownership boundaries.
- [Baseline provenance](baseline-provenance.md) – exact import sources and
  adaptations for Magitek.
- [Import execution plan](execplans/import-rust-template-repo-baseline.md) –
  approved scope, implementation progress, and acceptance evidence.
- [ACP port execution plan](execplans/acp-host-port-and-adapter-spike.md) –
  scope and validation for the paired host-port and adapter roadmap changes.
- [Documentation style](documentation-style-guide.md) – writing, Markdown,
  architectural decisions, and roadmap conventions.
- [Polonius policy](polonius.md) – pinned compiler and borrow-centric API
  design.

## Rust reference guides

These guides are development references. Their presence does not add runtime or
testing dependencies to Cargo.toml.

- [OrthoConfig v0.10.0](ortho-config-users-guide.md) – layered configuration for
  hosts; Magitek does not own configuration loading.
- [rstest-bdd v0.6.0](rstest-bdd-users-guide.md) – behaviour-driven testing.
- [Dependency injection](reliable-testing-in-rust-via-dependency-injection.md) –
  deterministic tests at external boundaries.
- [Rust doctest guide](rust-doctest-dry-guide.md) – maintainable executable
  documentation examples.
- [rstest fixtures](rust-testing-with-rstest-fixtures.md) – reusable and
  parameterized test setup.
- [Complexity and refactoring](complexity-antipatterns-and-refactoring-strategies.md)
  – maintainable code structure.
- [Scripting standards](scripting-standards.md) – helper-script conventions.

The technical design's section 5 defines the cross-field constraints that JSON
Schema cannot express. The repository contains a draft documentation set and a
dependency-free Rust tooling baseline; implementation and runtime qualification
are still ahead.
