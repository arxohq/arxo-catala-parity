# Formalization Status

**Status:** formalized, verified, and cross-checked against an independent implementation
as of September 9, 2026 (DECISION-0184, pilot completion criteria 1–4).

The package covers all thirteen clauses of the Rules (1, 2, 3, 3-1, 4, 4-1, 5–11)
and three annexes down to their sub-clauses. Teaching cases over the canon are a nested
case package [examples/gibel-i-detali](examples/gibel-i-detali/README.md):
seven cases, seventeen `law ask` questions, checked by `check.py` (09.09.2026). The
"source unit → requirement → implementation → scenarios → reference → status" matrix is
[COVERAGE-MATRIX.md](COVERAGE-MATRIX.md), generated and machine-verified by
`tools/coverage_matrix.py` from `analysis/coverage-matrix.json` (quotations are
substrings of the pinned text, rule/test/case names are checked to exist, coverage is
checked both ways). A report on the comparison with Catala, the actual results, and
open questions is [tools/catala/REPORT.md](tools/catala/REPORT.md).

## Question Catalog (10.09.2026, DECISION-0190)

Set up: `analysis/questions.json` (41 §172 query-template cards across six tasks,
6 boundaries with a reason type, 13 internal links), `package-info.json` (purpose, six
constraints verbatim, examples), and the generated [QUESTIONS.md](QUESTIONS.md). The
`check_package_questions.py` gate: 43 derived predicates and 12 norms are closed both
ways, parameters follow the CLIR declaration, every named test executes its card's
query, constraints ↔ boundaries are checked both ways, freshness, ratchet; canary —
6 out of 6 forgeries caught. The DECISION-0189 profile checks the catalog against a
private CLIR snapshot; the MCP lists the cards under the `catalog: "questions"` mode.
A card is not an answer (see README).

## Layout: Subject Modules (09.09.2026)

