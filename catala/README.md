# The Catala model

`vred_ts.catala_en` is an independent implementation, in Catala 1.2, of the
computational part of the Rules for Determining the Amount of Damage Caused to
a Vehicle (Resolution No. 14 of the Board of the National Bank of Kazakhstan,
28 January 2016). It was written from the pinned source text
(`../corpus/laws/kz/regulators/vred-ts/sources/vred-ts/ru.txt`), not translated from the Arxo package.

Six scopes cover the six computable points of the Rules:

| Scope | Clause | Computes |
|---|---|---|
| `Gibel` | cl. 9 | economic infeasibility of repair (80 % threshold), destruction, payment with or without usable remains |
| `StoimostDetali` | cl. 10 and annex 3 footnote | whether a replaced part is valued without depreciation; the part's value |
| `VyborOtsenshchikov` | cl. 4-1 | whether the choice of appraisers is secured (at least two proposed) |
| `DopustimostOsmotra` | cl. 7 | whether an inspection is possible and admissible |
| `SrokiPunkta3` | cl. 3 and 3-1 | working-day deadlines for the report, the objection and the reply; late report; right to payment under the Law |
| `ItogovayaVelichina` | annex 3 cl. 2 | whether the final amount is properly stated (whole tenge, spelled out) |

## Agreed semantics of the comparison

- **No conclusion.** Catala: an `optional` output that is `Absent` (the key is
  missing from the JSON result). Arxo: `truth_status == NEITHER`, or
  `collected_count(0)` for quantities. Expectation in `cases.json`: `null`.
- **Established negation.** Catala: `Present content false`. Arxo:
  `FALSE_ONLY`. Two conclusions have it: the choice of appraisers (cl. 4-1)
  and the admissibility of inspection (cl. 7).
- **Missing inputs.** Catala: an optional input omitted (`Absent`). Arxo: the
  fact is not asserted. Negative facts (`assert not …`) correspond to
  `Present content false` inputs (`ostatki_peredany`, `dokumenty_o_dtp`,
  `opredelyaetsya_stoimost_remonta`, `otchet_predostavlen`). Boolean inputs
  without a negative rule are `false` exactly when the fact is not asserted.
- **Money.** Whole tenge (KZT). Catala stores money to the cent and rounds a
  money-times-decimal product; Arxo stores `Money` exactly and rounds only where
  the text says so. On whole tenge, 80 % of an amount is exactly representable
  in both. On amounts with tiyn the two DIVERGE by construction: the Arxo
  scenario `urn:query:vred-t15-j` (market value 1 000 000.01, costs
  800 000.01) pins the exact semantics (800 000.008 < 800 000.01, hence
  infeasible), where Catala would round the threshold to 800 000.01 and give
  no conclusion. The comparison is therefore restricted to whole tenge, which
  is also what annex 3 cl. 2 requires of the final amount.
- **Dates and working days.** Calendar dates; working days come from the
  external snapshot of the official 2026 calendar
  (`../corpus/clir/kz-official-2026.calendar.json`): Saturday and Sunday are
  non-working, holidays and transferred rest days are listed in the snapshot.
  A period of N working days expires on the N-th working day after the day of
  the event (Civil Code of Kazakhstan, arts. 173 and 176; in Arxo the deadline
  policy `start_count next_day, include_end true, roll next_working_day`,
  supplied by the case). A day outside the snapshot's coverage yields no
  conclusion (Catala `Absent`; Arxo `NEITHER` with the code
  `CALENDAR_OUT_OF_RANGE`).
- **Rounding to tenge (annex 3 cl. 2).** The Rules do not name a rounding mode
  and none is chosen; only the absence of a fractional part is checked (Catala
  `round of s = s`, Arxo `round(amount, 0, "HALF_UP") == amount`; for a whole
  value the mode makes no difference).

## What the comparison does not cover

Deontic positions (ten duties and one liberty, with the statuses SATISFIED /
ACTIVE / VIOLATED), the defeasible layer with `unless` defeaters, established
negations inside the proof, `whyNot` explanations, the composition of documents
under annexes 1–3, and the chain "calculation under the Rules" are not
computational forms and have no comparable model in Catala. They are checked by
the Arxo scenarios of `../corpus/laws/kz/regulators/vred-ts/tests/` and by `../mutants.py`. This pilot is
not evidence about the full expressiveness of either language: exactly the six
scopes above were compared.

## Running Catala alone

```sh
opam install catala.1.2.0          # once
python3 ../parity.py --catala      # 65 reference cases
```

`parity.py` copies the model into a temporary project with its own `_build`
so that `clerk` does not rebuild the standard library on every call.
