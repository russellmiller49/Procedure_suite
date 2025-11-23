import pytest

from proc_report import (
    AnesthesiaInfo,
    EncounterInfo,
    PatientInfo,
    ProcedureBundle,
    ProcedureInput,
    SedationInfo,
    build_procedure_bundle_from_extraction,
    compose_structured_report,
)


def _bronch_and_pleural_bundle() -> ProcedureBundle:
    return ProcedureBundle(
        patient=PatientInfo(name="Jane Doe", age=58, sex="female"),
        encounter=EncounterInfo(
            date="2024-09-18",
            referred_physician="Dr. Referral",
            attending="Dr. Attending",
            assistant="Dr. Fellow",
        ),
        procedures=[
            ProcedureInput(
                proc_type="bronchoscopy_core",
                schema_id="bronchoscopy_shell_v1",
                data={
                    "airway_overview": "Systematic airway survey completed without obstruction.",
                    "right_lung_overview": "Clear to subsegmental bronchi.",
                    "left_lung_overview": "Clear with no secretions.",
                },
                cpt_candidates=["31622"],
            ),
            ProcedureInput(
                proc_type="bal",
                schema_id="bal_v1",
                data={
                    "lung_segment": "RML medial segment",
                    "instilled_volume_cc": 90,
                    "returned_volume_cc": 50,
                    "tests": ["cell count", "microbiology culture"],
                },
                cpt_candidates=["31624"],
            ),
            ProcedureInput(
                proc_type="thoracentesis",
                schema_id="thoracentesis_v1",
                data={
                    "side": "left",
                    "effusion_size": "moderate",
                    "effusion_echogenicity": "anechoic",
                    "loculations": None,
                    "intercostal_space": "7th",
                    "entry_location": "mid-axillary",
                    "volume_removed_ml": 1200,
                    "fluid_appearance": "serous",
                    "specimen_tests": ["cell count", "chemistries"],
                    "cxr_ordered": True,
                },
                cpt_candidates=["32555"],
            ),
        ],
        sedation=SedationInfo(type="Moderate", description="Moderate sedation with fentanyl and midazolam"),
        anesthesia=AnesthesiaInfo(type="Moderate", description="Topical + IV moderate sedation"),
        pre_anesthesia={
            "asa_status": "ASA II",
            "anesthesia_plan": "Moderate sedation with continuous monitoring",
            "prophylactic_antibiotics": False,
            "anticoagulant_use": "",
            "time_out_confirmed": True,
        },
        indication_text="dyspnea and pleural effusion",
        preop_diagnosis_text="Pleural effusion",
        postop_diagnosis_text="Pleural effusion, status post thoracentesis",
        impression_plan="Observation and follow-up as needed.",
        specimens_text="BAL for microbiology; pleural fluid for chemistry",
        estimated_blood_loss="Minimal",
    )


def test_structured_reporter_renders_templates_cleanly():
    bundle = _bronch_and_pleural_bundle()
    note = compose_structured_report(bundle)

    assert "INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT" in note
    assert "Thoracentesis was performed on the left hemithorax" in note
    assert "Bronchoalveolar lavage was performed in the RML medial segment" in note
    assert "[" not in note
    assert "None mL" not in note


def test_structured_reporter_enforces_required_fields():
    bundle = _bronch_and_pleural_bundle()
    bundle.procedures[-1] = ProcedureInput(
        proc_type="thoracentesis",
        schema_id="thoracentesis_v1",
        data={
            "side": "right",
            "effusion_size": "small",
            "effusion_echogenicity": "anechoic",
            # Missing volume_removed_ml on purpose
            "intercostal_space": "8th",
            "entry_location": "mid-scapular",
            "fluid_appearance": "serous",
            "specimen_tests": ["protein", "LDH"],
        },
    )

    with pytest.raises(ValueError):
        compose_structured_report(bundle)


def test_bronchial_washing_template():
    bundle = ProcedureBundle(
        patient=PatientInfo(name="Alex Roe", age=45, sex="male"),
        encounter=EncounterInfo(date="2024-09-18", attending="Dr. Attending"),
        procedures=[
            ProcedureInput(
                proc_type="bronchial_washing",
                schema_id="bronchial_washing_v1",
                data={
                    "airway_segment": "RLL",
                    "instilled_volume_ml": 30,
                    "returned_volume_ml": 20,
                    "tests": ["cytology", "culture"],
                },
            )
        ],
    )
    note = compose_structured_report(bundle)
    assert "Bronchial washing was performed" in note
    assert "30 mL" in note
    assert "{{" not in note
    assert "None mL" not in note


