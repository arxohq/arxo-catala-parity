#!/usr/bin/env python3
"""Mutation matrix for the compared computable core, by corpus.

    python3 mutants_core.py --law /path/to/law-cli [--record results] [--limit N] [--seeds 1,2] [--count 120]

The systematic operators of `mutants_systematic.py` are applied as there, but
only mutants whose site lies in the dependency cone of the compared outputs are
run (the rules that produce, directly or through other rules, a predicate the
parity suites query). Each compiled core mutant is run against four corpora:

    reference   the 65 shared reference cases (the parity suites)
    random      the random cases of the property mode (default 120 per seed, seeds 1 and 2),
                rendered for the mutant and checked against the Python oracle's expectations
    authored    the 104 authored scenarios of the package (every other suite)
    all         every scenario of the package (reference + authored)

Outcomes per corpus: KILLED (at least one scenario fails) or SURVIVED. Mutants
the compiler refuses are counted as REJECTED once. Survivor classes come from
`results/survivors-classified.csv` when present.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import re
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from parity import (CLIR_DIR, FAMILY, Arxo, PACKAGE, Reference, engine_identity, law_command,  # noqa: E402
                    load_calendar, load_cases, package_parts, random_case, render_suites)
from mutants_systematic import sites  # noqa: E402

RULE = re.compile(r"^\s*rule (\w+)\(")
HEAD = re.compile(r"^\s*then (?:not )?([a-z_0-9]+)\(")
BODY = re.compile(r"^\s*(?:when|unless \w+ when) (?:not )?([a-z_0-9]+)\(")
ASSERT = re.compile(r"^\s*assert ([a-z_0-9]+)\(")
QUERIED = re.compile(r"evaluate (?:truth\(|collect [^;]*?where (?:[\w.]+::)?)([a-z_0-9]+)\(")


def rule_graph(package: Path) -> tuple[dict[tuple[str, int], str], dict[str, set[str]], dict[str, str]]:
    """(file, line index) -> enclosing rule; rule -> body predicates; rule -> head predicate."""
    enclosing: dict[tuple[str, int], str] = {}
    bodies: dict[str, set[str]] = {}
    heads: dict[str, str] = {}
    for path in sorted(package.glob("modules/**/*.law")):
        current = None
        depth = 0
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
            m = RULE.match(line)
            if m:
                current = f"{path.name}:{m.group(1)}"
                depth = 0
                bodies.setdefault(current, set())
            if current:
                enclosing[(path.name, i)] = current
                b = BODY.match(line)
                if b:
                    bodies[current].add(b.group(1))
                h = HEAD.match(line)
                if h:
                    heads[current] = h.group(1)
                depth += line.count("{") - line.count("}")
                if depth <= 0 and "}" in line and not RULE.match(line):
                    current = None
            a = ASSERT.match(line)
            if a and not current:
                enclosing[(path.name, i)] = f"{path.name}:assert:{a.group(1)}"
                heads[f"{path.name}:assert:{a.group(1)}"] = a.group(1)
                bodies.setdefault(f"{path.name}:assert:{a.group(1)}", set())
    return enclosing, bodies, heads


def core_rules(package: Path) -> tuple[set[str], set[str]]:
    """Rules in the dependency cone of the predicates the parity suites query."""
    queried: set[str] = set()
    for suite in (package / "tests" / "parity").glob("*.lawtest"):
        queried |= set(QUERIED.findall(suite.read_text(encoding="utf-8")))
    _, bodies, heads = rule_graph(package)
    cone = set(queried)
    rules: set[str] = set()
    changed = True
    while changed:
        changed = False
        for rule, head in heads.items():
            if head in cone and rule not in rules:
                rules.add(rule)
                cone |= bodies[rule]
                changed = True
    return rules, queried


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--law", metavar="BINARY")
    parser.add_argument("--record", type=Path, metavar="DIR")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--seeds", default="1,2")
    parser.add_argument("--count", type=int, default=120)
    parser.add_argument("--classes", type=Path, default=Path(__file__).resolve().parent / "results" / "survivors-classified.csv")
    args = parser.parse_args()
    if args.law:
        law_command(args.law)
    rules, queried = core_rules(PACKAGE)
    enclosing, _, _ = rule_graph(PACKAGE)
    classes: dict[str, str] = {}
    if args.classes.exists():
        with args.classes.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                classes[f"{row['op']} {row['site']}"] = row["class"]
    plan = []
    for path in sorted(PACKAGE.glob("modules/**/*.law")):
        for op, i, new, what in sites(path):
            rule = enclosing.get((path.name, i))
            if rule in rules:
                plan.append((path.relative_to(PACKAGE), op, new, what, rule))
    print(f"{len(rules)} rules in the cone of {len(queried)} queried predicates; {len(plan)} core mutants planned")
    if args.limit:
        plan = plan[:args.limit]
    seeds = [int(s) for s in args.seeds.split(",") if s]
    cases = load_cases()
    calendar = load_calendar(cases)
    ref = Reference(calendar)
    scopes = ["Gibel", "StoimostDetali", "VyborOtsenshchikov", "SrokiPunkta3"]
    random_suites: dict[int, dict[str, str]] = {}
    for seed in seeds:
        rng = random.Random(seed)
        generated = []
        for n in range(args.count):
            scope = scopes[n % len(scopes)]
            inputs = random_case(rng, scope)
            generated.append({"id": f"P{n:04d}", "scope": scope, "source": "property", "inputs": inputs,
                              "expected": ref.compute(scope, inputs), "rationale": f"seed={seed}"})
        random_suites[seed] = render_suites({"cases": generated})
    parts = package_parts()
    reference_parts = [p for p in parts if p[0] == FAMILY]
    authored_parts = [p for p in parts if p[0] != FAMILY]
    outcomes = []
    with tempfile.TemporaryDirectory(prefix="parity-core-") as tmp:
        root = Path(tmp)
        (root / "corpus" / "clir").mkdir(parents=True)
        for name in ("kz-official-2026.calendar.json", "kz-official-calendar-2026.lawir.json"):
            shutil.copyfile(CLIR_DIR / name, root / "corpus" / "clir" / name)
        (root / "tests").mkdir()
        for seed, suites in random_suites.items():
            for name, text in suites.items():
                (root / "tests" / f"seed{seed}-{name}").write_text(text, encoding="utf-8")
        for n, (rel, op, new_lines, what, rule) in enumerate(plan):
            work = root / f"m{n:04d}"
            source = work / "package"
            shutil.copytree(PACKAGE, source, ignore=shutil.ignore_patterns("tests", "analysis", "__pycache__"))
            (source / rel).write_text("".join(new_lines), encoding="utf-8")
            entry = {"id": n, "op": op, "site": what, "rule": rule, "class": classes.get(f"{op} {what}")}
            try:
                engine = Arxo(work, package=source)
            except SystemExit as refusal:
                entry.update(outcome="REJECTED", detail=str(refusal)[-200:])
                outcomes.append(entry)
                shutil.rmtree(work, ignore_errors=True)
                continue

            def failing(parts_: list, tag: str) -> int:
                count = 0
                for k, (_family, suites, cal) in enumerate(parts_):
                    report = engine.test(suites, cal, f"{tag}-{k}")
                    count += sum(1 for item in report["tests"] if not item["passed"])
                return count

            by_corpus = {"reference": failing(reference_parts, "ref"), "authored": failing(authored_parts, "aut")}
            rnd = 0
            for seed, suites in random_suites.items():
                for name in suites:
                    report = engine.test([root / "tests" / f"seed{seed}-{name}"], "sroki" in name, f"rnd{seed}-{name}")
                    rnd += sum(1 for item in report["tests"] if not item["passed"])
            by_corpus["random"] = rnd
            by_corpus["all"] = by_corpus["reference"] + by_corpus["authored"]
            entry.update(outcome={c: ("KILLED" if v else "SURVIVED") for c, v in by_corpus.items()}, failing=by_corpus)
            outcomes.append(entry)
            print(f"{n:3} {op:6} {what[:60]:60} ref {by_corpus['reference']:3} rnd {rnd:3} aut {by_corpus['authored']:3}", flush=True)
            shutil.rmtree(work, ignore_errors=True)
    compiled = [o for o in outcomes if o["outcome"] != "REJECTED"]
    rejected = len(outcomes) - len(compiled)
    matrix = {}
    for corpus in ("reference", "random", "authored", "all"):
        killed = sum(1 for o in compiled if o["outcome"][corpus] == "KILLED")
        survivors = [o for o in compiled if o["outcome"][corpus] == "SURVIVED"]
        equivalent = sum(1 for o in survivors if o["class"] == "equivalent")
        matrix[corpus] = {"killed": killed, "survived": len(survivors) - equivalent, "equivalent": equivalent}
    print(f"core mutants {len(outcomes)}: compiled {len(compiled)}, rejected {rejected}")
    for corpus, row in matrix.items():
        print(f"  {corpus:10} killed {row['killed']:3} survived {row['survived']:3} equivalent {row['equivalent']:3}")
    if args.record:
        args.record.mkdir(parents=True, exist_ok=True)
        (args.record / "mutants-core.json").write_text(json.dumps(
            {"engine": engine_identity(), "coreRules": sorted(rules), "queried": sorted(queried),
             "total": len(outcomes), "compiled": len(compiled), "rejected": rejected, "matrix": matrix,
             "randomCount": args.count, "seeds": seeds, "mutants": outcomes}, ensure_ascii=False, indent=2),
            encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
