# Reporter Batch Results — Case-by-Case QA and Codex Improvement Instructions

## Executive summary

This QA reviews only `reporter_batch_results.json` / `reporter_batch_results.txt`. The batch ran 50/50 without hard runtime failures, but semantic accuracy remains uneven: many reports are well formatted yet clinically misrepresent the seed through wrong indication text, loss of action type, under-specified multi-step procedures, and generic closing plans.

### Quick scoring rubric

- **4/4 – Usable with minor edits:** Core procedure and clinically important details are preserved.
- **3/4 – Moderate revision:** Generally recognizable and salvageable, but missing important details or using generic/weak summaries.
- **2/4 – Major revision:** Clinically important fields are wrong or incomplete; substantial editing required.
- **1/4 – Critical revision:** Report structure may exist, but the procedure is materially misrepresented.

## Case-by-case QA

| Case | QA score | Verdict | Main issues | Recommended fix |
|---|---:|---|---|---|
| 1 | 2/4 | Major revision | Indication/preop/postop incorrectly use disposition text ('3 day pneumothorax watch'); JSON overcounts valves and mislabels CV assessment. | Prioritize disease/procedure indication over follow-up logistics; count each valve once; map 'CV negative' to absent collateral ventilation. |
| 2 | 3/4 | Moderate revision | Body captures bilateral TPCs, but impression only summarizes right side; awkward wording ('drained drained'); extraction underpopulates pleural procedure fields. | Summarize both laterality-specific procedures and outcomes; clean duplicated text; ensure bilateral TPCs populate structured pleural fields. |
| 3 | 2/4 | Major revision | Multi-step case partly captured, but indication is clumsy, pleural catheter brand becomes 'Other catheter,' and pleural coding/action remains ambiguous. | Use explicit multi-procedure template; preserve TPC identity and malignant effusion indication; keep airway and pleural components separately billable/structured. |
| 4 | 4/4 | Usable with minor edits | Strong overall fidelity; minor generic wording and plan boilerplate. | Keep exact sample tools/results and suppress generic plan text unless truly warranted. |
| 5 | 3/4 | Moderate revision | Procedure body is good, but indication/pre/post reduced to 'restaging' and pleural catheter is not fully represented in extraction. | Prefer richer indication text and ensure combined bronch + pleural procedures both populate structured outputs. |
| 6 | 1/4 | Critical revision | Stent removal case is mislabeled as stent placement, foreign-body language appears, and indication/pre/post become '6 months post radiation.' | Distinguish placement vs removal vs exchange from action verbs; never recast removed stents as foreign bodies unless truly aspirated objects. |
| 7 | 3/4 | Moderate revision | Captures main procedure, but indication truncates to 'RML 2' and eccentric-to-concentric adjustment/ROSE result are underrepresented. | Preserve lesion size phrase and trajectory adjustments; carry ROSE summary into report and structured extraction. |
| 8 | 3/4 | Moderate revision | Narrative is solid, but structured bundle records DNase as 10 mg instead of 5 mg. | Add numeric dose validation against prompt text and reject mismatched paired-drug doses. |
| 9 | 2/4 | Major revision | Hemoptysis is incorrectly placed in complications, and generic pathology/chest imaging plan is not procedure-specific. | Treat presenting bleeding as indication unless a new procedural complication occurs; use hemostasis-specific follow-up language. |
| 10 | 3/4 | Moderate revision | Overall good, but plan is generic and therapeutic interventions line underrepresents electrocautery/debulking. | Reflect all major therapeutic components in both body and impression. |
| 11 | 3/4 | Moderate revision | Misses snare resection in procedure list and defaults to generic plan despite therapeutic bronch details. | Capture all modalities: snare, APC, dilation, hemostasis, lumen restoration, pathology specimen. |
| 12 | 2/4 | Major revision | Clear thoracentesis indication is replaced with 'Not documented'; generic post-procedure plan omits specimen testing details. | Never emit 'Not documented' when an effusion indication exists; preserve test list and stop reason. |
| 13 | 3/4 | Moderate revision | EBUS structure is good, but ROSE negativity/adequacy is incompletely propagated and plan is generic. | Carry ROSE adequacy/negative findings across all stations and use staging-specific closing language. |
| 14 | 3/4 | Moderate revision | Good core EBUS output, but lymphoma-specific details (19G passes, flow/IHC/core intent) are incompletely preserved. | Use disease-specific sampling templates for lymphoma workups with dedicated specimen/test sections. |
| 15 | 2/4 | Major revision | Indication/pre/post become '2 hours'; misses additional 200 mL after unclamping and pain-management details. | Do not let timing phrases override diagnosis; sum serial drainage events and preserve pleurodesis-related symptoms/management. |
| 16 | 4/4 | Usable with minor edits | Good fidelity overall; minor generic impression language. | Prefer exact tool-in-lesion wording when CBCT shows adjacent lesion with eccentric rEBUS. |
| 17 | 4/4 | Usable with minor edits | Strong EBUS capture with direct hilar mass and nodal stations. | Add clearer separation between hilar mass sampling and nodal staging in impression. |
| 18 | 3/4 | Moderate revision | Laser case is under-described and omits complete resection/patency emphasis in plan. | Use modality-specific templates for Nd:YAG photoresection and preserve endoscopic completeness/hemostasis/patency. |
| 19 | 2/4 | Major revision | Correct valves listed, but target lobe becomes placeholder text ('target lobe') and plan is generic. | For BLVR assessment + placement, carry final selected lobe explicitly into all sections and avoid generic pathology boilerplate. |
| 20 | 2/4 | Major revision | Combined robotic bronchoscopy + thoracoscopy is under-summarized; pleural biopsies are undercounted (4 vs 6) and impression ignores thoracoscopy/pleurodesis. | Use multi-step composite template; validate counts across all procedure components; summarize every major intervention in final plan. |
| 21 | 4/4 | Usable with minor edits | Strong output; minor generic staging language. | Retain GGO-specific nuance and ROSE atypical wording in summary. |
| 22 | 2/4 | Major revision | Therapeutic mucus-plugging case collapses to BAL/washing and loses suctioning, NAC, restored patency, and re-expansion result. | Create dedicated secretion-clearance template distinct from BAL; preserve therapeutic goal/outcome statements. |
| 23 | 3/4 | Moderate revision | Valve-removal body is acceptable, but final plan is generic and ignores air-leak resolution/chest-tube course. | Use removal-specific disposition text with air-leak resolution and future candidacy planning. |
| 24 | 3/4 | Moderate revision | Foreign-body removal body is decent, but final plan is generic pathology/chest imaging despite no pathology rationale. | Use procedure-specific recovery language for foreign-body extraction. |
| 25 | 4/4 | Usable with minor edits | Good thoracoscopy structure; impression could better reflect malignant effusion/pleurodesis intent. | Promote clinically salient thoracoscopic findings into impression. |
| 26 | 4/4 | Usable with minor edits | Good thoracoscopy narrative; could preserve port site and ROSE atypia more explicitly. | Include entry site and ROSE result in findings/impression. |
| 27 | 1/4 | Critical revision | Whole lung lavage fails completely: procedure says 'See procedure details below' with no actual details and generic plan. | Build a dedicated whole-lung-lavage template and block empty-detail outputs in QA. |
| 28 | 2/4 | Major revision | Bilateral-target robotic case body includes both lesions, but indication/pre/post/specimens/impression only summarize RUL target. | For multi-target cases, require all targets in diagnosis, specimens, and final impression. |
| 29 | 4/4 | Usable with minor edits | Good overall stenosis case capture; follow-up timing not emphasized. | Preserve follow-up interval and final lumen explicitly in impression. |
| 30 | 3/4 | Moderate revision | Good procedural body, but anesthesia and complication fields may understate intraprocedural bleeding significance; final plan remains generic. | Differentiate expected managed bleeding from no-complication summary and tailor post-bleed monitoring language. |
| 31 | 2/4 | Major revision | Indication/pre/post become 'diagnosis and pleurodesis' rather than pleural disease context; ROSE mesothelioma clue not integrated into impression. | Prioritize disease indication over procedural purpose and carry high-value bedside diagnostic impressions forward. |
| 32 | 3/4 | Moderate revision | Percutaneous pleural biopsy mostly okay, but Abrams-specific and specimen-test details are thin and plan is generic. | Use pleural-biopsy-specific template with test dispatch and minor-oozing documentation. |
| 33 | 2/4 | Major revision | BLVR case incorrectly uses 'observation' as indication/pre/post instead of emphysema/BLVR treatment context. | Filter out observation/monitoring phrases from diagnostic fields; keep them only in disposition/plan. |
| 34 | 4/4 | Usable with minor edits | Stent placement case is largely faithful. | Carry fluoroscopic confirmation and patent downstream lobes into impression. |
| 35 | 4/4 | Usable with minor edits | Staging EBUS appears strong. | Keep extrinsic compression finding in airway survey/impression. |
| 36 | 3/4 | Moderate revision | Likely captures cryo/airway work, but should explicitly preserve spray cryo cycles and follow-up bronchoscopy timing. | Create cryotherapy modality fields for extraction vs spray cycles. |
| 37 | 4/4 | Usable with minor edits | Strong benign tracheal stenosis case. | Keep clock-face incision details and mitomycin concentration/time in structured output. |
| 38 | 4/4 | Usable with minor edits | ILD cryobiopsy case appears strong. | Preserve lobe/subsegment sample distribution, Fogarty use, and controlled bleeding in final summary. |
| 39 | 3/4 | Moderate revision | Mixed therapeutic bronch + BLVR evaluation should emphasize that no valves were placed today. | Use assessment-only BLVR template when Chartis performed without valve deployment. |
| 40 | 4/4 | Usable with minor edits | Sarcoid EBUS staging likely strong. | Include granulomatous ROSE pattern in impression. |
| 41 | 4/4 | Usable with minor edits | Robotic repeat-CBCT reposition case appears good. | Preserve iterative targeting sequence and repeat ROSE change in summary. |
| 42 | 4/4 | Usable with minor edits | Large mass + staging case appears strong. | Ensure malignant nodal station is highlighted in impression. |
| 43 | 2/4 | Major revision | BAL/TBBx ILD case mislabels biopsy target as RML instead of RLL and loses aliquot/return details. | Validate that BAL and biopsy locations may differ; preserve lavage volumes/return and bleeding/PTX monitoring. |
| 44 | 3/4 | Moderate revision | BLVR placement body is good, but plan is generic pathology/chest imaging instead of BLVR monitoring language. | Use BLVR-specific disposition/monitoring summary and suppress irrelevant pathology boilerplate. |
| 45 | 2/4 | Major revision | Valve removal/replacement case sets indication/pre/post to 'Not documented' and misses migrated valve nuance in summary. | Use action-aware BLVR revision template with migrated-valve retrieval details. |
| 46 | 2/4 | Major revision | Central airway obstruction case undercaptures coring/snare/debulking and even mislocates APC to LUL instead of left mainstem region. | Preserve exact anatomic site and every debulking modality; prohibit inferred location drift. |
| 47 | 2/4 | Major revision | TPC case records only the additional 500 mL instead of total 2000 mL and uses 'Other catheter' wording. | Track initial plus interval drainage totals and preserve catheter identity/education details. |
| 48 | 2/4 | Major revision | IPC removal indication/pre/post become '4 months, spontaneous pleurodesis achieved'; plan is generic and irrelevant. | Separate dwell time from indication; use removal-specific disposition without pathology/chest-imaging boilerplate. |
| 49 | 3/4 | Moderate revision | Combined EBUS/EUS-B is represented as EBUS-only stations 4R/7/8/9; modality distinction is lost. | Add EUS-B as separate structured procedure with station-level source modality. |
| 50 | 4/4 | Usable with minor edits | Assessment-only Chartis case is appropriately represented and clearly aborted without valve placement. | Keep aborted/procedure-not-performed language distinct from failed procedure wording. |

