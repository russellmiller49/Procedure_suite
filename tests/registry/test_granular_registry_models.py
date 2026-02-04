"""Tests for granular per-site registry models and helpers.

This module tests:
1. Model creation and JSON round-trip for all granular data types
2. EBUS consistency validation
3. Aggregate field derivation from granular data
4. RegistryRecord integration with granular_data field
"""

from __future__ import annotations

import pytest
from typing import Any

from modules.registry.schema_granular import (
    EnhancedRegistryGranularData,
    IPCProcedure,
    ClinicalContext,
    PatientDemographics,
    AirwayStentProcedure,
    EBUSStationDetail,
    NavigationTarget,
    CAOInterventionDetail,
    CAOModalityApplication,
    BLVRValvePlacement,
    BLVRChartisMeasurement,
    CryobiopsySite,
    ThoracoscopyFinding,
    SpecimenCollected,
    validate_ebus_consistency,
    derive_aggregate_fields,
)
from modules.registry.schema import (
    RegistryRecord,
)
from modules.registry.postprocess import process_granular_data


class TestEBUSStationDetailModel:
    """Tests for EBUSStationDetail Pydantic model."""


    def test_minimal_creation(self):
        """Test creating station detail with only required field."""
        station = EBUSStationDetail(station="4R")
        assert station.station == "4R"
        assert station.sampled is True  # Default
        assert station.short_axis_mm is None
        assert station.morphologic_impression is None

    def test_full_creation(self):
        """Test creating station detail with all fields."""
        station = EBUSStationDetail(
            station="7",
            short_axis_mm=12.5,
            long_axis_mm=18.0,
            shape="round",
            margin="distinct",
            echogenicity="heterogeneous",
            chs_present=False,
            necrosis_present=True,
            calcification_present=False,
            elastography_performed=True,
            elastography_score=4,
            elastography_strain_ratio=2.5,
            elastography_pattern="predominantly_blue",
            doppler_performed=True,
            doppler_pattern="peripheral",
            morphologic_impression="malignant",
            sampled=True,
            needle_gauge=22,
            needle_type="Standard FNA",
            number_of_passes=4,
            intranodal_forceps_used=False,
            rose_performed=True,
            rose_result="Malignant",
            rose_adequacy=True,
            specimen_sent_for=["Cytology", "Cell block", "Molecular/NGS"],
            final_pathology="Adenocarcinoma",
            n_stage_contribution="N2",
            notes="Large heterogeneous node with central necrosis",
        )
        assert station.station == "7"
        assert station.short_axis_mm == 12.5
        assert station.morphologic_impression == "malignant"
        assert station.rose_result == "Malignant"
        assert len(station.specimen_sent_for) == 3

    def test_json_roundtrip(self):
        """Test JSON serialization and deserialization."""
        station = EBUSStationDetail(
            station="4R",
            short_axis_mm=8.5,
            shape="oval",
            chs_present=True,
            morphologic_impression="benign",
            number_of_passes=3,
            rose_result="Adequate lymphocytes",
        )
        json_data = station.model_dump()
        restored = EBUSStationDetail(**json_data)
        assert restored.station == station.station
        assert restored.short_axis_mm == station.short_axis_mm
        assert restored.morphologic_impression == station.morphologic_impression


class TestIPCProcedureModel:
    """Tests for IPCProcedure model and Registry integration."""

    def test_action_normalization(self):
        """LLM variants like 'tunneled catheter' normalize to enum values."""
        ipc = IPCProcedure(action="Tunneled catheter placement")
        assert ipc.action == "Insertion"

    def test_registry_record_integration(self):
        """RegistryRecord should leverage IPCProcedure normalization."""
        record = RegistryRecord(
            pleural_procedures={
                "ipc": {
                    "performed": True,
                    "action": "Alteplase instillation",
                }
            }
        )
        assert record.pleural_procedures.ipc.action == "Fibrinolytic instillation"


class TestClinicalContextModel:
    """Tests for ClinicalContext overrides and integration."""

    def test_bronchus_sign_boolean_normalization(self):
        ctx = ClinicalContext(bronchus_sign=True)
        assert ctx.bronchus_sign == "Positive"

    def test_registry_record_integration(self):
        record = RegistryRecord(clinical_context={"bronchus_sign": None})
        assert record.clinical_context.bronchus_sign == "Not assessed"


class TestPatientDemographicsModel:
    """Tests for PatientDemographics overrides and integration."""

    def test_gender_normalization(self):
        patient = PatientDemographics(gender="m")
        assert patient.gender == "Male"

    def test_registry_record_integration(self):
        record = RegistryRecord(patient_demographics={"gender": "nb"})
        assert record.patient_demographics.gender == "Other"


