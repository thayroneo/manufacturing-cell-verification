"""Independent corpus checks; monitor verdicts belong to Java/PObserve tests."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import unittest

from d3_scenarios import inspect_adaptations, simulate_two
from simulate_logs import simulate
from d3_run import check_checker_output
from d3_verify import classify_result

PROJECT = Path(__file__).resolve().parents[1]
EVIDENCE = PROJECT / "Implementation/evidence/D3"


class CorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = json.loads((EVIDENCE / "cases.json").read_text(encoding="utf-8"))

    def test_original_simulator_outputs_remain_compatible(self):
        samples = PROJECT / "ManufacturingCell/pobserve/src/test/resources"
        for policy, seed in (("twophase", 1), ("naive", 2)):
            actual = "\n".join(simulate("cell", policy, seed, 60).lines) + "\n"
            expected = (samples / f"cell_{policy}.log").read_text(encoding="utf-8")
            self.assertEqual(expected, actual)

    def test_committed_samples_are_copied_byte_for_byte(self):
        for policy in ("twophase", "naive"):
            source = PROJECT / f"ManufacturingCell/pobserve/src/test/resources/cell_{policy}.log"
            copy = EVIDENCE / f"logs/original_{policy}.log"
            self.assertEqual(source.read_bytes(), copy.read_bytes())

    def test_all_timestamps_are_strict_and_all_hashes_match(self):
        for case in self.cases["cases"]:
            raw = (EVIDENCE / case["log"]).read_bytes()
            self.assertEqual(case["sha256"], hashlib.sha256(raw).hexdigest())
            timestamps = [dt.datetime.strptime(line[:26], "%Y-%m-%d %H:%M:%S.%f")
                          for line in raw.decode("utf-8").splitlines()]
            self.assertTrue(all(a < b for a, b in zip(timestamps, timestamps[1:])), case["name"])

    def test_two_technicians_overlap_and_fix_prevents_reopening(self):
        seed = self.cases["two_technicians_seed"]
        fixed = inspect_adaptations(simulate_two(seed))
        broken = inspect_adaptations(simulate_two(seed, fixed=False))
        self.assertEqual(2, fixed["max_people"])
        self.assertFalse(fixed["unsafe_reopenings"])
        self.assertTrue(broken["unsafe_reopenings"])

    def test_calibration_measures_start_to_commit_including_known_exceptions(self):
        analysis = inspect_adaptations(simulate("cell", "twophase", 64, 60))
        self.assertEqual(6, max(a["duration"] for a in analysis["completed"]))
        calibration = json.loads((EVIDENCE / "calibration.json").read_text(encoding="utf-8"))
        self.assertEqual(1000, len(calibration["runs"]))
        self.assertEqual(calibration["selected_bound"], max(r["max_ticks"] for r in calibration["runs"]))
        self.assertGreater(calibration["exceeding_original_bound"], 0)
        maximum = inspect_adaptations(simulate("cell", "twophase", 299, 60))
        self.assertEqual(8, max(a["duration"] for a in maximum["completed"]))

    def test_sanction_fault_changes_system_not_just_log(self):
        normal = simulate("cell", "twophase", 1, 60)
        faulty = simulate("cell", "twophase", 1, 60, suppress_sanctions=True)
        self.assertTrue(any(e == "SANCTION" for e, _ in normal.events))
        self.assertFalse(any(e == "SANCTION" for e, _ in faulty.events))
        self.assertEqual([f for e, f in normal.events if e == "TICK"],
                         [f for e, f in faulty.events if e == "TICK"])

    def test_parser_error_must_not_be_hidden_by_a_simultaneous_assertion(self):
        mixed = ("PObserve Spec Violation::\n"
                 "Total Events Read Total Verified Events Total Verified Keys Total Partition Keys\n"
                 "-----\n10 8 1 1\n"
                 "Total Parser Errors Total Spec Errors Total Out of Order Errors Total Unknown Errors\n"
                 "-----\n1 1 0 0\n")
        self.assertEqual("TOOL_ERROR", classify_result(2, mixed))
        self.assertEqual("VIOLATION", classify_result(2, mixed.replace("1 1 0 0", "0 1 0 0")))
        first_event_fails = mixed.replace("1 1 0 0", "0 1 0 0").replace("10 8 1 1", "1 0 0 1")
        self.assertEqual("VIOLATION", classify_result(2, first_event_fails))

    def test_empty_log_must_not_be_reported_as_a_passing_verification(self):
        empty = ("Success! No bugs found.\n"
                 "Total Events Read Total Verified Events Total Verified Keys Total Partition Keys\n"
                 "-----\n0 0 0 0\n"
                 "Total Parser Errors Total Spec Errors Total Out of Order Errors Total Unknown Errors\n"
                 "-----\n0 0 0 0\n")
        self.assertEqual("TOOL_ERROR", classify_result(0, empty))

    def test_partial_checker_campaign_must_not_be_reported_as_complete(self):
        output = "Found 0 bugs.\nExplored 100 schedules\n"
        with self.assertRaises(RuntimeError):
            check_checker_output(output, 1000)
        self.assertEqual(1000, check_checker_output(output.replace("100 schedules", "1000 schedules"), 1000))


if __name__ == "__main__":
    unittest.main(verbosity=2)