def test_chest_tube_template():
    bundle = ProcedureBundle(
        patient=PatientInfo(),
        encounter=EncounterInfo(),
        procedures=[
            ProcedureInput(
                proc_type="chest_tube",
                schema_id="chest_tube_v1",
                data={
                    "side": "right",
                    "intercostal_space": "6th",
                    "entry_line": "mid-axillary",
                    "guidance": "Ultrasound",
                    "fluid_removed_ml": 500,
                    "fluid_appearance": "serosanguinous",
                    "cxr_ordered": True,
                },
            )
        ],
    )
    note = compose_structured_report(bundle)
    assert "thoracostomy tube was inserted" in note
    assert "6th intercostal space" in note
    assert "500 mL" in note
    assert "{{" not in note
    assert "None mL" not in note


def test_end_to_end_from_extraction_bundle():
    extraction = {
        "patient_age": 63,
        "gender": "female",
        "procedure_date": "2024-09-18",
        "attending_name": "Dr. Attending",
        "sedation_type": "Moderate",
        "cpt_codes": [31622, 31624, 32555],
        "procedures": [
            {
                "proc_type": "bronchoscopy_core",
                "schema_id": "bronchoscopy_shell_v1",
                "data": {
                    "airway_overview": "Systematic airway survey completed.",
                    "right_lung_overview": "Patent to subsegmental bronchi.",
                    "left_lung_overview": "No obstruction.",
                },
            },
            {
                "proc_type": "bal",
                "schema_id": "bal_v1",
                "data": {
                    "lung_segment": "RML medial segment",
                    "instilled_volume_cc": 80,
                    "returned_volume_cc": 45,
                    "tests": ["cell count", "culture"],
                },
            },
            {
                "proc_type": "bronchial_washing",
                "schema_id": "bronchial_washing_v1",
                "data": {
                    "airway_segment": "RML",
                    "instilled_volume_ml": 20,
                    "returned_volume_ml": 15,
                    "tests": ["cytology"],
                },
            },
        ],
        "pleural_procedure_type": "Thoracentesis",
        "pleural_guidance": "Ultrasound",
        "pleural_volume_drained_ml": 900,
        "pleural_fluid_appearance": "Serous",
        "pleural_opening_pressure_measured": True,
        "pleural_opening_pressure_cmh2o": -6,
        "intercostal_space": "7th",
        "entry_location": "mid-axillary",
        "specimen_tests": ["cell count", "chemistry"],
        "pleural_effusion_volume": "Moderate",
        "pleural_echogenicity": "Anechoic",
    }

    bundle = build_procedure_bundle_from_extraction(extraction)
    note = compose_structured_report(bundle)

    assert "Bronchial washing was performed" in note
    assert "Bronchoalveolar lavage" in note
    assert "Thoracentesis" in note
    assert "{{" not in note
    assert "None mL" not in note