class TestAirwayStentModel:
    """Tests for AirwayStentProcedure overrides and integration."""

    def test_location_normalization(self):
        stent = AirwayStentProcedure(location="Mainstem")
        assert stent.location == "Other"

    def test_action_normalization_compound_revision(self):
        stent = AirwayStentProcedure(performed=True, action="Removal and Y-Stent Insertion")
        assert stent.action == "Revision/Repositioning"

    def test_registry_record_integration(self):
        record = RegistryRecord(
            procedures_performed={
                "airway_stent": {
                    "performed": True,
                    "location": "Mainstem",
                }
            }
        )
        assert record.procedures_performed.airway_stent.location == "Other"


class TestProcedureSettingSerialization:
    """Ensure procedure_setting serializes as a nested object."""

    def test_procedure_setting_serialized(self):
        record = RegistryRecord(procedure_setting={"airway_type": "ETT"})
        dumped = record.model_dump()
        assert isinstance(dumped.get("procedure_setting"), dict)
        assert dumped["procedure_setting"].get("airway_type") == "ETT"


class TestNavigationTargetModel:
    """Tests for NavigationTarget Pydantic model."""

    def test_minimal_creation(self):
        """Test creating nav target with only required fields."""
        target = NavigationTarget(
            target_number=1,
            target_location_text="RUL apical segment"
        )
        assert target.target_number == 1
        assert target.target_location_text == "RUL apical segment"
        assert target.tool_in_lesion_confirmed is None

    def test_full_creation(self):
        """Test creating nav target with all fields."""
        target = NavigationTarget(
            target_number=1,
            target_location_text="RUL apical segment, S1",
            target_lobe="RUL",
            target_segment="S1 apical",
            lesion_size_mm=22.0,
            distance_from_pleura_mm=15.0,
            bronchus_sign="Positive",
            ct_characteristics="Solid",
            pet_suv_max=8.5,
            registration_error_mm=3.2,
            navigation_successful=True,
            rebus_used=True,
            rebus_view="Concentric",
            rebus_lesion_appearance="Hyperechoic solid mass",
            tool_in_lesion_confirmed=True,
            confirmation_method="CBCT",
            cbct_til_confirmed=True,
            sampling_tools_used=["Forceps", "Needle (21G)", "Brush"],
            number_of_forceps_biopsies=5,
            number_of_needle_passes=3,
            number_of_cryo_biopsies=None,  # None if not used, not 0
            rose_performed=True,
            rose_result="Malignant cells",
            immediate_complication="Bleeding - mild",
            bleeding_management="Cold saline",
            specimen_sent_for=["Histology", "Cytology"],
            final_pathology="Adenocarcinoma",
            notes="TIL confirmed on first pass",
        )
        assert target.target_number == 1
        assert target.tool_in_lesion_confirmed is True
        assert target.lesion_size_mm == 22.0


class TestThoracoscopyFindingModel:
    """Tests for thoracoscopy finding normalization."""

    def test_biopsy_tool_normalization(self):
        finding = ThoracoscopyFinding(
            location="Parietal pleura - diaphragm",
            finding_type="Nodules",
            biopsy_tool="cryo forceps",
        )
        assert finding.biopsy_tool == "Cryoprobe"

    def test_location_normalization(self):
        finding = ThoracoscopyFinding(
            location="left pleural space",
            finding_type="Plaques",
        )
        assert finding.location == "Parietal pleura - chest wall"


class TestCAOInterventionDetailModel:
    """Tests for CAO intervention detail model."""

    def test_minimal_creation(self):
        """Test creating CAO intervention with only required field."""
        intervention = CAOInterventionDetail(location="RMS")
        assert intervention.location == "RMS"
        assert intervention.modalities_applied is None

    def test_with_modalities(self):
        """Test CAO intervention with multiple modalities."""
        intervention = CAOInterventionDetail(
            location="Trachea - mid",
            obstruction_type="Intraluminal",
            etiology="Malignant - primary lung",
            pre_obstruction_pct=80,
            post_obstruction_pct=20,
            modalities_applied=[
                CAOModalityApplication(
                    modality="APC",
                    power_setting_watts=40,
                    apc_flow_rate_lpm=2.0,
                    number_of_applications=3,
                ),
                CAOModalityApplication(
                    modality="Cryoextraction",
                    freeze_time_seconds=5,
                    number_of_applications=2,
                ),
            ],
            hemostasis_required=True,
            hemostasis_methods=["Cold saline", "Epinephrine"],
        )
        assert intervention.pre_obstruction_pct == 80
        assert intervention.post_obstruction_pct == 20
        assert len(intervention.modalities_applied) == 2

    def test_new_etiology_and_modalities(self):
        """Ensure new etiology and modality literals are supported."""
        intervention = CAOInterventionDetail(
            location="RMS",
            etiology="Infectious",
            modalities_applied=[
                CAOModalityApplication(modality="Iced saline lavage"),
                CAOModalityApplication(modality="Epinephrine instillation"),
                CAOModalityApplication(modality="Tranexamic acid instillation"),
                CAOModalityApplication(modality="Balloon tamponade"),
                CAOModalityApplication(modality="Laser"),
                CAOModalityApplication(modality="Suctioning"),
            ],
        )
        assert intervention.etiology == "Infectious"
        assert len(intervention.modalities_applied) == 6


