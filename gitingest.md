# Procedure Suite — gitingest (curated)

Generated: `2025-12-12T10:05:11-08:00`
Git: `main` @ `9eddcc8`

## What this file is
- A **token-budget friendly** snapshot of the repo **structure** + a curated set of **important files**.
- Intended for LLM/context ingestion; excludes large artifacts (models, datasets, caches).

## Exclusions (high level)
- Directories: `.git/`, `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`, `data/`, `dist/`, `distilled/`, `proc_suite.egg-info/`, `reports/`, `validation_results/`
- File types: `*.bin`, `*.db`, `*.onnx`, `*.pt`, `*.pth`, `*.tar.gz`, `*.zip`

## Repo tree (pruned)
```
- proc_suite/
  - .claude/
    - .claude/settings.local.json
  - .github/
    - .github/workflows/
      - .github/workflows/ci.yml
  - .vscode/
    - .vscode/settings.json
  - alembic/
    - alembic/versions/
      - alembic/versions/a1b2c3d4e5f6_add_phi_vault_tables.py
      - alembic/versions/b4c5d6e7f8a9_add_review_status_and_feedback_fields.py
    - alembic/env.py
  - analysis/
    - analysis/synthetic_notes_eval.txt
    - analysis/synthetic_notes_eval_after_kb_update.txt
    - analysis/synthetic_notes_eval_detailed.txt
  - cms_rvu_tools/
    - cms_rvu_tools/cms_rvus_2025_ip.csv
    - cms_rvu_tools/IP_Registry_Enhanced_v2.json
    - cms_rvu_tools/local_rvu_updater.py
    - cms_rvu_tools/README.md
    - cms_rvu_tools/rvu_fetcher.py
  - config/
    - config/__init__.py
    - config/settings.py
  - configs/
    - configs/coding/
      - configs/coding/__init__.py
      - configs/coding/ip_cpt_map.yaml
      - configs/coding/ncci_edits.yaml
      - configs/coding/payer_overrides.yaml
    - configs/lex/
      - configs/lex/__init__.py
      - configs/lex/airway.topology.yaml
      - configs/lex/devices.lex.yaml
      - configs/lex/procedures.lex.yaml
    - configs/prompts/
      - configs/prompts/phase1_coder_prompt.txt
    - configs/report_templates/
      - configs/report_templates/awake_foi.j2
      - configs/report_templates/awake_foi.yaml
      - configs/report_templates/bal.j2
      - configs/report_templates/bal.json
      - configs/report_templates/bal_variant.j2
      - configs/report_templates/bal_variant.yaml
      - configs/report_templates/blvr_discharge_instructions.j2
      - configs/report_templates/blvr_discharge_instructions.yaml
      - configs/report_templates/blvr_post_procedure_protocol.j2
      - configs/report_templates/blvr_post_procedure_protocol.yaml
      - configs/report_templates/blvr_valve_placement.j2
      - configs/report_templates/blvr_valve_placement.yaml
      - configs/report_templates/blvr_valve_removal_exchange.j2
      - configs/report_templates/blvr_valve_removal_exchange.yaml
      - configs/report_templates/bpf_endobronchial_sealant.j2
      - configs/report_templates/bpf_endobronchial_sealant.yaml
      - configs/report_templates/bpf_localization_occlusion.j2
      - configs/report_templates/bpf_localization_occlusion.yaml
      - configs/report_templates/bpf_valve_air_leak.j2
      - configs/report_templates/bpf_valve_air_leak.yaml
      - configs/report_templates/bronchial_brushings.j2
      - configs/report_templates/bronchial_brushings.yaml
      - configs/report_templates/bronchial_washing.j2
      - configs/report_templates/bronchial_washing.yaml
      - configs/report_templates/cbct_augmented_bronchoscopy.j2
      - configs/report_templates/cbct_augmented_bronchoscopy.yaml
      - configs/report_templates/cbct_cact_fusion.j2
      - configs/report_templates/cbct_cact_fusion.yaml
      - configs/report_templates/chest_tube.j2
      - configs/report_templates/chest_tube.yaml
      - configs/report_templates/chest_tube_discharge.j2
      - configs/report_templates/chest_tube_discharge.yaml
      - configs/report_templates/cryo_extraction_mucus.j2
      - configs/report_templates/cryo_extraction_mucus.yaml
      - configs/report_templates/dlt_placement.j2
      - configs/report_templates/dlt_placement.yaml
      - configs/report_templates/dye_marker_placement.j2
      - configs/report_templates/dye_marker_placement.yaml
      - configs/report_templates/ebus_19g_fnb.j2
      - configs/report_templates/ebus_19g_fnb.yaml
      - configs/report_templates/ebus_ifb.j2
      - configs/report_templates/ebus_ifb.yaml
      - configs/report_templates/ebus_tbna.j2
      - configs/report_templates/ebus_tbna.yaml
      - configs/report_templates/emn_bronchoscopy.j2
      - configs/report_templates/emn_bronchoscopy.yaml
      - configs/report_templates/endobronchial_biopsy.j2
      - configs/report_templates/endobronchial_biopsy.yaml
      - configs/report_templates/endobronchial_blocker.j2
      - configs/report_templates/endobronchial_blocker.yaml
      - configs/report_templates/endobronchial_cryoablation.j2
      - configs/report_templates/endobronchial_cryoablation.yaml
      - configs/report_templates/endobronchial_hemostasis.j2
      - configs/report_templates/endobronchial_hemostasis.yaml
      - configs/report_templates/eusb.j2
      - configs/report_templates/eusb.yaml
      - configs/report_templates/fiducial_marker_placement.j2
      - configs/report_templates/fiducial_marker_placement.yaml
      - configs/report_templates/foreign_body_removal.j2
      - configs/report_templates/foreign_body_removal.yaml
      - configs/report_templates/ion_registration_complete.j2
      - configs/report_templates/ion_registration_complete.yaml
      - configs/report_templates/ion_registration_drift.j2
      - configs/report_templates/ion_registration_drift.yaml
      - configs/report_templates/ion_registration_partial.j2
      - configs/report_templates/ion_registration_partial.yaml
      - configs/report_templates/ip_general_bronchoscopy_shell.j2
      - configs/report_templates/ip_general_bronchoscopy_shell.json
      - configs/report_templates/ip_or_main_oper_report_shell.j2
      - configs/report_templates/ip_or_main_oper_report_shell.json
      - configs/report_templates/ip_pre_anesthesia_assessment.j2
      - configs/report_templates/ip_pre_anesthesia_assessment.json
      - configs/report_templates/paracentesis.j2
      - configs/report_templates/paracentesis.yaml
      - configs/report_templates/pdt_debridement.j2
      - configs/report_templates/pdt_debridement.yaml
      - configs/report_templates/pdt_light.j2
      - configs/report_templates/pdt_light.yaml
      - configs/report_templates/peg_discharge.j2
      - configs/report_templates/peg_discharge.yaml
      - configs/report_templates/peg_exchange.j2
      - configs/report_templates/peg_exchange.yaml
      - configs/report_templates/peg_placement.j2
      - configs/report_templates/peg_placement.yaml
      - configs/report_templates/pigtail_catheter.j2
      - configs/report_templates/pigtail_catheter.yaml
      - configs/report_templates/pleurx_instructions.j2
      - configs/report_templates/pleurx_instructions.yaml
      - configs/report_templates/procedure_order.json
      - configs/report_templates/radial_ebus_sampling.j2
      - configs/report_templates/radial_ebus_sampling.yaml
      - configs/report_templates/radial_ebus_survey.j2
      - configs/report_templates/radial_ebus_survey.yaml
      - configs/report_templates/rigid_bronchoscopy.j2
      - configs/report_templates/rigid_bronchoscopy.yaml
      - configs/report_templates/robotic_ion_bronchoscopy.j2
      - configs/report_templates/robotic_ion_bronchoscopy.yaml
      - configs/report_templates/robotic_monarch_bronchoscopy.j2
      - configs/report_templates/robotic_monarch_bronchoscopy.yaml
      - configs/report_templates/robotic_navigation.j2
      - configs/report_templates/robotic_navigation.yaml
      - configs/report_templates/stent_surveillance.j2
      - configs/report_templates/stent_surveillance.yaml
      - configs/report_templates/therapeutic_aspiration.j2
      - configs/report_templates/therapeutic_aspiration.yaml
      - configs/report_templates/thoracentesis.j2
      - configs/report_templates/thoracentesis.json
      - configs/report_templates/thoracentesis_detailed.j2
      - configs/report_templates/thoracentesis_detailed.yaml
      - configs/report_templates/thoracentesis_manometry.j2
      - configs/report_templates/thoracentesis_manometry.yaml
      - configs/report_templates/tool_in_lesion_confirmation.j2
      - configs/report_templates/tool_in_lesion_confirmation.yaml
      - configs/report_templates/transbronchial_biopsy.j2
      - configs/report_templates/transbronchial_biopsy.yaml
      - configs/report_templates/transbronchial_cryobiopsy.j2
      - configs/report_templates/transbronchial_cryobiopsy.yaml
      - configs/report_templates/transbronchial_lung_biopsy.j2
      - configs/report_templates/transbronchial_lung_biopsy.yaml
      - configs/report_templates/transbronchial_needle_aspiration.j2
      - configs/report_templates/transbronchial_needle_aspiration.yaml
      - configs/report_templates/transthoracic_needle_biopsy.j2
      - configs/report_templates/transthoracic_needle_biopsy.yaml
      - configs/report_templates/tunneled_pleural_catheter_insert.j2
      - configs/report_templates/tunneled_pleural_catheter_insert.yaml
      - configs/report_templates/tunneled_pleural_catheter_remove.j2
      - configs/report_templates/tunneled_pleural_catheter_remove.yaml
      - configs/report_templates/whole_lung_lavage.j2
      - configs/report_templates/whole_lung_lavage.yaml
    - configs/__init__.py
  - docs/
    - docs/Multi_agent_collaboration/
      - docs/Multi_agent_collaboration/Architect Priming Script.md
      - docs/Multi_agent_collaboration/Codex Priming Script.md
      - docs/Multi_agent_collaboration/Codex “Repo Surgeon” Persona.md
      - docs/Multi_agent_collaboration/External_Review_Action_Plan.md
      - docs/Multi_agent_collaboration/Multi‑Agent Architecture.md
      - docs/Multi_agent_collaboration/Session Startup Template.md
      - docs/Multi_agent_collaboration/V8_MIGRATION_PLAN_UPDATED.md
    - docs/phi_review_system/
      - docs/phi_review_system/backend/
      - docs/phi_review_system/frontend/
      - docs/phi_review_system/README.md
    - docs/AGENTS.md
    - docs/ARCHITECTURE.md
    - docs/DEPLOY_ARCH.md
    - docs/DEPLOY_RAILWAY.md
    - docs/DEPLOYMENT.md
    - docs/DEVELOPMENT.md
    - docs/GRAFANA_DASHBOARDS.md
    - docs/INSTALLATION.md
    - docs/ml_first_hybrid_policy.md
    - docs/model_release_runbook.md
    - docs/REFERENCES.md
    - docs/Registry_API.md
    - docs/Registry_ML_summary.md
    - docs/REPORTER_STYLE_GUIDE.md
    - docs/STRUCTURED_REPORTER.md
    - docs/USER_GUIDE.md
    - docs/Validation_fix_plan_12_6_25.md
  - Feedback_csv_files/
    - Feedback_csv_files/qa-sessions-2025-11-30.csv
  - infra/
    - infra/prometheus/
      - infra/prometheus/prometheus.yml
  - modules/
    - modules/agents/
      - modules/agents/parser/
      - modules/agents/structurer/
      - modules/agents/summarizer/
      - modules/agents/__init__.py
      - modules/agents/contracts.py
      - modules/agents/run_pipeline.py
    - modules/api/
      - modules/api/routes/
      - modules/api/schemas/
      - modules/api/services/
      - modules/api/static/
      - modules/api/__init__.py
      - modules/api/coder_adapter.py
      - modules/api/dependencies.py
      - modules/api/fastapi_app.py
      - modules/api/gemini_client.py
      - modules/api/ml_advisor_router.py
      - modules/api/normalization.py
      - modules/api/phi_demo_store.py
      - modules/api/phi_dependencies.py
      - modules/api/routes_registry.py
    - modules/autocode/
      - modules/autocode/ip_kb/
      - modules/autocode/logging/
      - modules/autocode/rvu/
      - modules/autocode/tools/
      - modules/autocode/utils/
      - modules/autocode/__init__.py
      - modules/autocode/coder.py
      - modules/autocode/compat_v2.py
      - modules/autocode/confidence.py
      - modules/autocode/DEPRECATED.md
      - modules/autocode/engine.py
      - modules/autocode/evidence_validator.py
      - modules/autocode/pipeline.py
      - modules/autocode/rules.py
    - modules/coder/
      - modules/coder/adapters/
      - modules/coder/application/
      - modules/coder/reconciliation/
      - modules/coder/__init__.py
      - modules/coder/cli.py
      - modules/coder/code_families.py
      - modules/coder/constants.py
      - modules/coder/dictionary.py
      - modules/coder/domain_rules.py
      - modules/coder/ebus_extractor.py
      - modules/coder/ebus_rules.py
      - modules/coder/engine.py
      - modules/coder/llm_coder.py
      - modules/coder/ncci.py
      - modules/coder/peripheral_extractor.py
      - modules/coder/peripheral_rules.py
      - modules/coder/phi_gating.py
      - modules/coder/posthoc.py
      - modules/coder/rules.py
      - modules/coder/rules_engine.py
      - modules/coder/schema.py
      - modules/coder/sectionizer.py
      - modules/coder/types.py
    - modules/common/
      - modules/common/rules_engine/
      - modules/common/__init__.py
      - modules/common/exceptions.py
      - modules/common/knowledge.py
      - modules/common/knowledge_cli.py
      - modules/common/knowledge_schema.py
      - modules/common/llm.py
      - modules/common/logger.py
      - modules/common/rvu_calc.py
      - modules/common/sectionizer.py
      - modules/common/spans.py
      - modules/common/text_io.py
      - modules/common/umls_linking.py
    - modules/domain/
      - modules/domain/coding_rules/
      - modules/domain/knowledge_base/
      - modules/domain/procedure_store/
      - modules/domain/reasoning/
      - modules/domain/rvu/
      - modules/domain/text/
      - modules/domain/__init__.py
    - modules/infra/
      - modules/infra/__init__.py
      - modules/infra/nlp_warmup.py
    - modules/ml_coder/
      - modules/ml_coder/__init__.py
      - modules/ml_coder/data_prep.py
      - modules/ml_coder/predictor.py
      - modules/ml_coder/preprocessing.py
      - modules/ml_coder/registry_predictor.py
      - modules/ml_coder/registry_training.py
      - modules/ml_coder/self_correction.py
      - modules/ml_coder/thresholds.py
      - modules/ml_coder/training.py
      - modules/ml_coder/utils.py
    - modules/phi/
      - modules/phi/adapters/
      - modules/phi/__init__.py
      - modules/phi/db.py
      - modules/phi/models.py
      - modules/phi/ports.py
      - modules/phi/README.md
      - modules/phi/service.py
    - modules/proc_ml_advisor/
      - modules/proc_ml_advisor/__init__.py
      - modules/proc_ml_advisor/schemas.py
    - modules/registry/
      - modules/registry/adapters/
      - modules/registry/application/
      - modules/registry/extractors/
      - modules/registry/legacy/
      - modules/registry/ml/
      - modules/registry/slots/
      - modules/registry/__init__.py
      - modules/registry/cli.py
      - modules/registry/deterministic_extractors.py
      - modules/registry/ebus_config.py
      - modules/registry/engine.py
      - modules/registry/inference_onnx.py
      - modules/registry/inference_pytorch.py
      - modules/registry/ip_registry_improvements.md
      - modules/registry/ip_registry_schema_additions.json
      - modules/registry/model_bootstrap.py
      - modules/registry/model_runtime.py
      - modules/registry/normalization.py
      - modules/registry/postprocess.py
      - modules/registry/prompts.py
      - modules/registry/registry_system_prompt.txt
      - modules/registry/schema.py
      - modules/registry/schema_granular.py
      - modules/registry/self_correction.py
      - modules/registry/transform.py
      - modules/registry/v2_booleans.py
    - modules/registry_cleaning/
      - modules/registry_cleaning/__init__.py
      - modules/registry_cleaning/clinical_qc.py
      - modules/registry_cleaning/consistency_utils.py
      - modules/registry_cleaning/cpt_utils.py
      - modules/registry_cleaning/logging_utils.py
      - modules/registry_cleaning/schema_utils.py
    - modules/reporter/
      - modules/reporter/templates/
      - modules/reporter/__init__.py
      - modules/reporter/cli.py
      - modules/reporter/engine.py
      - modules/reporter/prompts.py
      - modules/reporter/schema.py
    - modules/reporting/
      - modules/reporting/second_pass/
      - modules/reporting/templates/
      - modules/reporting/__init__.py
      - modules/reporting/coder_view.py
      - modules/reporting/engine.py
      - modules/reporting/EXTRACTION_RULES.md
      - modules/reporting/inference.py
      - modules/reporting/ip_addons.py
      - modules/reporting/macro_engine.py
      - modules/reporting/metadata.py
      - modules/reporting/validation.py
    - modules/__init__.py
  - observability/
    - observability/__init__.py
    - observability/coding_metrics.py
    - observability/logging_config.py
    - observability/metrics.py
    - observability/timing.py
  - proc_autocode/
    - proc_autocode/ip_kb/
    - proc_autocode/rvu/
  - proc_kb/
    - proc_kb/ebus_config.yaml
  - proc_nlp/
    - proc_nlp/__init__.py
    - proc_nlp/normalize_proc.py
    - proc_nlp/umls_linker.py
  - proc_registry/
    - proc_registry/adapters/
  - proc_report/
  - proc_schemas/
    - proc_schemas/clinical/
      - proc_schemas/clinical/__init__.py
      - proc_schemas/clinical/airway.py
      - proc_schemas/clinical/common.py
      - proc_schemas/clinical/pleural.py
    - proc_schemas/registry/
      - proc_schemas/registry/__init__.py
      - proc_schemas/registry/ip_v2.py
      - proc_schemas/registry/ip_v3.py
    - proc_schemas/__init__.py
    - proc_schemas/billing.py
    - proc_schemas/coding.py
    - proc_schemas/envelope_models.py
    - proc_schemas/procedure_report.py
    - proc_schemas/reasoning.py
  - schemas/
    - schemas/IP_Registry.json
  - scripts/
    - scripts/apply_patch.py
    - scripts/build_registry_bundle.py
    - scripts/check_pydantic_models.py
    - scripts/clean_and_split_data.py
    - scripts/clean_and_split_data_updated.py
    - scripts/clean_and_split_data_updated_v2.py
    - scripts/clean_ip_registry.py
    - scripts/cleanup_v4_branch.sh
    - scripts/data_generators.py
    - scripts/data_generators_updated.py
    - scripts/data_generators_updated_v2.py
    - scripts/dev_pull_model.sh
    - scripts/devserver.sh
    - scripts/eval_hybrid_pipeline.py
    - scripts/evaluate_coder.py
    - scripts/evaluate_cpt.py
    - scripts/fit_thresholds_from_eval.py
    - scripts/fix_ml_data.py
    - scripts/fix_registry_data.py
    - scripts/generate_addon_templates.py
    - scripts/immediate_csv_fix.py
    - scripts/preflight.py
    - scripts/prepare_data.py
    - scripts/quantize_to_onnx.py
    - scripts/railway_start.sh
    - scripts/render_report.py
    - scripts/review_llm_fallback_errors.py
    - scripts/run_cleaning_pipeline.py
    - scripts/run_coder_hybrid.py
    - scripts/self_correct_registry.py
    - scripts/Smart_splitter.py
    - scripts/Smart_splitter_updated.py
    - scripts/Smart_splitter_updated_v2.py
    - scripts/train_cpt_custom.py
    - scripts/train_roberta.py
    - scripts/train_roberta_pm3.py
    - scripts/upload_registry_bundle.sh
    - scripts/validate_golden_extractions.py
    - scripts/validate_jsonschema.py
    - scripts/validate_registry2.py
    - scripts/verify_active_app.sh
    - scripts/verify_v4_enhancements.sh
    - scripts/warm_models.py
  - tests/
    - tests/api/
      - tests/api/conftest.py
      - tests/api/test_coding_phi_gating.py
      - tests/api/test_fastapi.py
      - tests/api/test_phi_demo_cases.py
      - tests/api/test_phi_endpoints.py
      - tests/api/test_registry_extract_endpoint.py
      - tests/api/test_ui.py
    - tests/coder/
      - tests/coder/test_coder_qa_regressions.py
      - tests/coder/test_coder_smoke.py
      - tests/coder/test_enhanced_rationale.py
      - tests/coder/test_hierarchy_bundling_fixes.py
      - tests/coder/test_mer_ncci.py
      - tests/coder/test_navigation_qa.py
      - tests/coder/test_pleuroscopy_patterns.py
      - tests/coder/test_reconciliation.py
      - tests/coder/test_registry_coder.py
      - tests/coder/test_regression_notes.py
      - tests/coder/test_rules_engine.py
      - tests/coder/test_smart_hybrid_policy.py
      - tests/coder/test_stent_removal.py
      - tests/coder/test_synthetic_patterns.py
      - tests/coder/test_terminology_utils.py
    - tests/coding/
      - tests/coding/test_ebus_integration.py
      - tests/coding/test_ebus_rules.py
      - tests/coding/test_enhanced_cptcoder_rules.py
      - tests/coding/test_enhanced_cptcoder_validation_regressions.py
      - tests/coding/test_hierarchy_normalization.py
      - tests/coding/test_json_rules_parity.py
      - tests/coding/test_ncci_bundling.py
      - tests/coding/test_peripheral_integration.py
      - tests/coding/test_peripheral_rules.py
      - tests/coding/test_phi_gating.py
      - tests/coding/test_rules_engine_phase1.py
      - tests/coding/test_rules_validation.py
      - tests/coding/test_sectionizer.py
      - tests/coding/test_sectionizer_integration.py
    - tests/contracts/
      - tests/contracts/.gitkeep
      - tests/contracts/test_coder_regressions.py
      - tests/contracts/test_compose_and_code.py
      - tests/contracts/test_registry_adapter.py
    - tests/e2e/
      - tests/e2e/test_coder_e2e.py
      - tests/e2e/test_registry_e2e.py
    - tests/fixtures/
      - tests/fixtures/.gitkeep
      - tests/fixtures/blvr_two_lobes.txt
      - tests/fixtures/complex_tracheal_stenosis.txt
      - tests/fixtures/ebus_staging_4R_7_11R.txt
      - tests/fixtures/ppl_nav_radial_tblb.txt
      - tests/fixtures/stent_rmb_and_dilation_lul.txt
      - tests/fixtures/therapeutic_aspiration_repeat_stay.txt
      - tests/fixtures/thora_bilateral.txt
    - tests/helpers/
      - tests/helpers/phi_asserts.py
    - tests/integration/
      - tests/integration/api/
      - tests/integration/coder/
      - tests/integration/persistence/
      - tests/integration/.gitkeep
      - tests/integration/test_phi_workflow_end_to_end.py
      - tests/integration/test_placeholder.py
    - tests/ml_advisor/
      - tests/ml_advisor/__init__.py
      - tests/ml_advisor/conftest.py
      - tests/ml_advisor/test_router.py
      - tests/ml_advisor/test_schemas.py
    - tests/ml_coder/
      - tests/ml_coder/__init__.py
      - tests/ml_coder/test_case_difficulty.py
      - tests/ml_coder/test_data_prep.py
      - tests/ml_coder/test_registry_data_prep.py
      - tests/ml_coder/test_registry_predictor.py
      - tests/ml_coder/test_training_pipeline.py
    - tests/phi/
      - tests/phi/test_fernet_encryption_adapter.py
      - tests/phi/test_manual_scrub.py
      - tests/phi/test_models.py
      - tests/phi/test_presidio_scrubber_adapter.py
      - tests/phi/test_service.py
    - tests/registry/
      - tests/registry/test_action_predictor.py
      - tests/registry/test_cao_extraction.py
      - tests/registry/test_ebus_config_station_count.py
      - tests/registry/test_ebus_deterministic.py
      - tests/registry/test_extraction_quality.py
      - tests/registry/test_granular_registry_models.py
      - tests/registry/test_new_extractors.py
      - tests/registry/test_normalization.py
      - tests/registry/test_pleural_extraction.py
      - tests/registry/test_registry_extraction_ebus.py
      - tests/registry/test_registry_qa_regressions.py
      - tests/registry/test_registry_service_hybrid_flow.py
      - tests/registry/test_sedation_blvr.py
      - tests/registry/test_slots_ebus_tblb.py
    - tests/reporter/
      - tests/reporter/test_ip_addons.py
      - tests/reporter/test_macro_engine_features.py
      - tests/reporter/test_reporter_engine.py
      - tests/reporter/test_struct_from_free_text.py
      - tests/reporter/test_template_render.py
    - tests/unit/
      - tests/unit/.gitkeep
      - tests/unit/__init__.py
      - tests/unit/test_cpt_cleaning.py
      - tests/unit/test_dsl.py
      - tests/unit/test_extraction_adapters.py
      - tests/unit/test_inference_engine.py
      - tests/unit/test_inmemory_procedure_store.py
      - tests/unit/test_knowledge.py
      - tests/unit/test_no_legacy_imports.py
      - tests/unit/test_procedure_type_detector.py
      - tests/unit/test_rules.py
      - tests/unit/test_schemas.py
      - tests/unit/test_structured_reporter.py
      - tests/unit/test_template_cache.py
      - tests/unit/test_template_coverage.py
      - tests/unit/test_templates.py
      - tests/unit/test_validation_engine.py
    - tests/utils/
      - tests/utils/case_filter.py
    - tests/conftest.py
    - tests/test_clean_ip_registry.py
    - tests/test_registry_normalization.py
  - .env
  - .env.example
  - .gitattributes
  - .gitignore
  - .pre-commit-config.yaml
  - .setup.stamp
  - alembic.ini
  - aws-g5-key.pem
  - CLAUDE.md
  - diagnose_codex.sh
  - geminiquota.py
  - ip_golden_knowledge_v2_2.json
  - Makefile
  - pyproject.toml
  - README.md
  - requirements-train.txt
  - requirements.txt
  - runtime.txt
  - test_gemini_simple.py
  - update_nodejs_conda.sh
```