def test_navigation_ebus_blvr_multi_procedure():
    bundle = ProcedureBundle(
        patient=PatientInfo(name="Jamie Smith", age=67, sex="female"),
        encounter=EncounterInfo(
            date="2024-09-18",
            attending="Dr. Navigator",
            assistant="Dr. Fellow",
        ),
        procedures=[
            ProcedureInput(
                proc_type="bronchoscopy_core",
                schema_id="bronchoscopy_shell_v1",
                data={
                    "airway_overview": "Airway survey completed without obstruction.",
                    "right_lung_overview": "Clear to subsegmental bronchi.",
                    "left_lung_overview": "No endobronchial lesions.",
                },
            ),
            ProcedureInput(
                proc_type="robotic_ion_bronchoscopy",
                schema_id="robotic_ion_bronchoscopy_v1",
                data={
                    "navigation_plan_source": "pre-procedure CT",
                    "vent_mode": "VC",
                    "vent_rr": 14,
                    "vent_tv_ml": 450,
                    "vent_peep_cm_h2o": 8,
                    "vent_fio2_pct": 40,
                    "vent_flow_rate": "30 L/min",
                    "vent_pmean_cm_h2o": 12,
                    "cbct_performed": True,
                    "radial_pattern": "concentric",
                },
            ),
            ProcedureInput(
                proc_type="ion_registration_complete",
                schema_id="ion_registration_complete_v1",
                data={
                    "method": "automatic",
                    "airway_landmarks": ["carina", "lobar carinas"],
                    "fiducial_error_mm": 1.2,
                    "alignment_quality": "excellent",
                },
            ),
            ProcedureInput(
                proc_type="ebus_tbna",
                schema_id="ebus_tbna_v1",
                data={
                    "needle_gauge": "22G",
                    "stations": [
                        {
                            "station_name": "4R",
                            "size_mm": 12,
                            "passes": 3,
                            "echo_features": "heterogeneous",
                            "biopsy_tools": ["TBNA"],
                            "rose_result": "adequate; lymphoid",
                        },
                        {
                            "station_name": "7",
                            "size_mm": 15,
                            "passes": 4,
                            "echo_features": "round, distinct margins",
                            "biopsy_tools": ["TBNA"],
                            "rose_result": "adequate; pending cytology",
                        },
                    ],
                    "rose_available": True,
                    "overall_rose_diagnosis": "Pending",
                },
            ),
            ProcedureInput(
                proc_type="radial_ebus_sampling",
                schema_id="radial_ebus_sampling_v1",
                data={
                    "guide_sheath_diameter": "1.9 mm",
                    "ultrasound_pattern": "concentric",
                    "lesion_size_mm": 18,
                    "sampling_tools": ["forceps", "brush"],
                    "passes_per_tool": "3 forceps, 2 brush",
                    "fluoro_used": True,
                    "rose_result": "adequate",
                    "specimens": ["cytology", "histology"],
                    "cxr_ordered": False,
                },
            ),
            ProcedureInput(
                proc_type="blvr_valve_placement",
                schema_id="blvr_valve_placement_v1",
                data={
                    "balloon_occlusion_performed": True,
                    "chartis_used": True,
                    "collateral_ventilation_absent": True,
                    "lobes_treated": ["RUL", "RML"],
                    "valves": [
                        {"valve_type": "Zephyr", "valve_size": "4.0", "lobe": "RUL", "segment": "RB1"},
                        {"valve_type": "Zephyr", "valve_size": "4.0", "lobe": "RUL", "segment": "RB2"},
                        {"valve_type": "Zephyr", "valve_size": "4.0", "lobe": "RML", "segment": "RB4"},
                    ],
                    "air_leak_reduction": "complete",
                },
            ),
            ProcedureInput(
                proc_type="blvr_post_procedure_protocol",
                schema_id="blvr_post_procedure_protocol_v1",
                data={
                    "cxr_schedule": ["immediate post-procedure", "4 hours post-procedure"],
                    "monitoring_plan": "Continuous pulse oximetry and telemetry for 72 hours",
                },
            ),
        ],
        sedation=SedationInfo(type="General"),
    )

    note = compose_structured_report(bundle)

    assert "Robotic navigation bronchoscopy was performed using the Intuitive Ion system" in note
    assert "Station: 4R" in note and "Number of Passes: 3" in note
    assert "Radial EBUS" in note
    assert "Endobronchial one-way valve therapy" in note or "Valves deployed" in note
    assert "{{" not in note
    assert "[" not in note

    # Order sanity: navigation/EBUS should precede BLVR content
    idx_ion = note.find("Robotic navigation bronchoscopy")
    idx_ebus = note.find("A systematic EBUS survey")
    idx_blvr = note.find("Balloon occlusion")
    assert idx_ion != -1 and idx_ebus != -1 and idx_blvr != -1
    assert idx_ion < idx_ebus < idx_blvr


def test_individual_templates_clean_render():
    # Ion registration complete
    ion_note = compose_structured_report(
        ProcedureBundle(
            patient=PatientInfo(),
            encounter=EncounterInfo(),
            procedures=[
                ProcedureInput(
                    proc_type="ion_registration_complete",
                    schema_id="ion_registration_complete_v1",
                    data={
                        "method": "automatic",
                        "fiducial_error_mm": 1.0,
                        "alignment_quality": "good",
                    },
                )
            ],
        )
    )
    assert "registration" in ion_note.lower()
    assert "{{" not in ion_note

    # BLVR valve placement
    blvr_note = compose_structured_report(
        ProcedureBundle(
            patient=PatientInfo(),
            encounter=EncounterInfo(),
            procedures=[
                ProcedureInput(
                    proc_type="blvr_valve_placement",
                    schema_id="blvr_valve_placement_v1",
                    data={
                        "lobes_treated": ["LUL"],
                        "valves": [{"valve_type": "Spiration", "valve_size": "5.5", "lobe": "LUL"}],
                    },
                )
            ],
        )
    )
    assert "Valves deployed" in blvr_note
    assert "{{" not in blvr_note


