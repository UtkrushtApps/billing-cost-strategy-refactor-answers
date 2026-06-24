import pytest

from src.billing.billing_service import BillingService
from src.billing.models import InsurancePlan, Visit
from src.billing.plan_type import PlanType


def _service():
    return BillingService()


def test_hmo_applies_copay_deductible_and_coinsurance():
    plan = InsurancePlan(
        plan_type=PlanType.HMO,
        deductible_remaining=100.0,
        copay=20.0,
        coinsurance_rate=0.2,
    )
    visit = Visit(visit_id="v1", gross_charge=500.0)
    # after_deductible = 400 -> share = 80 -> 20 + 100 + 80 = 200
    assert _service().calculate_patient_cost(plan, visit) == 200.0


def test_ppo_applies_copay_deductible_and_coinsurance():
    plan = InsurancePlan(
        plan_type=PlanType.PPO,
        deductible_remaining=50.0,
        copay=30.0,
        coinsurance_rate=0.1,
    )
    visit = Visit(visit_id="v2", gross_charge=450.0)
    # after_deductible = 400 -> share = 40 -> 30 + 50 + 40 = 120
    assert _service().calculate_patient_cost(plan, visit) == 120.0


def test_high_deductible_below_deductible_charges_full_amount():
    plan = InsurancePlan(
        plan_type=PlanType.HIGH_DEDUCTIBLE,
        deductible_remaining=1000.0,
        copay=0.0,
        coinsurance_rate=0.2,
    )
    visit = Visit(visit_id="v3", gross_charge=300.0)
    assert _service().calculate_patient_cost(plan, visit) == 300.0


def test_high_deductible_above_deductible_applies_coinsurance():
    plan = InsurancePlan(
        plan_type=PlanType.HIGH_DEDUCTIBLE,
        deductible_remaining=200.0,
        copay=0.0,
        coinsurance_rate=0.25,
    )
    visit = Visit(visit_id="v4", gross_charge=600.0)
    # after_deductible = 400 -> share = 100 -> 200 + 100 = 300
    assert _service().calculate_patient_cost(plan, visit) == 300.0


def test_self_pay_charges_full_amount_without_deducting_copay():
    plan = InsurancePlan(
        plan_type=PlanType.SELF_PAY,
        deductible_remaining=0.0,
        copay=75.0,
        coinsurance_rate=0.0,
    )
    visit = Visit(visit_id="v-self", gross_charge=500.0)

    assert _service().calculate_patient_cost(plan, visit) == 500.0


def test_cost_never_exceeds_gross_charge():
    plan = InsurancePlan(
        plan_type=PlanType.PPO,
        deductible_remaining=1000.0,
        copay=500.0,
        coinsurance_rate=0.5,
    )
    visit = Visit(visit_id="v5", gross_charge=400.0)
    assert _service().calculate_patient_cost(plan, visit) == 400.0


def test_unknown_plan_type_raises_clear_error():
    plan = InsurancePlan(
        plan_type="UNKNOWN_PLAN",  # type: ignore[arg-type]
        deductible_remaining=0.0,
        copay=0.0,
        coinsurance_rate=0.0,
    )
    visit = Visit(visit_id="v-unknown", gross_charge=250.0)

    with pytest.raises(ValueError, match="No pricing rule registered"):
        _service().calculate_patient_cost(plan, visit)

