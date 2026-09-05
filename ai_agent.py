def diagnose_and_recommend(row, probability):
    reason=str(row["reason"]).lower()
    attempts=int(row["attempts"])
    overdue=int(row["days_overdue"])
    status=str(row["status"]).lower()

    if status=="paid":
        return {"diagnosis":"Payment already completed.","action":"Stop all recovery actions.","action_type":"stop","guardrail":"Stop after successful payment."}
    if attempts>=3:
        return {"diagnosis":"Repeated recovery attempts detected.","action":"Escalate to a human collections agent.","action_type":"escalate","guardrail":"Maximum 3 automated attempts."}
    if "expired" in reason:
        return {"diagnosis":"Payment method is likely expired.","action":"Send secure payment-method update link.","action_type":"message","guardrail":"One update request before escalation."}
    if "insufficient" in reason:
        return {"diagnosis":"Insufficient funds is the likely failure cause.","action":"Send payment link and schedule one controlled retry.","action_type":"retry","guardrail":"Do not exceed 3 attempts."}
    if "checkout" in reason or str(row["type"]).lower()=="checkout":
        return {"diagnosis":"Customer showed purchase intent but abandoned checkout.","action":"Send personalized checkout recovery link.","action_type":"message","guardrail":"Limited follow-up; stop after conversion."}
    if overdue>30:
        return {"diagnosis":"Invoice is materially overdue.","action":"Send formal overdue notice and escalate if unpaid.","action_type":"escalate","guardrail":"Human review for prolonged overdue receivables."}
    return {"diagnosis":"Revenue risk requires a controlled follow-up.","action":"Schedule a bounded recovery reminder/retry.","action_type":"retry","guardrail":"Maximum 3 automated attempts."}
