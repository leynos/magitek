"""Share the disposable crate that the lane test modules run.

`test_lanes` and `test_coverage_lanes` both exercise the public Makefile
through a real checkout, so they derive from one fixture. The module name does
not begin with `test`, so test discovery imports it without collecting a case.
"""

from support import RepositoryTest

# Each fixture is a fresh checkout, so its crate compiles from scratch, and that
# compile shares the host's compiler-admission queue. A one-minute bound would
# measure queue latency rather than the lane; keep the run bounded, but wide.
# The bound is deliberately generous: a single coverage lane measured 479
# seconds of nearly pure queue wait while every admission slot was held by
# unrelated work, so a tighter bound fails the lane for the host's load rather
# than for its behaviour.
COMPILE_TIMEOUT = 900


class LaneFixture(RepositoryTest):
    """Own a dependency-free crate whose tests leave observable markers."""

    def setUp(self):
        """Create a dependency-free crate whose tests leave observable markers."""
        super().setUp()
        self.write(
            "Cargo.toml",
            """[package]
name = "lane-probe"
version = "0.1.0"
edition = "2024"
""",
        )
        self.write("src/lib.rs", "//! Tooling fixture.\n")

    def probe(self, name, body=None):
        """Create a test that records execution and nextest group ownership."""
        self.write(
            "tests/" + name + ".rs",
            body
            or f"""//! Tooling fixture.
#[test]
fn {name}() {{
    let group = std::env::var("NEXTEST_TEST_GROUP").unwrap_or_default();
    std::fs::write("{name}.ran", group).expect("record fixture execution");
}}
""",
        )
