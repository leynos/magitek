# Repository layout

Magitek starts as one library crate. This layout describes the infrastructure
currently present; protocol modules and host adapters remain future work.

| Path                          | Responsibility                                                            |
| ----------------------------- | ------------------------------------------------------------------------- |
| `src/lib.rs`                  | Documented library root, with no protocol API yet.                        |
| `tests/stub.rs`               | Temporary imported nextest package-name check.                            |
| `tests/tooling/`              | Imported tooling integration tests using Python unittest.                 |
| `scripts/`                    | Read-only capability checks, explicit installers, and coverage selection. |
| `tools/mold/`                 | Pinned `mold` release and verified archive checksums.                     |
| `tools/nextest/`              | Minimum runner version for bounded profiles.                              |
| `.cargo/config.toml`          | Development compiler and Linux linker flags.                              |
| `.config/nextest.toml`        | Bounded ordinary and serialized compile-time profiles.                    |
| `.github/workflows/`          | PR CI, main coverage, scheduled audits, and mutation testing.             |
| `.github/cv005.toml`          | Parameters for the shared workflow-contract checker.                      |
| `.github/dependabot.yml`      | Dependency and workflow update policy.                                    |
| `Cargo.toml`                  | Library metadata and Rust, Clippy, and rustdoc lint policy.               |
| `Cargo.lock`                  | Reproducible validation dependency resolution.                            |
| `Makefile`                    | Public build, test, lint, audit, and documentation commands.              |
| `AGENTS.md`                   | Contributor and agent working instructions.                               |
| `docs/contents.md`            | Documentation index.                                                      |
| `docs/execplans/`             | Execution plans and validation records.                                   |
| `docs/baseline-provenance.md` | Source revisions and deliberate adaptations.                              |
| `typos.local.toml`            | Narrow repository spelling exceptions.                                    |
| `typos.toml`                  | Generated shared Oxford British spelling dictionary.                      |

_Table 1: Paths and ownership in the library baseline._

Keep internal modules under src as actual requirements emerge. Tests exercising
public behaviour belong under tests. Keep build entry points in Makefile and
workflow callers under .github/workflows. Update the documentation index when
adding guides. Exclude build output, coverage reports, and Python caches from
Git. There is no binary entry point or binary release workflow; release licence
and support policy remain decisions for publication.