class TestEnhancedRegistryGranularData:
    """Tests for the main granular data container."""

    def test_empty_creation(self):
        """Test creating empty granular data container."""
        granular = EnhancedRegistryGranularData()
        assert granular.linear_ebus_stations_detail is None
        assert granular.navigation_targets is None
        assert granular.cao_interventions_detail is None

    def test_full_synthetic_data(self):
        """Test creating granular data with multiple procedure types."""
        granular = EnhancedRegistryGranularData(
            linear_ebus_stations_detail=[
                EBUSStationDetail(
                    station="4R",
                    short_axis_mm=8.5,
                    shape="oval",
                    chs_present=True,
                    morphologic_impression="benign",
                    sampled=True,
                    number_of_passes=3,
                    rose_result="Adequate lymphocytes",
                ),
                EBUSStationDetail(
                    station="7",
                    short_axis_mm=14.0,
                    shape="round",
                    echogenicity="heterogeneous",
                    chs_present=False,
                    morphologic_impression="malignant",
                    sampled=True,
                    number_of_passes=4,
                    rose_result="Malignant",
                ),
                EBUSStationDetail(
                    station="11L",
                    short_axis_mm=6.0,
                    shape="oval",
                    chs_present=True,
                    morphologic_impression="benign",
                    sampled=True,
                    number_of_passes=2,
                    rose_result="Adequate lymphocytes",
                ),
            ],
            navigation_targets=[
                NavigationTarget(
                    target_number=1,
                    target_location_text="RUL apical segment",
                    target_lobe="RUL",
                    lesion_size_mm=22.0,
                    tool_in_lesion_confirmed=True,
                    confirmation_method="CBCT",
                ),
                NavigationTarget(
                    target_number=2,
                    target_location_text="LLL posterior basal",
                    target_lobe="LLL",
                    lesion_size_mm=18.0,
                    tool_in_lesion_confirmed=False,
                ),
            ],
            cao_interventions_detail=[
                CAOInterventionDetail(
                    location="RMS",
                    obstruction_type="Intraluminal",
                    pre_obstruction_pct=70,
                    post_obstruction_pct=10,
                    modalities_applied=[
                        CAOModalityApplication(modality="APC", power_setting_watts=40),
                    ],
                ),
            ],
            blvr_valve_placements=[
                BLVRValvePlacement(
                    valve_number=1,
                    target_lobe="LUL",
                    segment="LB1+2",
                    valve_size="4.0",
                    valve_type="Zephyr (Pulmonx)",
                    deployment_successful=True,
                ),
                BLVRValvePlacement(
                    valve_number=2,
                    target_lobe="LUL",
                    segment="LB3",
                    valve_size="4.0-LP",
                    valve_type="Zephyr (Pulmonx)",
                    deployment_successful=True,
                ),
            ],
            cryobiopsy_sites=[
                CryobiopsySite(
                    site_number=1,
                    lobe="RLL",
                    segment="Lateral basal",
                    probe_size_mm=1.9,
                    freeze_time_seconds=5,
                    number_of_biopsies=4,
                    bleeding_severity="Mild",
                ),
            ],
            thoracoscopy_findings_detail=[
                ThoracoscopyFinding(
                    location="Parietal pleura - chest wall",
                    finding_type="Nodules",
                    extent="Multifocal",
                    biopsied=True,
                    number_of_biopsies=6,
                    impression="Malignant appearing",
                ),
            ],
            specimens_collected=[
                SpecimenCollected(
                    specimen_number=1,
                    source_procedure="EBUS-TBNA",
                    source_location="4R",
                    collection_tool="22G FNA",
                    destinations=["Cytology", "Cell block"],
                ),
                SpecimenCollected(
                    specimen_number=2,
                    source_procedure="EBUS-TBNA",
                    source_location="7",
                    collection_tool="22G FNA",
                    destinations=["Cytology", "Cell block", "Molecular/NGS"],
                ),
            ],
        )

        # Verify model dump produces JSON with expected keys
        json_data = granular.model_dump()
        assert "linear_ebus_stations_detail" in json_data
        assert "navigation_targets" in json_data
        assert "cao_interventions_detail" in json_data
        assert "blvr_valve_placements" in json_data
        assert "cryobiopsy_sites" in json_data
        assert "thoracoscopy_findings_detail" in json_data
        assert "specimens_collected" in json_data

        # Verify counts
        assert len(json_data["linear_ebus_stations_detail"]) == 3
        assert len(json_data["navigation_targets"]) == 2
        assert len(json_data["blvr_valve_placements"]) == 2

    def test_json_roundtrip(self):
        """Test that granular data survives JSON serialization."""
        granular = EnhancedRegistryGranularData(
            linear_ebus_stations_detail=[
                EBUSStationDetail(station="4R", number_of_passes=3),
            ],
        )
        json_data = granular.model_dump()
        restored = EnhancedRegistryGranularData(**json_data)
        assert len(restored.linear_ebus_stations_detail) == 1
        assert restored.linear_ebus_stations_detail[0].station == "4R"


