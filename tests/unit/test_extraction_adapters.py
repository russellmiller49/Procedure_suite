import pytest

from proc_registry.adapters.airway import (
    BALAdapter,
    BLVRValvePlacementAdapter,
    BPFLocalizationAdapter,
    BPFSealantApplicationAdapter,
    BPFValvePlacementAdapter,
    BronchialWashingAdapter,
    BronchoscopyShellAdapter,
    CBCTFusionAdapter,
    EBUSTBNAAdapter,
    EMNAdapter,
    IonRegistrationCompleteAdapter,
    RadialEBUSSamplingAdapter,
    RadialEBUSSurveyAdapter,
    RoboticNavigationAdapter,
    RoboticIonBronchoscopyAdapter,
    RoboticMonarchBronchoscopyAdapter,
    ToolInLesionConfirmationAdapter,
    WholeLungLavageAdapter,
)
from proc_registry.adapters.pleural import (
    ChestTubeAdapter,
    ParacentesisAdapter,
    PegExchangeAdapter,
    PegPlacementAdapter,
    PigtailCatheterAdapter,
    ThoracentesisAdapter,
    ThoracentesisManometryAdapter,
    TransthoracicNeedleBiopsyAdapter,
    TunneledPleuralCatheterInsertAdapter,
    TunneledPleuralCatheterRemoveAdapter,
)
from proc_schemas.clinical import airway as airway_schemas
from proc_schemas.clinical import pleural as pleural_schemas


def test_bronchoscopy_shell_adapter():
    source = {
        "airway_overview": "Survey completed",
        "right_lung_overview": "Clear",
        "left_lung_overview": "Clear",
    }
    model = BronchoscopyShellAdapter.extract(source)
    assert isinstance(model, airway_schemas.BronchoscopyShell)
    assert model.airway_overview == "Survey completed"


def test_navigation_adapters_for_ion_and_emn():
    emn_source = {
        "nav_platform": "EMN",
        "nav_registration_method": "fluoro",
        "nav_target_segment": "RUL",
        "nav_imaging_verification": "Cone Beam CT",
        "nav_lesion_size_cm": 1.2,
    }
    emn = EMNAdapter.extract(emn_source)
    assert isinstance(emn, airway_schemas.EMNBronchoscopy)
    assert emn.target_lung_segment == "RUL"
    assert emn.registration_method == "fluoro"

    ion_source = {
        "nav_platform": "ion",
        "ventilation_mode": "VC",
        "vent_rr": 12,
        "vent_tv_ml": 500,
        "vent_peep_cm_h2o": 8,
        "vent_fio2_pct": 40,
        "nav_registration_method": "fiducial",
        "nav_imaging_verification": "Cone Beam CT",
        "nav_rebus_view": "concentric",
    }
    ion = RoboticIonBronchoscopyAdapter.extract(ion_source)
    assert isinstance(ion, airway_schemas.RoboticIonBronchoscopy)
    assert ion.vent_mode == "VC"
    assert ion.cbct_performed is True

    reg = IonRegistrationCompleteAdapter.extract(ion_source)
    assert isinstance(reg, airway_schemas.IonRegistrationComplete)
    assert reg.method == "fiducial"

    fusion = CBCTFusionAdapter.extract(ion_source)
    assert isinstance(fusion, airway_schemas.CBCTFusion)
    assert fusion.overlay_result == "Cone Beam CT"

    navigation = RoboticNavigationAdapter.extract(ion_source)
    assert isinstance(navigation, airway_schemas.RoboticNavigation)
    assert navigation.platform == "Ion"
    assert navigation.registration_method == "fiducial"

    monarch = RoboticMonarchBronchoscopyAdapter.extract({"nav_platform": "Monarch", "nav_rebus_view": "eccentric"})
    assert isinstance(monarch, airway_schemas.RoboticMonarchBronchoscopy)
    assert monarch.radial_pattern == "eccentric"


def test_ebus_and_tool_adapters():
    survey = RadialEBUSSurveyAdapter.extract({"nav_rebus_used": True, "nav_target_segment": "RLL"})
    assert isinstance(survey, airway_schemas.RadialEBUSSurvey)
    assert survey.location == "RLL"

    sampling = RadialEBUSSamplingAdapter.extract({"nav_sampling_tools": ["forceps"], "nav_rebus_view": "concentric"})
    assert isinstance(sampling, airway_schemas.RadialEBUSSampling)
    assert sampling.sampling_tools == ["forceps"]

    tool = ToolInLesionConfirmationAdapter.extract({"nav_tool_in_lesion": True, "nav_imaging_verification": "fluoro"})
    assert isinstance(tool, airway_schemas.ToolInLesionConfirmation)
    assert tool.confirmation_method == "fluoro"

    ebus = EBUSTBNAAdapter.extract(
        {
            "ebus_stations_sampled": ["4R", "7"],
            "ebus_passes": 3,
            "ebus_echo_features": "heterogeneous",
            "ebus_rose_result": "adequate",
            "lesion_size_mm": 18,
            "ebus_intranodal_forceps_used": True,
        }
    )
    assert isinstance(ebus, airway_schemas.EBUSTBNA)
    assert len(ebus.stations) == 2
    assert ebus.stations[0].station_name == "4R"
    assert ebus.stations[0].size_mm is None
    assert ebus.stations[0].passes == 3
    assert "Forceps" in ebus.stations[0].biopsy_tools


