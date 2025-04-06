import streamlit as st
import subprocess
import tempfile
import os

...

st.header("Step 1: Upload RFP and Company Data for Eligibility Analysis")
rfp_file = st.file_uploader("Upload RFP File (PDF)", type=["pdf"], key="rfp")
company_file = st.file_uploader("Upload Company Data File (PDF)", type=["pdf"], key="company")

eligibility_output_path = "eligibility_verdict.txt"

if st.button("Run Eligibility Check"):
    if rfp_file and company_file:
        # Save the uploaded files as temp files
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as rfp_temp, \
             tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as company_temp:
            rfp_temp.write(rfp_file.read())
            company_temp.write(company_file.read())
            rfp_temp_path = rfp_temp.name
            company_temp_path = company_temp.name

        st.success("Files saved. Running eligibility analysis...")

        try:
            subprocess.run(
                ["python", "eligible_ineligible.py", rfp_temp_path, company_temp_path],
                check=True
            )
            st.success("Eligibility analysis completed.")

            # Display the verdict
            if os.path.exists(eligibility_output_path):
                with open(eligibility_output_path, "r", encoding="utf-8") as file:
                    st.text_area("Eligibility Output", file.read(), height=200)
            else:
                st.error("Eligibility verdict file not found.")
        except subprocess.CalledProcessError as e:
            st.error(f"Error running eligible_ineligible.py: {e}")
    else:
        st.warning("Please upload both PDF files.")
