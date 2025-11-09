from flask import Flask, request, jsonify
from flask_cors import CORS
from crewai import Crew
from agents import scraper_agent, followup_agent, drug_agent, doctor_agent
from tasks import create_scraper_task, create_followup_task, create_drug_task, create_doctor_task
import time
import json
import datetime
from typing import Dict, Any

app = Flask(__name__)
CORS(app)

LOGFILE = "log.json"
conversation_state = {}  # Conversation state per session

def now_ts():
    return datetime.datetime.now().isoformat()

def log_interaction(session_id: str, user_text: str, bot_text: str, meta: Dict[Any, Any] = None):
    """Log user-bot interactions"""
    entry = {
        "timestamp": now_ts(),
        "session_id": session_id,
        "user": user_text,
        "bot": bot_text,
        "meta": meta or {}
    }
    with open(LOGFILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": now_ts()})

@app.route("/chat", methods=["POST"])
def chat():
    """
    Main chat endpoint
    Expects JSON:
    {
      "message": "headache, fever",
      "session_id": "unique-session-id",
      "patient_info": {
        "age": 30,
        "weight": 70,
        "medications": [],
        ...
      }
    }
    """
    try:
        data = request.json
        user_text = data.get("message", "").strip()
        session_id = data.get("session_id", "default")
        patient_info = data.get("patient_info", {})
        
        if not user_text:
            return jsonify({"error": "Empty message"}), 400

        start_time = time.time()
        
        # Initialize or get conversation state
        if session_id not in conversation_state:
            conversation_state[session_id] = {
                "symptoms": [],
                "patient_info": patient_info,
                "stage": "initial"
            }
        
        state = conversation_state[session_id]
        
        # Parse symptoms (if comma-separated on first message)
        if state["stage"] == "initial":
            symptoms = [s.strip() for s in user_text.split(",") if s.strip()]
            state["symptoms"] = symptoms
            state["stage"] = "diagnosis"
        else:
            # User is providing follow-up information
            state["patient_info"]["additional_info"] = user_text
        
        # Update patient info from request
        state["patient_info"].update(patient_info)
        
        # Create context for agents
        context = {
            "symptoms": state["symptoms"],
            "patient_info": state["patient_info"]
        }
        
        # Create tasks
        scraper_task = create_scraper_task(state["symptoms"])
        followup_task = create_followup_task(context)
        drug_task = create_drug_task(context)
        doctor_task = create_doctor_task(context)
        
        # Create crew
        medical_crew = Crew(
            agents=[scraper_agent, followup_agent, drug_agent, doctor_agent],
            tasks=[scraper_task, followup_task, drug_task, doctor_task],
            verbose=True
        )
        
        # Execute crew
        result = medical_crew.kickoff()
        
        # Extract final output
        final_reply = str(result)
        
        latency = round(time.time() - start_time, 2)
        
        # Log interaction
        log_interaction(
            session_id=session_id,
            user_text=user_text,
            bot_text=final_reply,
            meta={
                "latency": latency,
                "symptoms": state["symptoms"],
                "stage": state["stage"]
            }
        )
        
        response = {
            "reply": final_reply,
            "latency": latency,
            "session_id": session_id,
            "stage": state["stage"]
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/reset", methods=["POST"])
def reset():
    """Reset conversation for a session"""
    data = request.json
    session_id = data.get("session_id", "default")
    
    if session_id in conversation_state:
        del conversation_state[session_id]
    
    return jsonify({"message": "Session reset", "session_id": session_id})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)