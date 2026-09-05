from flask import Flask, render_template, jsonify, request
from pathlib import Path
import pandas as pd
import numpy as np
from ml_model import train_model, predict_case
from ai_agent import diagnose_and_recommend

app = Flask(__name__)
DATA = Path("data/revenue_cases.csv")
MODEL = Path("models/recovery_model.joblib")

df = pd.read_csv(DATA)
if not MODEL.exists():
    train_model(df, MODEL)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/dashboard")
def dashboard():
    d = pd.read_csv(DATA)
    risk = d[d.status != "paid"]
    recovered = d[d.recovered == 1].amount.sum()
    total_risk = risk.amount.sum()
    by_reason = d.groupby("reason", dropna=False).amount.sum().sort_values(ascending=False).to_dict()
    by_type = d.groupby("type").amount.sum().to_dict()
    return jsonify({
        "revenue_at_risk": round(float(total_risk),2),
        "recovered": round(float(recovered),2),
        "recovery_rate": round(float(recovered/total_risk*100),1) if total_risk else 0,
        "cases": int(len(d)),
        "at_risk_cases": int(len(risk)),
        "reasons": {str(k): round(float(v),2) for k,v in by_reason.items()},
        "types": {str(k): round(float(v),2) for k,v in by_type.items()}
    })

@app.route("/api/cases")
def cases():
    d = pd.read_csv(DATA).fillna("")
    out=[]
    for _, r in d.iterrows():
        ml = predict_case(r, MODEL)
        ai = diagnose_and_recommend(r, ml["recovery_probability"])
        out.append({
            "id":r["id"], "customer":r["customer"], "type":r["type"],
            "amount":float(r["amount"]), "status":r["status"],
            "reason":r["reason"], "days_overdue":int(r["days_overdue"]),
            "attempts":int(r["attempts"]), "risk_score":float(r["risk_score"]),
            "probability":ml["recovery_probability"],
            "risk_band":ml["risk_band"], "diagnosis":ai["diagnosis"],
            "action":ai["action"], "guardrail":ai["guardrail"],
            "recovered":int(r["recovered"]), "last_action":r["last_action"]
        })
    return jsonify(out)

@app.route("/api/execute/<case_id>", methods=["POST"])
def execute(case_id):
    d = pd.read_csv(DATA)
    matches = d.index[d.id.astype(str)==str(case_id)]
    if len(matches)==0: return jsonify({"error":"Case not found"}),404
    i=matches[0]; r=d.loc[i]
    ml=predict_case(r, MODEL)
    ai=diagnose_and_recommend(r, ml["recovery_probability"])

    # Production systems must connect to approved payment/messaging APIs.
    # This prototype simulates the bounded workflow.
    if r["status"]=="paid":
        msg="STOP: payment already completed."
    elif int(r["attempts"])>=3:
        d.loc[i,"last_action"]="Human escalation"
        msg="STOP: retry limit reached. Escalated to human."
    elif ai["action_type"]=="escalate":
        d.loc[i,"last_action"]="Human escalation"
        msg="Escalated to human collections."
    else:
        d.loc[i,"last_action"]=ai["action"]
        d.loc[i,"attempts"]=int(r["attempts"])+1
        # Demo outcome: lower-risk cases recover; this is clearly a simulation.
        if ml["recovery_probability"] >= 55:
            d.loc[i,"status"]="paid"; d.loc[i,"recovered"]=1
            msg=f"SIMULATION: ₹{float(r['amount']):,.0f} recovered."
        else:
            msg="SIMULATION: intervention executed; payment not yet recovered."
    d.to_csv(DATA,index=False)
    return jsonify({"message":msg,"action":ai["action"],"probability":ml["recovery_probability"]})

@app.route("/api/analytics")
def analytics():
    d=pd.read_csv(DATA)
    failed=d[d.status!="paid"]
    return jsonify({
        "avg_risk":round(float(failed.risk_score.mean()),1) if len(failed) else 0,
        "top_reason":str(failed.groupby("reason").amount.sum().idxmax()) if len(failed) else "None",
        "overdue_30":int((failed.days_overdue>30).sum()),
        "high_risk":int((failed.risk_score>=70).sum()),
        "total_value":round(float(d.amount.sum()),2)
    })

if __name__=="__main__":
    app.run(debug=True)
