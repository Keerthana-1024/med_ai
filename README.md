# **MedAI: Multi-Agent Medical Diagnosis Chatbot**

**MedAI** is an AI-powered medical assistant that interacts with patients, asks relevant follow-up questions, scrapes trusted medical websites for information, and provides informed diagnosis and treatment recommendations. The system leverages a multi-agent architecture using CrewAI for coordinated reasoning and decision-making.

---

## **Features**

* Accepts multiple symptoms as comma-separated input (e.g., `headache, fever, cough`).
* Scraper agent collects symptom-specific information from reliable medical sources.
* Follow-up agent dynamically asks patients for additional details (age, weight, history, medications).
* Doctor agent supervises the conversation, integrates information, and generates diagnosis.
* Drug agent recommends medicines with proper brand names and dosage guidelines based on patient details.
* Logs all conversations in `log.json` with timestamps, user queries, AI responses, and metadata.
* LLM-based reasoning ensures conversational, second-person responses instead of generic advice.

---

## **Architecture**

1. **User Input:** Patient submits symptoms.
2. **Scraper Agent:** Scrapes web for relevant information per symptom using the scraping tool.
3. **Follow-up Agent:** Determines missing information and asks relevant questions.
4. **Doctor Agent:** Supervises, aggregates data, reasons over symptoms & patient responses, and provides diagnosis.
5. **Drug Agent:** Suggests medications considering interactions, age, weight, and patient history.

---

## **Tech Stack**

* **Backend:** Python, Flask
* **Frontend:** Static HTML/JS
* **LLM:** Google Gemini (`gemini-2.0-flash`)
* **Agent Framework:** CrewAI
* **Other Tools:** NumPy, BeautifulSoup, Requests, dotenv

---

## **Installation**

1. Clone the repository:

```bash
git clone git@github.com:Keerthana-1024/MedAi.git
cd MedAI
```

2. Create a `.env` file with your Gemini API key:

```
GOOGLE_API_KEY=<your_api_key>
```

3. Install Python dependencies:

```bash
pip install -r requirements.txt
```

---

## **Running the Application**

* **Backend:**

```bash
python backend/app.py
```

* **Frontend:**

  * Static HTML: open `index.html`

* All conversations and metadata are logged in `log.json`.

---

## **Usage**

1. Enter patient symptoms as comma-separated values (e.g., `headache, fever`).
2. Follow-up agent may ask additional questions (age, weight, history, medications).
3. Doctor agent provides reasoning, likely diagnosis, and treatment plan.
4. Drug agent suggests appropriate medications with recommended dosages based on patient details.

---