## Highest-priority Codex instructions

- **Never let disposition text overwrite diagnosis.** Phrases such as “observation,” “3 day pneumothorax watch,” “2 hours,” “restaging,” or “follow-up planned 6 weeks” must not become the indication, preoperative diagnosis, or postoperative diagnosis when a real clinical indication is present.
- **Do not emit `Not documented` when the seed contains a usable indication or diagnosis.** If the prompt names emphysema, malignant pleural effusion, ILD, PAP, hemoptysis, tracheal stenosis, or a lesion/mass/nodule, that disease/process should populate the diagnostic fields.
- **Infer the procedure action from verbs, not from device names alone.** Distinguish placement vs removal vs exchange vs revision; debulking vs ablation vs dilation; assessment-only Chartis vs BLVR valve deployment; BAL vs therapeutic secretion clearance vs whole-lung lavage.
- **Use composite templates for multi-step procedures.** If the seed contains more than one major procedure family (for example bronchoscopy + EBUS + tunneled pleural catheter, or robotic bronchoscopy + medical thoracoscopy), the final report must preserve every major component in the procedure list, detail section, specimens, and impression/plan.
- **Require exact preservation of laterality, lobe, segment, and nodal station.** Do not move a biopsy from RLL to RML, do not replace RUL with `target lobe`, and do not convert a tracheal/left mainstem intervention into LUL wording.
- **Preserve all quantified details exactly.** Validate sample counts, valve counts, valve sizes, stent sizes, biopsy counts, fluid volumes, serial drainage totals, drug doses, dwell/clamp times, and pass counts against the seed text before finalizing.
- **Summarize all targets in multi-target procedures.** If two lesions, bilateral procedures, or multiple pleural interventions were performed, each target must appear in diagnosis, procedures, specimens, and impression.
- **Do not use generic closing plans by default.** Suppress boilerplate like `Await final pathology and cytology` and `obtain post-procedure chest imaging` unless it is appropriate for that specific procedure and supported by the seed.
- **Use modality-specific templates for special procedures.** Whole-lung lavage, cryospray, foreign-body removal, IPC removal, talc slurry via catheter, EUS-B staging, and therapeutic mucus-plug bronchoscopy need dedicated templates rather than fallback bronchoscopy text.
- **Differentiate indication from complication.** Presenting hemoptysis, known pneumothorax prompting valve removal, or known pleural effusion are not new procedural complications unless the procedure caused a new adverse event.
- **Add a final self-check pass before report release.** Confirm: (1) diagnostic fields reflect disease not logistics, (2) action type matches the seed, (3) every major step is preserved, (4) counts/doses/totals are correct, (5) plan text is procedure-specific.

