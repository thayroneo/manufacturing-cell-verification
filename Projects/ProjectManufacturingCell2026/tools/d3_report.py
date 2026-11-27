"""Render the executed D3 evidence as a standalone HTML report and optional PDF."""
import argparse
import datetime as dt
import html
import json
from pathlib import Path
import re
import subprocess
import tempfile

PROJECT = Path(__file__).resolve().parents[1]


def render(evidence, browser=None):
    summary = json.loads((evidence / "summary.json").read_text(encoding="utf-8"))
    if summary["status"] != "D3_LOCALLY_VERIFIED_SYNTHETIC":
        raise RuntimeError("Only executed, successful evidence can be rendered as a completed report")
    matrix = json.loads((evidence / "results.json").read_text(encoding="utf-8"))
    markdown = (evidence / "D3_RELATORIO.md").read_text(encoding="utf-8")
    versions = json.loads((evidence / "versions.json").read_text(encoding="utf-8"))
    executed = dt.datetime.fromisoformat(versions["date_utc"])
    report_date = executed.astimezone(dt.timezone(dt.timedelta(hours=-3))).strftime("%d/%m/%Y")

    def inline(value):
        value = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", html.escape(value))
        return re.sub(r"`([^`]+)`", r"<code>\1</code>", value)

    body = []
    listing = False
    table = False
    for line in markdown.splitlines():
        if listing and not line.startswith("- "):
            body.append("</ul>")
            listing = False
        if table and not line.startswith("|"):
            body.append("</tbody></table>")
            table = False
        if line.startswith("|"):
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
                continue
            if not table:
                body.append('<table class="assumptions"><thead><tr>'
                            + "".join("<th>" + inline(cell) + "</th>" for cell in cells)
                            + "</tr></thead><tbody>")
                table = True
            else:
                body.append("<tr>" + "".join("<td>" + inline(cell) + "</td>" for cell in cells) + "</tr>")
            continue
        if line.startswith("# "):
            body.append("<h1>" + inline(line[2:]) + "</h1>")
        elif line.startswith("## "):
            body.append("<h2>" + inline(line[3:]) + "</h2>")
        elif line.startswith("### "):
            body.append("<h3>" + inline(line[4:]) + "</h3>")
        elif line.startswith("- "):
            if not listing:
                body.append("<ul>")
                listing = True
            body.append("<li>" + inline(line[2:]) + "</li>")
        elif line.strip():
            body.append("<p>" + inline(line) + "</p>")
    if listing:
        body.append("</ul>")
    if table:
        body.append("</tbody></table>")
    body.append('<h2 class="break">Matriz dos vereditos executados</h2><table><thead><tr>'
                '<th>Cenário</th><th>Monitor</th><th>Previsto</th><th>Observado</th></tr></thead><tbody>')
    for row in matrix["results"]:
        body.append("<tr>" + "".join("<td>" + html.escape(str(row[key])) + "</td>"
                                    for key in ("case", "monitor", "expected", "observed")) + "</tr>")
    body.append("</tbody></table>")
    css = """
    @page { size:A4; margin:17mm; }
    * {box-sizing:border-box} body {max-width:1060px;margin:36px auto;padding:0 28px;
    font:15px/1.6 'Segoe UI',sans-serif;color:#183044;background:#fff}
    .eyebrow {font-size:12px;letter-spacing:2px;color:#31756b;font-weight:700}
    h1 {font-size:30px;line-height:1.2;margin:12px 0 22px;color:#123454}
    h2 {font-size:20px;color:#123454;border-bottom:1px solid #cfdde4;padding-bottom:6px;
    margin-top:30px;break-after:avoid} p,li {overflow-wrap:anywhere}
    h3 {font-size:17px;color:#123454;margin-top:24px;break-after:avoid}
    li {margin-bottom:7px} code {font-size:.95em}
    .cards {display:flex;gap:15px;margin-bottom:25px}.card {flex:1;background:#edf5f6;
    border-left:4px solid #287a70;padding:15px}.card strong {display:block;font-size:28px}
    table {width:100%;border-collapse:collapse;font-size:10px;line-height:1.4}
    th {background:#123454;color:#fff;text-align:left} td,th {padding:7px 5px;border:1px solid #d6e1e7}
    tr {break-inside:avoid} tbody tr:nth-child(even) {background:#f3f7f9}
    thead {display:table-header-group}.assumptions {table-layout:fixed}
    .assumptions th:first-child {width:39%}.assumptions th:nth-child(2) {width:21%}
    .assumptions th:nth-child(3) {width:22%}.assumptions th:nth-child(4) {width:18%}
    .assumptions td {vertical-align:top;overflow-wrap:anywhere}
    .note {font-size:13px;color:#526b7b}.break {break-before:page}
    @media print {body {margin:0;padding:0;font-size:10.5pt}.cards {break-inside:avoid}h1 {font-size:24pt}
    h2 {font-size:15pt} h3 {font-size:12pt}li {break-inside:avoid}
    .card strong {font-size:23pt}table {font-size:8pt}}
    """
    cards = (f'<div class="cards"><div class="card"><strong>{summary["matched"]}/{summary["pobserve_checks"]}</strong>'
             f'Vereditos PObserve</div><div class="card"><strong>{summary["junit"]["tests"]}</strong>'
             f'Testes JUnit aprovados</div><div class="card"><strong>{summary["calibrated_bound"]} ticks</strong>'
             'Limite empírico de R2</div></div>')
    document = ('<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
                '<title>D3 — Relatório de verificação com PObserve</title><style>' + css + '</style></head><body>'
                '<div class="eyebrow">MANUFACTURING CELL · ENTREGA D3 · ' + report_date + '</div>' + cards
                + '\n'.join(body) + '<p class="note">Corpus sintético. Evidências e comandos completos acompanham este relatório.</p></body></html>')
    target = evidence / "D3_RELATORIO.html"
    target.write_text(document, encoding="utf-8")
    print("HTML report:", target)
    if browser:
        profile = Path(tempfile.gettempdir()).resolve() / "manufacturing-d3-report-browser"
        profile.mkdir(exist_ok=True)
        pdf = evidence / "D3_RELATORIO.pdf"
        command = [str(browser), "--headless", "--disable-gpu", "--no-first-run",
                   "--no-default-browser-check", "--user-data-dir=" + str(profile),
                   "--no-pdf-header-footer", "--print-to-pdf=" + str(pdf), target.as_uri()]
        completed = subprocess.run(command, capture_output=True, timeout=60)
        if completed.returncode or not pdf.is_file() or pdf.stat().st_size < 1000:
            raise RuntimeError("Browser PDF export failed: " + completed.stderr.decode("utf-8", errors="replace"))
        print("PDF report:", pdf, "bytes:", pdf.stat().st_size)
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, default=PROJECT / "Implementation/evidence/D3")
    parser.add_argument("--browser", type=Path)
    args = parser.parse_args()
    render(args.evidence.resolve(), args.browser)
