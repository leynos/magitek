# Developer guide

Magitek is a bounded async Agent Client Protocol (ACP) host library. This
checkout establishes the build and validation spine. The library has no
protocol implementation or runtime dependencies yet. The host owns its runtime,
configuration loading, authorization, storage, and process lifecycle.

## Local workflow

Run `make install-build-tools` to explicitly install the pinned Rust toolchain,
its components, and the checksum-verified Linux `mold` release under
`BUILD_TOOLS_PREFIX` (default `~/.local`). `make install-cranelift` repairs
only the backend. Installation is separate from validation:

```sh
make check-build-tools
make check-rust-toolchain
make check-coverage-tools
make all typecheck
make markdownlint nixie
make audit
make coverage
```

The capability checks set `RUSTUP_AUTO_INSTALL=0` and never install tools. They
report missing capabilities with repair commands. A usable `mold` version that
differs from the pin produces a diagnostic rather than a failure.

`make all` checks formatting, YAML, Actions, shell, rustdoc, Clippy, Whitaker,
ordinary tests, compile-time tests, repository tooling, shared workflow
contracts, and spelling. `make typecheck` runs Cargo checking separately.
`make build` and `make release` produce library artefacts, with no executable.
`make audit` derives the workspace root using Cargo metadata and runs one
workspace audit. Commit Cargo.lock for reproducible repository validation;
consumers still resolve library dependencies in their own lockfiles. The
supported Wireframe release is the exact version the release matrix qualifies
(ADR 0001); a consumer that resolves another version is outside the advertised
profile.

The full workflow needs clang, `mold`, lld, Python 3.11 or newer, uv, yamllint,
actionlint, ShellCheck, mdtablefix 0.6.1 or newer, Whitaker, cargo-nextest
0.9.100 or newer, and cargo-llvm-cov. Additional targets need cargo-audit,
markdownlint-cli2, and nixie. CI explicitly provisions its prerequisites. Local
Whitaker installation is separate from the build-tools installer; the Makefile
resolves it from PATH or `~/.local/bin/whitaker`.

The Makefile runs the `interrogate` and CV-005 contract tools through the
vendored `scripts/uv_gate.py` helper (`UV_GATE`, which needs `python3` on
`PATH`). The helper selects the global uv cache, runs offline first and makes
at most one online attempt when a tool is not cached yet. A uv that reports only
`Git operation failed` for a Git source missing from the cache is not retried:
warm the cache once with `uv tool run` on that source, or use a uv that names
the offline reason. The spelling builder keeps its direct release-tag call,
because the spelling baseline requires that form and the helper accepts only a
full commit. The Makefile has no `UV` override; the helper finds uv on `PATH`.

## Compiler and linker policy

The dated nightly in rust-toolchain.toml uses Polonius Alpha through
`-Zpolonius=next`. See [the borrow-checker policy](polonius.md). Cargo defaults
and development Make targets also select `-Zthreads=8` and
`-Zcodegen-backend=cranelift`. On Linux, clang invokes `mold`. The Linux Cargo
table repeats every development flag because target flags replace build flags.
The pinned nightly supports a new build directory layout that cargo-llvm-cov
0.8.4 does not scan. `build-dir-new-layout = false` retains conventional object
paths until coverage tooling supports that layout. The template's optional
`embed-metadata` setting is not needed here.

Assigning RUSTFLAGS replaces Cargo's configured flags. Make preserves inherited
RUSTFLAGS in `RUST_FLAGS` and adds warnings, Polonius, and the lane's own
flags. Coverage deliberately omits the development backend and frontend flags,
uses LLVM and lld. Do not set `CARGO_PROFILE_DEV_CODEGEN_BACKEND`: that
reintroduces the removed unstable Cargo profile feature. An inherited backend
flag can defeat that selection: run coverage from an environment without
development-only RUSTFLAGS. Whitaker omits development backend flags for its
own compiler. Release builds retain Polonius and use the pinned nightly,
omitting development backend and linker flags.

## Tests and coverage

`make test` prefers nextest, excludes discovered `tests/compile_*.rs` targets,
and runs workspace doctests separately. `make test-ui` selects those targets
under the serialized `ui` profile. An explicit `[[test]]` declaration must use
the file stem as its name. With no compile-time targets, the UI lane reports
that there is nothing to run. Without nextest, Cargo runs compile-time targets
as ordinary tests, without lane separation, serialization, or nextest timeouts.

The default nextest profile allows 180 seconds per test plus five seconds of
termination grace, and 90 minutes per run. The UI profile serializes nested
Cargo builds and allows 1,200 seconds plus ten seconds of grace per test. The
minimum nextest version is recorded in tools/nextest/VERSION.

`tests/stub.rs` is the imported temporary package-name check. Replace it when
real library tests exist. It prevents nextest's empty-suite error and is not
protocol coverage. `src/lib.rs` intentionally exposes no placeholder API.

