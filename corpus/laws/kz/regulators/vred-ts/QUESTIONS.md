# Questions for the package `kz.corpus.vred_ts`

<!-- Generated from analysis/questions.json: python3 verify/ci/gates/coverage/check_package_questions.py --emit. Do not edit by hand. -->

Catalog of **provided-for** queries §172 and what verifies each one (DECISION-0190). A card does not mean a positive answer on the case: the answer is given only by the evaluation document with proof. The absence of a card means "not described by the catalog," not "the law is silent."

## Total loss of the vehicle and the amount of the payout

Source units: VRED_TS_PT_8, VRED_TS_PT_9.

| id | question | form | goal | template | branches | verified |
|---|---|---|---|---|---|---|
| `unichtozheno` | Is the vehicle considered destroyed? | truth | `ts_schitaetsya_unichtozhennym(v: TransportnoeSredstvo)` | `evaluate truth(ts_schitaetsya_unichtozhennym(v: <v>));` | restoration is technically impossible (case fact) (`UnichtozhenoPoTekhnicheskoyNevozmozhnosti`); restoration is economically inexpedient: costs strictly exceed 80% of the market value as of the report date (`UnichtozhenoPoEkonomicheskoyNetselesoobraznosti`) | 5 tests; cases Gibel, PeredachaOstatkov, Porog, Molchanie, MolchanieSnyato; queries `unichtozheno.json` |
| `pochemu-ne-unichtozheno` | Why is the vehicle not recognized as destroyed: which premise is missing? | why_not | `ts_schitaetsya_unichtozhennym(v: TransportnoeSredstvo)` | `why_not(ts_schitaetsya_unichtozhennym(v: <v>)) — blocker graph §185 with the status of each premise; law ask --query-json queries/pochemu-ne-unichtozheno.json` | — | cases Porog; queries `pochemu-ne-unichtozheno.json` |
| `netselesoobrazno` | Do the expected restoration costs exceed eighty percent of the market value (the threshold is strict)? | truth | `vosstanovlenie_ekonomicheski_netselesoobrazno(v: TransportnoeSredstvo)` | `evaluate truth(vosstanovlenie_ekonomicheski_netselesoobrazno(v: <v>));` | Money > Money * 0.8 strictly; exactly 80% does not meet the threshold (`EkonomicheskayaNetselesoobraznost`) | 6 tests |
| `vyplata-pri-gibeli` | What is the insurance payout for total loss of the vehicle? | collect | `strakhovaya_vyplata_pri_gibeli(r: RaschetVreda, amount: Money↑)` | `evaluate collect amount: Money where kz.corpus.vred_ts::strakhovaya_vyplata_pri_gibeli(r: <r>, amount: amount);` | salvage transferred into the insurer's ownership — market value as of the report date (`VyplataPriPeredacheOstatkov`); it is established that the salvage was NOT transferred — market value minus the salvage value; the case's silence on the transfer does not count as negation (§113) (`VyplataZaMinusomGodnykhOstatkov`) | 5 tests; cases Gibel, PeredachaOstatkov, Molchanie, MolchanieSnyato; files `examples/gibel-i-detali/check.py` |
| `pochemu-ne-vyplata` | Why is the payout amount for total loss not derived? | why_not | `strakhovaya_vyplata_pri_gibeli(r: RaschetVreda, amount: Money)` | `why_not(strakhovaya_vyplata_pri_gibeli(r: <r>, amount: <amount>)); law ask --query-json queries/pochemu-ne-vyplata.json` | — | cases Molchanie; queries `pochemu-ne-vyplata.json` |
| `pozitsii-oplata-remonta` | Is the insurer entitled, by agreement with the injured party, to pay for the repair in lieu of the payout? | positions | rule `OrganizovatOplatuRemonta` | `evaluate positions(); expect position(OrganizovatOplatuRemonta, <status>);` | — | 1 test |

- `vyplata-pri-gibeli`: Q2 STATUS.md: the payout alternative is determined by the established fact of the salvage transfer or its established negation; on silence, the payout is undetermined. Q3: the lower bound of "minus" is not stated — if the salvage is worth more than the market value, the amount is negative (parity:G14), zero is not implied.
- `pochemu-ne-vyplata`: The rule head is computed: after E-0164 the graph names both rules of cl. 9; "minus the salvage" carries the headArguments (UNEVALUATED) marker. The blocker does not prove why the specific given value was not obtained.

