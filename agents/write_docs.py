from agents.state import AgentState
from agents.utils import extract_text
import google.generativeai as genai
import os

def write_docs(state: AgentState) -> AgentState:
    task = state.get("task")
    code = state.get("code")

    if not code or not task:
        state["documentation"] = "[ERROR] Missing code or task for documentation."
        return state

    print("📝 Generating documentation...")
    model = genai.GenerativeModel("models/gemini-1.5-flash")

    response = model.generate_content(
        f"""Generate developer-facing documentation for the following task and code. 
The documentation should include purpose, how it works, and usage examples if possible.

Task:
{task}

Code:
{code[:5000]}"""  # truncate if large
    )

    docs = extract_text(response)
    state["documentation"] = docs

    # Save documentation to markdown file
    try:
        local_path = state.get("local_path", ".")
        doc_path = os.path.join(local_path, "FEATURE_DOC.md")
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write(docs)
        print(f"📄 Documentation written to {doc_path}")
    except Exception as e:
        print(f"❌ Failed to save documentation: {e}")
        state["documentation"] = f"[ERROR] Failed to save docs: {e}"

    return {
        "documentation": state["documentation"],
        "local_path": local_path
    }   

