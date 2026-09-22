# Parity report: one regulation, Catala 1.2 and Arxo Law

This report accompanies the artifact of the paper *Law as Function, Law as
Data: A Parity Experiment Between Catala and Arxo Law*. It records what was
compared, how, and with what result. The original pilot was run on 9 September
2026 inside the Arxo corpus; the numbers below were re-obtained from this
repository on 22 September 2026 with the runners it contains (`results/`).

## 1. Subject

The Rules for Determining the Amount of Damage Caused to a Vehicle, approved
by Resolution No. 14 of the Board of the National Bank of the Republic of
Kazakhstan of 28 January 2016, in the wording of the archived copy of
7 September 2025. Nineteen fragments, thirteen clauses, three annexes; the text
is pinned by content hash (`NOTICE`).

The Arxo package `kz.corpus.vred_ts` (67 rules, 169 scenarios in three
families; source comments and documentation in English, the pinned text and
labels in the original Russian) models the Rules including their non-computational parts: ten
duties and one liberty, the defeasible layer, the composition of documents
under the annexes. The Catala model `catala/vred_ts.catala_en` (six scopes)
models the computational part only. Both were written from the pinned text,
independently of each other.

## 2. Method

1. **Reference cases.** 65 cases (`cases.json`) with inputs, expected outputs
   and a written rationale citing the clause, established by hand from the
   text and the 2026 official calendar before either model was run against
   them. Money is whole tenge; the agreed semantics of absence, negation and
   dates are in `catala/README.md`.
2. **Same cases, both systems.** `parity.py --emit` renders the 65 cases into
   two Arxo scenario suites (`tests/parity/parity.lawtest`, 48 cases without
   a calendar; `parity-sroki.lawtest`, 17 deadline cases with the calendar
   snapshot). `--check` proves the rendered suites are byte-identical to the
   package's committed ones. `--catala` runs the Catala model on the same
   inputs through `clerk run --scope … -F json`; `--arxo` lowers the package
   with the engine and runs the two suites.
3. **Random cases.** `--property N --seed S` generates N random inputs per
   scope (destruction, part value, choice of appraisers, deadlines), computes
   the expected outputs with an independent Python oracle written from the
   text (exact fractions, its own working-day arithmetic over the same
   calendar snapshot), and checks Catala and Arxo against it.
4. **Mutations.** `mutants.py` applies 20 one-line changes to the Arxo sources
   (thresholds, comparison operators, dropped conditions, changed periods),
   lowers each mutant and runs all 169 scenarios of the package against it.
   Each mutant must be caught by at least one scenario.
   `mutants_systematic.py` applies six operators (CMP, DROP, NEG, CONST, UNIT,
   UNLESS) to every applicable line of every rule module, one mutant per site,
   and runs each mutant against the same 169 scenarios. Survivors are
   classified by hand (§3a).
5. **Round trip of the input adapter.** `parity.py --roundtrip` decodes the
   rendered Arxo scenarios back into case fields through the published
   predicate-to-field mapping and compares them with the case they were
   rendered from, for the 65 reference cases and the 240 random cases. The
   Catala payload is the case's input dictionary itself, so the Catala side of
   the adapter is the identity.
6. **Alternative Catala encoding.** `catala/vred_ts-alt-disjunction.catala_en`
   encodes the two grounds of a late report (clause 3-1: report not received,
   or received after the inspection period) as one exception whose condition
   is their disjunction, with no guard between them. `parity.py --catala
   --model …` and `--property … --model …` run it on the same cases
   (`results-alt/`).

## 3. Results (22 September 2026, this repository)

| Check | Result |
|---|---|
| Rendered parity suites versus the committed ones | identical |
| 65 reference cases, Catala 1.2.0 | 65 of 65 |
| 65 reference cases, Arxo engine (`law-cli`) | 65 of 65 (48 + 17) |
| 120 random cases, seed 1: oracle versus Catala / versus Arxo | 120 of 120 / 120 of 120 |
| 120 random cases, seed 2: oracle versus Catala / versus Arxo | 120 of 120 / 120 of 120 |
| 20 targeted mutations of the Arxo model | 20 of 20 killed, 0 survived, 0 rejected |
| 420 systematic mutations of the Arxo model (`results/mutants-systematic.json`) | 133 killed, 97 survived, 190 rejected by static checks |
| 65 reference cases, alternative Catala encoding | 65 of 65 |
| 120 random cases per seed, oracle versus alternative Catala encoding | 120 of 120 (seed 1), 120 of 120 (seed 2) |
| Round trip of the adapter, 65 reference and 240 random cases | 65 of 65, 240 of 240 |

The JSON reports in `results/` carry the per-case Catala outputs, the per-suite
engine reports, the per-seed property logs and the per-mutant outcomes.

### 3a. Survivors of the systematic mutations

The generator produced 420 mutants over the 13 rule modules. The compiler
rejected 190 before any scenario ran: 188 because deleting or negating a
premise left a rule variable bound only by a negated or absent conjunct
(the range-restriction check, specification §190), one for a local term left
unused (`LDC-E0201`), one for a negation over a non-atom (`LDC-E1305`). Of the
230 mutants that compiled, 133 were caught and 97 survived. By operator, over
compiled mutants: DROP 45 of 137, NEG 69 of 71, CMP 6 of 7, CONST 7 of 8,
UNIT 3 of 3, UNLESS 3 of 4.

The 97 survivors, classified by reading each site:

