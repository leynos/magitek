# Baseline provenance

The repository baseline follows
[Youxia PR #7](https://github.com/leynos/youxia/pull/7) at
`a425e64043ef029fe3b67343bee0487418c9ab2d` and
[agent-template-rust PR #168](https://github.com/leynos/agent-template-rust/pull/168)
at `e2327fdbd216d627ee23538bf32cd437af5e7be7`. Youxia originally imported
revision `206c82d52b276903e4f9f1df0ebf85a2938a99bb`; the newer template
snapshot supplies its reviewed Cargo configuration corrections.

| Area                                      | Source and adaptation                                                                                      |
| ----------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| Shared reference guides                   | Youxia snapshot, retained as development reference material.                                               |
| AGENTS.md                                 | Youxia guidance, with project-facing documentation links adapted.                                          |
| Cargo lints, rustfmt, Clippy              | Youxia snapshot; package metadata names the Magitek library.                                               |
| Toolchain and Polonius                    | Youxia dated nightly and components.                                                                       |
| Cargo defaults                            | Template library configuration with Polonius enabled and Linux linker selection.                           |
| Makefile                                  | Template library render, plus Youxia tooling target and nextest coverage guard.                            |
| Shell helpers and tool pins               | Youxia snapshot, preserving bytes and executable modes.                                                    |
| Tooling tests                             | Youxia suite; temporary directory prefix, backend fixture, Git-isolation setup, and compile bound adapted. |
| Test stub                                 | Youxia package-name check adapted to Magitek; temporary until real tests exist.                            |
| YAML, Markdown, coverage configuration    | Youxia snapshot; CV-005 repository name adapted.                                                           |
| PR CI, publisher, audit, mutation callers | Youxia snapshot, plus a pinned Nixie gate for the public Mermaid target and library adaptations.           |
| Dependabot                                | Current template policy, retaining grouping, cooldowns, and default labels.                                |
| README, developer guide, layout, contents | Adapted to the Magitek scaffold and the product documentation on `main`.                                   |

_Table 1: Sources and local adaptations._

The library exposes no greeting function or application entry point. Its
licence, minimum supported Rust release, protocol dependencies, and published
support contract remain future maintainer decisions. No upstream application
licence, binary installation metadata, binary release workflow, or daemon
roadmap is imported.

The Act workflow repeats ordinary tests without consuming its Act flag, so it
is omitted. Delayed comments and automatic merging are outside the requested
validation baseline and are omitted. There is no automatic merge dispatcher or
coverage backstop. Main push and manual coverage publication remain available;
see the
[administration requirements](developers-guide.md#ci-and-repository-administration).

No additional tests duplicate the imported suite. The coverage fixture uses the
adopted template's development rustflags. Coverage replaces those flags to
select LLVM; no unstable Cargo profile override is retained. Empty-library
coverage is not evidence of protocol behaviour; the fixture supplies the
non-zero instrumentation check. The plan's backend-error control is new to this
import because neither reference repository seeds one: a second fixture forces
the Cranelift backend into an instrumented run and requires the failure, so an
empty report cannot pass as clean coverage. Every lane fixture compiles a crate
from scratch and so shares the host's compiler-admission queue; their bound is
widened beyond the imported value because a single coverage lane spent 479
seconds waiting for a slot, while a hung lane still exceeds the bound.

The Cargo configuration explicitly retains the conventional build-directory
layout, which cargo-llvm-cov 0.8.4 requires for object discovery on the pinned
nightly. The template's optional embed-metadata setting is omitted. The
imported coverage fixture uses the same layout setting.

The release artefact target has a toolchain-check prerequisite so that Make
always invokes Cargo, which owns source freshness checking. Without that
prerequisite, an existing release library could hide later source changes.

Local review corrections fix the formatter command examples, Codecov status
nesting, rstest file-glob example, linked-library doctest helpers, and the
environment-injection guidance. The tagged guides identify their actual refresh
source rather than a script absent from this repository. The existing
Git-isolation fixture now filters its setup environment and disables signing
for its temporary commit. Those corrections added no tests.

The publisher retains the reference policy that only main push events advance
the ratchet baseline. No automatic merge workflow is installed, so a review
claim depending on such a caller does not apply. The imported text scanner
retains its documented generated-workflow syntax boundary.

The empty library temporarily opts into the shared mutation workflow's
`allow-no-mutants` input. Remove that input when implementation introduces
mutation candidates. Additional reference corrections distinguish upstream
example testing from Magitek's documentation checks, label forward-looking BDD
APIs, and align ScenarioState/Default guidance with the actual v0.6.0 macro
source. A one-line scanner repair clears scalar state after dedentation.
