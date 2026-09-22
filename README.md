# arxo-catala-parity

One regulation, two independent formalizations, the same cases. The
computational part of the Kazakh Rules for Determining the Amount of Damage
Caused to a Vehicle (Resolution No. 14 of the Board of the National Bank of
Kazakhstan, 28 January 2016) was written twice from the pinned official text:
as a [Catala](https://catala-lang.org) 1.2 program and as an
[Arxo Law](https://www.arxo.io) package. This repository is the artifact of
that comparison: both models, the reference cases, the runners, and the
recorded results.

It accompanies the paper *Law as Function, Law as Data: A Parity Experiment
Between Catala and Arxo Law* and the essay
[Law as Function, Law as Data](https://blog.arxo.io/law-as-function-law-as-data/).

## Results

Re-obtained from this repository on 22 September 2026 (`results/`):

| Check | Result |
|---|---|
| 65 reference cases written from the text, Catala 1.2.0 | 65 of 65 |
| the same 65 cases as Arxo scenarios, Arxo engine | 65 of 65 |
| 240 random cases (two seeds), Python oracle versus Catala | 240 of 240 |
| the same 240 random cases, Python oracle versus Arxo | 240 of 240 |
| 20 targeted mutations of the Arxo model against its 169 scenarios | 20 of 20 caught |
| the alternative Catala encoding (one disjunctive exception, no guard), 65 reference and 240 random cases | 65 of 65, 240 of 240 |
| the input adapter: rendered scenarios decoded back to case fields, 65 + 240 cases | all |
| SYS_TOTAL systematic operator-based mutations against the 169 scenarios | SYS_KILLED caught, SYS_SURVIVED survived, SYS_REJECTED rejected |

Where a norm states an algorithm, both languages reproduce it identically.
What each of them does beyond the algorithm is the subject of the paper;
`docs/REPORT.md` records the method, the qualified divergences and the timing
measurements.

## Layout

```
cases.json                              65 reference cases: inputs, expected outputs, rationale, clause
catala/vred_ts.catala_en                the Catala model (six scopes), written from the pinned text
catala/vred_ts-alt-disjunction.catala_en the same model with the two grounds of a late report as one disjunctive exception (no guard)
catala/README.md                        agreed semantics of the comparison; what is not compared
corpus/laws/kz/regulators/vred-ts/      the Arxo package kz.corpus.vred_ts, as in the Arxo corpus (comments in English)
    package.law, sources.law, modules/  sources, pinned text and its fragments, 67 rules
    tests/                              169 scenarios in three families; tests/parity/ are the 65 cases rendered
    law.toml, law.lock                  manifest and lock (the lock pins the calendar snapshot by hash)
corpus/clir/                            the official-calendar snapshot of 2025–2026, pinned bytes
parity.py                               the runner: emit/check, Catala (--model for the alternative encoding), Arxo, property mode, --roundtrip
mutants.py                              the 20 targeted mutations
mutants_systematic.py                   operator-based mutations over every rule module (CMP, DROP, NEG, CONST, UNIT, UNLESS)
results/                                recorded JSON reports of the runs above
docs/REPORT.md                          the parity report
docs/claim-ledger.csv                   every claim of the paper with its status (measured / pilot / mechanized / counted / cited) and evidence
tools/toolchain.py, toolchain.lock.json pinned download of the engine release (see below)
```

The package directory keeps the depth it has in the Arxo corpus so that its
`law.lock` resolves the calendar resource without modification. The sources
are those of the Arxo corpus at revision `41952a1a9c`, in which the comments,
scenario comments and documentation of this package were translated into
English; the pinned official text, the labels and the quoted fragments are
unchanged, and the lowered program is byte-identical to the one before the
translation (semantic hash `c197794a8cb3c768…`, recorded in
`results/arxo-parity.json`).

## Reproducing

Python 3.12 or newer, standard library only.

**Catala.** Install Catala 1.2.0 with opam (`opam install catala.1.2.0`);
`clerk` is found on `PATH` or in `~/.opam/*/bin`.

```sh
python3 parity.py --check                 # the rendered parity suites equal the committed ones
python3 parity.py --catala                # 65 reference cases
python3 parity.py --property 120 --seed 1 --no-arxo
```

**Arxo.** The engine is the `law-cli` binary. Pass it with `--law`, set
`$LAW_CLI`, or put it on `PATH` (the `law` wrapper is accepted too).

```sh
python3 parity.py --arxo --law /path/to/law-cli
python3 parity.py --property 120 --seed 1 --law /path/to/law-cli
python3 mutants.py --law /path/to/law-cli
python3 parity.py --all --law /path/to/law-cli --record results
python3 parity.py --roundtrip                                   # adapter round trip, no engine needed
python3 parity.py --catala --model catala/vred_ts-alt-disjunction.catala_en
python3 mutants_systematic.py --law /path/to/law-cli --record results
```

`--arxo` lowers the package with the pinned imports context, adds the calendar
snapshot to the world of the deadline suite, and runs the two parity suites
through `law-cli test`. No code in this repository computes a legal answer; the
runners only call the two tools and compare their outputs with `cases.json`.

The engine release is pinned in `toolchain.lock.json`
(`law-package-tools@0.1.0`, Linux x86_64, SHA-256 in the lock);
`tools/toolchain.py download` fetches and verifies it once the release is
public. Until then the binary is available to reviewers on request from the
maintainer; the recorded reports in `results/` carry the SHA-256 of the binary
that produced them.

## What a third party can reproduce

Without the engine binary: the Catala rows (65 of 65; 120 of 120 on each seed
with `--no-arxo`) and the rendering check. With the binary: the Arxo rows, the
property mode on the Arxo side and the mutation check. The revision reviewed
for the paper is tagged `paper-rev2`; the repository's history was rewritten
once on 22 September 2026 when the package's comments were translated, and the
tag is the stable citation target.

## What is and is not established here

- Established: on the computational part of this regulation, the Catala model
  and the Arxo package agree with hand-written expectations and with an
  independent oracle on every case tried, and the Arxo scenarios catch every
  targeted mutation of the model.
- Not established: anything about the two languages beyond the six scopes
  compared. Deontic positions, the defeasible layer, editions in time and the
  proof documents of Arxo have no counterpart in the Catala model and are
  checked by the Arxo scenarios alone. The pilot's byte-identity between the
  two Arxo evaluators (Rust engine and Python reference implementation) is
  recorded in `docs/REPORT.md` as the pilot's result; the Python evaluator is
  not part of this repository.
- Money is compared in whole tenge: Catala rounds a money-times-decimal product
  to the cent, Arxo keeps money exact. On amounts with tiyn the two diverge by
  construction (`catala/README.md`).

## Rights

Code, models and scenarios: Apache-2.0 (`LICENSE`). The pinned text of the
Rules is an official document of the Republic of Kazakhstan; its terms and
provenance are in `NOTICE`.

Maintainer: Rifat Dzhumagulov (hi@arxo.io). Address:
https://github.com/arxohq/arxo-catala-parity.