## Important directories (not inlined)
- `modules/`
- `proc_report/`
- `proc_autocode/`
- `proc_nlp/`
- `proc_registry/`
- `proc_schemas/`
- `schemas/`
- `configs/`
- `scripts/`
- `tests/`

## Important files (inlined)

---
### `README.md`
```
# Procedure Suite

**Automated CPT Coding, Registry Extraction, and Synoptic Reporting for Interventional Pulmonology.**

This toolkit enables:
1.  **Predict CPT Codes**: Analyze procedure notes using ML + LLM hybrid pipeline to generate billing codes with RVU calculations.
2.  **Extract Registry Data**: Use deterministic extractors and LLMs to extract structured clinical data (EBUS stations, complications, demographics) into a validated schema.
3.  **Generate Reports**: Create standardized, human-readable procedure reports from structured data.

## Documentation

- **[Installation & Setup](docs/INSTALLATION.md)**: Setup guide for Python, spaCy models, and API keys.
- **[User Guide](docs/USER_GUIDE.md)**: How to use the CLI tools and API endpoints.
- **[Development Guide](docs/DEVELOPMENT.md)**: **CRITICAL** for contributors and AI Agents. Defines the system architecture and coding standards.
- **[Architecture](docs/ARCHITECTURE.md)**: System design, module breakdown, and data flow.
- **[Agents](docs/AGENTS.md)**: Multi-agent pipeline documentation for Parser, Summarizer, and Structurer.
- **[Registry API](docs/Registry_API.md)**: Registry extraction service API documentation.
- **[CPT Reference](docs/REFERENCES.md)**: List of supported codes.

## Quick Start

1.  **Install**:
    ```bash
    micromamba activate medparse-py311
    make install
    make preflight
    ```

2.  **Configure**:
    Create `.env` with your `GEMINI_API_KEY`.

3.  **Run**:
    ```bash
    # Start the API/Dev Server
    ./scripts/devserver.sh
    ```

## Key Modules

| Module | Description |
|--------|-------------|
| **`modules/api/fastapi_app.py`** | Main FastAPI backend |
| **`modules/coder/`** | CPT coding engine with CodingService (8-step pipeline) |
| **`modules/ml_coder/`** | ML-based code predictor and training pipeline |
| **`modules/registry/`** | Registry extraction with RegistryService and RegistryEngine |
| **`modules/agents/`** | 3-agent pipeline: Parser → Summarizer → Structurer |
| **`modules/reporter/`** | Template-based synoptic report generator |
| **`/ui/phi_demo.html`** | Synthetic PHI demo UI for scrubbing → vault → review → reidentify |

## System Architecture

> **Note:** The repository is in an architectural pivot toward **Extraction‑First**
> (Registry extraction → deterministic CPT rules). The current production pipeline
> remains ML‑First for CPT and hybrid‑first for registry; sections below describe
> current behavior unless explicitly labeled as “Target.”

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Procedure Note                               │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FastAPI Layer (modules/api/)                      │
│  • /v1/coder/run - CPT coding endpoint                              │
│  • /v1/registry/run - Registry extraction endpoint                  │
│  • /v1/report/render - Report generation endpoint                   │
└─────────────────────────────────────────────────────────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  CodingService  │    │ RegistryService │    │    Reporter     │
│  (8-step pipe)  │    │ (Hybrid-first)  │    │ (Jinja temps)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │
         ▼                        ▼
┌─────────────────┐    ┌─────────────────┐
│ SmartHybrid     │    │ RegistryEngine  │
│ Orchestrator    │    │ (LLM Extract)   │
│ ML→Rules→LLM    │    │                 │
└─────────────────┘    └─────────────────┘
```

### ML-First Hybrid Pipeline (CodingService)

The coding system uses a **SmartHybridOrchestrator** that prioritizes ML predictions:

1. **ML Prediction** → Predict CPT codes with confidence scores
2. **Difficulty Classification** → HIGH_CONF / GRAY_ZONE / LOW_CONF
3. **Decision Gate**:
   - HIGH_CONF + rules pass → Use ML codes directly (fast path, no LLM)
   - GRAY_ZONE or rules fail → LLM as judge
   - LOW_CONF → LLM as primary coder
4. **Rules Validation** → NCCI/MER compliance checks
5. **Final Codes** → CodeSuggestion objects for review

### Hybrid-First Registry Extraction (RegistryService)

Registry extraction follows a hybrid approach:

1. **CPT Coding** → Get codes from SmartHybridOrchestrator
2. **CPT Mapping** → Map CPT codes to registry boolean flags
3. **LLM Extraction** → Extract additional fields via RegistryEngine
4. **Reconciliation** → Merge CPT-derived and LLM-extracted fields
5. **Validation** → Validate against IP_Registry.json schema

## Data & Schemas

| File | Purpose |
|------|---------|
| `data/knowledge/ip_coding_billing_v2_8.json` | CPT codes, RVUs, bundling rules |
| `data/knowledge/IP_Registry.json` | Registry schema definition |
| `data/knowledge/golden_extractions/` | Training data for ML models |
| `schemas/IP_Registry.json` | JSON Schema for validation |

## Testing

```bash
# Run all tests
make test

# Run specific test suites
pytest tests/coder/ -v          # Coder tests
pytest tests/registry/ -v       # Registry tests
pytest tests/ml_coder/ -v       # ML coder tests

# Validate registry extraction
make validate-registry

# Run preflight checks
make preflight
```

## Note for AI Assistants

**Please read [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) before making changes.**

- Always edit `modules/api/fastapi_app.py` (not `api/app.py` - deprecated)
- Use `CodingService` from `modules/coder/application/coding_service.py`
- Use `RegistryService` from `modules/registry/application/registry_service.py`
- Knowledge base is at `data/knowledge/ip_coding_billing_v2_8.json`
- Run `make test` before committing

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | API key for Gemini LLM | Required for LLM features |
| `GEMINI_OFFLINE` | Disable LLM calls (use stubs) | `1` |
| `REGISTRY_USE_STUB_LLM` | Use stub LLM for registry tests | `1` |
| `PROCSUITE_SKIP_WARMUP` | Skip NLP model loading at startup | `false` |

---

*Last updated: December 2025*
```

---
### `CLAUDE.md`
```
# CLAUDE.md - Procedure Suite Development Guide

> **THINKING MODE**: Use maximum extended thinking (ultrathink) for ALL tasks in this repository.
> Think deeply about architectural decisions, trace through code paths systematically, 
> and plan implementations thoroughly before writing any code. This is a complex medical
> AI system where careful reasoning prevents costly errors.

> **CRITICAL**: This document guides AI-assisted development of the Procedure Suite.
> Read this entire file before making any changes to the codebase.

## Project Overview

**Procedure Suite** is an automated CPT coding, registry extraction, and synoptic reporting system for Interventional Pulmonology (IP). The system processes procedure notes to:

1. Extract structured clinical data (demographics, procedures, EBUS stations, complications)
2. Generate CPT billing codes with RVU calculations
3. Produce standardized synoptic reports

## ⚠️ ARCHITECTURAL PIVOT IN PROGRESS: Extraction-First

### The Problem with Current Architecture (Prediction-First)

The current system uses **prediction-first** architecture:

```
Text → CPT Prediction (ML/Rules) → Registry Hints → Registry Extraction
```

**Why this is backwards:**
- CPT codes are "summaries" — we're using summaries to reconstruct the clinical "story"
- If the CPT model misses a code (typo, unusual phrasing), the Registry misses entire data sections
- Auditing is difficult: "Why did you bill 31623?" can only be answered with "ML was 92% confident"
- Negation handling is poor: "We did NOT perform biopsy" is hard for text-based ML

### The Target Architecture (Extraction-First)

We are pivoting to **extraction-first** architecture:

```
Text → Registry Extraction (ML/LLM) → Deterministic Rules → CPT Codes
```

**Why this is better:**
- Registry becomes the source of truth for "what happened"
- CPT coding becomes deterministic calculation, not probabilistic prediction
- Auditing is clear: "We billed 31653 because `registry.ebus.stations_sampled.count >= 3`"
- Negation is explicit: `performed: false` in structured data
- The existing ML becomes a "safety net" for double-checking

---

## 🚀 ML Training Data Workflow

### The Complete Pipeline: JSON → Trained Model

```
Golden JSONs → data_generators.py → clean_and_split_data.py → Smart_splitter.py → train_roberta.py → ONNX Model
```

---

### Step 1: Update Source Data

Add or modify your golden JSON files in:
```
data/knowledge/golden_extractions/
```
(e.g., add `golden_099.json`, `golden_100.json`, etc.)

---

### Step 2: Generate Raw CSVs

Run the generator script. This reads all JSONs, rebuilds `train_flat.csv`, and regenerates `registry_train.csv` with the latest data and schema/flag definitions.

```bash
python scripts/data_generators.py
```

**What this does:**
- Scans all `golden_*.json` files
- Updates `data/ml_training/train_flat.csv` (the raw map of text → codes)
- Updates `data/ml_training/registry_train.csv` (calculates all the 0/1 flags based on the latest logic)

> **Note:** This file will still contain duplicates and potential leakage at this stage.

---

### Step 3: Clean & Split (The V2 Fix)

Run the cleaning script. This takes the "raw" output from Step 2, dedupes it, removes garbage rows, and strictly splits by Patient ID (`source_file`) to prevent leakage.

```bash
python scripts/clean_and_split_data.py
```

**What this does:**
- Reads the updated `registry_train.csv` (and existing test/edge files)
- Consolidates everything into one pool
- Removes conflicts (e.g., same text having different labels)
- Outputs:
  - `data/ml_training/cleaned_v2/registry_train_clean.csv`
  - `data/ml_training/cleaned_v2/registry_val_clean.csv`
  - `data/ml_training/cleaned_v2/registry_test_clean.csv`

---

### Step 4: Optimize Class Balance (Smart Splitter)

Run the smart splitter to optimize rare class coverage in val/test sets.

```bash
python scripts/Smart_splitter.py
```

**What this does:**
- Loads all 3 splits from cleaned_v2/ and recombines them
- Drops globally empty labels (e.g., `bronchial_wash`, `photodynamic_therapy`)
- Identifies **single-source labels** (labels that exist in only one source_file) and forces those files into Train
- Searches 1000 random seeds to find the split that maximizes rare label coverage in Val/Test
- Outputs optimized splits to `data/ml_training/cleaned_v3_balanced/`

**Why this matters:**
If a rare label (e.g., `brachytherapy_catheter`) only appears in one source file, a random split might put all examples in Test, leaving zero training examples. The smart splitter prevents this by locking single-source files to Train.

**Outputs:**
- `data/ml_training/cleaned_v3_balanced/registry_train_clean.csv`
- `data/ml_training/cleaned_v3_balanced/registry_val_clean.csv`
- `data/ml_training/cleaned_v3_balanced/registry_test_clean.csv`
- `data/ml_training/cleaned_v3_balanced/registry_label_fields.json`

---

### Step 5: Train Model

Run the training script using the balanced V3 data.

```bash
python scripts/train_roberta.py \
  --train-csv data/ml_training/cleaned_v3_balanced/registry_train_clean.csv \
  --val-csv data/ml_training/cleaned_v3_balanced/registry_val_clean.csv \
  --test-csv data/ml_training/cleaned_v3_balanced/registry_test_clean.csv
```

Or update the defaults in train_roberta.py and run:
```bash
python scripts/train_roberta.py --batch-size 16 --epochs 5
```

---

### Summary of Script Responsibilities

| Script | Responsibility | Input | Output |
|--------|---------------|-------|--------|
| `data_generators.py` | **Extraction & Logic** - Extracts text/codes from JSON and computes the flag columns | Golden JSONs | `registry_train.csv`, `train_flat.csv` |
| `clean_and_split_data.py` | **Hygiene & Splitting** - Deduplicates rows, fixes conflicts, splits by Patient ID | `registry_train.csv`, `train_flat.csv` | `cleaned_v2/*.csv` |
| `Smart_splitter.py` | **Balance Optimization** - Forces single-source labels to Train, optimizes rare class coverage | `cleaned_v2/*.csv` | `cleaned_v3_balanced/*.csv` |
| `train_roberta.py` | **Modeling** - Learns to predict the flags from the text | `cleaned_v3_balanced/*.csv` | `data/models/roberta_registry/` |

**Why the multi-step pipeline?**
- **Step 2 vs Step 3**: If you modify `data_generators.py` to change how a flag is calculated, Step 2 updates the columns in the raw CSV. Step 3 ensures rows are cleanly distributed into Train/Val/Test without leakage.
- **Step 3 vs Step 4**: Step 3 does basic splitting by Patient ID. Step 4 (Smart Splitter) further optimizes to ensure rare labels have representation in both Train and Val/Test sets, preventing zero-support classes that would drag down Macro F1.

---

## 🚀 Implementation Roadmap

### Phase 1: Data Preparation (Local)

**Goal**: Build clean, leak-free, class-balanced training data from Golden JSON notes.

**Tasks:**

1. **Add/Update Golden JSONs** in `data/knowledge/golden_extractions/`
2. **Run `data_generators.py`** to extract flags from JSONs
3. **Run `clean_and_split_data.py`** to create leak-free splits
4. **Run `Smart_splitter.py`** to optimize rare class coverage

**Output:**
- `data/ml_training/cleaned_v3_balanced/registry_train_clean.csv`
- `data/ml_training/cleaned_v3_balanced/registry_val_clean.csv`
- `data/ml_training/cleaned_v3_balanced/registry_test_clean.csv`
- `data/ml_training/cleaned_v3_balanced/registry_label_fields.json`

---

### Phase 2: BiomedBERT Training (Local - Fast Track)

**Goal**: Train a high-performance deep learning model. This will likely be sufficient.

**Hardware/Environment:**
- **GPU**: RTX 4070 Ti (local)
- **Framework**: PyTorch with CUDA 11.8/12.1
- **Mixed Precision**: `fp16=True`

