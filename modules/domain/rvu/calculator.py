"""RVU (Relative Value Unit) calculation logic."""

from __future__ import annotations

from dataclasses import dataclass

from modules.domain.knowledge_base.repository import KnowledgeBaseRepository


@dataclass(frozen=True)
class RVUResult:
    """RVU calculation result for a single code."""

    code: str
    work_rvu: float
    facility_pe_rvu: float
    malpractice_rvu: float
    total_facility_rvu: float
    total_nonfacility_rvu: float
    facility_payment: float
    nonfacility_payment: float


class RVUCalculator:
    """Calculator for RVU-based payments.

    Uses the CMS conversion factor to convert RVUs to dollar amounts.
    """

    # 2025 CMS Conversion Factor
    DEFAULT_CONVERSION_FACTOR = 32.7442

    def __init__(
        self,
        kb_repo: KnowledgeBaseRepository,
        conversion_factor: float | None = None,
    ):
        self.kb_repo = kb_repo
        self.conversion_factor = conversion_factor or self.DEFAULT_CONVERSION_FACTOR

    def calculate(self, code: str) -> RVUResult | None:
        """Calculate RVU-based payments for a code.

        Args:
            code: The CPT code to calculate.

        Returns:
            RVUResult with payment calculations, or None if code not found.
        """
        info = self.kb_repo.get_procedure_info(code)
        if not info:
            return None

        # Calculate facility payment
        facility_payment = info.total_facility_rvu * self.conversion_factor

        # Non-facility RVU typically includes higher practice expense
        # For now, use total_facility as proxy if not separately stored
        total_nonfacility_rvu = info.raw_data.get(
            "total_nonfacility_rvu", info.total_facility_rvu * 1.2
        )
        nonfacility_payment = total_nonfacility_rvu * self.conversion_factor

        return RVUResult(
            code=code,
            work_rvu=info.work_rvu,
            facility_pe_rvu=info.facility_pe_rvu,
            malpractice_rvu=info.malpractice_rvu,
            total_facility_rvu=info.total_facility_rvu,
            total_nonfacility_rvu=total_nonfacility_rvu,
            facility_payment=facility_payment,
            nonfacility_payment=nonfacility_payment,
        )

    def calculate_batch(self, codes: list[str]) -> list[RVUResult]:
        """Calculate RVU-based payments for multiple codes.

        Args:
            codes: List of CPT codes to calculate.

        Returns:
            List of RVUResult objects (codes not found are omitted).
        """
        results = []
        for code in codes:
            result = self.calculate(code)
            if result:
                results.append(result)
        return results
