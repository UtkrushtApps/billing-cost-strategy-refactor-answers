from collections.abc import Mapping

from .models import InsurancePlan, Visit
from .plan_type import PlanType
from .pricing_rules import (
    HighDeductiblePricingRule,
    HmoPricingRule,
    PpoPricingRule,
    PricingRule,
    SelfPayPricingRule,
)


DEFAULT_PRICING_RULES: dict[PlanType, PricingRule] = {
    PlanType.HMO: HmoPricingRule(),
    PlanType.PPO: PpoPricingRule(),
    PlanType.HIGH_DEDUCTIBLE: HighDeductiblePricingRule(),
    PlanType.SELF_PAY: SelfPayPricingRule(),
}


class BillingService:
    """Computes the patient's out-of-pocket cost for a visit."""

    def __init__(
        self, pricing_rules: Mapping[PlanType, PricingRule] | None = None
    ) -> None:
        self._pricing_rules = dict(
            DEFAULT_PRICING_RULES if pricing_rules is None else pricing_rules
        )

    def calculate_patient_cost(self, plan: InsurancePlan, visit: Visit) -> float:
        try:
            pricing_rule = self._pricing_rules[plan.plan_type]
        except KeyError as exc:
            raise ValueError(
                f"No pricing rule registered for plan type: {plan.plan_type!r}"
            ) from exc

        return pricing_rule.calculate(plan, visit)

