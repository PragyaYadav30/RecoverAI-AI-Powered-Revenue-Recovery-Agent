# RecoverAI — Full AI + Data Analytics Project

## Purpose
RecoverAI detects revenue leakage, analyzes causes, predicts recovery probability using machine learning, uses an AI decision layer to diagnose the case and recommend an intervention, applies guardrails, executes a bounded demo workflow, and measures recovered revenue.

## Run
1. Install Python 3.10+.
2. Open terminal in this folder.
3. `pip install -r requirements.txt`
4. `python app.py`
5. Open `http://127.0.0.1:5000`

## Project architecture
- `app.py` — Flask APIs and workflow orchestration
- `ml_model.py` — Random Forest recovery-probability model
- `ai_agent.py` — AI decision/diagnosis layer
- `data/revenue_cases.csv` — demo transaction/receivable data
- `templates/index.html` — dashboard
- `static/` — UI
- `models/` — generated ML model

## Data Analytics
Calculates revenue at risk, revenue recovered, recovery rate, average risk, overdue cases, top loss cause and transaction-type value.

## AI/ML
The Random Forest estimates recovery probability from amount, transaction type, failure reason, overdue days, attempts and risk score. The AI agent maps the case context to a recovery intervention and guardrail.

## Important
The action execution is simulated for demonstration. It does not charge cards or send real messages. For production, connect approved payment, CRM and messaging APIs, implement authentication, consent, compliance, rate limits, immutable audit logs and human approval where required.