**Model Selection:**
- **Primary**: `microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext` (#1 on BLURB benchmark)
- **Alternative**: `RoBERTa-large-PM-M3-Voc` for teacher-student distillation

**Key Training Features:**
- **Head + Tail Truncation**: Keeps first 382 + last 128 tokens (preserves complications at end)
- **pos_weight**: Upweights rare classes (capped at 100x)
- **Per-Class Threshold Optimization**: F1-optimal thresholds per label (not uniform 0.5)

**Training Script** (`scripts/train_roberta.py`):

```bash
python scripts/train_roberta.py --batch-size 16 --epochs 5
```

**Success Criteria:**
- Macro F1 Score > 0.90 on test set
- F1 > 0.85 on rare classes (BLVR, thermal ablation, cryotherapy)
- **If criteria met → SKIP Phase 3, proceed to Phase 4**

**Checklist:**
- [x] Configure PyTorch with CUDA
- [x] Implement `scripts/train_roberta.py` with Head+Tail truncation
- [x] Calculate `pos_weight` for class imbalance
- [x] Per-class threshold optimization
- [ ] Train model with fp16 mixed precision
- [ ] Evaluate Macro F1 on test set
- [ ] Evaluate F1 on rare classes specifically

---

### Phase 3: Teacher-Student Distillation (Cloud - CONDITIONAL)

> **Only execute if Phase 2 fails success criteria (Macro F1 ≤ 0.90 OR rare-class F1 ≤ 0.85)**

**Goal**: Use a larger model to "teach" the smaller model through knowledge distillation.

**Steps:**

1. **Rent Cloud GPU** (~1 hour)
   - Options: Lambda Labs, AWS (A10G), RunPod
   - Target: NVIDIA A10G or A100

2. **Train Teacher Model**
   - Model: `RoBERTa-large-PM-M3-Voc` (larger variant)
   - Fine-tune on augmented training data

3. **Generate Soft Labels**
   - Run trained Teacher on Training Data
   - Save output logits: `teacher_logits.pt`

4. **Retrain Student (Local)**
   - Return to RTX 4070 Ti
   - Loss function: `0.5 * GroundTruthLoss + 0.5 * TeacherDistillationLoss`

**Checklist:**
- [ ] Spin up cloud GPU (if needed)
- [ ] Train teacher model
- [ ] Export soft labels to `teacher_logits.pt`
- [ ] Retrain student with distillation loss

---

### Phase 4: Rules Engine (Deterministic Logic)

**Goal**: Derive CPT codes from Registry flags deterministically—no ML guessing for the final coding step.

**Location**: `data/rules/coding_rules.py`

**Implementation Pattern:**

```python
# data/rules/coding_rules.py

def rule_31652(registry: dict) -> bool:
    """EBUS-TBNA, 1-2 stations."""
    return (
        registry.get("linear_ebus", False) and 
        1 <= registry.get("stations_sampled", 0) <= 2
    )

def rule_31653(registry: dict) -> bool:
    """EBUS-TBNA, 3+ stations."""
    return (
        registry.get("linear_ebus", False) and 
        registry.get("stations_sampled", 0) >= 3
    )

def rule_31625(registry: dict) -> bool:
    """Bronchoscopy with transbronchial biopsy."""
    return registry.get("transbronchial_biopsy", False)

def rule_31627(registry: dict) -> bool:
    """Navigation add-on (requires primary procedure)."""
    return registry.get("navigation_used", False)

def derive_all_codes(registry: dict) -> list[str]:
    """Master function to derive all applicable CPT codes."""
    codes = []
    
    # EBUS (mutually exclusive)
    if rule_31653(registry):
        codes.append("31653")
    elif rule_31652(registry):
        codes.append("31652")
    
    # Biopsies
    if rule_31625(registry):
        codes.append("31625")
    
    # Add-ons (only if primary exists)
    if codes and rule_31627(registry):
        codes.append("31627")
    
    return codes
```

**Validation Process:**
1. Run all 5,000+ Golden Notes through the rules engine
2. Compare `Engine_CPT` vs. `Verified_CPT`
3. **Fix rules until 100% match on verified cases**

**Checklist:**
- [ ] Create `data/rules/coding_rules.py`
- [ ] Implement all CPT rule functions
- [ ] Create unit tests for each rule
- [ ] Validate against Golden Notes (target: 100% match)
- [ ] Document edge cases and exceptions

---

### Phase 5: Optimization & Deployment (Railway)

**Goal**: Deploy an optimized, cost-effective inference system on Railway Pro plan.

#### 5.1 Model Quantization (Local)

**Process:**
1. Convert trained PyTorch model (`.pt`) to **ONNX format**
2. Apply **INT8 quantization**

**Results:**
- Model size: ~350MB → ~80MB
- Inference speed: ~3x faster
- RAM usage: <500MB

**Script** (`scripts/quantize_to_onnx.py`):

```python
import torch
import onnx
from onnxruntime.quantization import quantize_dynamic, QuantType

# Export to ONNX
torch.onnx.export(model, dummy_input, "registry_model.onnx")

# INT8 Quantization
quantize_dynamic(
    "registry_model.onnx",
    "registry_model_int8.onnx",
    weight_type=QuantType.QUInt8
)
```

#### 5.2 ONNX Inference Service

**Location**: `modules/registry/inference_onnx.py`

```python
# modules/registry/inference_onnx.py
import onnxruntime as ort
import numpy as np

class ONNXRegistryPredictor:
    """Lightweight ONNX-based registry prediction."""
    
    def __init__(self, model_path: str = "models/registry_model_int8.onnx"):
        self.session = ort.InferenceSession(
            model_path,
            providers=['CPUExecutionProvider']
        )
    
    def predict(self, text: str) -> dict:
        """Run inference on procedure note text."""
        # Tokenize and run inference
        inputs = self._preprocess(text)
        outputs = self.session.run(None, inputs)
        return self._postprocess(outputs)
```

#### 5.3 Railway Deployment

**Benefits of INT8 Model:**
- RAM usage: <500MB (leaves room for app + overhead)
- No GPU required (CPU inference sufficient)
- Avoids Railway overage charges
- Response time: <100ms typical

**Checklist:**
- [ ] Export model to ONNX format
- [ ] Apply INT8 quantization
- [ ] Verify quantized model accuracy (should be ~same as original)
- [ ] Create `modules/registry/inference_onnx.py`
- [ ] Test locally with ONNX runtime
- [ ] Deploy to Railway
- [ ] Monitor RAM usage and response times

---

## Summary Checklist

| Phase | Task | Status |
|-------|------|--------|
| 1 | Add/update Golden JSONs → generate training CSVs | [ ] |
| 1 | Create leak-free, balanced train/val/test splits | [ ] |
| 2 | Train `microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext` on RTX 4070 Ti | [ ] |
| 2 | Achieve Macro F1 > 0.90 | [ ] |
| 3 | (Conditional) Teacher-student distillation | [ ] |
| 4 | Write deterministic CPT rule functions | [ ] |
| 4 | Validate rules against Golden Notes (100%) | [ ] |
| 5 | Convert model to ONNX INT8 | [ ] |
| 5 | Deploy to Railway | [ ] |

---

## Directory Structure

```
procedure-suite/
├── CLAUDE.md                          # THIS FILE - read first!
├── modules/
│   ├── api/
│   │   └── fastapi_app.py             # Main FastAPI backend (NOT api/app.py!)
│   ├── coder/
│   │   ├── application/
│   │   │   └── coding_service.py      # CodingService - main entry point
│   │   ├── adapters/
│   │   │   └── registry_coder.py      # Registry-based coder
│   │   └── domain/
│   │       └── smart_hybrid.py        # SmartHybridOrchestrator
│   ├── registry/
│   │   ├── application/
│   │   │   └── registry_service.py    # RegistryService - main entry point
│   │   ├── engine/
│   │   │   └── registry_engine.py     # LLM extraction logic
│   │   ├── inference_onnx.py          # NEW: ONNX inference service
│   │   └── ml/                        # Registry ML predictors
│   ├── agents/
│   │   ├── contracts.py               # Pydantic I/O schemas
│   │   ├── run_pipeline.py            # Pipeline orchestration
│   │   ├── parser/                    # ParserAgent
│   │   ├── summarizer/                # SummarizerAgent
│   │   └── structurer/                # StructurerAgent
│   ├── ml_coder/                      # ML-based CPT predictor
│   │   └── data_prep.py               # Train/test split generation
│   └── reporter/                      # Synoptic report generator
├── scripts/
│   ├── augment_registry_data.py       # Data augmentation for rare classes
│   ├── train_roberta.py               # RoBERTa training script
│   └── quantize_to_onnx.py            # ONNX conversion & quantization
├── data/
│   ├── knowledge/
│   │   ├── ip_coding_billing_v2_8.json  # CPT codes, RVUs, bundling rules
│   │   ├── IP_Registry.json             # Registry schema definition
│   │   └── golden_extractions/          # Training data
│   └── rules/
│       └── coding_rules.py            # Deterministic CPT derivation rules
├── models/
│   ├── registry_model.pt              # Trained PyTorch model
│   └── registry_model_int8.onnx       # Quantized ONNX model
├── schemas/
│   └── IP_Registry.json               # JSON Schema for validation
└── tests/
    ├── coder/
    ├── registry/
    ├── ml_coder/
    └── rules/                         # NEW: Rules engine tests
```

## Critical Development Rules

### 1. File Locations
- **ALWAYS** edit `modules/api/fastapi_app.py` — NOT `api/app.py` (deprecated)
- **ALWAYS** use `CodingService` from `modules/coder/application/coding_service.py`
- **ALWAYS** use `RegistryService` from `modules/registry/application/registry_service.py`
- Knowledge base is at `data/knowledge/ip_coding_billing_v2_8.json`
- Deterministic rules are at `data/rules/coding_rules.py`

### 2. Testing Requirements
- **ALWAYS** run `make test` before committing
- **ALWAYS** run `make preflight` for full validation
- Test commands:
  ```bash
  pytest tests/coder/ -v          # Coder tests
  pytest tests/registry/ -v       # Registry tests
  pytest tests/ml_coder/ -v       # ML coder tests
  pytest tests/rules/ -v          # Rules engine tests
  make validate-registry          # Registry extraction validation
  ```

### 3. Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | API key for Gemini LLM | Required for LLM |
| `GEMINI_OFFLINE` | Disable LLM calls (use stubs) | `1` |
| `REGISTRY_USE_STUB_LLM` | Use stub LLM for registry tests | `1` |
| `PROCSUITE_SKIP_WARMUP` | Skip NLP model loading | `false` |

### 4. Contract-First Development
All agents use Pydantic contracts defined in `modules/agents/contracts.py`:
- **ALWAYS** define input/output contracts before implementing
- **ALWAYS** include `status: Literal["ok", "degraded", "failed"]`
- **ALWAYS** include `warnings: List[AgentWarning]` and `errors: List[AgentError]`
- **ALWAYS** include `trace: Trace` for debugging

### 5. Status Tracking Pattern
```python
class MyAgentOut(BaseModel):
    status: Literal["ok", "degraded", "failed"]
    warnings: List[AgentWarning]
    errors: List[AgentError]
    trace: Trace
    # ... other fields
```

Pipeline behavior:
- `ok` → Continue to next stage
- `degraded` → Continue with warning
- `failed` → Stop pipeline, return partial results

---

## CPT Coding Rules Reference

### EBUS Codes
| Code | Description | Registry Condition |
|------|-------------|-------------------|
| 31652 | EBUS-TBNA, 1-2 stations | `ebus.performed AND len(ebus.stations) in [1,2]` |
| 31653 | EBUS-TBNA, 3+ stations | `ebus.performed AND len(ebus.stations) >= 3` |

### Bronchoscopy Codes
| Code | Description | Registry Condition |
|------|-------------|-------------------|
| 31622 | Diagnostic bronchoscopy | `bronchoscopy.diagnostic AND NOT any_interventional` |
| 31623 | Bronchoscopy with brushing | `brushings.performed` |
| 31624 | Bronchoscopy with BAL | `bal.performed` |
| 31625 | Bronchoscopy with biopsy | `transbronchial_biopsy.performed` |
| 31627 | Navigation add-on | `navigation.performed` (add-on only) |

### Bundling Rules
- 31622 is bundled into any interventional procedure
- 31627 can only be billed with a primary procedure
- Multiple biopsies from same lobe = single code
- Check `data/knowledge/ip_coding_billing_v2_8.json` for NCCI/MER rules

---

## Agent Pipeline Reference

The 3-agent pipeline (`modules/agents/`) provides structured note processing:

```
Raw Text → Parser → Summarizer → Structurer → Registry + Codes
```

### ParserAgent
- **Input**: Raw procedure note text
- **Output**: Segmented sections (History, Procedure, Findings, etc.)
- **Location**: `modules/agents/parser/parser_agent.py`

### SummarizerAgent
- **Input**: Parsed segments
- **Output**: Section summaries and caveats
- **Location**: `modules/agents/summarizer/summarizer_agent.py`

### StructurerAgent
- **Input**: Summaries
- **Output**: Registry fields and CPT codes
- **Location**: `modules/agents/structurer/structurer_agent.py`

### Usage
```python
from modules.agents.run_pipeline import run_pipeline

result = run_pipeline({
    "note_id": "test_001",
    "raw_text": "History: 65yo male with lung nodule..."
})

print(result["registry"])  # Structured data
print(result["codes"])     # CPT codes
```

---

## Testing Patterns

### Unit Test Pattern
```python
def test_ebus_three_stations_produces_31653():
    """Deterministic test: 3+ stations = 31653."""
    record = RegistryRecord(
        procedures=Procedures(
            ebus=EBUSRecord(
                performed=True,
                stations=["4R", "7", "11L"]
            )
        )
    )
    
    coder = RegistryBasedCoder()
    codes = coder.derive_codes(record)
    
    assert "31653" in [c["code"] for c in codes]
```

### Rules Engine Test Pattern
```python
def test_rule_31653():
    """Test EBUS 3+ stations rule."""
    registry = {
        "linear_ebus": True,
        "stations_sampled": 4
    }
    assert rule_31653(registry) is True
    
    registry["stations_sampled"] = 2
    assert rule_31653(registry) is False

def test_rule_31652():
    """Test EBUS 1-2 stations rule."""
    registry = {
        "linear_ebus": True,
        "stations_sampled": 2
    }
    assert rule_31652(registry) is True
```

### Integration Test Pattern
```python
def test_extraction_first_pipeline():
    """Full pipeline test: text → registry → codes."""
    note = """
    Procedure: EBUS bronchoscopy with TBNA of stations 4R, 7, and 11L.
    Findings: All stations showed benign lymphoid tissue.
    """
    
    service = RegistryService()
    result = service.extract_and_code(note)
    
    assert result.registry.procedures.ebus.performed is True
    assert len(result.registry.procedures.ebus.stations) == 3
    assert "31653" in [c["code"] for c in result.codes]
    assert result.confidence == "high"
```

---

## Development Workflow

### Before Starting Any Task
1. Read this CLAUDE.md file completely
2. Review the specific module documentation in `docs/`
3. Understand the extraction-first goal
4. Identify which phase the task belongs to

### Making Changes
1. Create a feature branch
2. Write tests first (TDD)
3. Implement the feature
4. Run `make test` — all tests must pass
5. Run `make preflight` — all checks must pass
6. Update relevant documentation

### Code Review Checklist
- [ ] Follows extraction-first architecture
- [ ] Uses Pydantic contracts
- [ ] Includes status tracking (ok/degraded/failed)
- [ ] Has comprehensive tests
- [ ] Updates CLAUDE.md if architecture changes

---

## Troubleshooting

### Common Issues

**LLM calls failing in tests:**
```bash
export GEMINI_OFFLINE=1
export REGISTRY_USE_STUB_LLM=1
```

**NLP models not loading:**
```bash
export PROCSUITE_SKIP_WARMUP=true
make install  # Reinstall spaCy models
```

**Import errors:**
```bash
micromamba activate medparse-py311
pip install -e .
```

**ONNX inference issues:**
```bash
pip install onnxruntime  # CPU-only runtime
# or
pip install onnxruntime-gpu  # If GPU available
```

---

## Contact & Resources

- **Knowledge Base**: `data/knowledge/ip_coding_billing_v2_8.json`
- **Registry Schema**: `schemas/IP_Registry.json`
- **API Docs**: `docs/Registry_API.md`
- **CPT Reference**: `docs/REFERENCES.md`
- **Rules Engine**: `data/rules/coding_rules.py`

---

*Last updated: December 2025*
*Architecture: Extraction-First with RoBERTa ML + Deterministic Rules Engine*
*Deployment Target: Railway (ONNX INT8)*
```

---
### `pyproject.toml`
```
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "proc-suite"
version = "0.1.0"
requires-python = ">=3.11,<3.14"
dependencies = [
  "pydantic>=2.6,<3",
  "jinja2>=3.1,<4",
  "spacy>=3.7,<4",
  "scispacy==0.5.4",
  "en-core-sci-sm @ https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.4/en_core_sci_sm-0.5.4.tar.gz",
  "medspacy>=1.0,<2",
  "sqlalchemy>=2.0,<3",
  "alembic>=1.13,<2",
  "scikit-learn>=1.5,<2.0",
  "scikit-multilearn>=0.2.0,<1",
  "pandas>=2.0,<3",
  "psycopg[binary,pool]>=3.2,<4",
  "python-dotenv>=1.0,<2",
  "rapidfuzz>=3.9,<4",
  "regex>=2024.4.28",
  "jsonschema>=4.23,<5",
  "typer>=0.12,<0.17",
  "rich>=13,<14",
  "httpx>=0.27,<1",
  "boto3>=1.34,<2",
  "google-auth>=2.23,<3",
  "google-generativeai>=0.8,<1",
  "cryptography>=42.0,<45",
  "presidio-analyzer>=2.2,<3",
  "pyyaml>=6.0,<7",
]

[project.optional-dependencies]
api = [
  "fastapi>=0.115",
  "uvicorn>=0.30",
]
dev = [
  "pytest",
  "pytest-cov",
  "ruff",
  "mypy",
  "types-regex",
  "httpx",
  "pytest-asyncio",
]

[tool.setuptools.packages.find]
where = ["."]

[tool.setuptools.package-data]
"modules.reporting" = ["templates/*.jinja", "templates/**/*.jinja", "templates/**/*.j2", "templates/.keep"]
"configs" = ["**/*.yaml", "**/*.json", "**/*.j2"]
"modules.api" = ["static/**/*"]

[tool.pytest.ini_options]
addopts = "-ra -q"
testpaths = ["tests"]
pythonpath = ["."]
markers = [
    "ebus: mark test as EBUS-specific registry extraction test"
]

[tool.ruff]
line-length = 100
extend-exclude = [
  "proc_nlp",
  "proc_schemas",
  "proc_suite.egg-info",
  "modules/autocode",
  "modules/reporting",
  "modules/registry/legacy",
]
include = [
  "modules/api/**/*.py",
  "modules/common/knowledge*.py",
  "modules/common/knowledge_cli.py",
  "modules/registry/cli.py",
  "modules/reporter/cli.py",
  "tests/api/**/*.py",
  "tests/unit/test_knowledge.py",
  "tests/conftest.py",
  "tests/coder/test_coder_smoke.py",
]

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]
extend-ignore = ["UP006", "UP035"]

[tool.ruff.lint.per-file-ignores]
"modules/coder/dictionary.py" = ["E501"]

[tool.mypy]
strict = true
plugins = []
exclude = [
    "docs/",
    "_archive/",
    "procedure_suite_ml_implimentation/",
]
explicit_package_bases = true

[[tool.mypy.overrides]]
module = "modules.*"
ignore_errors = true

[[tool.mypy.overrides]]
module = "modules.api.*"
ignore_errors = false

[[tool.mypy.overrides]]
module = "modules.common.knowledge"
ignore_errors = false

[[tool.mypy.overrides]]
module = "modules.common.knowledge_schema"
ignore_errors = false

[[tool.mypy.overrides]]
module = "modules.common.knowledge_cli"
ignore_errors = false

[[tool.mypy.overrides]]
module = "modules.registry.cli"
ignore_errors = false

[[tool.mypy.overrides]]
module = "modules.reporter.cli"
ignore_errors = false
```

---
### `requirements.txt`
```
# Requirements for Railway deployment
# Generated from pyproject.toml

# Core dependencies
pydantic>=2.6,<3
jinja2>=3.1,<4
spacy>=3.7,<4
scispacy==0.5.4
# spaCy language model required for umls_linker
en-core-sci-sm @ https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.4/en_core_sci_sm-0.5.4.tar.gz
medspacy>=1.0,<2
sqlalchemy>=2.0,<3
alembic>=1.13,<2
scikit-learn>=1.7,<1.8
scikit-multilearn>=0.2.0,<1
pandas>=2.0,<3
psycopg[binary,pool]>=3.2,<4
python-dotenv>=1.0,<2
cryptography>=46.0,<47
rapidfuzz>=3.9,<4
regex>=2024.4.28
jsonschema>=4.23,<5
typer>=0.12,<0.17
rich>=13,<14
httpx>=0.27,<1
boto3>=1.34,<2
google-auth>=2.23,<3
google-generativeai>=0.8,<1
presidio-analyzer>=2.2,<3
pyyaml>=6.0,<7

# ONNX inference (for BiomedBERT registry predictor)
onnxruntime>=1.16,<2
transformers>=4.35,<5

# API dependencies (required for FastAPI server)
fastapi>=0.115
uvicorn>=0.30
```

---
### `Makefile`
```
SHELL := /bin/bash
.PHONY: setup lint typecheck test validate-schemas validate-kb autopatch autocommit codex-train codex-metrics run-coder dev-iu pull-model-pytorch

# Use conda environment medparse-py311 (Python 3.11)
CONDA_ACTIVATE := source ~/miniconda3/etc/profile.d/conda.sh && conda activate medparse-py311
SETUP_STAMP := .setup.stamp
PYTHON := python
KB_PATH := data/knowledge/ip_coding_billing_v2_8.json
SCHEMA_PATH := data/knowledge/IP_Registry.json
NOTES_PATH := data/knowledge/synthetic_notes_with_registry2.json
PORT ?= 8000
MODEL_BACKEND ?= pytorch
PROCSUITE_SKIP_WARMUP ?= 1
REGISTRY_RUNTIME_DIR ?= data/models/registry_runtime

setup:
	@if [ -f $(SETUP_STAMP) ]; then echo "Setup already done"; exit 0; fi
	$(CONDA_ACTIVATE) && pip install -r requirements.txt
	touch $(SETUP_STAMP)

lint:
	$(CONDA_ACTIVATE) && ruff check --cache-dir .ruff_cache .

typecheck:
	$(CONDA_ACTIVATE) && mypy --cache-dir .mypy_cache .

test:
	$(CONDA_ACTIVATE) && pytest

# Validate JSON schemas and Pydantic models
validate-schemas:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/validate_jsonschema.py --schema $(SCHEMA_PATH) || true
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/check_pydantic_models.py

# Validate knowledge base
validate-kb:
	@echo "Validating knowledge base at $(KB_PATH)..."
	$(CONDA_ACTIVATE) && $(PYTHON) -c "import json; json.load(open('$(KB_PATH)'))" && echo "KB JSON valid"

# Run the smart-hybrid coder over notes
run-coder:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/run_coder_hybrid.py \
		--notes $(NOTES_PATH) \
		--kb $(KB_PATH) \
		--keyword-dir data/keyword_mappings \
		--out-json outputs/coder_suggestions.jsonl

pull-model-pytorch:
	MODEL_BUNDLE_S3_URI_PYTORCH="$(MODEL_BUNDLE_S3_URI_PYTORCH)" REGISTRY_RUNTIME_DIR="$(REGISTRY_RUNTIME_DIR)" ./scripts/dev_pull_model.sh

dev-iu:
	$(CONDA_ACTIVATE) && \
		MODEL_BACKEND="$(MODEL_BACKEND)" \
		REGISTRY_RUNTIME_DIR="$(REGISTRY_RUNTIME_DIR)" \
		PROCSUITE_SKIP_WARMUP="$(PROCSUITE_SKIP_WARMUP)" \
		RAILWAY_ENVIRONMENT="local" \
		$(PYTHON) -m uvicorn modules.api.fastapi_app:app --reload --host 0.0.0.0 --port "$(PORT)"

# Run cleaning pipeline with patches
autopatch:
	@mkdir -p autopatches reports
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/run_cleaning_pipeline.py \
		--notes $(NOTES_PATH) \
		--kb $(KB_PATH) \
		--schema $(SCHEMA_PATH) \
		--out-json autopatches/patches.json \
		--out-csv reports/errors.csv \
		--apply-minimal-fixes || true

# Autocommit generated patches/reports
autocommit:
	@git add .
	@git commit -m "Autocommit: generated patches/reports" || true

# Run codex training pipeline (full CI-like flow)
codex-train: setup lint typecheck test validate-schemas validate-kb autopatch
	@echo "Codex training pipeline complete"

# Run metrics over a batch of notes
codex-metrics: setup
	@mkdir -p outputs
	@echo "Running metrics pipeline..."
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/run_coder_hybrid.py \
		--notes $(NOTES_PATH) \
		--kb $(KB_PATH) \
		--keyword-dir data/keyword_mappings \
		--out-json outputs/metrics_run.jsonl
	@echo "Metrics written to outputs/metrics_run.jsonl"

# Clean generated files
clean:
	rm -rf $(SETUP_STAMP)
	rm -rf .ruff_cache .mypy_cache .pytest_cache
	rm -rf outputs autopatches reports
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Help target
help:
	@echo "Available targets:"
	@echo "  setup          - Install dependencies in conda env medparse-py311"
	@echo "  lint           - Run ruff linter"
	@echo "  typecheck      - Run mypy type checker"
	@echo "  test           - Run pytest"
	@echo "  validate-schemas - Validate JSON schemas and Pydantic models"
	@echo "  validate-kb    - Validate knowledge base"
	@echo "  run-coder      - Run smart-hybrid coder over notes"
	@echo "  autopatch      - Generate patches for registry cleaning"
	@echo "  autocommit     - Git commit generated files"
	@echo "  codex-train    - Full training pipeline"
	@echo "  codex-metrics  - Run metrics over notes batch"
	@echo "  clean          - Remove generated files"
```

---
### `runtime.txt`
```
python-3.11
```

---
### `modules/api/fastapi_app.py`
```
"""FastAPI application wiring for the Procedure Suite services.

⚠️ SOURCE OF TRUTH: This is the MAIN FastAPI application.
- Running on port 8000 via scripts/devserver.sh
- Uses CodingService from modules/coder/application/coding_service.py (new hexagonal architecture)
- DO NOT edit api/app.py - it's deprecated

See AI_ASSISTANT_GUIDE.md for details.
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

# Load .env file early so API keys are available
from dotenv import load_dotenv
# Prefer explicitly-exported environment variables over values in `.env`.
load_dotenv(override=False)
import subprocess
import uuid
from dataclasses import asdict
from functools import lru_cache
from pathlib import Path
from typing import Any, AsyncIterator, List

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Coding entry points:
# - Primary: /api/v1/procedures/{id}/codes/suggest (CodingService, PHI-gated)
# - Legacy shim: /v1/coder/run (non-PHI/synthetic only; blocked when CODER_REQUIRE_PHI_REVIEW=true)

# Import ML Advisor router
from modules.api.ml_advisor_router import router as ml_advisor_router
from modules.api.routes.phi import router as phi_router
from modules.api.routes.procedure_codes import router as procedure_codes_router
from modules.api.routes.metrics import router as metrics_router
from modules.api.routes.phi_demo_cases import router as phi_demo_router
from modules.api.routes_registry import router as registry_extract_router

# All API schemas (base + QA pipeline)
from modules.api.schemas import (
    # Base schemas
    CoderRequest,
    CoderResponse,
    HybridPipelineMetadata,
    KnowledgeMeta,
    QARunRequest,
    RegistryRequest,
    RegistryResponse,
    RenderRequest,
    RenderResponse,
    VerifyRequest,
    VerifyResponse,
    # QA pipeline schemas
    CodeEntry,
    CoderData,
    ModuleResult,
    ModuleStatus,
    QARunResponse,
    RegistryData,
    ReporterData,
)

# QA Pipeline service
from modules.api.services.qa_pipeline import (
    ModuleOutcome,
    QAPipelineResult,
    QAPipelineService,
)
from modules.api.dependencies import get_coding_service, get_qa_pipeline_service

from config.settings import CoderSettings
from modules.coder.schema import CodeDecision, CoderOutput
from modules.common.knowledge import knowledge_hash, knowledge_version
from modules.common.spans import Span
from modules.registry.engine import RegistryEngine

# New architecture imports
from modules.coder.application.coding_service import CodingService
from modules.api.coder_adapter import convert_coding_result_to_coder_output
from modules.coder.phi_gating import is_phi_review_required

from modules.reporting import MissingFieldIssue, ProcedureBundle
from modules.reporting.engine import (
    ReporterEngine,
    _load_procedure_order,
    apply_bundle_patch,
    apply_patch_result,
    build_procedure_bundle_from_extraction,
    default_schema_registry,
    default_template_registry,
)
from modules.reporting.inference import InferenceEngine
from modules.reporting.validation import ValidationEngine


# ============================================================================
# Application Lifespan Context Manager
# ============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan with resource management.

    This replaces the deprecated @app.on_event("startup") pattern.

    Startup:
    - Preloads heavy NLP models to avoid cold-start latency
    - Gracefully handles warmup failures (app still starts)

    Shutdown:
    - Placeholder for cleanup if needed in the future

    Environment variables:
    - PROCSUITE_SKIP_WARMUP: Set to "1", "true", or "yes" to skip warmup entirely
    - RAILWAY_ENVIRONMENT: If set, skips warmup (Railway caches models separately)
    """
    # Import here to avoid circular import at module load time
    from modules.infra.nlp_warmup import (
        should_skip_warmup as _should_skip_warmup,
        warm_heavy_resources as _warm_heavy_resources_fn,
    )

    # Startup phase
    if _should_skip_warmup():
        logging.getLogger(__name__).info(
            "Skipping heavy NLP warmup (disabled via environment)"
        )
    else:
        try:
            await _warm_heavy_resources_fn()
        except Exception as exc:
            logging.getLogger(__name__).error(
                "Heavy NLP warmup failed - starting API without NLP features. "
                "Some endpoints may return errors or degraded results. Error: %s",
                exc,
                exc_info=True,
            )

    # Optional: pull registry model bundle from S3 (does not block startup on failure).
    try:
        from modules.registry.model_bootstrap import ensure_registry_model_bundle

        ensure_registry_model_bundle()
    except Exception as exc:
        logging.getLogger(__name__).warning(
            "Registry model bundle bootstrap skipped/failed: %s", exc
        )

    yield  # Application runs

    # Shutdown phase (cleanup if needed)
    # Currently no cleanup required