class TestValidateEBUSConsistency:
    """Tests for the validate_ebus_consistency helper function."""

    def test_matching_stations(self):
        """Case 1: stations_sampled matches detail array - no errors."""
        stations_detail = [
            EBUSStationDetail(station="4R", sampled=True),
            EBUSStationDetail(station="7", sampled=True),
        ]
        stations_sampled = ["4R", "7"]
        errors = validate_ebus_consistency(stations_detail, stations_sampled)
        assert errors == []

    def test_missing_station_in_detail(self):
        """Case 2: station in sampled list but missing from detail."""
        stations_detail = [
            EBUSStationDetail(station="4R", sampled=True),
            EBUSStationDetail(station="7", sampled=True),
        ]
        stations_sampled = ["4R", "7", "11L"]  # 11L not in detail
        errors = validate_ebus_consistency(stations_detail, stations_sampled)
        assert len(errors) == 1
        assert "11L" in errors[0]

    def test_extra_station_in_detail(self):
        """Station in detail but not in sampled list."""
        stations_detail = [
            EBUSStationDetail(station="4R", sampled=True),
            EBUSStationDetail(station="7", sampled=True),
            EBUSStationDetail(station="11L", sampled=True),  # Extra
        ]
        stations_sampled = ["4R", "7"]
        errors = validate_ebus_consistency(stations_detail, stations_sampled)
        assert len(errors) == 1
        assert "11L" in errors[0]

    def test_empty_detail_with_sampled(self):
        """Case 3: stations_sampled populated but detail is empty."""
        stations_detail = None
        stations_sampled = ["4R", "7"]
        errors = validate_ebus_consistency(stations_detail, stations_sampled)
        assert len(errors) == 1
        # Error should indicate detail is missing when sampled list is populated
        assert "stations_sampled" in errors[0].lower() or "no stations_detail" in errors[0].lower()

    def test_both_empty(self):
        """Both empty - no errors."""
        errors = validate_ebus_consistency(None, None)
        assert errors == []

    def test_detail_only(self):
        """Detail populated but sampled list is None."""
        stations_detail = [
            EBUSStationDetail(station="4R", sampled=True),
        ]
        # This should not error - we have detail, just no aggregate list
        errors = validate_ebus_consistency(stations_detail, None)
        # Should be ok since we're not expecting sampled to be there
        assert errors == []  # or might have info that detail exists without sampled

    def test_unsampled_stations_ignored(self):
        """Stations with sampled=False should not cause consistency errors."""
        stations_detail = [
            EBUSStationDetail(station="4R", sampled=True),
            EBUSStationDetail(station="7", sampled=False),  # Visualized only
        ]
        stations_sampled = ["4R"]  # Only 4R was actually sampled
        errors = validate_ebus_consistency(stations_detail, stations_sampled)
        assert errors == []


