# Import the Rust repository baseline

Status: DRAFT — awaiting plan approval before implementation.

## Purpose / big picture

Turn Magitek's initial repository into a runnable Rust development baseline.
Contributors should be able to discover prerequisites, explicitly install build
tools, and run the same formatting, lint, test, and coverage checks locally and
in GitHub Actions. The import establishes infrastructure for the bounded async
ACP host described in README.md; it does not implement that host.

## Context and orientation

The selected checkout is
`/data/leynos/Projects/magitek.worktrees/import-rust-template-repo-baseline`,
on branch `import-rust-template-repo-baseline`. At inspection, HEAD is
`dff8055` and the working tree is clean. Git tracks only README.md and
.gitignore. There is no Cargo manifest, application source, test suite,
repository guidance, CI, technical design, or terms of reference.

The primary example is [Youxia PR #7](https://github.com/leynos/youxia/pull/7)
at `a425e64043ef029fe3b67343bee0487418c9ab2d`. Its import used
[agent-template-rust PR #168](https://github.com/leynos/agent-template-rust/pull/168)
at `206c82d52b276903e4f9f1df0ebf85a2938a99bb`. The template PR now has head
`e2327fdbd216d627ee23538bf32cd437af5e7be7`; its
`docs/migrations/0.5.0.md` documents further corrections relevant to a fresh
repository. Both PRs were open at inspection, so immutable revisions matter.

## Conformance basis

The user's request and the pinned reference revisions govern this import.
There are no Magitek architecture documents to inherit. Keep a provenance
record identifying the selected revision and any adaptation for each imported
area. Do not present Youxia's design, roadmap, or implementation history as
Magitek's own.

- BASE-1: Repository guidance and reusable development documentation map to
  M1 and M3, accepted by resolved internal links and documentation gates.
- BASE-2: Rust policy, build configuration, and explicit tool provisioning map
  to M1 and M2, accepted by real Cargo checks and capability negative controls.
- BASE-3: Bounded tests and tooling regression infrastructure map to M2,
  accepted by the imported tooling suite and test-lane negative controls.
- BASE-4: CI, audits, and isolated coverage publication map to M3, accepted by
  YAML, Actions, shell, and shared workflow contract checks.

## Constraints

Preserve the repository name, README's product description, origin remote,
and branch. Add only infrastructure and the smallest Cargo scaffold needed
to exercise it. Do not introduce ACP implementation, networking, a runtime,
or unrelated product dependencies. Do not import Youxia-specific daemon
design, RFCs, user claims, or roadmap content.

Keep Make as the public entry point. Import no Netsuke or Ninja machinery.
Keep capability checks read-only, with installation available only through
explicit commands. Preserve SHA-pinned Actions and checksum-verified mold
installation. Never give a PR job the CodeScene upload credential. Preserve
test source files when excluding compile-time tests from coverage.

Do not change repository secrets, environment restrictions, branch protection,
or auto-merge settings. Document any required hosted setup. Do not publish a
release or trigger comment workflows as part of validation.

## Tolerances (exception triggers)

Budgets reflect an infrastructure import rather than a product feature:
up to 3,500 added or changed lines of executable source and tests; up to
3,500 lines of build, lint, and CI configuration; and up to 15,000 lines of
documentation, including reusable reference guides. Generated spelling
dictionaries are recorded separately. The non-ExecPlan file limit is 100.
ExecPlans are excluded from all size and file-count budgets.

Escalate before exceeding those budgets, adding product dependencies, choosing
a product architecture, or weakening a reference policy to make a gate pass.
Routine metadata substitutions, portable fixtures, and verified upstream fixes
are within scope. Record tool failures and diagnose them; do not replace real
checks with successful no-ops.

## Risks

The dated nightly and external tools may require installation. First probe
with automatic installation disabled, then explicitly provision what is
needed. Record any remaining environmental limitation with its failing command.

Youxia's Cargo profile selects Cranelift even during instrumented builds. The
new template moves development backend selection into rustflags. Use that
corrected configuration consistently and verify real non-zero LLVM coverage.

Broad reference documentation can contain project assumptions. Review each
guide, adapt repository guidance, and import only generally applicable guides.
Check relative links and remove claims about nonexistent application features.

Local workflow checks cannot prove GitHub environment restrictions or hosted
execution. Record those as separate administrative and hosted evidence gaps.

## Progress

- [x] (2026-11-15) Inspect checkout, parent guidance, both reference PRs, and
  the current template migration guide.
- [x] (2026-11-15) Draft the adaptation and verification plan.
- [ ] Obtain explicit approval of this plan.
- [ ] M1: Establish Cargo, build policy, and contributor documentation.
- [ ] M2: Integrate checks, test lanes, installers, and regression tests.
- [ ] M3: Integrate CI and complete validation and provenance records.

## Surprises & discoveries

Magitek has no Rust crate yet. A manifest and minimal documented source target
are necessary to make the requested baseline executable.

The template has advanced beyond Youxia's imported revision. Its current
migration guide explicitly removes `[unstable].codegen-backend` and
`[profile.dev].codegen-backend` and places Cranelift in development rustflags.
It also requires explicit compile-test names to match their file stems.

## Decision log

2026-11-15: Use Youxia's integrated checks and tooling suite as the primary
example, reconciled with the pinned template's migration corrections. Keep a
clear record of differences rather than silently copying mixed revisions.

2026-11-15: Add a minimal binary Cargo scaffold named `magitek`, matching the
host description, without implementing host behavior. Adapt release metadata
and workflows to that actual target; do not inherit Youxia's package identity.

2026-11-15: This draft stops before baseline implementation because the
ExecPlan skill requires explicit approval after drafting. A subsequent hook
failure required a minimal Makefile with working `markdownlint` and `nixie`
targets. That repair also adds the missing heading spacing in README.md and
normalizes this plan's blank lines. It does not implement the baseline.

## Plan of work

### M1: Runnable Rust and documentation baseline

Create Cargo.toml, a minimal documented src/main.rs, rust-toolchain.toml,
.cargo/config.toml, .rustfmt.toml, clippy.toml, and appropriate ignore entries.
Adapt the reference manifest's Rust, Clippy, and rustdoc lint tables without
adding application dependencies. Preserve the nightly Polonius configuration
and use the template's corrected development rustflags for Cranelift and mold.
Review package and licence metadata against the source baseline before copying.

Adapt AGENTS.md and docs/developers-guide.md. Import applicable reusable guides
for documentation style, repository layout, scripting, complexity, dependency
injection, rstest fixtures, doctests, and Polonius. Include the rstest-bdd and
OrthoConfig reference guides where linked by the baseline, clearly as reference
material rather than installed Magitek capabilities. Add docs/contents.md and
link the development entry points from README.md. Do not copy the source
project's completed ExecPlan or product documents.

Acceptance: Cargo metadata resolves `magitek`, formatting and type-checking
work, and documentation describes the actual scaffold. Check BASE-1 and BASE-2
against the source snapshots. Remaining gap: full gates and CI. Recovery:
repeat additive file import and metadata substitutions without resetting user
changes. No compatibility layer is needed for this initial repository.

### M2: Checks, installers, and test infrastructure

Adapt Makefile; import scripts/build-tools-common.sh,
scripts/check-build-tools.sh, scripts/install-build-tools.sh, and
scripts/exclude-ui-targets.sh with executable modes. Import tools/mold pins
and checksums and tools/nextest/VERSION. Import .config/nextest.toml,
.yamllint-estate.yml, .yamllint.yml, .markdownlint-cli2.jsonc, and the local
spelling overlay. Keep the estate YAML policy unchanged.

Import and adapt tests/tooling from Youxia. Its standard-library Python suite
exercises Make targets in temporary repositories, real Cargo test routing,
toolchain diagnostics, checksum rejection, lint failures, timeout termination,
coverage exclusion, and workflow credential isolation. Review fixtures for
source-project names and the changed backend configuration. Match any
`[[test]]` compile-test name to `tests/compile_*.rs` file stems. Keep the
no-compile-tests case successful and the Cargo fallback behavior documented.

Acceptance: `make test-tooling`, `make test`, `make test-ui`, and real coverage
pass; negative controls fail for their intended reasons. Check BASE-2 and
BASE-3 and retain actionable missing-tool diagnostics. Remaining gap: workflow
integration. Recovery: rerun isolated fixtures; never run the coverage-selection
helper on the working checkout merely to inspect it.

### M3: CI, delivery checks, and final validation

Adapt .github/workflows/ci.yml and coverage-main.yml and .github/cv005.toml
to `leynos/magitek`. Import scheduled dependency audits, informational mutation
testing, and reviewed Dependabot configuration. Review template release CI for
the actual minimal application target, retaining dry-run dispatch and tag-only
publication. Include coverage dispatch/backstop infrastructure when needed by
the adopted publisher. Evaluate ancillary Act, delayed-comment, and auto-merge
callers for applicability; record omissions and rationale rather than copying
unused workflows. Do not run external comments or enable auto-merge settings.

Ensure CI explicitly installs the tools used by every public target. Keep
compile-time tests before coverage, LLVM backend and lld for instrumentation,
PR comparison without publication, and the main publisher's `codescene`
environment. Review action inputs against their pinned implementations.

Acceptance: run the full commands below, check internal documentation links and
source provenance, and inspect final diff and script modes. Check BASE-1 through
BASE-4 with evidence. Record administrative requirements separately. Recovery:
rerun gates after correcting configuration; no hosted publication is needed to
validate the local baseline.

## Verification plan

The new obligations concern configuration and process boundaries, not ACP
runtime algorithms. No new domain lemma or formal proof is required. The
external assumptions are Cargo, rustup, nextest, llvm-cov, Git, pinned shared
Actions, and GitHub's workflow and environment semantics. Test repository-owned
integration against real command interfaces; do not attempt to prove tool
internals.

Tool provisioning must be explicit: missing-pin, component, linker, and runner
fixtures must reject incomplete environments without changing them. A healthy
fixture supplies the witness that checks can succeed. A bad archive checksum
must fail before installation. Use tests/tooling/test_build_tools.py,
test_installer.py, and test_pins.py.

Ordinary tests, compile-time tests, doctests, and coverage must select the
intended work. Use real temporary Cargo fixtures in test_lanes.py and exclusion
fixtures in test_exclusion.py. Exercise both nextest and Cargo fallback paths,
empty and nonempty compile-target sets, repeated exclusion, and timeout
termination. Seed a backend error to show that coverage checks detect broken
instrumentation; require a real LCOV report with non-zero function coverage.

Lint gates must reject malformed YAML, workflow shell mistakes, shell defects,
and Markdown drift. Use test_lint.py negative controls and valid controls.
Git-aware enumeration must preserve unusual paths and propagate Git failures.

Only main's publisher may receive the CodeScene credential. Use the shared
`make test-workflow-contracts` checker and test_workflows.py fixtures with a
deliberately credential-bearing PR job that must be rejected. Local success
does not discharge GitHub environment policy or hosted execution.

Run imported tests before completing the corresponding implementation and
record meaningful initial failures. For a new repository with no existing
test framework, importing the harness establishes the framework first. Do
not add artificial production functions solely to inflate coverage.

## Concrete steps and validation

Run from the selected checkout. Probe installed tooling without triggering
rustup installation before explicit provisioning. Use the imported installer
for its documented toolchain and mold boundary; install other missing quality
tools explicitly. Stage only this task's files when Git-aware lint enumeration
requires tracked paths, preserving executable bits.

```sh
make check-build-tools check-rust-toolchain check-coverage-tools
make test-tooling
make all typecheck
make markdownlint nixie
make audit
make coverage
git diff --check
git diff --cached --check
```

Successful commands exit zero. Tooling tests report no failures; coverage emits
lcov.info with non-zero covered functions from the real fixture. Inspect
`git diff --stat` and `git diff --cached --stat` for budget compliance. Verify
shell script modes through Git and a disposable export. Inspect local relative
Markdown links, lint provenance records, and record tool versions and evidence
in this plan. Never report a skipped command or unrun hosted workflow as passed.

## Idempotence and recovery

Use immutable source revisions for repeatable imports. Keep test fixtures and
coverage-filter edits in temporary directories. Preserve user changes during
retry. Generated reports and caches belong in ignore rules. Preserve origin;
fetching reference source must not change tracking or push defaults.

## Interfaces and dependencies

The public development interface is the Make target set documented above,
including build/release, explicit installation, read-only checks, formatting,
lint, test, UI-test, audit, and coverage targets. Tests use Python's standard
library, following Youxia. There is no new application runtime dependency.
Shared checker and Actions dependencies retain immutable pins. Keep native
release target support aligned with the reviewed template workflow.

## Outcomes & retrospective

Planning is complete; implementation and validation have not started. The
remaining prerequisite is explicit plan approval. Final delivery must report
the implemented scope, checks actually run, deviations, and hosted setup gaps.

Revision note (2026-11-15): Initial draft based on live reference PR snapshots
and Magitek's initial commit. Adds the minimal Cargo-scaffold requirement and
accounts for current template corrections absent from the Youxia snapshot.

Revision note (2026-11-15): Record the requested post-turn hook repair and
normalize Markdown spacing. Baseline implementation still awaits approval.