app = FastAPI(
    title="Procedure Suite API",
    version="0.3.0",
    lifespan=lifespan,
)

# Include ML Advisor router
app.include_router(ml_advisor_router, prefix="/api/v1", tags=["ML Advisor"])
# Include PHI router
app.include_router(phi_router)
# Include procedure codes router
app.include_router(procedure_codes_router, prefix="/api/v1", tags=["procedure-codes"])
# Metrics router
app.include_router(metrics_router, tags=["metrics"])
# PHI demo cases router (non-PHI metadata)
app.include_router(phi_demo_router)
# Registry extraction router (hybrid-first pipeline)
app.include_router(registry_extract_router, tags=["registry"])

# Skip static file mounting when DISABLE_STATIC_FILES is set (useful for testing)
if os.getenv("DISABLE_STATIC_FILES", "").lower() not in ("true", "1", "yes"):
    # Use absolute path to static directory relative to this file
    static_dir = Path(__file__).parent / "static"
    app.mount("/ui", StaticFiles(directory=str(static_dir), html=True), name="ui")

# Configure logging
_logger = logging.getLogger(__name__)


# ============================================================================
# Heavy NLP model preloading (delegated to modules.infra.nlp_warmup)
# ============================================================================
from modules.infra.nlp_warmup import (
    should_skip_warmup,
    warm_heavy_resources as _warm_heavy_resources,
    is_nlp_warmed,
    get_spacy_model,
    get_sectionizer,
)


# NOTE: The lifespan context manager is defined above app creation.
# See lifespan() function for startup/shutdown logic.


class LocalityInfo(BaseModel):
    code: str
    name: str


@lru_cache(maxsize=1)
def _load_gpci_data() -> dict[str, str]:
    """Load GPCI locality data from CSV file.

    Returns a dict mapping locality codes to locality names.
    """
    import csv
    from pathlib import Path

    gpci_file = Path("data/RVU_files/gpci_2025.csv")
    if not gpci_file.exists():
        gpci_file = Path("proc_autocode/rvu/data/gpci_2025.csv")

    localities: dict[str, str] = {}
    if gpci_file.exists():
        try:
            with gpci_file.open() as f:
                reader = csv.DictReader(f)
                for row in reader:
                    code = row.get("mac_locality", row.get("locality_code", ""))
                    name = row.get("locality_name", "")
                    if code and name:
                        localities[code] = name
        except Exception as e:
            _logger.warning(f"Failed to load GPCI data: {e}")

    # Add default national locality if not present
    if "00" not in localities:
        localities["00"] = "National (Default)"

    return localities


@app.get("/")
async def root(request: Request) -> Any:
    """Root endpoint with API information or redirect to UI."""
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        return RedirectResponse(url="/ui/")
        
    return {
        "name": "Procedure Suite API",
        "version": "0.2.0",
        "endpoints": {
            "ui": "/ui/",
            "health": "/health",
            "knowledge": "/knowledge",
            "docs": "/docs",
            "redoc": "/redoc",
            "coder": "/v1/coder/run",
            "localities": "/v1/coder/localities",
            "registry": "/v1/registry/run",
            "report_verify": "/report/verify",
            "report_render": "/report/render",
            "qa_run": "/qa/run",
            "ml_advisor": {
                "health": "/api/v1/ml-advisor/health",
                "status": "/api/v1/ml-advisor/status",
                "code": "/api/v1/ml-advisor/code",
                "code_with_advisor": "/api/v1/ml-advisor/code_with_advisor",
                "suggest": "/api/v1/ml-advisor/suggest",
                "traces": "/api/v1/ml-advisor/traces",
                "metrics": "/api/v1/ml-advisor/metrics",
            },
            "registry_extract": "/api/registry/extract",
        },
        "note": "Coder uses CodingService (hexagonal architecture) with smart hybrid policy. ML Advisor endpoints available at /api/v1/ml-advisor/*",
    }


@app.get("/health")
async def health() -> dict[str, bool]:
    return {"ok": True}


@app.get("/health/nlp")
async def nlp_health() -> JSONResponse:
    """Check NLP model readiness.

    Returns 200 OK if NLP models are loaded and ready.
    Returns 503 Service Unavailable if NLP features are degraded.

    This endpoint can be used by load balancers to route requests
    to instances with fully warmed NLP models.
    """
    if is_nlp_warmed():
        return JSONResponse(
            status_code=200,
            content={"status": "ok", "nlp_ready": True},
        )
    return JSONResponse(
        status_code=503,
        content={"status": "degraded", "nlp_ready": False},
    )


@app.get("/knowledge", response_model=KnowledgeMeta)
async def knowledge() -> KnowledgeMeta:
    return KnowledgeMeta(version=knowledge_version() or "unknown", sha256=knowledge_hash() or "")


@app.get("/v1/coder/localities", response_model=List[LocalityInfo])
async def coder_localities() -> List[LocalityInfo]:
    """List available geographic localities for RVU calculation."""
    gpci_data = _load_gpci_data()
    localities = [
        LocalityInfo(code=code, name=name)
        for code, name in gpci_data.items()
    ]
    localities.sort(key=lambda x: x.name)
    return localities


@app.post("/v1/coder/run", response_model=CoderResponse)
async def coder_run(
    req: CoderRequest,
    mode: str | None = None,
    coding_service: CodingService = Depends(get_coding_service),
) -> CoderResponse:
    """Legacy raw-text coder shim (non-PHI). Use PHI workflow + /api/v1/procedures/{id}/codes/suggest."""
    require_review = is_phi_review_required()
    procedure_id = str(uuid.uuid4())
    report_text = req.note

    # If PHI review is required, reject direct raw text coding
    if require_review:
        raise HTTPException(
            status_code=400,
            detail="Direct coding on raw text is disabled; submit via /v1/phi and review before coding.",
        )

    # Check if ML-first hybrid pipeline is requested
    if req.use_ml_first:
        return await _run_ml_first_pipeline(report_text, req.locality, coding_service)

    # Determine if LLM should be used based on mode
    use_llm = True
    if mode == "rules_only" or req.mode == "rules_only":
        use_llm = False

    # Run the coding pipeline
    result = coding_service.generate_result(
        procedure_id=procedure_id,
        report_text=report_text,
        use_llm=use_llm,
        procedure_type=None,  # Auto-detect
    )

    # Convert to legacy CoderOutput format for backward compatibility
    output = convert_coding_result_to_coder_output(
        result=result,
        kb_repo=coding_service.kb_repo,
        locality=req.locality,
    )

    return output


async def _run_ml_first_pipeline(
    report_text: str,
    locality: str,
    coding_service: CodingService,
) -> CoderResponse:
    """
    Run the ML-first hybrid pipeline (SmartHybridOrchestrator).

    Uses ternary classification (HIGH_CONF/GRAY_ZONE/LOW_CONF) to decide
    whether to use ML+Rules fast path or LLM fallback.

    Args:
        report_text: The procedure note text
        locality: Geographic locality for RVU calculations
        coding_service: CodingService for KB access and RVU calculation

    Returns:
        CoderResponse with codes and hybrid pipeline metadata
    """
    from modules.coder.application.smart_hybrid_policy import build_hybrid_orchestrator

    # Build orchestrator with default components
    orchestrator = build_hybrid_orchestrator()

    # Run the hybrid pipeline
    result = orchestrator.get_codes(report_text)

    # Build code decisions from orchestrator result
    from modules.coder.schema import CodeDecision

    code_decisions = []
    for cpt in result.codes:
        proc_info = coding_service.kb_repo.get_procedure_info(cpt)
        desc = proc_info.description if proc_info else ""
        code_decisions.append(
            CodeDecision(
                cpt=cpt,
                description=desc,
                confidence=1.0,  # Hybrid pipeline doesn't return per-code confidence
                modifiers=[],
                rationale=f"Source: {result.source}",
            )
        )

    # Calculate RVU/financials if we have codes
    financials = None
    if code_decisions:
        from modules.coder.schema import FinancialSummary, PerCodeBilling

        per_code_billing: list[PerCodeBilling] = []
        total_work_rvu = 0.0
        total_facility_payment = 0.0
        conversion_factor = CoderSettings().cms_conversion_factor

        for cd in code_decisions:
            proc_info = coding_service.kb_repo.get_procedure_info(cd.cpt)
            if proc_info:
                work_rvu = proc_info.work_rvu
                total_rvu = proc_info.total_facility_rvu
                payment = total_rvu * conversion_factor

                total_work_rvu += work_rvu
                total_facility_payment += payment

                per_code_billing.append(PerCodeBilling(
                    cpt_code=cd.cpt,
                    description=cd.description,
                    modifiers=cd.modifiers,
                    work_rvu=work_rvu,
                    total_facility_rvu=total_rvu,
                    facility_payment=payment,
                    allowed_facility_rvu=total_rvu,
                    allowed_facility_payment=payment,
                ))

        if per_code_billing:
            financials = FinancialSummary(
                conversion_factor=conversion_factor,
                locality=locality,
                per_code=per_code_billing,
                total_work_rvu=total_work_rvu,
                total_facility_payment=total_facility_payment,
                total_nonfacility_payment=0.0,
            )

    # Build hybrid pipeline metadata
    hybrid_metadata = HybridPipelineMetadata(
        difficulty=result.difficulty.value,  # Use top-level difficulty attribute
        source=result.source,
        llm_used=result.metadata.get("llm_called", False),
        ml_candidates=result.metadata.get("ml_candidates", []),
        fallback_reason=result.metadata.get("reason_for_fallback"),
        rules_error=result.metadata.get("rules_error"),
    )

    # Build response
    from modules.coder.schema import CoderOutput
    return CoderOutput(
        codes=code_decisions,
        financials=financials,
        warnings=[],
        explanation=None,
        hybrid_metadata=hybrid_metadata.model_dump(),
    )


@app.post("/v1/registry/run", response_model=RegistryResponse)
async def registry_run(req: RegistryRequest) -> RegistryResponse:
    eng = RegistryEngine()
    # For interactive/demo usage, best-effort extraction should return 200 whenever possible.
    # RegistryEngine.run now attempts internal pruning on validation issues; if something still
    # raises, fall back to an empty record rather than failing the request.
    try:
        result = eng.run(req.note, explain=req.explain)
    except Exception as exc:
        _logger.warning("registry_run failed; returning empty record", exc_info=True)
        record = RegistryResponse()
        record.evidence = {}
        return record
    if isinstance(result, tuple):
        record, evidence = result
    else:
        record, evidence = result, result.evidence

    payload = record.model_dump()
    payload["evidence"] = _serialize_evidence(evidence)
    return RegistryResponse(**payload)


def _verify_bundle(bundle) -> tuple[ProcedureBundle, list[MissingFieldIssue], list[str], list[str], list[str]]:
    templates = default_template_registry()
    schemas = default_schema_registry()
    inference = InferenceEngine()
    inference_result = inference.infer_bundle(bundle)
    bundle = apply_patch_result(bundle, inference_result)
    validator = ValidationEngine(templates, schemas)
    issues = validator.list_missing_critical_fields(bundle)
    warnings = validator.apply_warn_if_rules(bundle)
    suggestions = validator.list_suggestions(bundle)
    return bundle, issues, warnings, suggestions, inference_result.notes


@app.post("/report/verify", response_model=VerifyResponse)
async def report_verify(req: VerifyRequest) -> VerifyResponse:
    bundle = build_procedure_bundle_from_extraction(req.extraction)
    bundle, issues, warnings, suggestions, notes = _verify_bundle(bundle)
    return VerifyResponse(bundle=bundle, issues=issues, warnings=warnings, suggestions=suggestions, inference_notes=notes)


@app.post("/report/render", response_model=RenderResponse)
async def report_render(req: RenderRequest) -> RenderResponse:
    templates = default_template_registry()
    schemas = default_schema_registry()
    bundle = req.bundle
    if req.patch:
        bundle = apply_bundle_patch(bundle, req.patch)
    inference = InferenceEngine()
    inference_result = inference.infer_bundle(bundle)
    bundle = apply_patch_result(bundle, inference_result)
    validator = ValidationEngine(templates, schemas)
    issues = validator.list_missing_critical_fields(bundle)
    warnings = validator.apply_warn_if_rules(bundle)
    suggestions = validator.list_suggestions(bundle)

    engine = ReporterEngine(
        templates,
        schemas,
        procedure_order=_load_procedure_order(),
    )
    structured = engine.compose_report_with_metadata(
        bundle,
        strict=req.strict,
        embed_metadata=req.embed_metadata,
        validation_issues=issues,
        warnings=warnings,
    )
    markdown = structured.text
    return RenderResponse(
        bundle=bundle,
        markdown=markdown,
        issues=issues,
        warnings=warnings,
        inference_notes=inference_result.notes,
        suggestions=suggestions,
    )


def _serialize_evidence(evidence: dict[str, list[Span]] | None) -> dict[str, list[dict[str, Any]]]:
    serialized: dict[str, list[dict[str, Any]]] = {}
    for field, spans in (evidence or {}).items():
        serialized[field] = [_span_to_dict(span) for span in spans]
    return serialized


def _span_to_dict(span: Span) -> dict[str, Any]:
    data = asdict(span)
    return data


# --- QA Sandbox Endpoint ---

def _get_git_info() -> tuple[str | None, str | None]:
    """Extract git branch and commit SHA for version tracking."""
    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        return branch, commit
    except Exception:
        return None, None


# Configuration for QA sandbox
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"
REPORTER_VERSION = os.getenv("REPORTER_VERSION", "v0.2.0")
CODER_VERSION = os.getenv("CODER_VERSION", "v0.2.0")


def _module_status_from_outcome(outcome: ModuleOutcome) -> ModuleStatus:
    """Convert ModuleOutcome to ModuleStatus enum."""
    if outcome.skipped:
        return ModuleStatus.SKIPPED
    if outcome.ok:
        return ModuleStatus.SUCCESS
    return ModuleStatus.ERROR


def _qapipeline_result_to_response(
    result: QAPipelineResult,
    reporter_version: str,
    coder_version: str,
    repo_branch: str | None,
    repo_commit_sha: str | None,
) -> QARunResponse:
    """Convert QAPipelineResult to QARunResponse.

    Handles status aggregation and data transformation for each module.
    """
    # Build registry ModuleResult
    registry_result: ModuleResult[RegistryData] | None = None
    if not result.registry.skipped:
        registry_data = None
        if result.registry.ok and result.registry.data:
            registry_data = RegistryData(
                record=result.registry.data.get("record", {}),
                evidence=result.registry.data.get("evidence", {}),
            )
        registry_result = ModuleResult[RegistryData](
            status=_module_status_from_outcome(result.registry),
            data=registry_data,
            error_message=result.registry.error_message,
            error_code=result.registry.error_code,
        )

    # Build reporter ModuleResult
    reporter_result: ModuleResult[ReporterData] | None = None
    if not result.reporter.skipped:
        reporter_data = None
        if result.reporter.ok and result.reporter.data:
            data = result.reporter.data
            reporter_data = ReporterData(
                markdown=data.get("markdown"),
                bundle=data.get("bundle"),
                issues=data.get("issues", []),
                warnings=data.get("warnings", []),
                procedure_core=data.get("procedure_core"),
                indication=data.get("indication"),
                postop=data.get("postop"),
                fallback_used=data.get("fallback_used", False),
            )
        reporter_result = ModuleResult[ReporterData](
            status=_module_status_from_outcome(result.reporter),
            data=reporter_data,
            error_message=result.reporter.error_message,
            error_code=result.reporter.error_code,
        )

    # Build coder ModuleResult
    coder_result: ModuleResult[CoderData] | None = None
    if not result.coder.skipped:
        coder_data = None
        if result.coder.ok and result.coder.data:
            data = result.coder.data
            codes = [
                CodeEntry(
                    cpt=c.get("cpt", ""),
                    description=c.get("description"),
                    confidence=c.get("confidence"),
                    source=c.get("source"),
                    hybrid_decision=c.get("hybrid_decision"),
                    review_flag=c.get("review_flag", False),
                )
                for c in data.get("codes", [])
            ]
            coder_data = CoderData(
                codes=codes,
                total_work_rvu=data.get("total_work_rvu"),
                estimated_payment=data.get("estimated_payment"),
                bundled_codes=data.get("bundled_codes", []),
                kb_version=data.get("kb_version"),
                policy_version=data.get("policy_version"),
                model_version=data.get("model_version"),
                processing_time_ms=data.get("processing_time_ms"),
            )
        coder_result = ModuleResult[CoderData](
            status=_module_status_from_outcome(result.coder),
            data=coder_data,
            error_message=result.coder.error_message,
            error_code=result.coder.error_code,
        )

    # Compute overall status
    active_results = []
    if registry_result:
        active_results.append(registry_result)
    if reporter_result:
        active_results.append(reporter_result)
    if coder_result:
        active_results.append(coder_result)

    if not active_results:
        overall_status = "completed"
    else:
        successes = sum(1 for r in active_results if r.status == ModuleStatus.SUCCESS)
        failures = sum(1 for r in active_results if r.status == ModuleStatus.ERROR)

        if failures == 0:
            overall_status = "completed"
        elif successes == 0:
            overall_status = "failed"
        else:
            overall_status = "partial_success"

    from modules.registry.model_runtime import get_registry_model_provenance

    model_provenance = get_registry_model_provenance()

    return QARunResponse(
        overall_status=overall_status,
        registry=registry_result,
        reporter=reporter_result,
        coder=coder_result,
        registry_output=(result.registry.data if result.registry.ok else None),
        reporter_output=(result.reporter.data if result.reporter.ok else None),
        coder_output=(result.coder.data if result.coder.ok else None),
        model_backend=model_provenance.backend,
        model_version=model_provenance.version,
        reporter_version=reporter_version,
        coder_version=coder_version,
        repo_branch=repo_branch,
        repo_commit_sha=repo_commit_sha,
    )


@app.post("/qa/run", response_model=QARunResponse)
async def qa_run(
    payload: QARunRequest,
    qa_service: QAPipelineService = Depends(get_qa_pipeline_service),
) -> QARunResponse:
    """
    QA sandbox endpoint: runs reporter, coder, and/or registry on input text.

    This endpoint does NOT persist data - that is handled by the Next.js layer.
    Returns structured outputs with per-module status + version metadata.

    The pipeline runs synchronously in a thread pool to avoid blocking the
    event loop during heavy NLP/ML processing.

    Returns HTTP 200 for all cases (success, partial failure, full failure).
    Check `overall_status` and individual module `status` fields for results.
    """
    branch, commit = _get_git_info()

    # Run pipeline in thread pool to avoid blocking event loop
    result = await run_in_threadpool(
        qa_service.run_pipeline,
        text=payload.note_text,
        modules=payload.modules_run,
        procedure_type=payload.procedure_type,
    )

    # Convert to response format
    return _qapipeline_result_to_response(
        result=result,
        reporter_version=REPORTER_VERSION,
        coder_version=CODER_VERSION,
        repo_branch=branch,
        repo_commit_sha=commit,
    )