class TestDeriveAggregateFields:
    """Tests for the derive_aggregate_fields helper function."""

    def test_ebus_aggregation(self):
        """Test EBUS aggregate field derivation."""
        granular = EnhancedRegistryGranularData(
            linear_ebus_stations_detail=[
                EBUSStationDetail(
                    station="4R",
                    sampled=True,
                    number_of_passes=3,
                    rose_result="Adequate lymphocytes",
                ),
                EBUSStationDetail(
                    station="7",
                    sampled=True,
                    number_of_passes=4,
                    rose_result="Malignant",
                ),
            ],
        )
        derived = derive_aggregate_fields(granular)

        assert derived["linear_ebus_stations"] == ["4R", "7"]
        assert derived["ebus_total_passes"] == 7
        # First station's ROSE result should be used
        assert derived["ebus_rose_result"] == "Adequate lymphocytes"

    def test_navigation_aggregation(self):
        """Test navigation aggregate field derivation."""
        granular = EnhancedRegistryGranularData(
            navigation_targets=[
                NavigationTarget(
                    target_number=1,
                    target_location_text="RUL apical",
                    tool_in_lesion_confirmed=True,
                ),
                NavigationTarget(
                    target_number=2,
                    target_location_text="LLL posterior",
                    tool_in_lesion_confirmed=False,
                ),
                NavigationTarget(
                    target_number=3,
                    target_location_text="RML lateral",
                    tool_in_lesion_confirmed=True,
                ),
            ],
        )
        derived = derive_aggregate_fields(granular)

        assert derived["nav_targets_count"] == 3
        assert derived["nav_til_confirmed_count"] == 2

    def test_blvr_aggregation(self):
        """Test BLVR aggregate field derivation."""
        granular = EnhancedRegistryGranularData(
            blvr_valve_placements=[
                BLVRValvePlacement(
                    valve_number=1,
                    target_lobe="LUL",
                    segment="LB1+2",
                    valve_size="4.0",
                    valve_type="Zephyr (Pulmonx)",
                    deployment_successful=True,
                ),
                BLVRValvePlacement(
                    valve_number=2,
                    target_lobe="LUL",
                    segment="LB3",
                    valve_size="4.0-LP",
                    valve_type="Zephyr (Pulmonx)",
                    deployment_successful=True,
                ),
                BLVRValvePlacement(
                    valve_number=3,
                    target_lobe="LUL",
                    segment="LB4+5",
                    valve_size="5.5",
                    valve_type="Zephyr (Pulmonx)",
                    deployment_successful=True,
                ),
            ],
        )
        derived = derive_aggregate_fields(granular)

        assert derived["blvr_number_of_valves"] == 3
        # All valves in same lobe
        assert derived["blvr_target_lobe"] == "LUL"

    def test_blvr_multiple_lobes(self):
        """Test BLVR with valves in different lobes."""
        granular = EnhancedRegistryGranularData(
            blvr_valve_placements=[
                BLVRValvePlacement(
                    valve_number=1,
                    target_lobe="LUL",
                    segment="LB1+2",
                    valve_size="4.0",
                    valve_type="Zephyr (Pulmonx)",
                    deployment_successful=True,
                ),
                BLVRValvePlacement(
                    valve_number=2,
                    target_lobe="RUL",  # Different lobe
                    segment="RB1",
                    valve_size="4.0",
                    valve_type="Zephyr (Pulmonx)",
                    deployment_successful=True,
                ),
            ],
        )
        derived = derive_aggregate_fields(granular)

        assert derived["blvr_number_of_valves"] == 2
        # Multiple lobes - should not set single target_lobe
        assert derived.get("blvr_target_lobe") is None

    def test_cryobiopsy_aggregation(self):
        """Test cryobiopsy aggregate field derivation."""
        granular = EnhancedRegistryGranularData(
            cryobiopsy_sites=[
                CryobiopsySite(
                    site_number=1,
                    lobe="RLL",
                    number_of_biopsies=4,
                ),
                CryobiopsySite(
                    site_number=2,
                    lobe="LLL",
                    number_of_biopsies=3,
                ),
            ],
        )
        derived = derive_aggregate_fields(granular)

        assert derived["cryo_specimens_count"] == 7

    def test_empty_granular_data(self):
        """Test derivation from empty granular data."""
        granular = EnhancedRegistryGranularData()
        derived = derive_aggregate_fields(granular)

        assert derived == {}  # No fields to derive


class TestRegistryRecordIntegration:
    """Tests for RegistryRecord integration with granular_data field."""

    def test_registry_record_with_granular(self):
        """Test creating RegistryRecord with granular data."""
        record = RegistryRecord(
            patient_mrn="12345",
            procedure_date="2024-01-15",
            granular_data=EnhancedRegistryGranularData(
                linear_ebus_stations_detail=[
                    EBUSStationDetail(
                        station="4R",
                        number_of_passes=3,
                        rose_result="Adequate lymphocytes",
                    ),
                    EBUSStationDetail(
                        station="7",
                        number_of_passes=4,
                        rose_result="Malignant",
                    ),
                ],
            ),
        )

        assert record.granular_data is not None
        assert len(record.granular_data.linear_ebus_stations_detail) == 2
        assert record.granular_validation_warnings == []

    def test_process_granular_data_integration(self):
        """Test that process_granular_data correctly merges aggregate fields."""
        data = {
            "patient_mrn": "12345",
            "procedure_date": "2024-01-15",
            "granular_data": {
                "linear_ebus_stations_detail": [
                    {"station": "4R", "number_of_passes": 3, "rose_result": "Adequate lymphocytes"},
                    {"station": "7", "number_of_passes": 4, "rose_result": "Malignant"},
                ],
                "navigation_targets": [
                    {"target_number": 1, "target_location_text": "RUL apical", "tool_in_lesion_confirmed": True},
                ],
            },
        }

        result = process_granular_data(data)

        # Check derived aggregate fields
        assert result["linear_ebus_stations"] == ["4R", "7"]
        assert result["ebus_total_passes"] == 7
        assert result["ebus_rose_result"] == "Adequate lymphocytes"
        assert result["nav_targets_count"] == 1
        assert result["nav_til_confirmed_count"] == 1

    def test_process_granular_data_preserves_existing(self):
        """Test that existing aggregate values are not overwritten."""
        data = {
            "patient_mrn": "12345",
            "linear_ebus_stations": ["4R", "7", "11L"],  # Pre-existing
            "ebus_total_passes": 10,  # Pre-existing
            "granular_data": {
                "linear_ebus_stations_detail": [
                    {"station": "4R", "number_of_passes": 3},
                    {"station": "7", "number_of_passes": 4},
                ],
            },
        }

        result = process_granular_data(data)

        # Pre-existing values should be preserved
        assert result["linear_ebus_stations"] == ["4R", "7", "11L"]
        assert result["ebus_total_passes"] == 10

    def test_process_granular_data_with_consistency_warning(self):
        """Test that EBUS consistency warnings are captured."""
        data = {
            "patient_mrn": "12345",
            "ebus_stations_sampled": ["4R", "7", "11L"],  # 11L not in detail
            "granular_data": {
                "linear_ebus_stations_detail": [
                    {"station": "4R", "number_of_passes": 3, "sampled": True},
                    {"station": "7", "number_of_passes": 4, "sampled": True},
                ],
            },
        }

        result = process_granular_data(data)

        # Should have a validation warning about 11L
        assert "granular_validation_warnings" in result
        warnings = result["granular_validation_warnings"]
        assert len(warnings) > 0
        assert any("11L" in w for w in warnings)


