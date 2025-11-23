from __future__ import annotations

from typing import Any, List

from pydantic import BaseModel, ConfigDict, Field, SerializeAsAny


class PatientInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")
    name: str | None = None
    age: int | None = None
    sex: str | None = None
    patient_id: str | None = None
    mrn: str | None = None


class EncounterInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")
    date: str | None = None
    encounter_id: str | None = None
    location: str | None = None
    referred_physician: str | None = None
    attending: str | None = None
    assistant: str | None = None


class SedationInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")
    type: str | None = None
    description: str | None = None


class AnesthesiaInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")
    type: str | None = None
    description: str | None = None


class PreAnesthesiaAssessment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    anticoagulant_use: str | None = None
    prophylactic_antibiotics: bool | None = None
    asa_status: str
    anesthesia_plan: str
    sedation_history: str | None = None
    time_out_confirmed: bool | None = None


class OperativeShellInputs(BaseModel):
    model_config = ConfigDict(extra="ignore")
    indication_text: str | None = None
    preop_diagnosis_text: str | None = None
    postop_diagnosis_text: str | None = None
    procedures_summary: str | None = None
    cpt_summary: str | None = None
    estimated_blood_loss: str | None = None
    complications_text: str | None = None
    specimens_text: str | None = None
    impression_plan: str | None = None


class ProcedureInput(BaseModel):
    model_config = ConfigDict(extra="ignore")
    proc_type: str
    schema_id: str
    proc_id: str | None = None
    data: SerializeAsAny[dict[str, Any] | BaseModel]
    cpt_candidates: List[str | int] = Field(default_factory=list)


class ProcedureBundle(BaseModel):
    model_config = ConfigDict(extra="ignore")
    patient: PatientInfo
    encounter: EncounterInfo
    procedures: List[ProcedureInput]
    sedation: SedationInfo | None = None
    anesthesia: AnesthesiaInfo | None = None
    pre_anesthesia: PreAnesthesiaAssessment | dict[str, Any] | None = None
    indication_text: str | None = None
    preop_diagnosis_text: str | None = None
    postop_diagnosis_text: str | None = None
    impression_plan: str | None = None
    estimated_blood_loss: str | None = None
    complications_text: str | None = None
    specimens_text: str | None = None
    free_text_hint: str | None = None
    acknowledged_omissions: dict[str, list[str]] = Field(default_factory=dict)


class ProcedurePatch(BaseModel):
    model_config = ConfigDict(extra="ignore")
    proc_id: str
    updates: dict[str, Any] = Field(default_factory=dict)
    acknowledge_missing: list[str] = Field(default_factory=list)


class BundlePatch(BaseModel):
    model_config = ConfigDict(extra="ignore")
    procedures: list[ProcedurePatch]


__all__ = [
    "PatientInfo",
    "EncounterInfo",
    "SedationInfo",
    "AnesthesiaInfo",
    "PreAnesthesiaAssessment",
    "OperativeShellInputs",
    "ProcedureInput",
    "ProcedureBundle",
    "ProcedurePatch",
    "BundlePatch",
]
