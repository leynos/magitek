"""Run real Cargo fixtures through the `make test`, `test-ui` and timeout lanes.

The lanes differ in target selection, grouping and timeout policy, so the tests
observe marker files that record which tests ran and under which nextest group.
The crate and compile bound come from `lanes.py`, the fixture this module
shares with `test_coverage_lanes.py`.
"""

import subprocess
import time
from pathlib import Path

import tomllib
from lanes import COMPILE_TIMEOUT, LaneFixture
from support import GRACEFUL_STOP_SECONDS, ROOT, CommandOptions, RepositoryTest


def _seconds(duration: str) -> float:
    """Convert a nextest duration such as `5s` or `2m` into seconds."""
    unit = duration[-1]
    scale = {"s": 1, "m": 60, "h": 3600}[unit]
    return float(duration[:-1]) * scale


def _grace_periods(settings: dict) -> list[float]:
    """Collect a profile's grace periods, including its overrides."""
    timeout = settings.get("slow-timeout")
    periods = [_seconds(timeout["grace-period"])] if isinstance(timeout, dict) else []
    for override in settings.get("overrides", []):
        periods += _grace_periods(override)
    return periods


def configured_grace_periods(config: dict) -> list[float]:
    """List every termination grace nextest may apply to a fixture run."""
    periods: list[float] = []
    for settings in config["profile"].values():
        periods += _grace_periods(settings)
    return periods


# The fixture installs a `SIGTERM` handler and ignores the signal, so only
# nextest's own escalation can stop it. It reports readiness before waiting, so
# the harness never signals a test that has not yet started.
STUBBORN_TEST = """//! Outlast the runner's termination signal to force its escalation.
unsafe extern "C" {
    fn signal(signal: i32, handler: extern "C" fn(i32)) -> usize;
}

extern "C" fn ignore(_: i32) {}

#[test]
fn stubborn() {
    // SAFETY: `signal` accepts a handler with the C calling convention, and
    // `SIGTERM` is 15 on every platform this fixture runs on.
    unsafe {
        signal(15, ignore);
    }
    std::fs::write("ready.marker", "ready").expect("record readiness");
    for _ in 0..1200 {
        if std::path::Path::new("go.marker").exists() {
            break;
        }
        std::thread::sleep(std::time::Duration::from_millis(50));
    }
    std::thread::sleep(std::time::Duration::from_secs(4));
    std::fs::write("survived.marker", "survived").expect("record survival");
}
"""

# A short grace keeps the fixture quick. What matters is that nextest escalates
# while the harness is still waiting for it to exit.
SHORT_GRACE_PROFILE = """[profile.default]
slow-timeout = { period = "60s", terminate-after = 1, grace-period = "1s" }
"""


def wait_for(marker: Path, process: subprocess.Popen[str]) -> bool:
    """Poll until the fixture reports readiness, gives up, or the bound passes."""
    deadline = time.monotonic() + COMPILE_TIMEOUT
    while time.monotonic() < deadline:
        if marker.exists():
            return True
        if process.poll() is not None:
            return False
        time.sleep(0.05)
    return marker.exists()


