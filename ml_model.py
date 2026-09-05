import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

FEATURES=["amount","type","reason","days_overdue","attempts","risk_score"]
TARGET="recovered"

def train_model(df, path):
    # Small synthetic/demo dataset: in production train on historical outcomes.
    X=df[FEATURES]; y=df[TARGET]
    pre=ColumnTransformer([
        ("cat",OneHotEncoder(handle_unknown="ignore"),["type","reason"]),
        ("num","passthrough",["amount","days_overdue","attempts","risk_score"])
    ])
    model=Pipeline([("pre",pre),("clf",RandomForestClassifier(n_estimators=150,max_depth=6,random_state=42,class_weight="balanced"))])
    model.fit(X,y)
    joblib.dump(model,path)

def predict_case(row,path):
    model=joblib.load(path)
    X=pd.DataFrame([{
        "amount":float(row["amount"]),"type":row["type"],"reason":row["reason"],
        "days_overdue":int(row["days_overdue"]),"attempts":int(row["attempts"]),
        "risk_score":float(row["risk_score"])
    }])
    p=float(model.predict_proba(X)[0][1]) if hasattr(model,"predict_proba") else float(model.predict(X)[0])
    p=round(p*100,1)
    return {"recovery_probability":p,"risk_band":"High" if p<40 else ("Medium" if p<70 else "High Recovery Potential")}
