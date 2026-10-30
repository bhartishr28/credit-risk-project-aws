from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Literal

# --------------------------------------------------
# 1. Load the saved model and preprocessing objects
# --------------------------------------------------

MODEL_PATH = (
        Path(__file__).resolve().parent.parent
        / "model"
        / "credit_risk_model.joblib"
)

if not MODEL_PATH.exists():
    raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

model_data = joblib.load(MODEL_PATH)

model = model_data["model"]
features = list(model_data["features"])
scaler = model_data["scaler"]
cols_to_scale = list(model_data["cols_to_scale"])

# --------------------------------------------------
# 2. Create the FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="Credit Risk API",
    description="API for the credit risk modelling project",
    version="1.0.0",
)

# --------------------------------------------------
# 3. Define the applicant input fields
# --------------------------------------------------

class ApplicantInput(BaseModel):
    age: int = Field(ge=18, le=100)
    income: float = Field(gt=0)
    loan_amount: float = Field(ge=0)
    loan_tenure_months: int = Field(ge=1)
    credit_history: Literal["New-to-credit", "Existing borrower"]
    avg_dpd_per_delinquency: float = Field(ge=0)
    delinquency_ratio: float = Field(ge=0, le=100)
    credit_utilization_ratio: float = Field(ge=0, le=100)
    num_open_accounts: int = Field(ge=1)

    residence_type: Literal["Owned", "Rented", "Mortgage"]
    loan_purpose: Literal["Education", "Home", "Auto", "Personal"]
    loan_type: Literal["Unsecured", "Secured"]

# --------------------------------------------------
# 4. Prepare applicant data exactly as the model needs
# --------------------------------------------------

def prepare_input(applicant: ApplicantInput) -> pd.DataFrame:

    # Reproduce the feature engineering from the notebook.
    loan_to_income = round(
        applicant.loan_amount / applicant.income, 2
    )

    # Create the 13 final model features.
    input_data = {
        "age": applicant.age,
        "loan_tenure_months": applicant.loan_tenure_months,
        "number_of_open_accounts": applicant.num_open_accounts,
        "credit_utilization_ratio": applicant.credit_utilization_ratio,
        "loan_to_income": loan_to_income,
        "delinquency_ratio": applicant.delinquency_ratio,
        "avg_dpd_per_delinquency": applicant.avg_dpd_per_delinquency,

        "residence_type_Owned": int(
            applicant.residence_type == "Owned"
        ),
        "residence_type_Rented": int(
            applicant.residence_type == "Rented"
        ),

        "loan_purpose_Education": int(
            applicant.loan_purpose == "Education"
        ),
        "loan_purpose_Home": int(
            applicant.loan_purpose == "Home"
        ),
        "loan_purpose_Personal": int(
            applicant.loan_purpose == "Personal"
        ),

        "loan_type_Unsecured": int(
            applicant.loan_type == "Unsecured"
        ),

        # Placeholder values required because the saved scaler
        # was fitted on these additional numeric columns.
        # These columns are not used by the final 13-feature model.
        "number_of_dependants": 1,
        "years_at_current_address": 1,
        "zipcode": 1,
        "sanction_amount": 1,
        "processing_fee": 1,
        "gst": 1,
        "net_disbursement": 1,
        "principal_outstanding": 1,
        "bank_balance_at_application": 1,
        "number_of_closed_accounts": 1,
        "enquiry_count": 1,
    }

    df = pd.DataFrame([input_data])

    # Apply the original fitted scaler, without fitting it again.
    missing_columns = [
        col for col in cols_to_scale if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns required by scaler: {missing_columns}"
        )

    df[cols_to_scale] = scaler.transform(df[cols_to_scale])

    # Match the exact feature names and order used during training.
    df = df.reindex(columns=features, fill_value=0)

    return df


# --------------------------------------------------
# 5. Calculate the credit score and rating
# --------------------------------------------------

def calculate_credit_score(default_probability: float):

    credit_score = int(
        300 + (1 - default_probability) * 600
    )

    if credit_score < 500:
        rating = "Poor"
    elif credit_score < 650:
        rating = "Average"
    elif credit_score < 750:
        rating = "Good"
    else:
        rating = "Excellent"

    return credit_score, rating


# --------------------------------------------------
# 6. Basic API endpoints
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": " Credit Risk API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "model_type": type(model).__name__,
    }


@app.get("/model-info")
def model_info():
    return {
        "artifact_type": type(model_data).__name__,
        "model_type": type(model).__name__,
        "number_of_features": len(features),
        "feature_names": features,
        "columns_to_scale": cols_to_scale,
    }


# --------------------------------------------------
# 7. Prediction endpoint
# --------------------------------------------------

@app.post("/predict")
def predict(applicant: ApplicantInput):

    try:
        input_df = prepare_input(applicant)

        # Predict the class: 0 or 1.
        predicted_class = int(model.predict(input_df)[0])

        # Get the probability specifically for class 1 (default).
        class_labels = list(model.classes_)

        if 1 not in class_labels:
            raise ValueError(
                "The model does not contain class 1."
            )

        default_index = class_labels.index(1)

        default_probability = float(
            model.predict_proba(input_df)[0][default_index]
        )

        credit_score, rating = calculate_credit_score(
            default_probability
        )

        return {
            "predicted_class": predicted_class,
            "default_probability": round(default_probability, 4),
            "credit_score": credit_score,
            "rating": rating,
        }

    except (ValueError, KeyError) as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction could not be completed: {exc}",
        ) from exc
