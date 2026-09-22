# Formalization completeness audit: kz/vred-ts

**Snapshot:** September 1, 2026. Checked: 7 `.law`, 8 `.lawtest`, CLIR
`corpus/clir/kz-vred-ts.lawir.json` (216 nodes), and the runner
`corpus/kz/acts/vred_ts.py` (30 scenarios KZ-VRED-01…30). Commands: `audit.py
kz/vred-ts --fast`, `inventory.py kz/vred-ts`, `orphan_refs.py`, `uncovered.py`,
`one_way_premises.py`, `boundaries.py kz/vred-ts`,
`check_source_pinning.py --only corpus/laws/kz/vred-ts`,
`check_rule_executability.py corpus/clir/kz-vred-ts.lawir.json`.

## Conclusion

The act uses 9 declaration kinds out of 47 — and should not use more:
the National Bank's Rules are a subordinate-legislation instrument of thirteen
clauses and three annexes, with no edition axis, no roles, no decision tables,
and no doctrinal readings. The Rules express EVERYTHING the text decides on
its own: two thresholds (80% of market value, 15,000 and 20,000 kilometers of
mileage), three deadlines in business days with their removal by cl. 3-1, four
"or" splits (§206), ten deontic positions, and all the part-price arithmetic
that the Rules contain. What enters as case facts is what the Rules HANDED OFF
to another instrument: the amount of depreciation wear and the part cost that
accounts for it (cl. 2, 11, annex 3) and the already-rounded final amount
(annex 3 cl. 2; the Rules do not name a rounding mode — §50). Two of the
thirteen clauses are declared a boundary: cl. 1 (the act's subject matter) and
cl. 5 (a bare reference to art. 29-1 of the Law).

## Measurements

| measurement | value | command |
|---|---|---|
| §33.1 depth | EXECUTABLE 11 / INTERPRETED 0 / ANCHORED 0 / SOURCE_ONLY 2 | `boundaries.py kz/vred-ts` |
| stub share | 1 bridge rule out of 56 (1%) — `StoimostDetaliSUchetomIznosa`, discussed below | `one_way_premises.py` |
| source bytes | 99.9% (22,921 of 22,940), 19 fragments | `check_source_pinning.py --only …` |
| volume within units | worst cases: cl. 1 — 2,080 bytes, 0 norms (boundary); cl. 5 — 481 bytes, 0 norms (boundary); cl. 11 — 1,336 bytes, 4 norms | `uncovered.py kz/vred-ts` |
| reachability | 26 of 42 rules with a literal head are reached by synthesis, 2 are not reached (both discussed below), 14 cases are not synthesized, 10 norm-heads and 4 branches of §142 are outside this measurement | `check_rule_executability.py` |
| scenarios | 30 regression scenarios + 8 `.lawtest` | `run_kz_regression.py --only vred_ts` |
| differential | 37 evaluate calls byte-identical | `check_kz_differential.py --only vred_ts` |

## Constructs used

| production | count | role in this act |
|---|---|---|
| `source_decl` / `edition_decl` / `publication_decl` | 1 / 1 / 1 | Resolution No. 14, the sole edition, an archival snapshot from «Әділет» |
| `fragment_decl` | 19 | thirteen clauses (generated), the title, two chapters, and three annexes (manual) |
| `entity_decl` | 10 | vehicle, calculation, insurer, injured party, appraiser, part, inspection report, report, application, insurance ombudsman |
| `relation_decl` | 115 | vocabulary of case facts and derived calculation states |
| `assertion_decl` | 3 | the three deadline values of cl. 3 — `3 business_day`, `3 business_day`, `5 business_day`; pinned constants, not numbers embedded in predicate names |
| `rule_decl` | 52 (56 rules in CLIR counting generated defeaters) | all the logic: thresholds, deadlines, "or" splits, ten deontic positions |
| `test_decl` | 8 | pairs on both sides of each numeric threshold |

## Depth of use

Rule strengths: strict 43, defeasible 9, defeater 4. The defeasible layer is
neither decoration nor a reserve: it carries exactly two of the act's
mechanisms. The first is cl. 3-1, which lifts all three deadlines of cl. 3
under simplified processing; it is written as an `unless` clause on each of
the three deadline-limit rules, and the entire chain up to the legal
consequence ("the report was not submitted on time" → the right to payment
under cl. 3-1 of art. 22 of the Law) is necessarily declared defeasible: a
strict rule reading the bare conclusion of a defeasible one is rejected by
both engines (LDC-E4103 §111). The second is the footnote to annex 3, under
which wear is not applied in the cases of cl. 10; it is written as `unless`
on the rule for part cost with wear.

There are two negative heads (`VyborOtsenshchikovNeObespechen`,
`OsmotrNedopustimBezDokumentov`), both defeasible: a strict negative head would
be a dead rule. There are seven negative literals in rule bodies — all of them
read ESTABLISHED negation under §113 (the remains were not handed over, there
are no accident documents, the report was not submitted, the mark was not
placed): in none of these places does the case's silence amount to a denial,
and `not_known` is deliberately not used anywhere in the act.

Modalities: duty 9, liberty 1. There are eight achievement goals and one
maintenance goal — preserving the damaged property in the condition it was in
after the incident (§124.2: a single established fact of alteration breaches
the duty immediately). The act has neither power under §127 nor immunity
under §128 — the Rules grant no one competence and shield no one from it.

Terms: `add_business_days` six calls, §86 units — `business_day` three
declarations, `km` two literals. Seven comparisons: `gt` three (the 80%
threshold, two dates past the deadline limit), `le` two (mileage thresholds),
`ge` one (two appraisers), `lt` one (fewer than two appraisers). No
aggregates, quantifiers, or priorities: there is nothing in this act to count
over sets and nothing to order between norms.

## Unused constructs — verdicts

### No data in the source

`revision_decl`, `entrenchment_decl`, `alignment_decl` — there is one
edition, no entrenched provisions, and no parallel second-language text within
the pinned bytes. `role_decl` — the Rules speak of the insurer, the appraiser,
and the injured party as PARTIES to a specific calculation, not as roles with
substitution conditions. `event_decl` / `action_decl` — there are no events
with an independent lifecycle in the act; actions ("hands over", "sends") are
expressed as state predicates, and the deontics read exactly those. `evidence_decl`
/ `support_decl` — the Rules say nothing at all about evidentiary weight.
`priority_decl` / `priority_policy_decl` — there are no conflicting norms in
the act: cl. 3-1 lifts the deadlines with an `unless` clause, not a priority.
`procedure_decl` — the act does not describe stages with transitions: cl. 6
lists three calculation STAGES but neither mandates their order nor links the
transitions to conditions. `decision_decl` / `function_decl` / `external_decl`
— there is no computable table or pure function in the Rules, and wear, which
would be a candidate for `external`, is not computed by them at all.
`map_decl`, `record_decl`, `variant_type_decl`, `alias_type_decl`, `facts_decl`,
`facts_use_decl` — there are no structured values or shared fact groups in the
act; `enum_decl` — nor are there closed enumerations: the one candidate,
annex 3's "paper or electronic form", is split into two rules (§206) because
the format requirement is the same across both branches.

### Equivalent refactoring (not a gap)

`concept_decl` — a synonym for `relation … kind institutional` (E-0071),
deprecated. `definition_decl … sufficient` — a synonym for the pair
"institutional relation + strict rule" (E-0071). `calendar_decl` — the §85
snapshot belongs to ANOTHER act in the corpus (the law on holidays) and
arrives here through its import; the Rules do not establish a calendar of
their own.

### False strengthening (must NOT be added)

`presumption_decl` — the Rules introduce no presumptions: cl. 3-1 is not a
presumption but an exception to the deadline's applicability. `fiction_decl`
— there are no fictions; cl. 9's "deemed destroyed" is a definition through a
condition, and it is computed by two rules rather than declared a fiction.
`classification_decl` — a classification without a computable criterion would
be a stub here: both cases of cl. 10 and both grounds of cl. 9 have complete
criteria in the text. `interpretation_decl` / `interpretation_group_decl` —
there are no readings in the act that change the outcome; introducing them
would amount to attributing to the Rules a dispute the text does not contain.
`closure_decl` — closure under §70 would declare the world closed where the
Rules say nothing about completeness of information; "the report was not
submitted" is supplied as an established denial by the case, and that is more
honest. `constraint_decl` — §93.1 is not computed at execution (a known v1
boundary), and recording a contradiction between "the remains were handed
over" and "the remains were not handed over" would be decoration.

### Outstanding work

None. All `audit.py` findings are discussed below and require no work.

## Candidates and their analysis

**Premises leading nowhere (`orphan_refs.py`): none.** Every empirical
predicate is supplied by a scenario or a `.lawtest`.

**One-way premises (`one_way_premises.py`): 1 of 56 (1%).**
`StoimostDetaliSUchetomIznosa` — the head `stoimost_zamenyaemoy_detali` is
TERMINAL: this is exactly the act's result, the amount fed into the damage
calculation, and there is nothing within the package to read it further —
the final cost of restorative repair is assembled outside the Rules, by
licensed software. The premise `stoimost_detali_s_uchetom_iznosa` is an
external result, named boundary 1 in STATUS.md. This is not a bridge stub:
the same head has a SECOND rule (`StoimostDetaliBezIznosa`), between them
stands the annex-3-footnote defeater, and both branches are closed by
scenarios KZ-VRED-28 and KZ-VRED-29 with different amounts. Verdict: not a
stub, no work needed.

**Dead symbols: none** (per the shared gate `check_dead_symbols`).

**Unreachable rules (`check_rule_executability.py`): 2, both explained.**
`OtchetPoluchenPosleSroka` — the case synthesizer does not pick a date pair
satisfying `got > due` after computing `add_business_days`; the rule fires in
scenario KZ-VRED-17 (report received 09.09.2026 with the last day being
08.09.2026). `VyborOtsenshchikovNeObespechen` — the head is negative, and the
synthesizer's `FALSE_ONLY` is exactly its firing; closed by scenario
KZ-VRED-12 and test `08-odin-otsenshchik.lawtest`.

**LawQL lint findings: 10, all expected and named in STATUS.md.**
`achievement-open-window` — six achievement duties with an open window
(cl. 2, 4-1, 10, 11): the Rules do not name a deadline for their performance,
and assigning one would amount to inventing a norm. `defeater-head-variable-unless`
— four defeaters generated by `unless` clauses: rebinding the head variables
in the clause is MANDATORY (without it the oracle fails on substitution), and
the behavior is verified by scenario KZ-VRED-20, where under simplified
processing neither the deadline limit nor the right to payment is derived.
Both groups require a deliberate re-freeze of `corpus/ratchets/ql-baseline.json`
— it is listed in STATUS.md among the work items outside this package's
directory.

**Heavyweight units (`uncovered.py`): cl. 1 (2,080 bytes, 0 norms) and cl. 5
(481 bytes, 0 norms)** — both have been read and declared a boundary with a
reason in `sources/vred-ts/articles.json`; the pinning gate checks these
declarations against the clause text, not against the plausibility of the
wording.

## Final criterion

The final criterion is not the share of productions used, but the absence
of unexpressed source content and silent pipeline losses. By this criterion
the act is closed: of the thirteen clauses, eleven produce derivations, and
two are declared a boundary with a reason checked against the text; no
threshold, deadline, or deontic position remains prose in a label; everything
supplied as a fact is supplied because the Rules explicitly handed it off to
another instrument, and every such label names the owner of that calculation.

## Addendum 09.09.2026 — content completeness and independent cross-check

The 01.09 snapshot measured addressability (13 clauses, 99.9% of bytes) and
the number of rules; under the DECISION-0184 criterion, this is not enough.
A line-by-line reading of the source against the model (the `COVERAGE-MATRIX.md`
matrix, 45 rows) found and closed the following:

| finding | before | after |
|---|---|---|
| annex 2 cl. 3–5 (14 sub-items) | three fact-groups | sub-items as facts, groups derived; "odometer photo (if available)" — two rules |
| annex 3 cl. 1 items 1, 3, 4 (15 elements) | three fact-groups | elements as facts, "seal (if available)" — two rules |
| annex 3 cl. 2 "rounded to tenge" | fact "already rounded" | check for the absence of a fractional part via the `round` term, with no mode selection |
| cl. 2 pt. 4 supplementary inspection | one rule reading the initial inspection report | three norms: its own application, its own report, adjustment |
| cl. 3 pt. 2 "submits … a report" | duty not expressed | duty with a window up to the limit of cl. 3 pt. 6; under simplified processing — no deadline |
| cl. 10 "was not previously damaged and has not undergone repair" | one fact | two facts and a rule |
| cl. 2 pt. 3, pt. 5; cl. 4-1 — positions | rules without position scenarios | t17 scenarios (SATISFIED/ACTIVE/VIOLATED, maintenance under §124.2) |
| adjustment for hidden defects | rule without a single scenario | four t10 scenarios |

Measurements after the addendum: 67 rules (strict 51, defeasible 12,
generated defeaters 4); 157 test headings (86 authored and regression + 65
cross-check + 6 positions); mutations 20/20 killed; Catala 65/65; profile
PASS. Boundaries 1–8 and questions Q1–Q3, SPEC-1 — in `STATUS.md` and
`tools/catala/REPORT.md`.
