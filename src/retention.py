from __future__ import annotations

def _get(customer: dict, *keys, default=None):
    """Case-insensitive key lookup across multiple possible column names."""
    lower_map = {k.lower(): v for k, v in customer.items()}
    for key in keys:
        val = lower_map.get(key.lower())
        if val is not None:
            try:
                return float(val)
            except (ValueError, TypeError):
                return str(val)
    return default


def _fval(customer: dict, *keys, default: float = 0.0) -> float:
    v = _get(customer, *keys, default=default)
    try:
        return float(v)
    except (ValueError, TypeError):
        return default


def _sval(customer: dict, *keys, default: str = "") -> str:
    v = _get(customer, *keys, default=default)
    return str(v).lower().strip()


# ── Main function ─────────────────────────────────────────────────────────────
def retention_strategy(customer: dict, risk: str) -> list[str]:
    """
    Generate tailored retention recommendations.

    Parameters
    ----------
    customer : dict of feature_name → value (raw or encoded)
    risk     : 'High Risk' | 'Medium Risk' | 'Low Risk'

    Returns
    -------
    List of actionable recommendation strings (up to 8).
    """
    tips: list[str] = []

    tenure          = _fval(customer, "tenure", "Tenure", "months", "customer_age")
    monthly_charges = _fval(customer, "MonthlyCharges", "monthly_charges", "monthly_bill", "monthly_fee")
    total_charges   = _fval(customer, "TotalCharges", "total_charges", "total_spend")
    support_calls   = _fval(customer, "support_calls", "SupportCalls", "num_support", "complaints")
    payment_delay   = _fval(customer, "payment_delay_days", "PaymentDelay", "days_overdue")
    num_products    = _fval(customer, "num_products", "NumProducts", "products", "services_count")
    contract        = _sval(customer, "contract_type", "Contract", "contract", "plan_type")
    tech_support    = _sval(customer, "tech_support", "TechSupport", "technical_support")
    online_sec      = _sval(customer, "online_security", "OnlineSecurity", "security")
    internet        = _sval(customer, "internet_service", "InternetService", "internet_type")
    payment_method  = _sval(customer, "payment_method", "PaymentMethod", "pay_method")
    paperless       = _sval(customer, "paperless_billing", "PaperlessBilling")
    senior          = _fval(customer, "senior_citizen", "SeniorCitizen", "is_senior")
    partner         = _sval(customer, "partner", "Partner")
    dependents      = _sval(customer, "dependents", "Dependents")
    streaming_tv    = _sval(customer, "streamingtv", "StreamingTV", "streaming_tv")
    streaming_mov   = _sval(customer, "streamingmovies", "StreamingMovies", "streaming_movies")

    # ═══════════════════════════════════════════════════════════════════════════
    # HIGH RISK
    # ═══════════════════════════════════════════════════════════════════════════
    if risk == "High Risk":
        tips.append(
            "🚨 PRIORITY ACTION: Assign a dedicated customer success manager immediately. "
            "Schedule a retention call within 24–48 hours before the customer self-churns."
        )

        # Contract
        if "month" in contract or contract in ("0", "0.0"):
            tips.append(
                "📋 CONTRACT UPGRADE: Offer a 20–25% discount to switch from month-to-month "
                "to a 1 or 2-year contract. Lock in revenue and dramatically reduce cancellation risk."
            )

        # Tenure bands
        if 0 < tenure < 6:
            tips.append(
                "🎁 EARLY-LIFE RESCUE: Customer is in the critical first 6 months. "
                "Offer a complimentary onboarding session, a 15% discount for 3 months, "
                "and a dedicated setup support contact."
            )
        elif tenure < 12:
            tips.append(
                "📈 FIRST-YEAR RETENTION: Provide a loyalty milestone reward — free upgrade, "
                "bonus data, or a one-month credit — to reinforce the relationship at the 6–12 month mark."
            )
        elif tenure >= 24:
            tips.append(
                "🏆 LONG-TERM LOYALTY: This is a long-standing customer. Offer a VIP tier, "
                "exclusive perks, or an annual loyalty discount (10–15%) as a retention anchor."
            )

        # Pricing
        if monthly_charges > 70:
            tips.append(
                f"💰 PRICING ALERT: Monthly charges are high (${monthly_charges:.0f}). "
                "Present a custom bundle at a lower price point or introduce a mid-tier plan "
                "that matches actual usage. Price sensitivity is a top churn driver."
            )

        # Support
        if support_calls >= 3:
            tips.append(
                f"📞 SUPPORT ISSUE ({int(support_calls)} contacts): Conduct a service health review. "
                "Identify and fix the root cause of repeated contacts, then offer priority support "
                "access and a service credit to restore confidence."
            )

        # Payment delay
        if payment_delay > 7:
            tips.append(
                f"💳 PAYMENT FRICTION ({int(payment_delay)} days overdue): Offer auto-pay enrolment "
                "with a 5% monthly discount, or a flexible billing date aligned to payroll. "
                "Reduce friction before it becomes a churn trigger."
            )

        # Single product
        if num_products == 1:
            tips.append(
                "📦 SINGLE-PRODUCT RISK: Customers with one product churn 3× more. "
                "Offer a 60-day free trial of a complementary service "
                "(security, cloud backup, or streaming). Increase switching costs."
            )

        # Missing add-ons
        if "no" in tech_support or tech_support in ("0", "0.0"):
            tips.append(
                "🛠 TECH SUPPORT UPSELL: Offer a free 60-day trial of Tech Support. "
                "Customers who adopt it show 35% lower churn. Frame it as peace of mind, not an upsell."
            )

        if "no" in online_sec or online_sec in ("0", "0.0"):
            tips.append(
                "🔒 SECURITY UPSELL: Proactively offer Online Security as a value-add. "
                "Position around data protection — customers with security services churn 28% less."
            )

        # Senior citizens
        if senior == 1 or senior == 1.0:
            tips.append(
                "👴 SENIOR CUSTOMER: Assign a specialised support rep. Offer simplified "
                "billing, a dedicated helpline, and consider a senior loyalty discount (10%)."
            )

        # Payment method
        if "electronic check" in payment_method or "e-check" in payment_method:
            tips.append(
                "💳 PAYMENT METHOD: Electronic check users have the highest churn rate. "
                "Incentivise a switch to auto-pay credit card or bank transfer with a monthly discount."
            )

    # ═══════════════════════════════════════════════════════════════════════════
    # MEDIUM RISK
    # ═══════════════════════════════════════════════════════════════════════════
    elif risk == "Medium Risk":
        tips.append(
            "⚡ PROACTIVE OUTREACH: This customer is drifting. Send a personalised check-in "
            "email within 7 days and offer a loyalty reward before dissatisfaction escalates."
        )

        if "month" in contract or contract in ("0", "0.0"):
            tips.append(
                "📋 CONTRACT INCENTIVE: Offer a 15% discount to move to an annual plan. "
                "Reducing flexibility reduces cancellation probability by up to 60%."
            )

        if monthly_charges > 60:
            tips.append(
                "💰 VALUE REINFORCEMENT: Highlight the value delivered vs cost. "
                "Send a personalised usage report and offer a bundle upgrade at a neutral price point."
            )

        if num_products <= 2:
            tips.append(
                "📦 PRODUCT DEPTH: Invite the customer to a free trial of an additional service. "
                "Multi-product customers are significantly less likely to cancel."
            )

        if support_calls >= 2:
            tips.append(
                "📞 SUPPORT FOLLOW-UP: The customer has contacted support recently. "
                "Send a proactive satisfaction check and ensure all issues are fully resolved."
            )

        tips.append(
            "🎯 LOYALTY PROGRAMME: Enrol in a points or reward scheme if not already active. "
            "Gamified loyalty creates emotional switching costs that protect the relationship."
        )

        if "no" in streaming_tv and "no" in streaming_mov:
            tips.append(
                "📺 STREAMING BUNDLE: Offer a combined streaming TV + Movies package at a "
                "promotional rate. Entertainment bundles significantly increase product stickiness."
            )

    # ═══════════════════════════════════════════════════════════════════════════
    # LOW RISK
    # ═══════════════════════════════════════════════════════════════════════════
    else:
        tips.append(
            "✅ HEALTHY ACCOUNT: This customer is stable. Schedule a quarterly business "
            "review and introduce them to your referral programme — satisfied customers "
            "are your best acquisition channel."
        )

        if partner == "yes" or partner == "1":
            tips.append(
                "👥 PARTNER ACCOUNT: Offer a couple or family bundle. Household accounts "
                "churn at a fraction of the rate of single-user accounts."
            )

        if dependents == "yes" or dependents == "1":
            tips.append(
                "👨‍👩‍👧 FAMILY ACCOUNT: Offer family plan features or a multi-device discount. "
                "Accounts with dependents have strong retention baseline — reward their loyalty."
            )

        if tenure >= 24:
            tips.append(
                "🏅 AMBASSADOR POTENTIAL: Long-tenure customer with low risk is ideal for a "
                "referral or case study programme. Offer a referral bonus and VIP status."
            )

        tips.append(
            "📊 PERIODIC HEALTH CHECK: Continue monitoring usage patterns. "
            "Set an automated alert if monthly charges spike or support contacts increase."
        )

    return tips[:8]  # Cap for UI readability