def test_whole_lung_lavage_and_blvr_adapters():
    lavage = WholeLungLavageAdapter.extract(
        {
            "wll_volume_instilled_l": 5.0,
            "wll_side": "left",
            "wll_dlt_used_size": 39,
            "wll_num_cycles": 2,
        }
    )
    assert isinstance(lavage, airway_schemas.WholeLungLavage)
    assert lavage.total_volume_l == 5.0
    assert lavage.num_cycles == 2

    blvr = BLVRValvePlacementAdapter.extract({"blvr_valve_type": "Zephyr", "blvr_number_of_valves": 2, "blvr_target_lobe": "LUL"})
    assert isinstance(blvr, airway_schemas.BLVRValvePlacement)
    assert len(blvr.valves) == 2
    assert blvr.lobes_treated == ["LUL"]


@pytest.mark.parametrize(
    ("adapter_cls", "source_key", "payload", "expected_cls"),
    [
        (BPFLocalizationAdapter, "bpf_localization", {"culprit_segment": "RB6"}, airway_schemas.BPFLocalizationOcclusion),
        (BPFValvePlacementAdapter, "bpf_valve_placement", {"culprit_location": "RB6"}, airway_schemas.BPFValvePlacement),
        (BPFSealantApplicationAdapter, "bpf_sealant_application", {"sealant_type": "fibrin"}, airway_schemas.BPFSealantApplication),
        (
            BronchialWashingAdapter,
            "bronchial_washing",
            {"airway_segment": "RML", "instilled_volume_ml": 20, "returned_volume_ml": 10, "tests": ["cytology"]},
            airway_schemas.BronchialWashing,
        ),
        (
            BALAdapter,
            "bal",
            {"lung_segment": "RLL", "instilled_volume_cc": 100, "returned_volume_cc": 60, "tests": ["culture"]},
            airway_schemas.BAL,
        ),
    ],
)
def test_dict_payload_adapters(adapter_cls, source_key, payload, expected_cls):
    model = adapter_cls.extract({source_key: payload})
    assert isinstance(model, expected_cls)


def test_thoracentesis_adapters():
    base_source = {
        "pleural_procedure_type": "thoracentesis",
        "pleural_volume_drained_ml": 900,
        "pleural_fluid_appearance": "serous",
        "intercostal_space": "7th",
        "entry_location": "mid-axillary",
        "pleural_side": "left",
        "specimen_tests": ["cell count"],
    }
    detailed = ThoracentesisAdapter.extract(base_source)
    assert isinstance(detailed, pleural_schemas.ThoracentesisDetailed)
    assert detailed.side == "left"
    assert detailed.volume_removed_ml == 900

    manometry_source = {
        **base_source,
        "pleural_opening_pressure_measured": True,
        "pleural_opening_pressure_cmh2o": -6,
        "pleural_pressure_readings": ["-6"],
        "pleural_stopping_criteria": "lightheaded",
    }
    manometry = ThoracentesisManometryAdapter.extract(manometry_source)
    assert isinstance(manometry, pleural_schemas.ThoracentesisManometry)
    assert manometry.total_removed_ml == 900
    assert manometry.opening_pressure_cmh2o == -6


def test_chest_tube_and_catheters():
    chest = ChestTubeAdapter.extract(
        {
            "pleural_procedure_type": "chest tube",
            "pleural_side": "right",
            "intercostal_space": "6th",
            "entry_location": "mid-axillary",
            "pleural_volume_drained_ml": 300,
            "pleural_fluid_appearance": "serosanguinous",
        }
    )
    assert isinstance(chest, pleural_schemas.ChestTube)
    assert chest.side == "right"

    tpc = TunneledPleuralCatheterInsertAdapter.extract(
        {
            "pleural_procedure_type": "tunneled catheter",
            "pleural_side": "left",
            "intercostal_space": "5th",
            "entry_location": "anterior",
            "tunnel_length_cm": 8,
        }
    )
    assert isinstance(tpc, pleural_schemas.TunneledPleuralCatheterInsert)
    assert tpc.tunnel_length_cm == 8

    pigtail = PigtailCatheterAdapter.extract(
        {
            "pleural_procedure_type": "pigtail catheter",
            "pleural_side": "right",
            "intercostal_space": "6th",
            "entry_location": "mid-axillary",
            "size_fr": "10",
            "pleural_volume_drained_ml": 200,
            "pleural_fluid_appearance": "straw",
        }
    )
    assert isinstance(pigtail, pleural_schemas.PigtailCatheter)
    assert pigtail.size_fr == "10"


def test_other_pleural_adapters():
    paracentesis = ParacentesisAdapter.extract({"paracentesis_performed": True, "paracentesis_volume_ml": 700})
    assert isinstance(paracentesis, pleural_schemas.Paracentesis)
    assert paracentesis.volume_removed_ml == 700

    peg = PegPlacementAdapter.extract({"peg_placed": True, "peg_size_fr": 14})
    assert isinstance(peg, pleural_schemas.PEGPlacement)
    assert peg.tube_size_fr == 14

    exchange = PegExchangeAdapter.extract({"peg_exchanged": True, "peg_size_fr": 16})
    assert isinstance(exchange, pleural_schemas.PEGExchange)
    assert exchange.new_tube_size_fr == 16

    removal = TunneledPleuralCatheterRemoveAdapter.extract({"tunneled_pleural_catheter_remove": {"side": "right"}})
    assert isinstance(removal, pleural_schemas.TunneledPleuralCatheterRemove)
    assert removal.side == "right"

    ttnb = TransthoracicNeedleBiopsyAdapter.extract(
        {"transthoracic_needle_biopsy": {"needle_gauge": "18G", "samples_collected": 2}}
    )
    assert isinstance(ttnb, pleural_schemas.TransthoracicNeedleBiopsy)
    assert ttnb.samples_collected == 2
