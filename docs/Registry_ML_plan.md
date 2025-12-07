I've created a comprehensive plan for wiring the ML process for registry fields using the golden extraction data. The plan follows the existing patterns in your codebase (mirroring how CPT code prediction works) and includes: Summary:
Phase 1: Extend data_prep.py to extract ~29 boolean procedure flags from golden extractions
Phase 2: Create RegistryMLPredictor class (mirrors MLCoderPredictor pattern)
Phase 3: Create training pipeline with same TF-IDF + Calibrated LR architecture
Phase 4: Integrate into RegistryService alongside existing CPT mapping
Phase 5: Add comprehensive tests
Key design decisions:
ML predicts procedures_performed.<proc>.performed booleans directly (not derived from CPT)
Only HIGH_CONF predictions are used to bootstrap fields
CPT-derived fields have priority over ML predictions
LLM still fills in detailed sub-fields (locations, counts, granular data)
Claude’s Plan
ML Training for Registry Fields - Implementation Plan
Goal
Train ML models to predict registry boolean procedure flags directly from note text, enabling an ML-first approach for registry extraction similar to the existing CPT code prediction.
Architecture Overview
Current:  Note Text --> ML Coder --> CPT Codes --> CPT-Registry Mapping --> Registry Fields
                                                          |
                                                          v
                                                    LLM Extractor (details)

Proposed: Note Text --> Registry ML Predictor --> procedure boolean flags (HIGH_CONF)
                |                                         |
                v                                         v
          ML Coder (CPT)                        Merge with CPT-derived fields
                |                                         |
                v                                         v
          CPT-Registry Mapping --> hints --> LLM Extractor (details)
The ML predictor predicts procedures_performed.<proc>.performed = True/False directly, complementing (not replacing) CPT-based mapping.
Target Registry Fields (~29 boolean flags)
procedures_performed (22 fields)
diagnostic_bronchoscopy, bal, bronchial_wash, brushings
endobronchial_biopsy, tbna_conventional, linear_ebus, radial_ebus
navigational_bronchoscopy, transbronchial_biopsy, transbronchial_cryobiopsy
therapeutic_aspiration, foreign_body_removal, airway_dilation, airway_stent
thermal_ablation, cryotherapy, blvr, peripheral_ablation
bronchial_thermoplasty, whole_lung_lavage, rigid_bronchoscopy
pleural_procedures (7 fields)
thoracentesis, chest_tube, ipc, medical_thoracoscopy
pleurodesis, pleural_biopsy, fibrinolytic_therapy
Implementation Phases
Phase 1: Data Preparation Extension
Modify: modules/ml_coder/data_prep.py
Add constants for registry procedure fields:
PROCEDURE_FIELDS = ["diagnostic_bronchoscopy", "bal", "linear_ebus", ...]
PLEURAL_FIELDS = ["thoracentesis", "chest_tube", "ipc", ...]
Add function _extract_registry_booleans(entry: dict) -> dict[str, bool]:
Extract .performed flag from registry_entry.procedures_performed.<field>
Extract .performed flag from registry_entry.pleural_procedures.<field>
Return dict with prefixed keys: proc_linear_ebus, pleural_thoracentesis
Add function _build_registry_dataframe() -> pd.DataFrame:
Similar to _build_dataframe() but extracts registry booleans
Columns: note_text, registry_labels (comma-separated), MRN, date
Add function prepare_registry_training_splits():
Output: data/ml_training/registry_train.csv, registry_test.csv
Phase 2: Registry ML Predictor
Create: modules/ml_coder/registry_predictor.py
Dataclasses (mirror CPT predictor pattern):
@dataclass
class RegistryFieldPrediction:
    field: str  # e.g., "proc_linear_ebus"
    prob: float

@dataclass
class RegistryFieldClassification:
    predictions: list[RegistryFieldPrediction]
    high_conf: list[RegistryFieldPrediction]
    gray_zone: list[RegistryFieldPrediction]
    difficulty: CaseDifficulty
RegistryMLPredictor class:
__init__(model_path, mlb_path, thresholds) - Load artifacts
predict_proba(note_text) -> list[RegistryFieldPrediction]
classify_case(note_text) -> RegistryFieldClassification
get_predicted_fields(note_text, threshold) -> dict[str, bool]
Phase 3: Training Pipeline
Create: modules/ml_coder/registry_training.py
train_registry_model(csv_path):
Load registry training CSV
Build TF-IDF + Calibrated LogisticRegression pipeline (same architecture as CPT)
Save to data/models/registry_classifier.pkl, registry_mlb.pkl
evaluate_registry_model(test_csv):
Per-field precision/recall/F1
Macro/micro averages
Save to data/models/registry_metrics.json
optimize_registry_thresholds():
Find optimal per-field thresholds
Save to data/models/registry_thresholds.json
Create: modules/ml_coder/registry_thresholds.py
RegistryThresholds dataclass (same pattern as thresholds.py)
Phase 4: Integration with Registry Service
Modify: modules/registry/application/registry_service.py
Add optional registry_ml_predictor: RegistryMLPredictor to __init__
Add method _get_ml_predicted_fields(note_text) -> dict:
Call registry_ml.classify_case(note_text)
Return nested dict with only HIGH_CONF predictions:
{
  "procedures_performed": {"linear_ebus": {"performed": True}, ...},
  "pleural_procedures": {"thoracentesis": {"performed": True}, ...}
}
Modify extract_fields():
Get ML predictions via _get_ml_predicted_fields()
Merge with CPT-mapped fields (CPT has priority over ML)
Pass merged hints to LLM extractor
Modify: modules/api/dependencies.py
Add build_registry_ml_predictor() factory
Wire into RegistryService initialization
Phase 5: Testing
Create: tests/ml_coder/test_registry_predictor.py
Unit tests for RegistryMLPredictor
Mock model for fast tests
Create: tests/ml_coder/test_registry_data_prep.py
Test _extract_registry_booleans() with various entry formats
Test stratified split maintains label distribution
Modify: tests/registry/test_registry_service_hybrid_flow.py
Add tests for ML-predicted registry fields integration
File Summary
File	Action	Description
modules/ml_coder/data_prep.py	Modify	Add registry field extraction
modules/ml_coder/registry_predictor.py	Create	RegistryMLPredictor class
modules/ml_coder/registry_training.py	Create	Training pipeline
modules/ml_coder/registry_thresholds.py	Create	Threshold configuration
modules/registry/application/registry_service.py	Modify	Integration point
modules/api/dependencies.py	Modify	Factory function
tests/ml_coder/test_registry_predictor.py	Create	Unit tests
tests/ml_coder/test_registry_data_prep.py	Create	Data prep tests
Model Artifacts
data/models/
  registry_classifier.pkl     # Trained sklearn pipeline
  registry_mlb.pkl           # MultiLabelBinarizer
  registry_thresholds.json   # Per-field thresholds
  registry_metrics.json      # Evaluation metrics
Key Design Decisions
Separate model from CPT coder: Registry fields are independent predictions, not derived from CPT
Same architecture: TF-IDF + Calibrated LR works well; no need to change
HIGH_CONF only for bootstrapping: Only use confident predictions to seed fields
CPT mapping has priority: If CPT evidence contradicts ML prediction, CPT wins
LLM fills details: ML only predicts boolean flags; LLM extracts locations, counts, etc.
Execution Order
Phase 1: Data preparation (extend data_prep.py)
Phase 2: Create registry_predictor.py
Phase 3: Create registry_training.py and train initial model
Phase 4: Integrate into RegistryService
Phase 5: Add tests