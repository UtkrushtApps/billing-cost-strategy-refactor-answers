from dataclasses import dataclass

from .plan_type import PlanType


@dataclass(frozen=True)
class InsurancePlan:
    """Insurance plan attributes used to price a visit.

    deductible_remaining: amount the patient must still pay before coverage kicks in.
    copay: flat amount the patient pays per visit.
    coinsurance_rate: fraction of the post-deductible amount the patient pays (0.0-1.0).
    """

    plan_type: PlanType
    deductible_remaining: float
    copay: float
    coinsurance_rate: float


@dataclass(frozen=True)
class Visit:
    """A billable visit with its gross charge."""

    visit_id: str
    gross_charge: float