__all__ = ["app"]
```

---
### `modules/coder/application/coding_service.py`
```
"""Coding Service - orchestrates the 8-step coding pipeline.

This service coordinates rule-based coding, LLM advisor suggestions,
smart hybrid merge, evidence validation, NCCI/MER compliance, and
produces CodeSuggestion objects for review.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

import os

from config.settings import CoderSettings
from modules.domain.knowledge_base.repository import KnowledgeBaseRepository
from modules.domain.coding_rules import apply_ncci_edits, apply_mer_rules
from modules.domain.coding_rules.rule_engine import RuleEngine
from modules.coder.adapters.nlp.keyword_mapping_loader import KeywordMappingRepository
from modules.coder.adapters.nlp.simple_negation_detector import SimpleNegationDetector
from modules.coder.adapters.llm.gemini_advisor import LLMAdvisorPort
from modules.coder.adapters.ml_ranker import MLRankerPort, MLRankingResult
from modules.coder.application.smart_hybrid_policy import (
    HybridPolicy,
    HybridCandidate,
    HybridDecision,
    RuleResult,
    AdvisorResult,
)
from modules.coder.application.procedure_type_detector import detect_procedure_type
from modules.coder.domain_rules import (
    apply_addon_family_rules,
    apply_all_ncci_bundles,
)
from modules.coder.sectionizer import (
    accordion_truncate,
    sectionizer_enabled,
    max_llm_input_tokens,
)
from modules.phi.ports import PHIScrubberPort
from proc_schemas.coding import CodeSuggestion, CodingResult
from proc_schemas.reasoning import ReasoningFields
from observability.timing import timed
from observability.logging_config import get_logger

logger = get_logger("coding_service")


class CodingService:
    """Orchestrates the 8-step coding pipeline.

    Pipeline Steps:
    1. Rule engine → rule_codes + rule_confidence
    2. (Optional) ML ranker → ml_confidence
    3. LLM advisor → advisor_codes + advisor_confidence
    4. Smart hybrid merge → merged_codes with HybridDecision flags
    5. Evidence validation → verify each code in text
    6. Non-negotiable rules (NCCI/MER) → remove invalid combinations
    7. Confidence aggregation → compute final_confidence, set review_flag
    8. Build CodeSuggestion[] → return for review
    """

    VERSION = "coding_service_v1"

    def __init__(
        self,
        kb_repo: KnowledgeBaseRepository,
        keyword_repo: KeywordMappingRepository,
        negation_detector: SimpleNegationDetector,
        rule_engine: RuleEngine,
        llm_advisor: Optional[LLMAdvisorPort],
        config: CoderSettings,
        phi_scrubber: Optional[PHIScrubberPort] = None,
        ml_ranker: Optional[MLRankerPort] = None,
    ):
        self.kb_repo = kb_repo
        self.keyword_repo = keyword_repo
        self.negation_detector = negation_detector
        self.rule_engine = rule_engine
        self.llm_advisor = llm_advisor
        self.config = config
        self.phi_scrubber = phi_scrubber
        self.ml_ranker = ml_ranker

        # Initialize hybrid policy
        self.hybrid_policy = HybridPolicy(
            kb_repo=kb_repo,
            keyword_repo=keyword_repo,
            negation_detector=negation_detector,
            config=config,
        )

        # Log PHI scrubber status
        if llm_advisor and not phi_scrubber:
            logger.warning(
                "LLM advisor enabled but no PHI scrubber configured. "
                "Raw text may be sent to external LLM service."
            )

        # Log ML ranker status
        if ml_ranker and ml_ranker.available:
            logger.info("ML ranker enabled: %s", ml_ranker.version)
        elif ml_ranker:
            logger.warning("ML ranker provided but not available (models not loaded)")

    def generate_suggestions(
        self,
        procedure_id: str,
        report_text: str,
        use_llm: bool = True,
    ) -> tuple[list[CodeSuggestion], float]:
        """Generate code suggestions for a procedure note.

        Args:
            procedure_id: Unique identifier for the procedure.
            report_text: The procedure note text.
            use_llm: Whether to use the LLM advisor.

        Returns:
            Tuple of (List of CodeSuggestion objects, LLM latency in ms).
        """
        llm_latency_ms = 0.0

        # Log input text size for debugging truncation issues
        text_length = len(report_text)
        logger.info(
            "Starting coding pipeline",
            extra={
                "procedure_id": procedure_id,
                "text_length_chars": text_length,
                "use_llm": use_llm,
            },
        )
        if text_length > 20000:
            logger.warning(
                f"Large procedure note detected ({text_length} chars). "
                "Potential for truncation in LLM processing.",
                extra={"procedure_id": procedure_id, "text_length_chars": text_length},
            )

        with timed("coding_service.generate_suggestions") as timing:
            # Step 1: Rule-based coding
            rule_result = self._run_rule_engine(report_text)

            # Step 2: Optional ML ranking
            ml_result = self._run_ml_ranker(report_text, rule_result)

            # Step 3: LLM advisor (track latency separately)
            advisor_result, llm_latency_ms = self._run_llm_advisor(report_text, use_llm)

            # Step 4: Smart hybrid merge
            candidates = self._run_hybrid_merge(rule_result, advisor_result, report_text)

            # Step 5: Evidence validation is done in hybrid merge

            # Step 6: NCCI/MER compliance
            candidates, ncci_warnings, mer_warnings = self._apply_compliance_rules(candidates)

            # Step 7-8: Build suggestions
            suggestions = self._build_suggestions(
                candidates=candidates,
                procedure_id=procedure_id,
                ncci_warnings=ncci_warnings,
                mer_warnings=mer_warnings,
            )

        logger.info(
            "Coding complete",
            extra={
                "procedure_id": procedure_id,
                "num_suggestions": len(suggestions),
                "processing_time_ms": timing.elapsed_ms,
                "llm_latency_ms": llm_latency_ms,
            },
        )

        return suggestions, llm_latency_ms

    def generate_result(
        self,
        procedure_id: str,
        report_text: str,
        use_llm: bool = True,
        procedure_type: str | None = None,
    ) -> CodingResult:
        """Generate a complete coding result with metadata.

        Args:
            procedure_id: Unique identifier for the procedure.
            report_text: The procedure note text.
            use_llm: Whether to use the LLM advisor.
            procedure_type: Classification of the procedure (e.g., bronch_diagnostic,
                          bronch_ebus, pleural, blvr). Used for metrics segmentation.
                          If None or "unknown", auto-detection is attempted.

        Returns:
            CodingResult with suggestions and metadata.
        """
        with timed("coding_service.generate_result") as timing:
            suggestions, llm_latency_ms = self.generate_suggestions(
                procedure_id, report_text, use_llm
            )

        # Auto-detect procedure type if not provided
        if not procedure_type or procedure_type == "unknown":
            suggestion_codes = [s.code for s in suggestions]
            detected_type = detect_procedure_type(
                report_text=report_text,
                codes=suggestion_codes,
            )
            procedure_type = detected_type
            logger.debug(
                "Auto-detected procedure type",
                extra={
                    "procedure_id": procedure_id,
                    "detected_type": detected_type,
                    "codes_used": suggestion_codes[:5],  # Log first 5 codes
                },
            )

        return CodingResult(
            procedure_id=procedure_id,
            suggestions=suggestions,
            final_codes=[],  # Populated after review
            procedure_type=procedure_type,
            warnings=[],
            ncci_notes=[],
            mer_notes=[],
            kb_version=self.kb_repo.version,
            policy_version=self.hybrid_policy.version,
            model_version=self.llm_advisor.version if self.llm_advisor else "",
            processing_time_ms=timing.elapsed_ms,
            llm_latency_ms=llm_latency_ms,
        )

    def _run_rule_engine(self, report_text: str) -> RuleResult:
        """Step 1: Run the rule-based coding engine."""
        with timed("coding_service.rule_engine"):
            result = self.rule_engine.generate_candidates(report_text)

        return RuleResult(
            codes=result.codes,
            confidence=result.confidence,
        )

    def _run_ml_ranker(
        self,
        report_text: str,
        rule_result: RuleResult,
    ) -> Optional[MLRankingResult]:
        """Step 2: Run the ML ranker to get confidence scores.

        If an ML ranker is configured, this augments rule-based codes with
        ML-derived confidence scores. High-confidence ML predictions may
        also be added if not already present from rules.

        Args:
            report_text: The procedure note text.
            rule_result: Result from the rule engine (Step 1).

        Returns:
            MLRankingResult with predictions and confidence scores,
            or None if ML ranker is not available.
        """
        if not self.ml_ranker or not self.ml_ranker.available:
            return None

        with timed("coding_service.ml_ranker"):
            ml_result = self.ml_ranker.rank_codes(
                note_text=report_text,
                candidate_codes=None,  # Score all known codes
            )

        # Log ML ranking results
        logger.info(
            "ML ranking complete",
            extra={
                "difficulty": ml_result.difficulty,
                "high_conf_count": len(ml_result.high_conf_codes),
                "gray_zone_count": len(ml_result.gray_zone_codes),
                "total_predictions": len(ml_result.predictions),
            },
        )

        # Augment rule result confidence with ML scores
        for code in rule_result.codes:
            if code in ml_result.confidence_map:
                ml_conf = ml_result.confidence_map[code]
                rule_conf = rule_result.confidence.get(code, 0.0)
                # Boost confidence if ML agrees, average otherwise
                if ml_conf > 0.5:
                    rule_result.confidence[code] = max(rule_conf, ml_conf * 0.9)
                logger.debug(
                    "ML augmented rule confidence",
                    extra={
                        "code": code,
                        "rule_conf": rule_conf,
                        "ml_conf": ml_conf,
                        "final_conf": rule_result.confidence[code],
                    },
                )

        return ml_result

    def _run_llm_advisor(self, report_text: str, use_llm: bool) -> tuple[AdvisorResult, float]:
        """Step 3: Run the LLM advisor.

        PHI Guardrail: If a PHI scrubber is configured, the text is scrubbed
        before being sent to the external LLM service. This prevents PHI
        from being transmitted to third-party APIs.

        Returns:
            Tuple of (AdvisorResult, latency_ms)
        """
        if not use_llm or not self.llm_advisor:
            return AdvisorResult(codes=[], confidence={}), 0.0

        # PHI Guardrail: Scrub text before sending to LLM
        text_for_llm = report_text
        if self.phi_scrubber:
            try:
                scrub_result = self.phi_scrubber.scrub(report_text)
                text_for_llm = scrub_result.scrubbed_text
                logger.debug(
                    "PHI scrubbed before LLM call",
                    extra={"entities_found": len(scrub_result.entities)},
                )
            except Exception as e:
                logger.error(f"PHI scrubbing failed: {e}", exc_info=True)
                # Fail safely: don't send potentially unscrubbed text to LLM
                logger.warning("Skipping LLM advisor due to scrubbing failure")
                return AdvisorResult(codes=[], confidence={}), 0.0

        text_for_llm = self._prepare_llm_context(text_for_llm)

        with timed("coding_service.llm_advisor") as timing:
            suggestions = self.llm_advisor.suggest_codes(text_for_llm)

        return AdvisorResult(
            codes=[s.code for s in suggestions],
            confidence={s.code: s.confidence for s in suggestions},
        ), timing.elapsed_ms

    def _run_hybrid_merge(
        self,
        rule_result: RuleResult,
        advisor_result: AdvisorResult,
        report_text: str,
    ) -> list:
        """Step 4: Run the smart hybrid merge."""
        with timed("coding_service.hybrid_merge"):
            candidates = self.hybrid_policy.merge(
                rule_result=rule_result,
                advisor_result=advisor_result,
                report_text=report_text,
            )

        return candidates

    def _apply_compliance_rules(
        self,
        candidates: list[HybridCandidate],
    ) -> tuple[list[HybridCandidate], list[str], list[str]]:
        """Step 6: Apply domain rules and NCCI/MER compliance rules.

        This applies rules in the following order:
        1. Add-on family consistency (e.g., 31636 -> +31637 when 31631 present)
        2. EBUS-Aspiration bundling (31645/31646 bundled into 31652/31653)
        3. NCCI edits from knowledge base
        4. MER (Multiple Endoscopy Rule) reductions
        """
        # Get accepted codes for compliance checking
        accepted_codes = self.hybrid_policy.get_accepted_codes(candidates)

        # Step 6a: Apply add-on family rules (hierarchy fix)
        # This ensures codes like 31636 become +31637 when 31631 is present
        family_result = apply_addon_family_rules(accepted_codes)
        for original, converted, reason in family_result.conversions:
            # Update the candidate code
            for candidate in candidates:
                if candidate.code == original:
                    candidate.code = converted
                    candidate.flags.append(f"FAMILY_CONVERSION: {reason}")
                    logger.info(
                        "Applied family conversion",
                        extra={"original": original, "converted": converted, "reason": reason},
                    )
                    break  # Only convert first occurrence per conversion

        # Refresh accepted codes after family conversions
        accepted_codes = self.hybrid_policy.get_accepted_codes(candidates)

        # Step 6b: Apply all NCCI bundling rules
        # This removes:
        # - Aspiration codes (31645/31646) when EBUS codes (31652/31653) are present
        # - Thoracentesis codes (32554/32555) when IPC placement (32550) is present
        # - Tumor excision (31640) when destruction (31641) is present
        bundle_result = apply_all_ncci_bundles(accepted_codes)
        bundled_codes = set(bundle_result.removed_codes)

        ncci_warnings: list[str] = []
        for primary, removed, reason in bundle_result.bundle_reasons:
            ncci_warnings.append(f"NCCI_BUNDLE: {removed} bundled into {primary} - {reason}")
            logger.info(
                "Applied NCCI bundle",
                extra={"primary": primary, "removed": removed, "reason": reason},
            )

        # Mark bundled candidates as rejected
        for candidate in candidates:
            if candidate.code in bundled_codes:
                candidate.decision = HybridDecision.REJECTED_HYBRID
                candidate.flags.append(f"NCCI_BUNDLED: Code bundled into primary procedure")

        # Refresh accepted codes after bundling
        accepted_codes = self.hybrid_policy.get_accepted_codes(candidates)

        # Step 6c: Apply NCCI edits from knowledge base
        ncci_result = apply_ncci_edits(accepted_codes, self.kb_repo)
        ncci_warnings.extend(ncci_result.warnings)

        # Step 6d: Apply MER rules
        mer_result = apply_mer_rules(ncci_result.kept_codes, self.kb_repo)
        mer_warnings = mer_result.warnings

        # Filter candidates based on compliance results
        final_codes = set(mer_result.kept_codes)
        filtered_candidates: list[HybridCandidate] = []

        for candidate in candidates:
            if candidate.code in final_codes:
                filtered_candidates.append(candidate)
            elif candidate.code in bundled_codes:
                # Already marked as rejected above
                filtered_candidates.append(candidate)
            elif candidate.code in ncci_result.removed_codes:
                # Update the candidate to show it was removed by NCCI
                candidate.decision = HybridDecision.REJECTED_HYBRID
                candidate.flags.append(f"NCCI_REMOVED: {ncci_warnings}")
                filtered_candidates.append(candidate)
            elif candidate.code in mer_result.removed_codes:
                # Update the candidate to show it was removed by MER
                candidate.decision = HybridDecision.REJECTED_HYBRID
                candidate.flags.append(f"MER_REMOVED: {mer_warnings}")
                filtered_candidates.append(candidate)
            else:
                filtered_candidates.append(candidate)

        return filtered_candidates, ncci_warnings, mer_warnings

    def _build_suggestions(
        self,
        candidates: list,
        procedure_id: str,
        ncci_warnings: list[str],
        mer_warnings: list[str],
    ) -> list[CodeSuggestion]:
        """Steps 7-8: Build CodeSuggestion objects."""
        suggestions = []

        for candidate in candidates:
            # Determine source
            if candidate.decision == HybridDecision.ACCEPTED_AGREEMENT:
                source = "hybrid"
            elif candidate.decision in (
                HybridDecision.ACCEPTED_HYBRID,
                HybridDecision.HUMAN_REVIEW_REQUIRED,
            ):
                source = "llm"
            elif candidate.decision in (
                HybridDecision.KEPT_RULE_PRIORITY,
                HybridDecision.DROPPED_LOW_CONFIDENCE,
            ):
                source = "rule"
            else:
                source = "hybrid"

            # Compute final confidence
            rule_conf = candidate.rule_confidence or 0.0
            llm_conf = candidate.llm_confidence or 0.0

            if candidate.decision == HybridDecision.ACCEPTED_AGREEMENT:
                # Agreement boosts confidence
                final_confidence = max(rule_conf, llm_conf) * 1.1
            elif candidate.decision == HybridDecision.ACCEPTED_HYBRID:
                final_confidence = llm_conf
            elif candidate.decision == HybridDecision.KEPT_RULE_PRIORITY:
                final_confidence = rule_conf
            else:
                final_confidence = max(rule_conf, llm_conf, 0.5)

            final_confidence = min(1.0, final_confidence)  # Cap at 1.0

            # Determine review flag
            if candidate.decision == HybridDecision.HUMAN_REVIEW_REQUIRED:
                review_flag = "required"
            elif candidate.decision in (
                HybridDecision.DROPPED_LOW_CONFIDENCE,
                HybridDecision.REJECTED_HYBRID,
            ):
                review_flag = "recommended"
            elif final_confidence < 0.8:
                review_flag = "recommended"
            else:
                review_flag = "optional"

            # Get procedure info for description
            proc_info = self.kb_repo.get_procedure_info(candidate.code)
            description = proc_info.description if proc_info else ""

            # Build reasoning
            reasoning = ReasoningFields(
                trigger_phrases=candidate.trigger_phrases,
                rule_paths=candidate.flags,
                confidence=final_confidence,
                kb_version=self.kb_repo.version,
                policy_version=self.hybrid_policy.version,
                model_version=self.llm_advisor.version if self.llm_advisor else "",
                keyword_map_version=self.keyword_repo.version,
                negation_detector_version=self.negation_detector.version,
                ncci_notes="; ".join(ncci_warnings) if ncci_warnings else "",
                mer_notes="; ".join(mer_warnings) if mer_warnings else "",
            )

            suggestion = CodeSuggestion(
                code=candidate.code,
                description=description,
                source=source,
                hybrid_decision=candidate.decision.value,
                rule_confidence=candidate.rule_confidence,
                llm_confidence=candidate.llm_confidence,
                final_confidence=final_confidence,
                reasoning=reasoning,
                review_flag=review_flag,
                trigger_phrases=candidate.trigger_phrases,
                evidence_verified=candidate.evidence_verified,
                suggestion_id=str(uuid.uuid4()),
                procedure_id=procedure_id,
            )

            suggestions.append(suggestion)

        return suggestions
    def _prepare_llm_context(self, scrubbed_text: str) -> str:
        if not scrubbed_text:
            return scrubbed_text
        if not sectionizer_enabled():
            return scrubbed_text
        tokens = max_llm_input_tokens()
        return accordion_truncate(scrubbed_text, tokens)
```

---
### `modules/registry/application/registry_service.py`
```
"""Registry Service for exporting procedure data to the IP Registry.

This application-layer service orchestrates:
- Building registry entries from final codes and procedure metadata
- Mapping CPT codes to registry boolean flags
- Validating entries against the registry schema
- Managing export state
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Any, Literal

from pydantic import BaseModel, ValidationError

from modules.common.exceptions import RegistryError
from modules.common.logger import get_logger
from modules.registry.adapters.schema_registry import (
    RegistrySchemaRegistry,
    get_schema_registry,
)
from modules.registry.application.cpt_registry_mapping import (
    aggregate_registry_fields,
    aggregate_registry_hints,
)
from modules.registry.application.registry_builder import (
    RegistryBuilderProtocol,
    get_builder,
)
from modules.registry.engine import RegistryEngine
from modules.registry.schema import RegistryRecord
from modules.registry.schema_granular import derive_procedures_from_granular

logger = get_logger("registry_service")
from proc_schemas.coding import FinalCode, CodingResult
from proc_schemas.registry.ip_v2 import (
    IPRegistryV2,
    PatientInfo as PatientInfoV2,
    ProcedureInfo as ProcedureInfoV2,
)
from proc_schemas.registry.ip_v3 import (
    IPRegistryV3,
    PatientInfo as PatientInfoV3,
    ProcedureInfo as ProcedureInfoV3,
)
from modules.coder.application.smart_hybrid_policy import (
    SmartHybridOrchestrator,
    HybridCoderResult,
)
from modules.ml_coder.registry_predictor import RegistryMLPredictor
from modules.registry.model_runtime import get_registry_runtime_dir, resolve_model_backend


@dataclass
class RegistryDraftResult:
    """Result from building a draft registry entry."""

    entry: IPRegistryV2 | IPRegistryV3
    completeness_score: float
    missing_fields: list[str]
    suggested_values: dict[str, Any]
    warnings: list[str]
    hints: dict[str, list[str]]  # Aggregated hints from CPT mappings


@dataclass
class RegistryExportResult:
    """Result from exporting a procedure to the registry."""

    entry: IPRegistryV2 | IPRegistryV3
    registry_id: str
    schema_version: str
    export_id: str
    export_timestamp: datetime
    status: Literal["success", "partial", "failed"]
    warnings: list[str] = field(default_factory=list)


@dataclass
class RegistryExtractionResult:
    """Result from hybrid-first registry field extraction.

    Combines:
    - CPT codes from SmartHybridOrchestrator
    - Registry fields mapped from CPT codes
    - Extracted fields from RegistryEngine
    - Validation results and manual review flags
    - ML audit results comparing CPT-derived flags with ML predictions

    Attributes:
        record: The extracted RegistryRecord.
        cpt_codes: CPT codes from the hybrid coder.
        coder_difficulty: Case difficulty (HIGH_CONF/GRAY_ZONE/LOW_CONF).
        coder_source: Where codes came from (ml_rules_fastpath/hybrid_llm_fallback).
        mapped_fields: Registry fields derived from CPT mapping.
        warnings: Non-blocking warnings about the extraction.
        needs_manual_review: Whether this case requires human review.
        validation_errors: List of validation errors found during reconciliation.
        audit_warnings: ML vs CPT discrepancy warnings requiring human review.
    """

    record: RegistryRecord
    cpt_codes: list[str]
    coder_difficulty: str
    coder_source: str
    mapped_fields: dict[str, Any]
    warnings: list[str] = field(default_factory=list)
    needs_manual_review: bool = False
    validation_errors: list[str] = field(default_factory=list)
    audit_warnings: list[str] = field(default_factory=list)


