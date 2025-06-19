from agents.state import AgentState
from agents.utils import extract_text
import google.generativeai as genai

def analyze_task(state: AgentState) -> AgentState:
    task = state.get("task")
    print(f"\n📌 Task: {task}")
    if not task:
        analysis = "[ERROR] No task provided."
    else:
        print("🔍 Analyzing task...")
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        response = model.generate_content(f"What steps are required to complete this task?\n\nTask: {task}")
        analysis = extract_text(response)
        print("\n✅ Task Analysis Complete:\n", analysis)

    state.update({"analysis": analysis})
    return state
