import os
from dotenv import load_dotenv
from groq import Groq
from eligible_ineligible import extract_text_from_pdf
import tiktoken  # To count tokens accurately

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# === Tokenizer for Groq (LLaMA-compatible)
encoding = tiktoken.get_encoding("cl100k_base")

def count_tokens(text):
    return len(encoding.encode(text))

def chunk_text(text, max_tokens=2000):
    tokens = encoding.encode(text)
    return [encoding.decode(tokens[i:i + max_tokens]) for i in range(0, len(tokens), max_tokens)]

# === Groq Call ===
def call_groq_model(prompt):
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192"
    )
    return response.choices[0].message.content.strip()

# === Risk Analyzer ===
def analyze_risk(company_data: str, rfp_text: str, rfp_filename: str = "") -> str:
    chunks = chunk_text(rfp_text, max_tokens=2000)
    results = []

    for i, chunk in enumerate(chunks):
        prompt = f"""
You are a contract analyst.

Analyze this part of an RFP and identify any risks, ambiguities, or unusual clauses in the contract, terms, scope, or evaluation criteria that could impact a bidder. Focus on legal, financial, or execution risks.

RFP Section (Part {i+1} of {len(chunks)}):
{chunk}
"""
        response = call_groq_model(prompt)
        results.append(f"--- Part {i+1} ---\n{response.strip()}")

    final_output = "\n\n".join(results)

    if rfp_filename:
        print(f"\n📂 Analyzing {rfp_filename}...\n{'='*60}")
        print("\n📌 Risk Analysis:\n", final_output)

    return final_output