## Valuation of the replaced part

Source units: VRED_TS_PT_10, VRED_TS_PRIL_3.

| id | question | form | goal | template | branches | verified |
|---|---|---|---|---|---|---|
| `detal-bez-iznosa` | Is the replaced part valued at the cost of a new part without accounting for wear? | truth | `detal_otsenivaetsya_bez_iznosa(d: Detal)` | `evaluate truth(detal_otsenivaetsya_bez_iznosa(d: <d>));` | owner is a natural person, vehicle without mandatory technical inspection, average annual mileage not exceeding 15,000 km, the part was not damaged and not repaired (`NovayaDetalUFizicheskogoLitsa`); owner is a legal entity, vehicle under warranty service, mileage not exceeding 20,000 km, the same condition on the part (`NovayaDetalUYuridicheskogoLitsa`) | 10 tests; cases DetalFizlitso, DetalYurlitso, DetalRemont; queries `detal-bez-iznosa.json` |
| `pochemu-ne-bez-iznosa` | Why is the part not valued without wear? | why_not | `detal_otsenivaetsya_bez_iznosa(d: Detal)` | `why_not(detal_otsenivaetsya_bez_iznosa(d: <d>)); law ask --query-json queries/pochemu-ne-bez-iznosa.json` | — | cases DetalRemont; queries `pochemu-ne-bez-iznosa.json` |
| `stoimost-detali` | Which value of the replaced part goes into the calculation: new or with wear accounted for? | collect | `stoimost_zamenyaemoy_detali(d: Detal, amount: Money↑)` | `evaluate collect amount: Money where kz.corpus.vred_ts::stoimost_zamenyaemoy_detali(d: <d>, amount: amount);` | the part is valued without wear — market value of the new part, the value with wear is defeated (`StoimostDetaliBezIznosa`); the general rule of annex 3 — value with wear accounted for (case fact, wear supplied externally) (`StoimostDetaliSUchetomIznosa`) | 4 tests; cases DetalFizlitso, DetalYurlitso, DetalRemont; files `examples/gibel-i-detali/check.py` |
| `pozitsii-peredat-detal` | Is the injured party obligated to hand over the replaced part to the insurer on its request, and has the obligation been performed? | positions | rule `PeredatZamenyaemuyuDetal` | `evaluate positions(); expect position(PeredatZamenyaemuyuDetal, <status>);` | — | 2 tests; cases DetalFizlitso; queries `positions.json` |

- `pozitsii-peredat-detal`: The obligation's window is open: it does not become violated by deadline (t17).

- **Does not answer:** What is the amount of the part's depreciation wear? — the source refers outward (VRED_TS_PT_2, VRED_TS_PT_11, VRED_TS_PRIL_3). The amount of depreciation wear is not computed: the Rules contain no formula (cl. 2 refers to licensed software, cl. 11 — to an internet resource, annex 3 names the wear calculation as a section of the report); the part's value with wear accounted for enters as a case fact. Supplied as the fact `stoimost_detali_s_uchetom_iznosa`. Related question: `stoimost-detali`.

## The damage-amount report: deadlines, endorsements, objections, formatting

Source units: VRED_TS_PT_3, VRED_TS_PT_3_1, VRED_TS_PRIL_3.

