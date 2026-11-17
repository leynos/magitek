"""Exercise the coverage lane's target selection, flags and backend failures."""

from lanes import COMPILE_TIMEOUT, LaneFixture
from support import CommandOptions


class CoverageLaneTests(LaneFixture):
    """Check coverage target selection and the instrumentation it must refuse."""

    def test_coverage_exclusion_preserves_targets_and_refuses_conflicts(self):
        self.probe("ordinary")
        self.probe("compile_probe")
        self.run_command("bash", "scripts/exclude-ui-targets.sh")
        config = self.repo / ".config/nextest.toml"
        first = config.read_bytes()
        self.run_command("bash", "scripts/exclude-ui-targets.sh")
        self.assertEqual(config.read_bytes(), first, "Exclusion must be idempotent")
        self.run_command(
            "cargo", "nextest", "run", options=CommandOptions(timeout=COMPILE_TIMEOUT)
        )
        self.assertTrue(
            (self.repo / "ordinary.ran").exists(),
            "Coverage selection must retain ordinary tests",
        )
        self.assertFalse(
            (self.repo / "compile_probe.ran").exists(),
            "The shared coverage route must not execute UI tests",
        )
        self.make(
            "test-ui",
            "CHECK_BUILD_TOOLS=true",
            command=CommandOptions(timeout=COMPILE_TIMEOUT),
        )
        self.assertTrue(
            (self.repo / "compile_probe.ran").exists(),
            "The UI profile must override coverage's default filter",
        )
        self.assertTrue(
            (self.repo / "tests/compile_probe.rs").exists(),
            "Exclusion must never remove target sources",
        )
        config.write_text(
            config.read_text().replace("not binary(compile_*)", "test(ordinary)")
        )
        conflicting = config.read_bytes()
        self.run_command(
            "bash",
            "scripts/exclude-ui-targets.sh",
            options=CommandOptions(expected="failure"),
        )
        self.assertEqual(
            config.read_bytes(),
            conflicting,
            "A conflicting filter must be preserved for diagnosis",
        )

    def test_coverage_requires_nextest_to_exclude_compile_targets(self):
        result = self.make(
            "coverage",
            "CHECK_COVERAGE_TOOLS=true",
            "TEST_CMD=test",
            command=CommandOptions(expected="failure"),
        )
        self.assertIn(
            "coverage requires cargo-nextest",
            result.stdout,
            "Coverage must refuse a fallback that would instrument UI targets",
        )
        self.assertFalse(
            (self.repo / "lcov.info").exists(),
            "Refused coverage must not write a report",
        )

    def test_coverage_overrides_the_development_cranelift_flags(self):
        self.write(
            ".cargo/config.toml",
            """[build]
rustflags = ["-Zthreads=8", "-Zcodegen-backend=cranelift"]
[unstable]
build-dir-new-layout = false
""",
        )
        self.write(
            "src/lib.rs", "//! Coverage fixture.\npub fn answer() -> u32 { 42 }\n"
        )
        self.write(
            "src/main.rs",
            "//! Mirror the application coverage boundary.\n"
            "fn main() { std::hint::black_box(lane_probe::answer()); }\n",
        )
        self.probe(
            "ordinary",
            """//! Exercise instrumented library code.
#[test]
fn covered() { assert_eq!(lane_probe::answer(), 42, "Fixture answer must be 42"); }
""",
        )
        sysroot = self.run_command("rustc", "--print", "sysroot").stdout.strip()
        host = self.run_command("rustc", "-vV").stdout.split("host: ")[1].split()[0]
        linker_dir = f"{sysroot}/lib/rustlib/{host}/bin/gcc-ld"
        self.env["PATH"] = linker_dir + ":" + self.env["PATH"]
        # Instrumenting the fixture compiles it from scratch, so a cold build
        # can outlast the harness's one-minute default while compiler admission
        # queues it behind unrelated work. Keep the run bounded, but wide enough
        # that the assertion tests instrumentation rather than queue latency.
        self.make(
            "coverage",
            "CHECK_COVERAGE_TOOLS=true",
            command=CommandOptions(timeout=COMPILE_TIMEOUT),
        )
        self.assertRegex(
            (self.repo / "lcov.info").read_text(),
            r"(?m)^FNDA:[1-9]\d*,",
            "The public coverage route must produce instrumented data",
        )

    def test_coverage_reports_a_backend_that_cannot_instrument(self):
        """A backend error must fail coverage instead of yielding empty data.

        The positive fixture proves that a healthy LLVM build produces non-zero
        function coverage. This negative control seeds the failure the check
        must catch: Cranelift cannot emit `-Cinstrument-coverage`, so a
        coverage run that reaches it is broken instrumentation, not a report
        with zero coverage. Accepting an empty `lcov.info` here would let a
        misconfigured backend pass as clean.
        """
        self.write(
            "src/lib.rs", "//! Coverage fixture.\npub fn answer() -> u32 { 42 }\n"
        )
        self.probe(
            "ordinary",
            """//! Exercise instrumented library code.
#[test]
fn covered() { assert_eq!(lane_probe::answer(), 42, "Fixture answer must be 42"); }
""",
        )
        # Re-state the coverage flags because a command-line assignment
        # replaces the Makefile's inherited value rather than adding to it.
        cranelift_flags = (
            "-D warnings -Zpolonius=next -Zcodegen-backend=cranelift "
            "-C link-arg=-fuse-ld=lld"
        )
        result = self.make(
            "coverage",
            "CHECK_COVERAGE_TOOLS=true",
            f"COVERAGE_RUST_FLAGS={cranelift_flags}",
            command=CommandOptions(expected="failure", timeout=COMPILE_TIMEOUT),
        )
        self.assertIn(
            "not supported by Cranelift",
            result.stdout,
            "Coverage must surface the backend error rather than hide it",
        )
        self.assertFalse(
            (self.repo / "lcov.info").exists(),
            "Broken instrumentation must not leave a coverage report",
        )
