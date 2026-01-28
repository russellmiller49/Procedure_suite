# Procedure Suite — gitingest (details)

Generated: `2026-01-28T13:25:43-08:00`
Git: `main` @ `dbb6e32`

## What this file is
- A **second** document you can provide to an LLM when more detail is needed.
- Focuses on **text-readable** code/docs and skips binaries, oversized files, and (best-effort) minified bundles.

## Selection settings
- Include dirs: `modules/, proc_nlp/, proc_schemas/, config/, scripts/, tests/, docs/`
- Include extensions: `.j2`, `.jinja`, `.js`, `.json`, `.md`, `.py`, `.toml`, `.ts`, `.txt`, `.yaml`, `.yml`
- Max file size: `200000` bytes
- Inline mode: `curated`
- Inline cap (files): `75`

## Manifest (filtered candidates)

```
      540  scripts/test_debulk.py
      697  scripts/generate_blank_granular_note_scripts.py
      988  scripts/render_report.py
     1026  scripts/prepare_data.py
     1173  scripts/merge_registry.py
     1351  scripts/validate_jsonschema.py
     1430  scripts/cpt_check.py
     1505  scripts/check_pydantic_models.py
     1609  scripts/preflight.py
     1728  scripts/verify_registry_runtime_bundle.py
     1833  scripts/check_onnx_inputs.py
     1918  scripts/patch.py
     2032  scripts/evaluate_cpt.py
     2073  scripts/clean_ner.py
     2224  scripts/self_correct_registry.py
     2273  scripts/verify_phi_redactor_vendor_assets.py
     2368  scripts/prodigy_prepare_registry_batch.py
     2998  scripts/phi_audit.py
     3095  scripts/create_blank_update_scripts_from_patient_note_texts.py
     3216  scripts/find_phi_failures.py
     3233  scripts/train_registry_sklearn.py
     3330  scripts/build_hard_negative_patch.py
     3766  scripts/apply_immediate_logic_fixes.py
     3869  scripts/prodigy_cloud_sync.py
     4064  scripts/run_python_update_scripts.py
     4248  scripts/generate_addon_templates.py
     4293  scripts/training.py
     4371  scripts/warm_models.py
     4406  scripts/build_phi_allowlist_trie.py
     4520  scripts/run_coder_hybrid.py
     4649  scripts/refine_ner_labels.py
     5160  scripts/fix_registry_hallucinations.py
     5248  scripts/force_merge_human_labels.py
     5264  scripts/split_phi_gold.py
     5339  scripts/validate_ner_alignment.py
     5450  scripts/sanitize_platinum_spans.py
     5540  scripts/build_registry_bundle.py
     5847  scripts/validate_knowledge_release.py
     5928  scripts/ingest_phase0_data.py
     5946  scripts/normalize_phi_labels.py
     6097  scripts/bootstrap_granular_ner_bundle.py
     6388  scripts/bootstrap_phi_redactor_vendor_bundle.py
     6413  scripts/add_training_case.py
     6444  scripts/eval_registry_granular.py
     6716  scripts/knowledge_diff_report.py
     6757  scripts/merge_registry_prodigy.py
     6875  scripts/prodigy_export_registry.py
     6884  scripts/clear_unannotated_prodigy_batch.py
     7110  scripts/merge_registry_human_labels.py
     7169  scripts/create_slim_branch.py
     7302  scripts/generate_teacher_logits.py
     7609  scripts/regenerate_granular_ner_stats.py
     7735  scripts/code_validation.py
     7803  scripts/dedupe_granular_ner.py
     7994  scripts/export_phi_gold_standard.py
     8166  scripts/export_patient_note_texts.py
     8191  scripts/test_phi_redaction_sample.py
     8397  scripts/prodigy_prepare_registry_relabel_batch.py
     9036  scripts/find_critical_failures.py
     9076  scripts/fit_thresholds_from_eval.py
     9264  scripts/clean_distilled_phi_labels.py
     9583  scripts/registry_label_overlap_report.py
     9603  scripts/align_synthetic_names.py
     9739  scripts/registry_pipeline_smoke.py
    10358  scripts/diamond_loop_cloud_sync.py
    11238  scripts/evaluate_coder.py
    11262  scripts/scrub_golden_jsons.py
    11519  scripts/prodigy_export_corrections.py
    12126  scripts/export_phi_model_for_transformersjs.py
    12153  scripts/convert_spans_to_bio.py
    13507  scripts/extract_ner_from_excel.py
    14532  scripts/review_llm_fallback_errors.py
    14742  scripts/quantize_to_onnx.py
    14760  scripts/unified_pipeline_batch.py
    15511  scripts/verify_registry_human_data.py
    15806  scripts/sanitize_dataset.py
    16360  scripts/apply_platinum_redactions.py
    16447  scripts/registry_pipeline_smoke_batch.py
    16517  scripts/generate_gitingest.py
    16578  scripts/eval_hybrid_pipeline.py
    16862  scripts/label_neg_stent.py
    17034  scripts/prodigy_prepare_phi_batch.py
    18193  scripts/build_model_agnostic_phi_spans.py
    18203  scripts/generate_synthetic_phi_data.py
    20528  scripts/audit_model_fp.py
    20931  scripts/train_roberta_pm3.py
    23467  scripts/fix_alignment.py
    24804  scripts/train_distilbert_ner.py
    25261  scripts/prodigy_prepare_registry.py
    26361  scripts/train_registry_ner.py
    27149  scripts/golden_to_csv.py
    34569  scripts/validate_golden_extractions.py
    37440  scripts/distill_phi_labels.py
    48966  scripts/train_roberta.py
      272  scripts/phi_test_node/package.json
    10951  scripts/phi_test_node/results.txt
    37995  scripts/phi_test_node/package-lock.json
        0  tests/unit/__init__.py
       16  config/__init__.py
       17  tests/ml_coder/__init__.py
       22  tests/phi/__init__.py
       24  modules/coder/adapters/__init__.py
       24  tests/integration/api/__init__.py
       26  tests/helpers/__init__.py
       26  tests/integration/coder/__init__.py
       28  modules/agents/parser/__init__.py
       28  tests/utils/__init__.py
       32  modules/agents/structurer/__init__.py
       32  modules/agents/summarizer/__init__.py
       32  tests/integration/persistence/__init__.py
       35  tests/ml_advisor/__init__.py
       37  modules/domain/__init__.py
       39  modules/registry/processing/__init__.py
       46  tests/integration/test_placeholder.py
       50  modules/registry/audit/__init__.py
       51  modules/api/routes/__init__.py
       56  modules/registry/evidence/__init__.py
       57  modules/extraction/postprocessing/__init__.py
       58  modules/registry/pipelines/__init__.py
       58  modules/registry/slots/__init__.py
       61  modules/agents/__init__.py
       68  proc_schemas/shared/__init__.py
       71  modules/extraction/__init__.py
       72  modules/domain/procedure_store/__init__.py
       75  modules/coder/domain_rules/registry_to_cpt/__init__.py
       90  modules/registry/extraction/__init__.py
       94  modules/__init__.py
      113  modules/domain/text/__init__.py
      116  modules/coder/adapters/persistence/__init__.py
      123  modules/domain/reasoning/__init__.py
      123  modules/domain/rvu/__init__.py
      132  modules/registry/legacy/__init__.py
      133  modules/common/rules_engine/__init__.py
      135  proc_schemas/registry/__init__.py
      147  modules/registry/legacy/adapters/__init__.py
      166  tests/__init__.py
      169  modules/api/adapters/__init__.py
      169  modules/registry/adapters/__init__.py
      182  modules/common/__init__.py
      191  modules/domain/knowledge_base/__init__.py
      194  modules/infra/__init__.py
      200  modules/reporter/__init__.py
      201  modules/registry/extractors/__init__.py
      215  modules/llm/__init__.py
      219  modules/registry/adapters/v3_to_v2.py
      226  modules/coder/adapters/llm/__init__.py
      226  modules/phi/__init__.py
      280  modules/registry/schema/ebus_events.py
      314  modules/coder/application/__init__.py
      314  modules/reporting/templates/addons/__init__.py
      315  modules/reporting/second_pass/__init__.py
      318  modules/coder/adapters/nlp/__init__.py
      333  modules/reporter/engine.py
      336  modules/api/services/__init__.py
      337  tests/ml_coder/test_registry_label_schema.py
      340  tests/helpers/phi_asserts.py
      359  tests/unit/test_cpt_cleaning.py
      369  modules/coder/domain_rules/registry_to_cpt/types.py
      373  tests/unit/test_templates.py
      393  modules/reporting/second_pass/station_consistency.py
      398  modules/coder/adapters/llm/noop_advisor.py
      413  modules/ner/__init__.py
      458  tests/coder/test_registry_to_cpt_rules_pure_registry.py
      482  modules/phi/safety/__init__.py
      490  modules/agents/structurer/structurer_agent.py
      508  modules/registry/extractors/noop.py
      529  tests/e2e/test_registry_e2e.py
      533  modules/registry/ner_mapping/__init__.py
      541  modules/registry/deterministic/__init__.py
      545  modules/registry_cleaning/__init__.py
      553  tests/registry/test_registry_to_cpt_airway_stent_assessment_only.py
      554  modules/registry/schema/ip_v3.py
      561  tests/registry/test_keyword_guard_high_conf_bypass.py
      565  modules/coder/code_families.py
      573  modules/phi/adapters/__init__.py
      576  modules/api/__init__.py
      579  tests/scripts/test_audit_model_fp_logic.py
      602  modules/infra/executors.py
      610  modules/infra/safe_logging.py
      615  modules/reporting/second_pass/counts_backfill.py
      630  proc_schemas/billing.py
      632  tests/registry/test_tracheostomy_route.py
      639  proc_schemas/clinical/__init__.py
      651  tests/unit/test_schemas.py
      666  proc_schemas/__init__.py
      692  tests/registry/test_provider_name_sanitization.py
      695  tests/coder/test_kb_professional_descriptions.py
      706  modules/registry/extraction/structurer.py
      715  modules/ml_coder/__init__.py
      715  modules/registry/slots/base.py
      728  modules/coder/parallel_pathway/__init__.py
      731  modules/reporting/second_pass/laterality_guard.py
      760  tests/registry/test_openai_model_structurer_override.py
      775  proc_nlp/__init__.py
      781  proc_schemas/envelope_models.py
      785  modules/domain/coding_rules/__init__.py
      802  tests/coder/test_candidate_expansion.py
      816  modules/phi/adapters/encryption_insecure_demo.py
      831  modules/registry/slots/imaging.py
      833  tests/coder/test_parallel_confidence_combiner.py
      839  modules/agents/summarizer/summarizer_agent.py
      840  modules/common/logger.py
      852  tests/ml_coder/test_registry_label_constraints.py
      863  modules/reporting/coder_view.py
      874  modules/domain/knowledge_base/models.py
      887  tests/api/test_ui.py
      894  modules/registry/application/__init__.py
      894  modules/registry/pipelines/v3_pipeline.py
      898  tests/scripts/test_train_roberta_cli.py
      904  tests/unit/test_inference_engine.py
      907  modules/infra/perf.py
      907  modules/registry/__init__.py
      926  modules/ml_coder/utils.py
      944  tests/scripts/test_audit_model_fp_cli.py
      968  modules/reporter/schema.py
      972  modules/registry/self_correction/types.py
      975  modules/coder/domain_rules/registry_to_cpt/engine.py
      996  modules/api/guards.py
      999  tests/phi/test_fernet_encryption_adapter.py
     1027  tests/registry/test_clinical_guardrails_stent_inspection.py
     1072  modules/coder/__init__.py
     1076  tests/registry/test_clinical_guardrails_radial_linear.py
     1123  modules/coder/types.py
     1125  modules/ml_coder/valid_ip_codes.py
     1126  tests/registry/test_clinical_guardrails_endobronchial_biopsy.py
     1134  tests/unit/test_normalize_phi_labels.py
     1140  modules/registry/schema_filter.py
     1143  tests/registry/test_slots_ebus_tblb.py
     1163  modules/registry/slots/disposition.py
     1168  proc_schemas/shared/ebus_events.py
     1184  tests/registry/test_schema_filter.py
     1200  tests/registry/test_structurer_fallback.py
     1201  tests/unit/test_knowledge.py
     1212  modules/common/exceptions.py
     1218  modules/registry/slots/pleura.py
     1220  tests/coder/test_ncci_ptp_indicator.py
     1224  tests/coding/test_sectionizer.py
     1229  modules/api/schemas/__init__.py
     1270  tests/coding/test_peripheral_rules.py
     1279  modules/phi/adapters/scrubber_stub.py
     1299  tests/ml_coder/test_distillation_io.py
     1300  modules/phi/adapters/audit_logger_db.py
     1309  modules/registry/slots/indication.py
     1313  tests/scripts/test_train_distilbert_ner_cli.py
     1320  tests/unit/test_template_cache.py
     1335  modules/common/spans.py
     1335  tests/coder/test_llm_provider_openai_compat.py
     1339  modules/common/knowledge_cli.py
     1355  modules/phi/adapters/fernet_encryption.py
     1376  tests/api/conftest.py
     1380  modules/api/readiness.py
     1382  tests/phi/test_presidio_nlp_backend_smoke.py
     1391  modules/registry/schema.py
     1402  tests/registry/test_clinical_guardrails_checkbox_negative.py
     1412  tests/registry/test_registry_engine_merge_llm_and_seed.py
     1423  tests/registry/test_keyword_guard_keywords.py
     1426  tests/registry/test_llm_timeout_fallback.py
     1442  modules/domain/reasoning/models.py
     1450  tests/registry/test_airway_stent_vascular_plug_revision.py
     1451  tests/coding/test_ebus_rules.py
     1461  modules/phi/db.py
     1476  modules/registry/schema_granular.py
     1477  tests/registry/test_ner_to_registry_mapper.py
     1493  tests/coding/test_hierarchy_normalization.py
     1511  tests/registry/test_table_row_masking_regressions.py
     1542  modules/domain/knowledge_base/repository.py
     1547  modules/registry/slots/complications.py
     1548  modules/common/rules_engine/ncci.py
     1551  proc_schemas/procedure_report.py
     1561  tests/test_openai_responses_parse.py
     1568  modules/coder/reconciliation/__init__.py
     1582  modules/registry/ml/__init__.py
     1609  tests/registry/test_registry_to_cpt_mechanical_debulking.py
     1675  modules/infra/llm_control.py
     1676  tests/scripts/test_prodigy_export_registry.py
     1687  tests/scripts/test_export_patient_note_texts.py
     1708  proc_schemas/reasoning.py
     1717  tests/coder/test_kitchen_sink_ml_first_fastpath_completeness.py
     1731  modules/domain/text/negation.py
     1761  modules/ml_coder/preprocessing.py
     1763  tests/registry/test_kitchen_sink_extraction_first.py
     1767  tests/registry/test_navigation_fiducials.py
     1767  tests/utils/case_filter.py
     1828  tests/registry/test_registry_to_cpt_diagnostic_bronchoscopy.py
     1832  config/settings.py
     1835  modules/registry/slots/tblb.py
     1842  tests/registry/test_pleural_extraction.py
     1847  modules/coder/parallel_pathway/reconciler.py
     1875  tests/coder/test_parallel_pathway_orchestrator_path_b.py
     1876  modules/reporting/__init__.py
     1877  tests/integration/api/test_health_endpoint.py
     1880  tests/registry/test_new_extractors.py
     1909  modules/coder/ncci.py
     1929  modules/coder/constants.py
     1961  tests/api/test_phi_demo_cases.py
     1984  tests/registry/test_keyword_guard_omissions.py
     1985  modules/coder/phi_gating.py
     1999  modules/phi/ports.py
     2001  modules/registry/schema/ip_v3_extraction.py
     2003  modules/registry/legacy/supabase_sink.py
     2027  modules/registry/audit/audit_types.py
     2032  modules/agents/parser/parser_agent.py
     2046  tests/registry/test_note_002_regression.py
     2093  modules/registry/slots/dilation.py
     2107  modules/ml_coder/training_losses.py
     2136  modules/coder/peripheral_rules.py
     2140  modules/registry/label_fields.py
     2143  modules/reporting/metadata.py
     2148  tests/registry/test_deterministic_extractors_phase6.py
     2167  modules/registry/legacy/adapters/base.py
     2167  tests/registry/test_ebus_postprocess_enrichment.py
     2174  tests/test_ip_registry_schema_guardrails.py
     2196  modules/registry/self_correction/__init__.py
     2225  tests/registry/test_sedation_blvr.py
     2237  tests/registry/test_ebus_postprocess_fallback.py
     2250  modules/ml_coder/self_correction.py
     2253  tests/unit/test_phi_distillation.py
     2275  tests/registry/test_pathology_extraction.py
     2307  tests/registry/test_ebus_specimen_override.py
     2320  modules/registry/slots/sedation.py
     2324  tests/registry/test_schema_refactor_smoke.py
     2346  tests/conftest.py
     2372  tests/scripts/test_prodigy_export_registry_file_mode.py
     2416  modules/common/text_cleaning.py
     2421  tests/registry/test_registry_to_cpt_fibrinolytic_therapy.py
     2448  modules/common/rules_engine/mer.py
     2472  modules/reporter/prompts.py
     2487  modules/proc_ml_advisor/__init__.py
     2488  modules/llm/client.py
     2582  modules/reporting/inference.py
     2601  tests/registry/test_note_281_elastography_regression.py
     2607  tests/registry/test_extraction_first_flow.py
     2612  modules/phi/safety/protected_terms.py
     2664  modules/registry/slots/ebus.py
     2713  modules/common/text_io.py
     2755  tests/registry/test_header_scan.py
     2768  modules/domain/coding_rules/mer.py
     2788  modules/domain/coding_rules/ncci.py
     2808  modules/domain/rvu/calculator.py
     2821  tests/registry/test_ner_procedure_extractor.py
     2825  tests/coding/test_phi_gating.py
     2835  modules/ml_coder/thresholds.py
     2853  modules/api/routes/phi_demo_cases.py
     2879  tests/test_clean_ip_registry.py
     2914  modules/reporter/cli.py
     2921  tests/registry/test_fixpack_trach_stent_elastography_normalization.py
     2927  modules/common/rvu_calc.py
     2936  tests/registry/test_masking.py
     2990  tests/coding/test_sectionizer_integration.py
     2993  tests/unit/test_openai_timeouts.py
     3060  modules/common/umls_linking.py
     3066  tests/registry/test_ebus_deterministic.py
     3076  modules/api/adapters/response_adapter.py
     3104  modules/coder/ebus_extractor.py
     3106  tests/registry/test_note_281_granularity_regression.py
     3131  modules/registry/adapters/schema_registry.py
     3141  tests/unit/test_validation_engine.py
     3163  modules/ml_coder/distillation_io.py
     3166  tests/registry/test_phase5_regression_harness.py
     3169  proc_nlp/umls_linker.py
     3186  modules/registry/summarize.py
     3188  modules/common/rules_engine/dsl.py
     3204  proc_nlp/normalize_proc.py
     3252  modules/infra/cache.py
     3264  tests/coder/test_ncci_bundling_excludes_financials.py
     3267  tests/registry/test_note_300_multilobe_navigation_regression.py
     3277  tests/registry/test_focusing_audit_guardrail.py
     3307  modules/registry/legacy/adapter.py
     3391  modules/coder/peripheral_extractor.py
     3399  modules/infra/settings.py
     3471  tests/registry/test_v3_note_281_narrative_first_and_anchors.py
     3513  tests/unit/test_sanitize_dataset.py
     3532  proc_schemas/coding.py
     3622  modules/coder/posthoc.py
     3624  tests/registry/test_parallel_ner_uplift_evidence.py
     3627  tests/scripts/test_prodigy_prepare_registry.py
     3656  proc_schemas/registry/ip_v2.py
     3682  modules/coder/sectionizer.py
     3694  modules/ml_coder/registry_label_schema.py
     3704  modules/registry/slots/blvr.py
     3706  modules/api/phi_redaction.py
     3774  modules/common/knowledge_schema.py
     3795  modules/common/model_capabilities.py
     3831  modules/api/phi_dependencies.py
     3862  tests/integration/test_pipeline_integrity.py
     3899  modules/registry/extraction/focus.py
     3944  modules/ml_coder/registry_label_constraints.py
     3958  modules/coder/schema.py
     3970  modules/agents/contracts.py
     3996  modules/registry/tags.py
     4071  modules/registry/self_correction/prompt_improvement.py
     4202  tests/unit/test_phi_platinum_filters.py
     4251  modules/registry/slots/stent.py
     4339  tests/phi/test_models.py
     4373  tests/registry/test_keyword_guard_overrides.py
     4390  modules/registry_cleaning/logging_utils.py
     4403  tests/phi/test_presidio_scrubber_adapter.py
     4404  modules/registry/audit/compare.py
     4425  tests/registry/test_registry_to_cpt_thoracoscopy_biopsy.py
     4461  proc_schemas/clinical/common.py
     4486  tests/registry/test_post_fix_regressions.py
     4494  modules/registry/ebus_config.py
     4509  tests/phi/test_manual_scrub.py
     4522  tests/registry/test_registry_engine_sanitization.py
     4534  tests/registry/test_derive_procedures_from_granular_consistency.py
     4568  modules/registry/self_correction/judge.py
     4598  tests/api/test_coding_phi_gating.py
     4751  tests/registry/test_fixpack_device_action_regressions.py
     4782  modules/common/sectionizer.py
     4845  tests/api/test_unified_process.py
     4978  tests/registry/test_auditor_raw_ml_only.py
     5045  modules/coder/adapters/nlp/simple_negation_detector.py
     5048  docs/phi_review_system/backend/main.py
     5103  modules/registry/cli.py
     5166  modules/api/schemas/qa.py
     5176  tests/unit/test_openai_payload_compat.py
     5186  tests/coding/test_rules_engine_phase1.py
     5334  modules/api/phi_demo_store.py
     5384  tests/registry/test_registry_to_cpt_blvr_chartis_sedation.py
     5394  modules/api/gemini_client.py
     5481  modules/registry/self_correction/apply.py
     5641  modules/coder/ebus_rules.py
     5653  modules/phi/models.py
     5706  modules/registry/deterministic/anatomy.py
     5773  modules/api/schemas/base.py
     5870  modules/infra/nlp_warmup.py
     6019  modules/ner/entity_types.py
     6042  tests/api/test_fastapi.py
     6131  tests/api/test_phi_redaction.py
     6150  modules/coder/parallel_pathway/confidence_combiner.py
     6184  tests/integration/test_phi_workflow_end_to_end.py
     6251  tests/unit/test_phi_distillation_refinery.py
     6252  modules/registry_cleaning/consistency_utils.py
     6276  tests/registry/test_self_correction_validation.py
     6333  tests/registry/test_audit_compare_report.py
     6351  modules/registry/slots/therapeutics.py
     6398  modules/registry/processing/navigation_fiducials.py
     6438  modules/domain/procedure_store/repository.py
     6439  tests/api/test_phi_redactor_ui.py
     6451  tests/phi/test_service.py
     6485  proc_schemas/clinical/pleural.py
     6596  tests/registry/test_registry_qa_regressions.py
     6632  modules/coder/cli.py
     6646  tests/unit/test_protected_veto.py
     6904  modules/reporting/ip_addons.py
     6955  tests/integration/api/test_startup_warmup.py
     7110  modules/coder/application/candidate_expansion.py
     7176  modules/agents/run_pipeline.py
     7307  tests/integration/coder/test_coding_service.py
     7383  tests/api/test_phi_endpoints.py
     7505  modules/registry/ner_mapping/entity_to_registry.py
     7526  modules/domain/coding_rules/evidence_context.py
     7599  modules/registry/model_runtime.py
     7652  tests/registry/test_registry_extraction_ebus.py
     7672  modules/coder/adapters/ml_ranker.py
     7672  tests/registry/test_extraction_quality_fixpack_jan2026.py
     7837  tests/unit/test_no_legacy_imports.py
     8149  modules/coder/adapters/persistence/inmemory_procedure_store.py
     8182  tests/ml_coder/test_registry_predictor.py
     8227  tests/coder/test_rules_engine.py
     8228  proc_schemas/registry/ip_v3.py
     8415  modules/registry/inference_pytorch.py
     8427  modules/registry_cleaning/clinical_qc.py
     8556  modules/registry/ml/evaluate.py
     8618  tests/coder/test_hierarchy_bundling_fixes.py
     8652  modules/coder/application/procedure_type_detector.py
     8695  tests/coding/test_json_rules_parity.py
     8702  modules/api/coder_adapter.py
     8750  modules/api/routes/unified_process.py
     9005  modules/api/routes/metrics.py
     9048  modules/registry/schema/adapters/v3_to_v2.py
     9393  modules/registry/processing/focus.py
     9466  tests/ml_coder/test_training_pipeline.py
     9471  tests/ml_coder/test_case_difficulty.py
     9490  modules/ml_coder/training.py
     9709  modules/registry/processing/navigation_targets.py
     9738  modules/phi/service.py
     9850  tests/unit/test_extraction_adapters.py
     9870  modules/reporting/validation.py
    10017  tests/registry/test_registry_guardrails.py
    10067  tests/unit/test_procedure_type_detector.py
    10070  modules/ml_coder/predictor.py
    10466  modules/api/routes_registry.py
    10601  modules/registry/self_correction/validation.py
    10791  tests/unit/test_inmemory_procedure_store.py
    10938  tests/registry/test_ebus_config_station_count.py
    11181  tests/test_phi_redaction_contract.py
    11253  modules/registry/application/registry_builder.py
    11289  modules/coder/adapters/nlp/keyword_mapping_loader.py
    11300  modules/registry/processing/masking.py
    11467  modules/api/routes/phi.py
    11598  modules/common/knowledge.py
    11691  modules/registry/legacy/adapters/pleural.py
    11758  modules/registry/evidence/verifier.py
    11799  modules/registry/application/pathology_extraction.py
    11881  modules/registry/ner_mapping/procedure_extractor.py
    12184  tests/registry/test_self_correction_loop.py
    12198  modules/api/dependencies.py
    12339  modules/registry_cleaning/schema_utils.py
    12446  docs/phi_review_system/backend/dependencies.py
    12517  modules/registry/extractors/v3_extractor.py
    12640  tests/ml_coder/test_data_prep.py
    12657  docs/phi_review_system/backend/schemas.py
    12997  tests/coder/test_smart_hybrid_policy.py
    13192  tests/unit/test_openai_responses_primary.py
    13453  modules/coder/application/coding_service.py
    13483  modules/coder/domain_rules/__init__.py
    13696  modules/coder/rules.py
    13980  tests/ml_advisor/test_router.py
    14135  tests/integration/persistence/test_supabase_procedure_store.py
    14250  modules/ml_coder/registry_predictor.py
    14397  modules/registry/ml/models.py
    14466  tests/integration/coder/test_hybrid_policy.py
    14585  docs/phi_review_system/backend/models.py
    14655  modules/registry/audit/raw_ml_auditor.py
    14876  tests/phi/test_veto_regression.py
    15142  modules/registry/v2_booleans.py
    15243  tests/unit/test_dsl.py
    15267  modules/domain/coding_rules/json_rules_evaluator.py
    15328  modules/registry/inference_onnx.py
    15346  tests/registry/test_action_predictor.py
    15436  modules/autocode/ip_kb/canonical_rules.py
    15467  modules/api/services/qa_pipeline.py
    15495  modules/ml_coder/registry_training.py
    15601  tests/reporter/test_ip_addons.py
    15653  tests/registry/test_extraction_quality.py
    15655  modules/coder/reconciliation/pipeline.py
    15800  modules/ner/inference.py
    15828  modules/registry/ner_mapping/station_extractor.py
    15857  tests/registry/test_normalization.py
    16032  modules/coder/rules_engine.py
    16171  modules/registry/application/cpt_registry_mapping.py
    16608  tests/integration/api/test_metrics_endpoint.py
    16911  tests/ml_coder/test_registry_first_data_prep.py
    17010  modules/phi/safety/veto.py
    17103  modules/registry/application/coding_support_builder.py
    17161  proc_schemas/clinical/airway.py
    17268  modules/common/openai_responses.py
    17313  modules/coder/reconciliation/reconciler.py
    17806  tests/ml_coder/test_label_hydrator.py
    17854  modules/coder/adapters/llm/gemini_advisor.py
    17939  tests/unit/test_template_coverage.py
    17947  modules/registry/normalization.py
    18428  modules/coder/adapters/persistence/csv_kb_adapter.py
    18937  tests/api/test_registry_extract_endpoint.py
    18997  tests/coder/test_registry_coder.py
    19783  tests/integration/api/test_registry_endpoints.py
    20079  modules/registry_cleaning/cpt_utils.py
    20194  tests/registry/test_cao_extraction.py
    20223  modules/domain/coding_rules/rule_engine.py
    20317  modules/coder/parallel_pathway/orchestrator.py
    20430  modules/registry/model_bootstrap.py
    20539  modules/registry/extractors/llm_detailed.py
    20678  tests/coder/test_coding_rules_phase7.py
    21220  modules/coder/adapters/llm/openai_compat_advisor.py
    21460  modules/coder/adapters/persistence/supabase_procedure_store.py
    21479  tests/coder/test_reconciliation.py
    21518  tests/test_registry_normalization.py
    22317  tests/reporter/test_macro_engine_features.py
    22456  modules/registry/legacy/adapters/airway.py
    22569  modules/phi/adapters/presidio_scrubber.py
    22644  modules/ml_coder/data_prep.py
    22670  tests/ml_coder/test_registry_data_prep.py
    23485  docs/phi_review_system/backend/endpoints.py
    24045  modules/registry/schema/v2_dynamic.py
    24069  tests/ml_advisor/conftest.py
    24922  tests/integration/api/test_coder_run_endpoint.py
    25665  modules/coder/application/smart_hybrid_policy.py
    25902  modules/reporting/macro_engine.py
    27507  modules/ml_coder/label_hydrator.py
    27574  modules/api/normalization.py
    27607  modules/registry/transform.py
    27702  modules/coder/adapters/registry_coder.py
    28626  modules/ml_coder/registry_data_prep.py
    29699  modules/registry/schema/granular_models.py
    29893  modules/domain/coding_rules/coding_rules_engine.py
    30063  modules/api/ml_advisor_router.py
    30872  modules/registry/schema/granular_logic.py
    31101  tests/integration/api/test_procedure_codes_endpoints.py
    33132  tests/registry/test_registry_service_hybrid_flow.py
    35268  tests/coding/test_rules_validation.py
    35381  modules/phi/adapters/phi_redactor_hybrid.py
    35981  modules/registry/ml/action_predictor.py
    36446  modules/registry/self_correction/keyword_guard.py
    36538  modules/coder/dictionary.py
    36877  tests/unit/test_structured_reporter.py
    39279  tests/ml_advisor/test_schemas.py
    40683  modules/common/llm.py
    41901  modules/proc_ml_advisor/schemas.py
    42913  modules/api/routes/procedure_codes.py
    43561  modules/api/fastapi_app.py
    43852  tests/registry/test_granular_registry_models.py
    48887  modules/extraction/postprocessing/clinical_guardrails.py
    52780  modules/coder/domain_rules/registry_to_cpt/coding_rules.py
    56440  modules/autocode/ip_kb/ip_kb.py
    62046  modules/registry/prompts.py
    63511  modules/reporting/engine.py
    90679  modules/registry/deterministic_extractors.py
   111411  modules/registry/engine.py
   120666  modules/registry/postprocess.py
   142007  modules/registry/application/registry_service.py
       94  modules/api/static/phi_redactor/vendor/phi_distilbert_ner_quant/.bootstrap_state.json
      181  modules/api/static/phi_redactor/vendor/phi_distilbert_ner_quant/manifest.json
      240  modules/reporting/templates/addons/pigtail_catheter_placement.jinja
      246  modules/reporting/templates/addons/eus_b.jinja
      247  modules/reporting/templates/addons/peg_removal_exchange.jinja
      259  modules/reporting/templates/addons/thoravent_placement.jinja
      264  modules/reporting/templates/addons/paracentesis.jinja
      281  modules/reporting/templates/addons/peg_placement.jinja
      282  modules/reporting/templates/addons/peg_discharge.jinja
      290  modules/reporting/templates/addons/intrapleural_fibrinolysis.jinja
      293  modules/reporting/templates/addons/tunneled_pleural_catheter_removal.jinja
      300  modules/reporting/templates/addons/whole_lung_lavage.jinja
      331  modules/reporting/templates/addons/indwelling_tunneled_pleural_catheter_placement.jinja
      338  modules/reporting/templates/addons/chest_tube_pleurx_catheter_discharge.jinja
      346  modules/reporting/templates/addons/therapeutic_aspiration.jinja
      349  modules/reporting/templates/addons/endobronchial_tumor_excision.jinja
      351  modules/reporting/templates/addons/thoracentesis.jinja
      364  modules/reporting/templates/addons/blvr_discharge.jinja
      393  modules/reporting/templates/addons/endobronchial_cryoablation.jinja
      395  modules/reporting/templates/addons/tracheobronchoscopy_via_tracheostomy.jinja
      412  modules/reporting/templates/addons/medical_thoracoscopy.jinja
      415  modules/reporting/templates/addons/airway_stent_placement.jinja
      415  modules/reporting/templates/addons/bronchial_brushings.jinja
      434  modules/reporting/templates/addons/bronchoalveolar_lavage.jinja
      437  modules/reporting/templates/addons/transbronchial_lung_biopsy.jinja
      439  modules/reporting/templates/addons/ebus_tbna.jinja
      444  modules/reporting/templates/addons/bronchial_washing.jinja
      446  modules/reporting/templates/addons/transthoracic_needle_biopsy.jinja
      450  modules/reporter/templates/pleural_synoptic.md.jinja
      450  modules/reporting/templates/addons/fiducial_marker_placement.jinja
      452  modules/reporting/templates/addons/chemical_cauterization_of_granulation_tissue.jinja
      457  modules/reporting/templates/addons/endobronchial_biopsy.jinja
      471  modules/reporter/templates/blvr_synoptic.md.jinja
      483  modules/reporting/templates/addons/transbronchial_needle_aspiration.jinja
      486  modules/reporting/templates/addons/pre_anesthesia_assessment_for_moderate_sedation.jinja
      490  modules/reporting/templates/addons/balloon_dilation.jinja
      492  modules/reporting/templates/addons/image_guided_chest_tube.jinja
      509  modules/reporting/templates/addons/radial_ebus_survey.jinja
      512  modules/reporting/templates/addons/transbronchial_cryobiopsy.jinja
      543  modules/reporting/templates/addons/chest_tube_removal.jinja
      565  modules/reporting/templates/addons/photodynamic_therapy_debridement_48_96_hours_post_light.jinja
      582  modules/reporting/templates/addons/control_of_minor_tracheostomy_bleeding_electrocautery.jinja
      584  modules/reporting/templates/addons/ion_registration_complete.jinja
      586  modules/reporting/templates/addons/tool_in_lesion_confirmation.jinja
      589  modules/reporting/templates/addons/airway_stent_surveillance_bronchoscopy.jinja
      607  tests/fixtures/ebus_staging_4R_7_11R.txt
      608  modules/reporting/templates/addons/focused_thoracic_ultrasound_pleura_lung.jinja
      612  modules/api/static/phi_redactor/sw.js
      612  modules/reporting/templates/addons/ebus_guided_19_gauge_core_fine_needle_biopsy_fnb.jinja
      619  modules/api/static/phi_redactor/vendor/phi_distilbert_ner/label_map.json
      620  modules/reporter/templates/bronchoscopy_synoptic.md.jinja
      622  modules/reporting/templates/addons/endobronchial_valve_placement.jinja
      632  modules/reporting/templates/addons/tracheostomy_tube_change.jinja
      641  modules/reporting/templates/addons/endobronchial_tumor_destruction.jinja
      644  modules/reporting/templates/addons/stoma_or_tracheal_granulation_mechanical_debridement.jinja
      647  modules/reporting/templates/addons/ultrasound_guided_pleural_biopsy_closed_core.jinja
      655  modules/reporting/templates/addons/chemical_pleurodesis_via_tunneled_pleural_catheter_ipc.jinja
      675  modules/reporting/templates/addons/photodynamic_therapy_pdt_light_application.jinja
      688  modules/reporting/templates/addons/tracheostomy_decannulation_bedside.jinja
      689  modules/reporting/templates/addons/chest_tube_exchange_upsizing_over_guidewire.jinja
      690  modules/reporting/templates/addons/ebus_guided_intranodal_forceps_biopsy_ifb.jinja
      695  modules/api/static/phi_redactor/vendor/phi_distilbert_ner/special_tokens_map.json
      695  modules/api/static/phi_redactor/vendor/phi_distilbert_ner_quant/special_tokens_map.json
      707  modules/reporting/templates/addons/indwelling_pleural_catheter_ipc_exchange.jinja
      708  modules/reporting/templates/addons/tracheostomy_downsizing_fenestrated_tube_placement.jinja
      714  modules/reporting/templates/addons/endobronchial_sealant_application_for_bronchopleural_fistula_bpf.jinja
      716  modules/reporting/templates/addons/awake_fiberoptic_intubation_foi.jinja
      720  modules/reporting/templates/addons/transbronchial_dye_marker_placement_for_surgical_localization.jinja
      725  modules/reporting/templates/addons/robotic_navigational_bronchoscopy_ion.jinja
      726  modules/reporting/templates/addons/endobronchial_blocker_placement_isolation_hemorrhage_control.jinja
      727  modules/reporting/templates/addons/endobronchial_valve_removal_exchange.jinja
      733  modules/reporting/templates/addons/foreign_body_removal_flexible_rigid.jinja
      733  tests/fixtures/blvr_two_lobes.txt
      735  modules/reporting/templates/addons/bronchoscopy_guided_double_lumen_tube_dlt_placement_confirmation.jinja
      746  modules/reporting/templates/addons/thoracentesis_with_pleural_manometry.jinja
      750  modules/reporting/templates/addons/endobronchial_valve_placement_for_persistent_air_leak_bpf.jinja
      762  tests/fixtures/thora_bilateral.txt
      764  modules/api/static/phi_redactor/vendor/phi_distilbert_ner_quant/ort_config.json
      765  modules/reporting/templates/addons/electromagnetic_navigation_bronchoscopy.jinja
      768  modules/reporting/templates/addons/intra_procedural_cbct_cact_fusion_registration_correction_e_g_navilink_3d.jinja
      778  modules/reporting/templates/addons/ion_registration_registration_drift_mismatch.jinja
      786  modules/reporting/templates/addons/airway_stent_removal_revision.jinja
      791  modules/reporting/templates/addons/cone_beam_ct_cbct_augmented_fluoroscopy_assisted_bronchoscopy.jinja
      800  tests/fixtures/therapeutic_aspiration_repeat_stay.txt
      808  modules/reporting/templates/addons/robotic_navigational_bronchoscopy_monarch_auris.jinja
      812  modules/reporting/templates/addons/flexible_fiberoptic_laryngoscopy.jinja
      818  modules/reporting/templates/addons/chemical_pleurodesis_via_chest_tube_talc_slurry_or_doxycycline.jinja
      858  modules/reporting/templates/addons/bronchopleural_fistula_bpf_localization_and_occlusion_test.jinja
      863  tests/fixtures/notes/phi_example_note.txt
      867  modules/reporting/templates/addons/endobronchial_hemostasis_hemoptysis_control.jinja
      910  modules/reporting/templates/addons/tracheostomy_planned_percutaneous_bronchoscopic_assistance.jinja
      920  modules/reporting/templates/addons/radial_ebus_guided_sampling_with_guide_sheath.jinja
      942  tests/fixtures/stent_rmb_and_dilation_lul.txt
      951  modules/api/static/phi_redactor/vendor/phi_distilbert_ner/config.json
      951  modules/api/static/phi_redactor/vendor/phi_distilbert_ner_quant/config.json
      982  modules/reporting/templates/addons/rigid_bronchoscopy_diagnostic_therapeutic.jinja
     1095  modules/reporting/templates/addons/percutaneous_tracheostomy_revision.jinja
     1193  tests/fixtures/ppl_nav_radial_tblb.txt
     1227  modules/api/static/phi_redactor/vendor/phi_distilbert_ner/tokenizer_config.json
     1227  modules/api/static/phi_redactor/vendor/phi_distilbert_ner_quant/tokenizer_config.json
     1232  docs/REPORTER_STYLE_GUIDE.md
     1306  docs/KNOWLEDGE_RELEASE_CHECKLIST.md
     1359  modules/reporting/templates/addons/tunneled_pleural_catheter_instructions.jinja
     1432  modules/reporting/templates/addons/ion_registration_partial_efficiency_strategy_ssrab.jinja
     1797  modules/api/static/phi_redactor/allowlist_trie.json
     1817  modules/reporting/templates/addons/post_blvr_management_protocol.jinja
     1925  modules/reporting/templates/addons/general_bronchoscopy_note.jinja
     1961  modules/phi/README.md
     1992  tests/fixtures/complex_tracheal_stenosis.txt
     2045  docs/model_release_runbook.md
     2196  docs/DEPLOY_RAILWAY.md
     2305  docs/KNOWLEDGE_INVENTORY.md
     2342  modules/reporting/templates/addons/interventional_pulmonology_operative_report.jinja
     2922  modules/api/static/phi_redactor/vendor/phi_distilbert_ner/protected_terms.json
     2922  modules/api/static/phi_redactor/vendor/phi_distilbert_ner_quant/protected_terms.json
     2954  tests/fixtures/notes/note_315.txt
     3054  tests/fixtures/notes/note_289.txt
     3085  modules/reporting/templates/ebus_tbna.jinja
     3086  modules/reporting/templates/cryobiopsy.jinja
     3087  modules/reporting/templates/pleuroscopy.jinja
     3088  modules/reporting/templates/bronchoscopy.jinja
     3088  modules/reporting/templates/stent.jinja
     3089  modules/reporting/templates/thoracentesis.jinja
     3103  modules/reporting/templates/ipc.jinja
     3227  docs/STRUCTURED_REPORTER.md
     3376  modules/registry/registry_system_prompt.txt
     3445  docs/Multi_agent_collaboration/Session Startup Template.md
     3579  docs/REFERENCES.md
     3717  modules/reporting/templates/macros/main.j2
     3830  docs/Multi_agent_collaboration/Codex “Repo Surgeon” Persona.md
     3837  docs/Multi_agent_collaboration/Codex Priming Script.md
     3883  modules/reporting/templates/macros/base.j2
     4071  docs/INSTALLATION.md
     4096  docs/DEPLOY_ARCH.md
     4198  docs/REGISTRY_PRODIGY_WORKFLOW.md
     4233  tests/fixtures/notes/kitchen_sink_ion_nav_ebus_fiducial_dilation.txt
     4437  tests/fixtures/notes/note_274.txt
     4544  docs/Production_Readiness_Review.md
     4595  tests/fixtures/notes/note_275.txt
     4606  docs/CODEX_PRODUCTION_PLAN.md
     4745  docs/Multi_agent_collaboration/Architect Priming Script.md
     5429  docs/ml_first_hybrid_policy.md
     6232  docs/Registry_API.md
     6862  modules/reporting/templates/macros/04_blvr_cryo.j2
     7031  docs/Registry_ML_summary.md
     7218  docs/IPregistry_update_plan.md
     7332  tests/fixtures/notes/note_281.txt
     7368  docs/Multi_agent_collaboration/Multi‑Agent Architecture.md
     7469  modules/reporting/templates/macros/06_other_interventions.j2
     8655  modules/reporting/EXTRACTION_RULES.md
     8821  docs/GRANULAR_NER_UPDATE_WORKFLOW.md
     9413  docs/"Diamond" Improvement Plan 1_18_26.txt
     9688  modules/reporting/templates/macros/01_minor_trach_laryngoscopy.j2
     9941  docs/optimization_12_16_25.md
    10242  docs/DEPLOYMENT.md
    11041  docs/DEVELOPMENT.md
    11785  modules/reporting/templates/macros/07_clinical_assessment.j2
    12969  modules/reporting/templates/macros/03_navigation_robotic_ebus.j2
    13411  docs/CODEX_REGISTRY_DIAMOND_LOOP.md
    14072  docs/Multi_agent_collaboration/External_Review_Action_Plan.md
    14126  modules/reporting/templates/macros/02_core_bronchoscopy.j2
    15081  docs/GRAFANA_DASHBOARDS.md
    15238  docs/REGISTRY_V3_IMPLEMENTATION_GUIDE.md
    16028  modules/reporting/templates/macros/05_pleural.j2
    16113  docs/AGENTS.md
    16515  docs/ARCHITECTURE.md
    17732  docs/phi_review_system/README.md
    17850  modules/api/static/phi_demo.js
    18104  modules/phi/adapters/redaction-service.js
    19826  docs/MAKEFILE_COMMANDS.md
    19835  modules/registry/ip_registry_schema_additions.json
    21781  modules/reporting/templates/macros/template_schema.json
    27821  modules/registry/ip_registry_improvements.md
    41682  docs/USER_GUIDE.md
    50398  docs/Multi_agent_collaboration/V8_MIGRATION_PLAN_UPDATED.md
    61430  modules/api/static/phi_redactor/protectedVeto.js
    61485  modules/api/static/phi_redactor/protectedVeto.legacy.js
    90791  modules/api/static/app.js
    93797  modules/api/static/phi_redactor/redactor.worker.js
    94017  modules/api/static/phi_redactor/redactor.worker.legacy.js
   133503  modules/api/static/phi_redactor/app.js
```

## Skipped (reason)

```
 inline_cap_reached>75  scripts/sanitize_dataset.py
 inline_cap_reached>75  scripts/apply_platinum_redactions.py
 inline_cap_reached>75  scripts/registry_pipeline_smoke_batch.py
 inline_cap_reached>75  scripts/generate_gitingest.py
 inline_cap_reached>75  scripts/eval_hybrid_pipeline.py
 inline_cap_reached>75  scripts/label_neg_stent.py
 inline_cap_reached>75  scripts/prodigy_prepare_phi_batch.py
 inline_cap_reached>75  scripts/build_model_agnostic_phi_spans.py
 inline_cap_reached>75  scripts/generate_synthetic_phi_data.py
 inline_cap_reached>75  scripts/audit_model_fp.py
 inline_cap_reached>75  scripts/train_roberta_pm3.py
 inline_cap_reached>75  scripts/fix_alignment.py
 inline_cap_reached>75  scripts/train_distilbert_ner.py
 inline_cap_reached>75  scripts/prodigy_prepare_registry.py
 inline_cap_reached>75  scripts/train_registry_ner.py
 inline_cap_reached>75  scripts/golden_to_csv.py
 inline_cap_reached>75  scripts/validate_golden_extractions.py
 inline_cap_reached>75  scripts/distill_phi_labels.py
 inline_cap_reached>75  scripts/train_roberta.py
 inline_cap_reached>75  modules/coder/adapters/__init__.py
 inline_cap_reached>75  modules/agents/parser/__init__.py
 inline_cap_reached>75  modules/agents/structurer/__init__.py
 inline_cap_reached>75  modules/agents/summarizer/__init__.py
 inline_cap_reached>75  modules/domain/__init__.py
 inline_cap_reached>75  modules/registry/processing/__init__.py
 inline_cap_reached>75  modules/registry/audit/__init__.py
 inline_cap_reached>75  modules/api/routes/__init__.py
 inline_cap_reached>75  modules/registry/evidence/__init__.py
 inline_cap_reached>75  modules/extraction/postprocessing/__init__.py
 inline_cap_reached>75  modules/registry/pipelines/__init__.py
 inline_cap_reached>75  modules/registry/slots/__init__.py
 inline_cap_reached>75  modules/agents/__init__.py
 inline_cap_reached>75  proc_schemas/shared/__init__.py
 inline_cap_reached>75  modules/extraction/__init__.py
 inline_cap_reached>75  modules/domain/procedure_store/__init__.py
 inline_cap_reached>75  modules/coder/domain_rules/registry_to_cpt/__init__.py
 inline_cap_reached>75  modules/registry/extraction/__init__.py
 inline_cap_reached>75  modules/__init__.py
 inline_cap_reached>75  modules/domain/text/__init__.py
 inline_cap_reached>75  modules/coder/adapters/persistence/__init__.py
 inline_cap_reached>75  modules/domain/reasoning/__init__.py
 inline_cap_reached>75  modules/domain/rvu/__init__.py
 inline_cap_reached>75  modules/registry/legacy/__init__.py
 inline_cap_reached>75  modules/common/rules_engine/__init__.py
 inline_cap_reached>75  proc_schemas/registry/__init__.py
 inline_cap_reached>75  modules/registry/legacy/adapters/__init__.py
 inline_cap_reached>75  modules/api/adapters/__init__.py
 inline_cap_reached>75  modules/registry/adapters/__init__.py
 inline_cap_reached>75  modules/common/__init__.py
 inline_cap_reached>75  modules/domain/knowledge_base/__init__.py
 inline_cap_reached>75  modules/infra/__init__.py
 inline_cap_reached>75  modules/reporter/__init__.py
 inline_cap_reached>75  modules/registry/extractors/__init__.py
 inline_cap_reached>75  modules/llm/__init__.py
 inline_cap_reached>75  modules/registry/adapters/v3_to_v2.py
 inline_cap_reached>75  modules/coder/adapters/llm/__init__.py
 inline_cap_reached>75  modules/phi/__init__.py
 inline_cap_reached>75  modules/registry/schema/ebus_events.py
 inline_cap_reached>75  modules/coder/application/__init__.py
 inline_cap_reached>75  modules/reporting/templates/addons/__init__.py
 inline_cap_reached>75  modules/reporting/second_pass/__init__.py
 inline_cap_reached>75  modules/coder/adapters/nlp/__init__.py
 inline_cap_reached>75  modules/reporter/engine.py
 inline_cap_reached>75  modules/api/services/__init__.py
 inline_cap_reached>75  modules/coder/domain_rules/registry_to_cpt/types.py
 inline_cap_reached>75  modules/reporting/second_pass/station_consistency.py
 inline_cap_reached>75  modules/coder/adapters/llm/noop_advisor.py
 inline_cap_reached>75  modules/ner/__init__.py
 inline_cap_reached>75  modules/phi/safety/__init__.py
 inline_cap_reached>75  modules/agents/structurer/structurer_agent.py
 inline_cap_reached>75  modules/registry/extractors/noop.py
 inline_cap_reached>75  modules/registry/ner_mapping/__init__.py
 inline_cap_reached>75  modules/registry/deterministic/__init__.py
 inline_cap_reached>75  modules/registry_cleaning/__init__.py
 inline_cap_reached>75  modules/registry/schema/ip_v3.py
 inline_cap_reached>75  modules/coder/code_families.py
 inline_cap_reached>75  modules/phi/adapters/__init__.py
 inline_cap_reached>75  modules/api/__init__.py
 inline_cap_reached>75  modules/infra/executors.py
 inline_cap_reached>75  modules/infra/safe_logging.py
 inline_cap_reached>75  modules/reporting/second_pass/counts_backfill.py
 inline_cap_reached>75  proc_schemas/billing.py
 inline_cap_reached>75  proc_schemas/clinical/__init__.py
 inline_cap_reached>75  proc_schemas/__init__.py
 inline_cap_reached>75  modules/registry/extraction/structurer.py
 inline_cap_reached>75  modules/ml_coder/__init__.py
 inline_cap_reached>75  modules/registry/slots/base.py
 inline_cap_reached>75  modules/coder/parallel_pathway/__init__.py
 inline_cap_reached>75  modules/reporting/second_pass/laterality_guard.py
 inline_cap_reached>75  proc_nlp/__init__.py
 inline_cap_reached>75  proc_schemas/envelope_models.py
 inline_cap_reached>75  modules/domain/coding_rules/__init__.py
 inline_cap_reached>75  modules/phi/adapters/encryption_insecure_demo.py
 inline_cap_reached>75  modules/registry/slots/imaging.py
 inline_cap_reached>75  modules/agents/summarizer/summarizer_agent.py
 inline_cap_reached>75  modules/common/logger.py
 inline_cap_reached>75  modules/reporting/coder_view.py
 inline_cap_reached>75  modules/domain/knowledge_base/models.py
 inline_cap_reached>75  modules/registry/application/__init__.py
 inline_cap_reached>75  modules/registry/pipelines/v3_pipeline.py
 inline_cap_reached>75  modules/infra/perf.py
 inline_cap_reached>75  modules/registry/__init__.py
 inline_cap_reached>75  modules/ml_coder/utils.py
 inline_cap_reached>75  modules/reporter/schema.py
 inline_cap_reached>75  modules/registry/self_correction/types.py
 inline_cap_reached>75  modules/coder/domain_rules/registry_to_cpt/engine.py
 inline_cap_reached>75  modules/api/guards.py
 inline_cap_reached>75  modules/coder/__init__.py
 inline_cap_reached>75  modules/coder/types.py
 inline_cap_reached>75  modules/ml_coder/valid_ip_codes.py
 inline_cap_reached>75  modules/registry/schema_filter.py
 inline_cap_reached>75  modules/registry/slots/disposition.py
 inline_cap_reached>75  proc_schemas/shared/ebus_events.py
 inline_cap_reached>75  modules/common/exceptions.py
 inline_cap_reached>75  modules/registry/slots/pleura.py
 inline_cap_reached>75  modules/api/schemas/__init__.py
 inline_cap_reached>75  modules/phi/adapters/scrubber_stub.py
 inline_cap_reached>75  modules/phi/adapters/audit_logger_db.py
 inline_cap_reached>75  modules/registry/slots/indication.py
 inline_cap_reached>75  modules/common/spans.py
 inline_cap_reached>75  modules/common/knowledge_cli.py
 inline_cap_reached>75  modules/phi/adapters/fernet_encryption.py
 inline_cap_reached>75  modules/api/readiness.py
 inline_cap_reached>75  modules/registry/schema.py
 inline_cap_reached>75  modules/domain/reasoning/models.py
 inline_cap_reached>75  modules/phi/db.py
 inline_cap_reached>75  modules/registry/schema_granular.py
 inline_cap_reached>75  modules/domain/knowledge_base/repository.py
 inline_cap_reached>75  modules/registry/slots/complications.py
 inline_cap_reached>75  modules/common/rules_engine/ncci.py
 inline_cap_reached>75  proc_schemas/procedure_report.py
 inline_cap_reached>75  modules/coder/reconciliation/__init__.py
 inline_cap_reached>75  modules/registry/ml/__init__.py
 inline_cap_reached>75  modules/infra/llm_control.py
 inline_cap_reached>75  proc_schemas/reasoning.py
 inline_cap_reached>75  modules/domain/text/negation.py
 inline_cap_reached>75  modules/ml_coder/preprocessing.py
 inline_cap_reached>75  modules/registry/slots/tblb.py
 inline_cap_reached>75  modules/coder/parallel_pathway/reconciler.py
 inline_cap_reached>75  modules/reporting/__init__.py
 inline_cap_reached>75  modules/coder/ncci.py
 inline_cap_reached>75  modules/coder/constants.py
 inline_cap_reached>75  modules/coder/phi_gating.py
 inline_cap_reached>75  modules/phi/ports.py
 inline_cap_reached>75  modules/registry/schema/ip_v3_extraction.py
 inline_cap_reached>75  modules/registry/legacy/supabase_sink.py
 inline_cap_reached>75  modules/registry/audit/audit_types.py
 inline_cap_reached>75  modules/agents/parser/parser_agent.py
 inline_cap_reached>75  modules/registry/slots/dilation.py
 inline_cap_reached>75  modules/ml_coder/training_losses.py
 inline_cap_reached>75  modules/coder/peripheral_rules.py
 inline_cap_reached>75  modules/registry/label_fields.py
 inline_cap_reached>75  modules/reporting/metadata.py
 inline_cap_reached>75  modules/registry/legacy/adapters/base.py
 inline_cap_reached>75  modules/registry/self_correction/__init__.py
 inline_cap_reached>75  modules/ml_coder/self_correction.py
 inline_cap_reached>75  modules/registry/slots/sedation.py
 inline_cap_reached>75  modules/common/text_cleaning.py
 inline_cap_reached>75  modules/common/rules_engine/mer.py
 inline_cap_reached>75  modules/reporter/prompts.py
 inline_cap_reached>75  modules/proc_ml_advisor/__init__.py
 inline_cap_reached>75  modules/llm/client.py
 inline_cap_reached>75  modules/reporting/inference.py
 inline_cap_reached>75  modules/phi/safety/protected_terms.py
 inline_cap_reached>75  modules/registry/slots/ebus.py
 inline_cap_reached>75  modules/common/text_io.py
 inline_cap_reached>75  modules/domain/coding_rules/mer.py
 inline_cap_reached>75  modules/domain/coding_rules/ncci.py
 inline_cap_reached>75  modules/domain/rvu/calculator.py
 inline_cap_reached>75  modules/ml_coder/thresholds.py
 inline_cap_reached>75  modules/api/routes/phi_demo_cases.py
 inline_cap_reached>75  modules/reporter/cli.py
 inline_cap_reached>75  modules/common/rvu_calc.py
 inline_cap_reached>75  modules/common/umls_linking.py
 inline_cap_reached>75  modules/api/adapters/response_adapter.py
 inline_cap_reached>75  modules/coder/ebus_extractor.py
 inline_cap_reached>75  modules/registry/adapters/schema_registry.py
 inline_cap_reached>75  modules/ml_coder/distillation_io.py
 inline_cap_reached>75  proc_nlp/umls_linker.py
 inline_cap_reached>75  modules/registry/summarize.py
 inline_cap_reached>75  modules/common/rules_engine/dsl.py
 inline_cap_reached>75  proc_nlp/normalize_proc.py
 inline_cap_reached>75  modules/infra/cache.py
 inline_cap_reached>75  modules/registry/legacy/adapter.py
 inline_cap_reached>75  modules/coder/peripheral_extractor.py
 inline_cap_reached>75  modules/infra/settings.py
 inline_cap_reached>75  proc_schemas/coding.py
 inline_cap_reached>75  modules/coder/posthoc.py
 inline_cap_reached>75  proc_schemas/registry/ip_v2.py
 inline_cap_reached>75  modules/coder/sectionizer.py
 inline_cap_reached>75  modules/ml_coder/registry_label_schema.py
 inline_cap_reached>75  modules/registry/slots/blvr.py
 inline_cap_reached>75  modules/api/phi_redaction.py
 inline_cap_reached>75  modules/common/knowledge_schema.py
 inline_cap_reached>75  modules/common/model_capabilities.py
 inline_cap_reached>75  modules/api/phi_dependencies.py
 inline_cap_reached>75  modules/registry/extraction/focus.py
 inline_cap_reached>75  modules/ml_coder/registry_label_constraints.py
 inline_cap_reached>75  modules/coder/schema.py
 inline_cap_reached>75  modules/agents/contracts.py
 inline_cap_reached>75  modules/registry/tags.py
 inline_cap_reached>75  modules/registry/self_correction/prompt_improvement.py
 inline_cap_reached>75  modules/registry/slots/stent.py
 inline_cap_reached>75  modules/registry_cleaning/logging_utils.py
 inline_cap_reached>75  modules/registry/audit/compare.py
 inline_cap_reached>75  proc_schemas/clinical/common.py
 inline_cap_reached>75  modules/registry/ebus_config.py
 inline_cap_reached>75  modules/registry/self_correction/judge.py
 inline_cap_reached>75  modules/common/sectionizer.py
 inline_cap_reached>75  modules/coder/adapters/nlp/simple_negation_detector.py
 inline_cap_reached>75  modules/registry/cli.py
 inline_cap_reached>75  modules/api/schemas/qa.py
 inline_cap_reached>75  modules/api/phi_demo_store.py
 inline_cap_reached>75  modules/api/gemini_client.py
 inline_cap_reached>75  modules/registry/self_correction/apply.py
 inline_cap_reached>75  modules/coder/ebus_rules.py
 inline_cap_reached>75  modules/phi/models.py
 inline_cap_reached>75  modules/registry/deterministic/anatomy.py
 inline_cap_reached>75  modules/api/schemas/base.py
 inline_cap_reached>75  modules/infra/nlp_warmup.py
 inline_cap_reached>75  modules/ner/entity_types.py
 inline_cap_reached>75  modules/coder/parallel_pathway/confidence_combiner.py
 inline_cap_reached>75  modules/registry_cleaning/consistency_utils.py
 inline_cap_reached>75  modules/registry/slots/therapeutics.py
 inline_cap_reached>75  modules/registry/processing/navigation_fiducials.py
 inline_cap_reached>75  modules/domain/procedure_store/repository.py
 inline_cap_reached>75  proc_schemas/clinical/pleural.py
 inline_cap_reached>75  modules/coder/cli.py
 inline_cap_reached>75  modules/reporting/ip_addons.py
 inline_cap_reached>75  modules/coder/application/candidate_expansion.py
 inline_cap_reached>75  modules/agents/run_pipeline.py
 inline_cap_reached>75  modules/registry/ner_mapping/entity_to_registry.py
 inline_cap_reached>75  modules/domain/coding_rules/evidence_context.py
 inline_cap_reached>75  modules/registry/model_runtime.py
 inline_cap_reached>75  modules/coder/adapters/ml_ranker.py
 inline_cap_reached>75  modules/coder/adapters/persistence/inmemory_procedure_store.py
 inline_cap_reached>75  proc_schemas/registry/ip_v3.py
 inline_cap_reached>75  modules/registry/inference_pytorch.py
 inline_cap_reached>75  modules/registry_cleaning/clinical_qc.py
 inline_cap_reached>75  modules/registry/ml/evaluate.py
 inline_cap_reached>75  modules/coder/application/procedure_type_detector.py
 inline_cap_reached>75  modules/api/coder_adapter.py
 inline_cap_reached>75  modules/api/routes/unified_process.py
 inline_cap_reached>75  modules/api/routes/metrics.py
 inline_cap_reached>75  modules/registry/schema/adapters/v3_to_v2.py
 inline_cap_reached>75  modules/registry/processing/focus.py
 inline_cap_reached>75  modules/ml_coder/training.py
 inline_cap_reached>75  modules/registry/processing/navigation_targets.py
 inline_cap_reached>75  modules/phi/service.py
 inline_cap_reached>75  modules/reporting/validation.py
 inline_cap_reached>75  modules/ml_coder/predictor.py
 inline_cap_reached>75  modules/api/routes_registry.py
 inline_cap_reached>75  modules/registry/self_correction/validation.py
 inline_cap_reached>75  modules/registry/application/registry_builder.py
 inline_cap_reached>75  modules/coder/adapters/nlp/keyword_mapping_loader.py
 inline_cap_reached>75  modules/registry/processing/masking.py
 inline_cap_reached>75  modules/api/routes/phi.py
 inline_cap_reached>75  modules/common/knowledge.py
 inline_cap_reached>75  modules/registry/legacy/adapters/pleural.py
 inline_cap_reached>75  modules/registry/evidence/verifier.py
 inline_cap_reached>75  modules/registry/application/pathology_extraction.py
 inline_cap_reached>75  modules/registry/ner_mapping/procedure_extractor.py
 inline_cap_reached>75  modules/api/dependencies.py
 inline_cap_reached>75  modules/registry_cleaning/schema_utils.py
 inline_cap_reached>75  modules/registry/extractors/v3_extractor.py
 inline_cap_reached>75  modules/coder/application/coding_service.py
 inline_cap_reached>75  modules/coder/domain_rules/__init__.py
 inline_cap_reached>75  modules/coder/rules.py
 inline_cap_reached>75  modules/ml_coder/registry_predictor.py
 inline_cap_reached>75  modules/registry/ml/models.py
 inline_cap_reached>75  modules/registry/audit/raw_ml_auditor.py
 inline_cap_reached>75  modules/registry/v2_booleans.py
 inline_cap_reached>75  modules/domain/coding_rules/json_rules_evaluator.py
 inline_cap_reached>75  modules/registry/inference_onnx.py
 inline_cap_reached>75  modules/autocode/ip_kb/canonical_rules.py
 inline_cap_reached>75  modules/api/services/qa_pipeline.py
 inline_cap_reached>75  modules/ml_coder/registry_training.py
 inline_cap_reached>75  modules/coder/reconciliation/pipeline.py
 inline_cap_reached>75  modules/ner/inference.py
 inline_cap_reached>75  modules/registry/ner_mapping/station_extractor.py
 inline_cap_reached>75  modules/coder/rules_engine.py
 inline_cap_reached>75  modules/registry/application/cpt_registry_mapping.py
 inline_cap_reached>75  modules/phi/safety/veto.py
 inline_cap_reached>75  modules/registry/application/coding_support_builder.py
 inline_cap_reached>75  proc_schemas/clinical/airway.py
 inline_cap_reached>75  modules/common/openai_responses.py
 inline_cap_reached>75  modules/coder/reconciliation/reconciler.py
 inline_cap_reached>75  modules/coder/adapters/llm/gemini_advisor.py
 inline_cap_reached>75  modules/registry/normalization.py
 inline_cap_reached>75  modules/coder/adapters/persistence/csv_kb_adapter.py
 inline_cap_reached>75  modules/registry_cleaning/cpt_utils.py
 inline_cap_reached>75  modules/domain/coding_rules/rule_engine.py
 inline_cap_reached>75  modules/coder/parallel_pathway/orchestrator.py
 inline_cap_reached>75  modules/registry/model_bootstrap.py
 inline_cap_reached>75  modules/registry/extractors/llm_detailed.py
 inline_cap_reached>75  modules/coder/adapters/llm/openai_compat_advisor.py
 inline_cap_reached>75  modules/coder/adapters/persistence/supabase_procedure_store.py
 inline_cap_reached>75  modules/registry/legacy/adapters/airway.py
 inline_cap_reached>75  modules/phi/adapters/presidio_scrubber.py
 inline_cap_reached>75  modules/ml_coder/data_prep.py
 inline_cap_reached>75  modules/registry/schema/v2_dynamic.py
 inline_cap_reached>75  modules/coder/application/smart_hybrid_policy.py
 inline_cap_reached>75  modules/reporting/macro_engine.py
 inline_cap_reached>75  modules/ml_coder/label_hydrator.py
 inline_cap_reached>75  modules/api/normalization.py
 inline_cap_reached>75  modules/registry/transform.py
 inline_cap_reached>75  modules/coder/adapters/registry_coder.py
 inline_cap_reached>75  modules/ml_coder/registry_data_prep.py
 inline_cap_reached>75  modules/registry/schema/granular_models.py
 inline_cap_reached>75  modules/domain/coding_rules/coding_rules_engine.py
 inline_cap_reached>75  modules/api/ml_advisor_router.py
 inline_cap_reached>75  modules/registry/schema/granular_logic.py
 inline_cap_reached>75  modules/phi/adapters/phi_redactor_hybrid.py
 inline_cap_reached>75  modules/registry/ml/action_predictor.py
 inline_cap_reached>75  modules/registry/self_correction/keyword_guard.py
 inline_cap_reached>75  modules/coder/dictionary.py
 inline_cap_reached>75  modules/common/llm.py
 inline_cap_reached>75  modules/proc_ml_advisor/schemas.py
 inline_cap_reached>75  modules/api/routes/procedure_codes.py
 inline_cap_reached>75  modules/api/fastapi_app.py
 inline_cap_reached>75  modules/extraction/postprocessing/clinical_guardrails.py
 inline_cap_reached>75  modules/coder/domain_rules/registry_to_cpt/coding_rules.py
 inline_cap_reached>75  modules/autocode/ip_kb/ip_kb.py
 inline_cap_reached>75  modules/registry/prompts.py
 inline_cap_reached>75  modules/reporting/engine.py
 inline_cap_reached>75  modules/registry/deterministic_extractors.py
 inline_cap_reached>75  modules/registry/engine.py
 inline_cap_reached>75  modules/registry/postprocess.py
 inline_cap_reached>75  modules/registry/application/registry_service.py
     too_large>200000B  modules/api/static/phi_redactor/vendor/phi_distilbert_ner/vocab.txt
     too_large>200000B  modules/api/static/phi_redactor/vendor/phi_distilbert_ner_quant/vocab.txt
     too_large>200000B  modules/api/static/phi_redactor/vendor/phi_distilbert_ner/tokenizer.json
     too_large>200000B  modules/api/static/phi_redactor/vendor/phi_distilbert_ner_quant/tokenizer.json
     too_large>200000B  modules/api/static/phi_redactor/transformers.legacy.js
     too_large>200000B  modules/api/static/phi_redactor/transformers.min.js
```

## Inlined file contents

---
### `scripts/test_debulk.py`
- Size: `540` bytes
```
import pandas as pd

# Load the data
df = pd.read_csv('data/ml_training/registry_train.csv')

# Filter for the anomaly: Debulking=1 but Rigid=0
anomaly = df[
    (df['tumor_debulking_non_thermal'] == 1) & 
    (df['rigid_bronchoscopy'] == 0)
]

print(f"Found {len(anomaly)} suspicious cases.\n")

# Print the first 200 characters of a few examples to verify context
for i, row in anomaly.head(5).iterrows():
    print(f"--- Case {row.get('encounter_id', 'Unknown')} ---")
    print(row['note_text'][:300].replace('\n', ' '))
    print("\n")
```

---
### `scripts/generate_blank_granular_note_scripts.py`
- Size: `697` bytes
```
from __future__ import annotations

from pathlib import Path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    target_dir = repo_root / "data" / "granular annotations" / "Python_update_scripts"
    target_dir.mkdir(parents=True, exist_ok=True)

    created = 0
    skipped = 0

    for note_num in range(129, 265):
        path = target_dir / f"note_{note_num:03d}.py"
        if path.exists():
            skipped += 1
            continue
        path.write_text("", encoding="utf-8")
        created += 1

    print(f"Target: {target_dir}")
    print(f"Created: {created}")
    print(f"Skipped (already existed): {skipped}")


if __name__ == "__main__":
    main()


```

---
### `scripts/render_report.py`
- Size: `988` bytes
```
#!/usr/bin/env python3
"""Render a structured report from an extraction JSON payload."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from modules.reporting import compose_structured_report_from_extraction


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a structured IP report from extraction JSON.")
    parser.add_argument("--input", required=True, help="Path to extraction JSON payload.")
    parser.add_argument("--output", help="Path to write the rendered report. Prints to stdout if omitted.")
    parser.add_argument("--strict", action="store_true", help="Enable style strict mode validation.")
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text())
    report = compose_structured_report_from_extraction(payload, strict=args.strict)

    if args.output:
        Path(args.output).write_text(report)
    else:
        print(report)


if __name__ == "__main__":
    main()

```

---
### `scripts/prepare_data.py`
- Size: `1026` bytes
```
import pandas as pd
from pathlib import Path

from modules.ml_coder.utils import clean_cpt_codes, join_codes

def main():
    # Path to your uploaded synthetic CSV
    input_path = Path("data/cpt_multilabel_training_data_updated.csv")
    output_path = Path("data/cpt_training_data_cleaned.csv")
    
    if not input_path.exists():
        print(f"Error: Could not find {input_path}")
        return

    print("Reading raw data...")
    df = pd.read_csv(input_path)
    
    # Apply cleaning
    print("Fixing CPT code formats...")
    df["verified_cpt_codes"] = df["verified_cpt_codes"].apply(clean_cpt_codes)
    df["verified_cpt_codes"] = df["verified_cpt_codes"].apply(join_codes)
    
    # Drop rows that ended up empty
    df = df[df["verified_cpt_codes"] != ""]
    
    # Ensure directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    df.to_csv(output_path, index=False)
    print(f"Cleaned data saved to {output_path} with {len(df)} valid rows.")

if __name__ == "__main__":
    main()

```

---
### `scripts/merge_registry.py`
- Size: `1173` bytes
```
import pandas as pd
import os

# Paths
files = [
    # Base/master human labels (typically large)
    "data/ml_training/registry_human_master.csv",
    # Smaller exports can also be present; include them if available
    "data/ml_training/registry_human.csv",
    "data/ml_training/registry_human_updates.csv",
    # Targeted fix batches should override everything else
    "data/ml_training/registry_debulking_fixes.csv",
]

dfs = []
for f in files:
    if os.path.exists(f):
        print(f"Loading {f}...")
        dfs.append(pd.read_csv(f))
    else:
        print(f"Warning: {f} not found (skipping)")

if dfs:
    # Concatenate and drop duplicates (keeping the latest fix if IDs overlap)
    master = pd.concat(dfs, ignore_index=True)
    # Deduplicate by encounter_id, keeping the last (newest) entry
    if 'encounter_id' in master.columns:
        master = master.drop_duplicates(subset=['encounter_id'], keep='last')
    
    output_path = "data/ml_training/registry_human_MASTER.csv"
    master.to_csv(output_path, index=False)
    print(f"\n✅ Success! Combined {len(master)} human labels into {output_path}")
else:
    print("\n❌ No files found to merge.")

```

---
### `scripts/validate_jsonschema.py`
- Size: `1351` bytes
```
#!/usr/bin/env python3
"""
Validate a JSON Schema file.

Supports draft-07 and 2020-12 (auto-detected via the schema's "$schema" field).

Usage:
    python scripts/validate_jsonschema.py --schema data/knowledge/IP_Registry.json
"""

import argparse
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, Draft7Validator


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--schema",
        required=True,
        help="Path to the JSON schema file (e.g., data/knowledge/IP_Registry_Enhanced_v2.json)",
    )
    args = parser.parse_args()

    schema_path = Path(args.schema)
    if not schema_path.is_file():
        print(f"ERROR: Schema file not found at {schema_path}", file=sys.stderr)
        return 1

    with schema_path.open() as f:
        schema = json.load(f)

    declared = str(schema.get("$schema") or "").lower()
    if "draft-07" in declared or "draft/07" in declared:
        Draft7Validator.check_schema(schema)
    else:
        # Default to 2020-12 when explicit or unknown. This keeps the script useful
        # for newer schemas without requiring flags.
        Draft202012Validator.check_schema(schema)
    print(f"Schema OK: {schema_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```

---
### `scripts/cpt_check.py`
- Size: `1430` bytes
```
"""
Find any token pieces that look like split 5-digit numbers still labeled GEO.

Example: ["12", "##345"] => "12345"
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--path",
        type=Path,
        default=Path("data/ml_training/distilled_phi_labels.jsonl"),
        help="Path to distilled_phi_labels.jsonl",
    )
    parser.add_argument("--limit", type=int, default=20, help="Stop after printing N matches")
    args = parser.parse_args()

    bad = 0
    with args.path.open() as f:
        for line in f:
            r = json.loads(line)
            toks, labs = r["tokens"], r["ner_tags"]
            for i in range(len(toks) - 1):
                if toks[i].isdigit() and toks[i + 1].startswith("##"):
                    combined = toks[i] + toks[i + 1][2:]
                    if re.fullmatch(r"\d{5}", combined) and (
                        "GEO" in labs[i] or "GEO" in labs[i + 1]
                    ):
                        bad += 1
                        print("BAD", combined, labs[i], labs[i + 1], "id=", r.get("id"))
                        if bad >= args.limit:
                            print("done, bad=", bad)
                            return 0

    print("done, bad=", bad)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```

---
### `scripts/check_pydantic_models.py`
- Size: `1505` bytes
```
#!/usr/bin/env python3
"""
Smoke-test imports for core Pydantic models and key services.

This is intentionally simple: if any import fails, the script exits non-zero
so `make validate-schemas` / CI will catch it.
"""

import importlib
import sys
from pathlib import Path


_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

MODULES = [
    # Clinical schemas
    "proc_schemas.clinical.airway",
    "proc_schemas.clinical.pleural",

    # Reasoning + coding lifecycle models
    "proc_schemas.reasoning",
    "proc_schemas.coding",

    # Registry models
    "proc_schemas.registry.ip_v2",
    "proc_schemas.registry.ip_v3",

    # Reporter agents contracts
    "modules.agents.contracts",

    # Coder application (pulls in smart_hybrid policy etc.)
    "modules.coder.application.coding_service",
    "modules.coder.application.smart_hybrid_policy",
]


def main() -> int:
    failed = False

    for mod in MODULES:
        try:
            importlib.import_module(mod)
            print(f"Imported OK: {mod}")
        except Exception as exc:  # noqa: BLE001
            failed = True
            print(f"FAILED to import {mod}: {exc}", file=sys.stderr)

    if failed:
        print("One or more modules failed to import.", file=sys.stderr)
        return 1

    print("All Pydantic model imports OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```

---
### `scripts/preflight.py`
- Size: `1609` bytes
```
"""Basic environment + asset validation ahead of CI."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml


def check_spacy_stack() -> None:
    import scispacy  # type: ignore
    import spacy  # type: ignore

    print(f"spaCy {spacy.__version__} detected")
    print(f"scispaCy {scispacy.__version__} detected")


def check_sklearn() -> None:
    import sklearn

    version = sklearn.__version__
    if not version.startswith("1.7"):
        raise RuntimeError(f"sklearn version must be 1.7.x, found {version}")
    print(f"sklearn {version} pinned OK")


def check_rules_and_templates() -> None:
    root = Path(__file__).resolve().parents[1]
    config_dir = root / "configs"
    for path in config_dir.rglob("*.yaml"):
        yaml.safe_load(path.read_text())
    print("YAML configs parsed")

    from modules.reporting.engine import compose_report_from_text

    text = "EBUS-TBNA of stations 7 and 4R; 3 FNA passes at each."
    report, note = compose_report_from_text(text, {"plan": "Recover in PACU"})
    assert "Targets & Specimens" in note
    from modules.autocode.engine import autocode

    billing = autocode(report)
    assert billing.codes, "Autocoder produced zero codes for smoke test"
    print("Templates render and coder returns codes")


def main() -> None:
    check_spacy_stack()
    check_sklearn()
    check_rules_and_templates()
    print("Preflight completed ✅")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover
        print(f"Preflight failed: {exc}", file=sys.stderr)
        raise

```

---
### `scripts/verify_registry_runtime_bundle.py`
- Size: `1728` bytes
```
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _truthy_env(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in ("1", "true", "yes")


if not _truthy_env("PROCSUITE_SKIP_DOTENV"):
    load_dotenv(override=False)

from modules.registry.model_runtime import (  # noqa: E402
    get_registry_runtime_dir,
    resolve_model_backend,
    verify_registry_runtime_bundle,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify registry runtime model bundle artifacts."
    )
    parser.add_argument(
        "--backend",
        choices=["pytorch", "onnx", "auto"],
        default=None,
        help="Backend to validate (defaults to MODEL_BACKEND resolution).",
    )
    parser.add_argument(
        "--runtime-dir",
        default=None,
        help="Override registry runtime directory.",
    )
    args = parser.parse_args()

    runtime_dir = Path(args.runtime_dir) if args.runtime_dir else get_registry_runtime_dir()
    backend = args.backend or resolve_model_backend()

    try:
        warnings = verify_registry_runtime_bundle(
            backend=backend,
            runtime_dir=runtime_dir,
        )
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"OK: registry runtime bundle valid (backend={backend}, runtime_dir={runtime_dir})")
    for warning in warnings:
        print(f"WARNING: {warning}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```

---
### `scripts/check_onnx_inputs.py`
- Size: `1833` bytes
```
#!/usr/bin/env python3
"""Check ONNX graph inputs for transformers.js compatibility."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

DEFAULT_REQUIRED = ("input_ids", "attention_mask")


def build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description="Validate that an ONNX model exposes required graph inputs (e.g., input_ids, attention_mask)."
    )
    ap.add_argument("onnx_path", type=Path, help="Path to an ONNX model file (e.g., onnx/model.onnx)")
    ap.add_argument(
        "--require",
        action="append",
        default=list(DEFAULT_REQUIRED),
        help="Input name to require (repeatable). Default: input_ids + attention_mask",
    )
    return ap


def main() -> int:
    args = build_arg_parser().parse_args()
    onnx_path: Path = args.onnx_path
    required: list[str] = args.require

    if not onnx_path.exists():
        print(f"ERROR: ONNX file not found: {onnx_path}", file=sys.stderr)
        return 2

    try:
        import onnx  # type: ignore[import-untyped]
    except ImportError as exc:
        print("ERROR: `onnx` is not installed. Install with: pip install onnx", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return 2

    m = onnx.load(str(onnx_path))
    input_names = [i.name for i in m.graph.input]

    print(f"ONNX: {onnx_path}")
    print(f"Inputs ({len(input_names)}): {', '.join(input_names) if input_names else '(none)'}")

    missing = [name for name in required if name not in input_names]
    if missing:
        print(
            f"FAIL: Missing required inputs: {missing}. Found: {input_names}",
            file=sys.stderr,
        )
        return 1

    print("OK: Required inputs present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


```

---
### `scripts/patch.py`
- Size: `1918` bytes
```
#!/usr/bin/env python3
"""Patch validator / status script.

The repository previously had a large, non-executable draft `scripts/patch.py` that mixed
code snippets and patch instructions. That draft could not run (SyntaxError).

This script is now a *validator* you can run to confirm the intended updates exist
in the current checkout.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

# Ensure repo root is on sys.path (so `import modules.*` works when running as a script).
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def _check_import(module: str) -> None:
    importlib.import_module(module)


def main() -> int:
    failures: list[str] = []

    # New/centralized registry modules
    for mod in ("modules.registry.tags", "modules.registry.schema_filter"):
        try:
            _check_import(mod)
        except Exception as exc:  # noqa: BLE001
            failures.append(f"FAILED import {mod}: {exc}")

    # Ensure auditors support warm/is_loaded
    try:
        from modules.registry.audit.raw_ml_auditor import RawMLAuditor, RegistryFlagAuditor

        for cls in (RawMLAuditor, RegistryFlagAuditor):
            for meth in ("warm", "is_loaded"):
                if not hasattr(cls, meth):
                    failures.append(f"{cls.__name__} missing method {meth}()")
    except Exception as exc:  # noqa: BLE001
        failures.append(f"FAILED import auditors: {exc}")

    if failures:
        print("Patch validation FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1

    print("Patch validation OK: registry tag/schema_filter modules and auditor helpers are present.")
    print("Optional prompt gating is available via: REGISTRY_PROMPT_FILTER_BY_FAMILY=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())



```

---
### `scripts/evaluate_cpt.py`
- Size: `2032` bytes
```
import json
from pathlib import Path

# Ensure imports resolve
import sys
sys.path.append(str(Path.cwd()))

import joblib  # noqa: E402
import pandas as pd  # noqa: E402

from modules.ml_coder.training import MLB_PATH, PIPELINE_PATH  # noqa: E402
from modules.ml_coder.utils import clean_cpt_codes, join_codes  # noqa: E402


def load_models():
    if not PIPELINE_PATH.exists() or not MLB_PATH.exists():
        raise FileNotFoundError("Trained models not found. Run make train-cpt first.")
    pipeline = joblib.load(PIPELINE_PATH)
    mlb = joblib.load(MLB_PATH)
    return pipeline, mlb


def main():
    input_path = Path("data/cpt_multilabel_training_data_updated.csv")
    error_log = Path("data/cpt_errors.jsonl")

    if not input_path.exists():
        print(f"Missing CPT data at {input_path}")
        return

    pipeline, mlb = load_models()

    df = pd.read_csv(input_path)
    df["note_text"] = df["note_text"].astype(str)
    df["gold_codes"] = df["verified_cpt_codes"].apply(clean_cpt_codes)

    error_log.write_text("")
    total = 0
    correct = 0

    with error_log.open("a") as elog:
        for _, row in df.iterrows():
            note = row["note_text"]
            gold_codes = row["gold_codes"]
            if not gold_codes:
                continue
            total += 1

            pred_binary = pipeline.predict([note])
            pred_codes = mlb.inverse_transform(pred_binary)[0]
            pred_set = set(pred_codes)
            gold_set = set(gold_codes)

            if pred_set == gold_set:
                correct += 1
                continue

            entry = {
                "note_text": note[:2000],
                "gold_codes": list(gold_set),
                "predicted_codes": list(pred_set),
            }
            elog.write(json.dumps(entry) + "\n")

    acc = (correct / total) * 100 if total else 0
    print(f"Evaluated {total} examples. Exact-match accuracy: {acc:.1f}%")
    print(f"CPT error log written to {error_log}")


if __name__ == "__main__":
    main()

```

---
### `scripts/clean_ner.py`
- Size: `2073` bytes
```
import json
import os
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).resolve().parents[1] / "data" / "ml_training" / "granular_ner"
input_file = BASE_DIR / "ner_dataset_all.jsonl"
output_clean = BASE_DIR / "clean_training_data.jsonl"
output_empty = BASE_DIR / "empty_notes_to_fix.jsonl"
BASE_DIR.mkdir(parents=True, exist_ok=True)

# Counters
total_notes = 0
valid_notes = 0
empty_notes = 0

print(f"Scanning {input_file}...")

with open(input_file, "r", encoding="utf-8") as f_in, \
     open(output_clean, "w", encoding="utf-8") as f_clean, \
     open(output_empty, "w", encoding="utf-8") as f_empty:

    for line in f_in:
        line = line.strip()
        if not line:
            continue

        total_notes += 1
        try:
            data = json.loads(line)
            note_id = data.get('id', 'unknown_id')
            entities = data.get('entities', [])

            # CHECK: Is the entity list empty?
            if len(entities) == 0:
                # Write to the "To Fix" file
                json.dump(data, f_empty)
                f_empty.write('\n')
                empty_notes += 1
                # Optional: Print the IDs of empty notes to console for quick verification
                # print(f"  [!] Flagged empty note: {note_id}")
            else:
                # Write to the "Ready for Training" file
                json.dump(data, f_clean)
                f_clean.write('\n')
                valid_notes += 1

        except json.JSONDecodeError:
            print(f"  [Error] Could not decode JSON on line {total_notes}")

# Summary Report
print("-" * 30)
print(f"Processing Complete.")
print(f"Total Notes Scanned: {total_notes}")
print(f"Valid Notes (Saved to {output_clean}): {valid_notes}")
print(f"Empty Notes (Saved to {output_empty}): {empty_notes}")
print("-" * 30)

if empty_notes > 0:
    print(f"ACTION REQUIRED: Please open '{output_empty}' and annotate the {empty_notes} missing notes.")
    print("Based on your uploaded file, expect to see IDs like: note_021, note_029, note_041, note_042, etc.")
```

---
### `scripts/self_correct_registry.py`
- Size: `2224` bytes
```
import argparse
import os
from pathlib import Path

# Ensure local imports
import sys
sys.path.append(str(Path.cwd()))

from modules.registry.prompts import FIELD_INSTRUCTIONS  # noqa: E402
from modules.registry.self_correction import (  # noqa: E402
    get_allowed_values,
    suggest_improvements_for_field,
)


def main():
    parser = argparse.ArgumentParser(description="Generate registry self-correction suggestions.")
    parser.add_argument("--field", required=True, help="Field name to analyze (e.g., sedation_type)")
    parser.add_argument(
        "--max-examples",
        type=int,
        default=20,
        help="Maximum number of error examples to send to the LLM",
    )
    parser.add_argument(
        "--model",
        help="Override model for self-correction (e.g., gpt-5.1, gemini-2.5-flash-lite). Defaults to env REGISTRY_SELF_CORRECTION_MODEL.",
    )
    args = parser.parse_args()

    field_name = args.field
    if args.model:
        os.environ["REGISTRY_SELF_CORRECTION_MODEL"] = args.model

    allowed_values = get_allowed_values(field_name)
    suggestions = suggest_improvements_for_field(field_name, allowed_values, max_examples=args.max_examples)

    current_instruction = FIELD_INSTRUCTIONS.get(field_name, "No instruction available.")

    print(f"Field: {field_name}")
    print("\nCurrent instruction:")
    print(current_instruction)

    print("\nSuggested updates:")
    for key in ("updated_instruction", "python_postprocessing_rules", "comments"):
        val = suggestions.get(key, "<none>")
        print(f"{key}: {val}")

    report_path = Path(f"reports/registry_self_correction_{field_name}.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w") as f:
        f.write(f"# Registry self-correction for {field_name}\n\n")
        f.write("## Current instruction\n")
        f.write(f"{current_instruction}\n\n")
        f.write("## Suggested updates\n")
        for key in ("updated_instruction", "python_postprocessing_rules", "comments"):
            f.write(f"### {key}\n")
            f.write(f"{suggestions.get(key, '<none>')}\n\n")

    print(f"\nSuggestions written to {report_path}")


if __name__ == "__main__":
    main()

```

---
### `scripts/verify_phi_redactor_vendor_assets.py`
- Size: `2273` bytes
```
#!/usr/bin/env python3
"""Verify PHI redactor vendor assets are present for the IU bundle."""

from __future__ import annotations

import json
import sys
from pathlib import Path

VENDOR_DIR = Path("modules/api/static/phi_redactor/vendor/phi_distilbert_ner_quant")


def _error(message: str, errors: list[str]) -> None:
    errors.append(message)


def main() -> int:
    errors: list[str] = []

    if not VENDOR_DIR.exists():
        _error(f"Missing vendor directory: {VENDOR_DIR}", errors)
    elif not VENDOR_DIR.is_dir():
        _error(f"Vendor path is not a directory: {VENDOR_DIR}", errors)

    config_path = VENDOR_DIR / "config.json"
    if not config_path.exists():
        _error(f"Missing config.json: {config_path}", errors)

    onnx_dir = VENDOR_DIR / "onnx"
    onnx_model = onnx_dir / "model.onnx"
    if not onnx_model.exists():
        _error(f"Missing model.onnx: {onnx_model}", errors)

    tokenizer_json = VENDOR_DIR / "tokenizer.json"
    tokenizer_config = VENDOR_DIR / "tokenizer_config.json"
    vocab_txt = VENDOR_DIR / "vocab.txt"
    vocab_json = VENDOR_DIR / "vocab.json"
    merges_txt = VENDOR_DIR / "merges.txt"

    has_tokenizer_bundle = tokenizer_json.exists()
    has_tokenizer_parts = tokenizer_config.exists() and (vocab_txt.exists() or vocab_json.exists() or merges_txt.exists())
    if not (has_tokenizer_bundle or has_tokenizer_parts):
        _error(
            "Missing tokenizer files: expected tokenizer.json or tokenizer_config.json + vocab files",
            errors,
        )

    if config_path.exists():
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
            if "id2label" not in config and "label2id" not in config:
                _error("config.json is missing label map keys (id2label/label2id)", errors)
        except Exception as exc:  # pragma: no cover - guard for malformed config
            _error(f"Failed to parse config.json: {exc}", errors)

    if errors:
        for message in errors:
            print(f"[verify_phi_redactor_vendor_assets] ERROR: {message}", file=sys.stderr)
        return 1

    print("[verify_phi_redactor_vendor_assets] OK: PHI redactor vendor assets present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```

---
### `scripts/prodigy_prepare_registry_batch.py`
- Size: `2368` bytes
```
#!/usr/bin/env python3
"""Compatibility wrapper for the Registry Prodigy batch prep ("Diamond Loop").

The repo historically used `scripts/prodigy_prepare_registry.py`. The Diamond Loop
brief references `scripts/prodigy_prepare_registry_batch.py`, so this wrapper
provides the documented CLI while delegating to the existing implementation.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

# Ensure repo root + scripts/ are importable when running as a file.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import prodigy_prepare_registry  # noqa: E402


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-file", type=Path, required=True)
    parser.add_argument("--output-file", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=None, help="Alias for --count")
    parser.add_argument("--count", type=int, default=200, help="Number of tasks to emit")
    parser.add_argument(
        "--strategy",
        choices=["disagreement", "uncertainty", "random", "rare_boost", "hybrid"],
        default="disagreement",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("data/ml_training/registry_prodigy_manifest.json"),
        help="Manifest JSON (dedup)",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--model-dir", type=Path, default=Path("data/models/registry_runtime"))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    count = args.limit if args.limit is not None else args.count

    forwarded = [
        "--input-file",
        str(args.input_file),
        "--output-file",
        str(args.output_file),
        "--count",
        str(count),
        "--strategy",
        str(args.strategy),
        "--manifest",
        str(args.manifest),
        "--seed",
        str(args.seed),
        "--model-dir",
        str(args.model_dir),
    ]
    return int(prodigy_prepare_registry.main(forwarded))


if __name__ == "__main__":
    raise SystemExit(main())

```

---
### `scripts/phi_audit.py`
- Size: `2998` bytes
```
"""Generate a structured PHI redaction audit report for a note.

Writes a JSON report to artifacts/phi_audit/<timestamp>.json and prints it.
Intended for synthetic notes only (do not run on real PHI).
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import typer
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _truthy_env(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in ("1", "true", "yes")


if not _truthy_env("PROCSUITE_SKIP_DOTENV"):
    load_dotenv(override=False)


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")


app = typer.Typer(add_completion=False)


@app.command()
def run(
    note_path: Path = typer.Option(
        Path("tests/fixtures/notes/phi_example_note.txt"),
        exists=True,
        readable=True,
        help="Path to the note text file (synthetic only).",
    ),
    output_dir: Path = typer.Option(
        Path("artifacts/phi_audit"),
        help="Directory for audit outputs.",
    ),
    golden: Path | None = typer.Option(
        None,
        help="Optional path to write a regression fixture JSON (synthetic only).",
    ),
) -> None:
    """Run the current Presidio scrubber and emit a JSON audit report."""

    from modules.phi.adapters.presidio_scrubber import PresidioScrubber

    text = note_path.read_text(encoding="utf-8")
    scrubber = PresidioScrubber()

    scrub_result, audit = scrubber.scrub_with_audit(text)
    report: dict[str, Any] = {
        "timestamp_utc": _utc_timestamp(),
        "note_path": str(note_path),
        "original_text": text,
        **audit,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{report['timestamp_utc']}.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    # Append to a JSONL decision log for easy diffing across changes.
    jsonl_path = output_dir / "redaction_decisions.jsonl"
    jsonl_record = {
        "timestamp_utc": report["timestamp_utc"],
        "note_path": report["note_path"],
        "original_text": text,
        "redacted_text": scrub_result.scrubbed_text,
        "removed_detections": audit.get("removed_detections", []),
    }
    with jsonl_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(jsonl_record, ensure_ascii=False) + "\n")

    if golden is not None:
        golden.parent.mkdir(parents=True, exist_ok=True)
        golden_payload = dict(report)
        golden_payload.pop("timestamp_utc", None)
        golden_path = golden
        golden_path.write_text(json.dumps(golden_payload, indent=2, ensure_ascii=False), encoding="utf-8")

    typer.echo(json.dumps(report, indent=2, ensure_ascii=False))
    typer.echo(f"Wrote {out_path}", err=True)


if __name__ == "__main__":
    app()

```

---
### `scripts/create_blank_update_scripts_from_patient_note_texts.py`
- Size: `3095` bytes
```
#!/usr/bin/env python3
"""
Create blank per-patient Python update scripts.

For each JSON file in `data/knowledge/patient_note_texts/` (e.g., 74-8829-C.json),
create a matching blank Python script in:
  `data/granular annotations/Python_update_scripts/74-8829-C.py`

This is useful for a manual workflow where you later fill in one script per patient.

Usage:
  python scripts/create_blank_update_scripts_from_patient_note_texts.py \
    --input-dir data/knowledge/patient_note_texts \
    --output-dir "data/granular annotations/Python_update_scripts"
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


TEMPLATE = """\
#!/usr/bin/env python3
\"\"\"Blank patient update script (auto-generated).

Source JSON: {source_json}
\"\"\"


def main() -> None:
    # TODO: implement per-patient updates here
    pass


if __name__ == \"__main__\":
    main()
"""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Create blank .py scripts for each patient_note_texts/*.json")
    p.add_argument(
        "--input-dir",
        type=Path,
        default=Path("data/knowledge/patient_note_texts"),
        help="Directory containing per-patient JSON files.",
    )
    p.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/granular annotations/Python_update_scripts"),
        help="Directory to write per-patient blank .py scripts.",
    )
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="If set, overwrite existing .py files.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="If set, do not write files; only log actions.",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    args = parse_args(argv)
    if not args.input_dir.exists():
        raise FileNotFoundError(f"Missing input dir: {args.input_dir}")

    json_paths = sorted(args.input_dir.glob("*.json"))
    if not json_paths:
        raise FileNotFoundError(f"No *.json files found in: {args.input_dir}")

    if not args.dry_run:
        args.output_dir.mkdir(parents=True, exist_ok=True)

    created = 0
    skipped_exists = 0
    for jp in json_paths:
        out_path = args.output_dir / f"{jp.stem}.py"
        if out_path.exists() and not args.overwrite:
            skipped_exists += 1
            continue

        content = TEMPLATE.format(source_json=str(jp))
        if args.dry_run:
            logger.info("Would write %s", out_path)
        else:
            out_path.write_text(content, encoding="utf-8")
        created += 1

    logger.info(
        "Done. input_json=%d created=%d skipped_exists=%d output_dir=%s",
        len(json_paths),
        created,
        skipped_exists,
        args.output_dir,
    )


if __name__ == "__main__":
    main(sys.argv[1:])


```

---
### `scripts/find_phi_failures.py`
- Size: `3216` bytes
```
import json
import re
import glob
from pathlib import Path

# --- Configuration ---
# Where the "bad" (scrubbed) files are
SCRUBBED_DIR = "data/knowledge/golden_extractions_scrubbed"
# Where the "original" (raw) files are (to get the text for Prodigy)
ORIGINAL_DIR = "data/knowledge/golden_extractions"
OUTPUT_FILE = "failures.jsonl"

# Regex patterns for common leaks
LEAK_PATTERNS = [
    (r"\b(19|20)\d{2}\b", "Unredacted Year"),  # 1990-2029
    (r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", "Unredacted Date"), # 1/1/2025
    (r"(?i)\b(mr\.|mrs\.|ms\.|dr\.)\s+[A-Z][a-z]+", "Titled Name"), # Mr. Smith
    (r"(?i)\b(patient|pt)\s*:\s*[A-Z][a-z]+", "Header Name"), # Patient: Smith
    (r"\b\d{3}-\d{2}-\d{4}\b", "SSN Pattern"),
]

def load_json_robust(path):
    """Helper to load JSON whether it's a dict or a list-wrapped dict."""
    with open(path, 'r') as f:
        data = json.load(f)
    
    # Unwrap list if necessary
    if isinstance(data, list):
        if len(data) > 0:
            return data[0]
        else:
            return {} # Empty list
    return data

def scan_for_failures():
    failures = []
    seen_ids = set()
    
    print(f"Scanning {SCRUBBED_DIR} for leaks...")
    files = glob.glob(f"{SCRUBBED_DIR}/*.json")
    
    if not files:
        print(f"WARNING: No JSON files found in {SCRUBBED_DIR}")
        return

    for file_path in files:
        try:
            # 1. Check the scrubbed file for leaks
            data = load_json_robust(file_path)
            scrubbed_text = data.get('note_text', '')

            if not scrubbed_text:
                continue

            reasons = []
            for pattern, name in LEAK_PATTERNS:
                if re.search(pattern, scrubbed_text):
                    reasons.append(name)

            # 2. If leak found, get ORIGINAL text for Prodigy
            if reasons:
                filename = Path(file_path).name
                original_path = Path(ORIGINAL_DIR) / filename
                
                if original_path.exists():
                    orig_data = load_json_robust(original_path)
                    raw_text = orig_data.get('note_text', '')
                    
                    if raw_text:
                        # Avoid duplicates
                        if filename not in seen_ids:
                            failures.append({
                                "text": raw_text,
                                "meta": {
                                    "file": filename,
                                    "suspected_leaks": ", ".join(reasons)
                                }
                            })
                            seen_ids.add(filename)
                            print(f"Found leak in {filename}: {reasons}")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    # 3. Write to JSONL
    if failures:
        with open(OUTPUT_FILE, 'w') as out:
            for entry in failures:
                out.write(json.dumps(entry) + "\n")
        print(f"Done. Found {len(failures)} failures. Saved to {OUTPUT_FILE}")
    else:
        print("Done. No leaks found matching patterns.")

if __name__ == "__main__":
    scan_for_failures()
```

---
### `scripts/train_registry_sklearn.py`
- Size: `3233` bytes
```
#!/usr/bin/env python3
"""Train Registry Multi-Label Classifier (Sklearn Baseline).

This script is the direct replacement for the old `train_cpt_custom.py`.
It trains the "Registry First" baseline model (TF-IDF + Calibrated Logistic Regression)
using the cleaned training data generated by `data_prep.py`.

The trained model is used for:
1. "Scenario C" Hybrid Audit (catching procedures missed by CPT).
2. Baseline comparison for the RoBERTa model.

Pipeline:
    Input:  data/ml_training/registry_train.csv
    Output: data/models/registry_classifier.pkl
            data/models/registry_mlb.pkl
            data/models/registry_thresholds.json
"""

import argparse
import sys
from pathlib import Path

# Ensure project root is in python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from modules.ml_coder.registry_training import train_and_evaluate, MODELS_DIR, TRAIN_CSV_PATH, TEST_CSV_PATH

def main():
    parser = argparse.ArgumentParser(description="Train Registry Sklearn Baseline Model")
    parser.add_argument(
        "--train-csv",
        type=Path,
        default=TRAIN_CSV_PATH,
        help=f"Path to training CSV (default: {TRAIN_CSV_PATH})"
    )
    parser.add_argument(
        "--test-csv",
        type=Path,
        default=TEST_CSV_PATH,
        help=f"Path to test CSV (default: {TEST_CSV_PATH})"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=MODELS_DIR,
        help=f"Directory to save models (default: {MODELS_DIR})"
    )
    parser.add_argument(
        "--skip-eval",
        action="store_true",
        help="Skip evaluation after training"
    )

    args = parser.parse_args()

    print(f"\n{'='*60}")
    print("  Registry Model Training (Sklearn Baseline)")
    print(f"{'='*60}")
    print(f"Train Data:  {args.train_csv}")
    print(f"Test Data:   {args.test_csv}")
    print(f"Output Dir:  {args.output_dir}")
    print(f"{'='*60}\n")

    if not args.train_csv.exists():
        print(f"Error: Training file not found: {args.train_csv}")
        print("Run `python modules/ml_coder/data_prep.py` first.")
        sys.exit(1)

    try:
        if args.skip_eval:
            # Just train
            from modules.ml_coder.registry_training import train_registry_model
            train_registry_model(
                train_csv=args.train_csv,
                models_dir=args.output_dir
            )
            print("\nTraining successful. Evaluation skipped.")
        else:
            # Train and Evaluate
            metrics = train_and_evaluate(
                train_csv=args.train_csv,
                test_csv=args.test_csv,
                models_dir=args.output_dir
            )
            
            print(f"\n{'='*60}")
            print("  Final Results")
            print(f"{'='*60}")
            print(f"Macro F1: {metrics['macro']['f1']:.4f}")
            print(f"Micro F1: {metrics['micro']['f1']:.4f}")
            print(f"Samples:  {metrics['n_samples']}")
            print("\nModel artifacts saved to output directory.")

    except Exception as e:
        print(f"\nCRITICAL ERROR during training: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---
### `scripts/build_hard_negative_patch.py`
- Size: `3330` bytes
```
#!/usr/bin/env python3
"""
Patch a training JSONL file using audit violations, turning offending spans into "O".
"""

import argparse
import json
from typing import Any, Dict, Iterable, List, Tuple


def build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-in", default="data/ml_training/distilled_phi_CLEANED_STANDARD.jsonl")
    ap.add_argument("--audit-report", default="artifacts/phi_distilbert_ner/audit_report.json")
    ap.add_argument("--data-out", default="data/ml_training/distilled_phi_CLEANED_STANDARD.hardneg.jsonl")
    return ap


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    return build_arg_parser().parse_args(argv)


def resolve_record_id(row: Dict[str, Any], fallback: int) -> str:
    record_id = row.get("id") or row.get("id_base") or row.get("record_index") or fallback
    return str(record_id)


def load_patches(report_path: str) -> Dict[str, List[Tuple[int, int, str]]]:
    with open(report_path, "r") as f:
        report = json.load(f)
    patches: Dict[str, List[Tuple[int, int, str]]] = {}
    for ex in report.get("examples", []):
        record_id = str(ex.get("id", ""))
        if not record_id:
            continue
        token_index = int(ex.get("token_index", 0))
        span_len = int(ex.get("span_len", 1))
        kind = str(ex.get("type", "unknown"))
        patches.setdefault(record_id, []).append((token_index, span_len, kind))
    return patches


def iter_jsonl(path: str) -> Iterable[Dict[str, Any]]:
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def main() -> None:
    args = parse_args()
    patches = load_patches(args.audit_report)
    if not patches:
        raise RuntimeError(f"No examples found in audit report: {args.audit_report}")

    modified_records = 0
    modified_spans = 0
    skipped_spans = 0
    modified_by_type: Dict[str, int] = {}

    with open(args.data_out, "w") as fout:
        for idx, row in enumerate(iter_jsonl(args.data_in)):
            record_id = resolve_record_id(row, idx)
            spans = patches.get(record_id, [])
            if spans:
                tags = row.get("ner_tags") or []
                if not isinstance(tags, list):
                    tags = []
                before = list(tags)
                for token_index, span_len, kind in spans:
                    if token_index < 0 or token_index >= len(tags):
                        skipped_spans += 1
                        continue
                    end = min(len(tags), token_index + max(span_len, 1))
                    for i in range(token_index, end):
                        tags[i] = "O"
                    modified_spans += 1
                    modified_by_type[kind] = modified_by_type.get(kind, 0) + 1
                if tags != before:
                    modified_records += 1
                row["ner_tags"] = tags
            fout.write(json.dumps(row) + "\n")

    print(f"Patched records: {modified_records}")
    print(f"Patched spans: {modified_spans}")
    if skipped_spans:
        print(f"Skipped spans (out of range): {skipped_spans}")
    print(f"Patched by type: {modified_by_type}")


if __name__ == "__main__":
    main()

```

---
### `scripts/apply_immediate_logic_fixes.py`
- Size: `3766` bytes
```
#!/usr/bin/env python3
"""Immediate hotfix utilities for critical extraction issues.

Primary use: apply checkbox-negative corrections where some EMR templates encode
unchecked options as "0- Item" or "[ ] Item", which can be hallucinated as True.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _ensure_repo_on_path() -> None:
    root = _repo_root()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


def _set_field_path(record: dict[str, Any], field_path: str, value: Any) -> bool:
    """Set a dotted field path on a JSON-like dict. Returns True if changed."""
    parts = [p for p in (field_path or "").split(".") if p]
    if not parts:
        return False

    current: Any = record
    for part in parts[:-1]:
        if not isinstance(current, dict):
            return False
        if part not in current or not isinstance(current.get(part), dict):
            current[part] = {}
        current = current[part]

    if not isinstance(current, dict):
        return False
    leaf = parts[-1]
    prior = current.get(leaf)
    current[leaf] = value
    return prior != value


def apply_checkbox_correction(text: str, record: Any) -> Any:
    """Fix hallucination of '0- Item' as True.

    Supports either a raw dict (JSON) or a RegistryRecord-like object that has
    `model_dump()` / `model_validate()`.
    """
    import re as _re

    record_dict: dict[str, Any]
    if isinstance(record, dict):
        record_dict = dict(record)
    elif hasattr(record, "model_dump"):
        record_dict = dict(record.model_dump())  # type: ignore[no-any-return]
    else:
        raise TypeError("record must be a dict or a RegistryRecord-like object")

    # Pattern for "0- Item" (indicating unselected in some EMRs)
    negation_patterns: list[tuple[str, str]] = [
        (r"(?im)^\s*0\s*[—\-]\s*Tunneled Pleural Catheter\b", "pleural_procedures.ipc.performed"),
        (r"(?im)^\s*0\s*[—\-]\s*Chest\s+tube\b", "pleural_procedures.chest_tube.performed"),
        (r"(?im)^\s*0\s*[—\-]\s*Pneumothorax\b", "complications.pneumothorax.occurred"),
    ]

    changed = False
    for pattern, field_path in negation_patterns:
        if _re.search(pattern, text or "", _re.IGNORECASE):
            changed |= _set_field_path(record_dict, field_path, False)

    if not changed:
        return record

    # Best-effort: return same type when possible.
    if isinstance(record, dict):
        return record_dict

    _ensure_repo_on_path()
    try:
        from modules.registry.schema import RegistryRecord

        return RegistryRecord.model_validate(record_dict)
    except Exception:
        return record_dict


def _load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply immediate extraction logic fixes to a record JSON.")
    parser.add_argument("--note", type=Path, required=True, help="Path to raw/masked note text file")
    parser.add_argument("--record", type=Path, required=True, help="Path to RegistryRecord JSON file")
    args = parser.parse_args()

    note_text = _load_text(args.note)
    record_json = _load_json(args.record)
    updated = apply_checkbox_correction(note_text, record_json)

    out = updated if isinstance(updated, dict) else getattr(updated, "model_dump", lambda: updated)()
    print(json.dumps(out, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```

---
### `scripts/prodigy_cloud_sync.py`
- Size: `3869` bytes
```
#!/usr/bin/env python3
"""
Prodigy dataset cloud sync helper (safe for Google Drive / Dropbox / OneDrive).

Why this exists:
- Prodigy stores datasets in a local DB (often SQLite under ~/.prodigy).
- Cloud-syncing the SQLite DB file directly is risky and can corrupt the DB.
- The safe workflow is export → sync file → import.

This script wraps `prodigy db-out` and `prodigy db-in` with a convenient CLI and an
optional "reset dataset before import" mode to avoid drift/duplicates.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def _run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def export_dataset(*, dataset: str, out_file: Path, answer: str | None) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, "-m", "prodigy", "db-out", dataset]
    if answer:
        cmd += ["--answer", answer]
    # Stream stdout directly to file (avoid loading into memory).
    with out_file.open("w", encoding="utf-8") as f:
        subprocess.run(cmd, check=True, stdout=f)


def reset_dataset(*, dataset: str) -> None:
    # Use the Prodigy DB API to avoid interactive CLI prompts.
    from prodigy.components.db import connect  # type: ignore

    db = connect()
    if dataset in db.datasets:
        db.drop_dataset(dataset)


def import_dataset(
    *,
    dataset: str,
    in_file: Path,
    reset_first: bool,
    overwrite: bool,
    rehash: bool,
) -> None:
    if not in_file.exists():
        raise FileNotFoundError(str(in_file))

    if reset_first:
        reset_dataset(dataset=dataset)

    cmd = [sys.executable, "-m", "prodigy", "db-in", dataset, str(in_file)]
    if overwrite:
        cmd += ["--overwrite"]
    if rehash:
        cmd += ["--rehash"]
    _run(cmd)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    p_exp = sub.add_parser("export", help="Export a dataset to a JSONL file (cloud-safe)")
    p_exp.add_argument("--dataset", required=True, help="Prodigy dataset name (e.g. registry_v1)")
    p_exp.add_argument("--out", required=True, type=Path, help="Output JSONL file path")
    p_exp.add_argument(
        "--answer",
        choices=["accept", "reject", "ignore"],
        default=None,
        help="Optional: export only one answer type",
    )

    p_imp = sub.add_parser("import", help="Import a dataset JSONL file into the local Prodigy DB")
    p_imp.add_argument("--dataset", required=True, help="Prodigy dataset name (e.g. registry_v1)")
    p_imp.add_argument("--in", dest="in_file", required=True, type=Path, help="Input JSONL file path")
    p_imp.add_argument(
        "--reset",
        action="store_true",
        help="Drop the local dataset before importing (recommended when switching machines)",
    )
    p_imp.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing answers when importing (use with care; default: off)",
    )
    p_imp.add_argument(
        "--rehash",
        action="store_true",
        help="Recompute and overwrite hashes when importing (rarely needed; default: off)",
    )

    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.cmd == "export":
        export_dataset(dataset=args.dataset, out_file=args.out, answer=args.answer)
        return 0
    if args.cmd == "import":
        import_dataset(
            dataset=args.dataset,
            in_file=args.in_file,
            reset_first=bool(args.reset),
            overwrite=bool(args.overwrite),
            rehash=bool(args.rehash),
        )
        return 0
    raise SystemExit(f"Unknown cmd: {args.cmd}")


if __name__ == "__main__":
    raise SystemExit(main())



```

---
### `scripts/run_python_update_scripts.py`
- Size: `4064` bytes
```
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run all python scripts in data/granular annotations/Python_update_scripts/"
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop on first failing script (default: continue).",
    )
    parser.add_argument(
        "--pattern",
        default="note_*.py",
        help="Glob pattern to select scripts (default: note_*.py).",
    )
    parser.add_argument(
        "--failure-report",
        type=Path,
        default=Path("reports/python_update_scripts_failures.json"),
        help="Where to write failure report JSON (default: reports/python_update_scripts_failures.json).",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    scripts_dir = repo_root / "data" / "granular annotations" / "Python_update_scripts"

    if not scripts_dir.exists():
        raise SystemExit(f"Scripts directory not found: {scripts_dir}")

    scripts = sorted(scripts_dir.glob(args.pattern))
    if not scripts:
        print(f"No scripts matched {args.pattern!r} in {scripts_dir}")
        return 0

    print(f"Found {len(scripts)} scripts in: {scripts_dir}")
    print(f"Python: {sys.executable}")
    print("-" * 60)

    failures: list[Path] = []
    failure_details: list[dict] = []
    start_all = time.time()
    started_at = datetime.now(timezone.utc).isoformat()

    for idx, script_path in enumerate(scripts, start=1):
        rel = script_path.relative_to(repo_root)
        print(f"[{idx}/{len(scripts)}] Running {rel} ...", flush=True)

        # Run each script in repo root so relative-path scripts behave consistently.
        start_one = time.time()
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(repo_root),
            text=True,
            capture_output=True,
        )
        elapsed_one = time.time() - start_one

        # Preserve script output (but printed after the script finishes).
        if result.stdout:
            sys.stdout.write(result.stdout)
            if not result.stdout.endswith("\n"):
                sys.stdout.write("\n")
        if result.stderr:
            sys.stderr.write(result.stderr)
            if not result.stderr.endswith("\n"):
                sys.stderr.write("\n")

        if result.returncode != 0:
            failures.append(script_path)
            failure_details.append(
                {
                    "script": str(rel),
                    "returncode": int(result.returncode),
                    "elapsed_seconds": round(elapsed_one, 6),
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                }
            )
            print(f"  -> FAILED (exit {result.returncode})")
            if args.fail_fast:
                break

    elapsed = time.time() - start_all
    print("-" * 60)
    print(f"Done in {elapsed:.2f}s")
    print(f"Failed: {len(failures)}")
    if failures:
        for p in failures:
            print(f" - {p.relative_to(repo_root)}")

        # Write a structured failure report for debugging.
        report_path = args.failure_report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "started_at": started_at,
            "elapsed_seconds": round(elapsed, 6),
            "python": sys.executable,
            "scripts_dir": str(scripts_dir.relative_to(repo_root)),
            "pattern": args.pattern,
            "total_scripts": len(scripts),
            "failed_scripts": len(failure_details),
            "failures": failure_details,
        }
        report_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"Failure report written to: {report_path}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


```

---
### `scripts/generate_addon_templates.py`
- Size: `4248` bytes
```
#!/usr/bin/env python3
"""Generate Jinja addon template files from ip_addon_templates_parsed.json.

This script reads the parsed addon templates JSON and generates individual
Jinja template files in the templates/addons/ directory.

Each generated file contains:
- A comment header with title, category, and CPT codes
- A render() macro that returns the template body
"""

import json
import re
from pathlib import Path


def sanitize_filename(slug: str) -> str:
    """Ensure slug is valid as a filename."""
    # Remove any characters that aren't alphanumeric, underscore, or hyphen
    return re.sub(r"[^a-zA-Z0-9_-]", "_", slug)


def escape_jinja_chars(text: str) -> str:
    """Escape any Jinja-like syntax in the body text.

    Since we're putting raw text into a Jinja template, we need to ensure
    any {{ or {% sequences don't get interpreted as Jinja.
    """
    # Replace any accidental Jinja-like syntax
    text = text.replace("{{", "{ {")
    text = text.replace("}}", "} }")
    text = text.replace("{%", "{ %")
    text = text.replace("%}", "% }")
    return text


def generate_template_file(template: dict, output_dir: Path) -> Path:
    """Generate a single Jinja template file for an addon.

    Args:
        template: Dict with slug, title, category, cpt_codes, body
        output_dir: Directory to write the template file to

    Returns:
        Path to the generated file
    """
    slug = template.get("slug", "")
    title = template.get("title", "")
    category = template.get("category", "")
    cpt_codes = template.get("cpt_codes", [])
    body = template.get("body", "")

    if not slug:
        raise ValueError("Template missing slug")

    filename = f"{sanitize_filename(slug)}.jinja"
    filepath = output_dir / filename

    # Format CPT codes for comment
    cpt_str = ", ".join(str(c) for c in cpt_codes) if cpt_codes else "None"

    # Escape the body text
    escaped_body = escape_jinja_chars(body)

    # Generate the Jinja template content using {# #} for Jinja2 comments
    content = f'''{{#
  file: templates/addons/{filename}
  Title: {title}
  Category: {category}
  CPT: {cpt_str}
#}}
{{% macro render(ctx=None) -%}}
{escaped_body}
{{%- endmacro %}}
'''

    filepath.write_text(content, encoding="utf-8")
    return filepath


def main():
    """Main entry point."""
    # Paths
    project_root = Path(__file__).resolve().parents[1]
    json_path = project_root / "data" / "knowledge" / "ip_addon_templates_parsed.json"
    output_dir = project_root / "proc_report" / "templates" / "addons"

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load the JSON
    print(f"Loading templates from: {json_path}")
    if not json_path.exists():
        print(f"ERROR: JSON file not found at {json_path}")
        return 1

    data = json.loads(json_path.read_text(encoding="utf-8"))
    templates = data.get("templates", [])

    print(f"Found {len(templates)} templates")

    # Generate template files
    generated = []
    errors = []

    for template in templates:
        try:
            filepath = generate_template_file(template, output_dir)
            generated.append(filepath.name)
            print(f"  Generated: {filepath.name}")
        except Exception as e:
            slug = template.get("slug", "unknown")
            errors.append(f"{slug}: {e}")
            print(f"  ERROR generating {slug}: {e}")

    # Summary
    print(f"\nGenerated {len(generated)} template files in {output_dir}")
    if errors:
        print(f"Errors: {len(errors)}")
        for err in errors:
            print(f"  - {err}")
        return 1

    # Create an __init__.py in the addons directory for easy importing
    init_path = output_dir / "__init__.py"
    init_content = '''"""Auto-generated addon templates.

These Jinja templates were generated from ip_addon_templates_parsed.json.
Each template provides a render(ctx=None) macro for inclusion in procedure reports.
"""

# This file intentionally left mostly empty.
# Templates are loaded via the Jinja environment, not Python imports.
'''
    init_path.write_text(init_content, encoding="utf-8")
    print(f"Created {init_path}")

    return 0


if __name__ == "__main__":
    exit(main())

```

---
### `scripts/training.py`
- Size: `4293` bytes
```
#!/usr/bin/env python3
"""
Generate an unlabeled JSONL file for Registry Prodigy annotation from an existing
registry training CSV.

This is a convenience helper for the Registry "Diamond Loop":
- Start with `data/ml_training/registry_train.csv` (or train/val/test)
- Filter to "weak" classes to create a high-yield annotation pool
- Emit JSONL where each line has `note_text` (or `text`) for Prodigy prep.

Next step (model-assisted / pre-annotated Prodigy tasks):
- Convert the unlabeled notes JSONL into a Prodigy-ready batch with prefilled
  labels from the *current* registry model (ONNX bundle when available, sklearn
  fallback otherwise):

  make registry-prodigy-prepare \
    REG_PRODIGY_INPUT_FILE=data/ml_training/registry_unlabeled_notes.jsonl \
    REG_PRODIGY_COUNT=200

Typical usage:

  python scripts/training.py \
    --csv data/ml_training/registry_train.csv \
    --out data/ml_training/registry_unlabeled_notes.jsonl \
    --weak-classes bronchial_wash therapeutic_aspiration rigid_bronchoscopy peripheral_ablation \
    --limit 500
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import pandas as pd


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--csv",
        type=Path,
        default=Path("data/ml_training/registry_train.csv"),
        help="Input training CSV containing note_text and label columns",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("data/ml_training/registry_unlabeled_notes.jsonl"),
        help="Output JSONL file for Prodigy batch prep",
    )
    p.add_argument(
        "--text-key",
        choices=["note_text", "text"],
        default="note_text",
        help="Key to write in JSONL (Prodigy prep accepts note_text or text)",
    )
    p.add_argument(
        "--weak-classes",
        nargs="*",
        default=[
            "bronchial_wash",
            "therapeutic_aspiration",
            "rigid_bronchoscopy",
            "peripheral_ablation",
        ],
        help="If provided, select rows where any of these labels are positive",
    )
    p.add_argument(
        "--min-positives",
        type=int,
        default=1,
        help="Minimum number of positive weak classes required for selection (default: 1)",
    )
    p.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Max number of notes to write (0 = no limit)",
    )
    p.add_argument("--seed", type=int, default=42, help="Random seed for sampling/shuffle")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.csv.exists():
        raise SystemExit(f"CSV not found: {args.csv}")

    df = pd.read_csv(args.csv)
    if "note_text" not in df.columns:
        raise SystemExit(f"CSV missing required column 'note_text': {args.csv}")

    weak = [c for c in (args.weak_classes or []) if c]
    if weak:
        missing = [c for c in weak if c not in df.columns]
        if missing:
            raise SystemExit(f"CSV missing weak class columns: {missing}")
        positives = df[weak].fillna(0).astype(int).sum(axis=1)
        target_df = df[positives >= int(args.min_positives)].copy()
    else:
        target_df = df.copy()

    # Shuffle to avoid ordering artifacts.
    rng = random.Random(int(args.seed))
    indices = list(target_df.index)
    rng.shuffle(indices)
    target_df = target_df.loc[indices]

    if args.limit and int(args.limit) > 0:
        target_df = target_df.head(int(args.limit))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    n_written = 0
    with args.out.open("w", encoding="utf-8") as f:
        for text in target_df["note_text"].fillna("").astype(str):
            text = text.strip()
            if not text:
                continue
            f.write(json.dumps({args.text_key: text}, ensure_ascii=False) + "\n")
            n_written += 1

    if weak:
        print(f"Wrote {n_written} notes targeting weak classes: {weak}")
    else:
        print(f"Wrote {n_written} notes (no weak-class filter)")
    print(f"Output: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```

---
### `scripts/warm_models.py`
- Size: `4371` bytes
```
#!/usr/bin/env python3
"""Warm up NLP models before starting the FastAPI server.

This script pre-loads heavy NLP models (spaCy, scispaCy, medspaCy) to ensure
they are ready before the first HTTP request. This is critical for Railway
deployments where cold-start latency can cause timeouts.

Usage:
    python scripts/warm_models.py

Environment Variables:
    PROCSUITE_SPACY_MODEL - spaCy model to use (default: en_core_sci_sm)
    ENABLE_UMLS_LINKER - Set to "false" to skip UMLS linker (saves ~1GB memory)

Exit codes:
    0 - All models loaded successfully
    1 - One or more models failed to load
"""

from __future__ import annotations

import logging
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> int:
    """Load and warm up all heavy NLP models."""
    model_name = os.getenv("PROCSUITE_SPACY_MODEL", "en_core_sci_sm")
    errors: list[str] = []

    # 1. Load spaCy model
    logger.info("Loading spaCy model: %s", model_name)
    try:
        import spacy

        nlp = spacy.load(model_name)
        # Warm up the pipeline with a test document
        doc = nlp("Patient underwent bronchoscopy for evaluation of lung nodule.")
        logger.info(
            "spaCy model loaded successfully (%d entities, %d tokens)",
            len(doc.ents),
            len(doc),
        )
    except ImportError:
        errors.append("spaCy not installed")
        logger.warning("spaCy not installed - skipping")
    except OSError as exc:
        errors.append(f"spaCy model '{model_name}' not found: {exc}")
        logger.error("spaCy model '%s' not found: %s", model_name, exc)

    # 2. Load medspaCy sectionizer
    logger.info("Initializing medspaCy sectionizer...")
    try:
        from modules.common.sectionizer import SectionizerService

        sectionizer = SectionizerService()
        # Test sectionization
        sections = sectionizer.sectionize(
            "INDICATION: Lung nodule\n\nPROCEDURE: Bronchoscopy\n\nFINDINGS: Normal airways"
        )
        logger.info("medspaCy sectionizer initialized (%d sections)", len(sections))
    except ImportError as exc:
        errors.append(f"medspaCy not installed: {exc}")
        logger.warning("medspaCy not available: %s", exc)
    except Exception as exc:
        errors.append(f"Sectionizer initialization failed: {exc}")
        logger.error("Sectionizer initialization failed: %s", exc)

    # 3. Load UMLS linker (if available and enabled)
    enable_umls = os.getenv("ENABLE_UMLS_LINKER", "true").lower() in ("true", "1", "yes")
    if enable_umls:
        logger.info("Initializing UMLS linker...")
        try:
            from proc_nlp.umls_linker import _load_model, umls_link

            _load_model(model_name)
            # Test UMLS linking with a simple term
            concepts = umls_link("bronchoscopy")
            logger.info("UMLS linker initialized (%d concepts found)", len(concepts))
        except ImportError as exc:
            logger.warning("UMLS linker not available: %s", exc)
        except RuntimeError as exc:
            logger.warning("UMLS linker not available: %s", exc)
        except Exception as exc:
            # UMLS linker is optional, so we just warn
            logger.warning("UMLS linker initialization skipped: %s", exc)
    else:
        logger.info("UMLS linker skipped (ENABLE_UMLS_LINKER=false)")

    # 4. Import FastAPI app to trigger any module-level initialization
    logger.info("Importing FastAPI app...")
    try:
        from modules.api.fastapi_app import app

        logger.info("FastAPI app imported successfully (version: %s)", app.version)
    except ImportError as exc:
        errors.append(f"FastAPI app import failed: {exc}")
        logger.error("FastAPI app import failed: %s", exc)
    except Exception as exc:
        errors.append(f"FastAPI app initialization failed: {exc}")
        logger.error("FastAPI app initialization failed: %s", exc)

    # Summary
    if errors:
        logger.error("Model warmup completed with %d error(s):", len(errors))
        for err in errors:
            logger.error("  - %s", err)
        return 1

    logger.info("All models warmed up successfully!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```

---
### `scripts/build_phi_allowlist_trie.py`
- Size: `4406` bytes
```
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Iterable
from urllib.error import URLError
from urllib.request import urlopen


def _read_terms_file(path: Path) -> list[str]:
    if not path.exists():
        return []
    terms: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        terms.append(line)
    return terms


def _try_fetch_openfda_terms(limit: int, timeout_s: float) -> list[str]:
    # Best-effort: keep small and safe. OpenFDA supports aggregation counts.
    url = (
        "https://api.fda.gov/device/510k.json?"
        "count=device_name.exact&limit="
        + str(limit)
    )
    try:
        with urlopen(url, timeout=timeout_s) as resp:  # noqa: S310 - explicit small fetch
            payload = json.loads(resp.read().decode("utf-8"))
    except (URLError, TimeoutError, json.JSONDecodeError):
        return []

    out: list[str] = []
    for row in payload.get("results", []) or []:
        term = str(row.get("term", "")).strip()
        if term:
            out.append(term)
    return out


_SPACE_RE = re.compile(r"\s+")
_TRIM_RE = re.compile(r"^[\W_]+|[\W_]+$")


def _normalize_term(term: str) -> str | None:
    t = term.strip().lower()
    if not t:
        return None
    t = _SPACE_RE.sub(" ", t)
    t = _TRIM_RE.sub("", t)
    if len(t) < 2:
        return None
    return t


def _build_trie(terms: Iterable[str]) -> dict:
    root: dict = {}
    for term in terms:
        node = root
        for ch in term:
            node = node.setdefault(ch, {})
        node["$"] = 1
    return root


def main(argv: list[str]) -> int:
    repo_root = Path(__file__).resolve().parents[1]

    parser = argparse.ArgumentParser(
        description="Build a compact allowlist trie JSON for the client-side PHI redactor."
    )
    parser.add_argument(
        "--terms-file",
        default=str(repo_root / "data" / "allowlist_terms.txt"),
        help="Primary repo-local allowlist terms file (one term per line).",
    )
    parser.add_argument(
        "--private-umls-file",
        default=str(repo_root / "data" / "private" / "umls_abbreviations.txt"),
        help="Optional local-only file (NOT committed).",
    )
    parser.add_argument(
        "--out",
        default=str(
            repo_root
            / "modules"
            / "api"
            / "static"
            / "phi_redactor"
            / "allowlist_trie.json"
        ),
        help="Output path for allowlist_trie.json.",
    )
    parser.add_argument(
        "--max-term-len",
        type=int,
        default=48,
        help="Maximum term length to include (trims overly long entries).",
    )
    parser.add_argument(
        "--openfda",
        action="store_true",
        help="Best-effort: fetch a small set of OpenFDA device terms.",
    )
    parser.add_argument(
        "--openfda-limit",
        type=int,
        default=500,
        help="Max number of OpenFDA device terms to include (if --openfda).",
    )
    args = parser.parse_args(argv)

    terms_file = Path(args.terms_file)
    private_umls_file = Path(args.private_umls_file)
    out_path = Path(args.out)
    max_len = int(args.max_term_len)

    raw_terms: list[str] = []
    raw_terms.extend(_read_terms_file(terms_file))
    raw_terms.extend(_read_terms_file(private_umls_file))

    if args.openfda and os.getenv("PROCSUITE_SKIP_NETWORK", "0") not in ("1", "true", "yes"):
        raw_terms.extend(_try_fetch_openfda_terms(args.openfda_limit, timeout_s=5.0))

    normalized: list[str] = []
    seen: set[str] = set()
    for t in raw_terms:
        nt = _normalize_term(t)
        if not nt:
            continue
        if len(nt) > max_len:
            continue
        if nt in seen:
            continue
        seen.add(nt)
        normalized.append(nt)

    normalized.sort()

    trie = _build_trie(normalized)
    payload = {"v": 1, "max_term_len": max_len, "count": len(normalized), "trie": trie}

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")

    print(f"Wrote {out_path} ({len(normalized)} terms)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))


```

---
### `scripts/run_coder_hybrid.py`
- Size: `4520` bytes
```
#!/usr/bin/env python3
"""
Run the full coding pipeline (rules + LLM advisor + smart_hybrid merge)
over a JSONL notes file and emit CodeSuggestion[] per note.

Usage:
    python scripts/run_coder_hybrid.py \
        --notes data/synthetic/synthetic_notes_with_registry.jsonl \
        --kb data/knowledge/ip_coding_billing_v3_0.json \
        --keyword-dir data/keyword_mappings \
        --model-version gemini-1.5-pro-002 \
        --out-json outputs/coder_suggestions.jsonl
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Iterator, Dict, Any

from config.settings import CoderSettings
from modules.coder.adapters.persistence.csv_kb_adapter import CsvKnowledgeBaseAdapter
from modules.coder.adapters.nlp.keyword_mapping_loader import YamlKeywordMappingRepository
from modules.coder.adapters.nlp.simple_negation_detector import SimpleNegationDetector
from modules.coder.adapters.llm.gemini_advisor import GeminiAdvisorAdapter  # per update-recs doc
from modules.domain.coding_rules.rule_engine import RuleEngine
from modules.coder.application.coding_service import CodingService


def iter_notes(jsonl_path: Path) -> Iterator[Dict[str, Any]]:
    with jsonl_path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:  # noqa: TRY003
                print(f"Skipping bad JSON line: {exc}", file=sys.stderr)


def main() -> int:
    ap = argparse.ArgumentParser(description="Run smart-hybrid coder over notes.")
    ap.add_argument("--notes", required=True, help="JSONL file with notes.")
    ap.add_argument("--kb", default="data/knowledge/ip_coding_billing_v3_0.json")
    ap.add_argument(
        "--keyword-dir",
        default="data/keyword_mappings",
        help="Directory of YAML keyword mapping files.",
    )
    ap.add_argument(
        "--model-version",
        default="gemini-1.5-pro-002",
        help="LLM model identifier for provenance.",
    )
    ap.add_argument(
        "--out-json",
        required=True,
        help="Output JSONL; one line per note with CodeSuggestion[] dump.",
    )
    args = ap.parse_args()

    notes_path = Path(args.notes)
    kb_path = Path(args.kb)
    keyword_dir = Path(args.keyword_dir)
    out_path = Path(args.out_json)

    if not notes_path.is_file():
        print(f"ERROR: notes file not found at {notes_path}", file=sys.stderr)
        return 1

    settings = CoderSettings(
        model_version=args.model_version,
        kb_path=str(kb_path),
        kb_version=kb_path.name,
        keyword_mapping_dir=str(keyword_dir),
        keyword_mapping_version="v1",
    )

    # Infra adapters
    kb_repo = CsvKnowledgeBaseAdapter(settings.kb_path)
    keyword_repo = YamlKeywordMappingRepository(settings.keyword_mapping_dir)
    negation_detector = SimpleNegationDetector()

    # Rule engine + LLM advisor
    rule_engine = RuleEngine(kb_repo=kb_repo)
    llm_advisor = GeminiAdvisorAdapter(
        model_name=settings.model_version,
        allowed_codes=list(kb_repo.get_all_codes()),
    )

    coding_service = CodingService(
        kb_repo=kb_repo,
        keyword_repo=keyword_repo,
        negation_detector=negation_detector,
        rule_engine=rule_engine,
        llm_advisor=llm_advisor,
        config=settings,
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w") as out_f:
        for note in iter_notes(notes_path):
            procedure_id = str(note.get("procedure_id") or note.get("id"))
            report_text = note.get("report_text") or note.get("note_text")
            if not (procedure_id and report_text):
                print(f"Skipping note with missing fields: {note}", file=sys.stderr)
                continue

            suggestions = coding_service.generate_suggestions(
                procedure_id=procedure_id,
                report_text=report_text,
            )

            out_record = {
                "procedure_id": procedure_id,
                "suggestions": [s.model_dump(mode="json") for s in suggestions],
            }
            out_f.write(json.dumps(out_record, default=str) + "\n")

    print(f"Coder run complete. Wrote suggestions to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```

---
### `scripts/refine_ner_labels.py`
- Size: `4649` bytes
```
import json
import shutil
from collections import Counter
from pathlib import Path

# --- CONFIGURATION ---

# 1. MERGE MAP: { "OLD_LABEL": "NEW_TARGET_LABEL" }
MERGE_MAP = {
    # Fix Schema Inconsistencies (Rare -> Common)
    "PROC_MEDICATION": "MEDICATION",        # 3 -> 954
    "MEAS_VOLUME": "MEAS_VOL",              # 4 -> 1055
    "DEV_DEVICE": "DEV_INSTRUMENT",         # 4 -> 6298
    
    # Semantic Merges (Specific -> General)
    "PROC_NAME": "PROC_ACTION",             # 3 -> 7411
    "LMB": "ANAT_AIRWAY",                   # 39 -> 6524
    "ANAT_INTERCOSTAL_SPACE": "ANAT_PLEURA",# 4 -> 1429
    "OBS_FLUID_COLOR": "OBS_FINDING",       # 4 -> 3045
    "OBS_NO_COMPLICATION": "OBS_FINDING",   # 1 -> 3045
    
    # NEW SUGGESTION based on updated stats (Optional but recommended)
    # "MEAS_AIRWAY_DIAM": "MEAS_SIZE",      # 36 -> 2364 (Borderline count)
    # "MEAS_TEMP": "OBS_FINDING",           # 48 -> 3045 (Borderline count)
}

# 2. PRUNE LIST: [ "LABEL_TO_REMOVE" ]
#    These labels will be converted to 'O' (Outside).
PRUNE_LIST = [
    "CTX_INDICATION",   # Count: 2 (Too low to learn)
    "DISPOSITION",      # Count: 2 (Too low to learn)
    
    # Note: CTX_HISTORICAL (192) and CTX_TIME (165) are now robust enough 
    # to keep! They are commented out below so they WON'T be pruned.
    # "CTX_HISTORICAL", 
    # "CTX_TIME",       
]

# --- SCRIPT LOGIC ---

def process_label(bio_tag):
    """Refines a single BIO tag (e.g., 'B-PROC_NAME') based on rules."""
    if bio_tag == "O":
        return "O"
        
    # Handle potentially malformed tags (just in case)
    if "-" not in bio_tag:
        return "O"

    prefix, label = bio_tag.split("-", 1)
    
    # Check Prune List
    if label in PRUNE_LIST:
        return "O"
        
    # Check Merge Map
    if label in MERGE_MAP:
        new_label = MERGE_MAP[label]
        return f"{prefix}-{new_label}"
        
    return bio_tag

def refine_dataset(input_path, output_path):
    print(f"Reading from: {input_path}")
    print(f"Writing to:   {output_path}")
    
    input_path = Path(input_path)
    output_path = Path(output_path)
    
    counts = Counter()
    modified_counts = Counter()
    
    with open(input_path, "r", encoding="utf-8") as fin, \
         open(output_path, "w", encoding="utf-8") as fout:
        
        for line_num, line in enumerate(fin):
            try:
                data = json.loads(line)
                original_tags = data.get("ner_tags", [])
                
                new_tags = []
                for tag in original_tags:
                    new_tag = process_label(tag)
                    new_tags.append(new_tag)
                    
                    # Track stats
                    if tag != "O":
                        # Handle cases where tag might be malformed
                        parts = tag.split("-", 1)
                        base_label = parts[1] if len(parts) > 1 else tag
                        counts[base_label] += 1
                        
                        if new_tag != "O":
                            new_parts = new_tag.split("-", 1)
                            new_base_label = new_parts[1] if len(new_parts) > 1 else new_tag
                            
                            if base_label != new_base_label:
                                modified_counts[f"Merged {base_label} -> {new_base_label}"] += 1
                        else:
                            modified_counts[f"Pruned {base_label}"] += 1

                data["ner_tags"] = new_tags
                fout.write(json.dumps(data) + "\n")
                
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON line {line_num}")

    print("\n--- Modification Stats ---")
    if not modified_counts:
        print("No labels were modified.")
    for action, count in modified_counts.most_common():
        print(f"{action}: {count} occurrences")
        
    print(f"\nSuccess! New dataset saved to {output_path}")

if __name__ == "__main__":
    # Point this to your uploaded file
    INPUT_FILE = "ner_bio_format.jsonl" 
    OUTPUT_FILE = "ner_bio_format_refined.jsonl"
    
    if Path(INPUT_FILE).exists():
        refine_dataset(INPUT_FILE, OUTPUT_FILE)
    else:
        # Fallback for folder structures
        INPUT_FILE = "data/ml_training/granular_ner/ner_bio_format.jsonl"
        OUTPUT_FILE = "data/ml_training/granular_ner/ner_bio_format_refined.jsonl"
        
        if Path(INPUT_FILE).exists():
            refine_dataset(INPUT_FILE, OUTPUT_FILE)
        else:
            print(f"Error: Could not find input file at {INPUT_FILE}")
```

---
### `scripts/fix_registry_hallucinations.py`
- Size: `5160` bytes
```
#!/usr/bin/env python3
"""Clean hallucinated or malformed institution fields in scrubbed golden JSONs.

Reads `.json` and `.jsonl` files from the scrubbed directory, fixes bad
`registry_entry.institution_name` values, and writes cleaned output to
`data/knowledge/golden_extractions_final/`.

Rules:
- If `institution_name` contains anatomical terms (e.g., bronchus/lobe/carina/distal),
  replace with "Unknown Institution".
- Remove date fragments mistakenly embedded in institution fields (e.g., "Date: 11/10/2025").
"""

from __future__ import annotations

import argparse
import json
import logging
import re
from pathlib import Path
from typing import Any, Iterable

logger = logging.getLogger(__name__)

ANATOMICAL_TERMS = ("bronchus", "lobe", "carina", "distal")

DATE_FRAGMENT_RE = re.compile(
    r"(?i)\bdate(?:\s+of\s+procedure)?\s*[:\-]\s*"
    r"(?:\[[^\]]+\]|<[^>]+>|\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})"
)
SEPARATOR_RE = re.compile(r"\s*\|\|\s*|\s*\|\s*")
PREFIX_RE = re.compile(r"(?i)\b(?:location|facility|hospital|institution|site|center)\s*[:\-]\s*")


def iter_input_files(input_dir: Path) -> Iterable[Path]:
    yield from sorted([*input_dir.glob("*.json"), *input_dir.glob("*.jsonl")])


def clean_institution_name(value: str) -> str:
    s = (value or "").strip()
    if not s:
        return "Unknown Institution"

    # Remove embedded date fragments
    s = DATE_FRAGMENT_RE.sub("", s)

    # Remove common separators used in evidence-like strings
    s = SEPARATOR_RE.sub(" ", s)

    # Strip common prefixes
    s = PREFIX_RE.sub("", s)

    s = " ".join(s.split()).strip(" -|")
    if not s:
        return "Unknown Institution"

    lowered = s.lower()
    if any(term in lowered for term in ANATOMICAL_TERMS):
        return "Unknown Institution"

    return s


def process_record(record: dict[str, Any]) -> bool:
    registry_entry = record.get("registry_entry")
    if not isinstance(registry_entry, dict):
        return False
    inst = registry_entry.get("institution_name")
    if not isinstance(inst, str):
        return False

    cleaned = clean_institution_name(inst)
    if cleaned == inst:
        return False
    registry_entry["institution_name"] = cleaned
    return True


def process_json_file(input_path: Path, output_path: Path) -> dict[str, int]:
    records = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        return {"records": 0, "changed": 0}

    changed = 0
    for rec in records:
        if isinstance(rec, dict) and process_record(rec):
            changed += 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"records": len(records), "changed": changed}


def process_jsonl_file(input_path: Path, output_path: Path) -> dict[str, int]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    changed = 0
    records = 0
    with input_path.open("r", encoding="utf-8") as in_f, output_path.open("w", encoding="utf-8") as out_f:
        for line in in_f:
            if not line.strip():
                continue
            records += 1
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                out_f.write(line)
                continue
            if isinstance(rec, dict) and process_record(rec):
                changed += 1
            out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return {"records": records, "changed": changed}


def main() -> int:
    parser = argparse.ArgumentParser(description="Fix hallucinated institution_name values in scrubbed golden JSONs")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("data/knowledge/golden_extractions_scrubbed"),
        help="Directory containing scrubbed golden JSON/JSONL files",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/knowledge/golden_extractions_final"),
        help="Directory to write cleaned output files",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if not args.input_dir.exists():
        logger.error("Input directory not found: %s", args.input_dir)
        return 1

    files = list(iter_input_files(args.input_dir))
    if not files:
        logger.warning("No .json/.jsonl files found in %s", args.input_dir)
        return 0

    total_records = 0
    total_changed = 0
    for path in files:
        out_path = args.output_dir / path.name
        if path.suffix == ".jsonl":
            stats = process_jsonl_file(path, out_path)
        else:
            stats = process_json_file(path, out_path)
        total_records += stats["records"]
        total_changed += stats["changed"]

    logger.info("Files processed: %s", len(files))
    logger.info("Records processed: %s", total_records)
    logger.info("Records changed: %s", total_changed)
    logger.info("Output directory: %s", args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


```

---
### `scripts/force_merge_human_labels.py`
- Size: `5248` bytes
```
import pandas as pd
import argparse
import logging
from pathlib import Path
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from modules.ml_coder.registry_label_schema import REGISTRY_LABELS  # noqa: E402
from modules.ml_coder.registry_label_constraints import apply_label_constraints  # noqa: E402


_CONSTRAINT_LABELS = [
    "bal",
    "bronchial_wash",
    "transbronchial_cryobiopsy",
    "transbronchial_biopsy",
    "rigid_bronchoscopy",
    "tumor_debulking_non_thermal",
]


def force_merge(human_csv_path: str, target_dir: str):
    human_path = Path(human_csv_path)
    if not human_path.exists():
        logger.error(f"Human CSV not found: {human_path}")
        return

    logger.info(f"Loading human labels from {human_path}...")
    human_df = pd.read_csv(human_path)
    
    # Ensure encounter_id exists
    if "encounter_id" not in human_df.columns:
        logger.error("Human CSV missing 'encounter_id' column. Cannot merge.")
        return

    human_df["encounter_id"] = human_df["encounter_id"].astype(str).str.strip()

    # Clean human df: set index to encounter_id
    human_df = human_df.set_index("encounter_id")
    
    # Identify label columns (canonical only; avoid accidentally treating meta cols as labels)
    label_cols = [c for c in REGISTRY_LABELS if c in human_df.columns]
    
    # Filter human_df to just labels to avoid overwriting text/metadata accidentally
    human_labels = human_df[label_cols]
    
    total_updates = 0
    
    # Process each split
    for split_name in ["train", "val", "test"]:
        split_path = Path(target_dir) / f"registry_{split_name}.csv"
        if not split_path.exists():
            logger.warning(f"Skipping {split_name} (not found at {split_path})")
            continue
            
        logger.info(f"Processing {split_name} split...")
        split_df = pd.read_csv(split_path)
        
        if "encounter_id" not in split_df.columns:
            logger.warning(f"Split {split_name} missing 'encounter_id'. Skipping.")
            continue

        split_df["encounter_id"] = split_df["encounter_id"].astype(str).str.strip()
            
        # Set index for alignment
        split_df = split_df.set_index("encounter_id")
        
        # Find intersection of IDs
        common_ids = split_df.index.intersection(human_labels.index)
        
        if common_ids.empty:
            logger.info(f"  No overlapping IDs in {split_name}.")
        else:
            # Only update columns that exist in this split CSV.
            # (Prep may omit rare labels; force-merge shouldn't crash.)
            split_label_cols = [c for c in label_cols if c in split_df.columns]
            missing_cols = [c for c in label_cols if c not in split_df.columns]
            if missing_cols:
                logger.info(
                    f"  Note: {len(missing_cols)} label columns not present in {split_name} split; "
                    f"skipping those (e.g. {missing_cols[:5]})."
                )

            if not split_label_cols:
                logger.warning(f"  No canonical label columns found in {split_name} split to update.")
            else:
                # FORCE UPDATE: Overwrite split values with human values where IDs match
                split_df.update(human_labels[split_label_cols])

                # Re-apply deterministic constraints on updated rows to avoid
                # reintroducing known contradictions (e.g., debulking without rigid).
                constraint_cols = [c for c in _CONSTRAINT_LABELS if c in split_df.columns]
                if constraint_cols:
                    for eid in common_ids.tolist():
                        row = split_df.loc[eid]
                        note_text = str(row.get("note_text") or "")
                        labels = {c: int(row.get(c, 0)) for c in constraint_cols}
                        apply_label_constraints(labels, note_text=note_text, inplace=True)
                        for c, v in labels.items():
                            split_df.at[eid, c] = int(v)
            
            # Count how many cells actually changed (optional debug)
            # Just logging row count is enough for now
            logger.info(f"  Overwrote labels for {len(common_ids)} rows in {split_name}.")
            total_updates += len(common_ids)
            
        # Reset index and save
        split_df = split_df.reset_index()
        split_df.to_csv(split_path, index=False)
        logger.info(f"  Saved updated {split_name} CSV.")

    logger.info(f"✅ Force merge complete. Total encounter updates: {total_updates}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Force overwrite training labels with human verified data.")
    parser.add_argument("--human-csv", required=True, help="Path to master human labels CSV")
    parser.add_argument("--target-dir", default="data/ml_training", help="Directory containing registry_{train,val,test}.csv")
    args = parser.parse_args()
    
    force_merge(args.human_csv, args.target_dir)

```

---
### `scripts/split_phi_gold.py`
- Size: `5264` bytes
```
#!/usr/bin/env python3
"""
Split Gold Standard PHI data into train/test sets with proper encounter grouping.

CRITICAL: Groups by id_base (note-level) before splitting to prevent data leakage.
If Note A has Window 1 and Window 2, both go to the same split.

Usage:
    python scripts/split_phi_gold.py \
        --input data/ml_training/phi_gold_standard_v1.jsonl \
        --train-out data/ml_training/phi_train_gold.jsonl \
        --test-out data/ml_training/phi_test_gold.jsonl \
        --seed 42
"""

from __future__ import annotations

import argparse
import json
import logging
import random
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Default paths
DEFAULT_INPUT = Path("data/ml_training/phi_gold_standard_v1.jsonl")
DEFAULT_TRAIN = Path("data/ml_training/phi_train_gold.jsonl")
DEFAULT_TEST = Path("data/ml_training/phi_test_gold.jsonl")
DEFAULT_SPLIT = 0.8
DEFAULT_SEED = 42


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Input gold JSONL file")
    parser.add_argument("--train-out", type=Path, default=DEFAULT_TRAIN, help="Output train JSONL file")
    parser.add_argument("--test-out", type=Path, default=DEFAULT_TEST, help="Output test JSONL file")
    parser.add_argument("--split", type=float, default=DEFAULT_SPLIT, help="Train split ratio (default: 0.8)")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="Random seed for reproducibility")
    return parser.parse_args(argv)


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    """Load records from JSONL file."""
    records = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def save_jsonl(records: List[Dict[str, Any]], path: Path) -> None:
    """Save records to JSONL file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")


def split_by_note(
    records: List[Dict[str, Any]],
    train_ratio: float,
    seed: int,
) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Split records by note (id_base) to prevent data leakage.

    All windows from the same note stay together in the same split.
    """
    # Group records by id_base (note-level grouping)
    groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for record in records:
        id_base = record.get("id_base", record.get("id", "unknown"))
        groups[id_base].append(record)

    logger.info(f"Found {len(groups)} unique notes from {len(records)} windows")

    # Shuffle group keys (note IDs)
    group_keys = list(groups.keys())
    random.seed(seed)
    random.shuffle(group_keys)

    # Split at the specified ratio
    split_idx = int(len(group_keys) * train_ratio)
    train_keys = group_keys[:split_idx]
    test_keys = group_keys[split_idx:]

    # Flatten back to records
    train_records = [r for k in train_keys for r in groups[k]]
    test_records = [r for k in test_keys for r in groups[k]]

    return train_records, test_records


def count_labels(records: List[Dict[str, Any]]) -> Dict[str, int]:
    """Count label distribution in records."""
    label_counts: Dict[str, int] = {}
    for rec in records:
        for tag in rec.get("ner_tags", []):
            if tag != "O":
                label_counts[tag] = label_counts.get(tag, 0) + 1
    return label_counts


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv)

    # Load input data
    if not args.input.exists():
        logger.error(f"Input file not found: {args.input}")
        return 1

    records = load_jsonl(args.input)
    logger.info(f"Loaded {len(records)} records from {args.input}")

    if not records:
        logger.error("No records to split")
        return 1

    # Split by note (encounter-level grouping)
    train_records, test_records = split_by_note(records, args.split, args.seed)

    # Log split statistics
    train_notes = len(set(r.get("id_base", "") for r in train_records))
    test_notes = len(set(r.get("id_base", "") for r in test_records))

    logger.info(f"Train: {len(train_records)} windows from {train_notes} notes")
    logger.info(f"Test:  {len(test_records)} windows from {test_notes} notes")
    logger.info(f"Split ratio: {train_notes}/{train_notes + test_notes} = {train_notes / (train_notes + test_notes):.2%}")

    # Log label distributions
    train_labels = count_labels(train_records)
    test_labels = count_labels(test_records)
    logger.info(f"Train labels: {train_labels}")
    logger.info(f"Test labels:  {test_labels}")

    # Save outputs
    save_jsonl(train_records, args.train_out)
    save_jsonl(test_records, args.test_out)

    logger.info(f"Wrote train set to {args.train_out}")
    logger.info(f"Wrote test set to {args.test_out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

```

---
### `scripts/validate_ner_alignment.py`
- Size: `5339` bytes
```
import json
from pathlib import Path
import sys

def _resolve_target_path(arg: str | None) -> Path:
    """
    If arg is None, default to our NER training data location:
      data/ml_training/granular_ner/ner_dataset_all.jsonl

    If arg is provided:
    - absolute paths are used as-is
    - relative paths are first interpreted relative to repo root
    - if not found, we try relative to the granular_ner folder
    """
    repo_root = Path(__file__).resolve().parents[1]
    granular_ner_dir = repo_root / "data" / "ml_training" / "granular_ner"

    if arg is None:
        return granular_ner_dir / "ner_dataset_all.jsonl"

    p = Path(arg)
    if p.is_absolute():
        return p

    p_repo = repo_root / p
    if p_repo.exists():
        return p_repo

    p_granular = granular_ner_dir / p
    return p_granular


def validate_ner_alignment(file_path: Path) -> None:
    print(f"Validating NER alignment for: {file_path}")
    
    issues_found = 0
    total_spans = 0

    def _normalize_span(span):
        """
        Supports common formats:
        - dict spans: {"start": int, "end": int, "label": str, "text": str}
        - dict spans (alt keys): start_char/end_char/span_text or start_offset/end_offset
        - list spans: [start, end, label] or [start, end, label, text]
        """
        if isinstance(span, dict):
            start = span.get("start")
            end = span.get("end")
            if start is None and "start_char" in span:
                start = span.get("start_char")
            if end is None and "end_char" in span:
                end = span.get("end_char")
            if start is None and "start_offset" in span:
                start = span.get("start_offset")
            if end is None and "end_offset" in span:
                end = span.get("end_offset")

            label = span.get("label")
            expected_text = span.get("text")
            if expected_text is None and "span_text" in span:
                expected_text = span.get("span_text")
            return start, end, label, expected_text

        if isinstance(span, (list, tuple)):
            if len(span) == 3:
                start, end, label = span
                return start, end, label, None
            if len(span) >= 4:
                start, end, label, expected_text = span[0], span[1], span[2], span[3]
                return start, end, label, expected_text

        return None, None, None, None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    print(f"Line {line_num}: Invalid JSON")
                    continue

                text = data.get('text', '')
                # Adjust key 'entities' or 'spans' based on your specific JSONL format
                spans = data.get('entities', []) or data.get('spans', [])
                record_id = data.get('id') or data.get('note_id') or "unknown_id"
                
                if not spans:
                    continue

                for span in spans:
                    total_spans += 1
                    start, end, label, expected_text = _normalize_span(span)

                    # 1. Check if indices exist
                    if start is None or end is None:
                        print(f"Line {line_num} ({record_id}): Span missing start/end indices")
                        issues_found += 1
                        continue

                    # 2. Check bounds
                    if end > len(text):
                        print(f"Line {line_num} ({record_id}): Span out of bounds! End {end} > Text Length {len(text)}")
                        issues_found += 1
                        continue

                    # 3. Check text alignment
                    actual_text = text[start:end]
                    
                    # Normalization for loose checking (optional)
                    # We usually want exact match, but sometimes whitespace differs
                    if expected_text is None:
                        continue
                    if actual_text != expected_text:
                        # Allow for minor whitespace differences if strictly necessary
                        if (expected_text is not None) and (actual_text.strip() == expected_text.strip()):
                            continue
                            
                        print(f"Line {line_num} ({record_id}): Mismatch for '{label}'")
                        print(f"   Expected: '{expected_text}'")
                        print(f"   Actual:   '{actual_text}'")
                        print(f"   Indices:  {start}:{end}")
                        issues_found += 1

    except FileNotFoundError:
        print(f"File not found: {file_path} (try data/ml_training/granular_ner/ner_dataset_all.jsonl)")
        return

    print("-" * 30)
    if issues_found == 0:
        print(f"Success! Verified {total_spans} spans. No alignment errors found.")
    else:
        print(f"Validation Failed. Found {issues_found} alignment errors.")

if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    target_file = _resolve_target_path(arg)
    validate_ner_alignment(target_file)
```

---
### `scripts/sanitize_platinum_spans.py`
- Size: `5450` bytes
```
#!/usr/bin/env python3
"""Sanitize platinum PHI spans with protected clinical term vetoes."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.build_model_agnostic_phi_spans import (  # noqa: E402
    _contains_device_keyword,
    _is_ln_station,
    _line_text,
    is_protected_for_geo,
    is_protected_for_person,
    looks_like_cpt,
    looks_like_real_address,
)

DEFAULT_IN_PATH = Path("data/ml_training/phi_platinum_spans.jsonl")
DEFAULT_OUT_PATH = Path("data/ml_training/phi_platinum_spans_CLEANED.jsonl")

GEO_LABELS = {"GEO", "STREET", "CITY", "LOCATION", "ADDRESS", "ZIPCODE", "BUILDINGNUM"}

logger = logging.getLogger("sanitize_platinum_spans")


def init_counters() -> dict[str, int]:
    return {
        "records_processed": 0,
        "records_changed": 0,
        "spans_seen": 0,
        "spans_kept": 0,
        "spans_dropped_protected_geo": 0,
        "spans_dropped_protected_person": 0,
        "spans_dropped_unplausible_address": 0,
        "spans_dropped_ln_station": 0,
        "spans_dropped_device_keyword": 0,
        "spans_dropped_cpt": 0,
    }


def should_drop_span(span: dict[str, Any], note_text: str, counters: dict[str, int]) -> bool:
    label = str(span.get("label", "")).upper()
    start = int(span.get("start", 0))
    end = int(span.get("end", 0))
    if start >= end:
        return True
    span_text = span.get("text")
    if not isinstance(span_text, str):
        span_text = note_text[start:end]
    line_text = _line_text(note_text, start)

    if label in GEO_LABELS:
        if looks_like_cpt(span_text, line_text) and not looks_like_real_address(span_text, line_text):
            counters["spans_dropped_cpt"] += 1
            return True
        if _is_ln_station(span_text, line_text):
            counters["spans_dropped_ln_station"] += 1
            return True
        if _contains_device_keyword(span_text):
            counters["spans_dropped_device_keyword"] += 1
            return True
        if is_protected_for_geo(span_text, line_text):
            counters["spans_dropped_protected_geo"] += 1
            return True
        if not looks_like_real_address(span_text, line_text):
            counters["spans_dropped_unplausible_address"] += 1
            return True

    if label == "PATIENT":
        if is_protected_for_person(span_text, line_text):
            counters["spans_dropped_protected_person"] += 1
            return True

    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Sanitize platinum PHI spans")
    parser.add_argument("--in", dest="in_path", type=Path, default=DEFAULT_IN_PATH)
    parser.add_argument("--out", dest="out_path", type=Path, default=DEFAULT_OUT_PATH)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if not args.in_path.exists():
        logger.error("Input file does not exist: %s", args.in_path)
        return 1

    counters = init_counters()
    args.out_path.parent.mkdir(parents=True, exist_ok=True)
    with args.in_path.open("r", encoding="utf-8") as in_f, args.out_path.open("w", encoding="utf-8") as out_f:
        for line in in_f:
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                out_f.write(line)
                continue
            if not isinstance(record, dict):
                out_f.write(line)
                continue

            counters["records_processed"] += 1
            note_text = record.get("text") or ""
            spans = record.get("spans") or []
            if not isinstance(spans, list):
                out_f.write(line)
                continue

            new_spans = []
            for span in spans:
                if not isinstance(span, dict):
                    continue
                counters["spans_seen"] += 1
                if should_drop_span(span, note_text, counters):
                    continue
                new_spans.append(span)

            counters["spans_kept"] += len(new_spans)
            if len(new_spans) != len(spans):
                counters["records_changed"] += 1
                record = dict(record)
                record["spans"] = new_spans
            out_f.write(json.dumps(record, ensure_ascii=False) + "\n")

    logger.info("Records processed: %s", counters["records_processed"])
    logger.info("Records changed: %s", counters["records_changed"])
    logger.info("Spans seen: %s", counters["spans_seen"])
    logger.info("Spans kept: %s", counters["spans_kept"])
    logger.info("Spans dropped (protected geo): %s", counters["spans_dropped_protected_geo"])
    logger.info("Spans dropped (protected person): %s", counters["spans_dropped_protected_person"])
    logger.info("Spans dropped (LN station): %s", counters["spans_dropped_ln_station"])
    logger.info("Spans dropped (device keyword): %s", counters["spans_dropped_device_keyword"])
    logger.info("Spans dropped (CPT): %s", counters["spans_dropped_cpt"])
    logger.info("Spans dropped (unplausible address): %s", counters["spans_dropped_unplausible_address"])
    logger.info("Output: %s", args.out_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```

---
### `scripts/build_registry_bundle.py`
- Size: `5540` bytes
```
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path
from typing import Any


def _utc_now_iso() -> str:
    return dt.datetime.now(dt.UTC).isoformat()


def _git_short_sha(repo_dir: Path) -> str | None:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(repo_dir))
            .decode()
            .strip()
        )
    except Exception:
        return None


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _copytree(src: Path, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def _is_zone_identifier(path: Path) -> bool:
    return path.name.endswith(":Zone.Identifier")


def build_bundle(src_dir: Path, out_dir: Path, version: str, backend: str) -> tuple[Path, Path]:
    src_dir = src_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    required_files = [
        "config.json",
        "thresholds.json",
    ]
    for rel in required_files:
        if not (src_dir / rel).exists():
            raise FileNotFoundError(f"Missing {rel} in {src_dir}")

    tokenizer_dir = src_dir / "tokenizer"
    if not tokenizer_dir.exists():
        raise FileNotFoundError(f"Missing tokenizer/ in {src_dir}")

    weights = None
    for candidate in ("model.safetensors", "pytorch_model.bin"):
        if (src_dir / candidate).exists():
            weights = src_dir / candidate
            break
    if not weights:
        raise FileNotFoundError("Missing model weights (model.safetensors or pytorch_model.bin)")

    # Labels: prefer label_order.json, otherwise registry_label_fields.json
    label_order_path = src_dir / "label_order.json"
    registry_label_fields_path = src_dir / "registry_label_fields.json"
    if label_order_path.exists():
        labels = _read_json(label_order_path)
        if not isinstance(labels, list) or not all(isinstance(x, str) for x in labels):
            raise ValueError("label_order.json must be a JSON string list")
    elif registry_label_fields_path.exists():
        labels = _read_json(registry_label_fields_path)
        if not isinstance(labels, list) or not all(isinstance(x, str) for x in labels):
            raise ValueError("registry_label_fields.json must be a JSON string list")
    else:
        raise FileNotFoundError("Missing label_order.json or registry_label_fields.json")

    manifest: dict[str, Any] = {
        "model_version": version,
        "model_backend": backend,
        "created_at": _utc_now_iso(),
        "label_count": len(labels),
        "source_dir": str(src_dir),
    }

    repo_root = Path(__file__).resolve().parents[1]
    sha = _git_short_sha(repo_root)
    if sha:
        manifest["repo_commit_sha"] = sha

    with tempfile.TemporaryDirectory(prefix="registry_bundle_stage_") as td:
        stage = Path(td)

        # Copy core files
        shutil.copy2(src_dir / "config.json", stage / "config.json")
        shutil.copy2(weights, stage / weights.name)
        shutil.copy2(src_dir / "thresholds.json", stage / "thresholds.json")

        # Copy labels (always include both for convenience)
        (stage / "label_order.json").write_text(json.dumps(labels, indent=2, sort_keys=False) + "\n")
        (stage / "registry_label_fields.json").write_text(
            json.dumps(labels, indent=2, sort_keys=False) + "\n"
        )

        # Copy tokenizer directory
        _copytree(tokenizer_dir, stage / "tokenizer")

        # Strip Windows ADS marker files if they exist
        for p in list(stage.rglob("*")):
            if _is_zone_identifier(p):
                p.unlink(missing_ok=True)

        # Write manifest
        (stage / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

        # Build tarball
        tar_path = out_dir / "bundle.tar.gz"
        with tarfile.open(tar_path, "w:gz") as tf:
            for p in sorted(stage.rglob("*")):
                if p.is_dir():
                    continue
                rel = p.relative_to(stage)
                tf.add(p, arcname=str(rel))

        # Also write manifest.json next to tarball
        manifest_path = out_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    return tar_path, out_dir / "manifest.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a deployable registry model bundle tarball.")
    parser.add_argument("--src", required=True, help="Source directory containing model artifacts")
    parser.add_argument("--out-dir", default="dist/registry_bundle", help="Output directory")
    parser.add_argument("--backend", default="pytorch", choices=["pytorch", "onnx"], help="Bundle backend")
    parser.add_argument("--version", default="", help="Model version string (used in manifest and S3 path)")
    args = parser.parse_args()

    src_dir = Path(args.src)
    out_dir = Path(args.out_dir)
    version = args.version.strip() or f"local-{_git_short_sha(Path(__file__).resolve().parents[1]) or 'unknown'}"
    backend = args.backend

    tar_path, manifest_path = build_bundle(src_dir=src_dir, out_dir=out_dir, version=version, backend=backend)

    print(f"Built: {tar_path}")
    print(f"Manifest: {manifest_path}")
    print(f"Version: {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


```

---
### `scripts/validate_knowledge_release.py`
- Size: `5847` bytes
```
#!/usr/bin/env python3
"""Validate a knowledge+schema release locally (no external network calls).

This script is intended to backstop knowledge/schema refactors:
- Loads the KB via both the lightweight JSON loader and the main KB adapter
- Validates the registry schema can build a RegistryRecord model
- Runs a no-op extraction in the **parallel_ner** pathway to ensure nothing crashes at import/runtime
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def _parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--kb",
        default="data/knowledge/ip_coding_billing_v3_0.json",
        help="Path to knowledge base JSON (default: data/knowledge/ip_coding_billing_v3_0.json)",
    )
    ap.add_argument(
        "--schema",
        default="data/knowledge/IP_Registry.json",
        help="Path to registry JSON schema (default: data/knowledge/IP_Registry.json)",
    )
    ap.add_argument(
        "--no-op-note",
        default="",
        help="Note text for a no-op registry extraction run (default: empty string).",
    )
    ap.add_argument(
        "--strict",
        action="store_true",
        help="Fail if KB filename semantic version mismatches internal version.",
    )
    return ap.parse_args()


def _extract_semver_from_filename(path: Path) -> tuple[int, int] | None:
    import re

    m = re.search(r"_v(\d+)[._](\d+)\.json$", path.name)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2))


def _extract_semver_from_kb_version(value: object) -> tuple[int, int] | None:
    if not isinstance(value, str):
        return None
    parts = value.strip().lstrip("v").split(".")
    if len(parts) < 2:
        return None
    try:
        return int(parts[0]), int(parts[1])
    except ValueError:
        return None


def main() -> int:
    args = _parse_args()
    kb_path = Path(args.kb)
    schema_path = Path(args.schema)

    if not kb_path.is_file():
        print(f"ERROR: KB not found: {kb_path}", file=sys.stderr)
        return 2
    if not schema_path.is_file():
        print(f"ERROR: Schema not found: {schema_path}", file=sys.stderr)
        return 2

    # 1) Basic JSON parse
    try:
        kb_json = json.loads(kb_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: KB is not valid JSON: {kb_path} ({exc})", file=sys.stderr)
        return 2

    kb_version = kb_json.get("version")
    file_semver = _extract_semver_from_filename(kb_path.resolve())
    kb_semver = _extract_semver_from_kb_version(kb_version)
    if args.strict and file_semver and kb_semver and file_semver != kb_semver:
        print(
            f"ERROR: KB filename semver {file_semver} != internal version {kb_semver} ({kb_path})",
            file=sys.stderr,
        )
        return 2

    # 2) Validate KB schema using the main loader (Draft-07 schema)
    try:
        from modules.common.knowledge import get_knowledge

        _ = get_knowledge(kb_path, force_reload=True)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: KB failed Procedure Suite knowledge schema validation: {exc}", file=sys.stderr)
        return 2

    # 3) Validate the KB adapter loads and can resolve a representative code
    try:
        from modules.coder.adapters.persistence.csv_kb_adapter import JsonKnowledgeBaseAdapter

        kb_repo = JsonKnowledgeBaseAdapter(kb_path)
        sample = kb_repo.get_procedure_info("31628") or kb_repo.get_procedure_info("+31628")
        if sample is None:
            print("ERROR: KB adapter could not resolve CPT 31628", file=sys.stderr)
            return 2
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: KB adapter load failed: {exc}", file=sys.stderr)
        return 2

    # 4) Validate RegistryRecord model can be built from schema (dynamic model)
    try:
        from modules.registry.schema import RegistryRecord

        _ = RegistryRecord.model_validate({})
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: RegistryRecord model build/validation failed: {exc}", file=sys.stderr)
        return 2

    # 5) No-op registry extraction (should not crash; no external calls required)
    try:
        from modules.registry.application.registry_service import RegistryService

        # Ensure no-network behavior: use the parallel_ner pathway instead of the LLM RegistryEngine.
        previous_engine = os.environ.get("REGISTRY_EXTRACTION_ENGINE")
        os.environ["REGISTRY_EXTRACTION_ENGINE"] = "parallel_ner"
        try:
            record, _warnings, _meta = RegistryService(default_version="v3").extract_record(
                args.no_op_note or "",
                note_id="validate_knowledge_release",
            )
        finally:
            if previous_engine is None:
                os.environ.pop("REGISTRY_EXTRACTION_ENGINE", None)
            else:
                os.environ["REGISTRY_EXTRACTION_ENGINE"] = previous_engine
        if record is None:
            print("ERROR: registry extract_record returned None", file=sys.stderr)
            return 2
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: registry no-op extraction failed: {exc}", file=sys.stderr)
        return 2

    # 6) Deterministic RegistryRecord→CPT should not crash
    try:
        from modules.coder.domain_rules.registry_to_cpt.coding_rules import derive_all_codes_with_meta

        _codes, _rationales, _warnings = derive_all_codes_with_meta(record)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: deterministic Registry→CPT derivation failed: {exc}", file=sys.stderr)
        return 2

    print("OK: validate_knowledge_release passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```

---
### `scripts/ingest_phase0_data.py`
- Size: `5928` bytes
```
#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from modules.registry.schema.ip_v3_extraction import (
    EvidenceSpan,
    IPRegistryV3,
    LesionDetails,
    Outcomes,
    ProcedureEvent,
    ProcedureTarget,
)


def _is_missing(value: Any) -> bool:
    return value is None or (isinstance(value, float) and pd.isna(value)) or (isinstance(value, str) and not value.strip())


def _get_str(row: pd.Series, column: str) -> str | None:
    if column not in row:
        return None
    value = row[column]
    if _is_missing(value):
        return None
    return str(value)


def _get_float(row: pd.Series, column: str) -> float | None:
    if column not in row:
        return None
    value = row[column]
    if _is_missing(value):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_json_value(row: pd.Series, column: str) -> Any | None:
    raw = _get_str(row, column)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def _parse_json_list(row: pd.Series, column: str) -> list[str]:
    value = _parse_json_value(row, column)
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if not _is_missing(item)]
    return []


def row_to_event(row: pd.Series) -> ProcedureEvent:
    target = ProcedureTarget(
        anatomy_type=_get_str(row, "target.anatomy_type"),
        lobe=_get_str(row, "target.location.lobe"),
        segment=_get_str(row, "target.location.segment"),
        station=_get_str(row, "target.station"),
    )

    lesion = LesionDetails(
        lesion_type=_get_str(row, "lesion.type"),
        size_mm=_get_float(row, "lesion.size_mm"),
    )

    outcomes = Outcomes(
        airway_lumen_pre=_get_str(row, "outcomes.airway.lumen_pre"),
        airway_lumen_post=_get_str(row, "outcomes.airway.lumen_post"),
        symptoms=_get_str(row, "outcomes.symptoms"),
        pleural=_get_str(row, "outcomes.pleural"),
        complications=_get_str(row, "outcomes.complications"),
    )

    evidence_quote = _get_str(row, "evidence_quote")
    evidence = EvidenceSpan(quote=evidence_quote) if evidence_quote else None

    return ProcedureEvent(
        event_id=str(row["event_id"]),
        type=str(row["type"]),
        method=_get_str(row, "method"),
        target=target,
        lesion=lesion,
        devices=_parse_json_list(row, "devices_json"),
        specimens=_parse_json_list(row, "specimens_json"),
        outcomes=outcomes,
        evidence=evidence,
        measurements=_parse_json_value(row, "measurements_json"),
        findings=_parse_json_value(row, "findings_json"),
        stent_size=_get_str(row, "stent.size"),
        stent_material_or_brand=_get_str(row, "stent.material_or_brand"),
        catheter_size_fr=_get_float(row, "catheter.size_fr"),
    )


def _default_index_csv(events_csv: Path) -> Path:
    candidate = events_csv.parent / "Note_Index.csv"
    if candidate.exists():
        return candidate
    candidate = events_csv.parent / "note_index.csv"
    if candidate.exists():
        return candidate
    return events_csv.parent / "Note_Index.csv"


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest Phase 0 granular CSVs into V3 golden JSON registry files.")
    parser.add_argument(
        "--events-csv",
        type=Path,
        default=Path("data/registry_granular/csvs/V3_Procedure_events.csv"),
        help="Path to V3_Procedure_events.csv",
    )
    parser.add_argument(
        "--index-csv",
        type=Path,
        default=None,
        help="Path to Note_Index.csv (or note_index.csv); default searches next to events CSV.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/knowledge/golden_registry_v3"),
        help="Directory to write {note_id}.json files",
    )
    args = parser.parse_args()

    events_csv: Path = args.events_csv
    index_csv: Path = args.index_csv or _default_index_csv(events_csv)
    output_dir: Path = args.output_dir

    if not events_csv.exists():
        raise FileNotFoundError(f"Events CSV not found: {events_csv}")
    if not index_csv.exists():
        raise FileNotFoundError(f"Index CSV not found: {index_csv}")

    output_dir.mkdir(parents=True, exist_ok=True)

    events_df = pd.read_csv(events_csv)
    index_df = pd.read_csv(index_csv)

    if "note_id" not in events_df.columns:
        raise ValueError(f"Events CSV missing required column 'note_id': {events_csv}")
    if "note_id" not in index_df.columns or "source_file" not in index_df.columns:
        raise ValueError(f"Index CSV must include 'note_id' and 'source_file': {index_csv}")

    note_id_to_source = (
        index_df[["note_id", "source_file"]].dropna(subset=["note_id"]).astype({"note_id": str}).set_index("note_id")[
            "source_file"
        ]
    ).to_dict()

    written = 0
    for note_id, group in events_df.groupby("note_id", dropna=True):
        note_id_str = str(note_id)
        source_filename = str(note_id_to_source.get(note_id_str, f"{note_id_str}.txt"))

        procedures = [row_to_event(row) for _, row in group.iterrows()]
        registry = IPRegistryV3(note_id=note_id_str, source_filename=source_filename, procedures=procedures)

        out_path = output_dir / f"{note_id_str}.json"
        out_path.write_text(json.dumps(registry.model_dump(mode="json"), indent=2, sort_keys=True) + "\n")
        written += 1

    print(f"Wrote {written} registry files to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```

---
### `scripts/normalize_phi_labels.py`
- Size: `5946` bytes
```
#!/usr/bin/env python3
"""Post-hoc label normalization for silver PHI distillation output.

Goal: map a potentially-granular (and occasionally noisy) label schema into a small,
stable client-training schema:

- PATIENT
- DATE
- GEO
- ID
- CONTACT
- O
"""

from __future__ import annotations

import argparse
import json
import logging
from collections import Counter
from pathlib import Path
from typing import Literal

DEFAULT_IN_PATH = Path("data/ml_training/distilled_phi_CLEANED.jsonl")
DEFAULT_OUT_PATH = Path("data/ml_training/distilled_phi_CLEANED_STANDARD.jsonl")

logger = logging.getLogger("normalize_phi_labels")

PasswordPolicy = Literal["id", "drop"]


def get_category(tag: str) -> str:
    if not tag or tag == "O":
        return "O"
    if "-" in tag:
        return tag.split("-", 1)[1]
    return tag


def repair_bio(tags: list[str]) -> list[str]:
    repaired = list(tags)
    for idx, tag in enumerate(repaired):
        if not tag.startswith("I-"):
            continue
        label = get_category(tag)
        if idx == 0:
            repaired[idx] = f"B-{label}"
            continue
        prev_tag = repaired[idx - 1]
        if prev_tag == "O" or get_category(prev_tag) != label:
            repaired[idx] = f"B-{label}"
    return repaired


_DIRECT_CATEGORY_MAP: dict[str, str] = {
    "PATIENT": "PATIENT",
    "GEO": "GEO",
    "STREET": "GEO",
    "DATEOFBIRTH": "DATE",
    "DATE": "DATE",
    "TELEPHONENUM": "CONTACT",
    "EMAIL": "CONTACT",
    "USERNAME": "PATIENT",
    "SOCIALNUM": "ID",
    "DRIVERLICENSENUM": "ID",
    "IDCARDNUM": "ID",
    "ACCOUNTNUM": "ID",
    "TAXNUM": "ID",
}

_OBVIOUS_ID_CATEGORIES: set[str] = {
    "PASSPORT",
    "SSN",
    "MEDICALRECORDNUM",
    "MRN",
    "CREDITCARD",
    "CREDITCARDNUM",
    "BANKACCOUNTNUM",
    "ROUTINGNUM",
    "VIN",
}


def _normalize_category(category: str, *, password_policy: PasswordPolicy) -> str | None:
    category_upper = category.upper()
    if category_upper == "PASSWORD":
        if password_policy == "drop":
            return None
        return "ID"
    if category_upper in _DIRECT_CATEGORY_MAP:
        return _DIRECT_CATEGORY_MAP[category_upper]
    if category_upper in _OBVIOUS_ID_CATEGORIES:
        return "ID"
    if "NUM" in category_upper:
        return "ID"
    return category_upper


def normalize_tags(tags: list[str], *, password_policy: PasswordPolicy = "id") -> tuple[list[str], Counter, Counter, int, int]:
    before = Counter()
    after = Counter()
    password_mapped = 0
    password_dropped = 0

    out: list[str] = []
    for tag in tags:
        if tag == "O":
            out.append(tag)
            continue

        if "-" in tag:
            prefix, category = tag.split("-", 1)
            prefix = prefix.upper()
        else:
            prefix, category = "B", tag

        category_upper = category.upper()
        before[category_upper] += 1

        normalized_category = _normalize_category(category_upper, password_policy=password_policy)
        if normalized_category is None:
            out.append("O")
            password_dropped += 1
            continue

        if category_upper == "PASSWORD" and normalized_category == "ID":
            password_mapped += 1

        after[normalized_category] += 1
        out.append(f"{prefix}-{normalized_category}")

    repaired = repair_bio(out)
    return repaired, before, after, password_mapped, password_dropped


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize silver PHI BIO labels into a small stable schema")
    parser.add_argument("--in", dest="in_path", type=Path, default=DEFAULT_IN_PATH)
    parser.add_argument("--out", dest="out_path", type=Path, default=DEFAULT_OUT_PATH)
    parser.add_argument("--password-policy", choices=("id", "drop"), default="id")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if not args.in_path.exists():
        logger.error("Input file does not exist: %s", args.in_path)
        return 1

    lines_processed = 0
    lines_changed = 0
    category_before = Counter()
    category_after = Counter()
    password_mapped = 0
    password_dropped = 0

    args.out_path.parent.mkdir(parents=True, exist_ok=True)
    with args.in_path.open("r", encoding="utf-8") as in_f, args.out_path.open("w", encoding="utf-8") as out_f:
        for line in in_f:
            if not line.strip():
                continue
            lines_processed += 1
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                out_f.write(line)
                continue
            if not isinstance(record, dict):
                out_f.write(line)
                continue

            tags = record.get("ner_tags")
            if not isinstance(tags, list):
                out_f.write(line)
                continue

            normalized, before, after, pw_mapped, pw_dropped = normalize_tags(
                tags, password_policy=args.password_policy
            )
            category_before.update(before)
            category_after.update(after)
            password_mapped += pw_mapped
            password_dropped += pw_dropped

            if normalized != tags:
                lines_changed += 1
                record = dict(record)
                record["ner_tags"] = normalized
            out_f.write(json.dumps(record, ensure_ascii=False) + "\n")

    logger.info("Lines processed: %s", lines_processed)
    logger.info("Lines changed: %s", lines_changed)
    logger.info("Password mapped: %s", password_mapped)
    logger.info("Password dropped: %s", password_dropped)
    logger.info("Top categories before: %s", category_before.most_common(20))
    logger.info("Top categories after: %s", category_after.most_common(20))
    logger.info("Output: %s", args.out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


```

---
### `scripts/bootstrap_granular_ner_bundle.py`
- Size: `6097` bytes
```
#!/usr/bin/env python3
"""Bootstrap the granular NER ONNX bundle into a local runtime directory.

This is intended for Railway deployment where large ONNX artifacts are stored in S3
and fetched at container start.

Env vars:
- GRANULAR_NER_BUNDLE_S3_URI_ONNX: s3://<bucket>/<key>/bundle.tar.gz
  - Fallback: GRANULAR_NER_BUNDLE_S3_URI
- GRANULAR_NER_RUNTIME_DIR: where to unpack the bundle (default: data/models/granular_ner_runtime)

On success, sets:
- GRANULAR_NER_MODEL_DIR=<GRANULAR_NER_RUNTIME_DIR>
"""

from __future__ import annotations

import json
import os
import shutil
import tarfile
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


BOOTSTRAP_STATE_FILENAME = ".bootstrap_state.json"


@dataclass(frozen=True)
class BootstrapResult:
    runtime_dir: Path
    downloaded: bool
    manifest: dict[str, Any]


def _parse_s3_uri(uri: str) -> tuple[str, str]:
    if not uri.startswith("s3://"):
        raise ValueError(f"Not an s3:// URI: {uri}")
    no_scheme = uri[len("s3://") :]
    bucket, _, key = no_scheme.partition("/")
    if not bucket or not key:
        raise ValueError(f"Invalid s3:// URI: {uri}")
    return bucket, key


def _download_s3_key(bucket: str, key: str, dest: Path) -> None:
    # Lazy import so local dev can run without boto3 unless bootstrap is enabled.
    import boto3  # type: ignore

    client = boto3.client("s3")
    dest.parent.mkdir(parents=True, exist_ok=True)

    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(prefix=dest.name, dir=str(dest.parent), delete=False) as tf:
            tmp_path = Path(tf.name)
        client.download_file(bucket, key, str(tmp_path))
        os.replace(str(tmp_path), str(dest))
    finally:
        if tmp_path and tmp_path.exists():
            try:
                tmp_path.unlink()
            except Exception:
                pass


def _extract_tarball_to_dir(tar_gz_path: Path, dest_dir: Path) -> None:
    dest_dir.mkdir(parents=True, exist_ok=True)
    with tarfile.open(tar_gz_path, "r:gz") as tf:
        tf.extractall(path=dest_dir)


def _flatten_single_root(extracted_dir: Path) -> Path:
    children = [p for p in extracted_dir.iterdir() if p.name not in (".DS_Store",)]
    if len(children) == 1 and children[0].is_dir():
        return children[0]
    return extracted_dir


def _replace_tree(src_dir: Path, dest_dir: Path) -> None:
    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    dest_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src_dir, dest_dir)


def _read_bootstrap_state(runtime_dir: Path) -> dict[str, Any]:
    path = runtime_dir / BOOTSTRAP_STATE_FILENAME
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def _write_bootstrap_state(runtime_dir: Path, state: dict[str, Any]) -> None:
    runtime_dir.mkdir(parents=True, exist_ok=True)
    path = runtime_dir / BOOTSTRAP_STATE_FILENAME
    path.write_text(json.dumps(state, indent=2, sort_keys=True))


def _configured_uri() -> str | None:
    return os.getenv("GRANULAR_NER_BUNDLE_S3_URI_ONNX") or os.getenv("GRANULAR_NER_BUNDLE_S3_URI")


def _runtime_dir() -> Path:
    return Path(os.getenv("GRANULAR_NER_RUNTIME_DIR", "data/models/granular_ner_runtime"))


def ensure_granular_ner_bundle() -> BootstrapResult:
    uri = (_configured_uri() or "").strip()
    runtime_dir = _runtime_dir()

    if not uri:
        # Nothing to do; still expose resolved model dir if it's already present.
        if runtime_dir.exists():
            os.environ.setdefault("GRANULAR_NER_MODEL_DIR", str(runtime_dir))
        return BootstrapResult(runtime_dir=runtime_dir, downloaded=False, manifest={})

    if not uri.endswith(".tar.gz"):
        raise ValueError(
            "GRANULAR_NER_BUNDLE_S3_URI_ONNX must point to a .tar.gz bundle "
            f"(got: {uri})."
        )

    existing_manifest_path = runtime_dir / "manifest.json"
    state = _read_bootstrap_state(runtime_dir)
    state_uri = (state.get("configured_source_uri") or "").strip()

    if existing_manifest_path.exists() and state_uri == uri:
        # Bundle URIs are immutable; matching state is sufficient.
        os.environ["GRANULAR_NER_MODEL_DIR"] = str(runtime_dir)
        try:
            manifest = json.loads(existing_manifest_path.read_text())
        except Exception:
            manifest = {}
        return BootstrapResult(runtime_dir=runtime_dir, downloaded=False, manifest=manifest)

    bucket, key = _parse_s3_uri(uri)

    with tempfile.TemporaryDirectory(prefix="granular_ner_bundle_") as td:
        td_path = Path(td)
        tar_path = td_path / "bundle.tar.gz"
        _download_s3_key(bucket=bucket, key=key, dest=tar_path)

        extracted = td_path / "extracted"
        _extract_tarball_to_dir(tar_path, extracted)
        root = _flatten_single_root(extracted)

        # Add/override minimal manifest for provenance.
        manifest: dict[str, Any] = {
            "bundle_type": "granular_ner",
            "model_backend": "onnx",
            "source_uri": uri,
            "source_type": "s3_tarball",
        }
        (root / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True))

        _replace_tree(root, runtime_dir)

    _write_bootstrap_state(
        runtime_dir,
        {
            "configured_source_uri": uri,
        },
    )
    os.environ["GRANULAR_NER_MODEL_DIR"] = str(runtime_dir)
    return BootstrapResult(runtime_dir=runtime_dir, downloaded=True, manifest=manifest)


def main() -> int:
    result = ensure_granular_ner_bundle()
    uri = _configured_uri()
    if uri:
        action = "downloaded" if result.downloaded else "cached"
        print(
            f"[bootstrap_granular_ner_bundle] {action} granular NER bundle into {result.runtime_dir} "
            f"(source={uri})"
        )
        print(f"[bootstrap_granular_ner_bundle] GRANULAR_NER_MODEL_DIR={os.environ.get('GRANULAR_NER_MODEL_DIR')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


```

---
### `scripts/bootstrap_phi_redactor_vendor_bundle.py`
- Size: `6388` bytes
```
#!/usr/bin/env python3
"""Bootstrap the PHI redactor vendor bundle into the UI vendor directory.

Intended for Railway deployment where large model assets live in S3.

Env vars:
- PHI_REDACTOR_VENDOR_BUNDLE_S3_URI: s3://<bucket>/<key>/bundle.tar.gz
  - Fallback: PHI_REDACTOR_VENDOR_BUNDLE_S3_URI_ONNX
- PHI_REDACTOR_VENDOR_DIR: destination directory
  (default: modules/api/static/phi_redactor/vendor/phi_distilbert_ner_quant)
"""

from __future__ import annotations

import json
import os
import shutil
import tarfile
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

BOOTSTRAP_STATE_FILENAME = ".bootstrap_state.json"


@dataclass(frozen=True)
class BootstrapResult:
    vendor_dir: Path
    downloaded: bool
    manifest: dict[str, Any]


def _parse_s3_uri(uri: str) -> tuple[str, str]:
    if not uri.startswith("s3://"):
        raise ValueError(f"Not an s3:// URI: {uri}")
    no_scheme = uri[len("s3://") :]
    bucket, _, key = no_scheme.partition("/")
    if not bucket or not key:
        raise ValueError(f"Invalid s3:// URI: {uri}")
    return bucket, key


def _download_s3_key(bucket: str, key: str, dest: Path) -> None:
    import boto3  # type: ignore

    client = boto3.client("s3")
    dest.parent.mkdir(parents=True, exist_ok=True)

    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(prefix=dest.name, dir=str(dest.parent), delete=False) as tf:
            tmp_path = Path(tf.name)
        client.download_file(bucket, key, str(tmp_path))
        os.replace(str(tmp_path), str(dest))
    finally:
        if tmp_path and tmp_path.exists():
            try:
                tmp_path.unlink()
            except Exception:
                pass


def _extract_tarball_to_dir(tar_gz_path: Path, dest_dir: Path) -> None:
    dest_dir.mkdir(parents=True, exist_ok=True)
    with tarfile.open(tar_gz_path, "r:gz") as tf:
        tf.extractall(path=dest_dir)


def _flatten_single_root(extracted_dir: Path) -> Path:
    children = [p for p in extracted_dir.iterdir() if p.name not in (".DS_Store",)]
    if len(children) == 1 and children[0].is_dir():
        return children[0]
    return extracted_dir


def _replace_tree(src_dir: Path, dest_dir: Path) -> None:
    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    dest_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src_dir, dest_dir)


def _normalize_model_layout(root: Path) -> None:
    """Ensure transformers.js-compatible layout (onnx/model.onnx)."""
    onnx_dir = root / "onnx"
    onnx_dir.mkdir(parents=True, exist_ok=True)

    # Preferred destination
    dest = onnx_dir / "model.onnx"
    if dest.exists():
        return

    candidates = [
        onnx_dir / "model_quantized.onnx",
        root / "model.onnx",
        root / "model_quantized.onnx",
    ]
    for candidate in candidates:
        if candidate.exists():
            shutil.copy2(candidate, dest)
            return

    raise FileNotFoundError("Unable to locate model.onnx or model_quantized.onnx in bundle")


def _read_bootstrap_state(dest_dir: Path) -> dict[str, Any]:
    path = dest_dir / BOOTSTRAP_STATE_FILENAME
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def _write_bootstrap_state(dest_dir: Path, state: dict[str, Any]) -> None:
    dest_dir.mkdir(parents=True, exist_ok=True)
    path = dest_dir / BOOTSTRAP_STATE_FILENAME
    path.write_text(json.dumps(state, indent=2, sort_keys=True))


def _configured_uri() -> str | None:
    return os.getenv("PHI_REDACTOR_VENDOR_BUNDLE_S3_URI") or os.getenv(
        "PHI_REDACTOR_VENDOR_BUNDLE_S3_URI_ONNX"
    )


def _vendor_dir() -> Path:
    return Path(
        os.getenv(
            "PHI_REDACTOR_VENDOR_DIR",
            "modules/api/static/phi_redactor/vendor/phi_distilbert_ner_quant",
        )
    )


def ensure_phi_redactor_vendor_bundle() -> BootstrapResult:
    # Local dev convenience: load .env if present.
    try:
        from dotenv import load_dotenv  # type: ignore

        load_dotenv()
    except Exception:
        pass

    uri = (_configured_uri() or "").strip()
    vendor_dir = _vendor_dir()

    if not uri:
        return BootstrapResult(vendor_dir=vendor_dir, downloaded=False, manifest={})

    if not uri.endswith(".tar.gz"):
        raise ValueError(
            "PHI_REDACTOR_VENDOR_BUNDLE_S3_URI must point to a .tar.gz bundle "
            f"(got: {uri})."
        )

    state = _read_bootstrap_state(vendor_dir)
    state_uri = (state.get("configured_source_uri") or "").strip()

    existing_config = vendor_dir / "config.json"
    if existing_config.exists() and state_uri == uri:
        _normalize_model_layout(vendor_dir)
        try:
            manifest = json.loads((vendor_dir / "manifest.json").read_text())
        except Exception:
            manifest = {}
        return BootstrapResult(vendor_dir=vendor_dir, downloaded=False, manifest=manifest)

    bucket, key = _parse_s3_uri(uri)

    with tempfile.TemporaryDirectory(prefix="phi_redactor_vendor_") as td:
        td_path = Path(td)
        tar_path = td_path / "bundle.tar.gz"
        _download_s3_key(bucket=bucket, key=key, dest=tar_path)

        extracted = td_path / "extracted"
        _extract_tarball_to_dir(tar_path, extracted)
        root = _flatten_single_root(extracted)
        _normalize_model_layout(root)

        manifest: dict[str, Any] = {
            "bundle_type": "phi_redactor_vendor",
            "model_backend": "onnx",
            "source_uri": uri,
            "source_type": "s3_tarball",
        }
        (root / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True))

        _replace_tree(root, vendor_dir)

    _write_bootstrap_state(
        vendor_dir,
        {
            "configured_source_uri": uri,
        },
    )
    return BootstrapResult(vendor_dir=vendor_dir, downloaded=True, manifest=manifest)


def main() -> int:
    result = ensure_phi_redactor_vendor_bundle()
    uri = _configured_uri()
    if uri:
        action = "downloaded" if result.downloaded else "cached"
        print(
            f"[bootstrap_phi_redactor_vendor_bundle] {action} PHI vendor bundle into {result.vendor_dir} "
            f"(source={uri})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```

---
### `scripts/add_training_case.py`
- Size: `6413` bytes
```
import json
import datetime
import re
from pathlib import Path

def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _resolve_repo_root(repo_root: Path | str | None) -> Path:
    """
    Resolve the actual repository root for this checkout.

    Many generated scripts pass an incorrect "repo_root" (often a subdirectory
    under ``data/``). When that subdirectory is still within this checkout, we
    can reliably correct it to the real repo root based on this module's path.
    """

    module_repo_root = Path(__file__).resolve().parents[1]
    if repo_root is None:
        return module_repo_root

    candidate = Path(repo_root).expanduser()
    try:
        candidate = candidate.resolve()
    except FileNotFoundError:
        candidate = candidate.absolute()

    if candidate.is_file():
        candidate = candidate.parent

    if _is_within(candidate, module_repo_root):
        return module_repo_root

    return candidate


def add_case(note_id, raw_text, entities, repo_root):
    """
    Central logic to update ML training files.
    
    Args:
        note_id (str): Unique identifier for the note.
        raw_text (str): The clinical text.
        entities (list): List of dicts [{'label': '...', 'start': 0, 'end': 5, 'text': '...'}, ...]
        repo_root (Path): Path object pointing to the repository root.
    """
    
    repo_root = _resolve_repo_root(repo_root)

    # --- Guard against the most common generated-script bug ---
    # Some generated scripts accidentally swap (note_id, raw_text) and call:
    #   add_case(<full note text>, <script_name_or_dataset_tag>, entities, repo_root)
    # That corrupts the dataset (entities get clamped to the short "raw_text").
    if isinstance(note_id, str) and isinstance(raw_text, str):
        note_id_looks_like_text = (len(note_id) > 200) and (("\n" in note_id) or (" " in note_id))
        raw_text_looks_like_id = (len(raw_text) <= 80) and ("\n" not in raw_text) and (
            raw_text.endswith(".py") or re.fullmatch(r"[A-Za-z0-9_.-]+", raw_text) is not None
        )
        if note_id_looks_like_text and raw_text_looks_like_id:
            raise ValueError(
                "add_case() expects (note_id, raw_text, entities, repo_root), but it looks like "
                "the first two arguments were swapped. Got a note_id that looks like note text "
                f"(len={len(note_id)}), and a raw_text that looks like an identifier ({raw_text!r}). "
                "Fix the caller to pass a short unique note_id and the full note text as raw_text."
            )

    # Define Output Directory Structure
    output_dir = repo_root / "data" / "ml_training" / "granular_ner"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    files = {
        "ner": output_dir / "ner_dataset_all.jsonl",
        "notes": output_dir / "notes.jsonl",
        "spans": output_dir / "spans.jsonl",
        "stats": output_dir / "stats.json",
        "log": output_dir / "alignment_warnings.log"
    }

    if entities is None:
        entities = []

    # 1. Normalize + sort entities
    normalized_entities = []
    for ent in entities:
        if not isinstance(ent, dict):
            continue

        label = ent.get("label")
        start = ent.get("start")
        end = ent.get("end")
        text = ent.get("text", ent.get("token"))

        try:
            start = int(start)
            end = int(end)
        except (TypeError, ValueError):
            if isinstance(text, str) and raw_text:
                idx = raw_text.find(text)
                if idx != -1:
                    start = idx
                    end = idx + len(text)
                else:
                    continue
            else:
                continue

        if not isinstance(label, str) or not label:
            continue

        if start < 0:
            start = 0
        if end < start:
            end = start
        if raw_text:
            max_len = len(raw_text)
            if start > max_len:
                start = max_len
            if end > max_len:
                end = max_len

        if text is None:
            text = raw_text[start:end]
        elif raw_text:
            text = raw_text[start:end]

        if end <= start:
            continue

        normalized_entities.append(
            {"label": label, "start": start, "end": end, "text": text}
        )

    entities = sorted(normalized_entities, key=lambda x: x["start"])

    # 2. Append to ner_dataset_all.jsonl
    with open(files["ner"], 'a', encoding='utf-8') as f:
        record = {"id": note_id, "text": raw_text, "entities": entities}
        f.write(json.dumps(record) + "\n")

    # 3. Append to notes.jsonl
    with open(files["notes"], 'a', encoding='utf-8') as f:
        record = {"id": note_id, "text": raw_text}
        f.write(json.dumps(record) + "\n")

    # 4. Append to spans.jsonl
    with open(files["spans"], 'a', encoding='utf-8') as f:
        for ent in entities:
            span_record = {
                "span_id": f"{ent['label']}_{ent['start']}",
                "note_id": note_id,
                "label": ent['label'],
                "text": ent["text"],
                "start": ent['start'],
                "end": ent['end']
            }
            f.write(json.dumps(span_record) + "\n")

    # 5. Update stats.json
    if files["stats"].exists():
        with open(files["stats"], 'r', encoding='utf-8') as f:
            stats = json.load(f)
    else:
        stats = {"total_notes": 0, "total_spans_valid": 0, "label_counts": {}}

    stats["total_notes"] += 1
    stats["total_spans_valid"] += len(entities)
    for ent in entities:
        lbl = ent['label']
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1
    
    with open(files["stats"], 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=4)

    # 6. Validation & Logging
    with open(files["log"], 'a', encoding='utf-8') as log:
        for ent in entities:
            extracted = raw_text[ent['start']:ent['end']]
            if extracted != ent['text']:
                log.write(f"[{datetime.datetime.now()}] MISMATCH: {note_id} | Label {ent['label']} expected '{ent['text']}' but got '{extracted}'\n")

    print(f"✅ Success: {note_id} added to pipeline. ({len(entities)} entities)")

```

---
### `scripts/eval_registry_granular.py`
- Size: `6444` bytes
```
#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from modules.common.exceptions import LLMError
from modules.registry.pipelines.v3_pipeline import run_v3_extraction
from modules.registry.schema.ip_v3_extraction import IPRegistryV3, ProcedureEvent


def _norm(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value.lower() if value else None


def _event_key(event: ProcedureEvent) -> tuple[str, str | None, str | None]:
    station = _norm(event.target.station if event.target else None)
    lobe = _norm(event.target.lobe if event.target else None)
    return (_norm(event.type) or "", station, lobe)


@dataclass(frozen=True)
class ScoreResult:
    tp: int
    fp: int
    fn: int

    @property
    def precision(self) -> float:
        denom = self.tp + self.fp
        if denom == 0:
            return 1.0 if self.fn == 0 else 0.0
        return self.tp / denom

    @property
    def recall(self) -> float:
        denom = self.tp + self.fn
        if denom == 0:
            return 1.0
        return self.tp / denom


class RegistryGranularScorer:
    def score(self, gold: IPRegistryV3, pred: IPRegistryV3) -> tuple[ScoreResult, dict]:
        gold_counts = Counter(_event_key(e) for e in gold.procedures)
        pred_counts = Counter(_event_key(e) for e in pred.procedures)

        tp = sum(min(gold_counts[k], pred_counts.get(k, 0)) for k in gold_counts)
        gold_total = sum(gold_counts.values())
        pred_total = sum(pred_counts.values())
        fp = pred_total - tp
        fn = gold_total - tp

        missing = []
        extra = []
        for k, c in (gold_counts - pred_counts).items():
            missing.append({"key": list(k), "count": c})
        for k, c in (pred_counts - gold_counts).items():
            extra.append({"key": list(k), "count": c})

        details = {
            "gold_event_count": gold_total,
            "pred_event_count": pred_total,
            "missing": missing,
            "extra": extra,
        }
        return ScoreResult(tp=tp, fp=fp, fn=fn), details


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate registry granular extraction against V3 golden JSONs.")
    parser.add_argument(
        "--gold-dir",
        type=Path,
        default=Path("data/knowledge/golden_registry_v3"),
        help="Directory containing gold {note_id}.json files",
    )
    parser.add_argument(
        "--notes-dir",
        type=Path,
        default=Path("data/registry_granular/notes"),
        help="Directory containing raw note .txt files",
    )
    parser.add_argument(
        "--errors-out",
        type=Path,
        default=Path("reports/registry_granular_errors.jsonl"),
        help="Path to write per-note error details (JSONL)",
    )
    args = parser.parse_args()

    gold_dir: Path = args.gold_dir
    notes_dir: Path = args.notes_dir
    errors_out: Path = args.errors_out

    if not gold_dir.exists():
        raise FileNotFoundError(f"Gold dir not found: {gold_dir}")
    if not notes_dir.exists():
        raise FileNotFoundError(f"Notes dir not found: {notes_dir}")

    errors_out.parent.mkdir(parents=True, exist_ok=True)

    scorer = RegistryGranularScorer()

    gold_paths = sorted(gold_dir.glob("*.json"))
    if not gold_paths:
        raise FileNotFoundError(f"No gold JSON files found in: {gold_dir}")

    totals = ScoreResult(tp=0, fp=0, fn=0)
    evaluated = 0
    extraction_errors = 0

    with errors_out.open("w", encoding="utf-8") as f:
        for gold_path in gold_paths:
            gold = IPRegistryV3.model_validate_json(gold_path.read_text())
            note_path = notes_dir / gold.source_filename
            if not note_path.exists():
                f.write(
                    json.dumps(
                        {
                            "note_id": gold.note_id,
                            "gold_path": str(gold_path),
                            "error": "note_file_missing",
                            "expected_note_path": str(note_path),
                        }
                    )
                    + "\n"
                )
                continue

            note_text = note_path.read_text(encoding="utf-8", errors="replace")
            error: dict | None = None
            try:
                pred = run_v3_extraction(note_text)
            except LLMError as exc:
                extraction_errors += 1
                error = {"type": "llm_error", "message": str(exc)[:500]}
                pred = IPRegistryV3(note_id=gold.note_id, source_filename=gold.source_filename, procedures=[])
            except Exception as exc:  # noqa: BLE001
                extraction_errors += 1
                error = {"type": type(exc).__name__, "message": str(exc)[:500]}
                pred = IPRegistryV3(note_id=gold.note_id, source_filename=gold.source_filename, procedures=[])
            pred = pred.model_copy(update={"note_id": gold.note_id, "source_filename": gold.source_filename})

            score, details = scorer.score(gold, pred)
            totals = ScoreResult(tp=totals.tp + score.tp, fp=totals.fp + score.fp, fn=totals.fn + score.fn)
            evaluated += 1

            f.write(
                json.dumps(
                    {
                        "note_id": gold.note_id,
                        "source_filename": gold.source_filename,
                        "extraction_error": error,
                        "score": {"tp": score.tp, "fp": score.fp, "fn": score.fn},
                        "precision": score.precision,
                        "recall": score.recall,
                        **details,
                    }
                )
                + "\n"
            )

    print(f"Evaluated notes: {evaluated} / {len(gold_paths)}")
    print(f"Micro precision: {totals.precision:.3f} (tp={totals.tp}, fp={totals.fp})")
    print(f"Micro recall:    {totals.recall:.3f} (tp={totals.tp}, fn={totals.fn})")
    if extraction_errors:
        print(f"Notes with extraction errors: {extraction_errors}")
    print(f"Wrote errors: {errors_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```

---
### `scripts/knowledge_diff_report.py`
- Size: `6716` bytes
```
#!/usr/bin/env python3
"""Generate a simple diff report between two knowledge base JSON files.

Focuses on high-signal changes for yearly updates:
- Codes added/removed in master_code_index
- Descriptor changes
- RVU changes (rvu_simplified + cms_pfs_2026 totals when available)
- add_on_codes changes
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--old", required=True, help="Path to the old KB JSON")
    ap.add_argument("--new", required=True, help="Path to the new KB JSON")
    ap.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Max examples to print per section (default: 50)",
    )
    return ap.parse_args()


@dataclass(frozen=True)
class _KB:
    path: Path
    sha256: str
    version: str | None
    data: dict[str, Any]


def _load_kb(path: Path) -> _KB:
    raw = path.read_bytes()
    data = json.loads(raw.decode("utf-8"))
    return _KB(
        path=path,
        sha256=hashlib.sha256(raw).hexdigest(),
        version=str(data.get("version")) if data.get("version") is not None else None,
        data=data,
    )


def _master_index(kb: _KB) -> dict[str, Any]:
    master = kb.data.get("master_code_index")
    return master if isinstance(master, dict) else {}


def _add_on_codes(kb: _KB) -> set[str]:
    add_ons = kb.data.get("add_on_codes")
    if not isinstance(add_ons, list):
        return set()
    return {str(x) for x in add_ons if isinstance(x, str) and x.strip()}


def _descriptor(entry: Any) -> str | None:
    if not isinstance(entry, dict):
        return None
    value = entry.get("descriptor")
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _rvu_simplified(entry: Any) -> tuple[float, float, float] | None:
    if not isinstance(entry, dict):
        return None
    simplified = entry.get("rvu_simplified")
    if not isinstance(simplified, dict):
        return None
    work = simplified.get("work")
    pe = simplified.get("pe")
    mp = simplified.get("mp")
    if work is None or pe is None or mp is None:
        return None
    try:
        return float(work), float(pe), float(mp)
    except (TypeError, ValueError):
        return None


def _cms_total_facility_rvu(entry: Any) -> float | None:
    if not isinstance(entry, dict):
        return None
    financials = entry.get("financials")
    if not isinstance(financials, dict):
        return None
    cms = financials.get("cms_pfs_2026")
    if not isinstance(cms, dict):
        return None
    total = cms.get("total_facility_rvu")
    if total is None:
        return None
    try:
        return float(total)
    except (TypeError, ValueError):
        return None


def _fmt_rvu(triple: tuple[float, float, float] | None) -> str:
    if not triple:
        return "n/a"
    work, pe, mp = triple
    total = work + pe + mp
    return f"work={work:.2f} pe={pe:.2f} mp={mp:.2f} total={total:.2f}"


def _print_header(old: _KB, new: _KB) -> None:
    print("Knowledge Diff Report")
    print(f"- old: {old.path} (version={old.version}, sha256={old.sha256[:12]}…)")
    print(f"- new: {new.path} (version={new.version}, sha256={new.sha256[:12]}…)")
    print()


def main() -> int:
    args = _parse_args()
    old = _load_kb(Path(args.old))
    new = _load_kb(Path(args.new))

    _print_header(old, new)

    old_master = _master_index(old)
    new_master = _master_index(new)

    old_codes = set(old_master.keys())
    new_codes = set(new_master.keys())
    added = sorted(new_codes - old_codes)
    removed = sorted(old_codes - new_codes)

    print("**Master Code Index**")
    print(f"- codes added: {len(added)}")
    for code in added[: args.limit]:
        print(f"  - + {code}")
    if len(added) > args.limit:
        print(f"  - … ({len(added) - args.limit} more)")
    print(f"- codes removed: {len(removed)}")
    for code in removed[: args.limit]:
        print(f"  - - {code}")
    if len(removed) > args.limit:
        print(f"  - … ({len(removed) - args.limit} more)")

    descriptor_changed: list[str] = []
    rvu_changed: list[str] = []
    cms_total_changed: list[str] = []

    for code in sorted(old_codes & new_codes):
        old_entry = old_master.get(code)
        new_entry = new_master.get(code)

        if _descriptor(old_entry) != _descriptor(new_entry):
            descriptor_changed.append(code)

        if _rvu_simplified(old_entry) != _rvu_simplified(new_entry):
            rvu_changed.append(code)

        if _cms_total_facility_rvu(old_entry) != _cms_total_facility_rvu(new_entry):
            cms_total_changed.append(code)

    print(f"- descriptor changes: {len(descriptor_changed)}")
    for code in descriptor_changed[: args.limit]:
        print(f"  - {code}: {(_descriptor(old_master.get(code)) or '')!r} -> {(_descriptor(new_master.get(code)) or '')!r}")
    if len(descriptor_changed) > args.limit:
        print(f"  - … ({len(descriptor_changed) - args.limit} more)")

    print(f"- rvu_simplified changes: {len(rvu_changed)}")
    for code in rvu_changed[: args.limit]:
        print(f"  - {code}: {_fmt_rvu(_rvu_simplified(old_master.get(code)))} -> {_fmt_rvu(_rvu_simplified(new_master.get(code)))}")
    if len(rvu_changed) > args.limit:
        print(f"  - … ({len(rvu_changed) - args.limit} more)")

    print(f"- cms_pfs_2026.total_facility_rvu changes: {len(cms_total_changed)}")
    for code in cms_total_changed[: args.limit]:
        o = _cms_total_facility_rvu(old_master.get(code))
        n = _cms_total_facility_rvu(new_master.get(code))
        print(f"  - {code}: {o if o is not None else 'n/a'} -> {n if n is not None else 'n/a'}")
    if len(cms_total_changed) > args.limit:
        print(f"  - … ({len(cms_total_changed) - args.limit} more)")
    print()

    old_add_ons = _add_on_codes(old)
    new_add_ons = _add_on_codes(new)
    added_add_ons = sorted(new_add_ons - old_add_ons)
    removed_add_ons = sorted(old_add_ons - new_add_ons)

    print("**Add-on Codes**")
    print(f"- added: {len(added_add_ons)}")
    for code in added_add_ons[: args.limit]:
        print(f"  - + {code}")
    if len(added_add_ons) > args.limit:
        print(f"  - … ({len(added_add_ons) - args.limit} more)")

    print(f"- removed: {len(removed_add_ons)}")
    for code in removed_add_ons[: args.limit]:
        print(f"  - - {code}")
    if len(removed_add_ons) > args.limit:
        print(f"  - … ({len(removed_add_ons) - args.limit} more)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


```

---
### `scripts/merge_registry_prodigy.py`
- Size: `6757` bytes
```
#!/usr/bin/env python3
"""Merge Prodigy-labeled registry procedure flags into the existing train split.

Rules:
- Hard guard: refuse to merge any Prodigy example whose note_text appears in val/test.
- Deduplicate by note_text, preferring Prodigy labels when duplicates exist.
- Ensure output contains all canonical label columns (missing columns filled with 0).
"""

from __future__ import annotations

import argparse
import hashlib
import logging
import sys
from pathlib import Path

# Add repo root to path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from modules.registry.label_fields import canonical_registry_procedure_labels, load_registry_procedure_labels
from modules.ml_coder.registry_label_constraints import apply_label_constraints

logger = logging.getLogger(__name__)


DEFAULT_LABEL_FIELDS = Path("data/ml_training/registry_label_fields.json")


def _normalize_text(text: str) -> str:
    return (text or "").strip()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(_normalize_text(text).encode("utf-8")).hexdigest()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-train-csv",
        type=Path,
        default=Path("data/ml_training/registry_train.csv"),
        help="Base training CSV to augment",
    )
    parser.add_argument(
        "--val-csv",
        type=Path,
        default=Path("data/ml_training/registry_val.csv"),
        help="Validation CSV (leakage guard)",
    )
    parser.add_argument(
        "--test-csv",
        type=Path,
        default=Path("data/ml_training/registry_test.csv"),
        help="Test CSV (leakage guard)",
    )
    parser.add_argument(
        "--prodigy-csv",
        type=Path,
        default=Path("data/ml_training/registry_prodigy_labels.csv"),
        help="Prodigy-labeled CSV to merge in",
    )
    parser.add_argument(
        "--out-csv",
        type=Path,
        default=Path("data/ml_training/registry_train_augmented.csv"),
        help="Output augmented train CSV",
    )
    parser.add_argument(
        "--label-fields",
        type=Path,
        default=DEFAULT_LABEL_FIELDS,
        help="JSON list of canonical registry labels",
    )
    return parser.parse_args(argv)


def _require_note_text(df, path: Path) -> None:
    if "note_text" not in df.columns:
        raise ValueError(f"Missing required column 'note_text' in {path}")


def _apply_constraints_inplace(df, labels: list[str]) -> None:
    """Apply deterministic label constraints after merges (avoid training skew)."""
    if df.empty or "note_text" not in df.columns:
        return

    # Fast, unconditional implications.
    if "transbronchial_cryobiopsy" in df.columns and "transbronchial_biopsy" in df.columns:
        df.loc[df["transbronchial_cryobiopsy"].astype(int) == 1, "transbronchial_biopsy"] = 1

    # Text-dependent normalization (only when both are positive).
    if "bal" not in df.columns or "bronchial_wash" not in df.columns:
        return
    mask = (df["bal"].astype(int) == 1) & (df["bronchial_wash"].astype(int) == 1)
    if not mask.any():
        return

    for idx in df.index[mask]:
        row = {
            "note_text": str(df.at[idx, "note_text"] or ""),
            "bal": int(df.at[idx, "bal"]),
            "bronchial_wash": int(df.at[idx, "bronchial_wash"]),
        }
        apply_label_constraints(row)
        df.at[idx, "bal"] = int(row["bal"])
        df.at[idx, "bronchial_wash"] = int(row["bronchial_wash"])


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    args = parse_args(argv)

    labels = load_registry_procedure_labels(args.label_fields)
    expected = len(canonical_registry_procedure_labels())
    if len(labels) != expected:
        raise ValueError(f"Expected {expected} registry labels, got {len(labels)}")

    import pandas as pd

    train_df = pd.read_csv(args.base_train_csv)
    val_df = pd.read_csv(args.val_csv)
    test_df = pd.read_csv(args.test_csv)
    prodigy_df = pd.read_csv(args.prodigy_csv)

    _require_note_text(train_df, args.base_train_csv)
    _require_note_text(val_df, args.val_csv)
    _require_note_text(test_df, args.test_csv)
    _require_note_text(prodigy_df, args.prodigy_csv)

    val_test_hashes = set(_sha256_text(t) for t in val_df["note_text"].fillna("").astype(str).tolist())
    val_test_hashes |= set(_sha256_text(t) for t in test_df["note_text"].fillna("").astype(str).tolist())

    prodigy_hashes = [_sha256_text(t) for t in prodigy_df["note_text"].fillna("").astype(str).tolist()]
    leaked = [h for h in prodigy_hashes if h in val_test_hashes]
    if leaked:
        raise SystemExit(
            f"Refusing to merge: {len(leaked)} Prodigy examples appear in val/test splits."
        )

    # Ensure label columns exist (fill missing with 0).
    for df in (train_df, prodigy_df):
        for label in labels:
            if label not in df.columns:
                df[label] = 0
            df[label] = pd.to_numeric(df[label], errors="coerce").fillna(0).clip(0, 1).astype(int)

    # Ensure required metadata columns exist.
    for df, source in ((train_df, "base"), (prodigy_df, "prodigy")):
        if "label_source" not in df.columns:
            df["label_source"] = source
        if "label_confidence" not in df.columns:
            df["label_confidence"] = 1.0

    # Prefer Prodigy rows when note_text duplicates exist.
    prodigy_df["_priority"] = 1
    train_df["_priority"] = 0

    combined = pd.concat([prodigy_df, train_df], ignore_index=True)
    combined["_note_hash"] = combined["note_text"].fillna("").astype(str).map(_sha256_text)

    combined.sort_values(by=["_priority"], ascending=False, inplace=True)
    merged = combined.drop_duplicates(subset=["_note_hash"], keep="first").drop(columns=["_priority", "_note_hash"])

    _apply_constraints_inplace(merged, labels)

    # Stable column order: base cols first (plus any prodigy-only cols), then labels.
    base_cols = [c for c in train_df.columns if c not in labels and c not in {"_priority"}]
    for c in prodigy_df.columns:
        if c in {"_priority"}:
            continue
        if c not in base_cols and c not in labels:
            base_cols.append(c)
    out_cols = [c for c in base_cols if c in merged.columns] + [c for c in labels if c in merged.columns]
    merged = merged.reindex(columns=out_cols)

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(args.out_csv, index=False)
    logger.info("Wrote %d rows to %s", len(merged), args.out_csv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```

---
### `scripts/prodigy_export_registry.py`
- Size: `6875` bytes
```
#!/usr/bin/env python3
"""Export Prodigy multi-label annotations for registry procedure flags.

Supports two modes:
  - DB mode:   --dataset <name> (requires Prodigy installed and configured)
  - File mode: --input-jsonl <path> (reads a Prodigy-exported JSONL file; CI friendly)

Outputs a training CSV compatible with `scripts/train_roberta.py`:
  - note_text
  - label columns (0/1) for each item in `REGISTRY_LABELS`
  - label_source="prodigy"
  - label_confidence=1.0
  - optional metadata columns (encounter_id/source_file/prodigy_dataset)

Input formats supported:
  - Prodigy `choice` style: uses `accept: [label, ...]`
  - Prodigy `textcat` style: may store `accept` OR `cats: {label: 0/1}`
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
from pathlib import Path
from typing import Any, Iterable

# Add repo root to path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from modules.ml_coder.registry_label_schema import (  # noqa: E402, I001
    REGISTRY_LABELS,
    compute_encounter_id,
)

logger = logging.getLogger(__name__)


def iter_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with open(path, encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                logger.warning("Skipping invalid JSON at %s:%d", path, line_num)
                continue
            if isinstance(obj, dict):
                yield obj


def load_prodigy_dataset(dataset: str) -> list[dict[str, Any]]:
    try:
        from prodigy.components.db import connect
    except ImportError as exc:  # pragma: no cover
        raise SystemExit(
            "Prodigy is not installed; use --input-jsonl for file mode or install prodigy."
        ) from exc

    db = connect()
    if dataset not in db:  # pragma: no cover
        available = getattr(db, "datasets", [])
        raise SystemExit(f"Prodigy dataset not found: {dataset}. Available: {available}")

    examples = db.get_dataset_examples(dataset)
    return list(examples)


def _normalize_text(text: Any) -> str:
    return str(text or "").strip()


def _accept_list(example: dict[str, Any]) -> list[str]:
    accept = example.get("accept")
    if accept is None:
        return []
    if isinstance(accept, list):
        return [str(x) for x in accept if str(x).strip()]
    return [str(accept).strip()] if str(accept).strip() else []


def _accepted_labels(example: dict[str, Any], labels: list[str]) -> list[str]:
    accepted = _accept_list(example)
    if accepted:
        return accepted

    cats = example.get("cats")
    if isinstance(cats, dict):
        out: list[str] = []
        for label in labels:
            val = cats.get(label)
            if isinstance(val, bool):
                if val:
                    out.append(label)
                continue
            if isinstance(val, int | float):
                if float(val) >= 0.5:
                    out.append(label)
        return out
    return []

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dataset", type=str, help="Prodigy dataset name (DB mode)")
    group.add_argument("--input-jsonl", type=Path, help="Prodigy-exported JSONL file (file mode)")

    parser.add_argument("--output-csv", type=Path, required=True, help="Output training CSV")
    parser.add_argument(
        "--output-jsonl",
        type=Path,
        default=None,
        help="Optional exported JSONL (deduped)",
    )
    parser.add_argument(
        "--label-source",
        type=str,
        default="human",
        help="Label source value to write",
    )
    parser.add_argument(
        "--label-confidence",
        type=float,
        default=1.0,
        help="Label confidence value to write",
    )
    parser.add_argument(
        "--include-empty-accept",
        action="store_true",
        help="Include examples with empty/missing accept as all-zero labels",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    args = parse_args(argv)

    labels = list(REGISTRY_LABELS)

    dataset_name = None
    source_file = None
    if args.dataset:
        dataset_name = args.dataset
        examples = load_prodigy_dataset(args.dataset)
    else:
        source_file = args.input_jsonl.name if args.input_jsonl else None
        examples = list(iter_jsonl(args.input_jsonl))

    rows_by_encounter: dict[str, dict[str, Any]] = {}
    for ex in examples:
        if ex.get("answer") != "accept":
            continue

        text = _normalize_text(ex.get("text") or ex.get("note_text") or ex.get("note"))
        if not text:
            continue

        accepted = _accepted_labels(ex, labels)
        if not accepted and not args.include_empty_accept:
            continue

        accepted_set = set(accepted)
        label_row = {label: int(label in accepted_set) for label in labels}

        meta = ex.get("meta") if isinstance(ex.get("meta"), dict) else {}
        encounter_id = compute_encounter_id(text)

        row: dict[str, Any] = {
            "note_text": text,
            "encounter_id": encounter_id,
            "source_file": meta.get("source_file") or meta.get("source") or source_file,
            "label_source": str(args.label_source),
            "label_confidence": float(args.label_confidence),
            "prodigy_dataset": dataset_name or meta.get("prodigy_dataset") or None,
        }
        row.update(label_row)
        rows_by_encounter[encounter_id] = row  # last write wins

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "note_text",
        "encounter_id",
        "source_file",
        "label_source",
        "label_confidence",
        "prodigy_dataset",
        *labels,
    ]

    rows = list(rows_by_encounter.values())
    with open(args.output_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    if args.output_jsonl:
        args.output_jsonl.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output_jsonl, "w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

    logger.info("Wrote %d rows to %s", len(rows), args.output_csv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```

---
### `scripts/clear_unannotated_prodigy_batch.py`
- Size: `6884` bytes
```
#!/usr/bin/env python3
"""
Remove unannotated examples from Prodigy batch file.

This script checks which examples in the batch file have been annotated in Prodigy
and removes those that haven't been annotated yet, keeping only unannotated examples
or removing all unannotated ones (depending on mode).
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

# Add repo root to path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_BATCH_FILE = Path("data/ml_training/prodigy_batch.jsonl")
DEFAULT_DATASET = "phi_corrections"


def load_prodigy_annotations(dataset_name: str) -> List[Dict[str, Any]]:
    """Load annotations from Prodigy database."""
    try:
        from prodigy.components.db import connect

        db = connect()
        if dataset_name not in db:
            logger.warning(f"Dataset '{dataset_name}' not found in Prodigy database")
            logger.info(f"Available datasets: {db.datasets}")
            return []

        examples = db.get_dataset_examples(dataset_name)
        logger.info(f"Loaded {len(examples)} annotations from Prodigy dataset '{dataset_name}'")
        return examples
    except ImportError:
        logger.error("Prodigy not installed. Install with: pip install prodigy")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to load Prodigy annotations: {e}")
        return []


def get_example_id(example: Dict[str, Any]) -> str:
    """Generate a unique ID for a Prodigy example based on its metadata."""
    meta = example.get("meta", {})
    source = meta.get("source", "unknown")
    record_index = meta.get("record_index", 0)
    window_index = meta.get("window_index", 0)
    return f"{source}:{record_index}:{window_index}"


def load_batch_file(batch_path: Path) -> List[Dict[str, Any]]:
    """Load examples from the batch file."""
    if not batch_path.exists():
        logger.error(f"Batch file not found: {batch_path}")
        sys.exit(1)

    examples = []
    with open(batch_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                example = json.loads(line)
                examples.append(example)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse line: {e}")
                continue

    logger.info(f"Loaded {len(examples)} examples from batch file")
    return examples


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--batch-file",
        type=Path,
        default=DEFAULT_BATCH_FILE,
        help=f"Path to Prodigy batch file (default: {DEFAULT_BATCH_FILE})",
    )
    parser.add_argument(
        "--dataset",
        default=DEFAULT_DATASET,
        help=f"Prodigy dataset name (default: {DEFAULT_DATASET})",
    )
    parser.add_argument(
        "--mode",
        choices=["remove-unannotated", "keep-unannotated"],
        default="remove-unannotated",
        help="Mode: 'remove-unannotated' removes unannotated examples, 'keep-unannotated' keeps only unannotated (default: remove-unannotated)",
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Create a backup of the original batch file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be removed without actually modifying the file",
    )
    args = parser.parse_args()

    # Load batch file
    batch_examples = load_batch_file(args.batch_file)
    if not batch_examples:
        logger.warning("No examples in batch file")
        return 0

    # Load Prodigy annotations
    prodigy_examples = load_prodigy_annotations(args.dataset)
    if not prodigy_examples:
        logger.warning(f"No annotations found in dataset '{args.dataset}'")
        if args.mode == "remove-unannotated":
            logger.info("All examples in batch are unannotated. Nothing to remove.")
        else:
            logger.info("All examples in batch are unannotated. Keeping all.")
        return 0

    # Build set of annotated example IDs
    annotated_ids: Set[str] = set()
    for prodigy_ex in prodigy_examples:
        # Check if this example has been accepted (annotated)
        answer = prodigy_ex.get("answer")
        if answer == "accept":
            example_id = get_example_id(prodigy_ex)
            annotated_ids.add(example_id)
        # Also check by text matching as fallback
        prodigy_text = prodigy_ex.get("text", "")
        if prodigy_text:
            for batch_ex in batch_examples:
                batch_text = batch_ex.get("text", "")
                if batch_text == prodigy_text:
                    batch_id = get_example_id(batch_ex)
                    annotated_ids.add(batch_id)

    logger.info(f"Found {len(annotated_ids)} annotated examples in Prodigy")

    # Filter batch examples
    if args.mode == "remove-unannotated":
        # Remove examples that haven't been annotated
        filtered_examples = []
        for batch_ex in batch_examples:
            batch_id = get_example_id(batch_ex)
            if batch_id in annotated_ids:
                filtered_examples.append(batch_ex)
            else:
                logger.debug(f"Removing unannotated example: {batch_id}")
    else:
        # Keep only unannotated examples
        filtered_examples = []
        for batch_ex in batch_examples:
            batch_id = get_example_id(batch_ex)
            if batch_id not in annotated_ids:
                filtered_examples.append(batch_ex)
            else:
                logger.debug(f"Removing annotated example: {batch_id}")

    removed_count = len(batch_examples) - len(filtered_examples)
    logger.info(f"Would {'remove' if args.mode == 'remove-unannotated' else 'keep'} {removed_count} examples")
    logger.info(f"Would keep {len(filtered_examples)} examples")

    if args.dry_run:
        logger.info("DRY RUN: No changes made to batch file")
        return 0

    # Create backup if requested
    if args.backup:
        backup_path = args.batch_file.with_suffix(f".jsonl.backup")
        logger.info(f"Creating backup: {backup_path}")
        import shutil

        shutil.copy2(args.batch_file, backup_path)

    # Write filtered examples
    logger.info(f"Writing {len(filtered_examples)} examples to {args.batch_file}")
    with open(args.batch_file, "w") as f:
        for ex in filtered_examples:
            f.write(json.dumps(ex) + "\n")

    logger.info(f"✓ Updated batch file: removed {removed_count} examples, kept {len(filtered_examples)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

```

---
### `scripts/merge_registry_human_labels.py`
- Size: `7110` bytes
```
#!/usr/bin/env python3
"""Merge/override relabeled registry human annotations into a base human CSV.

Use case:
- You exported a big "base" human CSV from Prodigy (e.g. registry_human_v1_backup.csv).
- You later re-annotated a subset (e.g. all rigid_bronchoscopy cases) in a *new* Prodigy dataset
  and exported that subset to another CSV.
- You want the subset to **override** the base labels for matching encounter_id rows.

Behavior:
- Matches rows by `encounter_id` (required in both CSVs).
- Overwrites ONLY the canonical registry label columns (REGISTRY_LABELS).
- Adds any missing label columns to the base output (e.g. newly introduced labels).
- Preserves non-label columns from the base row (note_text/source_file/etc) by default.
- Optionally can override `prodigy_dataset`, `label_source`, `label_confidence` from the updates file.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from modules.ml_coder.registry_label_schema import REGISTRY_LABELS, compute_encounter_id
from modules.ml_coder.registry_label_constraints import apply_label_constraints


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base-csv", type=Path, required=True, help="Base human labels CSV")
    p.add_argument("--updates-csv", type=Path, required=True, help="Updates (relabel) CSV")
    p.add_argument("--out-csv", type=Path, required=True, help="Output merged CSV")
    p.add_argument(
        "--prefer-updates-meta",
        action="store_true",
        help="Also prefer updates meta columns when present (prodigy_dataset, label_source, label_confidence).",
    )
    return p.parse_args(argv)


def _ensure_cols(df: pd.DataFrame, cols: list[str], default: int = 0) -> pd.DataFrame:
    for c in cols:
        if c not in df.columns:
            df[c] = default
    return df


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Be tolerant of messy headers (Excel exports often pad columns with spaces).
    df.columns = [str(c).strip().lstrip("\ufeff") for c in df.columns]
    return df


def _ensure_encounter_id(df: pd.DataFrame, *, name: str) -> pd.DataFrame:
    """
    Ensure an encounter_id column exists.

    - If missing but note_text exists, compute encounter_id from note_text.
    - If present but empty for some rows, fill those rows from note_text.
    """
    if "encounter_id" not in df.columns:
        if "note_text" not in df.columns:
            raise SystemExit(f"{name} CSV missing required column: encounter_id (and no note_text to compute it)")
        df["encounter_id"] = df["note_text"].fillna("").astype(str).map(lambda t: compute_encounter_id(t.strip()))
        return df

    # Normalize encounter_id values (trim whitespace/CRLF artifacts)
    df["encounter_id"] = df["encounter_id"].fillna("").astype(str).str.strip()

    # Fill missing/blank encounter_id values (best-effort)
    if "note_text" in df.columns:
        mask = df["encounter_id"].isna() | (df["encounter_id"].astype(str).str.strip() == "")
        if mask.any():
            df.loc[mask, "encounter_id"] = (
                df.loc[mask, "note_text"].fillna("").astype(str).map(lambda t: compute_encounter_id(t.strip()))
            )
    return df


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.base_csv.exists():
        raise SystemExit(f"Base CSV not found: {args.base_csv}")
    if not args.updates_csv.exists():
        raise SystemExit(f"Updates CSV not found: {args.updates_csv}")

    base = _normalize_columns(pd.read_csv(args.base_csv))
    updates = _normalize_columns(pd.read_csv(args.updates_csv))

    base = _ensure_encounter_id(base, name="base")
    updates = _ensure_encounter_id(updates, name="updates")

    # Ensure canonical label columns exist in both
    labels = list(REGISTRY_LABELS)
    base = _ensure_cols(base, labels, default=0)
    updates = _ensure_cols(updates, labels, default=0)

    # Deduplicate updates by encounter_id (keep last row)
    updates = updates.drop_duplicates(subset=["encounter_id"], keep="last")

    base_idx = base.set_index("encounter_id", drop=False)
    updates_idx = updates.set_index("encounter_id", drop=False)

    overlap = base_idx.index.intersection(updates_idx.index)
    new_only = updates_idx.index.difference(base_idx.index)

    # Overwrite label columns for overlapping rows
    if len(overlap) > 0:
        base_idx.loc[overlap, labels] = updates_idx.loc[overlap, labels].values

    # Optionally override a few meta fields if present in updates
    if args.prefer_updates_meta:
        for meta_col in ["prodigy_dataset", "label_source", "label_confidence"]:
            if meta_col in updates_idx.columns and meta_col in base_idx.columns:
                if len(overlap) > 0:
                    base_idx.loc[overlap, meta_col] = updates_idx.loc[overlap, meta_col]

    # Append brand-new encounter_ids from updates (common when you annotated a new batch/dataset)
    if len(new_only) > 0:
        # Ensure any updates-only columns exist on base (pandas will align on concat, but
        # we want to preserve them rather than drop them).
        to_append = updates_idx.loc[new_only].copy()
        out_idx = pd.concat([base_idx, to_append], axis=0, ignore_index=False)
    else:
        out_idx = base_idx

    # If any duplicates exist (shouldn't, but be defensive), keep the last occurrence.
    out = out_idx.reset_index(drop=True).drop_duplicates(subset=["encounter_id"], keep="last")

    if "note_text" in out.columns:
        # Apply deterministic constraints post-merge to keep human data normalized.
        if "transbronchial_cryobiopsy" in out.columns and "transbronchial_biopsy" in out.columns:
            out.loc[out["transbronchial_cryobiopsy"].astype(int) == 1, "transbronchial_biopsy"] = 1
        if "bal" in out.columns and "bronchial_wash" in out.columns:
            mask = (out["bal"].astype(int) == 1) & (out["bronchial_wash"].astype(int) == 1)
            for idx in out.index[mask]:
                row = {
                    "note_text": str(out.at[idx, "note_text"] or ""),
                    "bal": int(out.at[idx, "bal"]),
                    "bronchial_wash": int(out.at[idx, "bronchial_wash"]),
                }
                apply_label_constraints(row)
                out.at[idx, "bal"] = int(row["bal"])
                out.at[idx, "bronchial_wash"] = int(row["bronchial_wash"])

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.out_csv, index=False)

    print("Merged updates into base by encounter_id.")
    print(f"Base rows: {len(base)}")
    print(f"Updates rows (deduped): {len(updates)}")
    print(f"Overridden rows (existing encounter_id): {len(overlap)}")
    print(f"Appended rows (new encounter_id): {len(new_only)}")
    print(f"Output: {args.out_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```

---
### `scripts/create_slim_branch.py`
- Size: `7169` bytes
```
#!/usr/bin/env python3
"""
Create a slim Git branch for external review, excluding large files.

This script creates an orphan branch with only essential files for code review,
excluding ML models, training data, archives, and other large artifacts.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Directories to exclude
EXCLUDED_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "node_modules",
    "data/knowledge",
    "data",
    "data/models",
    "data/ml_training",
    "scripts/phi_test_node",
    "artifacts",
    "archive",
    "dist",
    "proc_suite.egg-info",
    "reports",
    "validation_results",
}

# File extensions to exclude
EXCLUDED_EXTENSIONS = {
    ".bin",
    ".db",
    ".onnx",
    ".pt",
    ".pth",
    ".safetensors",
    ".h5",
    ".ckpt",
    ".pkl",
    ".joblib",
    ".pb",
    ".tflite",
    ".mlmodel",
    ".tar",
    ".tar.gz",
    ".tar.bz2",
    ".tar.xz",
    ".tgz",
    ".zip",
    ".rar",
    ".7z",
    ".gz",
    ".bz2",
    ".xz",
    ".jsonl",  # Training data files
    ".pyc",
    ".pyo",
}

# File patterns to exclude (by filename)
EXCLUDED_PATTERNS = {
    "classifier.pt",
    "classifier.pkl",
    "mlb.pkl",
    "tokenizer.json",
    "model.safetensors",
    "pytorch_model.bin",
    "model.pt",
    "model.pth",
}

# Directories to keep (even if parent is excluded)
KEEP_DIRS = {
    "docs",
    "modules",
    "scripts",
    "tests",
    "schemas",
    "configs",
}


def is_archive_file(filename: str) -> bool:
    """Check if a file is an archive by name."""
    archive_names = {
        "archive",
        "backup",
        "old",
        "temp",
        "tmp",
    }
    name_lower = filename.lower()
    return any(archive_name in name_lower for archive_name in archive_names)


def should_exclude_path(path: Path, repo_root: Path) -> bool:
    """Check if a path should be excluded from the slim branch."""
    try:
        rel_path = path.relative_to(repo_root)
    except ValueError:
        return True

    # Check if any part of the path matches excluded dirs
    parts = rel_path.parts
    for part in parts:
        if part in EXCLUDED_DIRS:
            # Check if this is a keep directory
            if any(keep_dir in parts for keep_dir in KEEP_DIRS):
                # If it's a keep dir, only exclude if the excluded part comes after
                keep_indices = [i for i, p in enumerate(parts) if p in KEEP_DIRS]
                exclude_index = next((i for i, p in enumerate(parts) if p in EXCLUDED_DIRS), None)
                if exclude_index is not None and keep_indices:
                    if min(keep_indices) < exclude_index:
                        continue  # Keep this path
            return True

    # Check file extension
    if path.is_file():
        for ext in EXCLUDED_EXTENSIONS:
            if str(path).endswith(ext):
                return True

        # Check filename patterns
        if path.name in EXCLUDED_PATTERNS:
            return True

        # Check for archive files by name
        if is_archive_file(path.name):
            return True

        # Exclude large JSON files (>5MB)
        if path.suffix == ".json":
            try:
                size_mb = path.stat().st_size / (1024 * 1024)
                if size_mb > 5:
                    return True
            except (OSError, ValueError):
                pass

    return False


def run_git_command(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a git command and return the result."""
    result = subprocess.run(
        ["git"] + cmd,
        capture_output=True,
        text=True,
        check=check,
    )
    return result


def create_slim_branch(source_branch: str, target_branch: str, force: bool = False) -> None:
    """Create a slim branch from the source branch."""
    repo_root = Path.cwd()

    # Check if we're in a git repo
    if not (repo_root / ".git").exists():
        print("Error: Not in a git repository")
        sys.exit(1)

    # Check if target branch exists
    result = run_git_command(["branch", "--list", target_branch], check=False)
    if result.stdout.strip() and not force:
        print(f"Error: Branch '{target_branch}' already exists. Use --force to overwrite.")
        sys.exit(1)

    # Get current branch
    current_branch_result = run_git_command(["rev-parse", "--abbrev-ref", "HEAD"])
    current_branch = current_branch_result.stdout.strip()

    print(f"Creating slim branch '{target_branch}' from '{source_branch}'...")

    # Checkout source branch first
    print(f"Checking out source branch '{source_branch}'...")
    run_git_command(["checkout", source_branch])

    # Delete target branch if it exists and force is set
    if force:
        run_git_command(["branch", "-D", target_branch], check=False)

    # Create orphan branch
    print(f"Creating orphan branch '{target_branch}'...")
    run_git_command(["checkout", "--orphan", target_branch])

    # Remove all files from staging
    print("Removing all files from staging...")
    run_git_command(["rm", "-rf", "--cached", "."], check=False)

    # Add files that should be included
    print("Adding files to slim branch...")
    added_count = 0
    skipped_count = 0

    # Get all files from source branch
    result = run_git_command(["ls-tree", "-r", "--name-only", source_branch])
    files = result.stdout.strip().split("\n") if result.stdout.strip() else []

    for file_path_str in files:
        if not file_path_str:
            continue

        file_path = repo_root / file_path_str

        if should_exclude_path(file_path, repo_root):
            skipped_count += 1
            continue

        # Check if file exists (it should, since we're on the source branch)
        if file_path.exists():
            try:
                run_git_command(["add", file_path_str])
                added_count += 1
            except subprocess.CalledProcessError:
                skipped_count += 1

    print(f"\nAdded {added_count} files, skipped {skipped_count} files")

    # Commit
    print("Committing slim branch...")
    run_git_command(
        ["commit", "-m", f"Create slim branch from {source_branch} for external review"]
    )

    print(f"\n✓ Slim branch '{target_branch}' created successfully!")
    print(f"  To push to remote: git push -f origin {target_branch}")
    print(f"  To return to previous branch: git checkout {current_branch}")


def main():
    parser = argparse.ArgumentParser(
        description="Create a slim Git branch for external review"
    )
    parser.add_argument(
        "--source",
        default="v19",
        help="Source branch to create slim branch from (default: v19)",
    )
    parser.add_argument(
        "--target",
        default="slim-review",
        help="Target branch name (default: slim-review)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force overwrite if target branch exists",
    )
    args = parser.parse_args()

    create_slim_branch(args.source, args.target, args.force)


if __name__ == "__main__":
    main()

```

---
### `scripts/generate_teacher_logits.py`
- Size: `7302` bytes
```
#!/usr/bin/env python3
"""Generate teacher logits for distillation from a trained registry model."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn as nn
from tqdm import tqdm
from transformers import AutoModel, AutoTokenizer

from modules.ml_coder.distillation_io import load_label_fields_json
from modules.ml_coder.registry_label_schema import compute_encounter_id


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _pick_text(obj: dict[str, Any]) -> str:
    return str(obj.get("note_text") or obj.get("text") or obj.get("note") or obj.get("raw_text") or "").strip()


def _pick_id(obj: dict[str, Any], text: str) -> str:
    for key in ("encounter_id", "id", "note_id"):
        value = obj.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return compute_encounter_id(text)


def iter_jsonl(path: Path):
    with open(path, encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict):
                yield line_num, obj


def encode_head_tail(
    tokenizer,
    texts: list[str],
    *,
    max_length: int,
    head_tokens: int,
    tail_tokens: int,
) -> dict[str, torch.Tensor]:
    cls_id = int(tokenizer.cls_token_id)
    sep_id = int(tokenizer.sep_token_id)
    pad_id = int(tokenizer.pad_token_id)
    content_max = max_length - 2

    batch_ids: list[list[int]] = []
    for text in texts:
        ids = tokenizer(text, add_special_tokens=False, truncation=False)["input_ids"]
        if len(ids) > content_max:
            ids = ids[:head_tokens] + ids[-tail_tokens:]
        full = [cls_id] + ids + [sep_id]
        if len(full) < max_length:
            full = full + [pad_id] * (max_length - len(full))
        else:
            full = full[:max_length]
        batch_ids.append(full)

    input_ids = torch.tensor(batch_ids, dtype=torch.long)
    attention_mask = (input_ids != pad_id).long()
    return {"input_ids": input_ids, "attention_mask": attention_mask}


class TeacherModel(nn.Module):
    def __init__(self, model_dir: Path, num_labels: int) -> None:
        super().__init__()
        self.base = AutoModel.from_pretrained(str(model_dir))
        self.dropout = nn.Dropout(0.1)
        self.classifier = nn.Linear(self.base.config.hidden_size, num_labels)
        state = torch.load(model_dir / "classifier.pt", map_location="cpu")
        self.classifier.load_state_dict(state)

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        out = self.base(input_ids=input_ids, attention_mask=attention_mask)
        pooled = self.dropout(out.last_hidden_state[:, 0, :])
        return self.classifier(pooled)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model-dir", type=Path, required=True, help="Teacher model directory")
    p.add_argument("--input-jsonl", type=Path, required=True, help="JSONL with note text + IDs")
    p.add_argument(
        "--label-fields",
        type=Path,
        default=None,
        help="Ordered label list JSON (default: <model-dir>/label_fields.json)",
    )
    p.add_argument("--out", type=Path, required=True, help="Output .npz path")
    p.add_argument(
        "--meta-out",
        type=Path,
        default=None,
        help="Optional meta JSON sidecar (default: alongside --out)",
    )
    p.add_argument("--batch-size", type=int, default=32)
    p.add_argument("--max-length", type=int, default=512)
    p.add_argument("--head-tokens", type=int, default=382)
    p.add_argument("--tail-tokens", type=int, default=128)
    p.add_argument("--dtype", choices=["float16", "float32"], default="float16")
    p.add_argument("--device", type=str, default=None, help="cuda|cpu (default: auto)")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    model_dir = args.model_dir
    if not model_dir.exists():
        raise SystemExit(f"Model dir not found: {model_dir}")

    label_fields_path = args.label_fields or (model_dir / "label_fields.json")
    label_fields = load_label_fields_json(label_fields_path)

    classifier_path = model_dir / "classifier.pt"
    if not classifier_path.exists():
        raise SystemExit(f"Missing classifier weights: {classifier_path}")

    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")

    tokenizer_dir = model_dir / "tokenizer"
    tokenizer = AutoTokenizer.from_pretrained(str(tokenizer_dir if tokenizer_dir.exists() else model_dir))

    model = TeacherModel(model_dir=model_dir, num_labels=len(label_fields))
    model.to(device)
    model.eval()

    ids: list[str] = []
    logits_chunks: list[np.ndarray] = []

    batch_texts: list[str] = []
    batch_ids: list[str] = []

    def flush():
        if not batch_texts:
            return
        enc = encode_head_tail(
            tokenizer,
            batch_texts,
            max_length=int(args.max_length),
            head_tokens=int(args.head_tokens),
            tail_tokens=int(args.tail_tokens),
        )
        with torch.no_grad():
            batch_logits = model(enc["input_ids"].to(device), enc["attention_mask"].to(device))
        logits_chunks.append(batch_logits.detach().cpu().numpy())
        ids.extend(batch_ids)
        batch_texts.clear()
        batch_ids.clear()

    for _line_num, obj in tqdm(iter_jsonl(args.input_jsonl), desc="Reading notes"):
        text = _pick_text(obj)
        if not text:
            continue
        eid = _pick_id(obj, text)
        batch_texts.append(text)
        batch_ids.append(eid)
        if len(batch_texts) >= int(args.batch_size):
            flush()

    flush()

    if not ids:
        raise SystemExit("No valid notes found in input JSONL.")

    logits = np.vstack(logits_chunks)
    if args.dtype == "float16":
        logits = logits.astype(np.float16)
    else:
        logits = logits.astype(np.float32)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(args.out, ids=np.array(ids), logits=logits, label_fields=np.array(label_fields))

    meta_out = args.meta_out or args.out.with_name("teacher_logits_meta.json")
    meta = {
        "model_dir": str(model_dir),
        "classifier_sha256": _sha256_file(classifier_path)[:16],
        "label_fields_sha256": _sha256_file(Path(label_fields_path))[:16],
        "n": int(logits.shape[0]),
        "l": int(logits.shape[1]),
        "dtype": str(logits.dtype),
        "input_jsonl": str(args.input_jsonl),
    }
    meta_out.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote logits: {args.out} (N={logits.shape[0]}, L={logits.shape[1]})")
    print(f"Wrote meta: {meta_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```

---
### `scripts/regenerate_granular_ner_stats.py`
- Size: `7609` bytes
```
#!/usr/bin/env python3
"""
Regenerate data/ml_training/granular_ner/stats.json from current JSONL artifacts.

Inputs (all under --base-dir, default: data/ml_training/granular_ner):
  - ner_dataset_all.jsonl  (required) (records: {"id","text","entities":[{"start","end","label","text"}] ...})
  - spans.jsonl            (optional) (records: {"note_id","label","span_text","start_char","end_char","hydration_status"})

Outputs:
  - stats.json (same top-level shape as extract_ner_from_excel.py stats)

This is useful when stats.json becomes stale/out-of-sync after manual edits,
reruns, de-duplication, or incremental appends.

Important:
- Alignment stats + label_counts are recomputed from ner_dataset_all.jsonl
  (the actual training file).
- hydration_status_counts (if present) is computed from spans.jsonl only.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


def _normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


def _get_offset(ent: dict, start_key: str, end_key: str) -> tuple[int | None, int | None]:
    start = ent.get(start_key)
    end = ent.get(end_key)
    if start is None and start_key == "start":
        start = ent.get("start_char", ent.get("start_offset"))
    if end is None and end_key == "end":
        end = ent.get("end_char", ent.get("end_offset"))

    try:
        start_i = int(start)
        end_i = int(end)
    except (TypeError, ValueError):
        return None, None
    return start_i, end_i


@dataclass
class Stats:
    total_files: int = 0
    successful_files: int = 0
    total_notes: int = 0
    total_spans_raw: int = 0
    total_spans_valid: int = 0
    alignment_warnings: int = 0
    alignment_errors: int = 0
    label_counts: Counter | None = None
    hydration_status_counts: Counter | None = None
    duplicate_note_ids: int = 0

    def to_jsonable(self) -> dict:
        return {
            "total_files": self.total_files,
            "successful_files": self.successful_files,
            "total_notes": self.total_notes,
            "total_spans_raw": self.total_spans_raw,
            "total_spans_valid": self.total_spans_valid,
            "alignment_warnings": self.alignment_warnings,
            "alignment_errors": self.alignment_errors,
            "label_counts": dict((self.label_counts or Counter()).most_common()),
            "hydration_status_counts": dict(self.hydration_status_counts or Counter()),
            "duplicate_note_ids": self.duplicate_note_ids,
        }


def _iter_jsonl(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                yield line_num, json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in {path} at line {line_num}: {e}") from e


def regenerate(base_dir: Path) -> tuple[Stats, list[str]]:
    ner_path = base_dir / "ner_dataset_all.jsonl"
    spans_path = base_dir / "spans.jsonl"

    if not ner_path.exists():
        raise FileNotFoundError(f"Missing required file: {ner_path}")

    stats = Stats(label_counts=Counter(), hydration_status_counts=Counter())

    # --- Records / "files" ---
    seen_ids: set[str] = set()
    dup_ids: set[str] = set()
    record_ids: list[str] = []
    success_ids: set[str] = set()

    for _, rec in _iter_jsonl(ner_path):
        rid = rec.get("id") or rec.get("note_id")
        if not rid:
            continue
        rid = str(rid)
        record_ids.append(rid)
        if rid in seen_ids:
            dup_ids.add(rid)
        else:
            seen_ids.add(rid)

        text = rec.get("text") or ""
        entities = rec.get("entities") or rec.get("spans") or []
        if isinstance(entities, list) and len(entities) > 0:
            success_ids.add(rid)

        # Validate entities (alignment + label counts) against the record text.
        if not isinstance(text, str):
            text = str(text)

        if not isinstance(entities, list):
            stats.alignment_errors += 1
            continue

        for ent in entities:
            stats.total_spans_raw += 1

            # Support both dict entities and list-style [start,end,label] / [start,end,label,text]
            if isinstance(ent, dict):
                start_i, end_i = _get_offset(ent, "start", "end")
                label = ent.get("label")
                expected = ent.get("text", ent.get("span_text"))
            elif isinstance(ent, (list, tuple)) and len(ent) >= 3:
                start_i, end_i, label = ent[0], ent[1], ent[2]
                expected = ent[3] if len(ent) >= 4 else None
            else:
                stats.alignment_errors += 1
                continue

            try:
                start_i = int(start_i)
                end_i = int(end_i)
            except (TypeError, ValueError):
                stats.alignment_errors += 1
                continue

            if start_i < 0 or end_i < 0 or end_i > len(text) or start_i > end_i:
                stats.alignment_errors += 1
                continue

            extracted = text[start_i:end_i]
            if expected is None:
                # If no expected text was provided, treat as valid offsets-only.
                stats.total_spans_valid += 1
                stats.label_counts[str(label or "")] += 1
                continue

            expected_s = str(expected)
            if extracted == expected_s:
                stats.total_spans_valid += 1
                stats.label_counts[str(label or "")] += 1
                continue

            if _normalize_whitespace(extracted) == _normalize_whitespace(expected_s):
                stats.alignment_warnings += 1
                stats.total_spans_valid += 1
                stats.label_counts[str(label or "")] += 1
                continue

            stats.alignment_errors += 1

    stats.total_files = len(seen_ids)
    stats.total_notes = len(seen_ids)
    stats.successful_files = len(success_ids)
    stats.duplicate_note_ids = len(dup_ids)

    # --- Optional hydration status counts (from spans.jsonl) ---
    if spans_path.exists():
        for _, span in _iter_jsonl(spans_path):
            hydration = span.get("hydration_status")
            if hydration:
                stats.hydration_status_counts[str(hydration)] += 1

    # Return duplicate IDs for convenience
    dup_list = sorted(list(dup_ids))
    return stats, dup_list


def main() -> int:
    parser = argparse.ArgumentParser(description="Regenerate granular_ner stats.json from JSONL files")
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=Path("data/ml_training/granular_ner"),
        help="Directory containing ner_dataset_all.jsonl / notes.jsonl / spans.jsonl",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write stats.json (default: print only).",
    )
    args = parser.parse_args()

    stats, dup_ids = regenerate(args.base_dir)
    payload = stats.to_jsonable()

    print(json.dumps(payload, indent=2))
    if dup_ids:
        print("\nDuplicate note IDs detected:")
        for nid in dup_ids:
            print(f" - {nid}")

    if args.write:
        out_path = args.base_dir / "stats.json"
        out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"\nWrote: {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```

---
### `scripts/code_validation.py`
- Size: `7735` bytes
```
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable, Set, Tuple, Dict


# Matches:
#   - CPT: 5 digits (e.g., 31622)
#   - HCPCS Level II: Letter + 4 digits (e.g., C1601, J7665)
#   - Optional leading "+" used in this JSON to denote add-on codes (e.g., +31627)
CODE_RE = re.compile(r"^\+?(?:\d{5}|[A-Z]\d{4})$")


def normalize_code(code: str, *, keep_addon_plus: bool) -> str:
    code = code.strip().upper()
    return code if keep_addon_plus else code.lstrip("+")


def extract_codes_anywhere(obj: Any) -> Set[str]:
    """
    Recursively traverse a JSON-like structure and collect any strings/keys
    that look like CPT/HCPCS codes (including optional leading '+').
    """
    found: Set[str] = set()

    def walk(x: Any) -> None:
        if x is None:
            return
        if isinstance(x, str):
            s = x.strip().upper()
            if CODE_RE.match(s):
                found.add(s)
            return
        if isinstance(x, (int, float)):
            # Codes should be strings, but guard just in case
            s = str(int(x)).strip()
            if CODE_RE.match(s):
                found.add(s)
            return
        if isinstance(x, list):
            for item in x:
                walk(item)
            return
        if isinstance(x, dict):
            for k, v in x.items():
                # Keys can be codes too
                if isinstance(k, str):
                    ks = k.strip().upper()
                    if CODE_RE.match(ks):
                        found.add(ks)
                walk(v)
            return

    walk(obj)
    return found


def _codes_from_dict_keys(d: Any) -> Set[str]:
    if not isinstance(d, dict):
        return set()
    out = set()
    for k in d.keys():
        if isinstance(k, str):
            ks = k.strip().upper()
            if CODE_RE.match(ks):
                out.add(ks)
    return out


def collect_billable_codes(data: dict) -> Set[str]:
    """
    Collect codes that are intended to be "real" billable / selectable codes
    in this knowledge base (vs codes that show up only in references/logic).
    """
    billable: Set[str] = set()

    # 1) code_lists (explicit curated lists)
    code_lists = data.get("code_lists", {})
    if isinstance(code_lists, dict):
        for _, codes in code_lists.items():
            if isinstance(codes, list):
                for c in codes:
                    if isinstance(c, str) and CODE_RE.match(c.strip().upper()):
                        billable.add(c.strip().upper())

    # 2) add_on_codes list (explicit)
    add_on_codes = data.get("add_on_codes", [])
    if isinstance(add_on_codes, list):
        for c in add_on_codes:
            if isinstance(c, str) and CODE_RE.match(c.strip().upper()):
                billable.add(c.strip().upper())

    # 3) fee_schedules.*.codes (keys are CPT/HCPCS; include + add-ons)
    fee_schedules = data.get("fee_schedules", {})
    if isinstance(fee_schedules, dict):
        for _, sched in fee_schedules.items():
            if isinstance(sched, dict):
                billable |= _codes_from_dict_keys(sched.get("codes", {}))

    # 4) cms_rvus sections (bronchoscopy/pleural/thoracoscopy/sedation/em/imaging)
    cms_rvus = data.get("cms_rvus", {})
    if isinstance(cms_rvus, dict):
        for section_name, section in cms_rvus.items():
            if isinstance(section_name, str) and section_name.startswith("_"):
                continue
            billable |= _codes_from_dict_keys(section)

    # 5) simplified RVU tables
    billable |= _codes_from_dict_keys(data.get("rvus", {}))
    billable |= _codes_from_dict_keys(data.get("rvus_pleural", {}))
    billable |= _codes_from_dict_keys(data.get("rvus_sedation_em", {}))

    # 6) hcpcs top-level keys (HCPCS Level II device/drug codes; alphanumeric only)
    billable |= _codes_from_dict_keys(data.get("hcpcs", {}))

    # 7) pleural cpt maps (redundant but harmless; helps if future versions omit other sections)
    pleural = data.get("pleural", {})
    if isinstance(pleural, dict):
        billable |= _codes_from_dict_keys(pleural.get("cpt_map", {}))
        billable |= _codes_from_dict_keys(pleural.get("thoracoscopy_cpt_map", {}))

    return billable


def build_valid_ip_codes(
    json_path: str | Path,
    *,
    keep_addon_plus: bool = False,
    include_reference_codes: bool = False,
) -> Tuple[Set[str], Dict[str, Set[str]]]:
    """
    Returns:
      - valid_codes: the final normalized code set
      - debug: a dict with useful intermediate sets
    """
    json_path = Path(json_path)

    data = json.loads(json_path.read_text(encoding="utf-8"))

    codes_anywhere = extract_codes_anywhere(data)
    codes_billable = collect_billable_codes(data)

    # "reference-only" are codes referenced somewhere (e.g., NCCI pairs) but not in billable lists
    codes_reference_only = codes_anywhere - codes_billable

    selected = set(codes_billable)
    if include_reference_codes:
        selected |= codes_reference_only

    normalized = {normalize_code(c, keep_addon_plus=keep_addon_plus) for c in selected}

    debug = {
        "codes_anywhere_raw": codes_anywhere,
        "codes_billable_raw": codes_billable,
        "codes_reference_only_raw": codes_reference_only,
    }
    return normalized, debug


def format_as_python_set(codes: Iterable[str], cols: int = 10) -> str:
    codes_sorted = sorted(set(codes))
    chunks = [codes_sorted[i : i + cols] for i in range(0, len(codes_sorted), cols)]
    lines = []
    for chunk in chunks:
        lines.append("    " + ", ".join(f'"{c}"' for c in chunk) + ",")
    return "VALID_IP_CODES = {\n" + "\n".join(lines) + "\n}"


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Build VALID_IP_CODES set from knowledge base")
    parser.add_argument(
        "--kb-path",
        type=Path,
        default=Path("data/knowledge/ip_coding_billing_v3_0.json"),
        help="Path to knowledge base JSON file (default: data/knowledge/ip_coding_billing_v3_0.json)",
    )
    parser.add_argument(
        "--keep-addon-plus",
        action="store_true",
        help="Keep '+' prefix on add-on codes",
    )
    parser.add_argument(
        "--include-reference-codes",
        action="store_true",
        help="Include reference-only codes (e.g., NCCI-only codes like 32100)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file path (default: print to stdout)",
    )
    args = parser.parse_args()

    if not args.kb_path.exists():
        print(f"Error: Knowledge base file not found: {args.kb_path}")
        print(f"Please ensure the file exists or specify with --kb-path")
        exit(1)

    # Recommended: normalize add-on "+", and DO NOT include reference-only codes (e.g., 32100)
    valid_codes, dbg = build_valid_ip_codes(
        args.kb_path,
        keep_addon_plus=args.keep_addon_plus,
        include_reference_codes=args.include_reference_codes,
    )

    output_text = f"# Generated from {args.kb_path}\n"
    output_text += f"# Total codes: {len(valid_codes)}\n"
    output_text += format_as_python_set(valid_codes)

    if args.output:
        args.output.write_text(output_text, encoding="utf-8")
        print(f"✓ Wrote {len(valid_codes)} codes to {args.output}")
    else:
        print(f"Built {len(valid_codes)} codes")
        print(output_text)

    # If you want to see logic-only references (e.g., NCCI-only codes like 32100):
    # valid_with_refs, dbg2 = build_valid_ip_codes(args.kb_path, keep_addon_plus=False, include_reference_codes=True)
    # print("Reference-only codes:", sorted(dbg2["codes_reference_only_raw"]))

```

---
### `scripts/dedupe_granular_ner.py`
- Size: `7803` bytes
```
#!/usr/bin/env python3
"""
Dedupe granular NER training artifacts in-place (or to new files).

This repo's NER artifacts are sometimes generated via append-only scripts,
which can leave duplicate note IDs (same `id` appearing multiple times across
`ner_dataset_all.jsonl`, `notes.jsonl`, and derived BIO files).

Default behavior:
- chooses the "best" record per note_id (max entities, then text length, then last)
- writes deduped files next to originals unless `--write` is passed
- optionally creates timestamped backups (enabled by default for `--write`)
"""

from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


def _iter_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in {path} at line {line_num}: {e}") from e
            if not isinstance(obj, dict):
                continue
            yield obj


def _write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n += 1
    return n


def _stable_key(obj: dict[str, Any]) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _note_id_from_record(rec: dict[str, Any]) -> str | None:
    rid = rec.get("id") or rec.get("note_id")
    return str(rid) if rid is not None else None


@dataclass(frozen=True)
class _Candidate:
    idx: int
    rec: dict[str, Any]

    @property
    def note_id(self) -> str:
        rid = _note_id_from_record(self.rec)
        if rid is None:
            raise ValueError("record missing id/note_id")
        return rid

    @property
    def text(self) -> str:
        t = self.rec.get("text", self.rec.get("note_text", ""))
        return t if isinstance(t, str) else str(t)

    @property
    def entities_count(self) -> int:
        ents = self.rec.get("entities")
        return len(ents) if isinstance(ents, list) else 0


def _pick_best(cands: list[_Candidate], strategy: str) -> _Candidate:
    if not cands:
        raise ValueError("no candidates")

    if strategy == "last":
        return max(cands, key=lambda c: c.idx)
    if strategy == "max_text":
        return max(cands, key=lambda c: (len(c.text), c.entities_count, c.idx))
    if strategy == "max_entities":
        return max(cands, key=lambda c: (c.entities_count, len(c.text), c.idx))
    raise ValueError(f"Unknown strategy: {strategy}")


def dedupe_ner_dataset(in_path: Path, out_path: Path, *, strategy: str) -> tuple[int, int, set[str]]:
    by_id: dict[str, list[_Candidate]] = {}
    first_idx: dict[str, int] = {}

    for idx, rec in enumerate(_iter_jsonl(in_path), 1):
        rid = _note_id_from_record(rec)
        if not rid:
            continue
        first_idx.setdefault(rid, idx)
        by_id.setdefault(rid, []).append(_Candidate(idx=idx, rec=rec))

    kept: dict[str, _Candidate] = {}
    for rid, cands in by_id.items():
        kept[rid] = _pick_best(cands, strategy)

    ordered_ids = sorted(kept.keys(), key=lambda rid: first_idx.get(rid, 0))
    records = [kept[rid].rec for rid in ordered_ids]
    written = _write_jsonl(out_path, records)
    return sum(len(v) for v in by_id.values()), written, set(ordered_ids)


def dedupe_notes(in_path: Path, out_path: Path, *, keep_ids: set[str], strategy: str) -> tuple[int, int]:
    by_id: dict[str, list[_Candidate]] = {}
    first_idx: dict[str, int] = {}
    for idx, rec in enumerate(_iter_jsonl(in_path), 1):
        rid = _note_id_from_record(rec)
        if not rid or rid not in keep_ids:
            continue
        first_idx.setdefault(rid, idx)
        by_id.setdefault(rid, []).append(_Candidate(idx=idx, rec=rec))

    kept: dict[str, _Candidate] = {}
    for rid, cands in by_id.items():
        kept[rid] = _pick_best(cands, strategy)

    ordered_ids = sorted(kept.keys(), key=lambda rid: first_idx.get(rid, 0))
    records = [kept[rid].rec for rid in ordered_ids]
    written = _write_jsonl(out_path, records)
    return sum(len(v) for v in by_id.values()), written


def dedupe_spans(in_path: Path, out_path: Path, *, keep_ids: set[str]) -> tuple[int, int]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    total = 0

    for rec in _iter_jsonl(in_path):
        total += 1
        note_id = rec.get("note_id")
        if note_id is None or str(note_id) not in keep_ids:
            continue
        key = _stable_key(rec)
        if key in seen:
            continue
        seen.add(key)
        out.append(rec)

    written = _write_jsonl(out_path, out)
    return total, written


def _backup(paths: list[Path], backup_dir: Path) -> None:
    backup_dir.mkdir(parents=True, exist_ok=True)
    for p in paths:
        if p.exists():
            shutil.copy2(p, backup_dir / p.name)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--base-dir",
        type=Path,
        default=Path("data/ml_training/granular_ner"),
        help="Directory containing granular NER artifacts (default: data/ml_training/granular_ner).",
    )
    ap.add_argument(
        "--strategy",
        choices=["max_entities", "last", "max_text"],
        default="max_entities",
        help="How to pick which duplicate record to keep (default: max_entities).",
    )
    ap.add_argument(
        "--write",
        action="store_true",
        help="Overwrite existing files (default: write *.deduped.jsonl next to originals).",
    )
    ap.add_argument(
        "--no-backup",
        action="store_true",
        help="Disable backups when using --write.",
    )
    args = ap.parse_args()

    base: Path = args.base_dir
    ner_in = base / "ner_dataset_all.jsonl"
    notes_in = base / "notes.jsonl"
    spans_in = base / "spans.jsonl"

    if not ner_in.exists():
        raise SystemExit(f"Missing: {ner_in}")

    suffix = "" if args.write else ".deduped"
    ner_out = base / f"ner_dataset_all{suffix}.jsonl"
    notes_out = base / f"notes{suffix}.jsonl" if notes_in.exists() else None
    spans_out = base / f"spans{suffix}.jsonl" if spans_in.exists() else None

    # Backups (only relevant for in-place overwrites).
    if args.write and not args.no_backup:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup_dir = base / f"_backup_{stamp}"
        _backup([ner_in, notes_in, spans_in], backup_dir)
        print(f"Backed up originals to: {backup_dir}")

    total_in, total_out, keep_ids = dedupe_ner_dataset(ner_in, ner_out, strategy=args.strategy)
    print(f"ner_dataset_all: {total_in} -> {total_out} records ({total_in - total_out} removed)")

    if notes_in.exists() and notes_out is not None:
        notes_in_count, notes_out_count = dedupe_notes(
            notes_in, notes_out, keep_ids=keep_ids, strategy=args.strategy
        )
        print(f"notes: {notes_in_count} -> {notes_out_count} records ({notes_in_count - notes_out_count} removed)")

    if spans_in.exists() and spans_out is not None:
        spans_in_count, spans_out_count = dedupe_spans(spans_in, spans_out, keep_ids=keep_ids)
        print(f"spans: {spans_in_count} -> {spans_out_count} lines ({spans_in_count - spans_out_count} removed)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


```

---
### `scripts/export_phi_gold_standard.py`
- Size: `7994` bytes
```
#!/usr/bin/env python3
"""
Export pure Prodigy annotations to Gold Standard training format.

Unlike prodigy_export_corrections.py, this script does NOT merge with
any existing data. It exports only human-verified Prodigy annotations,
creating a pure "Gold Standard" dataset.

Usage:
    python scripts/export_phi_gold_standard.py \
        --dataset phi_corrections \
        --output data/ml_training/phi_gold_standard_v1.jsonl
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from transformers import AutoTokenizer

# Add repo root to path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Default paths
DEFAULT_MODEL_DIR = Path("artifacts/phi_distilbert_ner")
DEFAULT_OUTPUT = Path("data/ml_training/phi_gold_standard_v1.jsonl")


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True, help="Prodigy dataset name to export")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output JSONL file")
    parser.add_argument("--model-dir", type=Path, default=DEFAULT_MODEL_DIR, help="Tokenizer directory")
    return parser.parse_args(argv)


def load_prodigy_annotations(dataset_name: str) -> List[Dict[str, Any]]:
    """Load annotations from Prodigy database."""
    try:
        from prodigy.components.db import connect

        db = connect()
        if dataset_name not in db:
            logger.error(f"Dataset '{dataset_name}' not found in Prodigy database")
            logger.info(f"Available datasets: {db.datasets}")
            return []

        examples = db.get_dataset_examples(dataset_name)
        logger.info(f"Loaded {len(examples)} annotations from Prodigy dataset '{dataset_name}'")
        return examples

    except ImportError:
        logger.error("Prodigy not installed. Install with: pip install prodigy")
        return []
    except Exception as e:
        logger.error(f"Failed to load Prodigy annotations: {e}")
        return []


def spans_to_bio(
    text: str,
    spans: List[Dict[str, Any]],
    tokenizer: Any,
) -> Tuple[List[str], List[str]]:
    """
    Convert character spans to BIO tags aligned to tokenizer output.

    Args:
        text: The original text
        spans: List of spans with start, end, label
        tokenizer: The tokenizer to use for alignment

    Returns:
        (tokens, ner_tags) tuple
    """
    # Tokenize with offset mapping
    encoding = tokenizer(
        text,
        truncation=True,
        max_length=512,
        return_offsets_mapping=True,
    )

    offset_mapping = encoding.get("offset_mapping", [])
    input_ids = encoding.get("input_ids", [])

    # Convert input_ids back to tokens
    tokens = tokenizer.convert_ids_to_tokens(input_ids)

    # Initialize all tags as O
    ner_tags = ["O"] * len(tokens)

    # Skip special tokens (CLS, SEP)
    # Special tokens have offset (0, 0)
    valid_indices = []
    for idx, offset in enumerate(offset_mapping):
        if offset[0] != 0 or offset[1] != 0:
            valid_indices.append(idx)

    # Sort spans by start position
    sorted_spans = sorted(spans, key=lambda s: s.get("start", 0))

    # Assign BIO tags based on spans
    for span in sorted_spans:
        span_start = span.get("start", 0)
        span_end = span.get("end", 0)
        label = span.get("label", "UNKNOWN")

        # Find tokens that overlap with this span
        is_first = True
        for idx in valid_indices:
            tok_start, tok_end = offset_mapping[idx]

            # Check if token overlaps with span
            if tok_start < span_end and tok_end > span_start:
                if is_first:
                    ner_tags[idx] = f"B-{label}"
                    is_first = False
                else:
                    ner_tags[idx] = f"I-{label}"

    # Filter out special tokens for output
    filtered_tokens = []
    filtered_tags = []
    for idx, (token, tag) in enumerate(zip(tokens, ner_tags)):
        offset = offset_mapping[idx] if idx < len(offset_mapping) else (0, 0)
        if offset[0] != 0 or offset[1] != 0:
            filtered_tokens.append(token)
            filtered_tags.append(tag)

    return filtered_tokens, filtered_tags


def convert_annotation(
    example: Dict[str, Any],
    tokenizer: Any,
    dataset_name: str,
) -> Optional[Dict[str, Any]]:
    """Convert a single Prodigy annotation to training format."""
    text = example.get("text", "")
    if not text:
        return None

    # Get all spans (in ner.correct, all spans in the output are the final result)
    spans = example.get("spans", [])

    # Convert to BIO
    tokens, ner_tags = spans_to_bio(text, spans, tokenizer)

    if not tokens:
        return None

    # Extract metadata
    meta = example.get("meta", {})
    source = meta.get("source", "unknown")
    record_index = meta.get("record_index", 0)
    window_index = meta.get("window_index", 0)
    window_start = meta.get("window_start", 0)
    window_end = meta.get("window_end", len(text))

    # Build ID matching distilled format
    id_str = f"{source}:{record_index}:{window_index}"
    id_base = f"{source}:{record_index}"

    return {
        "id": id_str,
        "id_base": id_base,
        "source_path": f"prodigy:{dataset_name}",
        "record_index": record_index,
        "window_start": window_start,
        "window_end": window_end,
        "text": text,
        "tokens": tokens,
        "ner_tags": ner_tags,
        "origin": "gold-standard",
        "prodigy_dataset": dataset_name,
        "annotated_at": datetime.now().isoformat(),
    }


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv)

    # Load tokenizer
    if not args.model_dir.exists():
        logger.error(f"Model directory not found: {args.model_dir}")
        return 1

    logger.info(f"Loading tokenizer from {args.model_dir}")
    tokenizer = AutoTokenizer.from_pretrained(str(args.model_dir))

    # Load Prodigy annotations
    annotations = load_prodigy_annotations(args.dataset)
    if not annotations:
        logger.error("No annotations to export")
        return 1

    # Convert annotations to training format (only accepted examples)
    converted = []
    rejected_count = 0
    for example in annotations:
        # Only export accepted examples (answer == "accept")
        if example.get("answer") != "accept":
            rejected_count += 1
            continue

        record = convert_annotation(example, tokenizer, args.dataset)
        if record:
            converted.append(record)

    logger.info(f"Converted {len(converted)} accepted annotations")
    logger.info(f"Skipped {rejected_count} rejected/ignored annotations")

    if not converted:
        logger.warning("No valid annotations to export")
        return 0

    # Count label distribution
    label_counts: Dict[str, int] = {}
    for rec in converted:
        for tag in rec.get("ner_tags", []):
            if tag != "O":
                label_counts[tag] = label_counts.get(tag, 0) + 1
    logger.info(f"Label distribution: {label_counts}")

    # Count unique notes (id_base)
    unique_notes = set(rec["id_base"] for rec in converted)
    logger.info(f"Unique notes (id_base): {len(unique_notes)}")
    logger.info(f"Total windows: {len(converted)}")

    # Write output (pure gold, no merging)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        for record in converted:
            f.write(json.dumps(record) + "\n")

    logger.info(f"Wrote {len(converted)} gold standard records to {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

```

---
### `scripts/export_patient_note_texts.py`
- Size: `8166` bytes
```
#!/usr/bin/env python3
"""
Export per-patient NOTE_ID → note_text JSON files from golden extractions.

Context:
  `data/knowledge/golden_extractions_final/golden_*.json` contains arrays of entries like:
    {
      "note_text": "...",
      "registry_entry": { "patient_mrn": "445892_syn_2", ... },
      ...
    }

Goal:
  Create one JSON file per patient that includes ONLY the NOTE_ID and note text for each
  associated synthetic note, e.g.:
    output/445892.json
      {
        "445892_syn_1": "...",
        "445892_syn_2": "...",
        ...
      }

Usage:
  python scripts/export_patient_note_texts.py \
    --input-dir data/knowledge/golden_extractions_final \
    --output-dir data/knowledge/patient_note_texts
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


_SYN_RE = re.compile(r"^(?P<base>.+?)_syn_(?P<num>\d+)$")
_SAFE_FILENAME_RE = re.compile(r"[^A-Za-z0-9._-]+")


@dataclass(frozen=True)
class NoteRef:
    note_id: str
    note_text: str
    syn_num: int | None
    source_file: str


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Export per-patient NOTE_ID → note_text JSON files from golden_*.json."
    )
    p.add_argument(
        "--input-dir",
        type=Path,
        default=Path("data/knowledge/golden_extractions_final"),
        help="Directory containing golden_*.json files (arrays).",
    )
    p.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/knowledge/patient_note_texts"),
        help="Directory to write per-patient JSON files.",
    )
    p.add_argument(
        "--id-field",
        type=str,
        default="registry_entry.patient_mrn",
        help=(
            "Dot-path to the NOTE_ID. Examples: registry_entry.patient_mrn (default), "
            "note_id, registry_entry.note_id"
        ),
    )
    p.add_argument(
        "--text-field",
        type=str,
        default="note_text",
        help="Field name for note text (default: note_text).",
    )
    p.add_argument(
        "--only-synthetic",
        action="store_true",
        help="If set, only export notes whose NOTE_ID matches *_syn_<n>.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="If set, do not write files; only log counts.",
    )
    return p.parse_args(argv)


def _get_by_dotpath(obj: dict[str, Any], dotpath: str) -> Any:
    cur: Any = obj
    for key in dotpath.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


def extract_note_id(entry: dict[str, Any], id_field: str) -> str | None:
    """Extract a NOTE_ID from an entry, using the configured dot-path plus fallbacks."""
    raw = _get_by_dotpath(entry, id_field)
    if isinstance(raw, str) and raw.strip():
        return raw.strip()

    # Common fallbacks we’ve seen in various datasets.
    for fallback in ("note_id", "noteId", "registry_entry.patient_mrn", "registry_entry.note_id"):
        raw2 = _get_by_dotpath(entry, fallback)
        if isinstance(raw2, str) and raw2.strip():
            return raw2.strip()

    return None


def split_patient_base(note_id: str) -> tuple[str, int | None]:
    """Return (patient_base_id, syn_num) where syn_num is parsed from *_syn_<n>."""
    m = _SYN_RE.match(note_id)
    if not m:
        return note_id, None
    return m.group("base"), int(m.group("num"))


def _safe_patient_filename(patient_id: str) -> str:
    cleaned = _SAFE_FILENAME_RE.sub("_", patient_id).strip("._-")
    return cleaned or "unknown"


def collect_notes(
    input_dir: Path,
    *,
    id_field: str,
    text_field: str,
    only_synthetic: bool,
) -> tuple[dict[str, list[NoteRef]], dict[str, int]]:
    """Scan golden_*.json and group NoteRef entries by patient base id."""
    by_patient: dict[str, list[NoteRef]] = defaultdict(list)
    stats = {
        "files": 0,
        "entries": 0,
        "kept": 0,
        "skipped_missing_id": 0,
        "skipped_missing_text": 0,
        "skipped_non_synthetic": 0,
        "skipped_parse_error": 0,
    }

    golden_files = sorted(input_dir.glob("golden_*.json"))
    if not golden_files:
        raise FileNotFoundError(f"No golden_*.json found in: {input_dir}")

    for path in golden_files:
        stats["files"] += 1
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:  # noqa: BLE001 - surface source file in log + stats
            logger.warning("Failed to parse %s: %s", path, e)
            stats["skipped_parse_error"] += 1
            continue

        if not isinstance(data, list):
            logger.warning("Skipping %s (expected top-level list, got %s)", path, type(data).__name__)
            stats["skipped_parse_error"] += 1
            continue

        for entry in data:
            stats["entries"] += 1
            if not isinstance(entry, dict):
                stats["skipped_parse_error"] += 1
                continue

            note_id = extract_note_id(entry, id_field)
            if not note_id:
                stats["skipped_missing_id"] += 1
                continue

            patient_id, syn_num = split_patient_base(note_id)
            if only_synthetic and syn_num is None:
                stats["skipped_non_synthetic"] += 1
                continue

            note_text = entry.get(text_field)
            if not isinstance(note_text, str) or not note_text.strip():
                stats["skipped_missing_text"] += 1
                continue

            by_patient[patient_id].append(
                NoteRef(
                    note_id=note_id,
                    note_text=note_text,
                    syn_num=syn_num,
                    source_file=path.name,
                )
            )
            stats["kept"] += 1

    return by_patient, stats


def write_patient_files(by_patient: dict[str, list[NoteRef]], output_dir: Path) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)

    written = 0
    for patient_id, notes in by_patient.items():
        # Sort: synthetic notes by syn_num, then non-synthetic by note_id (stable).
        notes_sorted = sorted(
            notes,
            key=lambda n: (
                0 if n.syn_num is not None else 1,
                n.syn_num if n.syn_num is not None else 10**9,
                n.note_id,
            ),
        )

        payload: dict[str, str] = {}
        for n in notes_sorted:
            payload[n.note_id] = n.note_text

        out_path = output_dir / f"{_safe_patient_filename(patient_id)}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
            f.write("\n")
        written += 1

    return written


def main(argv: list[str] | None = None) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    args = parse_args(argv)

    by_patient, stats = collect_notes(
        args.input_dir,
        id_field=args.id_field,
        text_field=args.text_field,
        only_synthetic=args.only_synthetic,
    )

    logger.info(
        "Scanned %d files, %d entries; kept=%d (patients=%d).",
        stats["files"],
        stats["entries"],
        stats["kept"],
        len(by_patient),
    )
    logger.info(
        "Skipped: missing_id=%d missing_text=%d non_synthetic=%d parse_error=%d",
        stats["skipped_missing_id"],
        stats["skipped_missing_text"],
        stats["skipped_non_synthetic"],
        stats["skipped_parse_error"],
    )

    if args.dry_run:
        logger.info("Dry run: no files written.")
        return

    written = write_patient_files(by_patient, args.output_dir)
    logger.info("Wrote %d patient JSON files to %s", written, args.output_dir)


if __name__ == "__main__":
    main(sys.argv[1:])


```

---
### `scripts/test_phi_redaction_sample.py`
- Size: `8191` bytes
```
#!/usr/bin/env python3
"""
Test PHI Redaction on Random Sample of Golden Notes
====================================================

Randomly selects notes from golden JSON files and runs PHI redaction,
producing side-by-side comparison of original and redacted content.

Usage:
    python scripts/test_phi_redaction_sample.py [--count N] [--output FILE] [--no-ner]

Examples:
    python scripts/test_phi_redaction_sample.py                    # 10 random notes to stdout
    python scripts/test_phi_redaction_sample.py --count 5          # 5 random notes
    python scripts/test_phi_redaction_sample.py --output test.txt  # Save to file
    python scripts/test_phi_redaction_sample.py --no-ner             # Regex-only mode (faster)

Author: Claude Code
"""

import argparse
import glob
import json
import os
import random
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Any

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from modules.phi.adapters.phi_redactor_hybrid import PHIRedactor, RedactionConfig


def load_golden_notes(golden_dir: Path, limit: int = None) -> List[Tuple[str, str, str]]:
    """
    Load notes from golden JSON files.

    Returns:
        List of (note_text, source_file, note_index) tuples
    """
    notes = []
    pattern = golden_dir / "golden_*.json"

    for filepath in glob.glob(str(pattern)):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            filename = os.path.basename(filepath)

            # Handle both array and single-object formats
            if isinstance(data, list):
                for i, entry in enumerate(data):
                    if isinstance(entry, dict) and 'note_text' in entry:
                        note_text = entry['note_text']
                        if note_text and len(note_text.strip()) > 50:
                            notes.append((note_text, filename, str(i)))
            elif isinstance(data, dict) and 'note_text' in data:
                note_text = data['note_text']
                if note_text and len(note_text.strip()) > 50:
                    notes.append((note_text, filename, "0"))

        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load {filepath}: {e}", file=sys.stderr)
            continue

    return notes


def format_comparison(
    original: str,
    redacted: str,
    source: str,
    index: str,
    audit: Dict[str, Any],
    note_num: int
) -> str:
    """
    Format side-by-side comparison of original and redacted text.
    """
    separator = "=" * 80
    section_sep = "-" * 80

    lines = [
        separator,
        f"NOTE {note_num}: {source} [entry {index}]",
        separator,
        "",
        "ORIGINAL TEXT:",
        section_sep,
        original.strip(),
        "",
        section_sep,
        "REDACTED TEXT:",
        section_sep,
        redacted.strip(),
        "",
        section_sep,
        f"REDACTION SUMMARY: {audit.get('redaction_count', 0)} items redacted",
        section_sep,
    ]

    # Add detection details
    detections = audit.get('detections', [])
    if detections:
        lines.append("Detected PHI:")
        for det in detections:
            entity_type = det.get('type', 'UNKNOWN')
            text = det.get('text', '')[:50]  # Truncate long text
            confidence = det.get('confidence', 0)
            source_type = det.get('source', 'unknown')
            lines.append(f"  - [{entity_type}] \"{text}\" (conf={confidence:.2f}, source={source_type})")
    else:
        lines.append("No PHI detected.")

    # Add protected zones summary
    protected = audit.get('protected_zones', [])
    if protected:
        lines.append("")
        lines.append(f"Protected zones: {len(protected)}")
        # Show first few
        for pz in protected[:5]:
            reason = pz.get('reason', 'unknown')
            lines.append(f"  - {reason}")
        if len(protected) > 5:
            lines.append(f"  ... and {len(protected) - 5} more")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Test PHI redaction on random sample of golden notes"
    )
    parser.add_argument(
        "--count", "-n",
        type=int,
        default=10,
        help="Number of notes to sample (default: 10)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "--no-ner",
        action="store_true",
        help="Disable NER model (regex-only, faster)"
    )
    parser.add_argument(
        "--keep-dates",
        action="store_true",
        help="Do not redact procedure dates"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility"
    )
    parser.add_argument(
        "--golden-dir",
        type=str,
        default=None,
        help="Path to golden extractions directory"
    )

    args = parser.parse_args()

    # Set random seed if provided
    if args.seed is not None:
        random.seed(args.seed)

    # Determine golden directory
    if args.golden_dir:
        golden_dir = Path(args.golden_dir)
    else:
        golden_dir = PROJECT_ROOT / "data" / "knowledge" / "golden_extractions"

    if not golden_dir.exists():
        print(f"Error: Golden directory not found: {golden_dir}", file=sys.stderr)
        sys.exit(1)

    # Load notes
    print(f"Loading notes from {golden_dir}...", file=sys.stderr)
    all_notes = load_golden_notes(golden_dir)

    if not all_notes:
        print("Error: No notes found in golden files.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(all_notes)} notes total.", file=sys.stderr)

    # Sample random notes
    sample_size = min(args.count, len(all_notes))
    sample_notes = random.sample(all_notes, sample_size)

    print(f"Selected {sample_size} random notes.", file=sys.stderr)

    # Initialize redactor
    print(f"Initializing PHI Redactor (NER: {not args.no_ner})...", file=sys.stderr)
    config = RedactionConfig(
        redact_procedure_dates=not args.keep_dates
    )
    redactor = PHIRedactor(config=config, use_ner_model=not args.no_ner)

    # Process notes
    output_lines = []
    output_lines.append("=" * 80)
    output_lines.append("PHI REDACTION TEST REPORT")
    output_lines.append(f"Sample size: {sample_size} notes")
    output_lines.append(f"Mode: {'Regex + NER' if not args.no_ner else 'Regex-only'}")
    output_lines.append("=" * 80)
    output_lines.append("")

    total_redactions = 0

    for i, (note_text, source, index) in enumerate(sample_notes, 1):
        print(f"Processing note {i}/{sample_size}...", file=sys.stderr)

        try:
            redacted_text, audit = redactor.scrub(note_text)
            total_redactions += audit.get('redaction_count', 0)

            comparison = format_comparison(
                original=note_text,
                redacted=redacted_text,
                source=source,
                index=index,
                audit=audit,
                note_num=i
            )
            output_lines.append(comparison)

        except Exception as e:
            output_lines.append(f"ERROR processing note {i} from {source}[{index}]: {e}")
            output_lines.append("")

    # Summary
    output_lines.append("=" * 80)
    output_lines.append("SUMMARY")
    output_lines.append("=" * 80)
    output_lines.append(f"Notes processed: {sample_size}")
    output_lines.append(f"Total redactions: {total_redactions}")
    output_lines.append(f"Average redactions per note: {total_redactions / sample_size:.1f}")
    output_lines.append("")

    # Output results
    output_text = "\n".join(output_lines)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_text)
        print(f"Results saved to {args.output}", file=sys.stderr)
    else:
        print(output_text)

    print("Done!", file=sys.stderr)


if __name__ == "__main__":
    main()

```

---
### `scripts/prodigy_prepare_registry_relabel_batch.py`
- Size: `8397` bytes
```
#!/usr/bin/env python3
"""Prepare a Prodigy relabel batch from an existing human-labeled registry CSV.

Use case:
- You previously annotated registry procedure flags (e.g. in an older label schema).
- You added/renamed labels (e.g. updated the canonical label schema).
- You want to **re-annotate a focused subset** (e.g. all rigid bronchoscopy cases)
  in a fresh Prodigy dataset using the updated label set.

This script:
- Loads a human CSV (with note_text + label columns)
- Filters rows where one or more filter labels are positive (default: rigid_bronchoscopy)
- Expands cats to the *current* canonical label list from `modules/ml_coder/registry_label_schema.py`
- Emits Prodigy `textcat.manual` tasks:
    {"text": "...", "cats": {...}, "_view_id": "textcat", "meta": {...}}

Typical usage:

  python scripts/prodigy_prepare_registry_relabel_batch.py \
    --input-csv data/ml_training/registry_human_v1_backup.csv \
    --output-file data/ml_training/registry_rigid_review.jsonl \
    --filter-label rigid_bronchoscopy \
    --prefill-non-thermal-from-rigid \
    --limit 0

Then annotate in a new dataset:

  make registry-prodigy-annotate \
    REG_PRODIGY_DATASET=registry_v2_rigid_relabel \
    REG_PRODIGY_BATCH_FILE=data/ml_training/registry_rigid_review.jsonl
"""

from __future__ import annotations

import argparse
import json
import logging
import random
import sys
from pathlib import Path
from typing import Any

import pandas as pd

# Repo root on sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from modules.ml_coder.registry_label_schema import REGISTRY_LABELS  # noqa: E402


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--input-csv",
        type=Path,
        required=True,
        help="Human-labeled registry CSV (must include note_text)",
    )
    p.add_argument(
        "--output-file",
        type=Path,
        default=Path("data/ml_training/registry_rigid_review.jsonl"),
        help="Output Prodigy JSONL for relabeling",
    )
    p.add_argument(
        "--filter-label",
        action="append",
        default=["rigid_bronchoscopy"],
        help="Only include rows where this label column is positive. Repeatable.",
    )
    p.add_argument(
        "--filter-missing-label",
        action="append",
        default=[],
        help="Only include rows where this label column is NOT positive (i.e., 0/false). Repeatable.",
    )
    p.add_argument(
        "--min-positives",
        type=int,
        default=0,
        help="Skip rows with fewer than N total positive labels (across all canonical labels).",
    )
    p.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Max number of rows to emit (0 = no limit)",
    )
    p.add_argument(
        "--prefill-non-thermal-from-rigid",
        action="store_true",
        help=(
            "Heuristic prefill: set tumor_debulking_non_thermal=1 when rigid_bronchoscopy=1 "
            "and thermal_ablation=0 and cryotherapy=0. (You still review/edit in Prodigy.)"
        ),
    )
    p.add_argument(
        "--text-key",
        choices=["text", "note_text"],
        default="text",
        help="Key to use for the task text in Prodigy JSONL",
    )
    p.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed used when shuffling before applying --limit",
    )
    p.add_argument(
        "--shuffle",
        action="store_true",
        help="Shuffle rows after filtering (before applying --limit).",
    )
    return p.parse_args(argv)


def _coerce01(v: Any) -> int:
    try:
        return 1 if int(v) != 0 else 0
    except Exception:
        return 1 if bool(v) else 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.input_csv.exists():
        raise SystemExit(f"Input CSV not found: {args.input_csv}")

    logger.info("Reading CSV: %s", args.input_csv)
    df = pd.read_csv(args.input_csv)
    # Be tolerant of messy CSV headers (common when edited/exported in Excel):
    # - trailing spaces
    # - BOM markers
    df.columns = [str(c).strip().lstrip("\ufeff") for c in df.columns]
    if "note_text" not in df.columns:
        raise SystemExit(
            "Input CSV must contain a 'note_text' column (after header normalization). "
            f"Found columns: {list(df.columns)[:10]}..."
        )

    labels = list(REGISTRY_LABELS)

    # Normalize user-provided filter labels too (trim whitespace).
    filter_labels = [str(x).strip() for x in (args.filter_label or []) if str(x).strip()]
    filter_missing = [str(x).strip() for x in (args.filter_missing_label or []) if str(x).strip()]

    missing_filter = [c for c in (filter_labels + filter_missing) if c not in df.columns]
    if missing_filter:
        raise SystemExit(f"Missing filter label columns in CSV: {missing_filter}")

    logger.info("Loaded %d rows. Applying filters...", len(df))

    # Ensure canonical label columns exist (missing labels treated as 0).
    for label in labels:
        if label not in df.columns:
            df[label] = 0

    # Filter: must have at least one of filter_labels positive (unless none provided).
    if filter_labels:
        must_pos = df[filter_labels].fillna(0).applymap(_coerce01).sum(axis=1)
        df = df[must_pos >= 1].copy()

    # Filter: must have filter_missing labels NOT positive.
    if filter_missing:
        any_missing_pos = df[filter_missing].fillna(0).applymap(_coerce01).sum(axis=1)
        df = df[any_missing_pos == 0].copy()

    # Filter: minimum number of total positives across all canonical labels.
    min_pos = int(args.min_positives or 0)
    if min_pos > 0:
        total_pos = df[labels].fillna(0).applymap(_coerce01).sum(axis=1)
        df = df[total_pos >= min_pos].copy()

    if args.shuffle and len(df) > 1:
        rng = random.Random(int(args.seed))
        df = df.sample(frac=1.0, random_state=rng.randint(0, 2**31 - 1)).reset_index(drop=True)

    if args.limit and int(args.limit) > 0:
        df = df.head(int(args.limit))

    # Emit Prodigy tasks
    args.output_file.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Selected %d rows for review.", len(df))

    written = 0
    with args.output_file.open("w", encoding="utf-8") as f:
        for _, row in df.iterrows():
            note_text = str(row.get("note_text") or "").strip()
            if not note_text:
                continue

            cats: dict[str, int] = {label: _coerce01(row.get(label, 0)) for label in labels}

            # Optional prefill logic for specific cleanup workflows.
            if args.prefill_non_thermal_from_rigid and "tumor_debulking_non_thermal" in cats:
                rigid = cats.get("rigid_bronchoscopy", 0)
                thermal = cats.get("thermal_ablation", 0)
                cryo = cats.get("cryotherapy", 0)
                if rigid == 1 and thermal == 0 and cryo == 0:
                    cats["tumor_debulking_non_thermal"] = 1

            meta = {
                "source_csv": str(args.input_csv),
                "filter_labels": filter_labels,
                "filter_missing_label": filter_missing,
                "filter_hit": (filter_labels[0] if filter_labels else "manual"),
            }
            if "encounter_id" in df.columns:
                meta["encounter_id"] = str(row.get("encounter_id") or "")

            task = {
                # Prodigy `textcat.manual` expects a `text` field by default. We keep
                # this configurable for compatibility, but `text` is recommended.
                args.text_key: note_text,
                "cats": cats,
                "_view_id": "textcat",
                "meta": meta,
                # Non-exclusive is critical for registry multi-label.
                "config": {"exclusive": False},
            }

            f.write(json.dumps(task, ensure_ascii=False) + "\n")
            written += 1

    logger.info("Wrote %d tasks to %s", written, args.output_file)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```

---
### `scripts/find_critical_failures.py`
- Size: `9036` bytes
```
#!/usr/bin/env python3

from __future__ import annotations

import argparse
import glob
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable
from typing import TextIO

# --- CONFIGURATION: Define your keywords here ---
# These are "critical" classes you want to increase coverage for by finding notes
# that likely contain these concepts.
CRITICAL_CLASSES: dict[str, str] = {
    "PROC_MEDICATION": r"(?i)\b(lidocaine|fentanyl|midazolam|epinephrine|heparin|propofol|versed|saline|romazicon|narcan)\b",
    "CTX_INDICATION": r"(?i)\b(indication|history of|reason for|suspicion of|evaluate|eval|suspected|diagnosis)\b",
    "DISPOSITION": r"(?i)\b(discharged|admitted|transferred|follow-up|return to|released|stable condition)\b",
    "ANAT_INTERCOSTAL_SPACE": r"(?i)\b(intercostal|rib space|ics)\b",
    "OBS_FLUID_COLOR": r"(?i)\b(serous|sanguineous|purulent|straw|bloody|yellow|clear|cloudy|turbid|amber)\b",
    "MEAS_VOLUME": r"(?i)\b(\d+(\.\d+)?\s*(ml|cc|liters?|l))\b",
    "OBS_NO_COMPLICATION": r"(?i)\b(no complication|tolerated well|no adverse|uncomplicated|no immediate|no pneumothorax)\b",
    "PROC_NAME": r"(?i)\b(bronchoscopy|thoracentesis|biopsy|ebus|lavage|aspiration|pleuroscopy)\b",
}


@dataclass(frozen=True)
class NoteRecord:
    source_file: str
    note_id: str
    note_text: str
    record_index: int | None = None


def find_context(text: str, match_obj: re.Match[str], window: int = 50) -> str:
    start, end = match_obj.span()
    ctx_start = max(0, start - window)
    ctx_end = min(len(text), end + window)
    snippet = text[ctx_start:start] + "[[ " + text[start:end] + " ]]" + text[end:ctx_end]
    return snippet.replace("\n", " ")


def _extract_text_from_record(record: dict[str, Any]) -> str | None:
    for key in ("note_text", "text", "content", "evidence"):
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return None


def _extract_id_from_record(record: dict[str, Any], *, fallback: str) -> str:
    for key in ("id", "note_id", "noteId", "noteID"):
        value = record.get(key)
        if value is not None and str(value).strip():
            return str(value)
    return fallback


def iter_note_records(filepath: str) -> Iterable[NoteRecord]:
    """
    Yield NoteRecord objects from common JSON/JSONL shapes.

    Supported:
    - JSON dict mapping note_id -> note_text (this is how data/knowledge/patient_note_texts/*.json is structured)
    - JSON dict record: {"id": ..., "text"/"note_text": ...}
    - JSON list of dict records
    - JSONL of dict records
    """
    try:
        if filepath.endswith(".jsonl"):
            with open(filepath, "r", encoding="utf-8") as f:
                for idx, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    obj = json.loads(line)
                    if not isinstance(obj, dict):
                        continue
                    text = _extract_text_from_record(obj)
                    if not text:
                        continue
                    note_id = _extract_id_from_record(obj, fallback=f"{os.path.basename(filepath)}:line_{idx}")
                    yield NoteRecord(source_file=filepath, note_id=note_id, note_text=text, record_index=idx)
            return

        if filepath.endswith(".json"):
            with open(filepath, "r", encoding="utf-8") as f:
                content = json.load(f)

            # patient_note_texts format: { "note_123": "...", "note_123_syn_1": "..." }
            if isinstance(content, dict) and content and all(isinstance(v, str) for v in content.values()):
                for note_id, note_text in content.items():
                    if isinstance(note_text, str) and note_text.strip():
                        yield NoteRecord(source_file=filepath, note_id=str(note_id), note_text=note_text)
                return

            # single dict record: {"id": ..., "text": ...}
            if isinstance(content, dict):
                text = _extract_text_from_record(content)
                if text:
                    note_id = _extract_id_from_record(content, fallback=os.path.basename(filepath))
                    yield NoteRecord(source_file=filepath, note_id=note_id, note_text=text)
                return

            # list of dict records
            if isinstance(content, list):
                for idx, item in enumerate(content, 1):
                    if not isinstance(item, dict):
                        continue
                    text = _extract_text_from_record(item)
                    if not text:
                        continue
                    note_id = _extract_id_from_record(item, fallback=f"{os.path.basename(filepath)}:idx_{idx}")
                    yield NoteRecord(source_file=filepath, note_id=note_id, note_text=text, record_index=idx)
                return
    except Exception as e:
        print(f"Error reading {filepath}: {e}")


def scan_files(
    input_path: str,
    *,
    max_matches_per_label: int = 50,
    show_context: bool = True,
    output: TextIO | None = None,
) -> int:
    if os.path.isdir(input_path):
        files = glob.glob(os.path.join(input_path, "*.json*"))
    else:
        files = glob.glob(input_path)

    write_stdout = True

    def emit(line: str = "") -> None:
        nonlocal write_stdout
        if output is not None:
            output.write(line + "\n")
            output.flush()
        if write_stdout:
            try:
                print(line)
            except BrokenPipeError:
                # If stdout is piped (e.g., `| head`) and the reader closes early,
                # stop writing to stdout but keep writing to the output file.
                write_stdout = False

    emit(f"Scanning {len(files)} files for critical failure classes...\n")

    compiled = {label: re.compile(pattern) for label, pattern in CRITICAL_CLASSES.items()}
    hits_found = 0
    hits_by_label: dict[str, int] = {k: 0 for k in CRITICAL_CLASSES}
    notes_by_label: dict[str, set[str]] = {k: set() for k in CRITICAL_CLASSES}

    for file in files:
        for rec in iter_note_records(file):
            for label, rx in compiled.items():
                if max_matches_per_label >= 0 and hits_by_label[label] >= max_matches_per_label:
                    continue

                match = rx.search(rec.note_text)
                if not match:
                    continue

                hits_found += 1
                hits_by_label[label] += 1
                notes_by_label[label].add(rec.note_id)

                emit(f"[{label}]  note_id={rec.note_id}  file={os.path.basename(rec.source_file)}")
                if show_context:
                    emit(f"  Match: \"...{find_context(rec.note_text, match)}...\"")
                emit()

    if hits_found == 0:
        emit("No matches found. Check your keywords or input path.")
        return 0

    emit("Summary:")
    for label in sorted(CRITICAL_CLASSES.keys()):
        emit(f"- {label}: {hits_by_label[label]} matches across {len(notes_by_label[label])} notes")
    emit(f"\nDone. Found {hits_found} potential candidates.")
    return hits_found


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    default_output = repo_root / "reports" / "critical_failures.txt"

    parser = argparse.ArgumentParser(
        description="Scan JSONL/JSON note-text files for keywords indicating under-covered NER classes."
    )
    parser.add_argument("input", help="Path to a .jsonl file, a .json file, or a directory of files")
    parser.add_argument(
        "--max-matches-per-label",
        type=int,
        default=50,
        help="Limit printed matches per label (default: 50). Use -1 for unlimited.",
    )
    parser.add_argument(
        "--no-context",
        action="store_true",
        help="Don't print match context (just note_id + file).",
    )
    parser.add_argument(
        "--output",
        default=str(default_output),
        help=(
            "Path to write the same output to a text file (overwrites). "
            f"Default: {default_output}. Use '-' to disable file output."
        ),
    )
    args = parser.parse_args()

    out_f: TextIO | None = None
    try:
        if args.output and str(args.output).strip() != "-":
            out_path = os.path.expanduser(str(args.output))
            os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
            out_f = open(out_path, "w", encoding="utf-8")
            print(f"[output] writing report to: {out_path}")

        hits = scan_files(
            args.input,
            max_matches_per_label=int(args.max_matches_per_label),
            show_context=not bool(args.no_context),
            output=out_f,
        )
    finally:
        if out_f is not None:
            out_f.close()
    return 0 if hits else 1


if __name__ == "__main__":
    raise SystemExit(main())

```

---
### `scripts/fit_thresholds_from_eval.py`
- Size: `9076` bytes
```
#!/usr/bin/env python3
"""
Fit per-code thresholds from validation metrics.

This script analyzes model evaluation metrics and computes optimal thresholds
for the ternary case difficulty classification (HIGH_CONF / GRAY_ZONE / LOW_CONF).

For each code:
- Picks an upper threshold that achieves target precision (e.g. >= 0.9)
- Uses a global lower threshold (e.g. 0.4) for gray zone boundary

Usage:
    python scripts/fit_thresholds_from_eval.py [--metrics PATH] [--output PATH]
    python scripts/fit_thresholds_from_eval.py --target-precision 0.85
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import typer

from modules.common.logger import get_logger
from modules.ml_coder.thresholds import THRESHOLDS_PATH, Thresholds
from modules.ml_coder.training import MLB_PATH, PIPELINE_PATH
from modules.ml_coder.utils import clean_cpt_codes

logger = get_logger("fit_thresholds")

app = typer.Typer(help="Fit per-code thresholds from evaluation metrics.")


def compute_precision_at_threshold(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    threshold: float,
) -> float:
    """Compute precision at a given probability threshold."""
    y_pred = (y_prob >= threshold).astype(int)
    tp = ((y_pred == 1) & (y_true == 1)).sum()
    fp = ((y_pred == 1) & (y_true == 0)).sum()
    if tp + fp == 0:
        return 1.0  # No predictions, perfect precision by default
    return tp / (tp + fp)


def find_threshold_for_precision(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    target_precision: float = 0.9,
    min_threshold: float = 0.5,
    max_threshold: float = 0.95,
    step: float = 0.05,
) -> float:
    """Find the lowest threshold that achieves target precision."""
    for thresh in np.arange(min_threshold, max_threshold + step, step):
        prec = compute_precision_at_threshold(y_true, y_prob, thresh)
        if prec >= target_precision:
            return float(thresh)
    return max_threshold


def fit_thresholds_from_test_data(
    test_csv: Path,
    model_path: Path,
    mlb_path: Path,
    target_precision: float = 0.9,
    default_upper: float = 0.7,
    default_lower: float = 0.4,
) -> Thresholds:
    """
    Fit per-code thresholds from test data predictions.

    Args:
        test_csv: Path to test CSV with note_text and verified_cpt_codes
        model_path: Path to trained pipeline
        mlb_path: Path to MultiLabelBinarizer
        target_precision: Target precision for upper threshold
        default_upper: Default upper threshold if code has too few samples
        default_lower: Global lower threshold

    Returns:
        Thresholds object with per-code upper thresholds
    """
    logger.info("Loading model from %s", model_path)
    pipeline = joblib.load(model_path)
    mlb = joblib.load(mlb_path)

    logger.info("Loading test data from %s", test_csv)
    df = pd.read_csv(test_csv)
    df = df.dropna(subset=["note_text", "verified_cpt_codes"])
    df["note_text"] = df["note_text"].astype(str)
    df["verified_cpt_codes"] = df["verified_cpt_codes"].apply(clean_cpt_codes)

    texts = df["note_text"].tolist()
    labels = df["verified_cpt_codes"].tolist()

    logger.info("Running predictions on %d samples", len(texts))
    y_prob = pipeline.predict_proba(texts)
    y_true = mlb.transform(labels)

    per_code: dict[str, float] = {}

    for i, code in enumerate(mlb.classes_):
        code_true = y_true[:, i]
        code_prob = y_prob[:, i]

        # Only fit threshold if we have enough positive samples
        n_positive = code_true.sum()
        if n_positive < 3:
            logger.debug(
                "Code %s has only %d positive samples, using default threshold",
                code,
                n_positive,
            )
            per_code[code] = default_upper
            continue

        thresh = find_threshold_for_precision(
            code_true,
            code_prob,
            target_precision=target_precision,
            min_threshold=default_lower,
            max_threshold=0.95,
        )

        actual_precision = compute_precision_at_threshold(code_true, code_prob, thresh)
        logger.info(
            "Code %s: threshold=%.2f, precision=%.3f (n=%d)",
            code,
            thresh,
            actual_precision,
            n_positive,
        )
        per_code[code] = thresh

    return Thresholds(
        upper=default_upper,
        lower=default_lower,
        per_code=per_code,
    )


def analyze_metrics_file(
    metrics_path: Path,
    target_precision: float = 0.9,
    default_upper: float = 0.7,
    default_lower: float = 0.4,
) -> Thresholds:
    """
    Derive thresholds from pre-computed metrics file.

    This is a simpler approach that uses evaluation metrics
    to set thresholds based on observed performance.
    """
    logger.info("Loading metrics from %s", metrics_path)
    with open(metrics_path) as f:
        metrics = json.load(f)

    per_code: dict[str, float] = {}
    code_metrics = metrics.get("per_code", {})

    for code, data in code_metrics.items():
        precision = data.get("precision", 0.0)
        support = data.get("support", 0)

        # If current precision at 0.5 threshold is below target,
        # we need a higher threshold for high-confidence predictions
        if precision < target_precision and support >= 3:
            # Estimate: raise threshold proportionally to precision gap
            adjustment = (target_precision - precision) / target_precision
            new_thresh = min(0.5 + adjustment * 0.4, 0.9)
            per_code[code] = round(new_thresh, 2)
            logger.info(
                "Code %s: precision=%.2f < target, setting threshold=%.2f",
                code,
                precision,
                new_thresh,
            )
        elif precision >= target_precision:
            # Good precision at 0.5, can use default or slightly lower
            per_code[code] = default_upper
            logger.info(
                "Code %s: precision=%.2f >= target, using default threshold=%.2f",
                code,
                precision,
                default_upper,
            )
        else:
            # Low support, use default
            per_code[code] = default_upper

    return Thresholds(
        upper=default_upper,
        lower=default_lower,
        per_code=per_code,
    )


@app.command()
def main(
    test_csv: Path = typer.Option(
        Path("data/ml_training/test.csv"),
        "--test-csv",
        help="Path to test CSV file",
    ),
    metrics_path: Path = typer.Option(
        Path("data/models/metrics.json"),
        "--metrics",
        help="Path to evaluation metrics JSON (used if test CSV not available)",
    ),
    output_path: Path = typer.Option(
        THRESHOLDS_PATH,
        "--output",
        help="Output path for thresholds JSON",
    ),
    target_precision: float = typer.Option(
        0.9,
        "--target-precision",
        help="Target precision for high-confidence threshold",
    ),
    default_upper: float = typer.Option(
        0.7,
        "--default-upper",
        help="Default upper threshold",
    ),
    default_lower: float = typer.Option(
        0.4,
        "--default-lower",
        help="Default lower threshold (gray zone boundary)",
    ),
    use_metrics_only: bool = typer.Option(
        False,
        "--metrics-only",
        help="Use metrics file instead of re-running predictions",
    ),
) -> None:
    """Fit per-code thresholds from validation data."""
    model_path = PIPELINE_PATH
    mlb_path = MLB_PATH

    if use_metrics_only or not model_path.exists():
        if not metrics_path.exists():
            typer.echo(f"Error: Metrics file not found at {metrics_path}", err=True)
            raise typer.Exit(1)
        thresholds = analyze_metrics_file(
            metrics_path,
            target_precision=target_precision,
            default_upper=default_upper,
            default_lower=default_lower,
        )
    else:
        if not test_csv.exists():
            typer.echo(f"Error: Test CSV not found at {test_csv}", err=True)
            raise typer.Exit(1)
        thresholds = fit_thresholds_from_test_data(
            test_csv,
            model_path,
            mlb_path,
            target_precision=target_precision,
            default_upper=default_upper,
            default_lower=default_lower,
        )

    thresholds.to_json(output_path)
    logger.info("Saved thresholds to %s", output_path)

    # Summary
    typer.echo(f"\nThresholds saved to {output_path}")
    typer.echo(f"  Global upper: {thresholds.upper}")
    typer.echo(f"  Global lower: {thresholds.lower}")
    typer.echo(f"  Per-code overrides: {len(thresholds.per_code)}")

    # Show per-code thresholds
    if thresholds.per_code:
        typer.echo("\nPer-code upper thresholds:")
        for code, thresh in sorted(thresholds.per_code.items()):
            typer.echo(f"  {code}: {thresh:.2f}")


if __name__ == "__main__":
    app()

```

---
### `scripts/clean_distilled_phi_labels.py`
- Size: `9264` bytes
```
#!/usr/bin/env python3
"""Clean existing distilled PHI JSONL by removing obvious false positives."""

from __future__ import annotations

import argparse
import json
import logging
import re
from pathlib import Path

from scripts.distill_phi_labels import (
    DEGREE_SYMBOL,
    LABEL_MAPPING_STANDARD,
    line_bounds,
    normalize_entity_group,
    repair_bio,
    wipe_cpt_subword_labels,
    wipe_ln_station_labels,
)

logger = logging.getLogger("clean_distilled_phi")


def _load_tokenizer(name_or_path: str):
    from transformers import AutoTokenizer

    return AutoTokenizer.from_pretrained(name_or_path)


def _span_text(text: str, start: int, end: int) -> str:
    if not text:
        return ""
    start = max(0, min(start, len(text)))
    end = max(start, min(end, len(text)))
    return text[start:end]


def _line_text(text: str, idx: int) -> str:
    start, end = line_bounds(text, idx)
    return text[start:end]


def _looks_like_temp(span_text: str, line_text: str) -> bool:
    if re.fullmatch(r"\d{2,3}(?:\.\d+)?\s*[cCfF]", span_text.strip()):
        return True
    line_lower = line_text.lower()
    if any(token in line_lower for token in ("temp", "temperature", "degrees")):
        return True
    if DEGREE_SYMBOL in line_text:
        return True
    return False


def _iter_entities(ner_tags: list[str], offsets: list[tuple[int, int]]) -> list[tuple[int, int, str]]:
    entities: list[tuple[int, int, str]] = []
    current_label = None
    start_idx = None
    end_idx = None
    for idx, tag in enumerate(ner_tags):
        if tag == "O":
            if current_label is not None:
                entities.append((start_idx, end_idx, current_label))
                current_label = None
                start_idx = None
                end_idx = None
            continue
        if tag.startswith("B-"):
            if current_label is not None:
                entities.append((start_idx, end_idx, current_label))
            current_label = tag[2:]
            start_idx = idx
            end_idx = idx
            continue
        if tag.startswith("I-"):
            label = tag[2:]
            if current_label == label and start_idx is not None:
                end_idx = idx
            else:
                if current_label is not None:
                    entities.append((start_idx, end_idx, current_label))
                current_label = label
                start_idx = idx
                end_idx = idx
    if current_label is not None:
        entities.append((start_idx, end_idx, current_label))
    return entities


def _apply_refinery_to_tags(
    text: str,
    tokens: list[str],
    offsets: list[tuple[int, int]],
    ner_tags: list[str],
    *,
    drop_zipcode_if_cpt: bool,
    drop_buildingnum_if_temp: bool,
) -> list[str]:
    cleaned = list(ner_tags)
    entities = _iter_entities(cleaned, offsets)
    for start_idx, end_idx, label in entities:
        if start_idx is None or end_idx is None:
            continue
        span_start = offsets[start_idx][0]
        span_end = offsets[end_idx][1]
        span_text = _span_text(text, span_start, span_end)
        line_text = _line_text(text, span_start)
        label_upper = label.upper()
        if drop_zipcode_if_cpt and label_upper in {"ZIPCODE", "GEO"}:
            if re.fullmatch(r"\d{5}", span_text.strip()):
                if re.search(r"\bCPT\b", line_text, re.IGNORECASE):
                    for idx in range(start_idx, end_idx + 1):
                        cleaned[idx] = "O"
                elif re.search(r"\bCODE\b", line_text, re.IGNORECASE) and not re.search(
                    r"\bZIP\s+CODE\b",
                    line_text,
                    re.IGNORECASE,
                ):
                    for idx in range(start_idx, end_idx + 1):
                        cleaned[idx] = "O"
        if drop_buildingnum_if_temp and label_upper in {"BUILDINGNUM", "GEO"}:
            span_end = offsets[end_idx][1]
            tail = text[span_end : min(len(text), span_end + 4)]
            if _looks_like_temp(span_text, line_text) or re.match(
                rf"\s*(?:{DEGREE_SYMBOL}\s*)?[cCfF](?![a-zA-Z])",
                tail,
            ):
                for idx in range(start_idx, end_idx + 1):
                    cleaned[idx] = "O"
    return cleaned


def _normalize_ner_tags(ner_tags: list[str], schema: str, provider_label: str) -> list[str]:
    if schema != "standard":
        return ner_tags
    normalized = []
    for tag in ner_tags:
        if tag == "O":
            normalized.append(tag)
            continue
        prefix, label = tag.split("-", 1)
        mapped = normalize_entity_group(label, schema, provider_label)
        normalized.append(f"{prefix}-{mapped}")
    return normalized


def _tokenize_for_offsets(text: str, tokenizer, max_length: int | None = None):
    encoded = tokenizer(
        text,
        return_offsets_mapping=True,
        truncation=True,
        max_length=max_length,
    )
    tokens = tokenizer.convert_ids_to_tokens(encoded["input_ids"])
    offsets = [tuple(pair) for pair in encoded.get("offset_mapping", [])]
    filtered_tokens = []
    filtered_offsets = []
    for token, (start, end) in zip(tokens, offsets):
        if start == end:
            continue
        filtered_tokens.append(token)
        filtered_offsets.append((start, end))
    return filtered_tokens, filtered_offsets


def main() -> int:
    parser = argparse.ArgumentParser(description="Clean distilled PHI JSONL output")
    parser.add_argument(
        "--in",
        dest="in_path",
        type=Path,
        default=Path("data/ml_training/distilled_phi_labels.jsonl"),
    )
    parser.add_argument(
        "--out",
        dest="out_path",
        type=Path,
        default=Path("data/ml_training/distilled_phi_labels.cleaned.jsonl"),
    )
    parser.add_argument("--student-tokenizer", type=str, default="distilbert-base-uncased")
    parser.add_argument("--label-schema", choices=["teacher", "standard"], default="standard")
    parser.add_argument(
        "--drop-zipcode-if-cpt",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    parser.add_argument(
        "--drop-buildingnum-if-temp",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    parser.add_argument("--provider-label", type=str, default="PROVIDER")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    tokenizer = _load_tokenizer(args.student_tokenizer)

    cleaned_count = 0
    total = 0
    args.out_path.parent.mkdir(parents=True, exist_ok=True)

    with args.in_path.open("r", encoding="utf-8") as in_f, args.out_path.open("w", encoding="utf-8") as out_f:
        for line in in_f:
            line = line.strip()
            if not line:
                continue
            total += 1
            record = json.loads(line)
            text = record.get("text", "")
            tokens = record.get("tokens", [])
            ner_tags = record.get("ner_tags", [])
            offsets = record.get("offsets") or record.get("offset_mapping")

            if not text or not tokens or not ner_tags:
                out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
                continue

            if offsets is None:
                tok_tokens, tok_offsets = _tokenize_for_offsets(
                    text,
                    tokenizer,
                    max_length=len(tokens) + 2,
                )
                if tok_tokens != tokens:
                    logger.warning("Token mismatch; skipping refinery for record %s", record.get("id"))
                    cleaned_tags = _normalize_ner_tags(ner_tags, args.label_schema, args.provider_label)
                    record["ner_tags"] = cleaned_tags
                    out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
                    continue
                offsets = tok_offsets

            cleaned_tags = _apply_refinery_to_tags(
                text,
                tokens,
                offsets,
                ner_tags,
                drop_zipcode_if_cpt=args.drop_zipcode_if_cpt,
                drop_buildingnum_if_temp=args.drop_buildingnum_if_temp,
            )
            cleaned_tags = _normalize_ner_tags(cleaned_tags, args.label_schema, args.provider_label)
            cleaned_tags = wipe_cpt_subword_labels(
                tokens,
                cleaned_tags,
                text=text,
                offsets=offsets,
            )
            cleaned_tags = wipe_ln_station_labels(tokens, cleaned_tags)
            cleaned_tags = repair_bio(cleaned_tags)

            if cleaned_tags != ner_tags:
                cleaned_count += 1
            record["ner_tags"] = cleaned_tags
            out_f.write(json.dumps(record, ensure_ascii=False) + "\n")

    logger.info("Processed %s records", total)
    logger.info("Cleaned %s records", cleaned_count)
    logger.info("Output: %s", args.out_path)
    logger.info("Label schema: %s", args.label_schema)
    if args.label_schema == "standard":
        logger.info("Standard label mapping keys: %s", sorted(LABEL_MAPPING_STANDARD))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```

---
### `scripts/registry_label_overlap_report.py`
- Size: `9583` bytes
```
#!/usr/bin/env python3
"""Generate a registry label overlap/contradiction report for targeted annotation.

Input: one or more registry CSVs (train/val/test)
Output: JSON report with:
- per-label positive counts
- top pairwise co-occurrences (counts + rates)
- constraint-driven contradictions / normalization events

This is intended to drive targeted Prodigy batches for semantic overlap areas
(e.g., BAL vs bronchial wash, rigid vs debulking).
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from modules.ml_coder.registry_label_constraints import apply_label_constraints, registry_consistency_flags
from modules.ml_coder.registry_label_schema import REGISTRY_LABELS, compute_encounter_id

_RE_BAL = re.compile(r"\b(bal|bronchoalveolar\s+lavage)\b", flags=re.IGNORECASE)
_RE_WASH = re.compile(r"\bbronchial\s+wash(?:ing)?s?\b", flags=re.IGNORECASE)


def _first_span(regex: re.Pattern[str], text: str) -> tuple[int, int] | None:
    m = regex.search(text or "")
    if not m:
        return None
    return (int(m.start()), int(m.end()))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--csv",
        type=Path,
        action="append",
        default=[],
        help="Registry CSV to analyze (repeatable). Default: registry_train.csv only.",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("reports/registry_label_overlap.json"),
        help="Output JSON report path",
    )
    p.add_argument("--top-k", type=int, default=200, help="Top co-occurring label pairs to include")
    p.add_argument("--max-examples", type=int, default=50, help="Max example rows per issue type")
    return p.parse_args(argv)


def _load_csv(path: Path, labels: list[str]) -> pd.DataFrame:
    df = pd.read_csv(path)
    if df.empty:
        return df
    if "note_text" not in df.columns:
        raise ValueError(f"Missing note_text in {path}")

    for label in labels:
        if label not in df.columns:
            df[label] = 0
        df[label] = pd.to_numeric(df[label], errors="coerce").fillna(0).clip(0, 1).astype(int)
    return df


def _pairwise_stats(y: np.ndarray, labels: list[str], top_k: int) -> list[dict[str, Any]]:
    if y.size == 0:
        return []
    counts = y.sum(axis=0).astype(int)
    co = (y.T @ y).astype(int)

    pairs: list[dict[str, Any]] = []
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            c = int(co[i, j])
            if c == 0:
                continue
            denom = int(counts[i] + counts[j] - c)
            jaccard = float(c / denom) if denom else 0.0
            p_j_given_i = float(c / counts[i]) if counts[i] else 0.0
            p_i_given_j = float(c / counts[j]) if counts[j] else 0.0
            pairs.append(
                {
                    "a": labels[i],
                    "b": labels[j],
                    "co_count": c,
                    "count_a": int(counts[i]),
                    "count_b": int(counts[j]),
                    "jaccard": jaccard,
                    "p_b_given_a": p_j_given_i,
                    "p_a_given_b": p_i_given_j,
                }
            )

    pairs.sort(key=lambda d: d["co_count"], reverse=True)
    return pairs[: max(0, int(top_k))]


@dataclass
class IssueCollector:
    max_examples: int
    counts: dict[str, int]
    examples: dict[str, list[dict[str, Any]]]

    def __init__(self, max_examples: int):
        self.max_examples = max_examples
        self.counts = {}
        self.examples = {}

    def add(self, issue_type: str, example: dict[str, Any]) -> None:
        self.counts[issue_type] = int(self.counts.get(issue_type, 0)) + 1
        if issue_type not in self.examples:
            self.examples[issue_type] = []
        if len(self.examples[issue_type]) < self.max_examples:
            self.examples[issue_type].append(example)


def _analyze_constraints(df: pd.DataFrame, *, source: str, max_examples: int) -> dict[str, Any]:
    issues = IssueCollector(max_examples=max_examples)
    if df.empty:
        return {"counts": {}, "examples": {}}

    for idx, row in df.iterrows():
        text = str(row.get("note_text") or "")
        raw = {
            "note_text": text,
            "bal": int(row.get("bal", 0)),
            "bronchial_wash": int(row.get("bronchial_wash", 0)),
            "transbronchial_cryobiopsy": int(row.get("transbronchial_cryobiopsy", 0)),
            "transbronchial_biopsy": int(row.get("transbronchial_biopsy", 0)),
            "rigid_bronchoscopy": int(row.get("rigid_bronchoscopy", 0)),
            "tumor_debulking_non_thermal": int(row.get("tumor_debulking_non_thermal", 0)),
        }
        normalized = dict(raw)
        apply_label_constraints(normalized, note_text=text, inplace=True)

        eid = compute_encounter_id(text)

        # Record normalization events (where constraints changed labels).
        if raw["bal"] != normalized["bal"] or raw["bronchial_wash"] != normalized["bronchial_wash"]:
            issues.add(
                "bal_vs_bronchial_wash_normalized",
                {
                    "encounter_id": eid,
                    "source": source,
                    "row_index": int(idx),
                    "bal_raw": raw["bal"],
                    "wash_raw": raw["bronchial_wash"],
                    "bal_norm": normalized["bal"],
                    "wash_norm": normalized["bronchial_wash"],
                    "bal_span": _first_span(_RE_BAL, text),
                    "wash_span": _first_span(_RE_WASH, text),
                    "note_len": len(text),
                },
            )
        elif raw["bal"] == 1 and raw["bronchial_wash"] == 1:
            issues.add(
                "bal_and_bronchial_wash_overlap",
                {
                    "encounter_id": eid,
                    "source": source,
                    "row_index": int(idx),
                    "bal_span": _first_span(_RE_BAL, text),
                    "wash_span": _first_span(_RE_WASH, text),
                    "note_len": len(text),
                },
            )

        if raw["transbronchial_cryobiopsy"] == 1 and raw["transbronchial_biopsy"] == 0:
            issues.add(
                "cryo_without_tbb",
                {
                    "encounter_id": eid,
                    "source": source,
                    "row_index": int(idx),
                    "note_len": len(text),
                },
            )

        flags = registry_consistency_flags(raw)
        if flags.get("rigid_without_debulking"):
            issues.add("rigid_without_debulking", {"encounter_id": eid, "source": source, "row_index": int(idx)})
        if flags.get("debulking_without_rigid"):
            issues.add("debulking_without_rigid", {"encounter_id": eid, "source": source, "row_index": int(idx)})

    return {"counts": issues.counts, "examples": issues.examples}


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    csvs = args.csv if args.csv else [Path("data/ml_training/registry_train.csv")]
    labels = list(REGISTRY_LABELS)

    all_rows = 0
    label_counts: dict[str, int] = {label: 0 for label in labels}
    pairwise: list[dict[str, Any]] = []
    constraint_counts: dict[str, int] = {}
    constraint_examples: dict[str, list[dict[str, Any]]] = {}

    for csv_path in csvs:
        df = _load_csv(csv_path, labels)
        if df.empty:
            continue
        all_rows += int(len(df))

        y = df[labels].to_numpy(dtype=int)
        for label, c in zip(labels, y.sum(axis=0).tolist()):
            label_counts[label] += int(c)

        pairwise.extend(_pairwise_stats(y, labels, top_k=args.top_k))

        constraint_report = _analyze_constraints(df, source=str(csv_path), max_examples=args.max_examples)
        for k, v in constraint_report["counts"].items():
            constraint_counts[k] = int(constraint_counts.get(k, 0)) + int(v)
        for k, examples in constraint_report["examples"].items():
            constraint_examples.setdefault(k, [])
            remaining = args.max_examples - len(constraint_examples[k])
            if remaining > 0:
                constraint_examples[k].extend(list(examples)[:remaining])

    # De-duplicate pairwise list across multiple CSVs by (a,b) while summing counts.
    merged_pairs: dict[tuple[str, str], dict[str, Any]] = {}
    for item in pairwise:
        key = (item["a"], item["b"])
        if key not in merged_pairs:
            merged_pairs[key] = dict(item)
            continue
        merged_pairs[key]["co_count"] += int(item["co_count"])
        merged_pairs[key]["count_a"] += int(item["count_a"])
        merged_pairs[key]["count_b"] += int(item["count_b"])

    top_pairs = sorted(merged_pairs.values(), key=lambda d: d["co_count"], reverse=True)[: args.top_k]

    out = {
        "inputs": [str(p) for p in csvs],
        "n_rows": int(all_rows),
        "labels": labels,
        "label_counts": label_counts,
        "top_pairs": top_pairs,
        "constraint_counts": constraint_counts,
        "constraint_examples": constraint_examples,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(f"Wrote report: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


```

---
### `scripts/align_synthetic_names.py`
- Size: `9603` bytes
```
#!/usr/bin/env python3
"""Align patient name mentions to `synthetic_metadata.generated_name`.

Some golden extraction records contain inconsistent or placeholder patient names in
`note_text` and `registry_entry.evidence` (e.g., "Pt: [Name]" vs generated_name).
This script enforces the synthetic name for common patient header patterns and
prints a summary report.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import shutil
from pathlib import Path
from typing import Any, Iterable, Tuple

logger = logging.getLogger(__name__)

STANDARD_REDACTION_TOKEN = "[REDACTED]"

# Match common patient header keys and capture the patient name value (not age/MRN suffixes).
PATIENT_HEADER_NAME_RE = re.compile(
    r"(?im)"
    r"(?P<prefix>\b(?:patient(?:\s+name)?|pt|subject|name)\b\s*[:\-]\s*)"
    r"(?P<name>"
    r"\[(?:patient\s+)?name\]"  # [Name] / [Patient Name]
    r"|<PERSON>"  # <PERSON>
    r"|[A-Z][a-z]+,\s*[A-Z][a-z]+(?:\s+[A-Z]\.?)?"  # Last, First M.
    r"|[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}"  # First Last (2-4 parts)
    r"|[A-Z][a-z]+"  # Single token fallback
    r")"
)

# Replace honorific placeholders like "Ms. [Name]" or "Mr. <PERSON>"
HONORIFIC_PLACEHOLDER_RE = re.compile(r"(?i)\b(?P<title>mr|ms|mrs)\.\s*(?P<name>\[(?:patient\s+)?name\]|<PERSON>)")


def iter_input_files(input_dir: Path) -> Iterable[Path]:
    yield from sorted(input_dir.glob("*.json"))


def _normalize_name(raw: str) -> str:
    s = (raw or "").strip()
    if not s:
        return ""
    if STANDARD_REDACTION_TOKEN in s:
        return ""
    # Placeholders are treated as non-matching.
    if s.startswith("[") and s.endswith("]"):
        return ""
    if s.startswith("<") and s.endswith(">"):
        return ""
    s = re.sub(r"(?i)^(mr|ms|mrs|dr)\.\s+", "", s).strip()

    # Trim common trailing demographics (", 64M", ", 67-year-old Male", etc.)
    s = re.sub(r"(?i),\s*\d{1,3}\s*[mf]\b.*$", "", s).strip()
    s = re.sub(r"(?i),\s*\d{1,3}[-\s]*(?:y/?o|yo|yrs?|years?|year[-\s]old)\b.*$", "", s).strip()

    # Normalize "Last, First" to "First Last"
    if "," in s:
        last, rest = s.split(",", 1)
        rest = rest.strip()
        if rest:
            s = f"{rest} {last.strip()}"

    s = " ".join(s.split()).strip(" ,")
    return s.casefold()


def _swap_last_first(name: str) -> str | None:
    if "," not in name:
        return None
    last, rest = name.split(",", 1)
    rest = " ".join(rest.split()).strip()
    if not last.strip() or not rest:
        return None
    return f"{rest} {last.strip()}"


def enforce_synthetic_name(text: str, generated_name: str) -> Tuple[str, bool, int]:
    """Return (new_text, changed, replacements_count)."""
    if not text or not generated_name:
        return text, False, 0

    desired_norm = _normalize_name(generated_name)
    if not desired_norm:
        return text, False, 0

    replacements = 0
    changed = False
    original_names: set[str] = set()

    def _replace_header(match: re.Match[str]) -> str:
        nonlocal replacements, changed
        prefix = match.group("prefix")
        name = match.group("name")
        if STANDARD_REDACTION_TOKEN in name:
            return match.group(0)
        current_norm = _normalize_name(name)
        if current_norm == desired_norm and current_norm:
            return match.group(0)
        # Record the original (non-placeholder) for global replacement pass
        if current_norm and not (name.startswith("[") or name.startswith("<")):
            original_names.add(name)
        replacements += 1
        changed = True
        return f"{prefix}{generated_name}"

    new_text = PATIENT_HEADER_NAME_RE.sub(_replace_header, text)

    def _replace_honorific(match: re.Match[str]) -> str:
        nonlocal replacements, changed
        title = match.group("title")
        name = match.group("name")
        if STANDARD_REDACTION_TOKEN in name:
            return match.group(0)
        replacements += 1
        changed = True
        return f"{title}. {generated_name}"

    new_text = HONORIFIC_PLACEHOLDER_RE.sub(_replace_honorific, new_text)

    # Replace remaining mentions of the original patient name (if we saw a concrete name).
    for original in sorted(original_names, key=len, reverse=True):
        if original and original in new_text:
            new_text = new_text.replace(original, generated_name)
        swapped = _swap_last_first(original)
        if swapped and swapped in new_text:
            new_text = new_text.replace(swapped, generated_name)

    if new_text != text and not changed:
        # e.g., global replacements only
        changed = True

    return new_text, changed, replacements


def enforce_in_structure(value: Any, generated_name: str) -> Tuple[Any, int, bool]:
    """Return (new_value, replacements, changed)."""
    if isinstance(value, str):
        new_text, changed, replacements = enforce_synthetic_name(value, generated_name)
        return new_text, replacements, changed
    if isinstance(value, list):
        total_rep = 0
        any_changed = False
        new_list = []
        for item in value:
            new_item, rep, ch = enforce_in_structure(item, generated_name)
            total_rep += rep
            any_changed = any_changed or ch
            new_list.append(new_item)
        return new_list, total_rep, any_changed
    if isinstance(value, dict):
        total_rep = 0
        any_changed = False
        new_dict = {}
        for k, v in value.items():
            new_v, rep, ch = enforce_in_structure(v, generated_name)
            total_rep += rep
            any_changed = any_changed or ch
            new_dict[k] = new_v
        return new_dict, total_rep, any_changed
    return value, 0, False


def main() -> int:
    parser = argparse.ArgumentParser(description="Align patient names to synthetic_metadata.generated_name")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("data/knowledge/golden_extractions"),
        help="Directory containing golden JSON files",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/knowledge/golden_extractions_aligned"),
        help="Directory to write aligned output files",
    )
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="Overwrite input files instead of writing to --output-dir",
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="When --in-place, create .bak backups next to the originals",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if not args.input_dir.exists():
        logger.error("Input directory not found: %s", args.input_dir)
        return 1

    files = list(iter_input_files(args.input_dir))
    if not files:
        logger.warning("No golden_*.json files found in %s", args.input_dir)
        return 0

    if not args.in_place:
        args.output_dir.mkdir(parents=True, exist_ok=True)

    records_total = 0
    records_changed = 0
    replacements_total = 0

    for path in files:
        records = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(records, list):
            continue

        file_changed = False
        for rec in records:
            if not isinstance(rec, dict):
                continue
            records_total += 1

            synthetic = rec.get("synthetic_metadata")
            generated_name = synthetic.get("generated_name") if isinstance(synthetic, dict) else None
            if not isinstance(generated_name, str) or not generated_name.strip():
                continue

            rep_this = 0
            changed_this = False

            note_text = rec.get("note_text")
            if isinstance(note_text, str) and note_text:
                new_note, ch, rep = enforce_synthetic_name(note_text, generated_name)
                if ch and new_note != note_text:
                    rec["note_text"] = new_note
                    changed_this = True
                rep_this += rep

            registry_entry = rec.get("registry_entry")
            if isinstance(registry_entry, dict) and "evidence" in registry_entry:
                new_evidence, rep, ch = enforce_in_structure(registry_entry.get("evidence"), generated_name)
                if ch and new_evidence != registry_entry.get("evidence"):
                    registry_entry["evidence"] = new_evidence
                    changed_this = True
                rep_this += rep

            if changed_this:
                records_changed += 1
                replacements_total += rep_this
                file_changed = True

        out_path = path if args.in_place else (args.output_dir / path.name)
        if args.in_place and args.backup and file_changed:
            backup_path = path.with_suffix(path.suffix + ".bak")
            shutil.copy2(path, backup_path)
        if file_changed or not args.in_place:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    logger.info("Records processed: %s", records_total)
    logger.info("Records changed: %s", records_changed)
    logger.info("Name replacements applied: %s", replacements_total)
    if args.in_place:
        logger.info("Output: in-place (%s)", args.input_dir)
    else:
        logger.info("Output directory: %s", args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


```

---
### `scripts/registry_pipeline_smoke.py`
- Size: `9739` bytes
```
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _truthy_env(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in ("1", "true", "yes")


if not _truthy_env("PROCSUITE_SKIP_DOTENV"):
    load_dotenv(override=False)

from modules.registry.application.registry_service import RegistryService  # noqa: E402
from modules.registry.deterministic_extractors import run_deterministic_extractors  # noqa: E402
from modules.registry.processing.masking import mask_offset_preserving  # noqa: E402
from modules.registry.processing.navigation_fiducials import (  # noqa: E402
    apply_navigation_fiducials,
)
from modules.registry.schema import RegistryRecord  # noqa: E402
from modules.registry.self_correction.keyword_guard import scan_for_omissions  # noqa: E402


def _read_note_text(path: str | None, inline_text: str | None) -> str:
    if inline_text:
        return inline_text
    if not path:
        raise ValueError("Provide --note or --text.")
    note_path = Path(path)
    return note_path.read_text(encoding="utf-8")


def _collect_performed_flags(record_data: dict[str, Any]) -> set[str]:
    flags: set[str] = set()
    procs = record_data.get("procedures_performed")
    if isinstance(procs, dict):
        for name, payload in procs.items():
            if isinstance(payload, dict) and payload.get("performed") is True:
                flags.add(f"procedures_performed.{name}.performed")

    pleural = record_data.get("pleural_procedures")
    if isinstance(pleural, dict):
        for name, payload in pleural.items():
            if isinstance(payload, dict) and payload.get("performed") is True:
                flags.add(f"pleural_procedures.{name}.performed")

    if record_data.get("established_tracheostomy_route") is True:
        flags.add("established_tracheostomy_route")

    granular = record_data.get("granular_data")
    if isinstance(granular, dict):
        targets = granular.get("navigation_targets")
        if isinstance(targets, list):
            for target in targets:
                if isinstance(target, dict) and target.get("fiducial_marker_placed") is True:
                    flags.add("granular_data.navigation_targets[*].fiducial_marker_placed")
                    break

    return flags


def _apply_seed_uplift(
    record_data: dict[str, Any],
    seed: dict[str, Any],
    masked_note_text: str,
) -> tuple[dict[str, Any], list[str]]:
    uplifted: list[str] = []

    seed_procs = seed.get("procedures_performed")
    if isinstance(seed_procs, dict):
        record_procs = record_data.get("procedures_performed") or {}
        if not isinstance(record_procs, dict):
            record_procs = {}
        for name, payload in seed_procs.items():
            if not isinstance(payload, dict) or payload.get("performed") is not True:
                continue
            existing = record_procs.get(name) or {}
            if not isinstance(existing, dict):
                existing = {}
            if existing.get("performed") is not True:
                existing["performed"] = True
                uplifted.append(f"procedures_performed.{name}.performed")
            for key, value in payload.items():
                if key == "performed":
                    continue
                if existing.get(key) in (None, "", [], {}):
                    existing[key] = value
            record_procs[name] = existing
        if record_procs:
            record_data["procedures_performed"] = record_procs

    seed_pleural = seed.get("pleural_procedures")
    if isinstance(seed_pleural, dict):
        record_pleural = record_data.get("pleural_procedures") or {}
        if not isinstance(record_pleural, dict):
            record_pleural = {}
        for name, payload in seed_pleural.items():
            if not isinstance(payload, dict) or payload.get("performed") is not True:
                continue
            existing = record_pleural.get(name) or {}
            if not isinstance(existing, dict):
                existing = {}
            if existing.get("performed") is not True:
                existing["performed"] = True
                uplifted.append(f"pleural_procedures.{name}.performed")
            for key, value in payload.items():
                if key == "performed":
                    continue
                if existing.get(key) in (None, "", [], {}):
                    existing[key] = value
            record_pleural[name] = existing
        if record_pleural:
            record_data["pleural_procedures"] = record_pleural

    if seed.get("established_tracheostomy_route") is True:
        if record_data.get("established_tracheostomy_route") is not True:
            record_data["established_tracheostomy_route"] = True
            uplifted.append("established_tracheostomy_route")

    if apply_navigation_fiducials(record_data, masked_note_text):
        uplifted.append("granular_data.navigation_targets[*].fiducial_marker_placed")

    return record_data, uplifted


def _print_list(label: str, items: list[str] | set[str]) -> None:
    if not items:
        print(f"{label}: (none)")
        return
    if isinstance(items, set):
        items = sorted(items)
    print(f"{label}:")
    for item in items:
        print(f"  - {item}")


def _print_self_correction_diagnostics(result) -> None:
    audit_report = getattr(result, "audit_report", None)
    high_conf = getattr(audit_report, "high_conf_omissions", None) if audit_report is not None else None
    if not high_conf:
        print("Audit high-conf omissions: (none)")
    else:
        print("Audit high-conf omissions:")
        for pred in high_conf:
            cpt = getattr(pred, "cpt", None)
            prob = getattr(pred, "prob", None)
            bucket = getattr(pred, "bucket", None)
            try:
                prob_str = f"{float(prob):.2f}" if prob is not None else "?"
            except Exception:
                prob_str = "?"
            print(f"  - {cpt} (prob={prob_str}, bucket={bucket})")

    warnings = getattr(result, "warnings", None)
    if isinstance(warnings, list):
        self_correct_warnings = [w for w in warnings if isinstance(w, str) and "SELF_CORRECT" in w]
        auto_corrected = [w for w in warnings if isinstance(w, str) and "AUTO_CORRECTED" in w]
        diag = self_correct_warnings + auto_corrected
        if diag:
            print("Self-correction diagnostics:")
            for w in diag:
                print(f"  - {w}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Smoke test the registry extraction pipeline on a note."
    )
    parser.add_argument("--note", help="Path to a note text file.")
    parser.add_argument("--text", help="Inline note text.")
    parser.add_argument(
        "--self-correct",
        action="store_true",
        help="Attempt self-correction via extract_fields (requires raw-ML + LLM).",
    )
    parser.add_argument(
        "--real-llm",
        action="store_true",
        help="Allow real LLM calls (disables stub/offline defaults).",
    )
    args = parser.parse_args()

    try:
        note_text = _read_note_text(args.note, args.text)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.real_llm:
        os.environ.setdefault("REGISTRY_USE_STUB_LLM", "0")
        os.environ.setdefault("GEMINI_OFFLINE", "0")
        os.environ.setdefault("OPENAI_OFFLINE", "0")
    else:
        if os.getenv("REGISTRY_USE_STUB_LLM") is None:
            os.environ["REGISTRY_USE_STUB_LLM"] = "1"
        if os.getenv("GEMINI_OFFLINE") is None:
            os.environ["GEMINI_OFFLINE"] = "1"

    masked = mask_offset_preserving(note_text)

    service = RegistryService()
    record, warnings, meta = service.extract_record(note_text)

    before_flags = _collect_performed_flags(record.model_dump())

    seed = run_deterministic_extractors(masked)
    record_data = record.model_dump()
    record_data, uplifted = _apply_seed_uplift(record_data, seed, masked)
    uplifted_flags = set(uplifted)
    after_flags = _collect_performed_flags(record_data)

    record_after = RegistryRecord(**record_data)
    omission_warnings = scan_for_omissions(masked, record_after)

    _print_list("Performed flags (extract_record)", before_flags)
    _print_list("Performed flags added by deterministic uplift", uplifted_flags)
    _print_list("Performed flags (after uplift)", after_flags)
    _print_list("Extract warnings", warnings)
    _print_list("Omission warnings", omission_warnings)

    if args.self_correct:
        os.environ.setdefault("REGISTRY_SELF_CORRECT_ENABLED", "1")
        try:
            result = service.extract_fields(note_text)
        except Exception as exc:
            print(f"SELF_CORRECT_ERROR: {exc}")
        else:
            _print_self_correction_diagnostics(result)
            if result.self_correction:
                print("Self-correction applied:")
                for item in result.self_correction:
                    applied_paths = getattr(item, "applied_paths", None)
                    if isinstance(applied_paths, list) and applied_paths:
                        print(f"  - {item.trigger.target_cpt}: applied {', '.join(applied_paths)}")
                    else:
                        print(f"  - {item.trigger.target_cpt}: applied (no paths recorded)")
            else:
                print("Self-correction applied: (none)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```

---
### `scripts/diamond_loop_cloud_sync.py`
- Size: `10358` bytes
```
#!/usr/bin/env python3
"""
Diamond Loop cloud sync helper.

Goal:
- Keep Diamond Loop state consistent across machines (WSL + macOS) using a cloud
  drive folder (Google Drive).
- Avoid syncing Prodigy's SQLite DB directly (unsafe). Instead sync via export/import.

What this syncs:
- Prodigy dataset snapshot (JSONL) for REGISTRY textcat workflow
- Registry Prodigy manifest (prevents re-sampling)
- Unlabeled notes pool (ensures consistent sampling universe)
- Optional: current batch + human export CSV

Two modes:
- push: export Prodigy dataset → copy to cloud; copy local files → cloud
- pull: copy cloud files → local; import Prodigy dataset (with --reset)

WSL + Google Drive on Windows G: example:
  python scripts/diamond_loop_cloud_sync.py push --dataset registry_v1 --gdrive-win-root "G:\\My Drive\\proc_suite_sync"
  python scripts/diamond_loop_cloud_sync.py pull --dataset registry_v1 --gdrive-win-root "G:\\My Drive\\proc_suite_sync"

macOS example (Drive path varies by install):
  python scripts/diamond_loop_cloud_sync.py push --dataset registry_v1 --sync-root "/Users/<you>/Library/CloudStorage/GoogleDrive-<acct>/My Drive/proc_suite_sync"
  python scripts/diamond_loop_cloud_sync.py pull --dataset registry_v1 --sync-root "/Users/<you>/Library/CloudStorage/GoogleDrive-<acct>/My Drive/proc_suite_sync"
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SyncPaths:
    # Repo-local paths (relative to repo root)
    manifest_rel: Path = Path("data/ml_training/registry_prodigy_manifest.json")
    unlabeled_rel: Path = Path("data/ml_training/registry_unlabeled_notes.jsonl")
    batch_rel: Path = Path("data/ml_training/registry_prodigy_batch.jsonl")
    human_csv_rel: Path = Path("data/ml_training/registry_human.csv")

    # Cloud layout (relative to sync root)
    diamond_dir: Path = Path("diamond_loop")
    prodigy_dir: Path = Path("prodigy")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _run(cmd: list[str], *, check: bool = True, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        check=check,
        text=True,
        capture_output=capture,
    )


def _is_wsl() -> bool:
    # Common signal in WSL envs.
    return "WSL_INTEROP" in os.environ or "WSL_DISTRO_NAME" in os.environ


def _wslpath_to_windows(path: Path) -> str:
    """
    Convert a Linux/WSL path to a Windows path usable by PowerShell.
    Requires wslpath.
    """
    cp = _run(["wslpath", "-w", str(path)], capture=True)
    out = (cp.stdout or "").strip()
    if not out:
        raise RuntimeError(f"wslpath returned empty output for {path}")
    return out


def _ps_copy_item(win_src: str, win_dst: str) -> None:
    # Use Copy-Item with -Force; ensure destination directory exists.
    # Use single quotes (PowerShell) for proper handling of spaces.
    dst_dir = win_dst.rsplit("\\", 1)[0]
    cmd = (
        f"New-Item -ItemType Directory -Force -Path '{dst_dir}' | Out-Null; "
        f"Copy-Item -Force '{win_src}' '{win_dst}'"
    )
    _run(["powershell.exe", "-NoProfile", "-Command", cmd], check=True)


def _copy_local_to_cloud(local_src: Path, cloud_dst: Path, *, sync_root: Path | None, gdrive_win_root: str | None) -> None:
    local_src = local_src.resolve()
    if not local_src.exists():
        return

    if gdrive_win_root:
        if not _is_wsl():
            raise RuntimeError("--gdrive-win-root is intended for WSL environments.")
        win_src = _wslpath_to_windows(local_src)
        win_dst = str(Path(gdrive_win_root) / cloud_dst).replace("/", "\\")
        _ps_copy_item(win_src, win_dst)
        return

    if sync_root is None:
        raise RuntimeError("Must provide either --sync-root (mac/linux) or --gdrive-win-root (WSL).")
    dst = (sync_root / cloud_dst).resolve()
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(local_src, dst)


def _copy_cloud_to_local(cloud_src: Path, local_dst: Path, *, sync_root: Path | None, gdrive_win_root: str | None) -> bool:
    local_dst = local_dst.resolve()

    if gdrive_win_root:
        if not _is_wsl():
            raise RuntimeError("--gdrive-win-root is intended for WSL environments.")
        win_dst = _wslpath_to_windows(local_dst)
        win_src = str(Path(gdrive_win_root) / cloud_src).replace("/", "\\")
        try:
            _ps_copy_item(win_src, win_dst)
            return True
        except subprocess.CalledProcessError:
            return False

    if sync_root is None:
        raise RuntimeError("Must provide either --sync-root (mac/linux) or --gdrive-win-root (WSL).")
    src = (sync_root / cloud_src).resolve()
    if not src.exists():
        return False
    local_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, local_dst)
    return True


def _prodigy_export(dataset: str, out_file: Path) -> None:
    from scripts.prodigy_cloud_sync import export_dataset  # local helper

    export_dataset(dataset=dataset, out_file=out_file, answer=None)


def _prodigy_import(dataset: str, in_file: Path, *, reset: bool) -> None:
    from scripts.prodigy_cloud_sync import import_dataset  # local helper

    import_dataset(dataset=dataset, in_file=in_file, reset_first=reset, overwrite=False, rehash=False)


def push(
    *,
    dataset: str,
    sync_root: Path | None,
    gdrive_win_root: str | None,
    include_batch: bool,
    include_human: bool,
) -> None:
    repo = _repo_root()
    p = SyncPaths()

    # 1) Export Prodigy dataset snapshot to a temp file, then copy it to cloud.
    tmp = Path("/tmp") / f"{dataset}.prodigy.jsonl"
    _prodigy_export(dataset, tmp)
    _copy_local_to_cloud(tmp, p.prodigy_dir / f"{dataset}.prodigy.jsonl", sync_root=sync_root, gdrive_win_root=gdrive_win_root)

    # 2) Copy local Diamond Loop files to cloud if present.
    _copy_local_to_cloud(repo / p.manifest_rel, p.diamond_dir / p.manifest_rel.name, sync_root=sync_root, gdrive_win_root=gdrive_win_root)
    _copy_local_to_cloud(repo / p.unlabeled_rel, p.diamond_dir / p.unlabeled_rel.name, sync_root=sync_root, gdrive_win_root=gdrive_win_root)
    if include_batch:
        _copy_local_to_cloud(repo / p.batch_rel, p.diamond_dir / p.batch_rel.name, sync_root=sync_root, gdrive_win_root=gdrive_win_root)
    if include_human:
        _copy_local_to_cloud(repo / p.human_csv_rel, p.diamond_dir / p.human_csv_rel.name, sync_root=sync_root, gdrive_win_root=gdrive_win_root)

    print(f"OK: pushed dataset '{dataset}' and Diamond Loop files to sync root")


def pull(
    *,
    dataset: str,
    sync_root: Path | None,
    gdrive_win_root: str | None,
    reset_dataset: bool,
    include_batch: bool,
    include_human: bool,
) -> None:
    repo = _repo_root()
    p = SyncPaths()

    # 1) Pull dataset snapshot from cloud into temp, then import into local Prodigy DB.
    tmp = Path("/tmp") / f"{dataset}.prodigy.jsonl"
    ok = _copy_cloud_to_local(p.prodigy_dir / f"{dataset}.prodigy.jsonl", tmp, sync_root=sync_root, gdrive_win_root=gdrive_win_root)
    if not ok:
        raise FileNotFoundError(f"Missing cloud dataset snapshot: {p.prodigy_dir / f'{dataset}.prodigy.jsonl'}")
    _prodigy_import(dataset, tmp, reset=reset_dataset)

    # 2) Pull Diamond Loop files from cloud into repo (best-effort).
    _copy_cloud_to_local(p.diamond_dir / p.manifest_rel.name, repo / p.manifest_rel, sync_root=sync_root, gdrive_win_root=gdrive_win_root)
    _copy_cloud_to_local(p.diamond_dir / p.unlabeled_rel.name, repo / p.unlabeled_rel, sync_root=sync_root, gdrive_win_root=gdrive_win_root)
    if include_batch:
        _copy_cloud_to_local(p.diamond_dir / p.batch_rel.name, repo / p.batch_rel, sync_root=sync_root, gdrive_win_root=gdrive_win_root)
    if include_human:
        _copy_cloud_to_local(p.diamond_dir / p.human_csv_rel.name, repo / p.human_csv_rel, sync_root=sync_root, gdrive_win_root=gdrive_win_root)

    print(f"OK: pulled dataset '{dataset}' and Diamond Loop files from sync root")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    def add_common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--dataset", default="registry_v1", help="Prodigy dataset name (default: registry_v1)")
        g = p.add_mutually_exclusive_group(required=True)
        g.add_argument("--sync-root", type=Path, help="Local filesystem path to sync root (mac/linux)")
        g.add_argument("--gdrive-win-root", type=str, help="Windows path to sync root (WSL), e.g. G:\\My Drive\\proc_suite_sync")
        p.add_argument("--include-batch", action="store_true", help="Also sync the current batch JSONL")
        p.add_argument("--include-human", action="store_true", help="Also sync registry_human.csv")

    p_push = sub.add_parser("push", help="Export Prodigy dataset and push Diamond Loop files to cloud")
    add_common(p_push)

    p_pull = sub.add_parser("pull", help="Pull from cloud and import into local Prodigy DB")
    add_common(p_pull)
    p_pull.add_argument(
        "--reset",
        action="store_true",
        help="Drop local dataset before import (recommended when switching machines)",
    )

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    sync_root = args.sync_root.resolve() if getattr(args, "sync_root", None) is not None else None
    gdrive_win_root = getattr(args, "gdrive_win_root", None)

    if args.cmd == "push":
        push(
            dataset=args.dataset,
            sync_root=sync_root,
            gdrive_win_root=gdrive_win_root,
            include_batch=bool(args.include_batch),
            include_human=bool(args.include_human),
        )
        return 0

    if args.cmd == "pull":
        pull(
            dataset=args.dataset,
            sync_root=sync_root,
            gdrive_win_root=gdrive_win_root,
            reset_dataset=bool(args.reset),
            include_batch=bool(args.include_batch),
            include_human=bool(args.include_human),
        )
        return 0

    raise SystemExit(f"Unknown cmd: {args.cmd}")


if __name__ == "__main__":
    raise SystemExit(main())



```

---
### `scripts/evaluate_coder.py`
- Size: `11238` bytes
```
#!/usr/bin/env python3
"""
Evaluation harness for EnhancedCPTCoder using synthetic_notes_with_CPT.csv.

This script evaluates coder performance against the evaluation dataset but
DOES NOT influence rule generation. It is for assessment only.

Canonical rule sources remain:
- data/synthetic_CPT_corrected.json
- ip_golden_knowledge_v2_2.json

Usage:
    python scripts/evaluate_coder.py [--verbose] [--output results.csv]
"""
from __future__ import annotations

import argparse
import ast
import csv
import sys
from pathlib import Path
from typing import Set, Dict, List, Tuple
from collections import defaultdict

# Add root to path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from modules.autocode.coder import EnhancedCPTCoder


def load_evaluation_data(csv_path: Path) -> List[Dict]:
    """Load the evaluation dataset from synthetic_notes_with_CPT.csv."""
    data = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Parse the cpt_codes field (stored as string representation of list)
            cpt_codes_str = row.get("cpt_codes", "[]")
            try:
                cpt_codes = ast.literal_eval(cpt_codes_str)
                if isinstance(cpt_codes, list):
                    cpt_codes = [str(c).strip() for c in cpt_codes]
                else:
                    cpt_codes = [str(cpt_codes).strip()]
            except (ValueError, SyntaxError):
                cpt_codes = []

            data.append({
                "patient_id": row.get("patient_identifier_trigger", ""),
                "note_text": row.get("note_text", ""),
                "expected_codes": set(cpt_codes),
            })
    return data


def normalize_code(code: str) -> str:
    """Normalize CPT code by stripping + prefix and whitespace."""
    return code.lstrip("+").strip()


def extract_coder_codes(result: dict) -> Set[str]:
    """Extract CPT codes from coder output."""
    codes_list = result.get("codes", [])
    return {normalize_code(c.get("cpt", "")) for c in codes_list if c.get("cpt")}


def compute_metrics(
    all_expected: List[Set[str]],
    all_predicted: List[Set[str]]
) -> Dict[str, float]:
    """Compute precision, recall, and F1 for code-level evaluation."""
    # Aggregate counts
    total_tp = 0
    total_fp = 0
    total_fn = 0

    for expected, predicted in zip(all_expected, all_predicted):
        expected_norm = {normalize_code(c) for c in expected}
        predicted_norm = {normalize_code(c) for c in predicted}

        tp = len(expected_norm & predicted_norm)
        fp = len(predicted_norm - expected_norm)
        fn = len(expected_norm - predicted_norm)

        total_tp += tp
        total_fp += fp
        total_fn += fn

    precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
    recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "true_positives": total_tp,
        "false_positives": total_fp,
        "false_negatives": total_fn,
    }


def compute_per_code_metrics(
    all_expected: List[Set[str]],
    all_predicted: List[Set[str]]
) -> Dict[str, Dict[str, float]]:
    """Compute per-code precision, recall, and F1."""
    code_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})

    for expected, predicted in zip(all_expected, all_predicted):
        expected_norm = {normalize_code(c) for c in expected}
        predicted_norm = {normalize_code(c) for c in predicted}

        for code in expected_norm | predicted_norm:
            if code in expected_norm and code in predicted_norm:
                code_stats[code]["tp"] += 1
            elif code in predicted_norm:
                code_stats[code]["fp"] += 1
            elif code in expected_norm:
                code_stats[code]["fn"] += 1

    per_code_metrics = {}
    for code, stats in sorted(code_stats.items()):
        tp, fp, fn = stats["tp"], stats["fp"], stats["fn"]
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        per_code_metrics[code] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "tp": tp,
            "fp": fp,
            "fn": fn,
        }

    return per_code_metrics


def evaluate_coder(
    coder: EnhancedCPTCoder,
    data: List[Dict],
    verbose: bool = False,
) -> Tuple[Dict[str, float], Dict[str, Dict[str, float]], List[Dict]]:
    """
    Run coder evaluation on the dataset.

    Returns:
        - Overall metrics (precision, recall, F1)
        - Per-code metrics
        - Detailed results per note
    """
    all_expected = []
    all_predicted = []
    detailed_results = []

    exact_matches = 0
    total = len(data)

    for i, item in enumerate(data):
        note_text = item["note_text"]
        expected = item["expected_codes"]
        patient_id = item["patient_id"]

        result = coder.code_procedure({
            "note_text": note_text,
            "locality": "00",
            "setting": "facility"
        })
        predicted = extract_coder_codes(result)

        expected_norm = {normalize_code(c) for c in expected}
        predicted_norm = {normalize_code(c) for c in predicted}

        is_exact_match = expected_norm == predicted_norm
        if is_exact_match:
            exact_matches += 1

        missing = expected_norm - predicted_norm
        extra = predicted_norm - expected_norm

        all_expected.append(expected)
        all_predicted.append(predicted)

        result_detail = {
            "patient_id": patient_id,
            "expected": sorted(expected_norm),
            "predicted": sorted(predicted_norm),
            "exact_match": is_exact_match,
            "missing": sorted(missing),
            "extra": sorted(extra),
        }
        detailed_results.append(result_detail)

        if verbose:
            status = "✓" if is_exact_match else "✗"
            print(f"[{i+1}/{total}] {status} Patient {patient_id}")
            print(f"  Expected: {sorted(expected_norm)}")
            print(f"  Predicted: {sorted(predicted_norm)}")
            if missing:
                print(f"  Missing: {sorted(missing)}")
            if extra:
                print(f"  Extra: {sorted(extra)}")
            print()

    # Compute overall metrics
    overall = compute_metrics(all_expected, all_predicted)
    overall["exact_match_rate"] = exact_matches / total if total > 0 else 0.0
    overall["exact_matches"] = exact_matches
    overall["total"] = total

    # Compute per-code metrics
    per_code = compute_per_code_metrics(all_expected, all_predicted)

    return overall, per_code, detailed_results


def print_summary(overall: Dict, per_code: Dict[str, Dict]):
    """Print evaluation summary."""
    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)

    print(f"\nOverall Metrics:")
    print(f"  Exact Match Rate: {overall['exact_match_rate']:.1%} ({overall['exact_matches']}/{overall['total']})")
    print(f"  Precision: {overall['precision']:.3f}")
    print(f"  Recall: {overall['recall']:.3f}")
    print(f"  F1 Score: {overall['f1']:.3f}")
    print(f"  True Positives: {overall['true_positives']}")
    print(f"  False Positives: {overall['false_positives']}")
    print(f"  False Negatives: {overall['false_negatives']}")

    print(f"\nPer-Code Metrics:")
    print(f"{'Code':<10} {'Precision':<12} {'Recall':<12} {'F1':<12} {'TP':<6} {'FP':<6} {'FN':<6}")
    print("-" * 60)

    for code, metrics in sorted(per_code.items()):
        print(
            f"{code:<10} {metrics['precision']:.3f}        "
            f"{metrics['recall']:.3f}        {metrics['f1']:.3f}        "
            f"{metrics['tp']:<6} {metrics['fp']:<6} {metrics['fn']:<6}"
        )

    # Highlight problematic codes
    print("\n" + "-" * 60)
    print("Codes with low recall (< 0.5):")
    low_recall = [(c, m) for c, m in per_code.items() if m["recall"] < 0.5 and m["fn"] > 0]
    if low_recall:
        for code, metrics in sorted(low_recall, key=lambda x: x[1]["recall"]):
            print(f"  {code}: recall={metrics['recall']:.2f} (missing {metrics['fn']} times)")
    else:
        print("  None")

    print("\nCodes with low precision (< 0.5):")
    low_precision = [(c, m) for c, m in per_code.items() if m["precision"] < 0.5 and m["fp"] > 0]
    if low_precision:
        for code, metrics in sorted(low_precision, key=lambda x: x[1]["precision"]):
            print(f"  {code}: precision={metrics['precision']:.2f} (extra {metrics['fp']} times)")
    else:
        print("  None")


def save_results(detailed_results: List[Dict], output_path: Path):
    """Save detailed results to CSV."""
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "patient_id", "expected", "predicted", "exact_match", "missing", "extra"
        ])
        writer.writeheader()
        for result in detailed_results:
            writer.writerow({
                "patient_id": result["patient_id"],
                "expected": ",".join(result["expected"]),
                "predicted": ",".join(result["predicted"]),
                "exact_match": result["exact_match"],
                "missing": ",".join(result["missing"]),
                "extra": ",".join(result["extra"]),
            })
    print(f"\nDetailed results saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate EnhancedCPTCoder against synthetic_notes_with_CPT.csv"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print per-note results"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Save detailed results to CSV file"
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=ROOT / "data" / "synthetic_notes_with_CPT.csv",
        help="Path to evaluation CSV"
    )
    args = parser.parse_args()

    if not args.data.exists():
        print(f"Error: Evaluation data not found at {args.data}")
        sys.exit(1)

    print(f"Loading evaluation data from: {args.data}")
    data = load_evaluation_data(args.data)
    print(f"Loaded {len(data)} notes for evaluation")

    print("\nInitializing EnhancedCPTCoder...")
    coder = EnhancedCPTCoder(use_llm_advisor=False)

    print("\nRunning evaluation...")
    overall, per_code, detailed = evaluate_coder(coder, data, verbose=args.verbose)

    print_summary(overall, per_code)

    if args.output:
        save_results(detailed, args.output)

    # Return non-zero exit code if F1 is below threshold
    if overall["f1"] < 0.5:
        print("\n⚠️  Warning: F1 score below 0.5 threshold")
        sys.exit(1)


if __name__ == "__main__":
    main()

```

---
### `scripts/scrub_golden_jsons.py`
- Size: `11262` bytes
```
#!/usr/bin/env python3
"""Scrub PHI from golden JSON files for ML training.

This script processes all golden_*.json files in data/knowledge/golden_extractions/
and scrubs PHI from the `note_text` field using PresidioScrubber.

The scrubbing uses the same Presidio-based scrubber as the PHI Demo workflow,
with clinical allowlists to preserve anatomical terms and procedure vocabulary.

Usage:
    python scripts/scrub_golden_jsons.py                    # Scrub in-place (creates backups)
    python scripts/scrub_golden_jsons.py --dry-run          # Preview without modifying
    python scripts/scrub_golden_jsons.py --no-backup        # Scrub in-place without backups
    python scripts/scrub_golden_jsons.py --output-dir out/  # Write to separate directory
    python scripts/scrub_golden_jsons.py --report-path artifacts/redactions.jsonl  # Write redaction report (JSONL)
"""

from __future__ import annotations

import argparse
import json
import csv
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Add project root to path for module imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tqdm import tqdm


def get_scrubber():
    """Initialize PresidioScrubber with fallback."""
    from modules.phi.adapters.presidio_scrubber import PresidioScrubber
    return PresidioScrubber()


def _open_report_writer(report_path: Path | None, report_format: str):
    """Open a report writer for redactions.

    Returns:
        (handle, write_row_fn) or (None, None) if report_path is None.
    """
    if report_path is None:
        return None, None

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_format = report_format.lower().strip()
    if report_format not in {"jsonl", "csv"}:
        raise ValueError("report_format must be one of: jsonl, csv")

    if report_format == "jsonl":
        f = report_path.open("w", encoding="utf-8")

        def _write(row: dict[str, Any]) -> None:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

        return f, _write

    # CSV
    f = report_path.open("w", encoding="utf-8", newline="")
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "timestamp_utc",
            "input_file",
            "record_index",
            "entity_type",
            "placeholder",
            "original_start",
            "original_end",
            "original_text",
        ],
    )
    writer.writeheader()

    def _write(row: dict[str, Any]) -> None:
        writer.writerow(row)

    return f, _write


def scrub_golden_json(
    input_path: Path,
    scrubber,
    dry_run: bool = False,
    output_path: Path | None = None,
    create_backup: bool = True,
    report_write=None,
    report_timestamp_utc: str | None = None,
) -> dict:
    """Scrub PHI from a single golden JSON file.

    Args:
        input_path: Path to golden JSON file
        scrubber: PresidioScrubber instance
        dry_run: If True, don't write changes
        output_path: Optional separate output path
        create_backup: If True and output_path is None, create .bak backup
        report_write: Optional function which accepts a dict and writes a report row
        report_timestamp_utc: Optional timestamp string to include in report rows

    Returns:
        Dict with stats: {total_records, scrubbed_count, entity_count}
    """
    with open(input_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    stats = {
        "total_records": len(records),
        "scrubbed_count": 0,
        "entity_count": 0,
        "entities_by_type": {},
    }

    for idx, record in enumerate(records):
        if "note_text" not in record or not record["note_text"]:
            continue

        original_text = record["note_text"]
        result = scrubber.scrub(original_text, document_type="procedure_note")

        if result.scrubbed_text != original_text:
            stats["scrubbed_count"] += 1
            stats["entity_count"] += len(result.entities)

            # Track entity types
            for ent in result.entities:
                etype = ent.get("entity_type", "UNKNOWN")
                stats["entities_by_type"][etype] = stats["entities_by_type"].get(etype, 0) + 1

                # Optional per-entity report rows
                if report_write is not None:
                    try:
                        start = int(ent.get("original_start", -1))
                        end = int(ent.get("original_end", -1))
                    except Exception:
                        start, end = -1, -1
                    redacted = ""
                    if 0 <= start < end <= len(original_text):
                        redacted = original_text[start:end]
                    report_write(
                        {
                            "timestamp_utc": report_timestamp_utc,
                            "input_file": str(input_path),
                            "record_index": idx,
                            "entity_type": etype,
                            "placeholder": ent.get("placeholder", ""),
                            "original_start": start,
                            "original_end": end,
                            "original_text": redacted,
                        }
                    )

            # Update the record
            record["note_text"] = result.scrubbed_text

            # Store original for reference (optional metadata)
            if "scrub_metadata" not in record:
                record["scrub_metadata"] = {}
            record["scrub_metadata"]["entities_redacted"] = len(result.entities)
            record["scrub_metadata"]["entity_types"] = [e.get("entity_type") for e in result.entities]

    if not dry_run:
        # Determine output path
        final_output = output_path if output_path else input_path

        # Create backup if writing in-place
        if output_path is None and create_backup:
            backup_path = input_path.with_suffix(".json.bak")
            shutil.copy2(input_path, backup_path)

        # Ensure output directory exists
        final_output.parent.mkdir(parents=True, exist_ok=True)

        # Write scrubbed data
        with open(final_output, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Scrub PHI from golden JSON files for ML training",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("data/knowledge/golden_extractions"),
        help="Directory containing golden_*.json files",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Write scrubbed files to separate directory (default: in-place)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying files",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Don't create .bak backups when modifying in-place",
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default="golden_*.json",
        help="Glob pattern for input files (default: golden_*.json)",
    )
    parser.add_argument(
        "--report-path",
        type=Path,
        default=None,
        help="Optional path to write a redaction report (JSONL/CSV).",
    )
    parser.add_argument(
        "--report-format",
        type=str,
        default="jsonl",
        choices=["jsonl", "csv"],
        help="Redaction report format (default: jsonl).",
    )

    args = parser.parse_args()

    # Find golden JSON files
    input_files = sorted(args.input_dir.glob(args.pattern))
    if not input_files:
        print(f"No files matching '{args.pattern}' found in {args.input_dir}")
        return

    print(f"\n{'=' * 60}")
    print("Golden JSON PHI Scrubbing")
    print(f"{'=' * 60}")
    print(f"Input directory: {args.input_dir}")
    print(f"Files found: {len(input_files)}")
    print(f"Output: {'DRY RUN (no changes)' if args.dry_run else (args.output_dir or 'in-place')}")
    print(f"Backups: {'No' if args.no_backup else 'Yes'}")
    if args.report_path:
        print(f"Redaction report: {args.report_path} ({args.report_format})")
    print(f"{'=' * 60}\n")

    # Initialize scrubber
    print("Initializing Presidio scrubber...")
    scrubber = get_scrubber()
    print(f"Using spaCy model: {scrubber.model_name}\n")

    # Optional report writer
    report_ts = datetime.utcnow().strftime("%Y%m%d_%H%M%SZ")
    report_handle, report_write = _open_report_writer(args.report_path, args.report_format)

    # Process files
    total_stats = {
        "files_processed": 0,
        "total_records": 0,
        "scrubbed_count": 0,
        "entity_count": 0,
        "entities_by_type": {},
    }

    for input_path in tqdm(input_files, desc="Processing files"):
        # Determine output path
        if args.output_dir:
            output_path = args.output_dir / input_path.name
        else:
            output_path = None

        try:
            stats = scrub_golden_json(
                input_path=input_path,
                scrubber=scrubber,
                dry_run=args.dry_run,
                output_path=output_path,
                create_backup=not args.no_backup,
                report_write=report_write,
                report_timestamp_utc=report_ts,
            )

            total_stats["files_processed"] += 1
            total_stats["total_records"] += stats["total_records"]
            total_stats["scrubbed_count"] += stats["scrubbed_count"]
            total_stats["entity_count"] += stats["entity_count"]

            for etype, count in stats["entities_by_type"].items():
                total_stats["entities_by_type"][etype] = (
                    total_stats["entities_by_type"].get(etype, 0) + count
                )

        except Exception as e:
            print(f"\nError processing {input_path}: {e}")
            continue

    # Print summary
    print(f"\n{'=' * 60}")
    print("Summary")
    print(f"{'=' * 60}")
    print(f"Files processed: {total_stats['files_processed']}")
    print(f"Total records: {total_stats['total_records']}")
    print(f"Records with PHI scrubbed: {total_stats['scrubbed_count']}")
    print(f"Total entities redacted: {total_stats['entity_count']}")

    if total_stats["entities_by_type"]:
        print("\nEntities by type:")
        for etype, count in sorted(
            total_stats["entities_by_type"].items(), key=lambda x: -x[1]
        ):
            print(f"  {etype}: {count}")

    if args.dry_run:
        print("\n[DRY RUN] No files were modified.")
    elif args.output_dir:
        print(f"\nScrubbed files written to: {args.output_dir}")
    else:
        print(f"\nFiles modified in-place. Backups: {'disabled' if args.no_backup else 'created (.bak)'}")

    if report_handle is not None:
        report_handle.close()
        print(f"\nRedaction report written: {args.report_path}")


if __name__ == "__main__":
    main()

```

---
### `scripts/prodigy_export_corrections.py`
- Size: `11519` bytes
```
#!/usr/bin/env python3
"""
Export Prodigy annotations to training format.

Converts Prodigy NER annotations back to BIO-tagged JSONL format
compatible with the DistilBERT training pipeline.

Usage:
    python scripts/prodigy_export_corrections.py --dataset phi_corrections --output data/ml_training/prodigy_corrected.jsonl

    # With merge into existing training data:
    python scripts/prodigy_export_corrections.py --dataset phi_corrections \
        --merge-with data/ml_training/distilled_phi_CLEANED_STANDARD.jsonl \
        --output data/ml_training/distilled_phi_WITH_CORRECTIONS.jsonl
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from transformers import AutoTokenizer

# Add repo root to path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Default paths
DEFAULT_MODEL_DIR = Path("artifacts/phi_distilbert_ner")
DEFAULT_OUTPUT = Path("data/ml_training/prodigy_corrected.jsonl")
DEFAULT_MANIFEST = Path("data/ml_training/prodigy_manifest.json")


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True, help="Prodigy dataset name to export")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output JSONL file")
    parser.add_argument("--model-dir", type=Path, default=DEFAULT_MODEL_DIR, help="Tokenizer directory")
    parser.add_argument("--merge-with", type=Path, default=None, help="Existing training data to merge with")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST, help="Manifest file to update")
    return parser.parse_args(argv)


def load_prodigy_annotations(dataset_name: str) -> List[Dict[str, Any]]:
    """Load annotations from Prodigy database."""
    try:
        from prodigy.components.db import connect

        db = connect()
        if dataset_name not in db:
            logger.error(f"Dataset '{dataset_name}' not found in Prodigy database")
            logger.info(f"Available datasets: {db.datasets}")
            return []

        examples = db.get_dataset_examples(dataset_name)
        logger.info(f"Loaded {len(examples)} annotations from Prodigy dataset '{dataset_name}'")
        return examples

    except ImportError:
        logger.error("Prodigy not installed. Install with: pip install prodigy")
        return []
    except Exception as e:
        logger.error(f"Failed to load Prodigy annotations: {e}")
        return []


def spans_to_bio(
    text: str,
    spans: List[Dict[str, Any]],
    tokenizer: Any,
) -> Tuple[List[str], List[str]]:
    """
    Convert character spans to BIO tags aligned to tokenizer output.

    Args:
        text: The original text
        spans: List of spans with start, end, label
        tokenizer: The tokenizer to use for alignment

    Returns:
        (tokens, ner_tags) tuple
    """
    # Tokenize with offset mapping
    encoding = tokenizer(
        text,
        truncation=True,
        max_length=512,
        return_offsets_mapping=True,
    )

    offset_mapping = encoding.get("offset_mapping", [])
    input_ids = encoding.get("input_ids", [])

    # Convert input_ids back to tokens
    tokens = tokenizer.convert_ids_to_tokens(input_ids)

    # Initialize all tags as O
    ner_tags = ["O"] * len(tokens)

    # Skip special tokens (CLS, SEP)
    # Special tokens have offset (0, 0)
    valid_indices = []
    for idx, offset in enumerate(offset_mapping):
        if offset[0] != 0 or offset[1] != 0:
            valid_indices.append(idx)

    # Sort spans by start position
    sorted_spans = sorted(spans, key=lambda s: s.get("start", 0))

    # Assign BIO tags based on spans
    for span in sorted_spans:
        span_start = span.get("start", 0)
        span_end = span.get("end", 0)
        label = span.get("label", "UNKNOWN")

        # Find tokens that overlap with this span
        is_first = True
        for idx in valid_indices:
            tok_start, tok_end = offset_mapping[idx]

            # Check if token overlaps with span
            if tok_start < span_end and tok_end > span_start:
                if is_first:
                    ner_tags[idx] = f"B-{label}"
                    is_first = False
                else:
                    ner_tags[idx] = f"I-{label}"

    # Filter out special tokens for output
    filtered_tokens = []
    filtered_tags = []
    for idx, (token, tag) in enumerate(zip(tokens, ner_tags)):
        offset = offset_mapping[idx] if idx < len(offset_mapping) else (0, 0)
        if offset[0] != 0 or offset[1] != 0:
            filtered_tokens.append(token)
            filtered_tags.append(tag)

    return filtered_tokens, filtered_tags


def convert_annotation(
    example: Dict[str, Any],
    tokenizer: Any,
    dataset_name: str,
) -> Optional[Dict[str, Any]]:
    """Convert a single Prodigy annotation to training format."""
    text = example.get("text", "")
    if not text:
        return None

    # Get accepted spans (Prodigy marks rejected spans)
    spans = []
    for span in example.get("spans", []):
        # In ner.correct, all spans in the final output are accepted
        spans.append(span)

    # Convert to BIO
    tokens, ner_tags = spans_to_bio(text, spans, tokenizer)

    if not tokens:
        return None

    # Extract metadata
    meta = example.get("meta", {})
    source = meta.get("source", "unknown")
    record_index = meta.get("record_index", 0)
    window_index = meta.get("window_index", 0)
    window_start = meta.get("window_start", 0)
    window_end = meta.get("window_end", len(text))

    # Build ID matching distilled format
    id_str = f"{source}:{record_index}:{window_index}"
    id_base = f"{source}:{record_index}"

    return {
        "id": id_str,
        "id_base": id_base,
        "source_path": f"prodigy:{dataset_name}",
        "record_index": record_index,
        "window_start": window_start,
        "window_end": window_end,
        "text": text,
        "tokens": tokens,
        "ner_tags": ner_tags,
        "origin": "prodigy-corrected",
        "prodigy_dataset": dataset_name,
        "annotated_at": datetime.now().isoformat(),
    }


def load_existing_data(path: Path) -> Dict[str, Dict[str, Any]]:
    """Load existing training data into a dict keyed by id."""
    data = {}
    if not path.exists():
        return data

    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                record_id = record.get("id", "")
                if record_id:
                    data[record_id] = record
            except json.JSONDecodeError:
                continue

    logger.info(f"Loaded {len(data)} existing records from {path}")
    return data


def merge_data(
    existing: Dict[str, Dict[str, Any]],
    corrections: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Merge corrections into existing data using replace strategy.

    Corrections completely replace existing records with matching IDs.
    """
    # Build a dict of corrections by ID
    corrections_by_id = {}
    for rec in corrections:
        record_id = rec.get("id", "")
        if record_id:
            corrections_by_id[record_id] = rec

    # Replace matching records
    replaced_count = 0
    for record_id in corrections_by_id:
        if record_id in existing:
            replaced_count += 1

    # Merge: start with existing, override with corrections
    merged = {**existing, **corrections_by_id}

    logger.info(f"Merged {len(corrections)} corrections into {len(existing)} existing records")
    logger.info(f"Replaced {replaced_count} existing records, added {len(corrections) - replaced_count} new records")

    # Return as list, preserving order from existing where possible
    result = []
    seen_ids: Set[str] = set()

    # First, add all existing in order (with corrections applied)
    for record_id in existing:
        if record_id in merged:
            result.append(merged[record_id])
            seen_ids.add(record_id)

    # Then add any new corrections not in existing
    for rec in corrections:
        record_id = rec.get("id", "")
        if record_id and record_id not in seen_ids:
            result.append(rec)

    return result


def update_manifest(manifest_path: Path, dataset_name: str, output_path: Path, count: int) -> None:
    """Update the manifest with export info."""
    manifest = {"batches": [], "annotated_windows": []}
    if manifest_path.exists():
        try:
            with open(manifest_path, "r") as f:
                manifest = json.load(f)
        except Exception:
            pass

    # Find the batch for this dataset and update status
    for batch in manifest.get("batches", []):
        if batch.get("prodigy_dataset") == dataset_name:
            batch["status"] = "exported"
            batch["export_file"] = str(output_path)
            batch["exported_at"] = datetime.now().isoformat()
            batch["exported_count"] = count
            break

    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv)

    # Load tokenizer
    if not args.model_dir.exists():
        logger.error(f"Model directory not found: {args.model_dir}")
        return 1

    logger.info(f"Loading tokenizer from {args.model_dir}")
    tokenizer = AutoTokenizer.from_pretrained(str(args.model_dir))

    # Load Prodigy annotations
    annotations = load_prodigy_annotations(args.dataset)
    if not annotations:
        logger.error("No annotations to export")
        return 1

    # Convert annotations to training format
    converted = []
    for example in annotations:
        # Only export accepted examples (answer == "accept")
        if example.get("answer") != "accept":
            continue

        record = convert_annotation(example, tokenizer, args.dataset)
        if record:
            converted.append(record)

    logger.info(f"Converted {len(converted)} annotations to training format")

    if not converted:
        logger.warning("No valid annotations to export")
        return 0

    # Count label distribution
    label_counts: Dict[str, int] = {}
    for rec in converted:
        for tag in rec.get("ner_tags", []):
            if tag != "O":
                label_counts[tag] = label_counts.get(tag, 0) + 1
    logger.info(f"Label distribution in corrections: {label_counts}")

    # Merge with existing data if requested
    if args.merge_with:
        existing = load_existing_data(args.merge_with)
        merged = merge_data(existing, converted)
        output_data = merged
    else:
        output_data = converted

    # Write output
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        for record in output_data:
            f.write(json.dumps(record) + "\n")

    logger.info(f"Wrote {len(output_data)} records to {args.output}")

    # Update manifest
    update_manifest(args.manifest, args.dataset, args.output, len(converted))

    return 0


if __name__ == "__main__":
    sys.exit(main())

```

---
### `scripts/export_phi_model_for_transformersjs.py`
- Size: `12126` bytes
```
#!/usr/bin/env python3
"""Export PHI DistilBERT model to a transformers.js-compatible ONNX bundle.

Target layout (Xenova/transformers.js friendly):
  <out_dir>/
    config.json
    tokenizer.json
    ...
    protected_terms.json
    onnx/model.onnx
    onnx/model_quantized.onnx (optional, opt-in)
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Iterable

# Ensure repo root is on sys.path (so `import modules.*` works when running as a script).
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from modules.phi.adapters.phi_redactor_hybrid import (
    ANATOMICAL_TERMS,
    DEVICE_MANUFACTURERS,
    PROTECTED_DEVICE_NAMES,
)

MODEL_FILES = [
    "config.json",
    "tokenizer.json",
    "tokenizer_config.json",
    "special_tokens_map.json",
    "vocab.txt",
    "label_map.json",
]

REQUIRED_ONNX_INPUTS = ("input_ids", "attention_mask")


def parse_bool(value: str | bool | None) -> bool:
    """Parse bool-ish CLI args while supporting `--flag false` and `--flag`."""
    if isinstance(value, bool):
        return value
    if value is None:
        return True
    normalized = value.strip().lower()
    if normalized in {"1", "true", "t", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "f", "no", "n", "off"}:
        return False
    raise argparse.ArgumentTypeError(f"Invalid boolean value: {value!r}")


def build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-dir", default="artifacts/phi_distilbert_ner")
    ap.add_argument(
        "--out-dir",
        default="modules/api/static/phi_redactor/vendor/phi_distilbert_ner",
    )
    ap.add_argument(
        "--quantize",
        nargs="?",
        const=True,
        default=False,
        type=parse_bool,
        help="Also export `onnx/model_quantized.onnx` (opt-in; WASM INT8 may misbehave).",
    )
    ap.add_argument(
        "--static-quantize",
        nargs="?",
        const=True,
        default=False,
        type=parse_bool,
        help="Use static quantization instead of dynamic (smaller model, ~40-50%% size reduction).",
    )
    ap.add_argument(
        "--clean",
        nargs="?",
        const=True,
        default=True,
        type=parse_bool,
        help="Remove prior export artifacts from --out-dir before exporting.",
    )
    return ap


def run(cmd: list[str]) -> None:
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError as exc:
        tool = cmd[0]
        raise RuntimeError(f"{tool} not found. Install with: pip install 'optimum[onnxruntime]'") from exc


def locate_exported_onnx(export_dir: Path) -> Path:
    """Locate the exported ONNX model within an Optimum output directory."""
    direct = [
        export_dir / "model.onnx",
        export_dir / "onnx" / "model.onnx",
    ]
    for candidate in direct:
        if candidate.exists():
            return candidate

    candidates: list[Path] = []
    candidates.extend(export_dir.glob("*.onnx"))
    onnx_subdir = export_dir / "onnx"
    if onnx_subdir.exists():
        candidates.extend(onnx_subdir.glob("*.onnx"))

    candidates = [p for p in candidates if p.is_file()]
    if not candidates:
        raise FileNotFoundError(f"No ONNX files found in Optimum export dir: {export_dir}")

    # Prefer the largest ONNX file if multiple exist.
    candidates.sort(key=lambda p: p.stat().st_size, reverse=True)
    return candidates[0]


def write_protected_terms(out_dir: Path) -> None:
    terms = {
        "anatomy_terms": sorted({t.lower() for t in ANATOMICAL_TERMS}),
        "device_manufacturers": sorted({t.lower() for t in DEVICE_MANUFACTURERS}),
        "protected_device_names": sorted({t.lower() for t in PROTECTED_DEVICE_NAMES}),
        "ln_station_regex": r"^\\d{1,2}[LRlr](?:[is])?$",
        "segment_regex": r"^[LRlr][Bb]\\d{1,2}(?:\\+\\d{1,2})?$",
        "address_markers": [
            "street",
            "st",
            "rd",
            "road",
            "ave",
            "avenue",
            "dr",
            "drive",
            "blvd",
            "boulevard",
            "lane",
            "ln",
            "zip",
            "zipcode",
            "address",
            "city",
            "state",
            "ste",
            "suite",
            "apt",
            "unit",
        ],
        "code_markers": [
            "cpt",
            "code",
            "codes",
            "billing",
            "submitted",
            "justification",
            "rvu",
            "coding",
            "radiology",
            "guidance",
            "ct",
            "modifier",
            "billed",
            "cbct",
        ],
        "station_markers": ["station", "stations", "nodes", "sampled", "ebus", "tbna", "ln"],
    }
    with open(out_dir / "protected_terms.json", "w") as f:
        json.dump(terms, f, indent=2)


def format_size(size_bytes: int) -> str:
    return f"{size_bytes / (1024 * 1024):.1f} MB"


def find_optimum_cli() -> str:
    """Find optimum-cli in the current Python environment."""
    # First try to find it in the same Python environment's bin directory
    python_bin = Path(sys.executable).parent
    optimum_cli = python_bin / "optimum-cli"
    if optimum_cli.exists():
        return str(optimum_cli)
    
    # Fall back to which (may find system version, but better than nothing)
    which_cli = shutil.which("optimum-cli")
    if which_cli:
        return which_cli

    raise RuntimeError("optimum-cli not found. Install with: pip install 'optimum[onnxruntime]'")


def validate_onnx_inputs(model_onnx: Path, required: Iterable[str] = REQUIRED_ONNX_INPUTS) -> None:
    try:
        import onnx  # type: ignore[import-untyped]
    except ImportError as exc:
        raise RuntimeError(
            "onnx is required to validate exported model signatures. Install with: pip install onnx"
        ) from exc

    m = onnx.load(str(model_onnx))
    input_names = [i.name for i in m.graph.input]
    missing = [name for name in required if name not in input_names]
    if missing:
        raise RuntimeError(
            "Re-export failed: token-classification ONNX must have attention_mask.\n"
            f"ONNX missing required inputs: {missing}. Found: {input_names}"
        )


def quantize_onnx_model(model_onnx: Path, quantized_onnx: Path, use_static: bool = False) -> None:
    """Quantize ONNX model using dynamic or static quantization.
    
    Args:
        model_onnx: Path to input ONNX model
        quantized_onnx: Path for quantized output
        use_static: If True, use static quantization (smaller but requires calibration data)
    """
    try:
        from onnxruntime.quantization import (
            QuantType,
            quantize_dynamic,
            quantize_static,
            CalibrationDataReader,
        )
        import onnxruntime as ort
        import numpy as np
    except ImportError as exc:
        raise RuntimeError(
            "onnxruntime is required for quantization. Install with: pip install onnxruntime"
        ) from exc

    quantized_onnx.parent.mkdir(parents=True, exist_ok=True)
    
    if use_static:
        # Static quantization is more aggressive but requires calibration data
        # Create a simple calibration data reader with representative tokenized inputs
        class TokenCalibrationDataReader(CalibrationDataReader):
            def __init__(self, model_path: Path):
                self.model_path = model_path
                self.data_iter = None
                # Generate representative calibration samples
                # These are dummy tokenized sequences that represent typical input
                self.calibration_samples = []
                for _ in range(10):  # Use 10 calibration samples
                    # Create varied length sequences (typical for token classification)
                    seq_len = np.random.randint(128, 512)
                    self.calibration_samples.append({
                        "input_ids": np.random.randint(0, 30000, (1, seq_len), dtype=np.int64),
                        "attention_mask": np.ones((1, seq_len), dtype=np.int64),
                    })
            
            def get_next(self):
                if self.data_iter is None:
                    self.data_iter = iter(self.calibration_samples)
                return next(self.data_iter, None)
        
        try:
            print("Performing static quantization (this may take a few minutes)...")
            quantize_static(
                str(model_onnx),
                str(quantized_onnx),
                calibration_data_reader=TokenCalibrationDataReader(model_onnx),
                weight_type=QuantType.QInt8,
                activation_type=QuantType.QUInt8,
                optimize_model=True,
            )
            print("Static quantization completed successfully.")
        except Exception as e:
            # Fallback to dynamic if static fails
            print(f"Static quantization failed ({e}), falling back to dynamic...")
            quantize_dynamic(str(model_onnx), str(quantized_onnx), weight_type=QuantType.QInt8)
    else:
        # Dynamic quantization (default - faster, no calibration needed)
        print("Performing dynamic quantization...")
        quantize_dynamic(str(model_onnx), str(quantized_onnx), weight_type=QuantType.QInt8)


def clean_export_dir(out_dir: Path) -> None:
    """Remove generated artifacts so output layout is deterministic."""
    onnx_dir = out_dir / "onnx"
    if onnx_dir.exists():
        shutil.rmtree(onnx_dir)
    for filename in [*MODEL_FILES, "protected_terms.json", "model.onnx", "model_quantized.onnx"]:
        path = out_dir / filename
        if path.exists():
            path.unlink()


def main() -> None:
    args = build_arg_parser().parse_args()
    model_dir = Path(args.model_dir)
    out_dir = Path(args.out_dir)
    if not model_dir.exists():
        raise FileNotFoundError(f"--model-dir not found: {model_dir}")

    out_dir.mkdir(parents=True, exist_ok=True)
    if args.clean:
        clean_export_dir(out_dir)

    optimum_cli = find_optimum_cli()

    onnx_dir = out_dir / "onnx"
    onnx_dir.mkdir(parents=True, exist_ok=True)
    model_path = onnx_dir / "model.onnx"

    with tempfile.TemporaryDirectory(prefix="phi_onnx_export_") as tmp:
        tmp_dir = Path(tmp)
        run(
            [
                optimum_cli,
                "export",
                "onnx",
                "--model",
                str(model_dir),
                "--task",
                "token-classification",
                str(tmp_dir),
            ]
        )
        exported_onnx = locate_exported_onnx(tmp_dir)
        shutil.copy2(exported_onnx, model_path)

    if not model_path.exists():
        raise RuntimeError("Export failed: model.onnx not found.")
    model_size = model_path.stat().st_size
    if model_size < 5_000_000:
        raise RuntimeError("Export failed: model.onnx is unexpectedly small.")
    validate_onnx_inputs(model_path)
    print(f"Exported model.onnx size: {format_size(model_size)}")

    if args.quantize:
        quantized_path = onnx_dir / "model_quantized.onnx"
        quantize_onnx_model(model_path, quantized_path, use_static=args.static_quantize)
        if not quantized_path.exists() or quantized_path.stat().st_size < 5_000_000:
            raise RuntimeError("Quantization failed: model_quantized.onnx missing or too small.")
        validate_onnx_inputs(quantized_path)
        quantized_size = quantized_path.stat().st_size
        reduction_pct = (1 - quantized_size / model_size) * 100
        print(f"Quantized model_quantized.onnx size: {format_size(quantized_size)} ({reduction_pct:.1f}% reduction)")

    for name in MODEL_FILES:
        src = model_dir / name
        if src.exists():
            shutil.copy2(src, out_dir / name)

    write_protected_terms(out_dir)


if __name__ == "__main__":
    main()

```

---
### `scripts/convert_spans_to_bio.py`
- Size: `12153` bytes
```
#!/usr/bin/env python3
"""
Convert character-span NER annotations to BIO-tagged format for training.

Input format (ner_dataset_all.jsonl):
{
  "id": "note_001",
  "text": "Full procedure note text...",
  "entities": [
    {"start": 100, "end": 102, "label": "ANAT_LN_STATION", "text": "4R"},
    ...
  ]
}

Output format (for train_registry_ner.py):
{
  "id": "note_001",
  "tokens": ["station", "4", "##r", "was", "sampled", ...],
  "ner_tags": ["O", "B-ANAT_LN_STATION", "I-ANAT_LN_STATION", "O", "O", ...]
}

Usage:
    python scripts/convert_spans_to_bio.py \
        --input data/ml_training/granular_ner/ner_dataset_all.jsonl \
        --output data/ml_training/granular_ner/ner_bio_format.jsonl \
        --model microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

from transformers import AutoTokenizer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", "-i",
        type=Path,
        required=True,
        help="Input JSONL file with character-span annotations"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        required=True,
        help="Output JSONL file with BIO-tagged tokens"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext",
        help="Tokenizer model name (default: microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext)"
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=512,
        help="Maximum sequence length (default: 512)"
    )
    parser.add_argument(
        "--window-size",
        type=int,
        default=None,
        help="If set, split long texts into overlapping windows of this many chars"
    )
    parser.add_argument(
        "--window-overlap",
        type=int,
        default=200,
        help="Overlap between windows in characters (default: 200)"
    )
    return parser.parse_args(argv)


def normalize_entity(entity: Any) -> Dict[str, Any]:
    """
    Normalize entity to dict format.

    Handles both formats:
    - Dict: {"start": 100, "end": 102, "label": "ANAT_LN_STATION", "text": "4R"}
    - List: [100, 102, "ANAT_LN_STATION"] or [100, 102, "ANAT_LN_STATION", "4R"]
    """
    if isinstance(entity, dict):
        start = entity.get("start")
        end = entity.get("end")
        if start is None:
            start = entity.get("start_char", entity.get("start_offset", 0))
        if end is None:
            end = entity.get("end_char", entity.get("end_offset", 0))
        text = entity.get("text")
        if text is None:
            text = entity.get("span_text", "")
        return {
            "start": start,
            "end": end,
            "label": entity.get("label", "UNKNOWN"),
            "text": text or "",
        }
    elif isinstance(entity, (list, tuple)):
        if len(entity) >= 3:
            return {
                "start": entity[0],
                "end": entity[1],
                "label": entity[2],
                "text": entity[3] if len(entity) > 3 else "",
            }
    return {"start": 0, "end": 0, "label": "UNKNOWN", "text": ""}


def spans_to_bio(
    text: str,
    entities: List[Any],
    tokenizer: Any,
    max_length: int = 512,
) -> Tuple[List[str], List[str]]:
    """
    Convert character spans to BIO tags aligned to tokenizer output.

    Args:
        text: The original text
        entities: List of entities (dict or list format)
        tokenizer: The tokenizer to use for alignment
        max_length: Maximum sequence length

    Returns:
        (tokens, ner_tags) tuple with special tokens filtered out
    """
    # Normalize all entities to dict format
    normalized_entities = [normalize_entity(e) for e in entities]

    # Tokenize with offset mapping
    encoding = tokenizer(
        text,
        truncation=True,
        max_length=max_length,
        return_offsets_mapping=True,
        add_special_tokens=True,
    )

    offset_mapping = encoding.get("offset_mapping", [])
    input_ids = encoding.get("input_ids", [])

    # Convert input_ids back to tokens
    tokens = tokenizer.convert_ids_to_tokens(input_ids)

    # Initialize all tags as O
    ner_tags = ["O"] * len(tokens)

    # Find valid token indices (non-special tokens)
    # Special tokens like [CLS], [SEP] have offset (0, 0)
    valid_indices = []
    for idx, offset in enumerate(offset_mapping):
        if offset[0] != offset[1]:  # Has non-zero span
            valid_indices.append(idx)

    # Sort entities by start position
    sorted_entities = sorted(normalized_entities, key=lambda e: e.get("start", 0))

    # Assign BIO tags based on entity spans
    for entity in sorted_entities:
        span_start = entity.get("start", 0)
        span_end = entity.get("end", 0)
        label = entity.get("label", "UNKNOWN")

        # Find tokens that overlap with this entity span
        is_first = True
        for idx in valid_indices:
            tok_start, tok_end = offset_mapping[idx]

            # Check if token overlaps with entity span
            if tok_start < span_end and tok_end > span_start:
                if is_first:
                    ner_tags[idx] = f"B-{label}"
                    is_first = False
                else:
                    ner_tags[idx] = f"I-{label}"

    # Filter out special tokens for output
    filtered_tokens = []
    filtered_tags = []
    for idx, (token, tag) in enumerate(zip(tokens, ner_tags)):
        offset = offset_mapping[idx] if idx < len(offset_mapping) else (0, 0)
        # Include tokens with actual character spans
        if offset[0] != offset[1]:
            filtered_tokens.append(token)
            filtered_tags.append(tag)

    return filtered_tokens, filtered_tags


def split_into_windows(
    text: str,
    entities: List[Any],
    window_size: int,
    window_overlap: int,
) -> List[Tuple[str, List[Dict[str, Any]], int]]:
    """
    Split long text into overlapping windows with adjusted entity spans.

    Returns list of (window_text, adjusted_entities, window_start) tuples.
    """
    # Normalize all entities to dict format
    normalized_entities = [normalize_entity(e) for e in entities]

    windows = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + window_size, text_len)

        # Try to break at a sentence boundary if possible
        if end < text_len:
            # Look for sentence end markers in last 100 chars
            search_region = text[max(end - 100, start):end]
            for marker in [". ", ".\n", "! ", "? "]:
                last_marker = search_region.rfind(marker)
                if last_marker != -1:
                    end = max(end - 100, start) + last_marker + len(marker)
                    break

        window_text = text[start:end]

        # Adjust entity spans to window coordinates
        window_entities = []
        for entity in normalized_entities:
            ent_start = entity.get("start", 0)
            ent_end = entity.get("end", 0)

            # Check if entity overlaps with window
            if ent_start < end and ent_end > start:
                # Clip entity to window boundaries
                adj_start = max(0, ent_start - start)
                adj_end = min(end - start, ent_end - start)

                # Only include if entity has meaningful overlap
                if adj_end > adj_start:
                    window_entities.append({
                        "start": adj_start,
                        "end": adj_end,
                        "label": entity["label"],
                        "text": window_text[adj_start:adj_end],
                    })

        windows.append((window_text, window_entities, start))

        # Move to next window
        if end >= text_len:
            break
        start = end - window_overlap

    return windows


def convert_record(
    record: Dict[str, Any],
    tokenizer: Any,
    max_length: int,
    window_size: int | None,
    window_overlap: int,
) -> List[Dict[str, Any]]:
    """
    Convert a single record from span format to BIO format.

    May return multiple records if windowing is enabled.
    """
    record_id = record.get("id", "unknown")
    text = record.get("text", "")
    entities = record.get("entities", [])

    if not text:
        return []

    results = []

    if window_size and len(text) > window_size:
        # Split into windows
        windows = split_into_windows(text, entities, window_size, window_overlap)
        for idx, (window_text, window_entities, window_start) in enumerate(windows):
            tokens, ner_tags = spans_to_bio(
                window_text, window_entities, tokenizer, max_length
            )
            if tokens:
                results.append({
                    "id": f"{record_id}:w{idx}",
                    "id_base": record_id,
                    "window_index": idx,
                    "window_start": window_start,
                    "window_end": window_start + len(window_text),
                    "tokens": tokens,
                    "ner_tags": ner_tags,
                })
    else:
        # Process entire text
        tokens, ner_tags = spans_to_bio(text, entities, tokenizer, max_length)
        if tokens:
            results.append({
                "id": record_id,
                "tokens": tokens,
                "ner_tags": ner_tags,
            })

    return results


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv)

    # Load tokenizer
    logger.info(f"Loading tokenizer: {args.model}")
    tokenizer = AutoTokenizer.from_pretrained(args.model)

    # Read input
    logger.info(f"Reading input: {args.input}")
    records = []
    with open(args.input, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    logger.info(f"Loaded {len(records)} records")

    # Convert records
    output_records = []
    label_counts = {}
    total_tokens = 0

    for record in records:
        converted = convert_record(
            record,
            tokenizer,
            args.max_length,
            args.window_size,
            args.window_overlap,
        )
        for rec in converted:
            output_records.append(rec)
            total_tokens += len(rec["tokens"])

            # Count labels
            for tag in rec["ner_tags"]:
                if tag != "O":
                    # Extract base label (remove B-/I- prefix)
                    base_label = tag.split("-", 1)[-1] if "-" in tag else tag
                    label_counts[base_label] = label_counts.get(base_label, 0) + 1

    logger.info(f"Generated {len(output_records)} output records")
    logger.info(f"Total tokens: {total_tokens}")
    logger.info(f"Label distribution: {json.dumps(label_counts, indent=2)}")

    # Write output
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        for rec in output_records:
            f.write(json.dumps(rec) + "\n")

    logger.info(f"Wrote output to: {args.output}")

    # Write stats
    stats_path = args.output.with_suffix(".stats.json")
    stats = {
        "input_records": len(records),
        "output_records": len(output_records),
        "total_tokens": total_tokens,
        "label_counts": label_counts,
        "model": args.model,
        "max_length": args.max_length,
        "window_size": args.window_size,
        "window_overlap": args.window_overlap,
    }
    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2)

    logger.info(f"Wrote stats to: {stats_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

```

---
### `scripts/extract_ner_from_excel.py`
- Size: `13507` bytes
```
#!/usr/bin/env python3
"""
Extract NER training data from granular annotation Excel files.

Reads phase0_extraction_note_*.xlsx files and outputs:
- ner_dataset_all.jsonl: Primary training format (one line per note with entities)
- notes.jsonl: Debug file with note texts
- spans.jsonl: Debug file with all spans
- stats.json: Label distribution and statistics
- alignment_warnings.log: Whitespace drift issues

Usage:
    python scripts/extract_ner_from_excel.py \
        --input-dir "data/granular annotations/phase0_excels" \
        --output-dir data/ml_training/granular_ner
"""

import argparse
import json
import logging
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

import openpyxl

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class Span:
    note_id: str
    label: str
    span_text: str
    start_char: int
    end_char: int
    hydration_status: str
    # Validation results
    is_valid: bool = True
    validation_note: str = ""


@dataclass
class Note:
    note_id: str
    note_text: str
    source_file: str


def normalize_whitespace(text: str) -> str:
    """Collapse all whitespace to single spaces."""
    return " ".join(text.split())


def validate_span(span: Span, note_text: str) -> tuple[bool, str]:
    """
    Validate that span text matches note text at given offsets.

    Returns:
        (is_valid, validation_note)
        - is_valid: True if exact match
        - validation_note: 'exact_match', 'alignment_warning', or 'alignment_error'
    """
    if span.start_char is None or span.end_char is None:
        return False, "alignment_error: missing offsets"

    try:
        extracted = note_text[span.start_char:span.end_char]
    except (IndexError, TypeError):
        return False, f"alignment_error: invalid offsets [{span.start_char}:{span.end_char}]"

    # Check exact match
    if extracted == span.span_text:
        return True, "exact_match"

    # Check normalized match (whitespace only)
    if normalize_whitespace(extracted) == normalize_whitespace(span.span_text):
        return True, "alignment_warning: whitespace mismatch"

    # Complete mismatch
    return False, f"alignment_error: extracted='{extracted[:50]}...' vs span='{span.span_text[:50]}...'"


def read_excel_file(excel_path: Path) -> tuple[Optional[Note], list[Span]]:
    """
    Read an annotation Excel file and extract note + spans.

    Returns:
        (Note or None, list of Spans)
    """
    try:
        wb = openpyxl.load_workbook(excel_path, read_only=True, data_only=True)
    except Exception as e:
        logger.error(f"Failed to open {excel_path}: {e}")
        return None, []

    note = None
    spans = []

    # Read Note_Text sheet
    if "Note_Text" in wb.sheetnames:
        ws = wb["Note_Text"]
        rows = list(ws.iter_rows(values_only=True))
        if len(rows) >= 2:
            headers = [str(h).lower() if h else "" for h in rows[0]]
            try:
                note_id_idx = headers.index("note_id")
                note_text_idx = headers.index("note_text")

                # Find first actual data row (skip duplicate headers and empty rows)
                for data_row in rows[1:]:
                    if not data_row or not data_row[note_id_idx]:
                        continue
                    # Skip rows that look like headers (note_id column contains "note_id")
                    if str(data_row[note_id_idx]).lower() == "note_id":
                        continue
                    note = Note(
                        note_id=str(data_row[note_id_idx] or ""),
                        note_text=str(data_row[note_text_idx] or ""),
                        source_file=excel_path.name
                    )
                    break
            except (ValueError, IndexError) as e:
                logger.warning(f"Note_Text sheet missing required columns in {excel_path}: {e}")

    # Read Span_Hydrated sheet
    if "Span_Hydrated" in wb.sheetnames:
        ws = wb["Span_Hydrated"]
        rows = list(ws.iter_rows(values_only=True))
        if len(rows) >= 2:
            headers = [str(h).lower() if h else "" for h in rows[0]]

            # Find required column indices
            try:
                note_id_idx = headers.index("note_id")
                label_idx = headers.index("label")
                span_text_idx = headers.index("span_text")
                start_idx = headers.index("start_char")
                end_idx = headers.index("end_char")
                status_idx = headers.index("hydration_status")
            except ValueError as e:
                logger.warning(f"Span_Hydrated sheet missing columns in {excel_path}: {e}")
                return note, spans

            # Extract spans
            for row in rows[1:]:
                if not row or len(row) <= max(note_id_idx, label_idx, span_text_idx, start_idx, end_idx, status_idx):
                    continue

                # Skip empty rows (all None) and header-like rows
                if row[note_id_idx] is None or str(row[note_id_idx]).lower() == "note_id":
                    continue

                hydration_status = str(row[status_idx] or "")

                # Filter: only keep hydrated spans
                if not hydration_status.startswith("hydrated_"):
                    continue

                # Parse start/end as integers
                try:
                    start_char = int(row[start_idx]) if row[start_idx] else None
                    end_char = int(row[end_idx]) if row[end_idx] else None
                except (ValueError, TypeError):
                    start_char = None
                    end_char = None

                if start_char is None or end_char is None:
                    continue

                span = Span(
                    note_id=str(row[note_id_idx] or ""),
                    label=str(row[label_idx] or ""),
                    span_text=str(row[span_text_idx] or ""),
                    start_char=start_char,
                    end_char=end_char,
                    hydration_status=hydration_status
                )
                spans.append(span)

    wb.close()
    return note, spans


def process_excel_files(input_dir: Path) -> tuple[list[Note], list[Span], dict]:
    """
    Process all Excel files in the input directory.

    Returns:
        (list of Notes, list of Spans, stats dict)
    """
    all_notes = []
    all_spans = []
    stats = {
        "total_files": 0,
        "successful_files": 0,
        "total_notes": 0,
        "total_spans_raw": 0,
        "total_spans_valid": 0,
        "alignment_warnings": 0,
        "alignment_errors": 0,
        "label_counts": Counter(),
        "hydration_status_counts": Counter()
    }

    excel_files = sorted(input_dir.glob("phase0_extraction_*.xlsx"))
    stats["total_files"] = len(excel_files)

    logger.info(f"Found {len(excel_files)} Excel files in {input_dir}")

    alignment_warnings = []

    for excel_path in excel_files:
        note, spans = read_excel_file(excel_path)

        if note is None:
            logger.warning(f"No note found in {excel_path.name}")
            continue

        stats["successful_files"] += 1
        stats["total_notes"] += 1
        all_notes.append(note)

        # Validate each span
        for span in spans:
            stats["total_spans_raw"] += 1
            stats["hydration_status_counts"][span.hydration_status] += 1

            is_valid, validation_note = validate_span(span, note.note_text)
            span.is_valid = is_valid
            span.validation_note = validation_note

            if "alignment_warning" in validation_note:
                stats["alignment_warnings"] += 1
                alignment_warnings.append({
                    "note_id": span.note_id,
                    "label": span.label,
                    "span_text": span.span_text[:50],
                    "start": span.start_char,
                    "end": span.end_char,
                    "issue": validation_note
                })
            elif "alignment_error" in validation_note:
                stats["alignment_errors"] += 1
                alignment_warnings.append({
                    "note_id": span.note_id,
                    "label": span.label,
                    "span_text": span.span_text[:50],
                    "start": span.start_char,
                    "end": span.end_char,
                    "issue": validation_note
                })
                continue  # Skip invalid spans

            if is_valid:
                stats["total_spans_valid"] += 1
                stats["label_counts"][span.label] += 1
                all_spans.append(span)

    stats["label_counts"] = dict(stats["label_counts"].most_common())
    stats["hydration_status_counts"] = dict(stats["hydration_status_counts"])
    stats["alignment_issues"] = alignment_warnings

    return all_notes, all_spans, stats


def write_outputs(notes: list[Note], spans: list[Span], stats: dict, output_dir: Path):
    """Write all output files."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Group spans by note_id
    spans_by_note = defaultdict(list)
    for span in spans:
        spans_by_note[span.note_id].append(span)

    # 1. Primary output: ner_dataset_all.jsonl
    ner_path = output_dir / "ner_dataset_all.jsonl"
    with open(ner_path, "w") as f:
        for note in notes:
            note_spans = spans_by_note.get(note.note_id, [])
            # Sort entities by start position
            entities = sorted([
                {
                    "start": s.start_char,
                    "end": s.end_char,
                    "label": s.label,
                    "text": s.span_text
                }
                for s in note_spans
            ], key=lambda x: x["start"])

            record = {
                "id": note.note_id,
                "text": note.note_text,
                "entities": entities
            }
            f.write(json.dumps(record) + "\n")
    logger.info(f"Wrote {len(notes)} records to {ner_path}")

    # 2. Debug: notes.jsonl
    notes_path = output_dir / "notes.jsonl"
    with open(notes_path, "w") as f:
        for note in notes:
            f.write(json.dumps({"note_id": note.note_id, "note_text": note.note_text}) + "\n")
    logger.info(f"Wrote {len(notes)} notes to {notes_path}")

    # 3. Debug: spans.jsonl
    spans_path = output_dir / "spans.jsonl"
    with open(spans_path, "w") as f:
        for span in spans:
            f.write(json.dumps({
                "note_id": span.note_id,
                "label": span.label,
                "span_text": span.span_text,
                "start_char": span.start_char,
                "end_char": span.end_char,
                "hydration_status": span.hydration_status
            }) + "\n")
    logger.info(f"Wrote {len(spans)} spans to {spans_path}")

    # 4. Stats
    stats_path = output_dir / "stats.json"
    # Remove alignment_issues from stats for cleaner output
    alignment_issues = stats.pop("alignment_issues", [])
    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2)
    logger.info(f"Wrote stats to {stats_path}")

    # 5. Alignment warnings log
    if alignment_issues:
        warnings_path = output_dir / "alignment_warnings.log"
        with open(warnings_path, "w") as f:
            for issue in alignment_issues:
                f.write(json.dumps(issue) + "\n")
        logger.warning(f"Wrote {len(alignment_issues)} alignment issues to {warnings_path}")


def main():
    parser = argparse.ArgumentParser(description="Extract NER training data from Excel files")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("data/granular annotations/phase0_excels"),
        help="Directory containing phase0_extraction_*.xlsx files"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/ml_training/granular_ner"),
        help="Directory for output files"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print stats without writing files"
    )
    args = parser.parse_args()

    logger.info(f"Input directory: {args.input_dir}")
    logger.info(f"Output directory: {args.output_dir}")

    if not args.input_dir.exists():
        logger.error(f"Input directory does not exist: {args.input_dir}")
        return 1

    notes, spans, stats = process_excel_files(args.input_dir)

    # Print summary
    print("\n=== Extraction Summary ===")
    print(f"Files processed: {stats['successful_files']}/{stats['total_files']}")
    print(f"Notes extracted: {stats['total_notes']}")
    print(f"Spans (raw): {stats['total_spans_raw']}")
    print(f"Spans (valid): {stats['total_spans_valid']}")
    print(f"Alignment warnings: {stats['alignment_warnings']}")
    print(f"Alignment errors: {stats['alignment_errors']}")
    print(f"\nLabel distribution (top 10):")
    for label, count in list(stats['label_counts'].items())[:10]:
        print(f"  {label}: {count}")

    if args.dry_run:
        print("\n[Dry run - no files written]")
        return 0

    write_outputs(notes, spans, stats, args.output_dir)

    print(f"\nOutput written to: {args.output_dir}")
    return 0


if __name__ == "__main__":
    exit(main())

```

---
### `scripts/review_llm_fallback_errors.py`
- Size: `14532` bytes
```
#!/usr/bin/env python3
"""
Error review pipeline for LLM fallback cases.

Identifies cases where:
- source="hybrid_llm_fallback" (LLM was used as final judge)
- prediction ≠ golden codes (the output was incorrect)

Outputs a review file with detailed context for manual inspection
and potential addition to training data.

Usage:
    python scripts/review_llm_fallback_errors.py
    python scripts/review_llm_fallback_errors.py --input data/eval_results/eval_errors_*.jsonl
    python scripts/review_llm_fallback_errors.py --run-fresh  # Re-run evaluation first
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set

import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


@dataclass
class ReviewCase:
    """A case requiring review."""
    idx: int
    dataset: str
    note_preview: str
    gold_codes: List[str]
    predicted_codes: List[str]
    ml_only_codes: List[str]
    source: str
    difficulty: str
    false_positives: List[str]
    false_negatives: List[str]
    fallback_reason: str = ""
    rules_error: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "idx": self.idx,
            "dataset": self.dataset,
            "note_preview": self.note_preview,
            "gold_codes": self.gold_codes,
            "predicted_codes": self.predicted_codes,
            "ml_only_codes": self.ml_only_codes,
            "source": self.source,
            "difficulty": self.difficulty,
            "false_positives": self.false_positives,
            "false_negatives": self.false_negatives,
            "fallback_reason": self.fallback_reason,
            "rules_error": self.rules_error,
        }


def load_errors_from_jsonl(path: Path) -> List[Dict[str, Any]]:
    """Load error cases from JSONL file."""
    errors = []
    with open(path) as f:
        for line in f:
            if line.strip():
                errors.append(json.loads(line))
    return errors


def filter_llm_fallback_errors(errors: List[Dict[str, Any]]) -> List[ReviewCase]:
    """Filter to only LLM fallback cases with prediction errors."""
    return filter_errors_by_source(errors, source_filter="hybrid_llm_fallback")


def filter_fastpath_errors(errors: List[Dict[str, Any]]) -> List[ReviewCase]:
    """Filter to only fast path (ML+Rules) cases with prediction errors."""
    return filter_errors_by_source(errors, source_filter="ml_rules_fastpath")


def filter_errors_by_source(
    errors: List[Dict[str, Any]],
    source_filter: str | None = None,
) -> List[ReviewCase]:
    """Filter errors by source type."""
    review_cases = []

    for error in errors:
        source = error.get("source", "")

        # Apply source filter if specified
        if source_filter and source != source_filter:
            continue

        # Skip if it was an exception, not a prediction error
        if "error" in error and "gold" not in error:
            continue

        review_cases.append(ReviewCase(
            idx=error.get("idx", -1),
            dataset=error.get("dataset", "unknown"),
            note_preview=error.get("note_preview", ""),
            gold_codes=error.get("gold", []),
            predicted_codes=error.get("predicted", []),
            ml_only_codes=error.get("ml_only", []),
            source=source,
            difficulty=error.get("difficulty", "unknown"),
            false_positives=error.get("false_positives", []),
            false_negatives=error.get("false_negatives", []),
            fallback_reason=error.get("reason_for_fallback", ""),
            rules_error=error.get("rules_error", ""),
        ))

    return review_cases


def analyze_error_patterns(cases: List[ReviewCase]) -> Dict[str, Any]:
    """Analyze patterns in error cases."""
    analysis = {
        "total_llm_fallback_errors": len(cases),
        "by_difficulty": defaultdict(int),
        "by_fallback_reason": defaultdict(int),
        "common_false_positives": defaultdict(int),
        "common_false_negatives": defaultdict(int),
        "ml_would_have_been_correct": 0,
        "ml_partial_overlap": 0,
    }

    for case in cases:
        analysis["by_difficulty"][case.difficulty] += 1

        # Parse fallback reason
        if "gray_zone" in case.fallback_reason:
            analysis["by_fallback_reason"]["gray_zone"] += 1
        elif "low_confidence" in case.fallback_reason:
            analysis["by_fallback_reason"]["low_confidence"] += 1
        elif "rule_conflict" in case.fallback_reason:
            analysis["by_fallback_reason"]["rule_conflict"] += 1
        else:
            analysis["by_fallback_reason"]["other"] += 1

        # Track common error codes
        for code in case.false_positives:
            analysis["common_false_positives"][code] += 1
        for code in case.false_negatives:
            analysis["common_false_negatives"][code] += 1

        # Check if ML alone would have been correct
        gold_set = set(case.gold_codes)
        ml_set = set(case.ml_only_codes)
        if ml_set == gold_set:
            analysis["ml_would_have_been_correct"] += 1
        elif ml_set & gold_set:
            analysis["ml_partial_overlap"] += 1

    # Convert defaultdicts to regular dicts for JSON serialization
    analysis["by_difficulty"] = dict(analysis["by_difficulty"])
    analysis["by_fallback_reason"] = dict(analysis["by_fallback_reason"])
    analysis["common_false_positives"] = dict(
        sorted(analysis["common_false_positives"].items(), key=lambda x: -x[1])[:10]
    )
    analysis["common_false_negatives"] = dict(
        sorted(analysis["common_false_negatives"].items(), key=lambda x: -x[1])[:10]
    )

    return analysis


def generate_review_report(
    cases: List[ReviewCase],
    analysis: Dict[str, Any],
    output_dir: Path,
    report_prefix: str = "llm_fallback",
) -> Path:
    """Generate a human-readable review report."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = output_dir / f"{report_prefix}_review_{timestamp}.md"

    with open(report_path, "w") as f:
        title = report_prefix.replace("_", " ").title()
        f.write(f"# {title} Error Review Report\n\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n\n")

        f.write("## Summary\n\n")
        f.write(f"- Total errors reviewed: **{analysis['total_llm_fallback_errors']}**\n")
        f.write(f"- Cases where ML alone was correct: {analysis['ml_would_have_been_correct']}\n")
        f.write(f"- Cases where ML had partial overlap: {analysis['ml_partial_overlap']}\n\n")

        f.write("### Errors by Difficulty\n\n")
        for diff, count in sorted(analysis["by_difficulty"].items()):
            f.write(f"- {diff}: {count}\n")

        f.write("\n### Errors by Fallback Reason\n\n")
        for reason, count in sorted(analysis["by_fallback_reason"].items()):
            f.write(f"- {reason}: {count}\n")

        f.write("\n### Common False Positives (LLM suggested but shouldn't have)\n\n")
        for code, count in analysis["common_false_positives"].items():
            f.write(f"- {code}: {count} occurrences\n")

        f.write("\n### Common False Negatives (LLM missed)\n\n")
        for code, count in analysis["common_false_negatives"].items():
            f.write(f"- {code}: {count} occurrences\n")

        f.write("\n---\n\n")
        f.write("## Cases for Review\n\n")

        for i, case in enumerate(cases, 1):
            f.write(f"### Case {i} (idx={case.idx}, {case.dataset})\n\n")
            f.write(f"**Difficulty:** {case.difficulty}\n\n")
            f.write(f"**Fallback Reason:** {case.fallback_reason or 'N/A'}\n\n")

            if case.rules_error:
                f.write(f"**Rules Error:** {case.rules_error}\n\n")

            f.write("**Codes:**\n")
            f.write(f"- Gold: `{', '.join(case.gold_codes)}`\n")
            f.write(f"- Predicted: `{', '.join(case.predicted_codes)}`\n")
            f.write(f"- ML-only: `{', '.join(case.ml_only_codes)}`\n\n")

            if case.false_positives:
                f.write(f"- ❌ False Positives: `{', '.join(case.false_positives)}`\n")
            if case.false_negatives:
                f.write(f"- ⚠️ False Negatives: `{', '.join(case.false_negatives)}`\n")

            f.write("\n**Note Preview:**\n")
            f.write("```\n")
            f.write(case.note_preview[:500])
            if len(case.note_preview) > 500:
                f.write("...[truncated]")
            f.write("\n```\n\n")

            # Actionable recommendation
            f.write("**Recommendation:** ")
            if set(case.ml_only_codes) == set(case.gold_codes):
                f.write("ML was correct but LLM overrode it. Review LLM prompt constraints.\n")
            elif case.false_negatives and not case.false_positives:
                f.write("LLM missed codes. Consider adding to training data or improving prompt.\n")
            elif case.false_positives and not case.false_negatives:
                f.write("LLM hallucinated codes. Review prompt constraints for these codes.\n")
            else:
                f.write("Mixed errors. Manual review needed.\n")

            f.write("\n---\n\n")

    return report_path


def run_fresh_evaluation() -> Path:
    """Run the evaluation script and return the errors file path."""
    import subprocess

    print("Running fresh evaluation...")
    result = subprocess.run(
        ["python3", "scripts/eval_hybrid_pipeline.py"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"Evaluation failed: {result.stderr}")
        raise RuntimeError("Evaluation failed")

    # Find the most recent errors file
    errors_dir = Path("data/eval_results")
    errors_files = sorted(errors_dir.glob("eval_errors_*.jsonl"), reverse=True)
    if not errors_files:
        raise FileNotFoundError("No errors file found after evaluation")

    return errors_files[0]


def main():
    parser = argparse.ArgumentParser(description="Review pipeline prediction errors")
    parser.add_argument(
        "--input",
        type=Path,
        help="Path to errors JSONL file (default: most recent in data/eval_results/)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/eval_results"),
        help="Output directory for review report",
    )
    parser.add_argument(
        "--run-fresh",
        action="store_true",
        help="Run fresh evaluation before analyzing errors",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Also output cases as JSON for programmatic use",
    )
    parser.add_argument(
        "--mode",
        choices=["llm_fallback", "fastpath", "all"],
        default="all",
        help="Which errors to review: llm_fallback, fastpath, or all (default: all)",
    )
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Find or generate errors file
    if args.run_fresh:
        errors_path = run_fresh_evaluation()
    elif args.input:
        errors_path = args.input
    else:
        # Find most recent errors file
        errors_dir = Path("data/eval_results")
        errors_files = sorted(errors_dir.glob("eval_errors_*.jsonl"), reverse=True)
        if not errors_files:
            print("No errors file found. Run with --run-fresh to generate one.")
            return
        errors_path = errors_files[0]

    print(f"Loading errors from: {errors_path}")
    errors = load_errors_from_jsonl(errors_path)
    print(f"  Total error entries: {len(errors)}")

    # Filter errors based on mode
    if args.mode == "llm_fallback":
        review_cases = filter_llm_fallback_errors(errors)
        report_prefix = "llm_fallback"
        mode_desc = "LLM fallback"
    elif args.mode == "fastpath":
        review_cases = filter_fastpath_errors(errors)
        report_prefix = "fastpath"
        mode_desc = "fast path (ML+Rules)"
    else:
        review_cases = filter_errors_by_source(errors, source_filter=None)
        report_prefix = "all_errors"
        mode_desc = "all"

    print(f"  {mode_desc.capitalize()} errors: {len(review_cases)}")

    if not review_cases:
        print(f"No {mode_desc} errors found. The pipeline is performing well!")
        return

    # Analyze patterns
    analysis = analyze_error_patterns(review_cases)

    # Generate report
    report_path = generate_review_report(
        review_cases, analysis, args.output_dir, report_prefix=report_prefix
    )
    print(f"\nReview report saved to: {report_path}")

    # Optionally output JSON
    if args.json:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = args.output_dir / f"{report_prefix}_cases_{timestamp}.json"
        with open(json_path, "w") as f:
            json.dump({
                "analysis": analysis,
                "cases": [c.to_dict() for c in review_cases],
            }, f, indent=2)
        print(f"JSON output saved to: {json_path}")

    # Print summary
    print("\n" + "=" * 60)
    print(f"SUMMARY ({mode_desc.upper()} ERRORS)")
    print("=" * 60)
    print(f"Total errors: {len(review_cases)}")

    # Break down by source if showing all
    if args.mode == "all":
        by_source = defaultdict(int)
        for case in review_cases:
            by_source[case.source] += 1
        print("\nBy source:")
        for source, count in sorted(by_source.items(), key=lambda x: -x[1]):
            print(f"  {source}: {count}")

    print(f"\nCases where ML alone was correct: {analysis['ml_would_have_been_correct']}")
    print(f"\nBy difficulty:")
    for diff, count in sorted(analysis["by_difficulty"].items(), key=lambda x: -x[1]):
        print(f"  {diff}: {count}")

    if analysis["by_fallback_reason"]:
        print(f"\nBy fallback reason:")
        for reason, count in sorted(analysis["by_fallback_reason"].items(), key=lambda x: -x[1]):
            print(f"  {reason}: {count}")

    print(f"\nTop false positive codes (predicted but shouldn't have):")
    for code, count in list(analysis["common_false_positives"].items())[:5]:
        print(f"  {code}: {count}")
    print(f"\nTop false negative codes (missed):")
    for code, count in list(analysis["common_false_negatives"].items())[:5]:
        print(f"  {code}: {count}")


if __name__ == "__main__":
    main()

```

---
### `scripts/quantize_to_onnx.py`
- Size: `14742` bytes
```
#!/usr/bin/env python3
"""Export trained BiomedBERT model to ONNX and apply INT8 quantization.

This script converts the trained PyTorch model to ONNX format and applies
dynamic INT8 quantization for efficient CPU inference on Railway.

Results:
- Model size: ~440MB -> ~110MB
- Inference speed: ~3x faster
- Accuracy loss: < 1%

Usage:
    python scripts/quantize_to_onnx.py --model-dir data/models/roberta_registry
    python scripts/quantize_to_onnx.py --model-dir data/models/roberta_registry --validate
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import torch
import torch.nn as nn
from transformers import AutoConfig, AutoModel, AutoTokenizer

if TYPE_CHECKING:
    import onnxruntime as ort


# ============================================================================
# Model Definition (must match training script)
# ============================================================================

class BiomedBERTMultiLabel(nn.Module):
    """BiomedBERT with multi-label classification head."""

    def __init__(
        self,
        model_name: str,
        num_labels: int,
        pos_weight: torch.Tensor | None = None,
        dropout: float = 0.1,
    ):
        super().__init__()

        self.config = AutoConfig.from_pretrained(model_name)
        self.bert = AutoModel.from_pretrained(model_name)
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(self.config.hidden_size, num_labels)

        if pos_weight is not None:
            self.register_buffer("pos_weight", pos_weight)
        else:
            self.pos_weight = None

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
    ) -> torch.Tensor:
        """Forward pass returning logits only (no loss for inference)."""
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled = outputs.last_hidden_state[:, 0, :]
        pooled = self.dropout(pooled)
        logits = self.classifier(pooled)
        return logits

    @classmethod
    def from_pretrained(cls, path: Path, num_labels: int) -> "BiomedBERTMultiLabel":
        """Load model from directory."""
        path = Path(path)

        # Load pos_weight if present
        pos_weight_path = path / "pos_weight.pt"
        pos_weight = torch.load(pos_weight_path, map_location="cpu") if pos_weight_path.exists() else None

        # Create model
        model = cls(
            model_name=str(path),
            num_labels=num_labels,
            pos_weight=pos_weight,
        )

        # Load classifier weights
        classifier_path = path / "classifier.pt"
        if classifier_path.exists():
            model.classifier.load_state_dict(torch.load(classifier_path, map_location="cpu"))

        return model


# ============================================================================
# ONNX Export
# ============================================================================

def export_to_onnx(
    model: BiomedBERTMultiLabel,
    output_path: Path,
    max_length: int = 512,
    opset_version: int = 14,
) -> None:
    """Export PyTorch model to ONNX format.

    Args:
        model: Trained BiomedBERT model
        output_path: Path for output ONNX file
        max_length: Maximum sequence length
        opset_version: ONNX opset version (14 for good RoBERTa/BERT compatibility)
    """
    model.eval()

    # Create dummy inputs
    batch_size = 1
    dummy_input_ids = torch.randint(0, 30522, (batch_size, max_length))
    dummy_attention_mask = torch.ones(batch_size, max_length, dtype=torch.long)

    # Export
    print(f"Exporting model to ONNX: {output_path}")

    torch.onnx.export(
        model,
        (dummy_input_ids, dummy_attention_mask),
        str(output_path),
        input_names=["input_ids", "attention_mask"],
        output_names=["logits"],
        dynamic_axes={
            "input_ids": {0: "batch_size", 1: "sequence_length"},
            "attention_mask": {0: "batch_size", 1: "sequence_length"},
            "logits": {0: "batch_size"},
        },
        opset_version=opset_version,
        do_constant_folding=True,
        export_params=True,
    )

    # Verify export
    import onnx
    onnx_model = onnx.load(str(output_path))
    onnx.checker.check_model(onnx_model)
    print(f"  ONNX model verified successfully")

    # Print model size
    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"  Model size: {size_mb:.1f} MB")


# ============================================================================
# INT8 Quantization
# ============================================================================

def quantize_model(
    onnx_path: Path,
    output_path: Path,
) -> None:
    """Apply dynamic INT8 quantization to ONNX model.

    Uses dynamic quantization which quantizes weights to INT8 but keeps
    activations in FP32. This provides good speedup with minimal accuracy loss.

    Args:
        onnx_path: Path to unquantized ONNX model
        output_path: Path for quantized output
    """
    from onnxruntime.quantization import quantize_dynamic, QuantType

    print(f"Quantizing model: {onnx_path} -> {output_path}")

    quantize_dynamic(
        model_input=str(onnx_path),
        model_output=str(output_path),
        weight_type=QuantType.QUInt8,
        optimize_model=True,
    )

    # Print size comparison
    original_size = onnx_path.stat().st_size / (1024 * 1024)
    quantized_size = output_path.stat().st_size / (1024 * 1024)
    reduction = (1 - quantized_size / original_size) * 100

    print(f"  Original size: {original_size:.1f} MB")
    print(f"  Quantized size: {quantized_size:.1f} MB")
    print(f"  Size reduction: {reduction:.1f}%")


# ============================================================================
# Validation
# ============================================================================

def validate_quantized_model(
    original_model: BiomedBERTMultiLabel,
    quantized_onnx_path: Path,
    tokenizer_path: Path,
    test_texts: list[str],
    test_labels: np.ndarray,
    label_names: list[str],
    thresholds: dict[str, float],
    max_length: int = 512,
) -> dict:
    """Compare quantized ONNX model against original PyTorch model.

    Args:
        original_model: Original PyTorch model
        quantized_onnx_path: Path to quantized ONNX model
        tokenizer_path: Path to tokenizer
        test_texts: List of test note texts
        test_labels: Test labels array
        label_names: List of label names
        thresholds: Per-label thresholds
        max_length: Maximum sequence length

    Returns:
        Dict with accuracy comparison metrics
    """
    import onnxruntime as ort
    from sklearn.metrics import f1_score

    print("\nValidating quantized model against original...")

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(str(tokenizer_path))

    # Load ONNX model
    sess_options = ort.SessionOptions()
    sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    onnx_session = ort.InferenceSession(
        str(quantized_onnx_path),
        sess_options=sess_options,
        providers=["CPUExecutionProvider"],
    )

    original_model.eval()

    # Run predictions
    pytorch_probs = []
    onnx_probs = []

    for text in test_texts[:100]:  # Sample for speed
        # Tokenize
        encoding = tokenizer(
            text,
            max_length=max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )

        # PyTorch prediction
        with torch.no_grad():
            logits = original_model(
                encoding["input_ids"],
                encoding["attention_mask"],
            )
            probs = torch.sigmoid(logits).numpy()[0]
            pytorch_probs.append(probs)

        # ONNX prediction
        onnx_inputs = {
            "input_ids": encoding["input_ids"].numpy().astype(np.int64),
            "attention_mask": encoding["attention_mask"].numpy().astype(np.int64),
        }
        onnx_logits = onnx_session.run(None, onnx_inputs)[0]
        onnx_prob = 1 / (1 + np.exp(-onnx_logits[0]))  # Sigmoid
        onnx_probs.append(onnx_prob)

    pytorch_probs = np.array(pytorch_probs)
    onnx_probs = np.array(onnx_probs)

    # Compare predictions
    diff = np.abs(pytorch_probs - onnx_probs)
    max_diff = diff.max()
    mean_diff = diff.mean()

    print(f"  Max probability difference: {max_diff:.6f}")
    print(f"  Mean probability difference: {mean_diff:.6f}")

    # Apply thresholds and compare F1
    pytorch_preds = np.zeros_like(pytorch_probs)
    onnx_preds = np.zeros_like(onnx_probs)

    for i, label in enumerate(label_names):
        thresh = thresholds.get(label, 0.5)
        pytorch_preds[:, i] = (pytorch_probs[:, i] >= thresh).astype(int)
        onnx_preds[:, i] = (onnx_probs[:, i] >= thresh).astype(int)

    # Calculate F1 for both
    test_labels_subset = test_labels[:100]

    pytorch_f1 = f1_score(test_labels_subset.ravel(), pytorch_preds.ravel(), zero_division=0)
    onnx_f1 = f1_score(test_labels_subset.ravel(), onnx_preds.ravel(), zero_division=0)

    print(f"  PyTorch F1: {pytorch_f1:.4f}")
    print(f"  ONNX F1: {onnx_f1:.4f}")
    print(f"  F1 difference: {abs(pytorch_f1 - onnx_f1):.4f}")

    # Check if predictions match
    pred_match = (pytorch_preds == onnx_preds).all(axis=1).mean()
    print(f"  Prediction match rate: {pred_match * 100:.1f}%")

    return {
        "max_prob_diff": float(max_diff),
        "mean_prob_diff": float(mean_diff),
        "pytorch_f1": float(pytorch_f1),
        "onnx_f1": float(onnx_f1),
        "f1_diff": float(abs(pytorch_f1 - onnx_f1)),
        "prediction_match_rate": float(pred_match),
    }


# ============================================================================
# Main
# ============================================================================

def main():
    """Parse arguments and run export/quantization."""
    parser = argparse.ArgumentParser(
        description="Export and quantize BiomedBERT model to ONNX INT8"
    )

    parser.add_argument(
        "--model-dir",
        type=Path,
        required=True,
        help="Path to trained model directory",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("models"),
        help="Output directory for ONNX files (default: models/)",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate quantized model against original",
    )
    parser.add_argument(
        "--test-csv",
        type=Path,
        default=Path("data/ml_training/registry_test.csv"),
        help="Test CSV for validation",
    )
    parser.add_argument(
        "--skip-full-export",
        action="store_true",
        help="Skip full ONNX export, only do quantization",
    )

    args = parser.parse_args()

    # Paths
    model_dir = args.model_dir
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    onnx_path = output_dir / "registry_model.onnx"
    quantized_path = output_dir / "registry_model_int8.onnx"
    tokenizer_path = model_dir / "tokenizer"

    # Load label fields
    label_fields_path = Path("data/ml_training/registry_label_fields.json")
    with open(label_fields_path) as f:
        label_names = json.load(f)
    num_labels = len(label_names)

    print(f"\n{'=' * 60}")
    print("ONNX Export and Quantization")
    print(f"{'=' * 60}")
    print(f"Model directory: {model_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Number of labels: {num_labels}")

    # Load model
    print("\nLoading PyTorch model...")
    model = BiomedBERTMultiLabel.from_pretrained(model_dir, num_labels)
    model.eval()

    # Export to ONNX
    if not args.skip_full_export:
        print("\n" + "=" * 40)
        print("Step 1: Export to ONNX")
        print("=" * 40)
        export_to_onnx(model, onnx_path)

    # Quantize
    print("\n" + "=" * 40)
    print("Step 2: INT8 Quantization")
    print("=" * 40)

    if onnx_path.exists():
        quantize_model(onnx_path, quantized_path)
    else:
        print(f"ERROR: ONNX model not found at {onnx_path}")
        return

    # Validate
    if args.validate:
        print("\n" + "=" * 40)
        print("Step 3: Validation")
        print("=" * 40)

        # Load test data
        import pandas as pd
        test_df = pd.read_csv(args.test_csv)
        test_texts = test_df["note_text"].fillna("").tolist()

        exclude_cols = {"note_text", "verified_cpt_codes"}
        label_cols = [c for c in test_df.columns if c not in exclude_cols]
        test_labels = test_df[label_cols].fillna(0).astype(int).to_numpy()

        # Load thresholds
        thresholds_path = model_dir.parent / "roberta_registry_thresholds.json"
        if thresholds_path.exists():
            with open(thresholds_path) as f:
                thresholds = json.load(f)
        else:
            thresholds = {name: 0.5 for name in label_names}

        validation_results = validate_quantized_model(
            original_model=model,
            quantized_onnx_path=quantized_path,
            tokenizer_path=tokenizer_path,
            test_texts=test_texts,
            test_labels=test_labels,
            label_names=label_names,
            thresholds=thresholds,
        )

        # Save validation results
        results_path = output_dir / "quantization_validation.json"
        with open(results_path, "w") as f:
            json.dump(validation_results, f, indent=2)
        print(f"\nValidation results saved to: {results_path}")

    # Copy tokenizer to output dir
    print("\n" + "=" * 40)
    print("Step 4: Copy Tokenizer")
    print("=" * 40)

    tokenizer_out = output_dir / "roberta_registry_tokenizer"
    if tokenizer_path.exists():
        import shutil
        if tokenizer_out.exists():
            shutil.rmtree(tokenizer_out)
        shutil.copytree(tokenizer_path, tokenizer_out)
        print(f"Tokenizer copied to: {tokenizer_out}")
    else:
        print(f"WARNING: Tokenizer not found at {tokenizer_path}")

    # Summary
    print(f"\n{'=' * 60}")
    print("Export Complete!")
    print(f"{'=' * 60}")
    print(f"ONNX model: {onnx_path}")
    print(f"Quantized model: {quantized_path}")
    print(f"Tokenizer: {tokenizer_out}")

    if quantized_path.exists():
        size_mb = quantized_path.stat().st_size / (1024 * 1024)
        print(f"\nFinal model size: {size_mb:.1f} MB")
        print("Ready for Railway deployment!")


if __name__ == "__main__":
    main()

```

---
### `scripts/unified_pipeline_batch.py`
- Size: `14760` bytes
```
#!/usr/bin/env python3
"""Batch unified pipeline test on random notes.

This script randomly selects N notes from data/granular annotations/notes_text,
runs the full unified pipeline (same as UI at /ui/), and saves results to a text file.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _truthy_env(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in ("1", "true", "yes")


if not _truthy_env("PROCSUITE_SKIP_DOTENV"):
    load_dotenv(override=False)

# Import after environment setup
from modules.api.adapters.response_adapter import build_v3_evidence_payload  # noqa: E402
from modules.api.dependencies import get_coding_service, get_registry_service  # noqa: E402
from modules.api.phi_dependencies import get_phi_scrubber  # noqa: E402
from modules.api.phi_redaction import apply_phi_redaction  # noqa: E402
from modules.api.schemas import (  # noqa: E402
    CodeSuggestionSummary,
    UnifiedProcessRequest,
    UnifiedProcessResponse,
)
from modules.coder.application.coding_service import CodingService  # noqa: E402
from modules.coder.domain_rules.registry_to_cpt.coding_rules import derive_all_codes_with_meta  # noqa: E402
from modules.coder.phi_gating import is_phi_review_required  # noqa: E402
from modules.common.exceptions import LLMError  # noqa: E402
from modules.registry.application.registry_service import (  # noqa: E402
    RegistryExtractionResult,
    RegistryService,
)
from config.settings import CoderSettings  # noqa: E402


def _load_notes_from_directory(notes_dir: Path) -> dict[str, str]:
    """Load all notes from .txt files in the directory.
    
    Returns a dict mapping note_id (filename without .txt) to note_text.
    """
    notes = {}
    
    for txt_file in sorted(notes_dir.glob("*.txt")):
        try:
            note_text = txt_file.read_text(encoding="utf-8")
            note_id = txt_file.stem  # filename without .txt extension
            notes[note_id] = note_text
        except Exception as exc:
            print(f"Warning: Failed to load {txt_file}: {exc}", file=sys.stderr)
    
    return notes


def _run_unified_pipeline(
    note_text: str,
    registry_service: RegistryService,
    coding_service: CodingService,
    phi_scrubber,
    *,
    include_financials: bool = True,
    explain: bool = True,
) -> UnifiedProcessResponse:
    """Run the unified pipeline (same as /api/v1/process endpoint).
    
    This replicates the exact logic from modules/api/routes/unified_process.py
    """
    import time
    
    start_time = time.time()
    
    # PHI redaction (if not already scrubbed)
    # For batch testing, we'll treat notes as already scrubbed to match UI behavior
    # when user submits via PHI redactor
    redaction = apply_phi_redaction(note_text, phi_scrubber)
    scrubbed_text = redaction.text
    
    # Step 1: Registry extraction (synchronous call)
    try:
        extraction_result = registry_service.extract_fields(scrubbed_text)
    except Exception as exc:
        if isinstance(exc, LLMError) and "429" in str(exc):
            raise Exception("Upstream LLM rate limited") from exc
        raise
    
    # Step 2: Derive CPT codes from registry
    record = extraction_result.record
    if record is None:
        from modules.registry.schema import RegistryRecord
        record = RegistryRecord.model_validate(extraction_result.mapped_fields)
    
    codes, rationales, derivation_warnings = derive_all_codes_with_meta(record)
    
    # Build suggestions with confidence and rationale
    suggestions = []
    base_confidence = 0.95 if extraction_result.coder_difficulty == "HIGH_CONF" else 0.80
    
    for code in codes:
        proc_info = coding_service.kb_repo.get_procedure_info(code)
        description = proc_info.description if proc_info else ""
        rationale = rationales.get(code, "")
        
        # Determine review flag
        if extraction_result.needs_manual_review:
            review_flag = "required"
        elif extraction_result.audit_warnings:
            review_flag = "recommended"
        else:
            review_flag = "optional"
        
        suggestions.append(
            CodeSuggestionSummary(
                code=code,
                description=description,
                confidence=base_confidence,
                rationale=rationale,
                review_flag=review_flag,
            )
        )
    
    # Step 3: Calculate financials if requested
    total_work_rvu = None
    estimated_payment = None
    per_code_billing = []
    
    if include_financials and codes:
        settings = CoderSettings()
        conversion_factor = settings.cms_conversion_factor
        total_work = 0.0
        total_payment = 0.0
        
        for code in codes:
            proc_info = coding_service.kb_repo.get_procedure_info(code)
            if proc_info:
                work_rvu = proc_info.work_rvu
                total_rvu = proc_info.total_facility_rvu
                payment = total_rvu * conversion_factor
                
                total_work += work_rvu
                total_payment += payment
                
                per_code_billing.append({
                    "cpt_code": code,
                    "description": proc_info.description,
                    "work_rvu": work_rvu,
                    "total_facility_rvu": total_rvu,
                    "facility_payment": round(payment, 2),
                })
        
        total_work_rvu = round(total_work, 2)
        estimated_payment = round(total_payment, 2)
    
    # Combine audit warnings
    all_warnings: list[str] = []
    all_warnings.extend(extraction_result.warnings or [])
    all_warnings.extend(extraction_result.audit_warnings or [])
    all_warnings.extend(derivation_warnings)
    
    # Deduplicate warnings
    deduped_warnings: list[str] = []
    seen_warnings: set[str] = set()
    for warning in all_warnings:
        if warning in seen_warnings:
            continue
        seen_warnings.add(warning)
        deduped_warnings.append(warning)
    all_warnings = deduped_warnings
    
    # Build evidence payload
    evidence_payload = build_v3_evidence_payload(record=record, codes=codes)
    if not explain and not evidence_payload:
        evidence_payload = {}
    
    # Determine review status
    needs_manual_review = extraction_result.needs_manual_review
    if is_phi_review_required():
        review_status = "pending_phi_review"
        needs_manual_review = True
    elif needs_manual_review:
        review_status = "unverified"
    else:
        review_status = "finalized"
    
    processing_time_ms = (time.time() - start_time) * 1000
    
    # Build response
    registry_payload = record.model_dump(exclude_none=True)
    
    return UnifiedProcessResponse(
        registry=registry_payload,
        evidence=evidence_payload,
        cpt_codes=codes,
        suggestions=suggestions,
        total_work_rvu=total_work_rvu,
        estimated_payment=estimated_payment,
        per_code_billing=per_code_billing,
        pipeline_mode="extraction_first",
        coder_difficulty=extraction_result.coder_difficulty or "",
        needs_manual_review=needs_manual_review,
        audit_warnings=all_warnings,
        validation_errors=extraction_result.validation_errors or [],
        kb_version=coding_service.kb_repo.version,
        policy_version="extraction_first_v1",
        processing_time_ms=round(processing_time_ms, 2),
        review_status=review_status,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Batch unified pipeline test on random notes from notes_text directory."
    )
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of random notes to test (default: 10)",
    )
    parser.add_argument(
        "--notes-dir",
        type=Path,
        default=ROOT / "data" / "granular annotations" / "notes_text",
        help="Directory containing note .txt files (default: data/granular annotations/notes_text)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output file path (default: unified_pipeline_batch_<timestamp>.txt)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility",
    )
    parser.add_argument(
        "--include-financials",
        action="store_true",
        default=True,
        help="Include RVU and payment information (default: True)",
    )
    parser.add_argument(
        "--no-financials",
        dest="include_financials",
        action="store_false",
        help="Exclude RVU and payment information",
    )
    parser.add_argument(
        "--explain",
        action="store_true",
        default=True,
        help="Include evidence/explanation data (default: True)",
    )
    parser.add_argument(
        "--no-explain",
        dest="explain",
        action="store_false",
        help="Exclude evidence/explanation data",
    )
    parser.add_argument(
        "--real-llm",
        action="store_true",
        help="Allow real LLM calls (disables stub/offline defaults).",
    )
    args = parser.parse_args()
    
    # Set up environment
    if args.real_llm:
        os.environ.setdefault("REGISTRY_USE_STUB_LLM", "0")
        os.environ.setdefault("GEMINI_OFFLINE", "0")
    else:
        # Use stub LLM for offline testing
        if os.getenv("REGISTRY_USE_STUB_LLM") is None:
            os.environ["REGISTRY_USE_STUB_LLM"] = "1"
        if os.getenv("GEMINI_OFFLINE") is None:
            os.environ["GEMINI_OFFLINE"] = "1"
    
    # Load notes
    if not args.notes_dir.exists():
        print(f"ERROR: Notes directory not found: {args.notes_dir}", file=sys.stderr)
        return 1
    
    print(f"Loading notes from {args.notes_dir}...", file=sys.stderr)
    all_notes = _load_notes_from_directory(args.notes_dir)
    
    if not all_notes:
        print(f"ERROR: No notes found in {args.notes_dir}", file=sys.stderr)
        return 1
    
    print(f"Loaded {len(all_notes)} notes", file=sys.stderr)
    
    # Select random notes
    if args.seed is not None:
        random.seed(args.seed)
        print(f"Using random seed: {args.seed}", file=sys.stderr)
    
    count = min(args.count, len(all_notes))
    selected_notes = random.sample(list(all_notes.items()), count)
    
    print(f"Selected {count} random notes for testing", file=sys.stderr)
    
    # Determine output file
    if args.output:
        output_path = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = ROOT / f"unified_pipeline_batch_{timestamp}.txt"
    
    # Initialize services
    print("Initializing services...", file=sys.stderr)
    registry_service = get_registry_service()
    coding_service = get_coding_service()
    phi_scrubber = get_phi_scrubber()
    
    # Run unified pipeline on each note
    print(f"Running unified pipeline on {count} notes...", file=sys.stderr)
    print(f"Output will be saved to: {output_path}", file=sys.stderr)
    
    all_results = []
    for i, (note_id, note_text) in enumerate(selected_notes, 1):
        print(f"[{i}/{count}] Processing {note_id}...", file=sys.stderr)
        try:
            result = _run_unified_pipeline(
                note_text,
                registry_service,
                coding_service,
                phi_scrubber,
                include_financials=args.include_financials,
                explain=args.explain,
            )
            all_results.append((note_id, note_text, result, None))
        except Exception as exc:
            print(f"  ERROR: {exc}", file=sys.stderr)
            all_results.append((note_id, note_text, None, str(exc)))
    
    # Write output file
    with open(output_path, "w", encoding="utf-8") as f:
        # Write header
        f.write("=" * 80 + "\n")
        f.write("UNIFIED PIPELINE BATCH TEST RESULTS\n")
        f.write("=" * 80 + "\n")
        f.write(f"Date: {datetime.now().isoformat()}\n")
        f.write(f"Notes tested: {count}\n")
        f.write(f"Notes directory: {args.notes_dir}\n")
        if args.seed is not None:
            f.write(f"Random seed: {args.seed}\n")
        f.write(f"Include financials: {args.include_financials}\n")
        f.write(f"Include explain: {args.explain}\n")
        f.write(f"Real LLM enabled: {args.real_llm}\n")
        f.write("=" * 80 + "\n")
        f.write("\n")
        
        # Write results for each note
        success_count = 0
        failed_count = 0
        
        for note_id, note_text, result, error in all_results:
            f.write("=" * 80 + "\n")
            f.write(f"NOTE: {note_id}\n")
            f.write("=" * 80 + "\n")
            f.write("\n")
            
            # Write note text
            f.write("NOTE TEXT:\n")
            f.write("-" * 80 + "\n")
            f.write(note_text)
            f.write("\n")
            f.write("-" * 80 + "\n")
            f.write("\n")
            
            # Write results
            if error:
                f.write("ERROR:\n")
                f.write(f"{error}\n")
                f.write("\n")
                f.write("STATUS: FAILED\n")
                failed_count += 1
            else:
                f.write("RESULTS (JSON):\n")
                f.write("-" * 80 + "\n")
                # Convert Pydantic model to dict and serialize
                result_dict = result.model_dump(exclude_none=True)
                f.write(json.dumps(result_dict, indent=2, ensure_ascii=False))
                f.write("\n")
                f.write("-" * 80 + "\n")
                f.write("\n")
                f.write("STATUS: SUCCESS\n")
                success_count += 1
            
            f.write("\n")
        
        # Write summary
        f.write("=" * 80 + "\n")
        f.write("SUMMARY\n")
        f.write("=" * 80 + "\n")
        f.write(f"Total notes tested: {count}\n")
        f.write(f"Successful: {success_count}\n")
        f.write(f"Failed: {failed_count}\n")
        if count > 0:
            f.write(f"Success rate: {success_count/count*100:.1f}%\n")
        f.write("=" * 80 + "\n")
    
    print(f"\nCompleted! Results saved to: {output_path}", file=sys.stderr)
    print(f"Summary: {success_count} successful, {failed_count} failed", file=sys.stderr)
    
    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

```

---
### `scripts/verify_registry_human_data.py`
- Size: `15511` bytes
```
#!/usr/bin/env python3
"""Verify and cleanup registry human training data files.

This script:
1. Confirms all records from subset files exist in registry_human.csv (master)
2. Checks for label conflicts (same encounter_id with different procedure labels)
3. Reports schema differences (column mismatches)
4. Identifies any records missing from master
5. Optionally archives subset files to _archive/registry_human/

Usage:
    python scripts/verify_registry_human_data.py           # Dry-run (report only)
    python scripts/verify_registry_human_data.py --execute # Add missing + archive
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from modules.ml_coder.registry_label_schema import REGISTRY_LABELS, compute_encounter_id

# File configuration
DATA_DIR = ROOT / "data" / "ml_training"
MASTER_FILE = "registry_human.csv"
SUBSET_FILES = [
    "registry_human_updates.csv",
    "registry_human_v2.csv",
    "registry_human_rigid_review.csv",
    "registry_human_v1_backup.csv",
]
ARCHIVE_DIR = DATA_DIR / "_archive" / "registry_human"


@dataclass
class VerificationResult:
    """Results from verifying a subset file against master."""

    subset_name: str
    total_records: int
    unique_encounter_ids: int
    columns: int
    column_list: list[str] = field(default_factory=list)
    contained_in_master: int = 0
    missing_from_master: list[str] = field(default_factory=list)
    label_conflicts: list[dict[str, Any]] = field(default_factory=list)
    schema_warnings: list[str] = field(default_factory=list)
    load_error: str | None = None


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names (strip whitespace, BOM)."""
    df.columns = [str(c).strip().lstrip("\ufeff") for c in df.columns]
    return df


def _ensure_encounter_id(df: pd.DataFrame, name: str) -> pd.DataFrame:
    """Ensure encounter_id column exists and is populated."""
    if "encounter_id" not in df.columns:
        if "note_text" not in df.columns:
            raise ValueError(f"{name} missing both encounter_id and note_text columns")
        df["encounter_id"] = df["note_text"].fillna("").astype(str).map(
            lambda t: compute_encounter_id(t.strip())
        )
        return df

    df["encounter_id"] = df["encounter_id"].fillna("").astype(str).str.strip()

    if "note_text" in df.columns:
        mask = df["encounter_id"] == ""
        if mask.any():
            df.loc[mask, "encounter_id"] = df.loc[mask, "note_text"].fillna("").astype(str).map(
                lambda t: compute_encounter_id(t.strip())
            )
    return df


def load_csv_safe(path: Path) -> pd.DataFrame | None:
    """Load CSV with error handling for malformed files."""
    try:
        df = pd.read_csv(path)
        df = _normalize_columns(df)
        df = _ensure_encounter_id(df, path.name)
        return df
    except Exception as e:
        return None


def verify_subset(
    master_df: pd.DataFrame, subset_path: Path, labels: list[str]
) -> VerificationResult:
    """Verify a subset file against the master."""
    result = VerificationResult(
        subset_name=subset_path.name,
        total_records=0,
        unique_encounter_ids=0,
        columns=0,
    )

    if not subset_path.exists():
        result.load_error = "File not found"
        return result

    subset_df = load_csv_safe(subset_path)
    if subset_df is None:
        result.load_error = "Failed to load (malformed CSV)"
        return result

    result.total_records = len(subset_df)
    result.unique_encounter_ids = subset_df["encounter_id"].nunique()
    result.columns = len(subset_df.columns)
    result.column_list = list(subset_df.columns)

    # Check schema differences
    master_label_cols = set(labels) & set(master_df.columns)
    subset_label_cols = set(labels) & set(subset_df.columns)

    missing_in_subset = master_label_cols - subset_label_cols
    extra_in_subset = subset_label_cols - master_label_cols

    if missing_in_subset:
        result.schema_warnings.append(f"Missing columns vs master: {sorted(missing_in_subset)}")
    if extra_in_subset:
        result.schema_warnings.append(f"Extra columns vs master: {sorted(extra_in_subset)}")

    # Check containment
    master_ids = set(master_df["encounter_id"].unique())
    subset_ids = set(subset_df["encounter_id"].unique())

    contained = subset_ids & master_ids
    missing = subset_ids - master_ids

    result.contained_in_master = len(contained)
    result.missing_from_master = sorted(missing)

    # Check label conflicts for contained records
    common_labels = list(master_label_cols & subset_label_cols)
    if common_labels and contained:
        master_idx = master_df.set_index("encounter_id")
        subset_idx = subset_df.drop_duplicates("encounter_id").set_index("encounter_id")

        for eid in contained:
            if eid not in master_idx.index or eid not in subset_idx.index:
                continue

            master_row = master_idx.loc[eid]
            subset_row = subset_idx.loc[eid]

            conflicts = []
            for label in common_labels:
                if label in master_row and label in subset_row:
                    m_val = int(master_row[label]) if pd.notna(master_row[label]) else 0
                    s_val = int(subset_row[label]) if pd.notna(subset_row[label]) else 0
                    if m_val != s_val:
                        conflicts.append({"label": label, "master": m_val, "subset": s_val})

            if conflicts:
                result.label_conflicts.append({"encounter_id": eid, "conflicts": conflicts})

    return result


def generate_report(
    results: list[VerificationResult], master_stats: dict[str, Any]
) -> str:
    """Generate human-readable verification report."""
    lines = []
    ts = datetime.now().isoformat(timespec="seconds")

    lines.append("=" * 80)
    lines.append("              REGISTRY HUMAN DATA VERIFICATION REPORT")
    lines.append(f"              Generated: {ts}")
    lines.append("=" * 80)
    lines.append("")
    lines.append(f"MASTER FILE: {MASTER_FILE}")
    lines.append(f"  - Total records: {master_stats['total_records']}")
    lines.append(f"  - Unique encounter_ids: {master_stats['unique_ids']}")
    lines.append(f"  - Columns: {master_stats['columns']}")
    lines.append("")

    total_missing = []
    total_conflicts = 0

    for r in results:
        lines.append("-" * 80)
        lines.append(f"SUBSET FILE: {r.subset_name}")
        lines.append("-" * 80)

        if r.load_error:
            lines.append(f"  ERROR: {r.load_error}")
            lines.append("")
            continue

        lines.append(f"  Records: {r.total_records} ({r.unique_encounter_ids} unique encounter_ids)")
        lines.append(f"  Columns: {r.columns}")
        lines.append("")

        pct = (r.contained_in_master / r.unique_encounter_ids * 100) if r.unique_encounter_ids > 0 else 0
        status = "[OK]" if r.contained_in_master == r.unique_encounter_ids else "[MISSING]"
        lines.append(f"  Containment: {r.contained_in_master}/{r.unique_encounter_ids} ({pct:.1f}%) in master {status}")

        if r.missing_from_master:
            lines.append(f"  Missing from master: {len(r.missing_from_master)}")
            for eid in r.missing_from_master[:5]:
                lines.append(f"    - {eid}")
            if len(r.missing_from_master) > 5:
                lines.append(f"    ... and {len(r.missing_from_master) - 5} more")
            total_missing.extend(r.missing_from_master)
        lines.append("")

        conflict_status = "[OK]" if not r.label_conflicts else "[CONFLICTS]"
        lines.append(f"  Label Conflicts: {len(r.label_conflicts)} {conflict_status}")
        if r.label_conflicts:
            # Summarize by label
            label_counts: dict[str, int] = {}
            for c in r.label_conflicts:
                for conflict in c["conflicts"]:
                    label_counts[conflict["label"]] = label_counts.get(conflict["label"], 0) + 1
            lines.append("    Affected labels:")
            for label, count in sorted(label_counts.items(), key=lambda x: -x[1]):
                lines.append(f"      - {label}: {count} conflicts")
            total_conflicts += len(r.label_conflicts)
        lines.append("")

        if r.schema_warnings:
            lines.append("  Schema Warnings:")
            for w in r.schema_warnings:
                lines.append(f"    - {w}")
            lines.append("")

    # Summary
    lines.append("=" * 80)
    lines.append("                              SUMMARY")
    lines.append("=" * 80)
    lines.append("")
    lines.append(f"Files verified: {len(results)}")
    lines.append(f"Total unique missing records: {len(set(total_missing))}")
    if total_missing:
        lines.append(f"  Missing encounter_ids: {sorted(set(total_missing))}")
    lines.append(f"Total records with label conflicts: {total_conflicts}")
    lines.append("")

    if total_missing:
        lines.append("RECOMMENDATIONS:")
        lines.append("1. Add missing records to registry_human.csv")
        lines.append("2. Then run with --execute to archive subset files")
    else:
        lines.append("RECOMMENDATIONS:")
        lines.append("1. All records accounted for - safe to archive")
        lines.append("2. Run with --execute to archive subset files")

    lines.append("")
    lines.append("=" * 80)

    return "\n".join(lines)


def add_missing_records(
    master_df: pd.DataFrame,
    subset_files: list[Path],
    missing_ids: set[str],
    labels: list[str],
) -> pd.DataFrame:
    """Add missing records from subset files to master."""
    if not missing_ids:
        return master_df

    records_to_add = []

    for subset_path in subset_files:
        subset_df = load_csv_safe(subset_path)
        if subset_df is None:
            continue

        for eid in missing_ids:
            matches = subset_df[subset_df["encounter_id"] == eid]
            if not matches.empty:
                records_to_add.append(matches.iloc[0].to_dict())

    if not records_to_add:
        return master_df

    # Ensure all label columns exist
    new_rows = pd.DataFrame(records_to_add)
    for col in labels:
        if col not in new_rows.columns:
            new_rows[col] = 0

    # Align columns with master
    for col in master_df.columns:
        if col not in new_rows.columns:
            new_rows[col] = "" if master_df[col].dtype == object else 0

    # Append and deduplicate
    result = pd.concat([master_df, new_rows], ignore_index=True)
    result = result.drop_duplicates(subset=["encounter_id"], keep="last")

    return result


def archive_files(files: list[Path], dry_run: bool = True) -> list[dict[str, str]]:
    """Archive files to _archive/registry_human/ folder."""
    archived = []
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    if not dry_run:
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    for f in files:
        if not f.exists():
            continue

        archive_name = f"{f.name}.{ts}"
        archive_path = ARCHIVE_DIR / archive_name

        if dry_run:
            print(f"  [DRY-RUN] Would archive: {f.name} -> {archive_path}")
        else:
            shutil.move(str(f), str(archive_path))
            print(f"  Archived: {f.name} -> {archive_path}")

        archived.append({"original": f.name, "archived_as": archive_name})

    return archived


def create_manifest(
    archived: list[dict[str, str]],
    master_records: int,
    missing_added: int,
) -> None:
    """Create archive manifest JSON."""
    manifest = {
        "archived_at": datetime.now().isoformat(timespec="seconds"),
        "reason": "Consolidated into registry_human.csv (single source of truth)",
        "master_file": MASTER_FILE,
        "master_records_after": master_records,
        "missing_records_added": missing_added,
        "archived_files": archived,
    }

    manifest_path = ARCHIVE_DIR / "ARCHIVE_MANIFEST.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"  Created manifest: {manifest_path}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument(
        "--execute",
        action="store_true",
        help="Execute cleanup (add missing records and archive files). Default is dry-run.",
    )
    p.add_argument(
        "--data-dir",
        type=Path,
        default=DATA_DIR,
        help=f"Data directory (default: {DATA_DIR})",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    data_dir = args.data_dir

    master_path = data_dir / MASTER_FILE
    if not master_path.exists():
        print(f"ERROR: Master file not found: {master_path}")
        return 1

    # Load master
    master_df = load_csv_safe(master_path)
    if master_df is None:
        print(f"ERROR: Failed to load master file: {master_path}")
        return 1

    master_stats = {
        "total_records": len(master_df),
        "unique_ids": master_df["encounter_id"].nunique(),
        "columns": len(master_df.columns),
    }

    # Verify each subset
    results = []
    labels = list(REGISTRY_LABELS)

    for subset_name in SUBSET_FILES:
        subset_path = data_dir / subset_name
        result = verify_subset(master_df, subset_path, labels)
        results.append(result)

    # Generate and print report
    report = generate_report(results, master_stats)
    print(report)

    # Collect all missing IDs
    all_missing = set()
    for r in results:
        all_missing.update(r.missing_from_master)

    if args.execute:
        print("\n" + "=" * 80)
        print("                         EXECUTING CLEANUP")
        print("=" * 80 + "\n")

        # Step 1: Add missing records
        if all_missing:
            print(f"Adding {len(all_missing)} missing records to master...")
            subset_paths = [data_dir / name for name in SUBSET_FILES]
            master_df = add_missing_records(master_df, subset_paths, all_missing, labels)
            master_df.to_csv(master_path, index=False)
            print(f"  Updated: {master_path} (now {len(master_df)} records)")
        else:
            print("No missing records to add.")

        # Step 2: Archive subset files
        print("\nArchiving subset files...")
        subset_paths = [data_dir / name for name in SUBSET_FILES]
        archived = archive_files(subset_paths, dry_run=False)

        # Step 3: Create manifest
        if archived:
            create_manifest(archived, len(master_df), len(all_missing))

        print("\nCleanup complete!")
        print(f"  Master file: {master_path} ({len(master_df)} records)")
        print(f"  Archived files: {len(archived)}")

    else:
        print("\n[DRY-RUN MODE] No changes made. Use --execute to apply changes.")
        if all_missing:
            print(f"  Would add {len(all_missing)} missing records to master")
        print(f"  Would archive {len([f for f in SUBSET_FILES if (data_dir / f).exists()])} files")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```