def test_cryo_bpf_case():
    bundle = ProcedureBundle(
        patient=PatientInfo(name="Pat Lee", age=59, sex="male"),
        encounter=EncounterInfo(date="2024-10-01", attending="Dr. Cryo"),
        procedures=[
            ProcedureInput(
                proc_type="bronchoscopy_core",
                schema_id="bronchoscopy_shell_v1",
                data={"airway_overview": "Diffuse secretions cleared.", "right_lung_overview": "Patent.", "left_lung_overview": "Patent."},
            ),
            ProcedureInput(
                proc_type="transbronchial_cryobiopsy",
                schema_id="transbronchial_cryobiopsy_v1",
                data={
                    "lung_segment": "RLL posterior segment",
                    "num_samples": 3,
                    "cryoprobe_size_mm": 1.9,
                    "freeze_seconds": 5,
                    "thaw_seconds": 10,
                    "blocker_type": "Arndt blocker",
                    "blocker_volume_ml": 6,
                    "blocker_location": "RLL ostium",
                    "tests": ["pathology", "microbiology"],
                    "radial_vessel_check": True,
                },
            ),
            ProcedureInput(
                proc_type="bpf_localization_occlusion",
                schema_id="bpf_localization_occlusion_v1",
                data={
                    "culprit_segment": "RB6",
                    "balloon_type": "Fogarty",
                    "balloon_size_mm": 7,
                    "leak_reduction": "partial",
                    "methylene_blue_used": True,
                    "instillation_findings": "dye visualized at occluded airway",
                },
            ),
            ProcedureInput(
                proc_type="bpf_valve_air_leak",
                schema_id="bpf_valve_air_leak_v1",
                data={
                    "etiology": "post-operative air leak",
                    "culprit_location": "RB6",
                    "valve_type": "Zephyr",
                    "valve_size": "4.0",
                    "valves_placed": 1,
                    "leak_reduction": "complete",
                },
            ),
        ],
    )

    note = compose_structured_report(bundle)
    assert "Transbronchial cryobiopsy" in note or "cryobiopsy" in note.lower()
    assert "Arndt blocker" in note
    assert "sequential balloon occlusion" in note or "Fogarty" in note
    assert "one-way valve" in note or "valve was deployed" in note
    assert "{{" not in note and "[" not in note and "None mL" not in note


def test_wll_peg_instructions():
    bundle = ProcedureBundle(
        patient=PatientInfo(name="Taylor Ray", age=50, sex="female"),
        encounter=EncounterInfo(date="2024-10-02", attending="Dr. Other"),
        procedures=[
            ProcedureInput(
                proc_type="whole_lung_lavage",
                schema_id="whole_lung_lavage_v1",
                data={
                    "side": "left",
                    "dlt_size_fr": 37,
                    "position": "right lateral decubitus",
                    "aliquot_volume_l": 1.0,
                    "num_cycles": 5,
                    "total_volume_l": 10,
                },
            ),
            ProcedureInput(
                proc_type="peg_placement",
                schema_id="peg_placement_v1",
                data={
                    "incision_location": "2 cm below costal margin on the left",
                    "tube_size_fr": 20,
                    "bumper_depth_cm": 2.5,
                    "procedural_time_min": 25,
                },
            ),
            ProcedureInput(
                proc_type="tunneled_pleural_catheter_insert",
                schema_id="tunneled_pleural_catheter_insert_v1",
                data={
                    "side": "right",
                    "intercostal_space": "5th",
                    "entry_location": "mid-axillary",
                },
            ),
        ],
    )

    note = compose_structured_report(bundle)
    assert "Whole lung lavage" in note or "lavage" in note.lower()
    assert "Percutaneous endoscopic gastrostomy" in note or "PEG" in note
    assert "Tunneled pleural catheter" in note or "tunneled pleural catheter" in note.lower()
    assert "Discharge Instructions for Tunneled Pleural Catheter" in note
    assert "PEG Discharge Instructions" in note
    assert "{{" not in note and "[" not in note and "None mL" not in note
