from abc import ABC, abstractmethod

from .models import InsurancePlan, Visit


class PricingRule(ABC):
    """Strategy interface for calculating a patient's out-of-pocket visit cost."""

    @abstractmethod
    def calculate(self, plan: InsurancePlan, visit: Visit) -> float:
        """Return the patient's cost for the given plan and visit."""

    @staticmethod
    def _round_capped_at_gross(cost: float, gross: float) -> float:
        """Round to cents and ensure insurance math never charges more than the visit."""
        return round(min(cost, gross), 2)

    @staticmethod
    def _amount_after_deductible(gross: float, deductible_remaining: float) -> float:
        """Return the portion of the visit charge left after applying the deductible."""
        return max(gross - deductible_remaining, 0.0)

    @classmethod
    def _deductible_plus_coinsurance(cls, plan: InsurancePlan, gross: float) -> float:
        """Shared deductible/coinsurance arithmetic used by insured plan rules."""
        after_deductible = cls._amount_after_deductible(
            gross, plan.deductible_remaining
        )
        patient_share = after_deductible * plan.coinsurance_rate
        return plan.deductible_remaining + patient_share


class CopayDeductibleCoinsuranceRule(PricingRule):
    """Base rule for plans that apply copay, deductible, then coinsurance."""

    def calculate(self, plan: InsurancePlan, visit: Visit) -> float:
        gross = visit.gross_charge
        cost = plan.copay + self._deductible_plus_coinsurance(plan, gross)
        return self._round_capped_at_gross(cost, gross)


class HmoPricingRule(CopayDeductibleCoinsuranceRule):
    """HMO: flat copay, deductible, then coinsurance on the remaining charge."""


class PpoPricingRule(CopayDeductibleCoinsuranceRule):
    """PPO: flat copay, deductible, then coinsurance on the remaining charge."""


class HighDeductiblePricingRule(PricingRule):
    """High deductible: full charge until deductible is met, then coinsurance."""

    def calculate(self, plan: InsurancePlan, visit: Visit) -> float:
        gross = visit.gross_charge

        if gross <= plan.deductible_remaining:
            return round(gross, 2)

        cost = self._deductible_plus_coinsurance(plan, gross)
        return self._round_capped_at_gross(cost, gross)


class SelfPayPricingRule(PricingRule):
    """Self-pay: the patient owes the full visit charge, with no insurance copay."""

    def calculate(self, plan: InsurancePlan, visit: Visit) -> float:
        return round(visit.gross_charge, 2)