Norms are organized by TASK, not by file number: `modules/<area>/` — calculation,
inspection, payout, parts, report, depreciation; `tests/<area>/` mirrors them,
`tests/integration/` holds scenarios spanning several areas, `tests/regression/` is
the `vred_ts` family, `tests/parity/` is the generated comparison with Catala. The
entry point for readers is [README.ru.md](README.ru.md) (a "task → file → inputs →
results → scenarios" table). The convention is `docs/PACKAGE-LAYOUT.ru.md`, section
"Subject Layout of Norms".

Module boundaries are ORGANIZATIONAL: there is one package, one namespace, the
language does not introduce scopes within a package. The move was verified by byte
equality of the CLIR before and after: `corpus/clir/kz-vred-ts.lawir.json` did not
change by a single byte, and with it neither did StableId, public symbols, `@source`
anchors, or any of the §209 hashes.

## Date and Time of the Inspection Report — `Instant` (10.09.2026, night)

The boundary "time of day is not stored in the model" has been lifted as erroneous:
it attributed to the language the absence of an instant type for case facts, whereas
`Instant` is part of the v1 slice (the slice excludes `LocalTime` and
`OffsetDateTime`). Both fields of annex 2 cl. 1 are now `moment: Instant`, as the
text requires ("the date, the time of conduct, and the time of drafting"). Families
73/33/65, matrix with no findings, teaching case 8/19, CLIR and consumers rebuilt,
the report form accepts `datetime-local` with an offset. Below is the history of the
path taken.

## Existence of Values via `_` — E-0165 (10.09.2026, evening)

The presence layer and the bridges described below were removed the same day:
errata E-0165 gave the language an existential argument, and group rules now read
values directly (`when akt_vin(a: a, vin: _);`). 38 "contains …" institutional
predicates and 38 bridge rules were removed from the inspection report and the
report; group heads remain and still allow assertion by case fact. The source now
has 67 rules. Scenarios were converted to values (108 assertions, 23 bridge
expectations dropped, 4 questions redirected to group heads), parity was
regenerated, mutants M16/M20 rewritten. Families 73/33/65, regression 33/33, matrix
45 rows / 67 rules / 169 tests with no findings, teaching case 8/19, CLIR and
consumers rebuilt, demo forms and the reader regenerated. The description below is
kept as the history of the path taken.

## Value Layer of the Inspection Report (10.09.2026, additive; removed that same evening, see above)

The elements of annex 2 are recorded twice: BY VALUE — 21 empirical predicates with a
typed argument and a parameter label (`akt_vin(a, vin: Text)`,
`akt_god_vypuska(a, god: Integer)`, `akt_probeg(a, probeg: Quantity)`, two `Date`
dates, defect information under clause 2) — and BY PRESENCE: the former "the
inspection report contains …" predicates were converted to `institutional` and are
derived by 19 bridge rules (`modules/osmotr/akt.law`). Asserting presence by case
fact remains permitted: 63 prior authored scenarios, regression 33/33, parity 65/65,
and the teaching case (8 cases, 19 questions) were left unchanged and stay green. A
new scenario `tests/osmotr/19-znacheniya-akta.lawtest` (5 tests): a complete
inspection report by values, one of two dates, make without model, a mixed report,
defects by value. The consumer is the `apps/demos/akt-osmotra` form: the parameter
type determines the field kind. Boundary: time of day is not stored in the model
(there is no instant type for case facts — this claim turned out to be incorrect and
was lifted that same night, see above); `Text` is compared only for equality, there
are no masks in the language such as "a 12-digit IIN".

The same day — the value layer of the report (annex 3): 25 predicates with a value
and 19 bridges in `modules/otchet/oformlenie.law`; sums in calculation instructions
are `Money`, dates are `Date`, everything else is `Text`. Left without a value: the
"no seal" proviso, the cl. 3 marks (the form provides for a mark, an empty mark has
no value), the presentation type, and the format property of cl. 5. Scenario
`tests/otchet/20-znacheniya-otcheta.lawtest` (5 tests): a complete report, three of
four items of insurer information, volumes without cost of works, certification
without a seal, a mixed title page. Matrix row P3.1.2 ("depreciation calculation" —
formerly a case fact) became executable.

## Expressed by Rules (67 rules in the source)

| clause | what is computed |
|---|---|
| 2 | lawfulness of the calculation by the insurer and the appraiser (§206), the application under annex 1, formalizing the inspection with a report under annex 2, inspection at a service station on request (duty), **additional inspection** via three norms (application with annex-1 data, inspection by the insurer with a report, adjustment via an addendum to the report), two duties of the injured party from the day the application is filed (upholding §124.2 and attainment) |
| 3 | three deadlines: mark 3 business days, response 3 business days, report 5 business days (`Quantity business_day`, `add_business_days`, §123 windows); a mark of agreement or of disagreement with reasons (§206); adjustment or a written response (§206); failure to submit the report on time on two grounds and the right to payout under cl. 3-1 art. 22 of the Law; **the insurer's duty to submit the report** (window — up to the fifth business day from the day of inspection; under simplified processing — no deadline) |
| 3-1 | `unless` defeaters on three deadline limits and an open-ended duty to submit the report |
| 4 | an engaged appraiser is introduced into the procedure of clauses 2–3 |
| 4-1 | at least two appraisers (`>= 2`), a defeasible negation for a smaller number, the duty to provide a choice |
| 6 | three stages of organizing the calculation |
| 7 | seven conditions of possibility; admissibility when determining repair cost — only with traffic-accident documents, their established absence — inadmissibility |
| 8 | the §133 freedom to pay for the repair against the payout |
| 9 | two grounds for destruction (§206); the threshold `Money > Money * 0.8` strict; two payout alternatives |
| 10 | two cases of the cost of a new part without depreciation (`Quantity km` ≤ 15,000 / 20,000), **the part condition via two facts** ("was not damaged" and "was not repaired"), the duty to hand over the part on request |
| 11 | two duties to ensure the depreciation calculation is carried out (ombudsman, insurer) |
| annex 1 | two kinds of information in the application |
| annex 2 | six groups of inspection-report information; **groups 3, 4, 5 — down to sub-clauses** (3.1–3.3, 4.1–4.8 with the "odometer photo if available" proviso via two rules, 5.1–5.3) |
| annex 3 | **title page — eight elements**, certification by seal if available or by a single signature if the absence of a seal is established (§206); **calculation instructions — four elements; annexes — three**; **the final amount is checked for having no fractional part** (`round(amount, 0, "HALF_UP") == amount` — for an integer value the rounding mode has no effect, the mode itself is not chosen, §50); both marks; approval by the head or an authorized person; paper or electronic form; footnote — cost of a part without depreciation in the cases of cl. 10 |

## Expressed via the §47.3 Judgment Channel

Nothing: the text contains no open legal choices where the choice would change the
outcome on the facts; three places with ambiguity are named as questions to the
owner (Q1–Q3 below), with a reading adopted pending a decision and tests that lock
in that reading.

## Recorded as a Boundary

1. **Depreciation wear — an external result** (cl. 2 SPO, cl. 11 internet resource,
   annex 3 cl. 1 subcl. 2): the Rules contain no formula for it; the depreciated
   cost of the part enters as the fact `stoimost_detali_s_uchetom_iznosa`.
2. **The rounding mode to tenge** (annex 3 cl. 2) is not named and not selected
   (§50); only the absence of a fractional part is checked.
3. **Deadlines for inspection and drafting the inspection report** (cl. 3 part 1) —
   cl. 3 art. 22 of the Law; the duty of inspection at a service station with an
   open-ended window.
4. **The amount of the payout when the report is not submitted** (cl. 3 part 6) —
   cl. 3-1 art. 22 of the Law; what is computed is the right, not the amount.
5. **Clause 1** — subject matter and grounds; **clause 5** — a reference to
   art. 29-1 of the Law (`sources/vred-ts/articles.json`).
6. **The §86 term-computation policy is a case input** (Civil Code of the Republic
   of Kazakhstan art. 173, 176), together with the §85 calendar snapshot; without a
   snapshot in the world — `MISSING_INPUT`, outside its coverage —
   `CALENDAR_OUT_OF_RANGE`.
7. **Duties with an open-ended window** (subcl. 2, 4-1, 10, 11, 3-1): they are
   performed and never become overdue by deadline; locked in by the t17 scenarios.
8. **Clause 7 part 4** ("photographic materials — an additional source of
   information") — a description with no condition and no consequence; photographs
   of damage as an element of the inspection report are checked by subclause 5.2 of
   annex 2.

## Open Questions for the Owner (reading adopted, locked in by tests)

- **Q1.** Does cl. 3-1 lift the deadline for the injured party's mark (not the
  "insurer's performance deadline")? Adopted: all three cl. 3 deadlines are lifted.
- **Q2.** Who chooses the payout alternative of cl. 9 part 2? Adopted: the
  alternative is determined by the established fact of handing over the remains, or
  by its established negation; silence — the payout is undetermined.
- **Q3.** No lower bound is named for the payout "less" the value of the remains:
  when the value of the remains exceeds the market value, the formula yields a
  negative amount (case G14). Zero is not implied.
- **SPEC-1.** The §175 status for `CALENDAR_OUT_OF_RANGE`: the E-0105 list gives
  `RUNTIME_ERROR` ("other codes"), both implementations answer `MISSING_INPUT`,
  byte-identically — a gap in the prose, awaiting errata; test t14-g locks in the
  issue code and `NEITHER`, but not the status.

## Checks (09.09.2026)

| check | result |
|---|---|
| `sh verify/ci/run_all.sh` (DECISION-0184 profile) | PASS: 3 families, 157 `.lawtest` under both evaluators; `vred_ts` regression 33/33; 35 computations byte-identical (liblaw_ffi == lawref) |
| `tools/catala/compare.py --catala` | 65/65 Catala 1.2.0 cases matched the `cases.json` references |
| family `kz.corpus.vred_ts#catala-parity` | the same 65 cases: lawc and lawref matched the references (as part of the profile) |
| `tools/catala/compare.py --property 120 --seed 1` | see `tools/catala/REPORT.md` (reference Python ↔ Catala ↔ lawc) |
| `tools/catala/mutants.py` | 20 out of 20 mutations killed by scenarios |
| `tools/coverage_matrix.py --check` | 45 rows, 67 rules, 157 test headers, 65 cases; 0 findings |
| `check_package_questions.py --only corpus/laws/kz/vred-ts` (10.09) | 41 cards, 6 boundaries, 13 internal; 43 predicates and 12 norms closed; `--canary` 6/6 |
| `check_source_pinning --only corpus/laws/kz/vred-ts` | 0 violations; 19 fragments, clause coverage 13 out of 13 |
| `boundaries.py kz/vred-ts` | EXECUTABLE 11 / SOURCE_ONLY 2 (clauses 1 and 5 — a boundary with a reason) |
| `lawc check`, `lint.py` across modules | clean |

## Language Boundaries Encountered and Worked Around

- A `Text` value mask ("a 12-digit IIN", "a 17-character VIN") — as of 10.09.2026
  expressible (E-0166: `text_matches(v, "\\d{12}")` in a `constraint` §93), but NOT
  recorded in this package: the source of the mask is another act (`kz.corpus.iin`,
  cl. 2 of the IIN Formation Rules; for VIN, there is no ISO 3779 package in the
  corpus), and `@source(kz.corpus.iin::…)` requires a `pub fragment` from the
  neighboring package and re-pinning its frozen consumers — boundary DECISION-0191
  §2.9.
- `unless` rebinds all head variables (defeater `<rule>/unless/N`).
- A strict rule does not read the output of a defeasible one (LDC-E4103 §111): the
  chain from the deadline limit to the right to a payout, and the duty to submit the
  report, are defeasible.
- An inline `deadline_policy` in a test context — only in `language 0.1`
  (LDC-E1333 in 0.2): suites with deadlines are declared as `0.1`.
- Asserting an institutional predicate by case fact is permitted: old scenarios
  asserting the group predicates of annexes 2–3 were not changed when the groups
  were expanded down to sub-clauses.
