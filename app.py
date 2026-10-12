import streamlit as st
import pandas as pd
from pathlib import Path

# ---------------------------- PAGE SETUP ------------------------------- #

st.set_page_config(
    page_title="Healthy Destinations",
    page_icon="🌍",
    layout="centered"
)

st.title("🌍 Healthy Destinations")
st.write("Explore destination recommendations by disease, country, destination and month.")

# ---------------------------- LOAD DATA ------------------------------- #

@st.cache_data
def load_data():
    file_path = Path(__file__).parent / "data.csv"

    # The original CSV uses semicolons and Latin-1 encoding.
    data = pd.read_csv(
        file_path,
        sep=";",
        encoding="latin_1",
        nrows=100000
    )

    # Convert European decimal strings such as "50,75" to numbers.
    for column in [
        "nota",
        "average_temperature_approx_C",
        "peso_temperatura",
        "peso_contaminacion",
        "peso_ambiente",
        "peso_humedad",
        "suma_pesos"
    ]:
        if column in data.columns and data[column].dtype == "object":
            data[column] = pd.to_numeric(
                data[column].astype(str).str.replace(",", ".", regex=False),
                errors="coerce"
            )

    return data


df = load_data()

# ---------------------------- SELECTIONS ------------------------------- #

st.subheader("Choose your criteria")

disease_list = sorted(df["enfermedad"].dropna().unique().tolist())
disease = st.selectbox("Disease", disease_list)

country_list = sorted(df["country"].dropna().unique().tolist())
country = st.selectbox("Country", country_list)

destination_list = sorted(
    df.loc[df["country"] == country, "destination"].dropna().unique().tolist()
)
destination = st.selectbox("Destination", destination_list)

month_list = (
    df[["month", "month_name"]]
    .drop_duplicates()
    .sort_values("month")["month_name"]
    .tolist()
)
month = st.selectbox("Month", month_list)

# ---------------------------- RESULTS ------------------------------- #

if st.button("Check advice", type="primary"):
    result = df[
        (df["enfermedad"] == disease)
        & (df["country"] == country)
        & (df["destination"] == destination)
        & (df["month_name"] == month)
    ]

    if result.empty:
        st.warning("No information is available for this selection.")
    else:
        result_row = result.iloc[0]

        st.subheader("Result")
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Score", f'{result_row["nota"]}' if pd.notna(result_row["nota"]) else "N/A")

        with col2:
            st.write("**Advice**")
            st.write(result_row["recomendación"])

        st.write("**Comments**")
        st.write(result_row["comentario"])

        # ---------------- TOP 3 MONTHS ---------------- #

        st.subheader("Best months to visit this destination")

        top3 = df[
            (df["enfermedad"] == disease)
            & (df["country"] == country)
            & (df["destination"] == destination)
        ].copy()

        top3 = top3.sort_values("nota", ascending=False).head(3)

        top3 = top3.rename(
            columns={
                "recomendación": "Recommendation",
                "month_name": "Month",
                "nota": "Score"
            }
        )

        st.dataframe(
            top3[["Recommendation", "Month", "Score"]],
            hide_index=True,
            use_container_width=True
        )

st.caption(
    "Note: Scores and recommendations are based on the supplied dataset and should not be treated as medical advice."
)
