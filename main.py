import streamlit as st
import os
from eligible_ineligible import extract_text_from_pdf, chunk_text, filter_relevant_chunks, extract_hard_eligibility_criteria, check_company_against_criteria
from riskanalysis import analyze_risk

# === Streamlit UI ===
st.set_page_config(page_title="RFP Evaluation Tool", layout="wide")
st.title("📊 RFP Evaluation Tool")

# === Upload Files ===
st.sidebar.header("Upload Files")
rfp_file = st.sidebar.file_uploader("📄 Upload RFP File (PDF)", type=["pdf"])
company_file = st.sidebar.file_uploader("🏢 Upload Company Profile (PDF)", type=["pdf"])

# Create temp directory
os.makedirs("temp", exist_ok=True)

# === Run Eligibility Check ===
if st.button("✅ Run Eligibility Check"):
    if rfp_file and company_file:
        rfp_path = os.path.join("temp", rfp_file.name)
        company_path = os.path.join("temp", company_file.name)

        # Save uploaded files
        with open(rfp_path, "wb") as f:
            f.write(rfp_file.read())
        with open(company_path, "wb") as f:
            f.write(company_file.read())

        # Process
        st.info("Extracting and analyzing files...")

        rfp_text = extract_text_from_pdf(rfp_path)
        company_text = extract_text_from_pdf(company_path)

        rfp_chunks = chunk_text(rfp_text)
        filtered_chunks = filter_relevant_chunks(rfp_chunks)
        criteria = extract_hard_eligibility_criteria(filtered_chunks)
        verdict = check_company_against_criteria(criteria, company_text)

        # Save to file
        eligibility_output_path = "eligibility_verdict.txt"
        with open(eligibility_output_path, "w", encoding="utf-8") as f:
            f.write(verdict)

        # Show and allow download
        st.subheader("✅ Eligibility Verdict")
        st.text_area("Eligibility Check Result", verdict, height=300)

        with open(eligibility_output_path, "rb") as file:
            st.download_button(
                label="📥 Download Eligibility Verdict",
                data=file,
                file_name="eligibility_verdict.txt",
                mime="text/plain"
            )
    else:
        st.warning("Please upload both RFP and Company Profile files.")

# === Run Risk Analysis ===
if st.button("🔍 Run Risk Analysis"):
    if rfp_file and company_file:
        rfp_path = os.path.join("temp", rfp_file.name)
        company_path = os.path.join("temp", company_file.name)

        # Make sure files are saved
        if not os.path.exists(rfp_path):
            with open(rfp_path, "wb") as f:
                f.write(rfp_file.read())
        if not os.path.exists(company_path):
            with open(company_path, "wb") as f:
                f.write(company_file.read())

        st.info("Running risk analysis...")

        rfp_text = extract_text_from_pdf(rfp_path)
        company_text = extract_text_from_pdf(company_path)

        risk_result = analyze_risk(company_text, rfp_text)

        # Save to file
        risk_output_path = "risk_analysis_output.txt"
        with open(risk_output_path, "w", encoding="utf-8") as f:
            f.write(risk_result)

        # Show and allow download
        st.subheader("📉 Risk Analysis Output")
        st.text_area("Risk Analysis Result", risk_result, height=300)

        with open(risk_output_path, "rb") as file:
            st.download_button(
                label="📥 Download Risk Analysis Result",
                data=file,
                file_name="risk_analysis_output.txt",
                mime="text/plain"
            )
    else:
        st.warning("Please upload both RFP and Company Profile files.")