| Class | Count | Sites | Reading |
|---|---|---|---|
| (i) binding premise deleted | 9 | `otsenka.law` 68, 84; `gibel-ts.law` 66; `oformlenie.law` 210, 211; `organizatsiya.law` 23, 24; `otsenshchiki.law` 38, 39 | every scenario holds one vehicle, one calculation, one report; a rule that pairs entities across cases has nothing to pair with |
| (ii) one element of a document-completeness rule deleted | 58 | `akt.law` (20), `oformlenie.law` (36, all but 210, 211), `zayavlenie.law` 24, 25 | the scenarios exercise a complete document and specific omissions, not each element omitted singly |
| (iii) premise co-asserted by every scenario reaching the rule | 20 | `usloviya.law` 28–32, 34; `organizatsiya.law` 25, 26, 38, 39; `otsenshchiki.law` 40, 41; `provedenie.law` 65, 66; `otsenka.law` 85, 90, 107; `gibel-ts.law` 67, 80; `oplata-remonta.law` 22 | the clause-7 conditions, the annex-1 and inspection premises, the legal-entity path of clause 10, the destruction premise of the payout rules, the agreement of clause 8 |
| (iv) path no scenario takes | 6 | `sroki-i-vozrazheniya.law` 75, 76 (DROP and NEG each), 116 (UNLESS), 203 | a note of disagreement with reasons; the simplified-procedure defeater of the insurer's response period; a report never provided |
| (v) equivalent on the queried outputs | 4 | `otsenshchiki.law` 60 (CMP, DROP, CONST); `usloviya.law` 45 | the strict rule for two or more appraisers dominates the defeasible denial whatever the perturbation; the sibling clause-7 rule establishes the same conclusion |

Classes (ii)–(iv), 84 mutants, are untested behaviour of the scenario suite,
not defects of the model. Six of them lie in the six compared scopes
(`gibel-ts.law` 67, 80; `otsenka.law` 85, 90; `sroki-i-vozrazheniya.law` 116,
203) and mark where the reference cases do not look. The random cases were not
run against mutants; doing so would likely catch the destruction-premise
mutants.

In the original pilot (9 September 2026) the same 65 cases were also run by
the second Arxo evaluator, the Python reference implementation, and its
evaluation documents were byte-identical to the Rust engine's. That evaluator
is not part of this repository; the claim is recorded here as the pilot's
result, not as something this artifact re-establishes.

## 4. Divergences found and how they were qualified

| # | Observation | Qualification | Action |
|---|---|---|---|
| 1 | A scenario expected `MISSING_INPUT` without a `calendar` axis in the context; both Arxo evaluators answered `TRUE_ONLY` | defect of the test expectation: the single calendar snapshot in the world is selected automatically (specification §89) | the scenario was moved to a world without the calendar package |
| 2 | A scenario expected `RUNTIME_ERROR` for a date outside the calendar's coverage; both evaluators answered `MISSING_INPUT` with the code `CALENDAR_OUT_OF_RANGE`, byte-identically | gap in the prose specification: its list of `MISSING_INPUT` causes does not name this case; the implementations read it as "no snapshot supplied for the date" | recorded as an open specification issue; the scenario pins the code and `NEITHER`, not the status; no implementation was adjusted |
| 3 | Contradictory facts about the transfer of usable remains: two amounts expected, none obtained | defect of the test expectation: a bare premise is read as *established* (§66); under `BOTH` the rule does not apply | expectation corrected from the prose |
| 4 | Catala rounds `money * 80%` on an amount with tiyn; Arxo does not | difference of language semantics, not a defect | comparison restricted to whole tenge; the Arxo behaviour pinned by scenario `urn:query:vred-t15-j` |

No defect of the Rust engine, of the Python evaluator or of the Catala model was
found; the engine core was not changed for the comparison.

## 5. Timing (9 September 2026, Apple Silicon, macOS 24.6, warm runs)

The three implementations return different products for one call: Catala a
value, Arxo a canonical evaluation document (manifest, results, proof graph,
deontic positions, conflicts, issues, hashes). The timings are therefore not
a comparison of "the languages".

| Measure | Catala 1.2.0, interpreter | Arxo Rust engine | Arxo Python evaluator |
|---|---|---|---|
| one computation inside a process | ≈ 16 µs (10,000 calls of the `Gibel` scope in 0.16 s above the baseline) | ≈ 0.4 ms per `evaluate` | ≈ 2.5 ms per `evaluate` |
| process start and model loading | ≈ 40 ms (`clerk run`, project-local `_build`) | ≈ 10 ms (linked world, 274 nodes, 292 KB) | ≈ 0.3 s |
| whole reference set | 5.8 s in one process, including the one-time standard-library build | 0.07 s (48 cases, 118 evaluations) and 0.67 s (17 deadline cases, 101 evaluations) | 0.86 s for the family |

Method: Catala, the `Gibel` scope called 10,000 times inside one program, the
cost of a single-call run subtracted; Arxo, the engine's test runner over the
parity suites, the cost of a one-test run subtracted. The compiled Catala
backends were not measured. A profile of the Rust engine's base cost attributes
most of it to string comparison, map lookups and allocation; the solver itself
is under one percent.

## 6. Open questions about the text (not about the tools)

- **Q1.** Clause 3-1 lifts, under the simplified procedure, the periods "for
  the insurer to carry out the inspection … and determine the amount of
  damage, specified in clause 3". The victim's three-day period for a note of
  disagreement is not a period "for the insurer". Reading adopted: all three
  periods of clause 3 are lifted. Alternative: only the insurer's.
- **Q2.** Who chooses between the two payment alternatives of clause 9 part 2
  (transfer of the remains versus deduction of their value)? Reading adopted:
  the established fact of transfer, or its established negation; silence gives
  no payment.
- **Q3.** The lower bound of "less the value of usable remains" is not stated:
  remains worth more than the market value give a negative amount (case G14).
  Zero is not implied.

Both models implement the adopted readings; the questions are for the
regulator, and the artifact does not resolve them.
