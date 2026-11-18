"""Hold the workflow fixtures that `test_workflows.py` scans.

Each constant is a small GitHub Actions workflow that isolates one rule from
`workflow_lane.py`: where mold must be installed relative to `make test`, which
action and mapping may carry the input, and which near-miss targets must not be
treated as the public lane. Keeping them here leaves the test module within the
repository's file-size limit and places the YAML next to its rationale.
"""

# Mold is installed in `lint` only. A check that searches the whole workflow
# would accept the `test` job's `make test` step, which cannot link.
UNRELATED_MOLD_INSTALL = """\
name: Fixture

on: push

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: leynos/shared-actions/.github/actions/setup-rust@0000000000000000000000000000000000000000
        with:
          install-mold: 'true'
  test:
    runs-on: ubuntu-latest
    steps:
      - run: make test
"""

# A job can list the install after the step that needs it. The ordering
# matters: `make test` has already stopped for a missing linker by the time
# the later step would have installed it.
LATE_MOLD_INSTALL = """\
name: Fixture

on: push

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: make test
      - uses: leynos/shared-actions/.github/actions/setup-rust@0000000000000000000000000000000000000000
        with:
          install-mold: 'true'
"""

# Workflows commonly write commands under a block scalar. A pattern that reads
# only the text after `run:` on the same line would miss this job entirely and
# accept it without a linker installation.
MULTILINE_TEST_STEP = """\
name: Fixture

on: push

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: |
          echo preparing
          make test
"""

# `install-mold` is an input to the shared setup action. An action without that
# input ignores the key, so a check that accepts any action step would pass a
# job that never installs the linker.
MOLD_KEY_ON_AN_UNRELATED_ACTION = """\
name: Fixture

on: push

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/cache@v4
        with:
          path: ~/.cache
          install-mold: 'true'
      - run: make test
"""

# A third-party action may reuse the shared action's name. Only the reviewed
# `leynos/shared-actions` path is known to install mold, so a name match alone
# must not satisfy the check.
MOLD_KEY_ON_A_LOOKALIKE_ACTION = """\
name: Fixture

on: push

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: someone/setup-rust@v1
        with:
          install-mold: 'true'
      - run: make test
"""

# A `run:` block can quote the action path and the input key inside a shell
# script. Those lines are text rather than keys, so a check that searched a
# step's raw text would accept a job that installs nothing.
MOLD_KEY_QUOTED_IN_A_BLOCK = """\
name: Fixture

on: push

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: |
          cat <<'EOF' > snippet.yml
          uses: leynos/shared-actions/.github/actions/setup-rust@0000000000000000000000000000000000000000
          EOF
          install-mold: 'true'
      - run: make test
"""

# `install-mold` is an input to the shared setup action. Naming the key inside
# a shell step provisions nothing, so a check that searches only for the key
# would accept a job that never installs the linker.
MOLD_KEY_IN_A_RUN_STEP = """\
name: Fixture

on: push

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: |
          install-mold: 'true'
      - run: make test
"""

# YAML mapping keys may appear in either order. A check that read only the
# lines above the input would reject a step that does install the linker.
MOLD_INSTALL_LISTED_AFTER_WITH = """\
name: Fixture

on: push

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - with:
          install-mold: 'true'
        uses: leynos/shared-actions/.github/actions/setup-rust@0000000000000000000000000000000000000000
      - run: make test
"""

# The action may also open the step. A check that expected the reference to
# continue a step would report this valid installation as missing.
MOLD_INSTALL_OPENING_THE_STEP = """\
name: Fixture

on: push

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: leynos/shared-actions/.github/actions/setup-rust@0000000000000000000000000000000000000000
        with:
          install-mold: 'true'
      - run: make test
"""

# `make test-ui` shares the `check-build-tools` prerequisite with `make test`,
# so a UI-only lane needs the linker just as much. A pattern that matched only
# `make test` would let this job reach the hosted runner without mold.
UI_TEST_LANE_WITHOUT_MOLD = """\
name: Fixture

on: push

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: make test-ui
"""

# A widened pattern is only useful if a provisioned UI-only lane still passes.
UI_TEST_LANE_WITH_MOLD = """\
name: Fixture

on: push

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: leynos/shared-actions/.github/actions/setup-rust@0000000000000000000000000000000000000000
        with:
          install-mold: 'true'
      - run: make test-ui
"""

# Near-miss targets such as `make test-tooling` and `make testing` neither run
# the lane nor link with mold, so widening the pattern must not start
# requiring the linker in those jobs.
OTHER_TEST_TARGETS = """\
name: Fixture

on: push

jobs:
  tooling:
    runs-on: ubuntu-latest
    steps:
      - run: make test-tooling
      - run: make testing
"""

# The pinned setup action reads `install-mold` from its `with:` inputs, not
# from the process environment. An identically named key under `env:` would
# satisfy a search that ignored mapping ownership while installing nothing.
MOLD_KEY_IN_ENV_WITHOUT_WITH = """\
name: Fixture

on: push

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: leynos/shared-actions/.github/actions/setup-rust@0000000000000000000000000000000000000000
        env:
          install-mold: 'true'
      - run: make test
"""
