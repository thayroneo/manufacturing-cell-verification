"""Reproduce D3 locally: corpus, Python, P compilation, JUnit and PObserve CLI.

Requires Python 3.10+, .NET 8 / P 3.1.0, JDK 17 and the PObserve CLI jar.
No logs or project data are uploaded. Gradle may download build dependencies.
"""
import argparse
import csv
import datetime as dt
import html
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

PROJECT = Path(__file__).resolve().parents[1]


def check_checker_output(output, expected_schedules):
    bugs = re.search(r"Found (\d+) bugs?", output)
    schedules = re.search(r"Explored (\d+) schedules?", output)
    if bugs is None or schedules is None or int(bugs[1]) != 0 or int(schedules[1]) != expected_schedules:
        raise RuntimeError("Checker did not confirm zero bugs in the full requested schedule count")
    return int(schedules[1])


def main(args):
    evidence = PROJECT / "Implementation/evidence/D3"
    evidence.mkdir(parents=True, exist_ok=True)
    (evidence / "summary.json").write_text(json.dumps({"status": "RUNNING"}) + "\n", encoding="utf-8")
    steps = []
    started = time.monotonic()

    def run(name, command, cwd=PROJECT):
        print("Running " + name, flush=True)
        begin = time.monotonic()
        completed = subprocess.run([str(x) for x in command], cwd=cwd, capture_output=True,
                                   text=True, encoding="utf-8", errors="replace")
        output = completed.stdout + completed.stderr
        (evidence / (name + ".txt")).write_text(output, encoding="utf-8")
        steps.append({"step": name, "command": [str(x) for x in command], "cwd": str(cwd),
                      "exit_code": completed.returncode, "seconds": round(time.monotonic()-begin, 3)})
        (evidence / "commands.json").write_text(json.dumps(steps, indent=2) + "\n", encoding="utf-8")
        if completed.returncode:
            print(output[-6000:], flush=True)
            raise RuntimeError(f"{name} failed with exit {completed.returncode}; see {evidence / (name + '.txt')}")
        print(name + " OK", flush=True)
        return output

    versions = {"python": sys.version, "platform": platform.platform(),
                "date_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                "pobserve_source_commit": "260da92"}
    for name, command in (("p", [args.p, "--version"]), ("dotnet", ["dotnet", "--version"]),
                          ("java", [args.java, "-version"])):
        versions[name] = run("version_" + name, command).strip()
    (evidence / "versions.json").write_text(json.dumps(versions, indent=2) + "\n", encoding="utf-8")
    run("generate", [sys.executable, "tools/d3_generate.py"])
    python_output = run("python_tests", [sys.executable, "-m", "unittest", "discover", "-s", "tools", "-p", "test_d3.py", "-v"])
    python_count = re.search(r"Ran (\d+) tests? in", python_output)
    if python_count is None or int(python_count[1]) == 0:
        raise RuntimeError("Python test count not confirmed")
    run("p_compile_baseline", [args.p, "compile"], PROJECT / "ManufacturingCell")
    run("p_compile_d2", [args.p, "compile"], PROJECT / "Implementation")
    package_dir = PROJECT / "ManufacturingCell/pobserve"
    gradle = args.gradle or str(package_dir / ("gradlew.bat" if os.name == "nt" else "gradlew"))
    run("gradle_version", [gradle, "--version"], package_dir)
    run("gradle_build", [gradle, "--no-daemon", "build", "uberjar"], package_dir)
    run("pobserve_campaign", [sys.executable, "tools/d3_verify.py", "--cli", args.cli,
                              "--java", args.java, "--workers", str(args.workers)])
    # A short regression protects D2 integration without re-labelling its
    # existing 100,000-schedule evidence as a new D3 execution.
    checker = run("p_d2_regression", [args.p, "check", "-tc", "tcCellTwoTechniciansFixed",
                  "-s", "1000", "--seed", "42", "--outdir", evidence / "checker"], PROJECT / "Implementation")
    schedules = check_checker_output(checker, 1000)
    junit = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
    report_dir = evidence / "junit"
    report_dir.mkdir(exist_ok=True)
    for xml in (package_dir / "build/test-results/test").glob("TEST-*.xml"):
        tree = ET.parse(xml)
        for key in junit:
            junit[key] += int(tree.getroot().attrib.get(key, 0))
        (report_dir / xml.name).write_bytes(xml.read_bytes())
    matrix = json.loads((evidence / "results.json").read_text(encoding="utf-8"))
    calibration = json.loads((evidence / "calibration.json").read_text(encoding="utf-8"))
    manifest = json.loads((evidence / "cases.json").read_text(encoding="utf-8"))
    success = matrix["status"] == "VERIFIED" and junit["tests"] > junit["skipped"] and not (junit["failures"] or junit["errors"])
    pending_at_eof = sum(len(row["pending_at_eof"]) for row in calibration["runs"])
    summary = {"status": "D3_LOCALLY_VERIFIED_SYNTHETIC" if success else "INCOMPLETE",
               "maturity": "TECHNICALLY_VERIFIED" if success else "NOT_VERIFIED", "junit": junit,
               "python_tests": int(python_count[1]), "pobserve_checks": matrix["checks"],
               "matched": matrix["matched"], "cases": len(manifest["cases"]),
               "calibrated_bound": calibration["selected_bound"],
               "completed_adaptations_measured": calibration["completed_adaptations"],
               "calibration_pending_adaptations_at_eof": pending_at_eof,
               "d2_regression_schedules": schedules, "d2_regression_seed": 42,
               "elapsed_seconds": round(time.monotonic() - started, 2),
               "limitations": ["Os logs são sintéticos; nenhuma célula física ou implantação real foi avaliada.",
                               "O máximo da calibração é empírico e não limita todas as execuções futuras.",
                               "Logs finitos não demonstram vivacidade ilimitada; adaptações abertas ao final são registradas.",
                               "A instalação no controlador do simulador de dois técnicos é síncrona; não há prova de refinamento em relação ao modelo P."]}
    (evidence / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    with (evidence / "results.csv").open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=["case", "kind", "monitor", "expected", "observed", "matched", "exit_code"])
        writer.writeheader()
        writer.writerows({key: row[key] for key in writer.fieldnames} for row in matrix["results"])
    report = ["# D3 — Verificação de logs com PObserve", "", "Estado: **" + summary["status"] + "**.",
              "Maturidade: **" + summary["maturity"] + "**, restrita ao ambiente e corpus registrados.", "",
              "## Resultados executados", "",
              f"- {summary['cases']} cenários; {matrix['matched']}/{matrix['checks']} vereditos CLI coincidiram com a previsão.",
              f"- JUnit: {junit['tests']} testes, {junit['failures']} falhas, {junit['errors']} erros.",
              f"- Python: {summary['python_tests']} testes de consistência, reprodução dos exemplos e validação das evidências.",
              f"- Modelo base e implementação D2 compilados. Regressão D2: {schedules} schedules, seed 42, zero bugs.",
              f"Os {matrix['checks']} vereditos incluem aprovações e violações intencionais previstas; não são {matrix['checks']} execuções sem violações.", "",
              "## Calibração de R2", "",
              f"FACT: 500 seeds com um técnico e 500 com dois, 60 ticks por execução, {calibration['completed_adaptations']} adaptações concluídas.",
              f"FACT: {calibration['exceeding_original_bound']} durações excederam cinco ticks; máximo observado: {calibration['selected_bound']} ticks.",
              f"FACT: {pending_at_eof} adaptações ainda estavam abertas ao fim dos 60 ticks e não entram na distribuição de durações concluídas. Elas permanecem registradas em calibration.json.",
              f"ANALYTICAL_DECISION: B={calibration['selected_bound']} para este corpus, configurado pelo evento RUNTIME_CONFIG. Sem configuração, o monitor conserva o padrão B=5.",
              "A medição usa ADAPT_START até COMMIT/ADAPT_ABORT, incluindo o atraso do protocolo. Seed 64 excede cinco ticks; seed 299 atinge oito.", "",
              "## Dois técnicos e S4", "",
              "O corpus contém presença simultânea dos dois técnicos. A versão pré-correção reabre com uma pessoa dentro e S4 reporta a violação.",
              "A versão corrigida mantém os holders desde o pedido até a saída, cobrindo autorizações pendentes. Os sete monitores aceitam o log corrigido.", "",
              "## Falha do sistema e defeito do log", "",
              "SYSTEM_FAULT: a organização deixa de aplicar sanções; o logger registra fielmente os fatos. R1 detecta obrigação vencida.",
              "SYSTEM_FAULT: o controlador adia o commit efetivo, mantendo o bloqueio. R2 detecta atraso.",
              "LOG_DEFECT: removemos LEAVE ou SANCTION, ou duplicamos COMMIT/outcome depois da simulação correta. O comportamento real continua sendo o do log original.",
              "R1 pode produzir o mesmo alarme para sanção realmente suprimida e registro de sanção apagado. Esse alarme sozinho não identifica a causa; a proveniência das mutações está em cases.json.", "",
              "## Evidências e reprodução", "",
              "Comandos e versões: commands.json e versions.json. Corpus/hashes: cases.json e logs/. Calibração: calibration.json.",
              "Saídas reais do CLI, métricas e replay: pobserve/. Resultados tabulares: results.md, results.csv e results.json. JUnit: junit/.",
              "Consulte D3_GUIA.md para repetir a campanha.", "", "## Limitações", ""]
    report.extend("- " + limitation for limitation in summary["limitations"])
    # Keep the reviewed assumptions in every regenerated report, rather than
    # only in an edited copy of the current evidence.
    validity = (PROJECT / "ManufacturingCell/D3_PREMISSAS.md").read_text(encoding="utf-8")
    text = "\n".join(report) + "\n\n" + validity
    (evidence / "D3_RELATORIO.md").write_text(text, encoding="utf-8")
    (evidence / "D3_RELATORIO.html").write_text(
        '<!doctype html><html lang="pt-BR"><meta charset="utf-8"><title>D3 — PObserve</title>'
        '<style>body{max-width:1000px;margin:40px auto;padding:0 24px;color:#183044;font:16px/1.65 system-ui}pre{white-space:pre-wrap;font:inherit}</style>'
        '<body><pre>' + html.escape(text) + '</pre></body></html>', encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)
    return 0 if success else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cli", type=Path, required=True)
    parser.add_argument("--p", default="p")
    parser.add_argument("--java", default="java")
    parser.add_argument("--gradle")
    parser.add_argument("--workers", type=int, default=2)
    try:
        raise SystemExit(main(parser.parse_args()))
    except Exception as error:
        evidence = PROJECT / "Implementation/evidence/D3"
        evidence.mkdir(parents=True, exist_ok=True)
        (evidence / "summary.json").write_text(json.dumps({"status": "FAILED", "error": str(error)}, indent=2) + "\n", encoding="utf-8")
        raise