class TestGranularDataExtraFieldsIgnored:
    """Test that extra fields are properly ignored (ConfigDict extra='ignore')."""

    def test_extra_fields_ignored(self):
        """Test that models ignore extra fields without error."""
        # This should not raise an error
        station = EBUSStationDetail(
            station="4R",
            unknown_field="should be ignored",  # type: ignore
            another_unknown=123,  # type: ignore
        )
        assert station.station == "4R"
        assert not hasattr(station, "unknown_field")

    def test_granular_container_extra_fields(self):
        """Test that the container ignores extra fields."""
        granular = EnhancedRegistryGranularData(
            linear_ebus_stations_detail=[
                EBUSStationDetail(station="4R"),
            ],
            future_procedure_type=["ignored"],  # type: ignore
        )
        assert granular.linear_ebus_stations_detail is not None
        assert not hasattr(granular, "future_procedure_type")


class TestDeriveProceduresFromGranular:
    """Tests for derive_procedures_from_granular function."""

    def test_cryobiopsy_derivation(self):
        """Test that cryobiopsy_sites populates transbronchial_cryobiopsy."""
        from modules.registry.schema_granular import derive_procedures_from_granular

        granular_data = {
            "cryobiopsy_sites": [
                {
                    "site_number": 1,
                    "lobe": "LLL",
                    "segment": "Posterior-Basal",
                    "probe_size_mm": 1.1,
                    "freeze_time_seconds": 6,
                    "number_of_biopsies": 5,
                }
            ]
        }
        existing_procedures = {}

        procedures, warnings = derive_procedures_from_granular(granular_data, existing_procedures)

        assert procedures["transbronchial_cryobiopsy"]["performed"] is True
        assert procedures["transbronchial_cryobiopsy"]["number_of_samples"] == 5
        assert procedures["transbronchial_cryobiopsy"]["probe_size_mm"] == 1.1
        assert procedures["transbronchial_cryobiopsy"]["freeze_time_seconds"] == 6
        assert procedures["transbronchial_cryobiopsy"]["locations_biopsied"] == ["LLL Posterior-Basal"]

    def test_radial_ebus_derivation(self):
        """Test that navigation_targets with rebus_used populates radial_ebus.performed."""
        from modules.registry.schema_granular import derive_procedures_from_granular

        granular_data = {
            "navigation_targets": [
                {
                    "target_number": 1,
                    "target_location_text": "LLL Posterior-Basal",
                    "rebus_used": True,
                    "rebus_view": "Concentric",
                    "tool_in_lesion_confirmed": True,
                }
            ]
        }
        existing_procedures = {"radial_ebus": {"probe_position": "Concentric"}}

        procedures, warnings = derive_procedures_from_granular(granular_data, existing_procedures)

        assert procedures["radial_ebus"]["performed"] is True
        assert procedures["radial_ebus"]["probe_position"] == "Concentric"

    def test_linear_ebus_stations_sampled_derivation(self):
        """Test that linear_ebus_stations_detail populates stations_sampled."""
        from modules.registry.schema_granular import derive_procedures_from_granular

        granular_data = {
            "linear_ebus_stations_detail": [
                {"station": "7", "sampled": True},
                {"station": "11L", "sampled": True},
                {"station": "4R", "sampled": False},  # Inspected only
            ]
        }
        existing_procedures = {"linear_ebus": {"performed": True}}

        procedures, warnings = derive_procedures_from_granular(granular_data, existing_procedures)

        assert procedures["linear_ebus"]["stations_sampled"] == ["7", "11L"]

    def test_bal_derivation_from_specimens(self):
        """Test that BAL specimens populate procedures_performed.bal."""
        from modules.registry.schema_granular import derive_procedures_from_granular

        granular_data = {
            "specimens_collected": [
                {"source_procedure": "BAL", "source_location": "LLL Posterior-Basal Segment"},
                {"source_procedure": "BAL", "source_location": "mini-BAL"},
            ]
        }
        existing_procedures = {}

        procedures, warnings = derive_procedures_from_granular(granular_data, existing_procedures)

        assert procedures["bal"]["performed"] is True
        assert procedures["bal"]["location"] == "LLL Posterior-Basal Segment"

    def test_brushings_derivation_from_specimens(self):
        """Test that Brushing specimens populate procedures_performed.brushings."""
        from modules.registry.schema_granular import derive_procedures_from_granular

        granular_data = {
            "specimens_collected": [
                {"source_procedure": "Brushing", "source_location": "LLL Posterior-Basal Segment", "specimen_count": 1},
            ]
        }
        existing_procedures = {}

        procedures, warnings = derive_procedures_from_granular(granular_data, existing_procedures)

        assert procedures["brushings"]["performed"] is True
        assert procedures["brushings"]["locations"] == ["LLL Posterior-Basal Segment"]
        assert procedures["brushings"]["number_of_samples"] == 1

    def test_sampling_tools_union(self):
        """Test that sampling_tools_used is derived from navigation_targets."""
        from modules.registry.schema_granular import derive_procedures_from_granular

        granular_data = {
            "navigation_targets": [
                {
                    "target_number": 1,
                    "target_location_text": "LLL",
                    "sampling_tools_used": ["Needle (21G)", "Needle (23G)", "1.1mm cryoprobe", "Protected brush"],
                }
            ]
        }
        existing_procedures = {"navigational_bronchoscopy": {"performed": True, "sampling_tools_used": []}}

        procedures, warnings = derive_procedures_from_granular(granular_data, existing_procedures)

        tools = procedures["navigational_bronchoscopy"]["sampling_tools_used"]
        assert "Needle" in tools
        assert "Cryoprobe" in tools
        assert "Brush" in tools

    def test_clears_cryoprobe_forceps_type(self):
        """Test that forceps_type='Cryoprobe' is cleared when cryobiopsy_sites exists."""
        from modules.registry.schema_granular import derive_procedures_from_granular

        granular_data = {
            "cryobiopsy_sites": [
                {"site_number": 1, "lobe": "LLL", "number_of_biopsies": 5}
            ]
        }
        existing_procedures = {
            "transbronchial_biopsy": {
                "performed": True,
                "forceps_type": "Cryoprobe",  # Incorrect - should be cleared
            }
        }

        procedures, warnings = derive_procedures_from_granular(granular_data, existing_procedures)

        # Cryoprobe should be cleared from TBBx
        assert procedures["transbronchial_biopsy"]["forceps_type"] is None
        # And cryobiopsy should be populated instead
        assert procedures["transbronchial_cryobiopsy"]["performed"] is True


