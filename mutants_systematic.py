#!/usr/bin/env python3
"""Systematic, operator-based mutation of the Arxo model, run against all its scenarios.

    python3 mutants_systematic.py --law /path/to/law-cli [--record results] [--limit N]

Operators, applied to every applicable line of `modules/**/*.law` (one mutant per site):

    CMP    flip a comparison in a `when` premise: > <-> >=, < <-> <=
    DROP   delete one `when …;` premise
    NEG    remove `not ` from a negated premise, or add it to a positive one
    CONST  perturb a numeric constant on a `let`/`when`/`assert` line: integers +1,
           decimals -0.1 (0.8 -> 0.7)
    UNIT   business_day <-> calendar_day
    UNLESS delete one `unless …;` defeater clause (multi-line)

Each mutant is lowered with the engine and run against every scenario suite of the
package. Outcomes: KILLED (>= 1 scenario fails), SURVIVED (none fails), REJECTED
(the compiler refuses the mutant). Survivors are listed for manual classification
(equivalent mutant versus untested behaviour). No claim of completeness: the
operator set is the one above and nothing else.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from parity import Arxo, PACKAGE, engine_identity, law_command, package_parts  # noqa: E402

WHEN = re.compile(r"^(\s*)when (.*);\s*$")
UNLESS = re.compile(r"^\s*unless ")
NUM_INT = re.compile(r"(?<![\w.])(\d+)(?![\w.])")
NUM_DEC = re.compile(r"(?<![\w.])(\d+\.\d+)(?![\w.])")
CMP_OPS = ((">=", ">"), (">", ">="), ("<=", "<"), ("<", "<="))


def sites(path: Path) -> list[tuple[str, int, list[str], str]]:
    """(operator, line index, mutated lines, description) for every site of one file."""
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    out = []
    for i, line in enumerate(lines):
        if line.lstrip().startswith("//"):
            continue
        m = WHEN.match(line)
        if m:
            body = m.group(2)
            for a, b in CMP_OPS:
                pattern = rf"(?<![<>=!]){re.escape(a)}(?![=])"
                if re.search(pattern, body):
                    new = lines[:]
                    new[i] = re.sub(pattern, b, line, count=1)
                    if new[i] != line:
                        out.append(("CMP", i, new, f"{path.name}:{i+1} {a} -> {b}"))
                        break
            new = lines[:]
            del new[i]
            out.append(("DROP", i, new, f"{path.name}:{i+1} drop premise `{body[:50]}`"))
            new = lines[:]
            if body.startswith("not "):
                new[i] = line.replace("when not ", "when ", 1)
                out.append(("NEG", i, new, f"{path.name}:{i+1} remove not"))
            elif re.match(r"^[a-z_]+\(", body):
                new[i] = line.replace("when ", "when not ", 1)
                out.append(("NEG", i, new, f"{path.name}:{i+1} add not"))
            if "business_day" in body or "calendar_day" in body:
                new = lines[:]
                new[i] = (line.replace("business_day", "calendar_day") if "business_day" in body
                          else line.replace("calendar_day", "business_day"))
                out.append(("UNIT", i, new, f"{path.name}:{i+1} unit swap"))
        if m or line.lstrip().startswith(("let ", "assert ")):
            for num in NUM_DEC.finditer(line):
                val = num.group(1)
                new = lines[:]
                perturbed = str(round(float(val) - 0.1, 3)) if float(val) > 0.1 else str(round(float(val) + 0.1, 3))
                new[i] = line[:num.start(1)] + perturbed + line[num.end(1):]
                out.append(("CONST", i, new, f"{path.name}:{i+1} {val} -> {perturbed}"))
            masked = re.sub(r"\d+\.\d+", lambda x: " " * len(x.group(0)), line)
            for num in NUM_INT.finditer(masked):
                val = int(num.group(1))
                if val == 0:
                    continue
                new = lines[:]
                new[i] = line[:num.start(1)] + str(val + 1) + line[num.end(1):]
                out.append(("CONST", i, new, f"{path.name}:{i+1} {val} -> {val + 1}"))
            if "business_day" in line and not m:
                new = lines[:]
                new[i] = line.replace("business_day", "calendar_day")
                out.append(("UNIT", i, new, f"{path.name}:{i+1} unit swap"))
        if UNLESS.match(line):
            j = i
            while j < len(lines) and not lines[j].rstrip().endswith(";"):
                j += 1
            new = lines[:i] + lines[j + 1:]
            out.append(("UNLESS", i, new, f"{path.name}:{i+1} drop defeater"))
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--law", metavar="BINARY")
    parser.add_argument("--record", type=Path, metavar="DIR")
    parser.add_argument("--limit", type=int, metavar="N", help="run at most N mutants (for smoke runs)")
    parser.add_argument("--operators", default="CMP,DROP,NEG,CONST,UNIT,UNLESS")
    args = parser.parse_args()
    if args.law:
        law_command(args.law)
    ops = set(args.operators.split(","))
    parts = package_parts()
    plan = []
    for path in sorted(PACKAGE.glob("modules/**/*.law")):
        for op, i, new, what in sites(path):
            if op in ops:
                plan.append((path.relative_to(PACKAGE), op, new, what))
    if args.limit:
        plan = plan[:args.limit]
    print(f"{len(plan)} mutants planned over {len(set(p[0] for p in plan))} files")
    outcomes = []
    counts = {"KILLED": 0, "SURVIVED": 0, "REJECTED": 0}
    with tempfile.TemporaryDirectory(prefix="parity-sysmut-") as tmp:
        for n, (rel, op, new_lines, what) in enumerate(plan):
            work = Path(tmp) / f"m{n:04d}"
            source = work / "package"
            shutil.copytree(PACKAGE, source, ignore=shutil.ignore_patterns("tests", "sources", "analysis", "__pycache__"))
            (source / rel).write_text("".join(new_lines), encoding="utf-8")
            try:
                engine = Arxo(work, package=source)
            except SystemExit:
                counts["REJECTED"] += 1
                outcomes.append({"id": n, "op": op, "site": what, "outcome": "REJECTED"})
                shutil.rmtree(work, ignore_errors=True)
                continue
            failing = 0
            example = None
            for k, (family, suites, calendar) in enumerate(parts):
                report = engine.test(suites, calendar, f"{n}-{k}")
                for item in report["tests"]:
                    if not item["passed"]:
                        failing += 1
                        example = example or item["title"]
            outcome = "KILLED" if failing else "SURVIVED"
            counts[outcome] += 1
            outcomes.append({"id": n, "op": op, "site": what, "outcome": outcome, "failing": failing, "example": example})
            if outcome == "SURVIVED":
                print(f"SURVIVED {op} {what}", flush=True)
            shutil.rmtree(work, ignore_errors=True)
    by_op: dict = {}
    for o in outcomes:
        by_op.setdefault(o["op"], {"KILLED": 0, "SURVIVED": 0, "REJECTED": 0})[o["outcome"]] += 1
    print(f"systematic mutants {len(outcomes)}: killed {counts['KILLED']}, survived {counts['SURVIVED']}, rejected {counts['REJECTED']}")
    for op, c in sorted(by_op.items()):
        print(f"  {op:7} killed {c['KILLED']:3} survived {c['SURVIVED']:3} rejected {c['REJECTED']:3}")
    if args.record:
        args.record.mkdir(parents=True, exist_ok=True)
        (args.record / "mutants-systematic.json").write_text(json.dumps(
            {"engine": engine_identity(), "total": len(outcomes), **counts, "byOperator": by_op, "mutants": outcomes},
            ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