class RegistryService:
    """Application service for registry export operations.

    This service:
    - Builds registry entries from coding results and procedure metadata
    - Maps CPT codes to registry boolean flags using cpt_registry_mapping
    - Validates entries against Pydantic schemas
    - Produces structured export results with warnings
    """

    VERSION = "registry_service_v1"

    def __init__(
        self,
        schema_registry: RegistrySchemaRegistry | None = None,
        default_version: str = "v2",
        hybrid_orchestrator: SmartHybridOrchestrator | None = None,
        registry_engine: RegistryEngine | None = None,
    ):
        """Initialize RegistryService.

        Args:
            schema_registry: Registry for versioned schemas. Uses default if None.
            default_version: Default schema version to use if not specified.
            hybrid_orchestrator: Optional SmartHybridOrchestrator for ML-first coding.
            registry_engine: Optional RegistryEngine for field extraction. Lazy-init if None.
        """
        self.schema_registry = schema_registry or get_schema_registry()
        self.default_version = default_version
        self.hybrid_orchestrator = hybrid_orchestrator
        self._registry_engine = registry_engine
        self._registry_ml_predictor: Any | None = None
        self._ml_predictor_init_attempted: bool = False

    @property
    def registry_engine(self) -> RegistryEngine:
        """Lazy initialization of RegistryEngine."""
        if self._registry_engine is None:
            self._registry_engine = RegistryEngine()
        return self._registry_engine

    def _get_registry_ml_predictor(self) -> Any | None:
        """Get registry ML predictor with lazy initialization.

        Behavior:
        - If MODEL_BACKEND is set to "pytorch" or "onnx", prefer that backend and
          fall back to sklearn if unavailable.
        - Otherwise ("auto"), keep legacy behavior: try ONNX first (if available),
          then sklearn TF-IDF.

        Returns the predictor if available, or None if artifacts are missing.
        Logs once on initialization failure to avoid log spam.
        """
        if self._ml_predictor_init_attempted:
            return self._registry_ml_predictor

        self._ml_predictor_init_attempted = True

        backend = resolve_model_backend()
        runtime_dir = get_registry_runtime_dir()

        def _try_pytorch() -> Any | None:
            try:
                from modules.registry.inference_pytorch import TorchRegistryPredictor

                predictor = TorchRegistryPredictor(bundle_dir=runtime_dir)
                if predictor.available:
                    logger.info(
                        "Using TorchRegistryPredictor with %d labels",
                        len(getattr(predictor, "labels", [])),
                    )
                    return predictor
                logger.debug("Torch predictor initialized but not available")
            except ImportError as e:
                logger.debug("PyTorch/Transformers not available (%s)", e)
            except Exception as e:
                logger.debug("Torch predictor init failed (%s)", e)
            return None

        def _try_onnx() -> Any | None:
            try:
                from modules.registry.inference_onnx import ONNXRegistryPredictor

                # Prefer runtime bundle paths if present; otherwise keep defaults.
                model_path = (
                    runtime_dir / "registry_model_int8.onnx"
                    if (runtime_dir / "registry_model_int8.onnx").exists()
                    else None
                )
                tokenizer_path = (
                    runtime_dir / "tokenizer" if (runtime_dir / "tokenizer").exists() else None
                )
                thresholds_path = (
                    runtime_dir / "thresholds.json" if (runtime_dir / "thresholds.json").exists() else None
                )
                label_fields_path = (
                    runtime_dir / "registry_label_fields.json"
                    if (runtime_dir / "registry_label_fields.json").exists()
                    else None
                )

                predictor = ONNXRegistryPredictor(
                    model_path=model_path,
                    tokenizer_path=tokenizer_path,
                    thresholds_path=thresholds_path,
                    label_fields_path=label_fields_path,
                )
                if predictor.available:
                    logger.info(
                        "Using ONNXRegistryPredictor with %d labels",
                        len(getattr(predictor, "labels", [])),
                    )
                    return predictor
                logger.debug("ONNX model not available")
            except ImportError:
                logger.debug("ONNX runtime not available")
            except Exception as e:
                logger.debug("ONNX predictor init failed (%s)", e)
            return None

        if backend == "pytorch":
            predictor = _try_pytorch()
            if predictor is not None:
                self._registry_ml_predictor = predictor
                return self._registry_ml_predictor
        elif backend == "onnx":
            predictor = _try_onnx()
            if predictor is not None:
                self._registry_ml_predictor = predictor
                return self._registry_ml_predictor
        else:
            predictor = _try_onnx()
            if predictor is not None:
                self._registry_ml_predictor = predictor
                return self._registry_ml_predictor

        # Fall back to TF-IDF sklearn predictor
        try:
            self._registry_ml_predictor = RegistryMLPredictor()
            if not self._registry_ml_predictor.available:
                logger.warning(
                    "RegistryMLPredictor initialized but not available "
                    "(model artifacts missing). ML hybrid audit disabled."
                )
                self._registry_ml_predictor = None
            else:
                logger.info(
                    "Using RegistryMLPredictor (TF-IDF) with %d labels",
                    len(self._registry_ml_predictor.labels),
                )
        except Exception:
            logger.exception(
                "Failed to initialize RegistryMLPredictor; ML hybrid audit disabled."
            )
            self._registry_ml_predictor = None

        return self._registry_ml_predictor

    def build_draft_entry(
        self,
        procedure_id: str,
        final_codes: list[FinalCode],
        procedure_metadata: dict[str, Any] | None = None,
        version: str | None = None,
    ) -> RegistryDraftResult:
        """Build a draft registry entry from final codes and metadata.

        This method:
        1. Maps CPT codes to registry boolean flags
        2. Merges with provided procedure metadata
        3. Validates against the target schema
        4. Computes completeness score and missing fields

        Args:
            procedure_id: The procedure identifier
            final_codes: List of approved FinalCode objects
            procedure_metadata: Optional dict with patient/procedure info
            version: Schema version ("v2" or "v3"), defaults to default_version

        Returns:
            RegistryDraftResult with entry, completeness, and warnings
        """
        version = version or self.default_version
        metadata = procedure_metadata or {}
        warnings: list[str] = []
        missing_fields: list[str] = []

        # Extract CPT codes
        cpt_codes = [fc.code for fc in final_codes]

        # Get aggregated registry fields from CPT mappings
        registry_fields = aggregate_registry_fields(cpt_codes, version)
        hints = aggregate_registry_hints(cpt_codes)

        # Get the appropriate builder for this version
        builder = get_builder(version)

        # Build patient and procedure info using the builder
        patient_info = builder.build_patient(metadata, missing_fields)
        procedure_info = builder.build_procedure(procedure_id, metadata, missing_fields)

        # Build the registry entry using the builder
        entry = builder.build_entry(
            procedure_id=procedure_id,
            patient=patient_info,
            procedure=procedure_info,
            registry_fields=registry_fields,
            metadata=metadata,
        )

        # Validate and generate warnings
        validation_warnings = self._validate_entry(entry, version)
        warnings.extend(validation_warnings)

        # Compute completeness score
        completeness_score = self._compute_completeness(entry, missing_fields)

        # Suggest values based on hints
        suggested_values = self._generate_suggestions(hints, entry)

        return RegistryDraftResult(
            entry=entry,
            completeness_score=completeness_score,
            missing_fields=missing_fields,
            suggested_values=suggested_values,
            warnings=warnings,
            hints=hints,
        )

    def export_procedure(
        self,
        procedure_id: str,
        final_codes: list[FinalCode],
        procedure_metadata: dict[str, Any] | None = None,
        version: str | None = None,
    ) -> RegistryExportResult:
        """Export a procedure to the registry.

        This method:
        1. Builds a draft entry using build_draft_entry()
        2. Generates an export ID for tracking
        3. Returns a structured export result

        Note: Actual persistence is handled by the caller (API layer),
        keeping this service focused on business logic.

        Args:
            procedure_id: The procedure identifier
            final_codes: List of approved FinalCode objects
            procedure_metadata: Optional dict with patient/procedure info
            version: Schema version ("v2" or "v3")

        Returns:
            RegistryExportResult with entry and export metadata

        Raises:
            RegistryError: If export fails due to validation errors
        """
        version = version or self.default_version

        # Build the draft entry
        draft = self.build_draft_entry(
            procedure_id=procedure_id,
            final_codes=final_codes,
            procedure_metadata=procedure_metadata,
            version=version,
        )

        # Generate export ID
        export_id = f"export_{uuid.uuid4().hex[:12]}"
        export_timestamp = datetime.utcnow()

        # Determine status based on completeness
        if draft.completeness_score >= 0.8:
            status: Literal["success", "partial", "failed"] = "success"
        elif draft.completeness_score >= 0.5:
            status = "partial"
            draft.warnings.append(
                f"Export completed with partial data (completeness: {draft.completeness_score:.0%})"
            )
        else:
            # Still allow export but mark as partial
            status = "partial"
            draft.warnings.append(
                f"Low completeness score ({draft.completeness_score:.0%}). "
                "Consider adding more procedure metadata."
            )

        return RegistryExportResult(
            entry=draft.entry,
            registry_id="ip_registry",
            schema_version=version,
            export_id=export_id,
            export_timestamp=export_timestamp,
            status=status,
            warnings=draft.warnings,
        )

    # NOTE: _build_patient_info, _build_procedure_info, _build_v2_entry, and
    # _build_v3_entry have been refactored into the registry_builder module
    # using the Strategy Pattern. See registry_builder.py for V2RegistryBuilder
    # and V3RegistryBuilder.

    def _validate_entry(
        self,
        entry: IPRegistryV2 | IPRegistryV3,
        version: str,
    ) -> list[str]:
        """Validate an entry and return warnings."""
        warnings: list[str] = []

        # Check for common data quality issues
        if not entry.patient.patient_id and not entry.patient.mrn:
            warnings.append("Patient identifier missing (patient_id or mrn)")

        if not entry.procedure.procedure_date:
            warnings.append("Procedure date not specified")

        if not entry.procedure.indication:
            warnings.append("Procedure indication not specified")

        # Check for procedure-specific completeness
        if entry.ebus_performed and not entry.ebus_stations:
            warnings.append("EBUS performed but no stations documented")

        if entry.tblb_performed and not entry.tblb_sites:
            warnings.append("TBLB performed but no biopsy sites documented")

        if entry.bal_performed and not entry.bal_sites:
            warnings.append("BAL performed but no sites documented")

        if entry.stent_placed and not entry.stents:
            warnings.append("Stent placed but no stent details documented")

        return warnings

    def _compute_completeness(
        self,
        entry: IPRegistryV2 | IPRegistryV3,
        missing_fields: list[str],
    ) -> float:
        """Compute a completeness score for the entry.

        Score is based on:
        - Required fields present (patient ID, date, indication)
        - Procedure-specific fields when relevant
        """
        max_score = 10.0
        score = max_score

        # Deduct for missing required fields
        required_deductions = {
            "patient.patient_id or patient.mrn": 2.0,
            "procedure.procedure_date": 1.5,
            "procedure.indication": 1.0,
        }

        for field in missing_fields:
            if field in required_deductions:
                score -= required_deductions[field]

        # Deduct for procedure-specific missing data
        if entry.ebus_performed and not entry.ebus_stations:
            score -= 0.5
        if entry.tblb_performed and not entry.tblb_sites:
            score -= 0.5
        if entry.stent_placed and not entry.stents:
            score -= 0.5

        return max(0.0, score / max_score)

    def _generate_suggestions(
        self,
        hints: dict[str, list[str]],
        entry: IPRegistryV2 | IPRegistryV3,
    ) -> dict[str, Any]:
        """Generate suggested values based on hints and entry state."""
        suggestions: dict[str, Any] = {}

        # Suggest EBUS station count based on CPT hint
        if "station_count_hint" in hints:
            hint_values = hints["station_count_hint"]
            if "3+" in hint_values:
                suggestions["ebus_station_count"] = "3 or more stations (based on 31653)"
            elif "1-2" in hint_values:
                suggestions["ebus_station_count"] = "1-2 stations (based on 31652)"

        # Suggest navigation system if navigation performed
        if entry.navigation_performed and not entry.navigation_system:
            suggestions["navigation_system"] = "Consider specifying navigation system"

        return suggestions

    # -------------------------------------------------------------------------
    # Hybrid-First Registry Extraction
    # -------------------------------------------------------------------------

    def extract_fields(self, note_text: str) -> RegistryExtractionResult:
        """Extract registry fields using hybrid-first flow.

        This method orchestrates:
        1. Run hybrid coder to get CPT codes and difficulty classification
        2. Map CPT codes to registry boolean flags
        3. Run RegistryEngine extractor with coder context as hints
        4. Merge CPT-driven fields into the extraction result
        5. Validate and finalize the result

        Args:
            note_text: The procedure note text.

        Returns:
            RegistryExtractionResult with extracted record and metadata.
        """
        # Legacy fallback: if no hybrid orchestrator is injected, run extractor only
        if self.hybrid_orchestrator is None:
            logger.info("No hybrid_orchestrator configured, running extractor-only mode")
            record = self.registry_engine.run(note_text, context=None)
            if isinstance(record, tuple):
                record = record[0]  # Unpack if evidence included
            return RegistryExtractionResult(
                record=record,
                cpt_codes=[],
                coder_difficulty="unknown",
                coder_source="extractor_only",
                mapped_fields={},
                warnings=["No hybrid orchestrator configured - CPT codes not extracted"],
            )

        # 1. Run Hybrid Coder
        logger.debug("Running hybrid coder for registry extraction")
        coder_result: HybridCoderResult = self.hybrid_orchestrator.get_codes(note_text)

        # 2. Map Codes to Registry Fields
        mapped_fields = aggregate_registry_fields(
            coder_result.codes, version=self.default_version
        )
        logger.debug(
            "Mapped %d CPT codes to registry fields",
            len(coder_result.codes),
            extra={"cpt_codes": coder_result.codes, "mapped_fields": list(mapped_fields.keys())},
        )

        # 3. Run Extractor with Coder Hints
        extraction_context = {
            "verified_cpt_codes": coder_result.codes,
            "coder_difficulty": coder_result.difficulty.value,
            "hybrid_source": coder_result.source,
            "ml_metadata": coder_result.metadata.get("ml_result"),
        }

        record = self.registry_engine.run(note_text, context=extraction_context)
        if isinstance(record, tuple):
            record = record[0]  # Unpack if evidence included

        # 4. Merge CPT-driven fields into the extraction result
        merged_record = self._merge_cpt_fields_into_record(record, mapped_fields)

        # 5. Validate and finalize (includes ML hybrid audit)
        final_result = self._validate_and_finalize(
            RegistryExtractionResult(
                record=merged_record,
                cpt_codes=coder_result.codes,
                coder_difficulty=coder_result.difficulty.value,
                coder_source=coder_result.source,
                mapped_fields=mapped_fields,
                warnings=[],
            ),
            coder_result=coder_result,
            note_text=note_text,
        )

        return final_result

    def _merge_cpt_fields_into_record(
        self,
        record: RegistryRecord,
        mapped_fields: dict[str, Any],
    ) -> RegistryRecord:
        """Apply CPT-based mapped fields onto the registry record.

        Handles the NESTED structure from aggregate_registry_fields:
        {
            "procedures_performed": {
                "linear_ebus": {"performed": True},
                "bal": {"performed": True},
            },
            "pleural_procedures": {
                "thoracentesis": {"performed": True},
            }
        }

        This is conservative: only overwrite fields that are currently unset/False,
        unless there's a strong reason to prefer CPT over text extraction.

        Args:
            record: The extracted RegistryRecord from RegistryEngine.
            mapped_fields: Nested dict of fields from CPT mapping.

        Returns:
            Updated RegistryRecord with merged fields.
        """
        record_data = record.model_dump()

        # Handle procedures_performed section
        proc_map = mapped_fields.get("procedures_performed") or {}
        if proc_map:
            current_procs = record_data.get("procedures_performed") or {}
            for proc_name, proc_values in proc_map.items():
                current_proc = current_procs.get(proc_name) or {}

                # Merge each field in the procedure
                for field_name, cpt_value in proc_values.items():
                    current_val = current_proc.get(field_name)

                    # Only overwrite if current is falsy
                    if current_val in (None, False, "", [], {}):
                        current_proc[field_name] = cpt_value
                        logger.debug(
                            "Merged CPT field procedures_performed.%s.%s=%s (was %s)",
                            proc_name,
                            field_name,
                            cpt_value,
                            current_val,
                        )
                    elif isinstance(cpt_value, bool) and cpt_value is True:
                        # For boolean flags, CPT evidence is strong
                        if current_val is False:
                            current_proc[field_name] = True
                            logger.debug(
                                "Overrode procedures_performed.%s.%s to True based on CPT",
                                proc_name,
                                field_name,
                            )

                current_procs[proc_name] = current_proc
            record_data["procedures_performed"] = current_procs

        # Handle pleural_procedures section
        pleural_map = mapped_fields.get("pleural_procedures") or {}
        if pleural_map:
            current_pleural = record_data.get("pleural_procedures") or {}
            for proc_name, proc_values in pleural_map.items():
                current_proc = current_pleural.get(proc_name) or {}

                # Merge each field in the procedure
                for field_name, cpt_value in proc_values.items():
                    current_val = current_proc.get(field_name)

                    if current_val in (None, False, "", [], {}):
                        current_proc[field_name] = cpt_value
                        logger.debug(
                            "Merged CPT field pleural_procedures.%s.%s=%s (was %s)",
                            proc_name,
                            field_name,
                            cpt_value,
                            current_val,
                        )
                    elif isinstance(cpt_value, bool) and cpt_value is True:
                        if current_val is False:
                            current_proc[field_name] = True
                            logger.debug(
                                "Overrode pleural_procedures.%s.%s to True based on CPT",
                                proc_name,
                                field_name,
                            )

                current_pleural[proc_name] = current_proc
            record_data["pleural_procedures"] = current_pleural

        # Reconstruct the record
        return RegistryRecord(**record_data)

    def _validate_and_finalize(
        self,
        result: RegistryExtractionResult,
        *,
        coder_result: HybridCoderResult,
        note_text: str = "",
    ) -> RegistryExtractionResult:
        """Central validation and finalization logic.

        Compare CPT-driven signals (coder_result.codes) with registry fields and
        set validation flags accordingly. Also performs ML hybrid audit to detect
        procedures that ML predicted but CPT-derived flags did not capture.

        Marks cases for manual review when:
        - CPT codes don't match extracted registry fields
        - Case difficulty is LOW_CONF or GRAY_ZONE
        - ML predictor detects procedures not captured by CPT pathway

        Args:
            result: The extraction result to validate.
            coder_result: The original hybrid coder result for cross-validation.
            note_text: Original procedure note text for ML prediction.

        Returns:
            Validated and finalized RegistryExtractionResult with validation flags.
        """
        from modules.ml_coder.thresholds import CaseDifficulty

        codes = set(result.cpt_codes)
        record = result.record
        validation_errors: list[str] = list(result.validation_errors)
        warnings = list(result.warnings)
        audit_warnings: list[str] = list(result.audit_warnings)
        needs_manual_review = result.needs_manual_review

        # Get nested procedure objects (may be None)
        procedures = getattr(record, "procedures_performed", None)
        pleural = getattr(record, "pleural_procedures", None)

        # Helper to safely check if a nested procedure is present
        def _proc_is_set(obj, attr: str) -> bool:
            if obj is None:
                return False
            sub_obj = getattr(obj, attr, None)
            if sub_obj is None:
                return False
            # For nested Pydantic models, check if 'performed' field exists and is True
            if hasattr(sub_obj, "performed"):
                return bool(getattr(sub_obj, "performed", False))
            # Otherwise, just check if the object is truthy
            return bool(sub_obj)

        # -------------------------------------------------------------------------
        # 1. Derive aggregate procedure flags from granular_data if present
        # -------------------------------------------------------------------------
        granular = None
        if record.granular_data is not None:
            granular = record.granular_data.model_dump()

        existing_procedures = None
        if record.procedures_performed is not None:
            existing_procedures = record.procedures_performed.model_dump()

        if granular is not None:
            updated_procs, granular_warnings = derive_procedures_from_granular(
                granular_data=granular,
                existing_procedures=existing_procedures,
            )
            # Re-apply to record via reconstruction
            record_data = record.model_dump()
            if updated_procs:
                record_data["procedures_performed"] = updated_procs
            # Append warnings to both record + result
            record_data.setdefault("granular_validation_warnings", [])
            record_data["granular_validation_warnings"].extend(granular_warnings)
            validation_errors.extend(granular_warnings)
            # Reconstruct record with updated procedures
            record = RegistryRecord(**record_data)

        # Re-fetch procedures/pleural after potential update
        procedures = getattr(record, "procedures_performed", None)
        pleural = getattr(record, "pleural_procedures", None)

        # -------------------------------------------------------------------------
        # 2. CPT-to-Registry Field Consistency Checks
        # -------------------------------------------------------------------------

        # Linear EBUS: 31652 (1-2 stations), 31653 (3+ stations)
        if "31652" in codes or "31653" in codes:
            if not _proc_is_set(procedures, "linear_ebus"):
                validation_errors.append(
                    f"CPT {'31652' if '31652' in codes else '31653'} present "
                    "but procedures_performed.linear_ebus is not marked."
                )
            # Check station count hint
            if procedures and getattr(procedures, "linear_ebus", None):
                ebus_obj = procedures.linear_ebus
                stations = getattr(ebus_obj, "stations_sampled", None)
                if "31653" in codes and stations:
                    # 31653 implies 3+ stations
                    try:
                        station_count = len(stations) if isinstance(stations, list) else int(stations)
                        if station_count < 3:
                            warnings.append(
                                f"CPT 31653 implies 3+ EBUS stations, but only {station_count} recorded."
                            )
                    except (ValueError, TypeError):
                        pass

        # Radial EBUS: 31620
        if "31620" in codes:
            if not _proc_is_set(procedures, "radial_ebus"):
                validation_errors.append(
                    "CPT 31620 present but procedures_performed.radial_ebus is not marked."
                )

        # BAL: 31624, 31625
        if "31624" in codes or "31625" in codes:
            if not _proc_is_set(procedures, "bal"):
                validation_errors.append(
                    "CPT 31624/31625 present but procedures_performed.bal is not marked."
                )

        # Transbronchial biopsy: 31628, 31629
        if "31628" in codes or "31629" in codes:
            if not _proc_is_set(procedures, "transbronchial_biopsy"):
                validation_errors.append(
                    "CPT 31628/31629 present but procedures_performed.transbronchial_biopsy is not marked."
                )

        # Navigation: 31627
        if "31627" in codes:
            if not _proc_is_set(procedures, "navigational_bronchoscopy"):
                validation_errors.append(
                    "CPT 31627 present but procedures_performed.navigational_bronchoscopy is not marked."
                )

        # Stent: 31636, 31637
        if "31636" in codes or "31637" in codes:
            if not _proc_is_set(procedures, "airway_stent"):
                validation_errors.append(
                    "CPT 31636/31637 present but procedures_performed.airway_stent is not marked."
                )

        # Dilation: 31630, 31631
        if "31630" in codes or "31631" in codes:
            if not _proc_is_set(procedures, "airway_dilation"):
                validation_errors.append(
                    "CPT 31630/31631 present but procedures_performed.airway_dilation is not marked."
                )

        # BLVR (valve): 31647, 31648, 31649
        blvr_codes = {"31647", "31648", "31649"}
        if blvr_codes & codes:
            if not _proc_is_set(procedures, "blvr"):
                validation_errors.append(
                    "CPT 31647/31648/31649 present but procedures_performed.blvr is not marked."
                )

        # Thermoplasty: 31660, 31661
        if "31660" in codes or "31661" in codes:
            if not _proc_is_set(procedures, "bronchial_thermoplasty"):
                validation_errors.append(
                    "CPT 31660/31661 present but procedures_performed.bronchial_thermoplasty is not marked."
                )

        # Rigid bronchoscopy: 31641
        if "31641" in codes:
            if not _proc_is_set(procedures, "rigid_bronchoscopy"):
                # Only warn, as 31641 can also be thermal ablation
                warnings.append(
                    "CPT 31641 present - verify rigid_bronchoscopy or thermal ablation is marked."
                )

        # Tube thoracostomy: 32551
        if "32551" in codes:
            if not _proc_is_set(pleural, "chest_tube"):
                validation_errors.append(
                    "CPT 32551 present but pleural_procedures.chest_tube is not marked."
                )

        # Thoracentesis: 32554, 32555, 32556, 32557
        thoracentesis_codes = {"32554", "32555", "32556", "32557"}
        if thoracentesis_codes & codes:
            if not _proc_is_set(pleural, "thoracentesis") and not _proc_is_set(pleural, "chest_tube"):
                validation_errors.append(
                    "Thoracentesis CPT codes present but no pleural procedure marked."
                )

        # Medical thoracoscopy / pleuroscopy: 32601
        if "32601" in codes:
            if not _proc_is_set(pleural, "medical_thoracoscopy"):
                validation_errors.append(
                    "CPT 32601 present but pleural_procedures.medical_thoracoscopy is not marked."
                )

        # Pleurodesis: 32560, 32650
        if "32560" in codes or "32650" in codes:
            if not _proc_is_set(pleural, "pleurodesis"):
                validation_errors.append(
                    "CPT 32560/32650 present but pleural_procedures.pleurodesis is not marked."
                )

        # -------------------------------------------------------------------------
        # 3. Difficulty-based Manual Review Flags
        # -------------------------------------------------------------------------

        # Low-confidence cases: always require manual review
        if coder_result.difficulty == CaseDifficulty.LOW_CONF:
            needs_manual_review = True
            if not validation_errors:
                validation_errors.append(
                    "Hybrid coder marked this case as LOW_CONF; manual review required."
                )

        # Gray zone cases: also require manual review
        if coder_result.difficulty == CaseDifficulty.GRAY_ZONE:
            needs_manual_review = True

        # Any validation errors trigger manual review
        if validation_errors and not needs_manual_review:
            needs_manual_review = True

        # Granular validation warnings also trigger manual review
        granular_warnings_on_record = getattr(record, "granular_validation_warnings", [])
        if granular_warnings_on_record and not needs_manual_review:
            needs_manual_review = True

        # -------------------------------------------------------------------------
        # 4. ML Hybrid Audit: Compare ML predictions with CPT-derived flags
        # -------------------------------------------------------------------------
        # This is an audit overlay that cross-checks ML predictions against
        # CPT-derived flags to catch procedures the CPT pathway may have missed.

        ml_predictor = self._get_registry_ml_predictor()
        if ml_predictor is not None and note_text:
            ml_case = ml_predictor.classify_case(note_text)

            # Build CPT-derived flags dict from mapped_fields
            # The mapped_fields has structure like:
            # {"procedures_performed": {"linear_ebus": {"performed": True}, ...}}
            cpt_flags: dict[str, bool] = {}
            proc_map = result.mapped_fields.get("procedures_performed") or {}
            for proc_name, proc_values in proc_map.items():
                if isinstance(proc_values, dict) and proc_values.get("performed"):
                    cpt_flags[proc_name] = True

            pleural_map = result.mapped_fields.get("pleural_procedures") or {}
            for proc_name, proc_values in pleural_map.items():
                if isinstance(proc_values, dict) and proc_values.get("performed"):
                    cpt_flags[proc_name] = True

            # Build ML flags dict
            ml_flags: dict[str, bool] = {}
            for pred in ml_case.predictions:
                ml_flags[pred.field] = pred.is_positive

            # Compare flags and generate audit warnings
            # Scenario C: ML detected a procedure that CPT pathway did not
            for field_name, ml_positive in ml_flags.items():
                cpt_positive = cpt_flags.get(field_name, False)

                if ml_positive and not cpt_positive:
                    # ML detected a procedure the CPT pathway did not capture
                    # Find the probability for context
                    prob = next(
                        (p.probability for p in ml_case.predictions if p.field == field_name),
                        0.0,
                    )
                    audit_warnings.append(
                        f"ML detected procedure '{field_name}' with high confidence "
                        f"(prob={prob:.2f}), but no corresponding CPT-derived flag was set. "
                        f"Please review."
                    )
                    needs_manual_review = True

            # Log ML audit summary
            ml_detected_count = sum(1 for f, v in ml_flags.items() if v and not cpt_flags.get(f, False))
            if ml_detected_count > 0:
                logger.info(
                    "ml_hybrid_audit_discrepancy",
                    extra={
                        "ml_detected_not_in_cpt": ml_detected_count,
                        "audit_warnings": audit_warnings,
                    },
                )

        # -------------------------------------------------------------------------
        # Telemetry: Log validation outcome for monitoring
        # -------------------------------------------------------------------------
        logger.info(
            "registry_validation_complete",
            extra={
                "coder_difficulty": coder_result.difficulty.value,
                "coder_source": coder_result.source,
                "needs_manual_review": needs_manual_review,
                "validation_error_count": len(validation_errors),
                "warning_count": len(warnings),
                "audit_warning_count": len(audit_warnings),
                "cpt_code_count": len(codes),
            },
        )

        # -------------------------------------------------------------------------
        # 5. Return Updated Result
        # -------------------------------------------------------------------------
        return RegistryExtractionResult(
            record=record,  # Use potentially updated record from granular derivation
            cpt_codes=result.cpt_codes,
            coder_difficulty=result.coder_difficulty,
            coder_source=result.coder_source,
            mapped_fields=result.mapped_fields,
            warnings=warnings,
            needs_manual_review=needs_manual_review,
            validation_errors=validation_errors,
            audit_warnings=audit_warnings,
        )


