# Clarify the ACP host port and adapter spike

## Purpose and scope

Record how an embedding application can use Magitek's planned semantics as the
target for its own Agent Client Protocol (ACP) host port, while developing an
experimental official-SDK adapter before Magitek's runtime becomes available.
The paired Youxia change defines the port and the `arun` spike. This change
defines Magitek's side of that boundary and the route to qualification.

The user requested both documentation pull requests on 2026-11-20. The request
authorizes this scope; it does not commission runtime implementation,
dependency changes, completed roadmap milestones, or release qualification.

## Context and references

The starting revision is `2296f8ac5d550a2f5706952fb6a641179605dfa5`. The
[technical design](../magitek-design.md) §§2, 3, and 7–10 defines host
ownership, Wireframe adoption gates, and protocol evidence. The
[roadmap](../roadmap.md) separates foundation work from real host adoption.
[ADR 0001](../adrs/adr-0001-reuse-wireframe-for-budgeting-and-stream-parsing.md)
remains the authority for Wireframe reuse. The documentation style guide and
the roadmap and technical design skills govern the edits.

## Invariants and acceptance criteria

- The host owns the port and its concrete adapters. Magitek acquires no
  dependency on Youxia, its storage, or `arun`.
- Capability support, negotiated peer support, installed services, current
  authority/readiness, and qualification remain distinct facts.
- No adapter can describe possible publication as non-submission, omit an
  ordered prefix under a success claim, or grant stale callback authority.
- Adapter replacement starts a fresh protocol generation. Neither process
  survival nor byte replay establishes recovered ACP state.
- Early contract work and the external spike do not bypass Wireframe gates
  or complete any bounded runtime milestone.
- The roadmap gives measurable tasks with satisfiable dependencies and links
  the paired Youxia spike to later Magitek adapter qualification.

## Plan of work

1. Read the existing design, context, roadmap, accepted ADR, and repository
   guidance. Identify existing ownership and evidence contracts to reuse.
2. Add a proposed ADR and design §10.4 for the application boundary. Extend
   the vocabulary and preserve the accepted ADR's historical sequencing text.
3. Add early contract/fixture tasks and connect them to later host-adapter
   qualification. Add the new documents to the contents index.
4. Review both repository changes together. Run `make fmt`, `make check-fmt`,
   `make markdownlint`, and `make nixie`; check relative links, anchors,
   numbering, and `git diff --check`. Record environmental limitations rather
   than replacing a gate with a no-op.

## Progress

- [x] Read the current contracts and agree the paired change outline.
- [x] Update the design, vocabulary, decision records, roadmap, and index.
- [x] Complete cross-repository review and documentation validation.

## Decisions and limits

Keep Rust names illustrative until executable contract tasks fix the API. Reuse
the existing submission-evidence and event-delivery contracts instead of
inventing a second protocol model. Add no new diagram or runtime source file.
Full library and host resource qualification remains later roadmap work.

## Validation and delivery record

Validation on 2026-11-20:

- The exact Markdown formatting and check portions of `make fmt` and
  `make check-fmt` passed with mdtablefix 0.6.1. The editing environment lacked
  the pinned Rust toolchain, so the full Rust targets did not run.
- `make markdownlint`, including the pinned spelling gate, passed across all
  23 Markdown files. Dictionary regeneration introduced no tracked change.
- `make nixie` passed with its documented Merman renderer; no diagrams changed.
- Relative files and anchors resolve, task IDs are unique, and explicit task
  dependency references resolve without cycles. `git diff --check` passed.
- Cross-repository review confirmed that the early Youxia experiment and
  Magitek contract tasks remain independent of runtime gates. The paired Youxia
  task 3.2.6 now permits joint qualification against a pinned Magitek
  candidate, avoiding a circular requirement for a published release.

The pull request carries the paired Youxia link and publication/CI state. No
runtime code changed, no integration test ran, and no planned capability became
an implemented or qualified claim.
