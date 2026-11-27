"""Generate the D3 corpus, calibration and expected verdicts (standard library only)."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import shutil

from d3_scenarios import inspect_adaptations, simulate_two
from simulate_logs import Log, simulate

PROJECT = Path(__file__).resolve().parents[1]
MONITORS = ["RegimentationSafety", "NoStaleAdmission", "NoDoubleOutcome",
            "ObligationDeadlineRespected", "AdaptationBoundedTime",
            "LockoutBeforeEntry", "NoOpeningWhileHumanInside"]


def rebuild(events, bound=None):
    log = Log("cell-A")
    for event, fields in events:
        if event == "TICK":
            log.now = fields["Now"]
            log.micro = 0
        log.emit(event, **fields)
        if event == "CONFIG" and bound is not None:
            log.emit("RUNTIME_CONFIG", MaxAdaptTicks=bound)
    return log


def write_log(path, log):
    path.write_text("\n".join(log.lines) + "\n", encoding="utf-8", newline="\n")


def generate(outdir):
    outdir.mkdir(parents=True, exist_ok=True)
    logs = outdir / "logs"
    logs.mkdir(exist_ok=True)
    # Match the independent evaluation's seed range; only durations are
    # computed here. These measurements are not PObserve verdicts.
    calibration_runs = []
    durations = []
    for scenario in ("one_technician", "two_technicians"):
        for seed in range(500):
            log = simulate("cell", "twophase", seed, 60) if scenario == "one_technician" else simulate_two(seed)
            analysis = inspect_adaptations(log)
            if scenario == "two_technicians" and analysis["unsafe_reopenings"]:
                raise AssertionError("fixed simulator reopened with a technician inside")
            durations.extend(a["duration"] for a in analysis["completed"])
            calibration_runs.append({"scenario": scenario, "seed": seed,
                                     "completed": len(analysis["completed"]),
                                     "max_ticks": max((a["duration"] for a in analysis["completed"]), default=0),
                                     "pending_at_eof": analysis["pending_at_eof"],
                                     "max_people": analysis["max_people"]})
    bound = max(durations)
    calibration = {"status": "FACT", "maturity": "LOCALLY_EXECUTED_SYNTHETIC",
                   "method": "ADAPT_START to COMMIT/ADAPT_ABORT in logical ticks, including protocol delay",
                   "seeds_per_scenario": 500, "ticks_per_run": 60,
                   "completed_adaptations": len(durations), "original_bound": 5,
                   "exceeding_original_bound": sum(d > 5 for d in durations),
                   "selected_bound": bound, "histogram": dict(sorted(Counter(durations).items())),
                   "limitation": "Observed maximum of synthetic runs; not a bound for every execution.",
                   "runs": calibration_runs}
    (outdir / "calibration.json").write_text(json.dumps(calibration, indent=2) + "\n", encoding="utf-8")
    cases = []

    def add(name, log, kind, checks, note, original=None):
        path = logs / (name + ".log")
        if original:
            shutil.copyfile(original, path)  # preserve original fixtures byte for byte
        else:
            write_log(path, log)
        cases.append({"name": name, "log": "logs/" + path.name, "kind": kind,
                      "expected": checks, "note": note,
                      "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                      "events": dict(Counter(e for e, _ in log.events)),
                      "analysis": inspect_adaptations(log)})

    passes = {monitor: "PASS" for monitor in MONITORS}
    samples = PROJECT / "ManufacturingCell/pobserve/src/test/resources"
    good = simulate("cell", "twophase", 1, 60)
    naive = simulate("cell", "naive", 2, 60)
    add("original_twophase", good, "BASELINE", passes,
        "Original committed fixture; no runtime configuration added.", samples / "cell_twophase.log")
    add("original_naive", naive, "KNOWN_SYSTEM_DESIGN_FAULT",
        {"RegimentationSafety": "VIOLATION", "NoStaleAdmission": "VIOLATION"},
        "Original naive fixture, unchanged.", samples / "cell_naive.log")
    witness = next(seed for seed in range(500)
                   if inspect_adaptations(simulate_two(seed, fixed=False))["unsafe_reopenings"]
                   and inspect_adaptations(simulate_two(seed))["max_people"] == 2)
    add("two_technicians_fixed", rebuild(simulate_two(witness).events, bound), "SYNTHETIC_FIXED",
        passes, "Two overlapping technicians; seed " + str(witness) + "; holders include pending entry authorizations.")
    add("two_technicians_prefix", rebuild(simulate_two(witness, fixed=False).events, bound),
        "KNOWN_SYSTEM_DESIGN_FAULT", {"NoOpeningWhileHumanInside": "VIOLATION"},
        "Same seed, holder check disabled; serialized adaptations alone do not ensure S4.")
    seed64 = simulate("cell", "twophase", 64, 60)
    add("seed64_default_bound", seed64, "BOUND_CALIBRATION",
        {"AdaptationBoundedTime": "VIOLATION"}, "Original five-tick choice is too small for this synthetic run.")
    add("seed64_calibrated", rebuild(seed64.events, bound), "BOUND_CALIBRATION", passes,
        "Same events with explicit calibrated runtime bound.")
    add("seed299_calibrated", rebuild(simulate("cell", "twophase", 299, 60).events, bound),
        "BOUND_CALIBRATION", passes, "Observed maximum of eight ticks, checked at the selected bound.")
    fault = simulate("cell", "twophase", 1, 60, suppress_sanctions=True)
    add("system_sanction_suppressed", rebuild(fault.events, bound), "SYSTEM_FAULT",
        {"ObligationDeadlineRespected": "VIOLATION"},
        "Organization never performs sanctions. Logger records all events that actually occurred.")
    delayed = simulate("cell", "twophase", 1, 60, commit_delay=bound + 2)
    add("system_commit_delayed", rebuild(delayed.events, bound), "SYSTEM_FAULT",
        {"AdaptationBoundedTime": "VIOLATION"}, "Actual commit is postponed; affected guard remains blocked.")
    for name, event_to_remove, monitor in [
        ("log_missing_leave", "LEAVE", "RegimentationSafety"),
        ("log_deleted_sanction", "SANCTION", "ObligationDeadlineRespected")]:
        events = list(good.events)
        index = next(i for i, (event, _) in enumerate(events) if event == event_to_remove)
        removed = events.pop(index)
        add(name, rebuild(events, bound), "LOG_DEFECT", {monitor: "VIOLATION"},
            "Post-processing removed one actual event " + str(removed) + "; ground truth remains original_twophase.")
    events = list(good.events)
    index = next(i for i, (event, _) in enumerate(events) if event == "COMMIT")
    events.insert(index + 1, events[index])
    add("log_duplicate_commit", rebuild(events, bound), "LOG_DEFECT",
        {"NoStaleAdmission": "VIOLATION"}, "Duplicated COMMIT; timestamps remain strictly increasing.")
    events = list(good.events)
    index = next(i for i, (event, _) in enumerate(events) if event == "SANCTION")
    events.insert(index + 1, events[index])
    add("log_duplicate_outcome", rebuild(events, bound), "LOG_DEFECT",
        {"NoDoubleOutcome": "VIOLATION"}, "Duplicated existing SANCTION; tests S3 on runtime data.")
    bypass = [("CONFIG", {"Capacity": "0:1"}), ("HUMAN_ENTER", {"Res": 0})]
    add("human_bypasses_lockout", rebuild(bypass), "SYSTEM_FAULT",
        {"LockoutBeforeEntry": "VIOLATION"}, "Faithfully recorded entry without a committed lock-out.")
    for wrong in (False, True):
        events = [("CONFIG", {"Capacity": "0:1"}), ("TICK", {"Now": 1}),
                  ("ADAPT_START", {"Ver": 1}), ("TICK", {"Now": 2}),
                  ("ADAPT_ABORT", {"Ver": 2 if wrong else 1})]
        add("abort_wrong_version" if wrong else "abort_valid", rebuild(events, bound),
            "MONITOR_BOUNDARY", {"AdaptationBoundedTime": "VIOLATION" if wrong else "PASS"},
            "Abort must correlate with the pending version.")
    manifest = {"status": "GENERATED_NOT_YET_VERIFIED", "origin": "Synthetic simulation and explicit log mutations",
                "selected_bound": bound, "two_technicians_seed": witness, "cases": cases}
    (outdir / "cases.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {len(cases)} cases; calibrated B={bound}; {len(durations)} completed adaptations; seed={witness}")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, default=PROJECT / "Implementation/evidence/D3")
    generate(parser.parse_args().outdir.resolve())