class LaneTests(LaneFixture):
    """Check selected tests, cleanup boundaries and actual timeout termination."""

    def test_normal_ui_and_cargo_fallback_retain_tests(self):
        self.probe("ordinary")
        self.probe("compile_probe")
        options = ("CHECK_BUILD_TOOLS=true",)
        self.make("test", *options, command=CommandOptions(timeout=COMPILE_TIMEOUT))
        self.assertTrue(
            (self.repo / "ordinary.ran").exists(),
            "The ordinary lane must execute its integration test",
        )
        self.assertFalse(
            (self.repo / "compile_probe.ran").exists(),
            "nextest must leave compile targets for the UI lane",
        )
        self.make("test-ui", *options, command=CommandOptions(timeout=COMPILE_TIMEOUT))
        self.assertEqual(
            (self.repo / "compile_probe.ran").read_text(),
            "nested-cargo",
            "UI tests must use the serialized group",
        )
        (self.repo / "compile_probe.ran").unlink()
        self.make(
            "test",
            *options,
            "TEST_CMD=test",
            command=CommandOptions(timeout=COMPILE_TIMEOUT),
        )
        self.assertTrue(
            (self.repo / "compile_probe.ran").exists(),
            "Cargo fallback must not silently drop compile targets",
        )

    def test_empty_ui_lane_is_an_explicit_noop(self):
        result = self.make(
            "test-ui",
            "CHECK_BUILD_TOOLS=true",
            command=CommandOptions(timeout=COMPILE_TIMEOUT),
        )
        self.assertIn("nothing to run", result.stdout)

    def test_harness_outlasts_every_configured_nextest_grace_period(self) -> None:
        """The harness must not kill nextest while it is still stopping tests.

        A wait equal to the longest grace period is a race: the harness would
        escalate at the same moment nextest does, so a test that ignores
        `SIGTERM` could outlive the checkout it was running in.
        """
        config = tomllib.loads((ROOT / ".config/nextest.toml").read_text())
        periods = configured_grace_periods(config)
        self.assertTrue(
            periods, "The nextest profiles must configure a termination grace"
        )
        self.assertGreater(
            GRACEFUL_STOP_SECONDS,
            max(periods),
            "The harness must wait longer than nextest's longest grace period",
        )
        self.assertGreaterEqual(
            GRACEFUL_STOP_SECONDS - max(periods),
            5,
            "Leave margin for signal delivery and the runner's own cleanup",
        )

    def test_termination_reaches_a_test_that_ignores_sigterm(self) -> None:
        """A test that ignores `SIGTERM` must not outlive the fixture."""
        self.probe("stubborn", STUBBORN_TEST)
        self.write(".config/nextest.toml", SHORT_GRACE_PROFILE)
        self.run_command(
            "cargo",
            "nextest",
            "run",
            "--no-run",
            options=CommandOptions(timeout=COMPILE_TIMEOUT),
        )
        process = self.start_lane()
        ready = self.repo / "ready.marker"
        try:
            self.assertTrue(
                wait_for(ready, process),
                "The fixture must install its handler before any shutdown",
            )
            # Release the test into its sleep, then let the harness stop it.
            self.write("go.marker", "")
            RepositoryTest._stop(process)
        finally:
            if process.poll() is None:
                RepositoryTest._stop(process)
        self.assert_not_survived()

    def start_lane(self) -> subprocess.Popen[str]:
        """Run the lane in its own session so the harness can signal it."""
        return subprocess.Popen(
            ("cargo", "nextest", "run"),
            cwd=self.repo,
            env=self.env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )

    def assert_not_survived(self) -> None:
        """Reject a survival marker from a test the harness failed to stop."""
        marker = self.repo / "survived.marker"
        released = time.monotonic()
        # The fixture writes its marker four seconds after release; allow more.
        while time.monotonic() - released < 6 and not marker.exists():
            time.sleep(0.1)
        self.assertFalse(
            marker.exists(),
            "A test that ignores SIGTERM must still stop with its process group",
        )

    def test_timeouts_terminate_a_hanging_test(self):
        config = self.repo / ".config/nextest.toml"
        text = config.read_text()
        profile = tomllib.loads(text)["profile"]["default"]
        self.assertGreater(
            profile["slow-timeout"]["terminate-after"],
            0,
            "Per-test termination must be enabled",
        )
        self.assertIn("global-timeout", profile, "The full run must also be bounded")
        self.probe(
            "hanging",
            """//! Deliberately stalled timeout fixture.
#[test]
fn hanging() {
    std::thread::sleep(std::time::Duration::from_secs(60));
}
""",
        )
        for period, total, required, forbidden in (
            # A per-test timeout must not be satisfied by the run-wide limit;
            # nextest reports the global limit as "global timeout" instead, and
            # both outcomes terminate the test and fail the command.
            ("100ms", "3s", "timeout", "global timeout"),
            ("180s", "100ms", "global timeout", None),
        ):
            with self.subTest(limit=required):
                config.write_text(
                    text.replace('"180s"', f'"{period}"')
                    .replace('"5s"', '"100ms"')
                    .replace('"90m"', f'"{total}"')
                )
                result = self.run_command(
                    "cargo",
                    "nextest",
                    "run",
                    options=CommandOptions(expected="failure", timeout=COMPILE_TIMEOUT),
                )
                output = result.stdout.lower()
                self.assertIn(
                    required,
                    output,
                    "The configured limit must terminate a built test",
                )
                if forbidden is not None:
                    self.assertNotIn(
                        forbidden,
                        output,
                        "Per-test termination must not be reported as the global limit",
                    )