class TestTherapeuticAspirationNormalization:
    """Tests for therapeutic aspiration vs transbronchial biopsy normalization."""

    def test_airway_locations_become_therapeutic_aspiration(self):
        """Test that airway locations are moved from TBBx to therapeutic_aspiration."""
        from modules.api.normalization import normalize_registry_payload

        payload = {
            "procedures_performed": {
                "transbronchial_biopsy": {
                    "performed": True,
                    "locations": ["RMS", "LMS", "BI", "RUL", "RML", "LUL", "LLL"],
                }
            }
        }

        result = normalize_registry_payload(payload)

        # TBBx should be cleared (all locations were airways)
        assert result["procedures_performed"]["transbronchial_biopsy"]["performed"] is False

        # Therapeutic aspiration should be set
        assert result["procedures_performed"]["therapeutic_aspiration"]["performed"] is True
        assert "Mucus plug" in result["procedures_performed"]["therapeutic_aspiration"]["material"]

    def test_parenchymal_locations_stay_as_tbbx(self):
        """Test that parenchymal locations remain as transbronchial_biopsy."""
        from modules.api.normalization import normalize_registry_payload

        payload = {
            "procedures_performed": {
                "transbronchial_biopsy": {
                    "performed": True,
                    "locations": ["LLL posterior basal segment"],
                }
            }
        }

        result = normalize_registry_payload(payload)

        # TBBx should remain
        assert result["procedures_performed"]["transbronchial_biopsy"]["performed"] is True
        assert "LLL posterior basal segment" in result["procedures_performed"]["transbronchial_biopsy"]["locations"]


