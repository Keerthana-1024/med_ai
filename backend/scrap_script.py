import re
import os
import requests
import numpy as np
from bs4 import BeautifulSoup
from google import genai
from dotenv import load_dotenv

# CONFIG
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

GEMINI_MODEL = "gemini-2.0-flash"
EMBED_MODEL = "text-embedding-004"
SYMPTOM_BASE_URL = "https://medlineplus.gov/"
EMBED_FILE = "medical_symptoms_embeddings.npy"

client = genai.Client(api_key=API_KEY)

# UTILITIES

def fetch_page_text(symptom_slug: str) -> str:
    """Scrape MedlinePlus content for given symptom page."""
    url = SYMPTOM_BASE_URL + symptom_slug
    print(f"Fetching data from: {url}")
    resp = requests.get(url, timeout=10)
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to fetch {url} (status {resp.status_code})")
    soup = BeautifulSoup(resp.text, "html.parser")
    elems = soup.find_all(["p", "li"])
    return "\n".join(e.get_text(strip=True) for e in elems if e.get_text(strip=True))

def embed_text(text: str):
    """Get embedding for a string using Gemini embeddings."""
    result = client.models.embed_content(model=EMBED_MODEL, contents=text)
    emb = result.embedding if hasattr(result, "embedding") else result.embeddings[0]
    return np.array(emb.values if hasattr(emb, "values") else emb)

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# EMBEDDING FILE

def get_or_create_embeddings():
    predefined_symptoms = [
        "headache", "cough", "gas", "fever"
    ]

    if os.path.exists(EMBED_FILE):
        print(f"📁 Loading cached embeddings from {EMBED_FILE}")
        data = np.load(EMBED_FILE, allow_pickle=True).item()
    else:
        print("⚙️ Generating new embeddings and caching...")
        data = {s: embed_text(s) for s in predefined_symptoms}
        np.save(EMBED_FILE, data)
        print(f"✅ Saved embeddings to {EMBED_FILE}")
    return data

# SYMPTOM MATCHING

def map_to_predefined_symptoms(user_symptoms):
    predefined_embeddings = get_or_create_embeddings()

    matched = []
    for symptom in user_symptoms:
        symptom_emb = embed_text(symptom)
        sims = {s: cosine_similarity(symptom_emb, emb) for s, emb in predefined_embeddings.items()}
        best_match, score = max(sims.items(), key=lambda x: x[1])
        if score > 0.6:
            matched.append(best_match)
            print(f"  ✓ '{symptom}' → matched with '{best_match}' ({score:.2f})")
        else:
            print(f"  ✗ '{symptom}' → no good match ({score:.2f})")
    return list(set(matched))

# SUMMARIZATION / REASONING

def summarize_combined(symptom_texts, symptoms):
    joined_text = "\n\n".join(symptom_texts)
    prompt = f"""
You are a professional medical summarizer.

Combine and summarize the following medical content from MedlinePlus
for these symptoms: {', '.join(symptoms)}.

Provide a structured report including:
- Overview
- Likely combined causes or conditions
- Risk factors or triggers
- Diagnostic guidance (what doctors usually check)
- Prevention and general care advice
- When to seek urgent care

Source material:
{joined_text}
"""
    response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    return response.text.strip()

def generate_treatment_plan(symptom_texts, symptoms):
    joined_text = "\n\n".join(symptom_texts)
    prompt = f"""
You are acting as an experienced general physician.

Patient reports: {', '.join(symptoms)}.

Start your answer like:
"Ok, so if these are the issues then it could be due to..."

Then explain:
1. Possible underlying causes (reason medically)
2. If diagnostic tests are needed — list them in logical order
   (for example: blood test → imaging → specialist consult)
3. If no tests needed, describe likely first-line treatments and medications
4. Give simple advice or home remedies (if safe)
5. Mention when the patient should seek immediate care

Use both your medical knowledge and the following reference data:
{joined_text}
"""
    response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    return response.text.strip()

# MAIN

def process_symptoms(user_input):
    user_symptoms = [s.strip().lower() for s in user_input.split(",") if s.strip()]
    matched = map_to_predefined_symptoms(user_symptoms)
    if not matched:
        print("No valid symptoms recognized.")
        return

    symptom_texts = []
    for symptom in matched:
        try:
            slug = re.sub(r"\s+", "", symptom.lower()) + ".html"
            text = fetch_page_text(slug)
            symptom_texts.append(text)
        except Exception as e:
            print(f"⚠️ Could not fetch {symptom}: {e}")

    if not symptom_texts:
        print("No data fetched for any symptom.")
        return

    print("\n🧠 Generating combined summary...")
    combined_summary = summarize_combined(symptom_texts, matched)

    print("\n💊 Generating treatment plan...")
    treatment_plan = generate_treatment_plan(symptom_texts, matched)

    with open("symptom_summary.md", "w", encoding="utf-8") as f:
        f.write("# 🩺 Combined Symptom Summary\n\n" + combined_summary)
        f.write("\n\n---\n\n*AI-generated for educational purposes only.*")

    with open("treatment_plan.md", "w", encoding="utf-8") as f:
        f.write("# 💊 Treatment Plan & Medical Reasoning\n\n" + treatment_plan)
        f.write("\n\n---\n\n*Always consult a licensed healthcare provider before acting on this information.*")

    print("\n✅ Generated:")
    print(" - symptom_summary.md")
    print(" - treatment_plan.md")

if __name__ == "__main__":
    user_input = input("Enter your symptoms (comma-separated): ")
    process_symptoms(user_input)