`make test-tooling` runs the imported standard-library Python integration suite
in disposable repositories. The suite exercises real Cargo routing, timeout
termination, non-zero coverage, missing capabilities, checksum rejection,
configuration parsing, Git-aware lint selection, and workflow secret isolation.
The inherited tests are the verification basis for this import; no duplicate
tests are introduced. See [baseline provenance](baseline-provenance.md).

`make coverage` requires nextest and writes lcov.info using LLVM and lld. The
current empty library has no executable production statements, so its report is
not a product-coverage claim. The imported fixture separately verifies that
real executable code produces non-zero function coverage, and a negative
control forces a backend that cannot instrument so the run fails instead of
leaving an empty report. Hosted lanes run UI tests before
`scripts/exclude-ui-targets.sh` narrows nextest's default profile. That helper
retains target sources, is idempotent, and rejects conflicting filters. Run it
only in disposable CI checkouts.

## Formatting and documentation

`make fmt` formats Rust and Git-selected Markdown; `make check-fmt` checks
both. mdtablefix includes untracked, nonignored Markdown files. `lint-yaml` and
`lint-shell` enumerate tracked files with null delimiters and propagate Git
errors, so stage new YAML and shell files before validating them. actionlint
checks workflow structure and runs ShellCheck on embedded scripts. Keep
.yamllint-estate.yml identical to the imported estate policy; the local overlay
may add ignores only.

`make spelling` uses the pinned typos-config-builder to regenerate typos.toml
from the shared Oxford British dictionary and typos.local.toml, then checks
Markdown prose. Never hand-edit the generated dictionary or drift-check it in
CI: shared dictionary updates are intentional. Put narrow identifier or quoted
fixture exceptions in the local overlay. `make markdownlint` also runs spelling;
`make nixie` validates Mermaid diagrams. CI provisions the pinned Nixie and
Merman releases and runs `make nixie`, so a diagram that fails locally fails
the pull request too.

The builder requires Python 3.14, so the `Makefile` runs it with
`uv tool run --python 3.14`. `uv` downloads that interpreter when it is
missing; environments that forbid downloads must provide Python 3.14.

## CI and repository administration

PR CI checks formatting, Markdown and Mermaid validation, spelling, lint,
tooling, UI tests, and coverage. It skips whole-lockfile audits for Dependabot
to avoid blocking unrelated updates with existing advisories. The weekly audit
is the compensating check. Scheduled mutation testing temporarily sets
`allow-no-mutants: true` because the library has no implementation to mutate;
remove that input when mutable production code is added. Mutation testing is
informational; surviving mutations need triage, not an assumed successful
quality result. There is no binary release workflow, Act duplicate test lane,
delayed-comment caller, or automatic merge workflow.

Dependabot checks Actions, Cargo, and the Rust toolchain daily, groups shared
Actions and routine minor/patch updates, allows five open updates per
ecosystem, and applies seven-day routine cooldowns and fourteen days for Cargo
majors. Security updates bypass version-update cooldowns. Default ecosystem
labels are retained. Tests should validate SHA pin shape and required action
inputs rather than locking routine action upgrades to a literal commit.

The shared CV-005 checker is pinned in Makefile and configured in
.github/cv005.toml. PR coverage compares without publishing. Only the main
coverage publisher declares the `codescene` environment and receives
`CS_ACCESS_TOKEN`, exclusively as the upload action's input. Missing
credentials skip upload. Before enabling publication, an administrator must
restrict that environment to main and store its credential there. Local
workflow checks cannot verify GitHub settings or hosted execution.

The publisher also supports manual dispatch. No automatic merge caller is
installed, so token-driven merge paths must explicitly dispatch coverage if
they suppress push workflows. The shared coverage action updates the ratchet
baseline on push; dispatch alone does not advance it.

## Reference guides and product design

[Documentation contents](contents.md) indexes reusable development guidance.
OrthoConfig and rstest-bdd guides describe available techniques; their import
adds neither dependency to the library. Configuration loading belongs to the
host. Product design and the roadmap sit alongside this guide in `docs/`; their
tasks stay incomplete until implemented, so do not copy their proposed
capabilities into implemented API documentation.

### Workflow scanner boundary

The imported test helper in tests/tooling/workflow_lane.py recognizes the
generated workflow style used in this repository, rather than arbitrary YAML.
Keep `run: make test` or `run: make test-ui` unquoted or use a literal block.
Keep action inputs directly under `with`, not under a step's `env` mapping, and
do not embed dashed YAML step examples in script blocks. Quoted scalars, nested
mapping ownership, and arbitrary YAML examples are outside this text scanner's
supported syntax. actionlint validates actual workflow syntax, and the real
build preflight checks linker availability. Extending the scanner to other
workflow styles is separate work requiring additional cases; this import
retains the existing tested helper.
