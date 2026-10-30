
import requests
import streamlit as st

# --------------------------------------------------
# Configuration
# --------------------------------------------------

import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

API_URL = f"{API_BASE_URL}/predict"
HEALTH_URL = f"{API_BASE_URL}/health"

st.set_page_config(
    page_title="ABC Finance | Credit Risk",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------
# Custom styling
# --------------------------------------------------

st.markdown("""
<style>
    .stApp {
        background-color: #F4F7FB;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #10243A 0%, #173B50 100%);
    }

    [data-testid="stSidebar"] * {
        color: #F5F8FC;
    }

    .brand {
        font-size: 27px;
        font-weight: 800;
        letter-spacing: 1px;
        color: #FFFFFF;
        margin-bottom: 3px;
    }

    .brand-subtitle {
        font-size: 13px;
        color: #B9CEDD;
        margin-bottom: 25px;
    }

    .hero {
        background: linear-gradient(115deg, #10243A, #176B70);
        padding: 30px;
        border-radius: 18px;
        color: white;
        margin-bottom: 24px;
    }

    .hero h1 {
        color: white;
        font-size: 32px;
        margin: 0 0 10px 0;
    }

    .hero p {
        color: #DCEBF1;
        font-size: 15px;
        margin: 0;
    }

    .section-title {
        font-size: 20px;
        font-weight: 700;
        color: #17334A;
        margin: 12px 0 4px 0;
    }

    .section-caption {
        color: #64748B;
        font-size: 13px;
        margin-bottom: 18px;
    }

    div[data-testid="stForm"] {
        background: white;
        padding: 24px;
        border: 1px solid #E1E8F0;
        border-radius: 16px;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #E1E8F0;
        padding: 20px;
        border-radius: 14px;
        box-shadow: 0 3px 12px rgba(16, 36, 58, 0.04);
    }

    div[data-testid="stMetricLabel"] {
        color: #64748B;
    }

    div.stButton > button,
    div[data-testid="stFormSubmitButton"] > button {
        background: #087F8C;
        color: white;
        border: none;
        border-radius: 9px;
        padding: 10px 22px;
        font-weight: 700;
        min-height: 44px;
    }

    div.stButton > button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover {
        background: #066873;
        color: white;
        border: none;
    }

    .result-card {
        background: white;
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #E1E8F0;
        margin-top: 8px;
    }

    .rating {
        font-size: 25px;
        font-weight: 800;
        margin: 5px 0;
    }

    .small-note {
        color: #64748B;
        font-size: 12px;
        line-height: 1.6;
    }
    /* Make all input labels clearly visible */
div[data-testid="stWidgetLabel"] p {
    color: #17334A !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    opacity: 1 !important;
}

/* Make dropdown labels and number input labels visible */
div[data-testid="stSelectbox"] label,
div[data-testid="stNumberInput"] label {
    color: #17334A !important;
}

/* Keep input text readable */
input, [data-baseweb="select"] {
    color: #17334A !important;
}
    #MainMenu, footer {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

with st.sidebar:
    st.markdown(
        '<div class="brand">ABC FINANCE</div>'
        '<div class="brand-subtitle">CREDIT INTELLIGENCE PLATFORM</div>',
        unsafe_allow_html=True,
    )

    st.divider()

    st.markdown("### 🏦 Risk Assessment")
    st.caption("Evaluate applicant information using the trained credit risk model.")

    st.markdown("### 📊 Model Outputs")
    st.markdown(
        "- Default probability\n"
        "- Credit score\n"
        "- Risk rating"
    )

    st.divider()

    try:
        health_response = requests.get(HEALTH_URL, timeout=3)

        if health_response.ok:
            st.success("Prediction API connected")
        else:
            st.warning("Prediction API needs attention")

    except requests.exceptions.RequestException:
        st.error("Prediction API offline")

    st.markdown("---")
    st.caption("ABC Finance · Credit Risk Analytics")


# --------------------------------------------------
# Header
# --------------------------------------------------

st.markdown("""
<div class="hero">
    <h1>Credit Risk Dashboard</h1>
    <p>
        Assess applicant default risk with a machine learning model.
        Enter the applicant details below to generate an assessment.
    </p>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# Applicant input form
# --------------------------------------------------

st.markdown(
    '<div class="section-title">👤 Applicant Profile</div>'
    '<div class="section-caption">'
    'Enter personal, financial and credit behaviour information.'
    '</div>',
    unsafe_allow_html=True,
)

with st.form("credit_risk_form"):

    st.markdown("**Personal & Financial Information**")

    col1, col2, col3 = st.columns(3)

    with col1:
        age = st.number_input(
            "Age (years)",
            min_value=18,
            max_value=100,
            value=28,
            help="Applicant age in years.",
        )

    with col2:
        income = st.number_input(
            "Annual Income (₹)",
            min_value=1,
            value=1200000,
            step=50000,
            help="Annual income in rupees. Must be greater than zero.",
        )

    with col3:
        loan_amount = st.number_input(
            "Loan Amount (₹)",
            min_value=0,
            value=2560000,
            step=50000,
        )

    st.markdown("---")
    st.markdown("**Loan & Credit Behaviour**")
    credit_history = st.selectbox(
        "Credit History",
        ["Existing borrower", "New-to-credit"],
        help="Choose whether the applicant has previous borrowing history."
    )
    col4, col5, col6 = st.columns(3)

    with col4:
        loan_tenure_months = st.number_input(
            "Loan Tenure (months)",
            min_value=1,
            value=36,
            step=1,
        )

    with col5:
        avg_dpd_per_delinquency = st.number_input(
            "Average Days Past Due",
            min_value=0.0,
            value=20.0,
            step=1.0,
            help="Average days overdue per delinquency.",
        )

    with col6:
        num_open_accounts = st.number_input(
            "Open Loan Accounts",
            min_value=1,
            max_value=100,
            value=2,
            step=1,
        )

    col7, col8 = st.columns(2)

    with col7:
        delinquency_ratio = st.number_input(
            "Delinquency Ratio (%)",
            min_value=0.0,
            max_value=100.0,
            value=30.0,
            step=1.0,
        )

    with col8:
        credit_utilization_ratio = st.number_input(
            "Credit Utilization Ratio (%)",
            min_value=0.0,
            max_value=100.0,
            value=30.0,
            step=1.0,
        )

    st.markdown("---")
    st.markdown("**Applicant Classification**")

    col9, col10, col11 = st.columns(3)

    with col9:
        residence_type = st.selectbox(
            "Residence Type",
            ["Owned", "Rented", "Mortgage"],
        )

    with col10:
        loan_purpose = st.selectbox(
            "Loan Purpose",
            ["Education", "Home", "Auto", "Personal"],
        )

    with col11:
        loan_type = st.selectbox(
            "Loan Type",
            ["Unsecured", "Secured"],
        )

    loan_to_income = loan_amount / income

    st.info(
        f"Loan-to-Income Ratio: **{loan_to_income:.2f}**"
    )

    submitted = st.form_submit_button(
        "Calculate Credit Risk  →",
        use_container_width=True,
    )


# --------------------------------------------------
# Call FastAPI and retain the result
# --------------------------------------------------

if submitted:

    payload = {
        "age": age,
        "income": income,
        "loan_amount": loan_amount,
        "loan_tenure_months": loan_tenure_months,
        "credit_history": credit_history,
        "avg_dpd_per_delinquency": avg_dpd_per_delinquency,
        "delinquency_ratio": delinquency_ratio,
        "credit_utilization_ratio": credit_utilization_ratio,
        "num_open_accounts": num_open_accounts,
        "residence_type": residence_type,
        "loan_purpose": loan_purpose,
        "loan_type": loan_type,
    }

    try:
        with st.spinner("Analysing applicant profile..."):
            response = requests.post(
                API_URL,
                json=payload,
                timeout=15,
            )

        if response.ok:
            st.session_state["credit_risk_result"] = response.json()
            st.session_state["credit_risk_error"] = None
        else:
            st.session_state["credit_risk_result"] = None
            st.session_state["credit_risk_error"] = (
                f"API returned {response.status_code}: {response.text}"
            )

    except requests.exceptions.RequestException as exc:
        st.session_state["credit_risk_result"] = None
        st.session_state["credit_risk_error"] = str(exc)


# --------------------------------------------------
# Display results
# --------------------------------------------------

error = st.session_state.get("credit_risk_error")
result = st.session_state.get("credit_risk_result")

if error:
    st.error(f"Could not calculate risk. {error}")


if result:
    st.markdown("---")

    if credit_history == "New-to-credit":
        st.markdown(
            '<div class="section-title">'
            '📈 Credit Risk Assessment</div>'
            '<div class="section-caption">'
            'Applicant has no previous borrowing history.'
            '</div>',
            unsafe_allow_html=True,
        )

        st.warning(
            "New-to-credit applicant: this model has not been "
            "specifically validated for applicants without previous "
            "borrowing history."
        )

        st.info(
            "The model prediction, probability, and score are hidden "
            "for this applicant type because their reliability has "
            "not been established. This does not mean the applicant "
            "is high risk or should be declined."
        )

    else:
        st.markdown(
            '<div class="section-title">📈 Credit Risk Assessment</div>'
            '<div class="section-caption">'
            'Model-generated results for the submitted applicant.'
            '</div>',
            unsafe_allow_html=True,
        )

        probability = result["default_probability"]
        score = result["credit_score"]
        rating = result["rating"]
        predicted_class = result["predicted_class"]

        metric1, metric2, metric3 = st.columns(3)

        with metric1:
            st.metric(
                "Default Probability",
                f"{probability:.2%}",
                help="Estimated probability of the default class.",
            )

        with metric2:
            st.metric(
                "Credit Score",
                f"{score} / 900",
                help="Project-specific score derived from model probability.",
            )

        with metric3:
            st.metric("Risk Rating", rating)

        st.markdown(
            '<div class="result-card">',
            unsafe_allow_html=True,
        )

        if probability >= 0.5:
            rating_color = "#B42318"
            st.warning(
                "The model predicts the default class for this applicant."
            )
        else:
            rating_color = "#087F5B"
            st.success(
                "The model predicts the non-default class for this applicant."
            )

        st.markdown(
            f'<div style="color:#64748B;font-size:13px;">'
            f'DEFAULT PROBABILITY INDICATOR</div>'
            f'<div class="rating" style="color:{rating_color};">'
            f'{probability:.1%}</div>',
            unsafe_allow_html=True,
        )

        st.progress(min(max(float(probability), 0.0), 1.0))

        st.markdown(
            f'<p class="small-note">'
            f'Predicted class: <b>{predicted_class}</b> · '
            f'Rating category: <b>{rating}</b></p>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True,
        )

        st.caption(
            "Important: This is an educational, model-based estimate. "
            "The score and rating are specific to this project and are "
            "not an official credit bureau score or a guarantee of repayment."
        )