# Factory function for DI
def get_registry_service() -> RegistryService:
    """Get a RegistryService instance with default configuration."""
    return RegistryService()
```

---
### `modules/agents/contracts.py`
```
"""Agent contracts defining I/O schemas for the 3-agent reporter pipeline.

This module defines the data contracts between:
- ParserAgent: Splits raw text into segments and extracts entities
- SummarizerAgent: Produces section summaries from segments/entities
- StructurerAgent: Maps summaries to registry model and generates codes
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict, Tuple, Literal


class AgentWarning(BaseModel):
    """A warning from an agent that doesn't prevent output."""

    code: str  # "MISSING_HEADER", "AMBIGUOUS_SECTION"
    message: str
    section: Optional[str] = None


class AgentError(BaseModel):
    """An error from an agent that may prevent successful output."""

    code: str  # "NO_SECTIONS_FOUND", "PARSING_FAILED"
    message: str
    section: Optional[str] = None


class Segment(BaseModel):
    """A segmented portion of the note with optional character spans."""

    id: str = ""
    type: str  # "HISTORY", "PROCEDURE", "FINDINGS", "IMPRESSION", etc.
    text: str
    start_char: Optional[int] = None
    end_char: Optional[int] = None
    spans: List[Tuple[int, int]] = Field(default_factory=list)


class Entity(BaseModel):
    """An entity extracted from the note, such as a station or stent."""

    label: str
    value: str
    name: str = ""  # For backwards compatibility
    type: str = ""
    offsets: Optional[Tuple[int, int]] = None
    evidence_segment_id: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None


class Trace(BaseModel):
    """Trace metadata capturing what triggered an agent's output."""

    trigger_phrases: List[str] = Field(default_factory=list)
    rule_paths: List[str] = Field(default_factory=list)
    confounders_checked: List[str] = Field(default_factory=list)
    confidence: float = 0.0
    notes: Optional[str] = None


class ParserIn(BaseModel):
    """Input to the Parser agent."""

    note_id: str
    raw_text: str


class ParserOut(BaseModel):
    """Output from the Parser agent."""

    note_id: str = ""
    segments: List[Segment] = Field(default_factory=list)
    entities: List[Entity] = Field(default_factory=list)
    trace: Trace = Field(default_factory=Trace)
    warnings: List[AgentWarning] = Field(default_factory=list)
    errors: List[AgentError] = Field(default_factory=list)
    status: Literal["ok", "degraded", "failed"] = "ok"


class SummarizerIn(BaseModel):
    """Input to the Summarizer agent."""

    parser_out: ParserOut


class SummarizerOut(BaseModel):
    """Output from the Summarizer agent."""

    note_id: str = ""
    summaries: Dict[str, str] = Field(default_factory=dict)
    caveats: List[str] = Field(default_factory=list)
    trace: Trace = Field(default_factory=Trace)
    warnings: List[AgentWarning] = Field(default_factory=list)
    errors: List[AgentError] = Field(default_factory=list)
    status: Literal["ok", "degraded", "failed"] = "ok"


class StructurerIn(BaseModel):
    """Input to the Structurer agent."""

    summarizer_out: SummarizerOut


class StructurerOut(BaseModel):
    """Output from the Structurer agent."""

    note_id: str = ""
    registry: Dict[str, Any] = Field(default_factory=dict)
    codes: Dict[str, Any] = Field(default_factory=dict)
    rationale: Dict[str, Any] = Field(default_factory=dict)
    trace: Trace = Field(default_factory=Trace)
    warnings: List[AgentWarning] = Field(default_factory=list)
    errors: List[AgentError] = Field(default_factory=list)
    status: Literal["ok", "degraded", "failed"] = "ok"


class PipelineResult(BaseModel):
    """Full result from running the 3-agent pipeline."""

    pipeline_status: Literal["ok", "degraded", "failed_parser", "failed_summarizer", "failed_structurer"]
    parser: Optional[ParserOut] = None
    summarizer: Optional[SummarizerOut] = None
    structurer: Optional[StructurerOut] = None
    registry: Optional[Dict[str, Any]] = None
    codes: Optional[Dict[str, Any]] = None
```

---
### `modules/agents/run_pipeline.py`
```
"""Pipeline orchestrator for parser, summarizer, and structurer agents.

This module orchestrates the 3-agent reporter pipeline with proper
status tracking, error handling, and graceful degradation.
"""

from typing import Literal

from modules.agents.contracts import (
    ParserIn,
    ParserOut,
    SummarizerIn,
    SummarizerOut,
    StructurerIn,
    StructurerOut,
    PipelineResult,
    AgentError,
)
from modules.agents.parser.parser_agent import ParserAgent
from modules.agents.summarizer.summarizer_agent import SummarizerAgent
from modules.agents.structurer.structurer_agent import StructurerAgent
from observability.timing import timed
from observability.logging_config import get_logger

logger = get_logger("pipeline")


def run_pipeline(note: dict) -> dict:
    """Run the full agent pipeline on a single note dict.

    Args:
        note: Dict with keys 'note_id' and 'raw_text'.

    Returns:
        Dict with pipeline_status, agent outputs, registry, and codes.
    """
    result = run_pipeline_typed(note)
    return result.model_dump()


def run_pipeline_typed(note: dict) -> PipelineResult:
    """Run the full agent pipeline with typed output.

    The pipeline runs through three stages:
    1. Parser: Splits raw text into segments and extracts entities
    2. Summarizer: Produces section summaries from segments/entities
    3. Structurer: Maps summaries to registry model and generates codes

    If any stage fails (status='failed'), the pipeline stops and returns
    the partial result. Degraded stages continue but mark the overall
    pipeline as degraded.

    Args:
        note: Dict with keys 'note_id' and 'raw_text'.

    Returns:
        PipelineResult with status, agent outputs, registry, and codes.
    """
    note_id = note.get("note_id", "")
    raw_text = note.get("raw_text", "")

    with timed("pipeline.total") as timing:
        # Stage 1: Parser
        with timed("pipeline.parser"):
            parser_out = _run_parser(note_id, raw_text)

        if parser_out.status == "failed":
            logger.warning(
                "Pipeline failed at parser stage",
                extra={"note_id": note_id, "errors": [e.model_dump() for e in parser_out.errors]},
            )
            return PipelineResult(
                pipeline_status="failed_parser",
                parser=parser_out,
            )

        # Stage 2: Summarizer
        with timed("pipeline.summarizer"):
            summarizer_out = _run_summarizer(parser_out)

        if summarizer_out.status == "failed":
            logger.warning(
                "Pipeline failed at summarizer stage",
                extra={"note_id": note_id, "errors": [e.model_dump() for e in summarizer_out.errors]},
            )
            return PipelineResult(
                pipeline_status="failed_summarizer",
                parser=parser_out,
                summarizer=summarizer_out,
            )

        # Stage 3: Structurer
        with timed("pipeline.structurer"):
            structurer_out = _run_structurer(summarizer_out)

        if structurer_out.status == "failed":
            logger.warning(
                "Pipeline failed at structurer stage",
                extra={"note_id": note_id, "errors": [e.model_dump() for e in structurer_out.errors]},
            )
            return PipelineResult(
                pipeline_status="failed_structurer",
                parser=parser_out,
                summarizer=summarizer_out,
                structurer=structurer_out,
            )

        # Determine overall status
        statuses = [parser_out.status, summarizer_out.status, structurer_out.status]
        if all(s == "ok" for s in statuses):
            pipeline_status: Literal["ok", "degraded", "failed_parser", "failed_summarizer", "failed_structurer"] = "ok"
        else:
            pipeline_status = "degraded"

    logger.info(
        "Pipeline complete",
        extra={
            "note_id": note_id,
            "pipeline_status": pipeline_status,
            "processing_time_ms": timing.elapsed_ms,
            "parser_status": parser_out.status,
            "summarizer_status": summarizer_out.status,
            "structurer_status": structurer_out.status,
        },
    )

    return PipelineResult(
        pipeline_status=pipeline_status,
        parser=parser_out,
        summarizer=summarizer_out,
        structurer=structurer_out,
        registry=structurer_out.registry,
        codes=structurer_out.codes,
    )


def _run_parser(note_id: str, raw_text: str) -> ParserOut:
    """Run the parser agent with error handling."""
    try:
        parser_in = ParserIn(note_id=note_id, raw_text=raw_text)
        parser_agent = ParserAgent()
        parser_out = parser_agent.run(parser_in)

        # Ensure note_id is set
        parser_out.note_id = note_id

        return parser_out

    except Exception as e:
        logger.error(f"Parser agent threw exception: {e}")
        return ParserOut(
            note_id=note_id,
            status="failed",
            errors=[
                AgentError(
                    code="PARSER_EXCEPTION",
                    message=str(e),
                )
            ],
        )


def _run_summarizer(parser_out: ParserOut) -> SummarizerOut:
    """Run the summarizer agent with error handling."""
    try:
        summarizer_in = SummarizerIn(parser_out=parser_out)
        summarizer_agent = SummarizerAgent()
        summarizer_out = summarizer_agent.run(summarizer_in)

        # Ensure note_id is set
        summarizer_out.note_id = parser_out.note_id

        return summarizer_out

    except Exception as e:
        logger.error(f"Summarizer agent threw exception: {e}")
        return SummarizerOut(
            note_id=parser_out.note_id,
            status="failed",
            errors=[
                AgentError(
                    code="SUMMARIZER_EXCEPTION",
                    message=str(e),
                )
            ],
        )


def _run_structurer(summarizer_out: SummarizerOut) -> StructurerOut:
    """Run the structurer agent with error handling."""
    try:
        structurer_in = StructurerIn(summarizer_out=summarizer_out)
        structurer_agent = StructurerAgent()
        structurer_out = structurer_agent.run(structurer_in)

        # Ensure note_id is set
        structurer_out.note_id = summarizer_out.note_id

        return structurer_out

    except Exception as e:
        logger.error(f"Structurer agent threw exception: {e}")
        return StructurerOut(
            note_id=summarizer_out.note_id,
            status="failed",
            errors=[
                AgentError(
                    code="STRUCTURER_EXCEPTION",
                    message=str(e),
                )
            ],
        )
```

---
### `docs/DEVELOPMENT.md`
```
# Development Guide

This document is the **Single Source of Truth** for developers and AI assistants working on the Procedure Suite.

## Core Mandates

1.  **Main Application**: Always edit `modules/api/fastapi_app.py`. Never edit `api/app.py` (deprecated).
2.  **Coding Service**: Use `CodingService` from `modules/coder/application/coding_service.py`. The old `modules.coder.engine.CoderEngine` is deprecated.
3.  **Registry Service**: Use `RegistryService` from `modules/registry/application/registry_service.py`.
4.  **Knowledge Base**: The source of truth for coding rules is `data/knowledge/ip_coding_billing_v2_8.json`.
5.  **Tests**: Preserve existing tests. Run `make test` before committing.

---

## System Architecture

### Directory Structure

| Directory | Status | Purpose |
|-----------|--------|---------|
| `modules/api/` | **ACTIVE** | Main FastAPI app (`fastapi_app.py`) |
| `modules/coder/` | **ACTIVE** | CPT Coding Engine with CodingService (8-step pipeline) |
| `modules/ml_coder/` | **ACTIVE** | ML-based code prediction and training |
| `modules/registry/` | **ACTIVE** | Registry extraction with RegistryService and RegistryEngine |
| `modules/agents/` | **ACTIVE** | 3-agent pipeline (Parser, Summarizer, Structurer) |
| `modules/reporter/` | **ACTIVE** | Report generation with Jinja templates |
| `modules/common/` | **ACTIVE** | Shared utilities, logging, exceptions |
| `modules/domain/` | **ACTIVE** | Domain models and business rules |
| `api/` | **DEPRECATED** | Old API entry point. Do not use. |

### Key Services

| Service | Location | Purpose |
|---------|----------|---------|
| `CodingService` | `modules/coder/application/coding_service.py` | 8-step CPT coding pipeline |
| `RegistryService` | `modules/registry/application/registry_service.py` | Hybrid-first registry extraction |
| `SmartHybridOrchestrator` | `modules/coder/application/smart_hybrid_policy.py` | ML-first hybrid coding |
| `RegistryEngine` | `modules/registry/engine.py` | LLM-based field extraction |

### Data Flow

```
[Procedure Note]
       │
       ▼
[API Layer] (modules/api/fastapi_app.py)
       │
       ├─> [CodingService] ──> [SmartHybridOrchestrator] ──> [Codes + RVUs]
       │        │                    │
       │        │                    ├── ML Prediction
       │        │                    ├── Rules Engine
       │        │                    └── LLM Advisor (fallback)
       │        │
       │        └──> NCCI/MER Compliance ──> Final Codes
       │
       ├─> [RegistryService] ──> [CPT Mapping + LLM Extraction] ──> [Registry Record]
       │
       └─> [Reporter] ──────> [Jinja Templates] ───> [Synoptic Report]
```

---

## AI Agent Roles

### 1. Coder Agent

**Focus**: `modules/coder/`

**Key Files:**
- `modules/coder/application/coding_service.py` - Main orchestrator
- `modules/coder/application/smart_hybrid_policy.py` - Hybrid decision logic
- `modules/coder/domain_rules.py` - NCCI bundling, domain rules
- `modules/coder/rules_engine.py` - Rule-based inference

**Responsibilities:**
- Maintain the 8-step coding pipeline in `CodingService`
- Update domain rules in `domain_rules.py`
- Ensure NCCI/MER compliance logic is correct
- Keep confidence thresholds tuned in `modules/ml_coder/thresholds.py`

**Rule**: Do not scatter logic. Keep business rules central in the Knowledge Base or domain_rules.py.

### 2. Registry Agent

**Focus**: `modules/registry/`

**Key Files:**
- `modules/registry/application/registry_service.py` - Main service
- `modules/registry/application/cpt_registry_mapping.py` - CPT → registry mapping
- `modules/registry/engine.py` - LLM extraction engine
- `modules/registry/prompts.py` - LLM prompts
- `modules/registry/schema.py` - RegistryRecord model
- `modules/registry/v2_booleans.py` - V2→V3 boolean mapping for ML
- `modules/registry/postprocess.py` - Output normalization

**Responsibilities:**
- Maintain schema definitions in `schema.py` and `schema_granular.py`
- Update LLM prompts in `prompts.py`
- Handle LLM list outputs by adding normalizers in `postprocess.py`
- Keep CPT-to-registry mapping current in `cpt_registry_mapping.py`
- Update V2→V3 boolean mapping in `v2_booleans.py` when schema changes

**Critical**: When changing the registry schema, update:
1. `data/knowledge/IP_Registry.json` - Schema definition
2. `schemas/IP_Registry.json` - JSON Schema for validation
3. `modules/registry/v2_booleans.py` - Boolean field list
4. `modules/registry/application/cpt_registry_mapping.py` - CPT mappings

### 3. ML Agent

**Focus**: `modules/ml_coder/`

**Key Files:**
- `modules/ml_coder/predictor.py` - CPT code predictor
- `modules/ml_coder/registry_predictor.py` - Registry field predictor
- `modules/ml_coder/training.py` - Model training
- `modules/ml_coder/data_prep.py` - Data preparation
- `modules/ml_coder/thresholds.py` - Confidence thresholds

**Responsibilities:**
- Maintain ML model training pipelines
- Tune confidence thresholds for hybrid policy
- Prepare training data from golden extractions
- Ensure ML predictions align with registry schema

### 4. Reporter Agent

**Focus**: `modules/reporter/`

**Responsibilities:**
- Edit Jinja templates for report formatting
- Maintain validation logic for required fields
- Ensure inference logic derives fields correctly
- **Rule**: Use `{% if %}` guards in templates. Never output "None" or "missing" in final reports.

### 5. DevOps/API Agent

**Focus**: `modules/api/`

**Responsibilities:**
- Maintain `fastapi_app.py`
- Ensure endpoints `/v1/coder/run`, `/v1/registry/run`, `/report/render` work correctly
- **Warning**: Do not create duplicate routes. Check existing endpoints first.

---

## Module Dependencies

```
modules/api/
    └── depends on: modules/coder/, modules/registry/, modules/reporter/

modules/coder/
    ├── depends on: modules/ml_coder/, modules/domain/, modules/phi/
    └── provides: CodingService, SmartHybridOrchestrator

modules/registry/
    ├── depends on: modules/coder/, modules/ml_coder/
    └── provides: RegistryService, RegistryEngine

modules/ml_coder/
    └── provides: MLPredictor, RegistryMLPredictor

modules/agents/
    └── provides: run_pipeline(), ParserAgent, SummarizerAgent, StructurerAgent
```

---

## Testing

### Test Commands

```bash
# All tests
make test

# Specific test suites
pytest tests/coder/ -v              # Coder tests
pytest tests/registry/ -v           # Registry tests
pytest tests/ml_coder/ -v           # ML coder tests
pytest tests/api/ -v                # API tests

# Validation
make validate-registry              # Registry extraction validation
make preflight                      # Pre-flight checks
make lint                           # Linting
```

### LLM Tests

By default, tests run in offline mode with stub LLMs. To test actual extraction:

```bash
export GEMINI_OFFLINE=0
export REGISTRY_USE_STUB_LLM=0
export GEMINI_API_KEY="..."
pytest tests/registry/test_extraction.py
```

### Test Data

- Golden extractions: `data/knowledge/golden_extractions/`
- Synthetic test data: Use fixtures in test files
- **Never** commit PHI (real patient data)

---

## Development Workflow

### Before Making Changes

1. Read relevant documentation:
   - [ARCHITECTURE.md](ARCHITECTURE.md) for system design
   - [AGENTS.md](AGENTS.md) for multi-agent pipeline
   - [Registry_API.md](Registry_API.md) for registry service

2. Understand the data flow:
   - Trace the code path from API endpoint to service to engine
   - Identify which module owns the logic you're changing

3. Check existing tests:
   - Run relevant test suite before changes
   - Understand what behavior is expected

### Making Changes

1. **Edit the correct files**:
   - API: `modules/api/fastapi_app.py` (not `api/app.py`)
   - Coder: `modules/coder/` (not legacy engine)
   - Registry: `modules/registry/`

2. **Follow the architecture**:
   - Services orchestrate, engines execute
   - Keep business rules in domain modules
   - Use adapters for external dependencies

3. **Maintain contracts**:
   - Don't break existing API contracts
   - Update Pydantic schemas if needed
   - Add deprecation warnings, not breaking changes

### After Making Changes

1. Run tests: `make test` or specific test suite
2. Run linting: `make lint`
3. Test the dev server: `./scripts/devserver.sh`
4. Verify no PHI was committed

---

## Development Checklist

Before committing changes:

- [ ] I am editing `modules/api/fastapi_app.py` (not `api/app.py`)
- [ ] I am using `CodingService` (not legacy `CoderEngine`)
- [ ] I am using `RegistryService` (not direct engine calls)
- [ ] I have run `make test` (or relevant unit tests)
- [ ] I have checked `scripts/devserver.sh` to ensure the app starts
- [ ] I have not committed any PHI (real patient data)
- [ ] I have updated documentation if changing APIs or schemas

---

## Common Pitfalls

1. **Editing deprecated files**: Always check if a file is deprecated before editing
2. **Duplicate routes**: Check existing endpoints before adding new ones
3. **Breaking contracts**: Don't change API response shapes without versioning
4. **Scattered logic**: Keep business rules in domain modules, not scattered across services
5. **Missing normalization**: LLM outputs often need post-processing in `postprocess.py`
6. **Schema drift**: When changing registry schema, update all dependent files

---

*Last updated: December 2025*
```

---
### `docs/ARCHITECTURE.md`
```
# Procedure Suite Architecture

This document describes the system architecture, module organization, and data flow of the Procedure Suite.

