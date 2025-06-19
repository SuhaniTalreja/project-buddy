import json
from agents.state import AgentState
from agents.utils import extract_text
import google.generativeai as genai

def decompose_task(state: AgentState) -> AgentState:
    task = state.get("task")
    print(f"\n🧩 Decomposing task: {task}")

    if not task:
        state["subtasks"] = [{
            "id": 1,
            "title": "No task",
            "description": "No task provided",
            "complexity": "high",
            "depends_on": []
        }]
        return state

    model = genai.GenerativeModel("models/gemini-1.5-flash")
    response = model.generate_content(f"""
You are a software engineering intern.

Your mentor gave you this task: "{task}"

Break this down into smaller subtasks in logical order. For each subtask, provide:
- id (start from 1)
- title
- description
- complexity (low/medium/high)
- dependencies (ids of any subtasks this depends on)

Format your answer in a valid JSON list of objects. Don't include any markdown formatting like ```json or ```. Just the pure JSON.
""")

    try:
        response_text = extract_text(response)
        # Remove markdown code block markers if present
        response_text = response_text.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
        subtasks = json.loads(response_text)

        # Normalize the subtasks
        normalized_subtasks = []
        for subtask in subtasks:
            normalized = {
                "id": subtask.get("id"),
                "title": subtask.get("title", "Untitled subtask"),
                "description": subtask.get("description", ""),
                "complexity": subtask.get("complexity", "unknown"),
                "depends_on": subtask.get("depends_on", subtask.get("dependencies", []))
            }
            normalized_subtasks.append(normalized)

    except Exception as e:
        print(f"⚠️ Failed to parse JSON from response: {e}. Returning raw text.")
        print("Raw Gemini response:\n", response_text)
        normalized_subtasks = [{
            "id": 1,
            "title": "Parsing Error",
            "description": response_text,
            "complexity": "high",
            "depends_on": []
        }]

    print("📝 Subtasks:")
    for task in normalized_subtasks:
        task_id = task.get("id", "?")
        title = task.get("title", "No title")
        complexity = task.get("complexity", "unknown")
        depends_on = task.get("depends_on", [])
        print(f"- [{task_id}] {title} (Complexity: {complexity}, Depends on: {depends_on})")

    state["subtasks"] = normalized_subtasks
    return state