class TestRobotNavigationEBUSRegression:
    """Regression test for robot-assisted navigation + EBUS bronchoscopy case.

    This test uses the sample note from the user's bug report to ensure
    all procedure fields are correctly derived from granular data.
    """

    def test_full_registry_derivation(self):
        """Test complete registry derivation for navigation + EBUS case."""
        from modules.api.normalization import normalize_registry_payload

        # Simulate the granular data that the LLM correctly extracts
        payload = {
            "procedures_performed": {
                "linear_ebus": {
                    "performed": True,
                    "stations_sampled": None,  # Not set by LLM
                    "needle_gauge": 22,
                },
                "radial_ebus": {
                    "performed": None,  # Not set by LLM
                    "probe_position": "Concentric",
                },
                "navigational_bronchoscopy": {
                    "performed": True,
                    "tool_in_lesion_confirmed": True,
                    "sampling_tools_used": [],  # Empty - should be derived
                },
                "transbronchial_biopsy": {
                    "performed": True,
                    "locations": ["RMS", "LMS", "BI", "RUL", "RML", "LUL", "LLL"],  # Incorrectly set
                    "number_of_samples": 5,
                    "forceps_type": "Cryoprobe",  # Incorrect
                },
                "transbronchial_cryobiopsy": None,  # Not set by LLM
                "bal": None,  # Not set by LLM
                "brushings": None,  # Not set by LLM
                "therapeutic_aspiration": None,  # Not set by LLM
            },
            "granular_data": {
                "linear_ebus_stations_detail": [
                    {"station": "7", "sampled": True},
                    {"station": "11L", "sampled": True},
                ],
                "navigation_targets": [
                    {
                        "target_number": 1,
                        "target_location_text": "Posterior-Basal Segment of LLL (LB10)",
                        "target_lobe": "LLL",
                        "rebus_used": True,
                        "rebus_view": "Concentric",
                        "tool_in_lesion_confirmed": True,
                        "confirmation_method": "CBCT",
                        "sampling_tools_used": [
                            "Needle (21G)",
                            "Needle (23G)",
                            "1.1mm cryoprobe",
                            "Protected cytology brush",
                        ],
                        "number_of_needle_passes": 6,
                        "number_of_cryo_biopsies": 5,
                    }
                ],
                "cryobiopsy_sites": [
                    {
                        "site_number": 1,
                        "lobe": "LLL",
                        "segment": "Posterior-Basal",
                        "probe_size_mm": 1.1,
                        "freeze_time_seconds": 6,
                        "number_of_biopsies": 5,
                    }
                ],
                "specimens_collected": [
                    {"specimen_number": 1, "source_procedure": "Navigation biopsy", "source_location": "LLL"},
                    {"specimen_number": 2, "source_procedure": "Transbronchial cryobiopsy", "source_location": "LLL"},
                    {"specimen_number": 3, "source_procedure": "Brushing", "source_location": "LLL Posterior-Basal"},
                    {"specimen_number": 4, "source_procedure": "BAL", "source_location": "mini-BAL"},
                    {"specimen_number": 5, "source_procedure": "BAL", "source_location": "LLL Posterior-Basal (LB10)"},
                ],
            },
        }

        result = normalize_registry_payload(payload)
        procs = result["procedures_performed"]

        # 1. Therapeutic aspiration should be set (airway locations moved from TBBx)
        assert procs["therapeutic_aspiration"]["performed"] is True

        # 2. Transbronchial biopsy should be cleared (was incorrectly set)
        assert procs["transbronchial_biopsy"]["performed"] is False
        assert procs["transbronchial_biopsy"]["forceps_type"] is None

        # 3. Transbronchial cryobiopsy should be derived from cryobiopsy_sites
        assert procs["transbronchial_cryobiopsy"]["performed"] is True
        assert procs["transbronchial_cryobiopsy"]["number_of_samples"] == 5
        assert procs["transbronchial_cryobiopsy"]["probe_size_mm"] == 1.1

        # 4. Radial EBUS should have performed=True (derived from navigation_targets)
        assert procs["radial_ebus"]["performed"] is True
        assert procs["radial_ebus"]["probe_position"] == "Concentric"

        # 5. Linear EBUS stations_sampled should be derived
        assert procs["linear_ebus"]["stations_sampled"] == ["7", "11L"]

        # 6. BAL should be derived from specimens
        assert procs["bal"]["performed"] is True

        # 7. Brushings should be derived from specimens
        assert procs["brushings"]["performed"] is True

        # 8. Sampling tools should be derived from navigation_targets
        tools = procs["navigational_bronchoscopy"]["sampling_tools_used"]
        assert len(tools) > 0
        assert "Needle" in tools or any("needle" in t.lower() for t in tools)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
