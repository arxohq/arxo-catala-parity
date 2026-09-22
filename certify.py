#!/usr/bin/env python3
"""Run the evaluation documents of the Arxo scenario suites through the Lean checker.

    python3 certify.py --law /path/to/law-cli --checker /path/to/lawcheck [--all] [--record results]

For every scenario of the parity suites (default) or of every suite of the
package (--all), the runner lowers the scenario with the engine, evaluates each
of its queries into an evaluation document (`law-cli eval`), and hands the
program, the case and the document to `lawcheck`, the checker whose soundness
theorem is stated in the paper. The report counts documents accepted and
refused, proof steps proved, safety checks, defeasible-layer certificates,
admitted nodes and nodes outside the checked fragment, by reason.

Inline deadline policies of a scenario are pinned into program nodes exactly as
the engine's own test runner does (a `deadline_policy` node whose id is the
SHA-256 of the policy record), because the wire form of a case refers to a
policy by id.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from parity import FAMILY, Arxo, PACKAGE, engine_identity, law, law_command, package_parts  # noqa: E402

CHECKER: list[str] = ["lawcheck"]
HEAD = re.compile(
    r"lawcheck: узлов (\d+) · доказано: листьев (\d+), шагов (\d+), запросов (\d+) · judgment §47\.3 (\d+) · "
    r"constraint §93\.3 (\d+) · AF §274 (\d+) · PREC §276 (\d+) · safety §190 (\d+) · L1: кандидатов (\d+), "
    r"побеждений (\d+), сертификатов §181\.1 (\d+), выжило (\d+) · допущено (\d+) · вне ядра v1 (\d+)")
HEAD_KEYS = ("nodes", "leaves", "steps", "queries", "judgment", "constraint", "af", "prec", "safety",
             "l1Candidates", "l1Defeats", "l1Certificates", "l1Survivors", "admitted", "outside")


def canon(path: Path) -> None:
    result = law("canon", str(path))
    if result.returncode:
        raise SystemExit(f"canon failed for {path}: {result.stderr[-500:]}")
    path.write_bytes(result.stdout.encode("utf-8") if isinstance(result.stdout, str) else result.stdout)


def policy_id(namespace: str, policy: dict) -> str:
    digest = hashlib.sha256(json.dumps(policy, separators=(",", ":"), sort_keys=True, ensure_ascii=False)
                            .encode("utf-8")).hexdigest()
    return f"{namespace}#deadline-policy-{digest}"


def pin_policies(world: dict, case: dict) -> tuple[dict, dict]:
    """The engine's host-side pinning of inline §86 policies (DECISION-0111 §2.9)."""
    namespace = world["package"]["namespace"]
    case = json.loads(json.dumps(case))
    nodes = list(world["nodes"])
    inline = []
    if isinstance(case.get("context", {}).get("deadlinePolicy"), dict):
        inline.append(case["context"]["deadlinePolicy"])
        case["context"]["deadlinePolicy"] = policy_id(namespace, case["context"]["deadlinePolicy"])
    for profile in (case.get("contextProfiles") or {}).values():
        value = profile.get("fields", {}).get("deadlinePolicy")
        if isinstance(value, dict):
            inline.append(value)
            profile["fields"]["deadlinePolicy"] = policy_id(namespace, value)
    for policy in inline:
        pid = policy_id(namespace, policy)
        if not any(n.get("kind") == "deadline_policy" and n.get("id") == pid for n in nodes):
            nodes.append({"kind": "deadline_policy", "id": pid, "package": namespace, "policy": policy})
    return dict(world, nodes=nodes), case


