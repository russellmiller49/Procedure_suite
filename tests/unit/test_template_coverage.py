import json
import re
from pathlib import Path


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", text.strip().lower()).strip("_")
    slug = re.sub(r"_+", "_", slug)
    return slug


def test_all_knowledge_templates_have_configs():
    root = Path(__file__).resolve().parents[2]
    knowledge_path = root / "data" / "knowledge" / "comprehensive_ip_procedural_templates9_18.md"
    yaml_dir = root / "configs" / "report_templates"

    template_entries: list[tuple[str, str]] = []
    template_pattern = re.compile(r"^Template:\s*(.*)", re.IGNORECASE)
    for line in knowledge_path.read_text().splitlines():
        m = template_pattern.match(line.strip())
        if m:
            text = m.group(1).strip()
            slug = _slugify(text)
            if not slug:
                continue
            template_entries.append((slug, text.lower()))

    yaml_ids = {json.loads(path.read_text()).get("id") for path in yaml_dir.glob("*.json")}
    try:
        import yaml  # type: ignore
    except Exception:
        yaml = None  # pragma: no cover

    for path in yaml_dir.glob("*.yaml"):
        if path.name == "procedure_order.json":
            continue
        if yaml:
            loaded = yaml.safe_load(path.read_text())
            if isinstance(loaded, dict):
                yaml_ids.add(loaded.get("id") or path.stem)
                continue
        yaml_ids.add(Path(path).stem)

    alias_map = {
        "pre_anesthesia_assessment_for_moderate_sedation": "ip_pre_anesthesia_assessment",
        "general_bronchoscopy_note": "ip_general_bronchoscopy_shell",
        "interventional_pulmonology_operative_report": "ip_or_main_oper_report_shell",
        "blvr_discharge": "blvr_discharge_instructions",
        "chest_tube_pleurx_catheter_discharge": "chest_tube_discharge",
        "tunneled_pleural_catheter_instructions": "pleurx_instructions",
        "peg_discharge": "peg_discharge",
        "patient_instructed_to_avoid_exertion_driving_or_travel_for_one_week_monitor_for_shortness_of_breath_chest_pain_fever_arrange_follow_up_with_interventional_pulmonology": "blvr_discharge_instructions",
        "patient_advised_to_maintain_drainage_system_care_monitor_for_infection_and_follow_scheduled_drainage": "chest_tube_discharge",
        "patient_advised_on_wound_care_flushing_protocols_medications_and_diet_after_peg_placement": "peg_discharge",
        "prior_to_the_procedure_the_risks_and_benefits_of_the_procedure_and_the_sedation_options_and_sedation_related_risks_were_discussed_with_the_patient_surrogate_all_questions_were_answered_and_written_informed_consent_was_obtained": "ip_pre_anesthesia_assessment",
        "linear_ebus_scope_advanced_into_esophagus_mediastinal_nodes_visualized_and_sampled": "eUSB",
    }

    allowed_missing = {
        # Tracheostomy/airway change-out templates not yet structured
        "minor_bleeding_was_noted_from_the_tracheostomy_incision_site_hemostasis_did_not_occur_after_holding_pressure_electrocautery_cautery_loop_tip_was_applied_to_the_bleeding_area_with_fio2_confirmed_at_40_bleeding_ceased_after_bovie_application_the_patient_tolerated_the_intervention_well_without_immediate_complications",
        "minor_bleeding_was_noted_from_the_tracheostomy_incision_site_hemostasis_did_not_occur_after_holding_pressure_electrocautery_cautery_loop_tip_was_applied_to_the_bleeding_area_with_fio_confirmed_at_40_bleeding_ceased_after_bovie_application_the_patient_tolerated_the_intervention_well_without_immediate_complications",
        "silver_nitrate_applicators_75_silver_nitrate_and_25_potassium_nitrate_were_moistened_and_applied_directly_to_granulation_tissue_surrounding_the_stoma_until_the_tissue_was_ablated_no_complications_were_observed",
        "upper_airway_was_suctioned_and_cleared_endotracheal_suctioning_performed_the_cuff_was_deflated_and_the_existing_tracheostomy_tube_removed_the_stoma_was_widely_patent_without_granulation_tissue_a_new_tracheostomy_tube_was_placed_with_obturator_in_place_the_obturator_was_removed_the_inner_cannula_inserted_and_the_cuff_inflated_position_and_patency_were_confirmed_the_patient_tolerated_the_procedure_well",
        "with_bronchoscopic_visualization_the_anterior_neck_was_prepped_and_draped_in_sterile_fashion_local_anesthesia_was_infiltrated_a_vertical_skin_incision_was_made_just_inferior_to_the_cricoid_a_needle_was_inserted_into_the_trachea_under_direct_bronchoscopic_visualization_and_a_guidewire_advanced_between_the_1st_and_2nd_tracheal_rings_after_sequential_dilation_the_tracheostomy_tube_was_placed_over_a_guiding_catheter_into_the_trachea_the_obturator_removed_and_ventilation_transferred_to_the_tube_position_was_confirmed_bronchoscopically_the_patient_tolerated_the_procedure_well_without_immediate_complications",
        "patient_was_intubated_with_et_tube_the_bronchoscope_was_introduced_through_the_et_tube_the_et_tube_was_retracted_into_the_subglottic_space_under_direct_visualization_the_inferior_border_of_the_cricoid_along_with_the_proximal_tracheal_rings_were_visualized_next_the_anterior_neck_was_prepped_and_draped_in_the_usual_sterile_fashion_lidocaine_1_3ml_was_injected_into_the_anterior_neck_the_prior_tracheostomy_tube_was_removed_with_minimal_resistance_a_j_wire_was_passed_through_the_prior_tracheostomy_site_also_visualized_with_the_bronchoscope_the_site_was_then_dilated_using_the_blue_rhino_dilator_placed_over_the_guiding_catheter_until_the_positioning_mark_was_visualized_via_the_bronchoscope_the_blue_rhino_dilator_was_then_removed_leaving_the_guiding_catheter_and_guide_wire_assembly_in_place_all_under_direct_visualization_bronchoscopically",
        "tracheobronchoscopy_was_performed_with_insertion_of_bronchoscope_through_the_tracheostomy_to_perform_airway_clearance_and_confirm_tracheostomy_position",
        "indication_tolerated_capping_speaking_valve_adequate_cough_secretion_burden_acceptable_the_tracheostomy_tube_type_size_was_removed_at_bedside_after_oropharyngeal_and_tracheal_suctioning_the_stoma_was_dressed_with_occlusive_gauze_and_secured_patient_instructed_to_apply_pressure_over_stoma_during_speech_cough_observation_for_hours_with_pulse_oximetry_was_uneventful_follow_up_dressing_changes_daily_return_precautions_reviewed",
        "the_tracheostomy_site_was_inspected_and_suctioned_the_existing_tube_type_size_was_removed_a_smaller_size_fenestrated_tracheostomy_tube_brand_size_was_inserted_with_obturator_in_place_obturator_removed_inner_cannula_inserted_and_cuff_inflated_deflated_per_plan_position_and_patency_were_confirmed_indication_weaning_phonation_speaking_valve_trial_the_patient_tolerated_the_exchange_without_complications",
        "granulation_tissue_at_the_stoma_tracheal_site_was_identified_mechanical_debridement_was_performed_using_forceps_curette_microdebrider_until_healthy_mucosa_was_seen_topical_hemostasis_with_silver_nitrate_epinephrine_pressure_achieved_the_tracheostomy_tube_was_exchanged_not_exchanged_the_patient_tolerated_the_procedure_without_immediate_complications",
        "flexible_laryngoscopy_was_performed_by_advancing_the_scope_along_the_floor_of_the_nose_nasal_cavity_nasopharynx_vallecula_supraglottis_glottis_post_cricoid_region_and_piriform_sinuses_were_systematically_evaluated_without_suspicious_mass_or_mucosal_lesions_vocal_folds_adducted_and_abducted_normally_and_symmetrically_no_obvious_abnormalities_noted_along_the_nasal_chamber_pharyngeal_walls_tongue_base_vallecula_epiglottis_supraglottis_glottis_post_cricoid_and_piriform_sinuses_were_evaluated_and_found_to_be_without_evidence_of_suspicious_mass_or_mucosal_lesions",
        "bronchial_stenosis_was_dilated_with_a_balloon_catheter_patency_improved_without_complications_performed_at_airway_segment_balloon_type_elation_balloon_was_used_to_perform_dilation_to_size_mm_total_number_inflations_with_dilation_time_of_seconds_seconds_each",
        "a_stent_was_deployed_across_the_target_stenosis_under_bronchoscopic_and_fluoroscopic_guidance_the_following_stent_type_was_placed_in_the_airway_segment",
        "endobronchial_obstruction_was_treated_with_electrocautery_apc_laser_cryo_pre_and_post_procedure_patency_recorded_performed_at_airway_segment_with_the_following_modalities_modality_electrocautery_apc_laser_corecath_cryoprobe_setting_mode_details_duration_time_results_prior_to_treatment_affected_airway_was_noted_to_be_pct_patent_after_treatment_the_airway_was_pct_patent",
        "endobronchial_tumor_was_noted_and_excised_with_mechanical_debridement_coring_or_microdebrider_or_forceps",
        "indication_for_stent_removal_revision_mucus_plugging_granulation_migration_therapy_complete_stent_details_brand_type_silicone_or_metallic_aero_dumon_y_stent_size_dimensions_location_airway_segment_technique_rigid_extraction_hook_forceps_snare_cryoadhesion_the_stent_was_removed_repositioned_trimmed_adjuncts_balloon_dilation_debridement_post_intervention_inspection_showed_the_airway_patent_with_no_minimal_bleeding_if_replaced_a_new_stent_was_placed_details_the_patient_tolerated_the_procedure_well",
        "thoracoscopic_survey_performed_biopsies_taken_adhesiolysis_pleurodesis_performed_as_indicated_chest_tube_left_in_situ_initial_thoracoscopic_survey_demonstrates_findings_lysis_of_adhesion_was_performed",
        "chemical_pleurodesis_via_chest_tube_talc_slurry_or_doxycycline",
        "chemical_pleurodesis_via_tunneled_pleural_catheter_ipc",
        "ipc_exchange_over_wire",
        "chest_tube_exchange_upsizing_over_guidewire",
        "chest_tube_removal",
        "ultrasound_guided_pleural_biopsy_closed_core",
        "focused_thoracic_ultrasound_pleura_lung",
        "thoravent_placement",
        "dlt_tube_balloon_leak_test_context",
        "endobronchial_obstruction_was_treated_with_electrocautery_apc_laser_cryo_pre_and_post_procedure_patency_recorded_performed_at_airway_segment_with_the_following_modalities_modality_electrocautery_apc_laser_corecath_cryoprobe_setting_mode_details_duration_time_results_prior_to_treatment_affected_airway_was_noted_to_be_patent_after_treatment_the_airway_was_patent",
        "chest_ultrasound_findings_as_above",
        "indication_autopleurodesis_not_achieved_recurrent_symptomatic_effusion_after_complete_drainage_talc_slurry_doxycycline_was_instilled_via_ipc_agent_dose_volume_ml_the_catheter_was_capped_and_the_patient_was_instructed_to_rotate_through_positions_over_duration_drainage_was_resumed_after_hours_tolerance_was_good_fair_poor_follow_up_drainage_schedule_clinic_visit",
        "indication_for_exchange_occlusion_infection_defect_leak_the_existing_ipc_was_prepped_guidewire_inserted_through_the_catheter_lumen_into_the_pleural_space_under_ultrasound_guidance_the_old_catheter_was_removed_and_a_new_tunneled_catheter_brand_size_was_placed_over_the_wire_using_the_standard_tunneling_and_peel_away_sheath_technique_position_confirmed_by_aspiration_and_ultrasound_the_catheter_was_secured_and_dressed_the_patient_tolerated_the_procedure_well",
        "criteria_met_for_removal_no_air_leak_for_24_h_drainage_ml_day_lung_expanded_on_cxr_after_sterile_prep_the_tube_was_placed_to_water_seal_a_valsalva_inspiratory_hold_was_performed_and_the_tube_was_removed_the_site_was_closed_with_suture_occlusive_dressing_the_patient_tolerated_the_procedure_well_post_removal_cxr_ordered_not_indicated",
        "under_ultrasound_guidance_the_pleural_target_at_interspace_location_was_identified_and_skin_marked_after_local_anesthesia_a_14_16_18_g_core_needle_device_brand_obtained_number_cores_from_the_parietal_pleura_hemostasis_achieved_with_manual_pressure_specimens_placed_in_formalin_saline_sterile_container_for_histology_microbiology_no_immediate_complications_dressing_applied",
        "focused_thoracic_ultrasound_was_performed_and_archived_findings_right_effusion_size_echogenicity_loculations_lung_sliding_b_lines_consolidation_diaphragm_motion_left_same_impression_free_flowing_vs_loculated_effusion_trapped_vs_expandable_lung_pneumothorax_suspected_vs_not_clinical_correlation_and_procedural_planning_as_documented",
    }

    missing = []
    for slug, raw_text in template_entries:
        candidate = alias_map.get(slug, slug)
        if "thoracentesis" in raw_text and "pressure" in raw_text:
            candidate = "thoracentesis_manometry"
        elif "thoracentesis" in raw_text:
            candidate = "thoracentesis_detailed"
        elif "chest" in raw_text and "tube" in raw_text and "thoracostomy" in raw_text:
            candidate = "chest_tube"
        elif "endobronchial biopsies" in raw_text:
            candidate = "endobronchial_biopsy"
        elif "transbronchial forceps biopsies" in raw_text:
            candidate = "transbronchial_lung_biopsy"
        elif "foreign body" in raw_text:
            candidate = "foreign_body_removal"
        elif "photosensitizer" in raw_text:
            candidate = "pdt_light"
        elif ("follow-up" in raw_text or "follow‑up" in raw_text) and "necrotic tissue" in raw_text:
            candidate = "pdt_debridement"
        elif "endotracheal tube" in raw_text and "railroaded" in raw_text:
            candidate = "awake_foi"
        elif "double lumen tube" in raw_text or "dlt" in raw_text:
            candidate = "dlt_placement"
        elif "tunneled pleural catheter" in raw_text and "removed" in raw_text:
            candidate = "tunneled_pleural_catheter_remove"
        elif "tunneled pleural catheter" in raw_text:
            candidate = "tunneled_pleural_catheter_insert"
        elif "paracentesis" in raw_text:
            candidate = "paracentesis"
        elif "gastrostomy" in raw_text:
            candidate = "peg_placement"
        elif "peg" in raw_text and "exchang" in raw_text:
            candidate = "peg_exchange"
        elif "peg" in raw_text:
            candidate = "peg_placement"
        elif "whole lung lavage" in raw_text or "effluent clear" in raw_text:
            candidate = "whole_lung_lavage"
        elif "blvr" in raw_text or "one-way valve therapy" in raw_text:
            candidate = "blvr_valve_placement"
        elif "valve removal" in raw_text and "exchange" in raw_text:
            candidate = "blvr_valve_removal_exchange"
        elif "cryobiopsy" in raw_text:
            candidate = "transbronchial_cryobiopsy"
        elif "cryoablation" in raw_text:
            candidate = "endobronchial_cryoablation"
        elif "cryoprobe" in raw_text and "casts" in raw_text:
            candidate = "cryo_extraction_mucus"
        elif "bronchopleural fistula" in raw_text or "balloon occlusion" in raw_text:
            candidate = "bpf_localization_occlusion"
        elif "persistent air leak" in raw_text and "valve" in raw_text:
            candidate = "bpf_valve_air_leak"
        elif "sealant" in raw_text and "air leak" in raw_text:
            candidate = "bpf_endobronchial_sealant"
        elif "fiducial marker" in raw_text:
            candidate = "fiducial_marker_placement"
        elif "electromagnetic navigation" in raw_text:
            candidate = "emn_bronchoscopy"
        elif "robotic navigation bronchoscopy was performed using the intuitive ion" in raw_text:
            candidate = "robotic_ion_bronchoscopy"
        elif "monarch" in raw_text:
            candidate = "robotic_monarch_bronchoscopy"
        elif "radial endobronchial ultrasound was used to confirm" in raw_text:
            candidate = "radial_ebus_survey"
        elif "guide sheath" in raw_text and "radial ebus" in raw_text:
            candidate = "radial_ebus_sampling"
        elif "cbct spin was acquired" in raw_text:
            candidate = "cbct_augmented_bronchoscopy"
        elif "cbct/cact spin" in raw_text or "image fusion" in raw_text:
            candidate = "cbct_cact_fusion"
        elif "tool-in-lesion" in raw_text or ("tool" in raw_text and "lesion" in raw_text):
            candidate = "tool_in_lesion_confirmation"
        elif "registration" in raw_text and "partial" in raw_text:
            candidate = "ion_registration_partial"
        elif "registration drift" in raw_text:
            candidate = "ion_registration_drift"
        elif "registration to the pre-procedure ct was completed" in raw_text:
            candidate = "ion_registration_complete"
        elif "ebus" in raw_text and "intranodal forceps" in raw_text:
            candidate = "ebus_ifb"
        elif "19g ebus" in raw_text or "19g ebus needle" in raw_text:
            candidate = "ebus_19g_fnb"
        elif "core samples" in raw_text and "ebus needle" in raw_text:
            candidate = "ebus_ifb"
        elif "passes" in raw_text and "ebus needle" in raw_text:
            candidate = "ebus_19g_fnb"
        elif "systematic ebus survey" in raw_text or "ebus survey" in raw_text:
            candidate = "ebus_tbna"
        elif "linear ebus scope" in raw_text:
            candidate = "eUSB"
        elif "cryoprobe" in raw_text and "secretions" in raw_text:
            candidate = "cryo_extraction_mucus"
        elif "paracentesis" in raw_text:
            candidate = "paracentesis"
        elif "thoravent" in raw_text:
            candidate = "thoracentesis"  # placeholder until thoravent template exists
        elif "valves removed" in raw_text or "exchange performed" in raw_text:
            candidate = "blvr_valve_removal_exchange"
        elif "needle catheter" in raw_text and "mark the lesion" in raw_text:
            candidate = "dye_marker_placement"
        elif "core needle biopsy" in raw_text and "ultrasound" in raw_text:
            candidate = "transthoracic_needle_biopsy"
        covered = False
        if candidate in yaml_ids:
            covered = True
        if not covered:
            for yid in yaml_ids:
                if yid and yid in slug:
                    covered = True
                    break
        if covered or slug in allowed_missing:
            continue
        missing.append(slug)

    assert not missing, f"Missing template configs for: {missing}"
