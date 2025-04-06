import os
import sys
import fitz  # PyMuPDF
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ... (same utility functions as before)
# === Utility: Extract text from PDF ===
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()

# === Utility: Chunk large text ===
def chunk_text(text, max_chars=3000):
    return [text[i:i + max_chars] for i in range(0, len(text), max_chars)]

# === Utility: Filter eligibility-relevant chunks ===
def filter_relevant_chunks(chunks):
    keywords = ["eligibility", "qualification", "criteria", "requirement", "mandatory", "experience", "license", "turnover"]
    return [chunk for chunk in chunks if any(k in chunk.lower() for k in keywords)] or chunks[:5]  # fallback

# === Groq: Extract strict eligibility criteria ===
def extract_hard_eligibility_criteria(text_chunks, batch_size=3):
    all_criteria = []

    for i in range(0, len(text_chunks), batch_size):
        batch = "\n".join(text_chunks[i:i + batch_size])
        prompt = f"""
You're a compliance expert. Extract all strict eligibility and mandatory exclusion criteria from this RFP text. Focus only on hard constraints. Format each as a bullet point.

Text:
{batch}
"""
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192"
        )
        batch_criteria = response.choices[0].message.content.strip().split("\n")
        all_criteria.extend(batch_criteria)

    deduped = list(set([line.strip() for line in all_criteria if line.strip()]))
    return "\n".join(sorted(deduped))

# === Groq: Evaluate company against criteria ===
def check_company_against_criteria(criteria_text, company_text):
    prompt = f"""
Act as an auditor. Check whether the company profile meets the most of the following eligibility criteria.

Eligibility Criteria:
{criteria_text}

Company Profile:
{company_text}


If the failed criteria is greater than Criteria Met, respond: 
❌ Ineligible

If most of criteria are clearly met and Criteria Met are greater than failed criteria, respond:
✅ Eligible  

If uncertain, respond:
✅ Eligible 
 
Analyze the match and return a formatted output like:
Criteria Met:
- ...

Failed Criteria:
- ...

Suggestion to improve:
- ...
"""
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192"
    )
    return response.choices[0].message.content.strip()


def main():
    if len(sys.argv) != 3:
        print("Usage: python eligible_ineligible.py <rfp_pdf_path> <company_pdf_path>")
        return

    rfp_file = sys.argv[1]
    company_file = sys.argv[2]

    print("\n📄 Extracting and chunking RFP...")
    rfp_text = extract_text_from_pdf(rfp_file)
    rfp_chunks = chunk_text(rfp_text)
    filtered_rfp_chunks = filter_relevant_chunks(rfp_chunks)

    print("\n🔍 Extracting hard eligibility criteria...")
    criteria_text = extract_hard_eligibility_criteria(filtered_rfp_chunks)

    print("\n📄 Extracting Company Profile...")
    company_text = extract_text_from_pdf(company_file)

    print("\n📋 Checking company against hard criteria...")
    verdict = check_company_against_criteria(criteria_text, company_text)

    print("\n🔍 Initial Verdict based on strict checks:")
    print(verdict)

    with open("eligibility_verdict.txt", "w", encoding="utf-8") as f:
        f.write(verdict)

if __name__ == "__main__":
    main()
