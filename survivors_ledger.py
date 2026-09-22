#!/usr/bin/env python3
"""Machine-readable ledger of the surviving systematic mutants with their class.

    python3 survivors_ledger.py results/mutants-systematic.json > results/survivors-classified.csv

Classes (paper, Section "Systematic mutations"):
    binding      a premise that binds an entity to the case's single vehicle, calculation or report
    element      one element of a conjunctive document-completeness rule (annexes 1-3)
    co-asserted  a premise every scenario reaching the rule asserts together with the others
    untested     a path no scenario takes
    equivalent   equivalent on the queried outputs
The `diff` column is the mutated line as the operator produced it.
"""
import csv, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mutants_systematic import sites  # noqa: E402
from parity import PACKAGE  # noqa: E402

CLASSES = {
    "binding": {"otsenka.law": [68, 84], "gibel-ts.law": [66], "oformlenie.law": [210, 211],
                "organizatsiya.law": [23, 24], "otsenshchiki.law": [38, 39]},
    "element": {"akt.law": "*", "oformlenie.law": "*", "zayavlenie.law": [24, 25]},
    "co-asserted": {"usloviya.law": [28, 29, 30, 31, 32, 34], "organizatsiya.law": [25, 26, 38, 39],
                    "otsenshchiki.law": [40, 41], "provedenie.law": [65, 66], "otsenka.law": [85, 90, 107],
                    "gibel-ts.law": [67, 80], "oplata-remonta.law": [22]},
    "untested": {"sroki-i-vozrazheniya.law": [75, 76, 116, 203]},
    "equivalent": {"otsenshchiki.law": [60], "usloviya.law": [45]},
}
RATIONALE = {
    "binding": "every scenario holds one vehicle, one calculation and one report; a rule that pairs entities across cases has nothing to pair with",
    "element": "the scenarios exercise a complete document and specific omissions, not each element omitted singly",
    "co-asserted": "every scenario reaching the rule asserts this premise together with the others",
    "untested": "no scenario takes this path (disagreement with reasons; simplified-procedure defeater of the response period; report never provided)",
    "equivalent": "the strict rule for two or more appraisers dominates the defeasible denial; the sibling clause-7 rule establishes the same conclusion",
}


def classify(site: str) -> str:
    name, rest = site.split(":", 1)
    line = int(rest.split(" ")[0])
    for cls in ("binding", "equivalent", "untested", "co-asserted", "element"):
        lines = CLASSES[cls].get(name)
        if lines == "*" or (lines and line in lines):
            return cls
    raise SystemExit(f"unclassified survivor {site}")


def main() -> int:
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    plan = []
    for path in sorted(PACKAGE.glob("modules/**/*.law")):
        plan.extend(sites(path))
    writer = csv.writer(sys.stdout)
    writer.writerow(["id", "op", "site", "class", "rationale", "diff"])
    for m in data["mutants"]:
        if m["outcome"] != "SURVIVED":
            continue
        op, i, new, what = plan[m["id"]]
        assert what == m["site"], (what, m["site"])
        original = Path(next(p for p in PACKAGE.glob("modules/**/*.law") if p.name == what.split(":")[0]))
        old = original.read_text(encoding="utf-8").splitlines(keepends=True)
        diff = ("-" + old[i].strip()) if op == "DROP" or op == "UNLESS" else ("-" + old[i].strip() + " / +" + new[i].strip())
        cls = classify(m["site"])
        writer.writerow([m["id"], op, m["site"], cls, RATIONALE[cls], diff])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
