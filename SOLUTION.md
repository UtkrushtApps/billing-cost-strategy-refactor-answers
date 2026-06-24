# Solution Steps

1. Create a pricing-rule abstraction, such as a PricingRule base class, with a calculate(plan, visit) method so all plan-specific algorithms share the same interface.

2. Move shared deductible, coinsurance, rounding, and gross-charge capping helpers into the pricing-rule base class to remove duplicated arithmetic from the billing service and concrete rules.

3. Implement one concrete rule class per supported plan: HmoPricingRule, PpoPricingRule, HighDeductiblePricingRule, and SelfPayPricingRule.

4. Use a shared CopayDeductibleCoinsuranceRule base for HMO and PPO because both apply copay plus deductible plus coinsurance on the post-deductible amount.

5. Implement the high-deductible rule so visits below the remaining deductible charge the full gross amount; otherwise charge deductible plus coinsurance on the remaining amount, capped at gross.

6. Fix the self-pay rule by returning the full rounded visit gross charge directly, without subtracting copay or applying insurance math.

7. Replace the if/elif chain in BillingService with a registry mapping PlanType values to PricingRule instances.

8. In BillingService.calculate_patient_cost, look up the rule by plan.plan_type and delegate calculation to it; if the plan type is not registered, raise a clear ValueError instead of returning a fallback amount.

9. Extend the tests with a self-pay case where copay is nonzero to prove no copay is deducted.

10. Extend the tests with an unknown plan type and assert that BillingService raises ValueError.

11. Run pytest -q from /root/task and confirm the full suite passes.

