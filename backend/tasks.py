from crewai import Task
from agents import scraper_agent, followup_agent, drug_agent, doctor_agent

def create_scraper_task(symptoms: list) -> Task:
    """Create task for scraping symptom information"""
    return Task(
        description=f"""Research the following symptoms: {', '.join(symptoms)}.
        Use the symptom scraper tool to fetch information from MedlinePlus.
        Summarize only the most relevant information for these specific symptoms.
        Focus on: common causes, when to see a doctor, and typical characteristics.""",
        agent=scraper_agent,
        expected_output="Concise summary of medical information for the given symptoms"
    )

def create_followup_task(context: dict) -> Task:
    """Create task for identifying missing patient information"""
    return Task(
        description=f"""Based on these symptoms: {context.get('symptoms', [])} and 
        the scraped medical information, identify what patient information is missing.
        
        Check if we have:
        - Patient age and weight
        - Duration and severity of symptoms
        - Previous medical conditions or illnesses
        - Current medications
        - Allergies
        
        Generate 2-3 specific questions to ask the patient. Keep questions clear and concise.
        If sufficient information is already available, state "No additional information needed".""",
        agent=followup_agent,
        expected_output="List of 2-3 specific follow-up questions or confirmation that no questions are needed"
    )

def create_drug_task(context: dict) -> Task:
    """Create task for medication recommendations"""
    return Task(
        description=f"""Based on:
        - Symptoms: {context.get('symptoms', [])}
        - Patient info: {context.get('patient_info', 'Not provided yet')}
        - Medical research: Use context from scraper agent
        
        Recommend appropriate over-the-counter or common prescription medications.
        Use brand names (e.g., "Tylenol" not "acetaminophen").
        Consider age, weight, and any mentioned current medications to avoid interactions.
        Provide dosage based on patient specifics.
        
        If patient information is insufficient, state what's needed before prescribing.""",
        agent=drug_agent,
        expected_output="Medication recommendations with brand names and dosages, or request for more information"
    )

def create_doctor_task(context: dict) -> Task:
    """Create task for final diagnosis and recommendations"""
    return Task(
        description=f"""Synthesize all information from the research, follow-up, and medication specialists.
        
        Context:
        - Symptoms: {context.get('symptoms', [])}
        - Patient info: {context.get('patient_info', 'Pending')}
        
        Provide a clear response that:
        1. Addresses the likely condition
        2. Includes medication recommendations if appropriate
        3. Advises whether to see a doctor in person
        4. Is written in second person (you, your)
        5. Is concise (aim for under 50 words unless more detail is critical)
        
        If follow-up questions were generated, present them to the user in a friendly way.""",
        agent=doctor_agent,
        expected_output="Clear, concise diagnosis and recommendations in second person, under 50 words"
    )