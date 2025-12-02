"""Helpers to map flat extraction output into the nested registry schema."""

from __future__ import annotations

from typing import Any


def build_nested_registry_payload(data: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of the flat registry payload with nested sections populated."""
    payload = dict(data)
    families = {fam for fam in data.get("procedure_families") or []}

    providers = _build_providers(data)
    if providers:
        payload["providers"] = providers

    demographics = _build_patient_demographics(data)
    if demographics:
        payload["patient_demographics"] = demographics

    clinical = _build_clinical_context(data)
    if clinical:
        payload["clinical_context"] = clinical

    sedation = _build_sedation(data)
    if sedation:
        payload["sedation"] = sedation

    procedure_setting = _build_procedure_setting(data)
    if procedure_setting:
        payload["procedure_setting"] = procedure_setting

    equipment = _build_equipment(data)
    if equipment:
        payload["equipment"] = equipment

    procedures = _build_procedures_performed(data, families)
    if procedures:
        payload["procedures_performed"] = procedures

    pleural = _build_pleural_procedures(data)
    if pleural:
        payload["pleural_procedures"] = pleural

    specimens = _build_specimens(data)
    if specimens:
        payload["specimens"] = specimens

    # Always set complications to ensure it's a dict (not the list from slot extractor)
    complications = _build_complications(data)
    if complications:
        payload["complications"] = complications
    elif "complications" in payload and isinstance(payload["complications"], list):
        # Remove list-typed complications from slot extractor; schema expects dict
        del payload["complications"]

    outcomes = _build_outcomes(data)
    if outcomes:
        payload["outcomes"] = outcomes

    billing = _build_billing(data)
    if billing:
        payload["billing"] = billing

    metadata = _build_metadata(data)
    if metadata:
        payload["metadata"] = metadata

    return payload


def _build_providers(data: dict[str, Any]) -> dict[str, Any]:
    attending = data.get("attending_name")
    if not attending:
        return {}
    providers: dict[str, Any] = {"attending_name": attending}
    providers["attending_npi"] = data.get("attending_npi")
    providers["fellow_name"] = data.get("fellow_name")
    providers["assistant_name"] = (data.get("assistant_name") or (data.get("assistant_names") or [None])[0])
    providers["assistant_role"] = data.get("assistant_role")
    providers["trainee_present"] = data.get("trainee_present")
    providers["rose_present"] = data.get("ebus_rose_available")
    return providers


def _build_patient_demographics(data: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    if data.get("patient_age") is not None:
        result["age_years"] = data.get("patient_age")
    gender = data.get("gender")
    if gender:
        mapping = {"M": "Male", "F": "Female"}
        result["gender"] = mapping.get(gender, gender)
    if not result:
        return {}
    return result


def _build_clinical_context(data: dict[str, Any]) -> dict[str, Any]:
    context: dict[str, Any] = {}
    if data.get("asa_class") is not None:
        context["asa_class"] = data.get("asa_class")
    if data.get("primary_indication"):
        context["primary_indication"] = data.get("primary_indication")
    if data.get("radiographic_findings"):
        context["radiographic_findings"] = data.get("radiographic_findings")
    if data.get("lesion_size_mm") is not None:
        context["lesion_size_mm"] = data.get("lesion_size_mm")
    if data.get("lesion_location"):
        context["lesion_location"] = data.get("lesion_location")
    if data.get("pet_avid") is not None:
        context["pet_avidity"] = data.get("pet_avid")
    if data.get("pet_suv_max") is not None:
        context["suv_max"] = data.get("pet_suv_max")
    if data.get("bronchus_sign_present") is not None:
        context["bronchus_sign"] = data.get("bronchus_sign_present")
    if not context:
        return {}
    return context


def _build_sedation(data: dict[str, Any]) -> dict[str, Any]:
    sedation: dict[str, Any] = {}
    sed_type = data.get("sedation_type") or data.get("anesthesia_type")
    if isinstance(sed_type, str):
        sedation["type"] = sed_type
    if data.get("anesthesia_agents"):
        sedation["agents_used"] = data.get("anesthesia_agents")
    if data.get("sedation_paralytic_used") is not None:
        sedation["paralytic_used"] = data.get("sedation_paralytic_used")
    if data.get("sedation_reversal_given") is not None:
        sedation["reversal_given"] = data.get("sedation_reversal_given")
    if data.get("sedation_reversal_agent"):
        sedation["reversal_agent"] = data.get("sedation_reversal_agent")
    if data.get("sedation_start"):
        sedation["start_time"] = data.get("sedation_start")
    if data.get("sedation_stop"):
        sedation["end_time"] = data.get("sedation_stop")
    if data.get("sedation_intraservice_minutes") is not None:
        sedation["intraservice_minutes"] = data.get("sedation_intraservice_minutes")
    return sedation


def _build_procedure_setting(data: dict[str, Any]) -> dict[str, Any]:
    """Build procedure_setting section with airway_type and other setting fields."""
    setting: dict[str, Any] = {}
    if data.get("procedure_location"):
        setting["location"] = data.get("procedure_location")
    if data.get("patient_position"):
        setting["patient_position"] = data.get("patient_position")
    if data.get("airway_type"):
        setting["airway_type"] = data.get("airway_type")
    if data.get("ett_size") is not None:
        setting["ett_size"] = data.get("ett_size")
    return setting


def _build_equipment(data: dict[str, Any]) -> dict[str, Any]:
    equipment: dict[str, Any] = {}
    # bronchoscope_type is a separate field from airway_type
    # bronchoscope_type: Diagnostic, Therapeutic, Ultrathin, EBUS, Single-use
    # airway_type: Native, ETT, Tracheostomy, LMA, iGel (goes in procedure_setting)
    if data.get("bronchoscope_type"):
        equipment["bronchoscope_type"] = data.get("bronchoscope_type")
    if data.get("airway_device_size"):
        equipment["bronchoscope_outer_diameter_mm"] = data.get("airway_device_size")
    if data.get("nav_platform"):
        equipment["navigation_platform"] = data.get("nav_platform")
    if data.get("fluoro_time_min") is not None:
        equipment["fluoroscopy_time_seconds"] = float(data["fluoro_time_min"]) * 60
    if data.get("cbct_used") is not None:
        equipment["cbct_used"] = data.get("cbct_used")
    if data.get("augmented_fluoroscopy") is not None:
        equipment["augmented_fluoroscopy"] = data.get("augmented_fluoroscopy")
    return equipment


def _build_procedures_performed(data: dict[str, Any], families: set[str]) -> dict[str, Any]:
    procedures: dict[str, Any] = {}

    if "EBUS" in families or data.get("ebus_stations_sampled"):
        linear: dict[str, Any] = {"performed": True}
        if data.get("ebus_stations_sampled"):
            linear["stations_sampled"] = data.get("ebus_stations_sampled")
        if data.get("ebus_needle_gauge"):
            linear["needle_gauge"] = data.get("ebus_needle_gauge")
        if data.get("ebus_needle_type"):
            linear["needle_type"] = data.get("ebus_needle_type")
        if data.get("ebus_elastography_used") is not None:
            linear["elastography_used"] = data.get("ebus_elastography_used")
        if data.get("ebus_elastography_pattern"):
            linear["elastography_pattern"] = data.get("ebus_elastography_pattern")
        if data.get("ebus_photodocumentation_complete") is not None:
            linear["photodocumentation_complete"] = data.get("ebus_photodocumentation_complete")
        if data.get("ebus_stations_detail"):
            linear["stations_detail"] = data.get("ebus_stations_detail")
        if data.get("linear_ebus_stations"):
            linear["stations_planned"] = data.get("linear_ebus_stations")
        procedures["linear_ebus"] = linear

    if data.get("nav_rebus_used") is not None or data.get("nav_rebus_view"):
        radial: dict[str, Any] = {}
        if data.get("nav_rebus_used") is not None:
            radial["performed"] = bool(data.get("nav_rebus_used"))
        if data.get("nav_rebus_view"):
            radial["probe_position"] = data.get("nav_rebus_view")
        procedures["radial_ebus"] = radial

    if "NAVIGATION" in families or data.get("nav_tool_in_lesion"):
        nav: dict[str, Any] = {"performed": True}
        if data.get("nav_tool_in_lesion") is not None:
            nav["tool_in_lesion_confirmed"] = data.get("nav_tool_in_lesion")
        if data.get("nav_sampling_tools"):
            nav["sampling_tools_used"] = data.get("nav_sampling_tools")
        if data.get("nav_divergence"):
            nav["divergence_mm"] = data.get("nav_divergence")
        if data.get("nav_target_size"):
            nav["target_size_mm"] = data.get("nav_target_size")
        if data.get("nav_target_location"):
            nav["target_location"] = data.get("nav_target_location")
        if data.get("nav_imaging_verification"):
            nav["imaging_verification"] = data.get("nav_imaging_verification")
        procedures["navigational_bronchoscopy"] = nav

    if data.get("bronch_num_tbbx") or data.get("bronch_biopsy_sites"):
        tblb: dict[str, Any] = {"performed": True}
        if data.get("bronch_num_tbbx") is not None:
            tblb["number_of_samples"] = data.get("bronch_num_tbbx")
        if data.get("bronch_biopsy_sites"):
            tblb["locations"] = data.get("bronch_biopsy_sites")
        if data.get("bronch_tbbx_tool"):
            tblb["forceps_type"] = data.get("bronch_tbbx_tool")
        procedures["transbronchial_biopsy"] = tblb

    if data.get("cryo_probe_size") or data.get("cryo_specimens_count"):
        cryo: dict[str, Any] = {"performed": True}
        cryo["cryoprobe_size_mm"] = data.get("cryo_probe_size")
        cryo["number_of_samples"] = data.get("cryo_specimens_count")
        cryo["freeze_time_seconds"] = data.get("cryo_freeze_time")
        procedures["transbronchial_cryobiopsy"] = cryo

    if data.get("bal_volume_instilled") or data.get("bal_volume_returned"):
        bal: dict[str, Any] = {"performed": True}
        bal["volume_instilled_ml"] = data.get("bal_volume_instilled")
        bal["volume_returned_ml"] = data.get("bal_volume_returned")
        bal["location"] = data.get("bal_location")
        procedures["bal"] = bal

    if data.get("stent_type") or data.get("stent_action"):
        stent: dict[str, Any] = {"performed": True}
        stent["stent_type"] = data.get("stent_type")
        stent["action"] = data.get("stent_action")
        stent["location"] = data.get("stent_location")
        stent["size"] = data.get("stent_size")
        procedures["airway_stent"] = stent

    if data.get("blvr_target_lobe") or data.get("blvr_valve_type"):
        blvr: dict[str, Any] = {"performed": True}
        blvr["target_lobe"] = data.get("blvr_target_lobe")
        blvr["valve_type"] = data.get("blvr_valve_type")
        blvr["number_of_valves"] = data.get("blvr_valve_count")
        blvr["segments_treated"] = data.get("blvr_segments_treated")
        blvr["collateral_ventilation_assessment"] = data.get("blvr_cv_assessment_method")
        procedures["blvr"] = blvr

    return procedures


def _build_pleural_procedures(data: dict[str, Any]) -> dict[str, Any]:
    pleural_type = data.get("pleural_procedure_type")
    if not pleural_type:
        return {}
    pleural: dict[str, Any] = {}

    def _base_fields() -> dict[str, Any]:
        return {
            "performed": True,
            "side": data.get("pleural_side"),
            "guidance": data.get("pleural_guidance"),
            "intercostal_space": data.get("pleural_intercostal_space"),
            "volume_drained_ml": data.get("pleural_volume_drained_ml"),
            "fluid_character": data.get("pleural_fluid_appearance"),
            "opening_pressure_cmh2o": data.get("pleural_opening_pressure_cmh2o"),
            "opening_pressure_measured": data.get("pleural_opening_pressure_measured"),
        }

    if pleural_type == "Thoracentesis":
        pleural["thoracentesis"] = _base_fields()
    elif pleural_type in {"Chest Tube", "Chest Tube Removal"}:
        chest = _base_fields()
        chest["action"] = pleural_type
        pleural["chest_tube"] = chest
    elif pleural_type.startswith("Tunneled"):
        ipc = _base_fields()
        ipc["action"] = pleural_type
        pleural["ipc"] = ipc
    elif pleural_type == "Medical Thoracoscopy":
        thor = _base_fields()
        thor["findings"] = data.get("pleural_thoracoscopy_findings")
        pleural["medical_thoracoscopy"] = thor
    elif pleural_type == "Chemical Pleurodesis":
        pleuro = _base_fields()
        pleuro["agent"] = data.get("pleurodesis_agent")
        pleural["pleurodesis"] = pleuro
    return pleural


def _build_complications(data: dict[str, Any]) -> dict[str, Any]:
    complications: dict[str, Any] = {}
    comp_list = []
    if data.get("bronch_immediate_complications"):
        comp_list.append(data["bronch_immediate_complications"])
    if comp_list:
        complications["complication_list"] = comp_list
        complications["any_complication"] = True
    if data.get("bleeding_severity"):
        complications["bleeding"] = data.get("bleeding_severity")
    if data.get("pneumothorax") is not None:
        complications["pneumothorax"] = data.get("pneumothorax")
        complications["pneumothorax_intervention"] = data.get("pneumothorax_intervention")
    if data.get("hypoxia_respiratory_failure"):
        complications["respiratory"] = data.get("hypoxia_respiratory_failure")
    if data.get("other_complication_details"):
        complications["other_complication_details"] = data.get("other_complication_details")
    return complications


def _build_outcomes(data: dict[str, Any]) -> dict[str, Any]:
    outcomes: dict[str, Any] = {}
    if data.get("disposition"):
        outcomes["disposition"] = data.get("disposition")
    if data.get("procedure_completed") is not None:
        outcomes["procedure_completed"] = data.get("procedure_completed")
    if data.get("procedure_aborted_reason"):
        outcomes["procedure_aborted_reason"] = data.get("procedure_aborted_reason")
    return outcomes


def _build_billing(data: dict[str, Any]) -> dict[str, Any]:
    billing: dict[str, Any] = {}
    if data.get("cpt_codes"):
        entries = []
        for code in data["cpt_codes"]:
            if not code:
                continue
            entries.append({"code": str(code)})
        if entries:
            billing["cpt_codes"] = entries
    return billing


def _build_metadata(data: dict[str, Any]) -> dict[str, Any]:
    if data.get("note_id") or data.get("source_system"):
        return {
            "note_id": data.get("note_id"),
            "source_system": data.get("source_system"),
        }
    return {}


def _build_specimens(data: dict[str, Any]) -> dict[str, Any]:
    specimens: dict[str, Any] = {}
    if data.get("ebus_rose_result"):
        specimens["rose_result"] = data.get("ebus_rose_result")
    if data.get("specimens_collected"):
        specimens["specimens_collected"] = data.get("specimens_collected")
    return specimens
