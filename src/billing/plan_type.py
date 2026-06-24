from enum import Enum


class PlanType(str, Enum):
    """Supported insurance plan categories for the portal."""

    HMO = "HMO"
    PPO = "PPO"
    HIGH_DEDUCTIBLE = "HIGH_DEDUCTIBLE"
    SELF_PAY = "SELF_PAY"

