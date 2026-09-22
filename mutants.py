#!/usr/bin/env python3
"""Mutation check of the Arxo model: every targeted loss of meaning must be caught.

    python3 mutants.py                 # all 20 mutants
    python3 mutants.py --only M01 M09  # a subset
    python3 mutants.py --record results

Each mutant is a one-line change to a source file of the package under `corpus/laws/kz/regulators/vred-ts/` (a threshold, a
comparison, a dropped condition). The mutated package is lowered with the engine
and every scenario suite of the package is run against it. A mutant is KILLED
when at least one scenario fails, SURVIVED when none does, REJECTED when the
compiler refuses the mutated source. The exit code is 1 if any mutant survives.

The anchors are exact source strings and must occur exactly once: a stale anchor
stops the run instead of silently skipping a mutation.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from parity import Arxo, PACKAGE, law_command, package_parts  # noqa: E402

MUTANTS = [
    # id, file, what was, what replaces it, what is lost
    ("M01", "modules/vyplata/gibel-ts.law", "when costs > porog_gibeli;", "when costs >= porog_gibeli;",
     "cl. 9: 'exceed' becomes 'not less than' (the 80 % boundary itself)"),
    ("M02", "modules/vyplata/gibel-ts.law", "let porog_gibeli: Money = market * 0.8;",
     "let porog_gibeli: Money = market * 0.7;", "cl. 9: threshold 80 % becomes 70 %"),
    ("M03", "modules/vyplata/gibel-ts.law", "let vyplata: Money = market - salvage;",
     "let vyplata: Money = market;", "cl. 9: payment without deduction of usable remains"),
    ("M04", "modules/vyplata/gibel-ts.law", "        when not ostatki_peredany_v_sobstvennost_strakhovshchika(r);\n",
     "", "cl. 9: second alternative without the established negation of transfer"),
    ("M05", "modules/detali/otsenka.law", "when distance <= 15000 km;", "when distance < 15000 km;",
     "cl. 10 (1): 'does not exceed' becomes strictly less (15,000 km boundary)"),
    ("M06", "modules/detali/otsenka.law", "when distance <= 20000 km;", "when distance < 20000 km;",
     "cl. 10 (2): 20,000 km boundary"),
    ("M07", "modules/detali/otsenka.law", "        when nakhoditsya_na_garantiynom_obsluzhivanii(v);\n", "",
     "cl. 10 (2): warranty-service condition lost"),
    ("M08", "modules/detali/otsenka.law", "        when detal_ne_podvergalas_remontu(d);\n", "",
     "cl. 10: 'not previously repaired' condition lost"),
    ("M09", "modules/otchet/sroki-i-vozrazheniya.law", "assert srok_predostavleniya_otcheta(5 business_day);",
     "assert srok_predostavleniya_otcheta(6 business_day);", "cl. 3: five working days become six"),
    ("M10", "modules/otchet/sroki-i-vozrazheniya.law", "assert srok_otmetki_poterpevshego(3 business_day);",
     "assert srok_otmetki_poterpevshego(3 calendar_day);", "cl. 3: working days become calendar days"),
    ("M11", "modules/otchet/sroki-i-vozrazheniya.law",
     "    unless UproshchennoeOformlenie when uproshchennoe_oformlenie_proisshestviya(r)\n"
     "        and srok_predostavleniya_otcheta(limit)\n"
     "        and osmotr_osushchestvlen_strakhovshchikom(r: r, day: day);\n",
     "", "cl. 3-1: the simplified-procedure defeater of the report deadline lost"),
    ("M12", "modules/otchet/sroki-i-vozrazheniya.law", "        when got > due;\n", "        when got >= due;\n",
     "cl. 3: a report on the last day of the period counted as late"),
    ("M13", "modules/raschet/otsenshchiki.law", "        when n >= 2;\n", "        when n >= 1;\n",
     "cl. 4-1: one appraiser suffices"),
    ("M14", "modules/detali/otsenka.law",
     "    unless DetalBezIznosa when detal_otsenivaetsya_bez_iznosa(d)\n"
     "        and stoimost_detali_s_uchetom_iznosa(d: d, amount: amount);\n", "",
     "annex 3 footnote: depreciation also applied in the cases of cl. 10 (two amounts)"),
    ("M15", "modules/otchet/oformlenie.law", '        when round(amount, 0, "HALF_UP") == amount;\n', "",
     "annex 3 cl. 2: rounding-to-tenge check lost"),
    ("M16", "modules/osmotr/akt.law", "        when akt_vin(a: a, vin: _);\n", "",
     "annex 2 cl. 4.1: an inspection act without VIN counted as complete"),
    ("M17", "modules/osmotr/provedenie.law", "        when zayavlenie_o_dopolnitelnom_osmotre(z: z, r: r);\n", "",
     "cl. 2 part 4: additional inspection without its own application"),
    ("M18", "modules/osmotr/usloviya.law", "        when not dokumenty_o_povrezhdeniyakh_v_dtp_predstavleny(r);\n", "",
     "cl. 7: inadmissibility without the established absence of documents"),
    ("M19", "modules/osmotr/usloviya.law", "        when fotosemka_povrezhdeniy_provodima(r);\n", "",
     "cl. 7: photography condition lost"),
    ("M20", "modules/otchet/oformlenie.law", "        when pechat_otsutstvuet(o);\n", "        when otchet_podpis_utverzhdayushchego(o: o, fio: _);\n",
     "annex 3 cl. 1: certification by one signature without the established absence of a seal"),
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--only", nargs="*", default=[])
    parser.add_argument("--law", metavar="BINARY")
    parser.add_argument("--record", type=Path, metavar="DIR")
    args = parser.parse_args()
    if args.law:
        law_command(args.law)
    selected = [m for m in MUTANTS if not args.only or m[0] in args.only]
    parts = package_parts()
    outcomes = []
    survivors = rejected = 0
    with tempfile.TemporaryDirectory(prefix="parity-mutants-") as tmp:
        for mid, filename, old, new, what in selected:
            work = Path(tmp) / mid
            source = work / "package"
            shutil.copytree(PACKAGE, source, ignore=shutil.ignore_patterns("tests", "__pycache__"))
            path = source / filename
            text = path.read_text(encoding="utf-8")
            if text.count(old) != 1:
                raise SystemExit(f"{mid}: anchor occurs {text.count(old)} times in {filename}: {old[:60]!r}")
            path.write_text(text.replace(old, new), encoding="utf-8")
            try:
                engine = Arxo(work, package=source)
            except SystemExit as refusal:
                rejected += 1
                outcomes.append({"id": mid, "what": what, "outcome": "REJECTED", "detail": str(refusal)[-300:]})
                print(f"REJECTED {mid} ({what}): the compiler refused the mutant")
                continue
            killed_by = []
            # The suites are read from the ORIGINAL package: the scenarios are the
            # oracle, the mutant is the subject.
            for n, (family, suites, calendar) in enumerate(parts):
                report = engine.test(suites, calendar, f"{mid}-{n}")
                killed_by += [item["title"] for item in report["tests"] if not item["passed"]]
            if killed_by:
                outcomes.append({"id": mid, "what": what, "outcome": "KILLED", "failing": len(killed_by),
                                 "example": killed_by[0]})
                print(f"KILLED   {mid} ({what}): {len(killed_by)} scenario failures, e.g. {killed_by[0]}")
            else:
                survivors += 1
                outcomes.append({"id": mid, "what": what, "outcome": "SURVIVED"})
                print(f"SURVIVED {mid} ({what}): no scenario failed")
    killed = len(selected) - survivors - rejected
    print(f"mutants {len(selected)}: killed {killed}, survived {survivors}, rejected by the compiler {rejected}")
    if args.record:
        args.record.mkdir(parents=True, exist_ok=True)
        (args.record / "mutants.json").write_text(json.dumps(
            {"total": len(selected), "killed": killed, "survived": survivors, "rejected": rejected,
             "mutants": outcomes}, ensure_ascii=False, indent=2), encoding="utf-8")
    return 1 if survivors else 0


if __name__ == "__main__":
    raise SystemExit(main())