## Suggested Codex implementation prompt

```text
You are validating and revising an interventional pulmonology procedure report generated from a compact seed.

Your job is not just to produce polished prose. Your job is to preserve the seed truth exactly.

Hard rules:
1. The indication, preoperative diagnosis, and postoperative diagnosis must reflect the underlying disease / lesion / airway or pleural process, not logistics, monitoring, timing phrases, or follow-up plans.
2. Never output “Not documented” if the seed contains a clinically usable indication.
3. Infer action type from verbs:
   - placed / deployed = placement
   - removed / extracted = removal
   - removed and replaced / exchanged = exchange
   - assessed only = assessment without treatment
4. Preserve every major procedure family present in the seed. Do not collapse multi-step cases into one dominant procedure.
5. Preserve laterality, lobe, segment, nodal station, device type, device size, pass counts, sample counts, fluid volumes, drug doses, serial drainage totals, and major outcomes exactly.
6. If there are two or more targets or bilateral procedures, summarize all of them in the procedure list, specimens, and final impression/plan.
7. Do not invent generic pathology follow-up or chest imaging language unless that workflow is specifically supported by the seed or procedure type.
8. Distinguish the presenting problem from a procedural complication. A pre-existing hemoptysis or pneumothorax is not automatically a complication caused by the procedure.
9. If the seed describes a specialized procedure (whole-lung lavage, EUS-B, IPC removal, cryospray, talc slurry via catheter, secretion-clearance bronchoscopy), use a dedicated template and do not fall back to generic bronchoscopy text.
10. Before finalizing, run a self-check:
   - Are the diagnostic fields clinically correct?
   - Does the action type match the seed?
   - Are all major steps preserved?
   - Are all numbers correct?
   - Is the final plan specific and relevant?

If any of these checks fail, revise before returning the report.
```

## Recommended engineering changes

- Add a **field-priority parser** so diagnostic fields prefer disease/problem entities over disposition/time entities.
- Add **action-type classifiers** for valve/stent/catheter workflows with strong lexical triggers for placement, removal, exchange, and assessment-only cases.
- Add **count-and-dose consistency checks** comparing seed numbers against final markdown and structured JSON.
- Add a **multi-procedure completeness validator** that flags any seed mentioning more than one major procedure family if the impression/plan or procedure list omits one.
- Add a **location consistency validator** to catch drift between BAL location, biopsy location, stent location, and lesion location.
- Add **template guards** for whole-lung lavage and other rare procedures so empty fallback text cannot pass QA.
- Add **boilerplate suppression rules** so pathology/cytology or chest-imaging recommendations appear only when context-appropriate.