## Overview

The Procedure Suite is a modular system for automated medical coding, registry extraction, and report generation. It follows a **hexagonal architecture** pattern with clear separation between:

- **Domain logic** (business rules, schemas)
- **Application services** (orchestration, workflows)
- **Adapters** (LLM, ML, database, API)

> **Architectural Pivot:** The system is currently **ML‑First** for CPT coding and
> **hybrid‑first** for registry extraction. A pivot to **Extraction‑First**
> (registry → deterministic CPT) is in progress; “Target” sections in docs
> describe that end state.

## Directory Structure

```
Procedure_suite/
├── modules/                    # Core application modules
│   ├── api/                    # FastAPI endpoints and routes
│   ├── coder/                  # CPT coding engine
│   ├── ml_coder/               # ML-based prediction
│   ├── registry/               # Registry extraction
│   ├── agents/                 # 3-agent pipeline
│   ├── reporter/               # Report generation
│   ├── common/                 # Shared utilities
│   ├── domain/                 # Domain models and rules
│   └── phi/                    # PHI handling
├── data/
│   └── knowledge/              # Knowledge bases and training data
├── schemas/                    # JSON Schema definitions
├── proc_schemas/               # Pydantic schema definitions
├── config/                     # Configuration settings
├── scripts/                    # CLI tools and utilities
├── tests/                      # Test suites
└── docs/                       # Documentation
```

## Core Modules

### 1. API Layer (`modules/api/`)

The FastAPI application serving REST endpoints.

**Key Files:**
- `fastapi_app.py` - Main application with route registration
- `routes/` - Endpoint handlers
- `schemas/` - Request/response models
- `dependencies.py` - Dependency injection

**Endpoints:**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/coder/run` | POST | Run CPT coding on procedure note |
| `/v1/registry/run` | POST | Extract registry data from note |
| `/v1/report/render` | POST | Generate synoptic report |
| `/health` | GET | Health check |

### 2. Coder Module (`modules/coder/`)

CPT code prediction using rules, ML, and LLM.

**Architecture:**
```
modules/coder/
├── application/
│   ├── coding_service.py       # Main orchestrator (8-step pipeline)
│   └── smart_hybrid_policy.py  # ML-first hybrid decision logic
├── adapters/
│   ├── llm/                    # LLM advisor adapter
│   ├── nlp/                    # Keyword mapping, negation detection
│   └── ml_ranker.py            # ML prediction adapter
├── domain_rules.py             # NCCI bundling, EBUS rules
├── rules_engine.py             # Rule-based code inference
└── engine.py                   # Legacy coder (deprecated)
```

**CodingService 8-Step Pipeline:**
1. Rule engine → rule_codes + confidence
2. (Optional) ML ranker → ml_confidence
3. LLM advisor → advisor_codes + confidence
4. Smart hybrid merge → HybridDecision flags
5. Evidence validation → verify codes in text
6. Non-negotiable rules (NCCI/MER) → remove invalid combos
7. Confidence aggregation → final_confidence, review_flag
8. Build CodeSuggestion[] → return for review

### 3. ML Coder Module (`modules/ml_coder/`)

Machine learning models for CPT and registry prediction.

**Key Files:**
- `predictor.py` - CPT code predictor
- `registry_predictor.py` - Registry field predictor
- `training.py` - Model training pipeline
- `registry_training.py` - Registry ML training
- `data_prep.py` - Data preparation utilities
- `thresholds.py` - Confidence thresholds

**ML-First Hybrid Policy:**
```
Note → ML Predict → Classify Difficulty → Decision Gate → Final Codes
                         ↓
         HIGH_CONF: ML + Rules (fast path)
         GRAY_ZONE: LLM as judge
         LOW_CONF:  LLM primary
```

### 4. Registry Module (`modules/registry/`)

Registry data extraction from procedure notes.

**Architecture:**
```
modules/registry/
├── application/
│   ├── registry_service.py     # Main service (hybrid-first)
│   ├── registry_builder.py     # Build registry entries
│   └── cpt_registry_mapping.py # CPT → registry field mapping
├── adapters/
│   └── schema_registry.py      # Schema validation
├── engine.py                   # LLM extraction engine
├── prompts.py                  # LLM prompts
├── schema.py                   # RegistryRecord model
├── schema_granular.py          # Granular per-site data
├── v2_booleans.py              # V2→V3 boolean mapping for ML
├── deterministic_extractors.py # Rule-based extractors
├── normalization.py            # Field normalization
└── postprocess.py              # Output post-processing
```

**Hybrid-First Extraction Flow:**
1. CPT Coding (SmartHybridOrchestrator)
2. CPT Mapping (aggregate_registry_fields)
3. LLM Extraction (RegistryEngine)
4. Reconciliation (merge CPT-derived + LLM-extracted)
5. Validation (IP_Registry.json schema)
6. ML Audit (compare CPT-derived vs ML predictions)

### 5. Agents Module (`modules/agents/`)

3-agent pipeline for structured note processing.

**Architecture:**
```
modules/agents/
├── contracts.py                # I/O schemas (Pydantic)
├── run_pipeline.py             # Pipeline orchestration
├── parser/
│   └── parser_agent.py         # Segment extraction
├── summarizer/
│   └── summarizer_agent.py     # Section summarization
└── structurer/
    └── structurer_agent.py     # Registry mapping
```

**Pipeline Flow:**
```
Raw Text → Parser → Segments/Entities
                        ↓
              Summarizer → Section Summaries
                              ↓
                    Structurer → Registry + Codes
```

See [AGENTS.md](AGENTS.md) for detailed agent documentation.

### 6. Reporter Module (`modules/reporter/`)

Synoptic report generation from structured data.

**Key Components:**
- Jinja2 templates for report formatting
- Validation logic for required fields
- Inference logic for derived fields

## Data Flow

### CPT Coding Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Raw Note  │ ──▶ │  ML Predict │ ──▶ │   Classify  │
└─────────────┘     └─────────────┘     │  Difficulty │
                                        └──────┬──────┘
                                               │
                    ┌──────────────────────────┼──────────────────────────┐
                    │                          │                          │
                    ▼                          ▼                          ▼
           ┌────────────────┐       ┌─────────────────┐       ┌────────────────┐
           │   HIGH_CONF    │       │    GRAY_ZONE    │       │   LOW_CONF     │
           │ ML + Rules     │       │  LLM as Judge   │       │ LLM Primary    │
           └───────┬────────┘       └────────┬────────┘       └───────┬────────┘
                   │                         │                        │
                   └─────────────────────────┼────────────────────────┘
                                             │
                                             ▼
                                    ┌─────────────────┐
                                    │ NCCI/MER Rules  │
                                    │  (Compliance)   │
                                    └────────┬────────┘
                                             │
                                             ▼
                                    ┌─────────────────┐
                                    │  Final Codes    │
                                    │ CodeSuggestion[]│
                                    └─────────────────┘
```

### Registry Extraction Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Raw Note  │ ──▶ │  CPT Coder  │ ──▶ │ CPT Mapping │
└─────────────┘     └─────────────┘     │ (Bool Flags)│
                                        └──────┬──────┘
                                               │
                    ┌──────────────────────────┼──────────────────────────┐
                    │                          │                          │
                    ▼                          ▼                          ▼
           ┌────────────────┐       ┌─────────────────┐       ┌────────────────┐
           │  CPT-Derived   │       │ Deterministic   │       │  LLM Extract   │
           │    Fields      │       │   Extractors    │       │  (Engine)      │
           └───────┬────────┘       └────────┬────────┘       └───────┬────────┘
                   │                         │                        │
                   └─────────────────────────┼────────────────────────┘
                                             │
                                             ▼
                                    ┌─────────────────┐
                                    │  Reconciliation │
                                    │  (Merge Fields) │
                                    └────────┬────────┘
                                             │
                                             ▼
                                    ┌─────────────────┐
                                    │   Validation    │
                                    │ (JSON Schema)   │
                                    └────────┬────────┘
                                             │
                                             ▼
                                    ┌─────────────────┐
                                    │ RegistryRecord  │
                                    └─────────────────┘
```

## Schema System

### JSON Schemas
- `schemas/IP_Registry.json` - Registry entry validation
- `data/knowledge/IP_Registry.json` - Registry schema (dynamic model)

### Pydantic Schemas
- `proc_schemas/coding.py` - CodeSuggestion, CodingResult
- `proc_schemas/registry/ip_v2.py` - IPRegistryV2
- `proc_schemas/registry/ip_v3.py` - IPRegistryV3
- `modules/registry/schema.py` - RegistryRecord (dynamic)

### Registry Procedure Flags

The registry uses 29 boolean procedure presence flags for ML training:

**Bronchoscopy Procedures (22):**
- diagnostic_bronchoscopy, bal, bronchial_wash, brushings
- endobronchial_biopsy, tbna_conventional, linear_ebus, radial_ebus
- navigational_bronchoscopy, transbronchial_biopsy, transbronchial_cryobiopsy
- therapeutic_aspiration, foreign_body_removal, airway_dilation, airway_stent
- thermal_ablation, cryotherapy, blvr, peripheral_ablation
- bronchial_thermoplasty, whole_lung_lavage, rigid_bronchoscopy

**Pleural Procedures (7):**
- thoracentesis, chest_tube, ipc, medical_thoracoscopy
- pleurodesis, pleural_biopsy, fibrinolytic_therapy

See `modules/registry/v2_booleans.py` for the canonical V2→V3 mapping.

## Configuration

### Settings (`config/settings.py`)

Key configuration classes:
- `CoderSettings` - Coder thresholds and behavior
- `RegistrySettings` - Registry extraction settings
- `MLSettings` - ML model paths and parameters

### Environment Variables

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Gemini LLM API key |
| `GEMINI_OFFLINE` | Skip LLM calls (use stubs) |
| `REGISTRY_USE_STUB_LLM` | Use stub LLM for registry |
| `PROCSUITE_SKIP_WARMUP` | Skip model warmup |

## Dependencies

### External Services
- **Gemini API** - LLM for code suggestion and extraction
- **spaCy** - NLP for entity extraction

### Key Libraries
- FastAPI - Web framework
- Pydantic - Data validation
- scikit-learn - ML models
- Jinja2 - Report templating

## Testing Strategy

### Test Organization
```
tests/
├── coder/           # CodingService tests
├── registry/        # RegistryService tests
├── ml_coder/        # ML predictor tests
├── agents/          # Agent pipeline tests
└── api/             # API endpoint tests
```

### Test Categories
- **Unit tests** - Individual function testing
- **Integration tests** - Service-level testing
- **Contract tests** - Schema validation
- **Validation tests** - Ground truth comparison

### Running Tests
```bash
make test                           # All tests
pytest tests/coder/ -v              # Coder only
pytest tests/registry/ -v           # Registry only
make validate-registry              # Registry validation
```

---

*Last updated: December 2025*
```

---
### `docs/INSTALLATION.md`
```
# Installation & Setup Guide

This guide covers setting up the Procedure Suite environment, including Python dependencies, spaCy models, and Gemini API configuration.

## 1. Prerequisites

- **Python 3.11+** (Required: `>=3.11,<3.14`)
- **micromamba** or **conda** (Recommended for environment management)
- **Git**

## 2. Environment Setup

### Create Python Environment

Using `micromamba` (recommended) or `conda`:

```bash
# Create environment
micromamba create -n medparse-py311 python=3.11
micromamba activate medparse-py311
```

### Install Dependencies

Install the project in editable mode along with API and dev dependencies:

```bash
make install
# Or manually: pip install -e ".[api,dev]"
```

### Install spaCy Models

The project requires specific spaCy models for NLP tasks:

```bash
# Install scispaCy model (Required - may take a few minutes)
pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.4/en_core_sci_sm-0.5.4.tar.gz

# Install standard spaCy model
python -m spacy download en_core_web_sm
```

## 3. Configuration (.env)

Create a `.env` file in the project root to store configuration and secrets:

```bash
touch .env
```

### Gemini API Configuration (Required for Extraction)

The system uses Google's Gemini models for registry extraction.

**Option 1: API Key (Simpler)**
Get your key from [Google AI Studio](https://aistudio.google.com/app/apikey).

```bash
GEMINI_API_KEY=your-api-key-here
GEMINI_MODEL=gemini-2.5-flash-lite  # Optional: Override default model
```

**Option 2: OAuth2 / Service Account (For Cloud Subscriptions)**
If running on GCP or using a service account:

```bash
GEMINI_USE_OAUTH=true
# Optional: Path to service account JSON if not using default credentials
# GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

### Other Settings

```bash
# Enable LLM Advisor for Coder (Optional)
CODER_USE_LLM_ADVISOR=1

# Supabase Integration (Optional - for DB export)
# SUPABASE_DB_URL=postgresql://postgres:password@db.xxx.supabase.co:5432/postgres
```

## 4. Verification

Run the preflight check to validate your setup:

```bash
make preflight
```

This script checks:
- ✅ Python version
- ✅ Installed dependencies (including `sklearn` version)
- ✅ spaCy models
- ✅ Configuration validity

## 5. Running Tests (Offline vs Online)

By default, tests run in **offline mode** using a stub LLM to avoid API costs and network dependency.

### Offline Mode (Default)
```bash
pytest -q
```

### Online Mode (Live API)
To test with the real Gemini API:

```bash
# Override default offline flags
export GEMINI_OFFLINE=0
export REGISTRY_USE_STUB_LLM=0
export GEMINI_API_KEY="your-key"

pytest -q
```

## 6. Starting the API Server

To run the FastAPI backend locally:

```bash
make api
# Or: ./scripts/devserver.sh
```

The API will be available at `http://localhost:8000`.
Docs: `http://localhost:8000/docs`
```

---
### `docs/USER_GUIDE.md`
```
# Procedure Suite - User Guide

This guide explains how to use the Procedure Suite tools for generating reports, coding procedures, and validating registry data.

---

## How the System Works (Plain Language)

The Procedure Suite is an intelligent medical coding assistant that reads procedure notes and suggests appropriate CPT billing codes. Here's how it works in simple terms:

### The Three Brains

1. **Machine Learning (ML) Model**: A trained neural network that has learned from thousands of procedure notes. It quickly predicts which CPT codes are likely correct and assigns a confidence score to each prediction.

2. **Rules Engine**: A set of explicit business rules that encode medical billing knowledge, such as:
   - "You can't bill these two codes together" (bundling rules)
   - "This code requires specific documentation" (validation rules)
   - "If procedure X was done, code Y is required" (inference rules)

3. **LLM Advisor**: A large language model (like GPT/Gemini) that can read and understand procedure notes in natural language. It acts as a "second opinion" when the ML model is uncertain.

### The ML-First Hybrid Pipeline (NEW)

The system uses a smart decision-making process called the **SmartHybridOrchestrator**:

```
Note Text → ML Predicts → Classify Difficulty → Decision Gate → Final Codes
                              ↓
            HIGH_CONF: ML + Rules (fast path, no LLM)
            GRAY_ZONE: LLM as judge (ML provides hints)
            LOW_CONF:  LLM as primary coder
```

**Step-by-step:**

1. **ML Prediction**: The ML model reads the note and predicts CPT codes with confidence scores.

2. **Difficulty Classification**: Based on confidence scores, the case is classified:
   - **HIGH_CONF** (High Confidence): ML is very sure about the codes
   - **GRAY_ZONE**: ML sees multiple possibilities, needs help
   - **LOW_CONF** (Low Confidence): ML is unsure, note may be unusual

3. **Decision Gate**:
   - If HIGH_CONF and rules pass → Use ML codes directly (fast, cheap, no LLM call)
   - If GRAY_ZONE or rules fail → Ask LLM to make the final decision
   - If LOW_CONF → Let LLM be the primary coder

4. **Rules Validation**: Final codes always pass through rules engine for safety checks

This approach is **faster** (43% of cases skip LLM entirely) and **more accurate** (ML catches patterns, LLM handles edge cases).

---

## 🚀 Quick Start: The Dev Server

The easiest way to interact with the system is the development server, which provides a web UI and API documentation.

```bash
./scripts/devserver.sh
```
*Starts the server on port 8000.*

- **Web UI**: [http://localhost:8000/ui/](http://localhost:8000/ui/)
- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🛠 CLI Tools

The suite includes several command-line scripts for batch processing and validation.

### 1. Validate Registry Extraction
Run the extraction pipeline on synthetic notes and compare against ground truth.

```bash
make validate-registry
```
*Output*: `reports/registry_validation_output.txt` and `data/registry_errors.jsonl`

### 2. Evaluate CPT Coder
Test the CPT coding engine against the training dataset.

```bash
python scripts/evaluate_cpt.py
```
*Output*: Accuracy metrics and error logs in `data/cpt_errors.jsonl`.

### 3. Self-Correction (LLM)
Ask the LLM to analyze specific registry fields or errors and suggest improvements.

```bash
# Analyze errors for a specific field
make self-correct-registry FIELD=sedation_type
```
*Output*: `reports/registry_self_correction_sedation_type.md`

### 4. Clean & Normalize Registry
Run the full cleaning pipeline (Schema Norm -> CPT Logic -> Consistency -> Clinical QC) on a raw dataset.

```bash
python scripts/clean_ip_registry.py \
  --registry-data data/samples/my_registry_dump.jsonl \
  --output-json reports/cleaned_registry_data.json \
  --issues-log reports/issues_log.csv
```

---

## 🔌 API Usage

You can interact with the system programmatically via the REST API.

### CPT Coding Endpoint
**POST** `/v1/coder/run`

Input:
```json
{
  "note": "Bronchoscopy with EBUS at station 7.",
  "locality": "00",
  "setting": "facility"
}
```

Output:
```json
{
  "codes": [
    {
      "cpt": "31652",
      "description": "Bronchoscopy w/ EBUS 1-2 stations",
      "confidence": 0.95
    }
  ],
  "financials": {
    "total_work_rvu": 4.46
  }
}
```

### Registry Extraction Endpoint
**POST** `/v1/registry/run`

Input:
```json
{
  "note": "Patient is a 65yo male..."
}
```

Output:
```json
{
  "record": {
    "patient_age": 65,
    "gender": "M",
    "cpt_codes": [...]
  }
}
```

---

## 📊 Key Files

- **`data/knowledge/ip_coding_billing_v2_8.json`**: The "Brain". Contains all CPT codes, RVUs, and bundling rules.
- **`schemas/IP_Registry.json`**: The "Law". Defines the valid structure for registry data.
- **`reports/`**: Where output logs and validation summaries are saved.

---

## 🖥️ Using the Web UI (Unicorn Frontend)

The Web UI provides a simple interface for coding procedure notes.

### Basic Usage

1. **Start the server**: `./scripts/devserver.sh`
2. **Open the UI**: Navigate to [http://localhost:8000/ui/](http://localhost:8000/ui/)
3. **Select "Coder" tab** (default)
4. **Paste your procedure note** into the text area
5. **Configure options**:
   - **Use ML-First Pipeline** (recommended): Enables the smart hybrid pipeline
   - **Locality**: Geographic code for RVU calculations (default: 00 = National)
   - **Setting**: Facility or Non-Facility pricing
6. **Click "Run Processing"**

### Understanding the Results

When using the ML-First Pipeline, you'll see:

- **Pipeline Metadata** (colored badges):
  - **Difficulty**: green (high_confidence), yellow (gray_zone), red (low_confidence)
  - **Source**: green (ml_rules_fastpath) means no LLM was used, blue (hybrid_llm_fallback) means LLM was consulted
  - **LLM Used**: green (No) or yellow (Yes)

- **Billing Codes**: The final CPT codes with descriptions

- **RVU & Payment**: Work RVUs and estimated Medicare payment

---

## ➕ Adding New Training Cases

To improve the ML model's accuracy, you can add new training cases. Here's how:

### Step 1: Prepare Your Data

Create a JSONL file with your cases. Each line should be a JSON object with:

```json
{
  "note": "Your procedure note text here...",
  "cpt_codes": ["31622", "31628"],
  "dataset": "my_new_cases"
}
```

**Required fields:**
- `note`: The full procedure note text
- `cpt_codes`: List of correct CPT codes for this note

**Optional fields:**
- `dataset`: A label for grouping (e.g., "bronchoscopy", "pleural")
- `procedure_type`: The type of procedure (auto-detected if not provided)

### Step 2: Add Cases to Training Data

Place your JSONL file in the training data directory:

```bash
# Copy your cases to the training data folder
cp my_new_cases.jsonl data/training/
```

### Step 3: Validate Your Cases

Before training, validate that your cases are properly formatted:

```bash
python scripts/validate_training_data.py data/training/my_new_cases.jsonl
```

### Step 4: Retrain the Model (Optional)

If you have enough new cases (50+), you can retrain the ML model:

```bash
# Run the training pipeline
python scripts/train_ml_coder.py --include data/training/my_new_cases.jsonl
```

### Tips for Good Training Data

1. **Diverse examples**: Include various procedure types and complexity levels
2. **Accurate labels**: Double-check the CPT codes are correct
3. **Representative notes**: Use real-world note formats and writing styles
4. **Edge cases**: Include tricky cases where coding is non-obvious
5. **Clean text**: Remove any PHI (patient identifying information)

---

## 🔍 Reviewing Errors

When the system makes mistakes, you can review them to improve future performance.

### Run the Error Review Script

```bash
# Review all errors
python scripts/review_llm_fallback_errors.py --mode all

# Review only fast path errors (ML+Rules mistakes)
python scripts/review_llm_fallback_errors.py --mode fastpath

# Review only LLM fallback errors
python scripts/review_llm_fallback_errors.py --mode llm_fallback
```

This generates a markdown report in `data/eval_results/` with:
- Error patterns and common mistakes
- Per-case review with recommendations
- Codes that were incorrectly predicted or missed

### Using Error Analysis to Improve the System

1. **False Positives** (codes predicted but shouldn't be):
   - May need to add negative rules to the rules engine
   - May need more training examples without these codes

2. **False Negatives** (codes missed):
   - May need to add new keyword patterns
   - May need more training examples with these codes

3. **ML was correct but LLM overrode it**:
   - Consider adjusting confidence thresholds
   - May need to improve LLM prompt constraints

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PROCSUITE_SKIP_WARMUP` | Skip NLP model loading at startup | `false` |
| `CODER_REQUIRE_PHI_REVIEW` | Require PHI review before coding | `false` |
| `DEMO_MODE` | Enable demo mode (synthetic data only) | `false` |

### Adjusting ML Thresholds

The ML model's confidence thresholds can be tuned in `modules/ml_coder/thresholds.py`:

```python
# High confidence threshold (codes above this are HIGH_CONF)
HIGH_CONF_THRESHOLD = 0.80

# Gray zone lower bound (codes between this and HIGH_CONF are GRAY_ZONE)
GRAY_ZONE_THRESHOLD = 0.45

# Codes below GRAY_ZONE_THRESHOLD are LOW_CONF
```

Higher thresholds = more cases go to LLM (safer but slower)
Lower thresholds = more cases use fast path (faster but may miss edge cases)

---

## 📞 Getting Help

- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Technical Issues**: Check the logs in `logs/` directory
- **Questions**: Open an issue on the repository

---

*Last updated: December 2025*
```