| id | question | form | goal | template | branches | verified |
|---|---|---|---|---|---|---|
| `predel-otmetki` | Which day is the last for the injured party's endorsement acknowledging the report (three business days)? | truth | `predel_otmetki_poterpevshego(r: RaschetVreda, day: Date)` | `evaluate truth(predel_otmetki_poterpevshego(r: <r>, day: <day>)); — the world needs a snapshot of kz.corpus.clir.official_calendar and the case's deadline_policy` | three business days from the day the report is received, per the official calendar (`PredelOtmetkiPoterpevshego`); under simplified accident registration the deadline is lifted (defeater) (`PredelOtmetkiPoterpevshego/unless/UproshchennoeOformlenie`) | 6 tests |
| `predel-otveta` | Which day is the last for the insurer's response to the disagreement endorsement? | truth | `predel_otveta_strakhovshchika(r: RaschetVreda, day: Date)` | `evaluate truth(predel_otveta_strakhovshchika(r: <r>, day: <day>)); — a calendar snapshot §85 is needed` | three business days from the day the disagreement endorsement is received (`PredelOtvetaStrakhovshchika`); under simplified registration the deadline is lifted (`PredelOtvetaStrakhovshchika/unless/UproshchennoeOformlenie`) | 3 tests |
| `predel-otcheta` | Which day is the last for delivering the report to the injured party (five business days from the day of inspection)? | truth | `predel_predostavleniya_otcheta(r: RaschetVreda, day: Date)` | `evaluate truth(predel_predostavleniya_otcheta(r: <r>, day: <day>)); — a calendar snapshot §85 is needed` | five business days from the day of inspection (`PredelPredostavleniyaOtcheta`); under simplified registration the deadline is lifted (`PredelPredostavleniyaOtcheta/unless/UproshchennoeOformlenie`) | 3 tests |
| `otchet-ne-v-srok` | Was the report not delivered within the established deadline? | truth | `otchet_ne_predostavlen_v_srok(r: RaschetVreda)` | `evaluate truth(otchet_ne_predostavlen_v_srok(r: <r>));` | the report was received after the deadline limit (`OtchetPoluchenPosleSroka`); the report was not delivered at all (established negation of receipt) (`OtchetNePredostavlenVovse`) | 3 tests |
| `pravo-na-vyplatu-3-1` | Does the injured party have the right to a payout under cl. 3-1 of art. 22 of the Law when the report is not delivered? | truth | `pravo_na_vyplatu_po_punktu_3_1_stati_22_zakona(p: Poterpevshiy, r: RaschetVreda)` | `evaluate truth(pravo_na_vyplatu_po_punktu_3_1_stati_22_zakona(p: <p>, r: <r>));` | the right is derived from non-delivery of the report on time; the AMOUNT of the payout is not computed here (`PravoNaVyplatuPriNepredostavleniiOtcheta`) | 5 tests |
| `otvet-na-nesoglasie` | Did the insurer respond to the disagreement endorsement: by correcting the report or by a written reply? | truth | `strakhovshchik_otreagiroval_na_nesoglasie(r: RaschetVreda)` | `evaluate truth(strakhovshchik_otreagiroval_na_nesoglasie(r: <r>));` | correction of the calculation (`ReaktsiyaKorrektirovkoy`); a written, reasoned reply (`ReaktsiyaPismennymOtvetom`) | 1 test |
| `pozitsii-otchet` | Is the insurer's obligation to deliver the report performed, violated, or still open (within the deadline, or without a deadline under simplified registration)? | positions | rules `PredostavitOtchet`, `PredostavitOtchetBezSroka` | `evaluate positions(); expect position(PredostavitOtchet, <status>); expect position(PredostavitOtchetBezSroka, <status>); — a calendar snapshot §85 is needed` | — | 4 tests |
| `pozitsii-otmetka-i-otvet` | What is the status of the obligations to place the endorsement (injured party) and respond to the disagreement (insurer)? | positions | rules `ProstavitOtmetku`, `OtvetitNaNesoglasie` | `evaluate positions(); expect position(ProstavitOtmetku, <status>); expect position(OtvetitNaNesoglasie, <status>);` | — | 3 tests |
| `otchet-sostavlen` | Is the report drawn up according to the Rules: formatted per annex 3, approved, submitted in an admissible form? | truth | `otchet_sostavlen_po_pravilam(o: Otchet)` | `evaluate truth(otchet_sostavlen_po_pravilam(o: <o>));` | — | 1 test |
| `otchet-prilozhenie-3` | Is the report formatted according to annex 3 (title page, cl. 1 information, values and quantities, attachments, final figure, certification, endorsements)? | truth | `otchet_oformlen_po_prilozheniyu_3(o: Otchet)` | `evaluate truth(otchet_oformlen_po_prilozheniyu_3(o: <o>));` | — | 1 test |
| `otchet-titulnyy-list` | Is the report's title page complete (the eight elements of annex 3, with field values)? | truth | `otchet_soderzhit_titulnyy_list(o: Otchet)` | `evaluate truth(otchet_soderzhit_titulnyy_list(o: <o>));` | — | 4 tests |
| `otchet-zaveren` | Is the report certified: by seal and signature, or by signature alone when the absence of a seal is established? | truth | `otchet_zaveren(o: Otchet)` | `evaluate truth(otchet_zaveren(o: <o>));` | seal and signature (`OtchetZaverenPechatyuIPodpisyu`); signature without a seal when its absence is established (`OtchetZaverenPodpisyuBezPechati`) | 2 tests |
| `otchet-stoimosti-i-obemy` | Does the report contain the calculation particulars: the costs of work, materials, parts, and the quantities? | truth | `otchet_soderzhit_stoimosti_i_obemy(o: Otchet)` | `evaluate truth(otchet_soderzhit_stoimosti_i_obemy(o: <o>));` | — | 3 tests |
| `otchet-prilozheniya` | Does the report contain the three attachments named by annex 3? | truth | `otchet_soderzhit_prilozheniya(o: Otchet)` | `evaluate truth(otchet_soderzhit_prilozheniya(o: <o>));` | — | 2 tests |
| `otchet-itogovaya-velichina` | Is the final damage figure stated as a whole number of tenge? | truth | `otchet_soderzhit_itogovuyu_velichinu(o: Otchet)` | `evaluate truth(otchet_soderzhit_itogovuyu_velichinu(o: <o>));` | round(amount, 0, "HALF_UP") == amount — checks the absence of a fractional part; the rounding mode is not selected (§50) (`OtchetSoderzhitItogovuyuVelichinu`) | 4 tests |

- **Does not answer:** What is the payout amount when the report is not delivered on time? — the source refers outward (VRED_TS_PT_3). The payout amount for non-delivery of the report is not computed: cl. 3-1 of art. 22 of the Law; only the right to such a payout is computed. Related question: `pravo-na-vyplatu-3-1`.
- **Does not answer:** How is the final figure rounded to tenge? — the source refers outward (VRED_TS_PRIL_3). Rounding of the final figure to tenge is not performed: annex 3 requires rounding but does not name a mode (§50); only the absence of a fractional part is checked. Related question: `otchet-itogovaya-velichina`.
- **Does not answer:** How are the business days of the cl. 3 deadlines counted: from the next day, with a carry-over to a business day? — this needs data that the case supplies (VRED_TS_PT_3). The rule for counting deadlines (§86) is not declared by the norm: the Rules name the deadlines, while the policy and the official-calendar snapshot §85 arrive as case input; without a snapshot in the world, the answer is MISSING_INPUT. Related question: `predel-otmetki`. Civil Code of the RK art. 173, 176; the scenario tests/otchet/16-srok-bez-kalendarya.lawtest verifies the ABSENCE of a calendar in the world.
- **Does not answer:** What status does a deadline question receive when the date falls outside the calendar snapshot? — a limitation of the language or the engine (VRED_TS_PT_3). A date outside the calendar snapshot: both implementations answer MISSING_INPUT with the code CALENDAR_OUT_OF_RANGE, while prose §175, in the E-0105 list, names RUNTIME_ERROR — a SPEC gap (SPEC-1); the scenario locks in the code and NEITHER, not the status. Related question: `predel-otmetki`.

## Inspection and the inspection report

Source units: VRED_TS_PT_2, VRED_TS_PT_7, VRED_TS_PRIL_2.

| id | question | form | goal | template | branches | verified |
|---|---|---|---|---|---|---|
| `osmotr-vozmozhen` | Are all seven conditions for the inspection's feasibility met (cl. 7)? | truth | `osmotr_vozmozhen(r: RaschetVreda)` | `evaluate truth(osmotr_vozmozhen(r: <r>));` | — | 2 tests |
| `osmotr-dopustim` | Is the inspection admissible: when determining the repair cost, only with documents on the damage from the traffic accident? | truth | `osmotr_dopustim(r: RaschetVreda)` | `evaluate truth(osmotr_dopustim(r: <r>));` | the repair cost is being determined and the documents are submitted (`OsmotrDopustimPriOpredeleniiStoimostiRemonta`); the repair cost is not being determined (`OsmotrDopustimVneOpredeleniyaStoimostiRemonta`); an established absence of the documents — inadmissibility (a negative conclusion) (`OsmotrNedopustimBezDokumentovODtp`) | 5 tests |
| `osmotr-oformlen` | Is the inspection properly documented by a report? | truth | `osmotr_oformlen(r: RaschetVreda)` | `evaluate truth(osmotr_oformlen(r: <r>));` | — | 1 test |
| `akt-prilozhenie-2` | Does the inspection report contain all the information of annex 2 (as field values: VIN, license plate, mileage, dates, defects)? | truth | `akt_soderzhit_svedeniya_prilozheniya_2(a: AktOsmotra)` | `evaluate truth(akt_soderzhit_svedeniya_prilozheniya_2(a: <a>));` | — | 5 tests |
| `akt-svedeniya-o-ts` | Is the report's information about the vehicle complete (cl. 4 of annex 2, odometer photo where available)? | truth | `akt_soderzhit_svedeniya_o_ts(a: AktOsmotra)` | `evaluate truth(akt_soderzhit_svedeniya_o_ts(a: <a>));` | — | 3 tests |
| `akt-predstavivshee-litso` | Is the report's information about the person who presented the vehicle for inspection complete (cl. 3 of annex 2)? | truth | `akt_soderzhit_svedeniya_o_predstavivshem_lice(a: AktOsmotra)` | `evaluate truth(akt_soderzhit_svedeniya_o_predstavivshem_lice(a: <a>));` | — | 1 test |
| `akt-povrezhdennye-elementy` | Is the report's information about the damaged elements complete (cl. 5 of annex 2)? | truth | `akt_soderzhit_svedeniya_o_povrezhdennykh_elementakh(a: AktOsmotra)` | `evaluate truth(akt_soderzhit_svedeniya_o_povrezhdennykh_elementakh(a: <a>));` | — | 1 test |
| `dopolnitelnyy-osmotr` | Was the additional inspection conducted according to the rules: on a proper application, by the insurer, with a report? | truth | `dopolnitelnyy_osmotr_proveden_po_pravilam(r: RaschetVreda)` | `evaluate truth(dopolnitelnyy_osmotr_proveden_po_pravilam(r: <r>));` | — | 1 test |
| `korrektirovka-skrytye-defekty` | Is the calculation correction for hidden defects documented as an addendum to the report? | truth | `korrektirovka_pri_skrytykh_defektakh_oformlyaetsya_dopolneniem(r: RaschetVreda)` | `evaluate truth(korrektirovka_pri_skrytykh_defektakh_oformlyaetsya_dopolneniem(r: <r>));` | — | 4 tests |
| `pozitsii-osmotr-na-sto` | Is the insurer obligated to conduct the inspection at a service station at the injured party's request, and has the obligation been performed? | positions | rule `OsmotrNaStantsii` | `evaluate positions(); expect position(OsmotrNaStantsii, <status>);` | — | 2 tests |

- **Does not answer:** Within what deadline is the insurer obligated to conduct the inspection and draw up the report? — the source refers outward (VRED_TS_PT_3). The deadline for the inspection and drawing up the inspection report is not computed: the first part of cl. 3 hands it off to cl. 3 of art. 22 of the Law, and no pinned bytes of the Law are in the package. Related question: `pozitsii-osmotr-na-sto`. The obligation to inspect at a service station is derived with an open window: it does not become violated by deadline.

## Who conducts the calculation and how it is organized

Source units: VRED_TS_PT_2, VRED_TS_PT_4, VRED_TS_PT_4_1, VRED_TS_PT_6, VRED_TS_PRIL_1.

| id | question | form | goal | template | branches | verified |
|---|---|---|---|---|---|---|
| `raschet-po-pravilam` | Is the calculation conducted according to the Rules, and by whom: the insurer or an engaged appraiser? | truth | `raschet_vedetsya_po_pravilam(r: RaschetVreda)` | `evaluate truth(raschet_vedetsya_po_pravilam(r: <r>));` | the calculation is carried out by the insurer (`RaschetStrakhovshchikom`); the calculation is carried out by an appraiser engaged under a contract (cl. 4) (`RaschetOtsenshchikom`) | 2 tests |
| `organizatsiya-rascheta` | Has the calculation's organization been completed: have the three stages of cl. 6 been passed? | truth | `organizatsiya_rascheta_vypolnena(r: RaschetVreda)` | `evaluate truth(organizatsiya_rascheta_vypolnena(r: <r>));` | — | 2 tests |
| `vybor-otsenshchikov` | Is the injured party provided a choice of at least two appraisers? | truth | `vybor_otsenshchikov_obespechen(r: RaschetVreda)` | `evaluate truth(vybor_otsenshchikov_obespechen(r: <r>));` | at least two are offered (>= 2) (`VyborOtsenshchikovObespechen`); fewer than two are offered — a defeasible negation (`VyborOtsenshchikovNeObespechen`) | 6 tests |
| `pozitsii-dva-otsenshchika` | Has the insurer's obligation to offer the injured party a choice of two appraisers been performed? | positions | rule `PredlozhitDvukhOtsenshchikov` | `evaluate positions(); expect position(PredlozhitDvukhOtsenshchikov, <status>);` | — | 2 tests |
| `pozitsii-poterpevshiy` | What is the status of the injured party's obligations from the day of the application: to preserve the property and to provide the opportunity for the calculation? | positions | rules `SokhranitImushchestvo`, `PredostavitVozmozhnostRascheta` | `evaluate positions(); expect position(SokhranitImushchestvo, <status>); expect position(PredostavitVozmozhnostRascheta, <status>);` | — | 2 tests |

- `pozitsii-poterpevshiy`: Preservation of the property is a maintenance obligation §124.2: altering the property after the accident yields VIOLATED.

## Availability of the wear calculation

Source units: VRED_TS_PT_11.

| id | question | form | goal | template | branches | verified |
|---|---|---|---|---|---|---|
| `pozitsii-raschet-iznosa` | Is the possibility of the wear calculation provided by the insurance ombudsman and the insurer (cl. 11)? | positions | rules `ObespechitRaschetIznosaOmbudsmanom`, `ObespechitRaschetIznosaStrakhovshchikom` | `evaluate positions(); expect position(ObespechitRaschetIznosaOmbudsmanom, <status>); expect position(ObespechitRaschetIznosaStrakhovshchikom, <status>);` | — | 2 tests |

## Inferable items without their own card

Inference links: queried through the cards above, named here for the completeness of the surface in both directions.

| predicate | why without a card |
|---|---|
| `detal_ne_povrezhdalas_i_ne_remontirovalas` | The cl. 10 condition, as two facts; read by the rules of detal_otsenivaetsya_bez_iznosa, queried through the card detal-bez-iznosa (t12). |
| `dopolnitelnyy_osmotr_oformlen` | A link of the additional inspection; queried through dopolnitelnyy_osmotr_proveden_po_pravilam (t10-d). |
| `otchet_predostavlen_v_dopustimom_vide` | Paper or electronic form (§206); a link of otchet_sostavlen_po_pravilam (KZ-VRED-27). |
| `otchet_soderzhit_otmetki` | Both endorsements of cl. 3; a link of otchet_oformlen_po_prilozheniyu_3 (t20-a). |
| `otchet_soderzhit_svedeniya_punkta_1` | The cl. 1 information of annex 3; a link of otchet_oformlen_po_prilozheniyu_3 (t20-a). |
| `otchet_utverzhden` | Approval by the head or an authorized person (§206); a link of otchet_sostavlen_po_pravilam (KZ-VRED-27). |
| `otmetka_prostavlena` | An endorsement of agreement or of disagreement with reasons (§206); a link of the obligation ProstavitOtmetku (KZ-VRED-13, KZ-VRED-14). |
| `raschet_osushchestvlyaet_otsenshchik` | The engaged appraiser of cl. 4; a link of raschet_vedetsya_po_pravilam (KZ-VRED-22). |
| `srok_otmetki_poterpevshego` | The normative deadline constant (3 business days, assert fact); read by the rule PredelOtmetkiPoterpevshego. |
| `srok_otveta_strakhovshchika` | The normative deadline constant (3 business days, assert fact); read by the rule PredelOtvetaStrakhovshchika. |
| `srok_predostavleniya_otcheta` | The normative deadline constant (5 business days, assert fact); read by the rule PredelPredostavleniyaOtcheta. |
| `trebovanie_o_foto_odometra_soblyudeno` | The proviso "odometer photo where available," by two rules; a link of akt_soderzhit_svedeniya_o_ts (t09-c, t09-d). |
| `zayavlenie_soderzhit_svedeniya_prilozheniya_1` | The application's composition per annex 1; a link of the additional inspection and of organizing the calculation (t10-d, KZ-VRED-25). |

## Summary

41 cards, 6 boundaries, 13 internal links; 43 inferable predicates in the CLIR, 12 rules — the surface is closed in both directions. Reasons for a specific case are taken not from the catalog but from the issues and why_not of the answer.