def short(message: str) -> str:
    return re.sub(r"^\S+: ", "", message.strip())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--law", metavar="BINARY")
    parser.add_argument("--checker", metavar="BINARY", default="lawcheck")
    parser.add_argument("--all", action="store_true", help="every suite of the package, not only the parity suites")
    parser.add_argument("--record", type=Path, metavar="DIR")
    args = parser.parse_args()
    if args.law:
        law_command(args.law)
    CHECKER[0] = args.checker
    parts = package_parts(family=None if args.all else FAMILY)
    if not parts:
        raise SystemExit("no test parts selected")
    documents = []
    totals = collections.Counter()
    outside = collections.Counter()
    admitted = collections.Counter()
    refused = []
    errors = []
    with tempfile.TemporaryDirectory(prefix="parity-certify-") as tmp:
        work = Path(tmp)
        engine = Arxo(work)
        for k, (family, suites, calendar) in enumerate(parts):
            world_path = engine.world(calendar)
            world = json.loads(world_path.read_text(encoding="utf-8"))
            listing = work / f"part{k}.list.json"
            listing.write_text(json.dumps([str(s) for s in suites]), encoding="utf-8")
            lowered = law("lower-test", str(listing), "--lawtest-list", "--program", str(world_path),
                          "--imports", str(engine.context))
            if lowered.returncode:
                raise SystemExit(f"lower-test failed: {lowered.stderr[-800:]}")
            tests = json.loads(lowered.stdout)["document"]["tests"]
            worlds: dict[str, Path] = {}
            for n, test in enumerate(tests):
                pinned_world, case = pin_policies(world, test["case"])
                key = hashlib.sha256(json.dumps([x["id"] for x in pinned_world["nodes"]]).encode()).hexdigest()
                if key not in worlds:
                    p = work / f"world-{k}-{key[:12]}.json"
                    p.write_text(json.dumps(pinned_world, ensure_ascii=False), encoding="utf-8")
                    canon(p)
                    worlds[key] = p
                for j, step in enumerate(test.get("steps") or [{"query": test["query"]}]):
                    base = work / f"d{k}-{n:03d}-{j}"
                    base.mkdir()
                    shutil.copyfile(worlds[key], base / "ir.json")
                    (base / "case.json").write_text(json.dumps(case, ensure_ascii=False), encoding="utf-8")
                    (base / "query.json").write_text(json.dumps(step["query"], ensure_ascii=False), encoding="utf-8")
                    canon(base / "case.json")
                    canon(base / "query.json")
                    if calendar:
                        resource = law("calendar-resource", str(PACKAGE), "--ir", str(base / "ir.json"),
                                       "--case", str(base / "case.json"))
                        if resource.returncode:
                            errors.append(f"{test['title']}/{j}: calendar-resource: {resource.stderr[-300:]}")
                            continue
                        (base / "calendar.resource.json").write_text(resource.stdout, encoding="utf-8")
                    evaluated = law("eval", str(base))
                    doc = evaluated.stdout
                    if evaluated.returncode or doc.lstrip().startswith('{"error"'):
                        errors.append(f"{test['title']}/{j}: eval: {(doc or evaluated.stderr)[-300:]}")
                        continue
                    (base / "doc.json").write_text(doc, encoding="utf-8")
                    result = subprocess.run([CHECKER[0], str(base / "ir.json"), str(base / "case.json"),
                                             str(base / "doc.json"), "--verbose"], capture_output=True, text=True)
                    head = HEAD.search(result.stdout)
                    counters = dict(zip(HEAD_KEYS, map(int, head.groups()))) if head else {}
                    for line in result.stdout.splitlines():
                        line = line.strip()
                        if line.startswith("вне ядра:"):
                            outside[short(line[len("вне ядра:"):])] += 1
                        elif line.startswith("допущение:"):
                            admitted[short(line[len("допущение:"):])] += 1
                    entry = {"scenario": test["title"], "query": step["query"].get("queryId"),
                             "family": family, "calendar": calendar, "exit": result.returncode,
                             "documentHash": hashlib.sha256(doc.encode("utf-8")).hexdigest(),
                             "counters": counters}
                    if result.returncode:
                        refused.append(f"{test['title']}/{j}: {(result.stdout + result.stderr)[-400:]}")
                        entry["refusal"] = (result.stdout + result.stderr)[-400:]
                    else:
                        for key_, value in counters.items():
                            totals[key_] += value
                        totals["accepted"] += 1
                    documents.append(entry)
                    shutil.rmtree(base, ignore_errors=True)
    checker_hash = hashlib.sha256(Path(CHECKER[0]).read_bytes()).hexdigest() if Path(CHECKER[0]).exists() else None
    print(f"certify: {totals['accepted']}/{len(documents)} evaluation documents accepted by lawcheck; "
          f"{len(refused)} refused; {len(errors)} not evaluated")
    print(f"  proved: leaves {totals['leaves']}, rule steps {totals['steps']}, queries {totals['queries']}, "
          f"safety §190 {totals['safety']}; L1: candidates {totals['l1Candidates']}, defeats {totals['l1Defeats']}, "
          f"certificates {totals['l1Certificates']}, survivors {totals['l1Survivors']}; "
          f"admitted {totals['admitted']}; outside the checked fragment {totals['outside']}")
    for reason, count in outside.most_common():
        print(f"  outside: {count:4}  {reason}")
    for reason, count in admitted.most_common():
        print(f"  admitted: {count:4}  {reason}")
    for line in refused + errors:
        print("  " + line.replace("\n", " ")[:300])
    if args.record:
        args.record.mkdir(parents=True, exist_ok=True)
        out = args.record / ("certify-all.json" if args.all else "certify.json")
        out.write_text(json.dumps({
            "engine": engine_identity(), "checker": {"binary": CHECKER[0], "sha256": checker_hash},
            "documents": len(documents), "accepted": totals["accepted"], "refused": len(refused),
            "notEvaluated": errors, "totals": dict(totals), "outside": dict(outside), "admitted": dict(admitted),
            "perDocument": documents}, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  report {out}: sha256 {hashlib.sha256(out.read_bytes()).hexdigest()}")
    return 1 if (refused or errors) else 0


if __name__ == "__main__":
    raise SystemExit(main())
