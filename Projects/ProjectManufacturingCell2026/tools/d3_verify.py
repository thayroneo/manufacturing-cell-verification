"""Run real PObserve CLI checks; distinguish assertions from tool/parser errors.

Exit 0 means every requested verdict matched. Exit 1 includes a mismatch or
tool error. Python simulation/mirror results never count as PObserve results.
"""
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time

PROJECT = Path(__file__).resolve().parents[1]


def classify_result(code, console):
    """Accept verdicts only with populated, clean runtime metrics.

    PObserve can return exit 2 when an assertion and parser errors coexist;
    the assertion alone must not hide an unusable input log.
    """
    def metrics(heading):
        if heading not in console:
            return None
        match = re.search(r"(?m)^\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*$",
                          console.split(heading)[-1])
        return tuple(map(int, match.groups())) if match else None

    events = metrics("Total Events Read")
    errors = metrics("Total Parser Errors")
    if events is None or errors is None or events[0] == 0 or events[3] == 0:
        return "TOOL_ERROR"
    parser, assertions, out_of_order, unknown = errors
    if parser or out_of_order or unknown:
        return "TOOL_ERROR"
    if code == 0 and assertions == 0 and events[1] > 0 and events[2] > 0 and "Success! No bugs found." in console:
        return "PASS"
    if code == 2 and assertions > 0 and "PObserve Spec Violation::" in console:
        return "VIOLATION"
    return "TOOL_ERROR"


def verify(args):
    evidence = args.evidence.resolve()
    manifest = json.loads((evidence / "cases.json").read_text(encoding="utf-8"))
    cli = args.cli.resolve()
    package = args.package.resolve()
    for path in (cli, package):
        if not path.is_file():
            raise FileNotFoundError(path)
    output = evidence / "pobserve"
    output.mkdir(exist_ok=True)

    def run(item):
        case, monitor, expected = item
        log = evidence / case["log"]
        if hashlib.sha256(log.read_bytes()).hexdigest() != case["sha256"]:
            raise ValueError("Log differs from manifest: " + case["name"])
        destination = output / case["name"] / monitor
        destination.mkdir(parents=True, exist_ok=True)
        command = [args.java, "-Xmx256m", "-jar", str(cli), "--jars", str(package),
                   "--spec", monitor,
                   "--logs", str(log), "--outputDir", str(destination)]
        started = time.monotonic()
        try:
            result = subprocess.run(command, cwd=PROJECT, capture_output=True, text=True,
                                    encoding="utf-8", errors="replace", timeout=args.timeout)
            stdout = result.stdout + result.stderr
            code = result.returncode
            observed = classify_result(code, stdout)
        except subprocess.TimeoutExpired as error:
            stdout = "PObserve timeout: " + str(error)
            code = None
            observed = "TOOL_ERROR"
        (destination / "console.txt").write_text(stdout, encoding="utf-8")
        # Commands in the JSON are exact local invocations; the public guide
        # provides portable paths. No credentials are placed in commands.
        row = {"case": case["name"], "kind": case["kind"], "monitor": monitor,
               "expected": expected, "observed": observed, "matched": observed == expected,
               "exit_code": code, "elapsed_seconds": round(time.monotonic() - started, 3),
               "command": command, "log_sha256": case["sha256"],
               "console": str((destination / "console.txt").relative_to(evidence))}
        print(f"{case['name']} / {monitor}: {observed} (expected {expected})", flush=True)
        return row

    jobs = [(case, monitor, expected) for case in manifest["cases"]
            for monitor, expected in case["expected"].items()]
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(run, jobs))
    success = all(row["matched"] for row in rows)
    summary = {"status": "VERIFIED" if success else "INCOMPLETE_OR_FAILED",
               "maturity": "LOCALLY_EXECUTED_POBSERVE", "checks": len(rows),
               "matched": sum(row["matched"] for row in rows),
               "tool_errors": sum(row["observed"] == "TOOL_ERROR" for row in rows),
               "cli_sha256": hashlib.sha256(cli.read_bytes()).hexdigest(),
               "package_sha256": hashlib.sha256(package.read_bytes()).hexdigest(),
               "pobserve_source_commit": "260da92", "results": rows}
    (evidence / "results.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    lines = ["# D3 — PObserve CLI results", "", "Status: " + summary["status"], "",
             "| Case | Monitor | Expected | Observed | Exit |", "|---|---|---|---|---|"]
    lines.extend(f"| {r['case']} | {r['monitor']} | {r['expected']} | {r['observed']} | {r['exit_code']} |"
                 for r in rows)
    lines.extend(["", "These are real PObserve CLI invocations on synthetic logs.",
                  "A passing finite log does not prove liveness or physical safety."])
    (evidence / "results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Matched {summary['matched']}/{len(rows)}; tool errors: {summary['tool_errors']}")
    return 0 if success else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, default=PROJECT / "Implementation/evidence/D3")
    parser.add_argument("--cli", type=Path, required=True)
    parser.add_argument("--package", type=Path, default=PROJECT / "ManufacturingCell/pobserve/build/libs/CellRegulation-1.0.0-uber.jar")
    parser.add_argument("--java", default="java")
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--timeout", type=int, default=90)
    raise SystemExit(verify(parser.parse_args()))
