from __future__ import annotations

from dataclasses import dataclass

from proc_schemas.coding import CodeSuggestion, CodingResult
from proc_schemas.reasoning import ReasoningFields

from app.api.coder_adapter import convert_coding_result_to_coder_output


@dataclass(frozen=True)
class _ProcInfo:
    description: str
    work_rvu: float
    facility_pe_rvu: float
    malpractice_rvu: float
    total_facility_rvu: float


class _StubKBRepo:
    def __init__(self, info_by_cpt: dict[str, _ProcInfo]):
        self._info_by_cpt = dict(info_by_cpt)

    def get_procedure_info(self, cpt: str):  # type: ignore[no-untyped-def]
        return self._info_by_cpt.get(cpt)


def test_ncci_bundled_codes_excluded_from_financials_and_billable_codes() -> None:
    kb_repo = _StubKBRepo(
        {
            "31652": _ProcInfo(
                description="EBUS-TBNA (1-2 stations)",
                work_rvu=10.0,
                facility_pe_rvu=0.0,
                malpractice_rvu=0.0,
                total_facility_rvu=20.0,
            ),
            "31645": _ProcInfo(
                description="Therapeutic aspiration",
                work_rvu=5.0,
                facility_pe_rvu=0.0,
                malpractice_rvu=0.0,
                total_facility_rvu=6.0,
            ),
            "31646": _ProcInfo(
                description="Subsequent aspiration",
                work_rvu=7.0,
                facility_pe_rvu=0.0,
                malpractice_rvu=0.0,
                total_facility_rvu=8.0,
            ),
        }
    )

    ncci_note = (
        "NCCI_BUNDLE: 31645 bundled into 31652 - "
        "Therapeutic aspiration is bundled into EBUS-TBNA (1-2 stations)"
    )
    result = CodingResult(
        procedure_id="proc_1",
        suggestions=[
            CodeSuggestion(
                code="31652",
                description="EBUS-TBNA (1-2 stations)",
                source="rule",
                hybrid_decision="kept_rule_priority",
                final_confidence=0.95,
                reasoning=ReasoningFields(ncci_notes=ncci_note),
            ),
            CodeSuggestion(
                code="31645",
                description="Therapeutic aspiration",
                source="rule",
                hybrid_decision="rejected_hybrid",
                final_confidence=0.5,
                reasoning=ReasoningFields(ncci_notes=ncci_note),
            ),
            CodeSuggestion(
                code="31646",
                description="Subsequent aspiration",
                source="rule",
                hybrid_decision="rejected_hybrid",
                final_confidence=0.5,
                reasoning=ReasoningFields(ncci_notes=ncci_note),
            ),
        ],
    )

    output = convert_coding_result_to_coder_output(
        result=result,
        kb_repo=kb_repo,  # enables financials computation
        locality="00",
        conversion_factor=1.0,
    )

    billed = {c.cpt for c in output.codes}
    assert billed == {"31652"}

    assert output.financials is not None
    per_code = {row.cpt_code for row in output.financials.per_code}
    assert per_code == {"31652"}

    assert output.financials.total_work_rvu == 10.0
    assert output.financials.total_facility_payment == 20.0

