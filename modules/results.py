import streamlit as st
import requests
import pandas as pd

def show_results():
    st.title("Results & Visualization")
    if "sequence" not in st.session_state or "organism" not in st.session_state:
        st.warning("No sequence submitted. Please go to the Upload page and submit a sequence first.")
        st.stop()

    sequence = st.session_state["sequence"]
    organism = st.session_state["organism"]
    
    st.write(f"### Selected Organism: {organism}")
    st.write(f"### Submitted Sequence: \n`{sequence}`")
    FASTAPI_URL = "http://127.0.0.1:8000/predict"
    with st.spinner("Processing your sequence..."):
        try:
            response = requests.post(
                FASTAPI_URL,
                json={"sequence": sequence, "organism": organism}
            )
            response.raise_for_status()
            results = response.json()
        except Exception as e:
            st.error(f"Prediction failed: {str(e)}")
            st.stop()
    if not isinstance(results.get("predictions"), dict):
        st.error("Invalid response format from server")
        st.stop()
    try:
        df = pd.DataFrame(
            list(results["predictions"].items()),
            columns=["Model", "Prediction"]
        )
        st.session_state["results_df"] = df
        st.write("## Prediction Results")
        st.dataframe(df.style.applymap(
            lambda x: "background-color: green" if x == 1 else "background-color: red",
            subset=["Prediction"]
        ))
    except Exception as e:
        st.error(f"Failed to display results: {str(e)}")

if __name__ == "__main__":
    show_results()