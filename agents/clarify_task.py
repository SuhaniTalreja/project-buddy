# from agents.state import AgentState
# import google.generativeai as genai

# def clarify_task(state: AgentState) -> AgentState:
#     task = state["task"]
#     model = genai.GenerativeModel("models/gemini-2.0-flash")

#     prompt = (
#         "You are an assistant helping clarify software development tasks.\n"
#         "If the task below is ambiguous, respond with a clarifying question (max 1).\n"
#         "If it's already clear, just reply with 'CLEAR'.\n\n"
#         f"Task: {task}"
#     )

#     try:
#         response = model.generate_content(prompt)
#         reply = response.text.strip()
#     except Exception as e:
#         return state.update({
#             "clarification_needed": False,
#             "clarified_task": task,
#             "clarify_error": str(e)
#         })

#     # Check if clarification is needed
#     if "CLEAR" in reply.upper():
#         state.update({
#             "clarified_task": task,
#             "clarification_needed": False,
#             "clarification_response": reply
#         })
#     else:
#         state.update({
#             "clarification_needed": True,
#             "question": reply,
#             "clarification_response": reply
#         })

#     state["current_step"] = "Clarify Task"
#     return state
from agents.state import AgentState
import google.generativeai as genai

def clarify_task(state: AgentState) -> AgentState:
    task = state.get("task", "")
    if not task:
        return state.update({
            "clarification_needed": True,
            "question": "No task provided - please enter a development task",
            "status": "error"
        })

    model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
    
    prompt = f"""Analyze this software development task and respond with either:
1. 'CLEAR' if the task is ready for implementation
2. A single clarifying question if more details are needed

Task: {task}

Consider these aspects:
- Required technologies/frameworks
- Specific features/functionality
- Design requirements
- Authentication needs
- Data handling requirements"""

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.3,
                max_output_tokens=500
            )
        )
        reply = (response.text or "").strip()
        
        state["logs"].append(f"Clarification response: {reply}")

        if not reply or reply.upper().startswith("CLEAR"):
            return state.update({
                "clarified_task": task,
                "clarification_needed": False,
                "status": "clear"
            })
            
        return state.update({
            "clarified_task": reply,
            "clarification_needed": True,
            "question": reply,
            "status": "needs_clarification"
        })

    except Exception as e:
        return state.update({
            "clarified_task": task,
            "clarification_needed": False,
            "clarify_error": str(e),
            "status": "api_error"
        })