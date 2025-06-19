# import os
# import datetime
# from dotenv import load_dotenv
# from langgraph.graph import StateGraph, END
# from agents.state import AgentState
# from agents.clarify_task import clarify_task
# from agents.analyze_task import analyze_task
# from agents.decompose_task import decompose_task
# from agents.generate_code import generate_code
# from agents.write_docs import write_docs
# from agents.write_pr import write_pr
# # from agents.analyzeCodeQuality import analyze_code_quality
# import google.generativeai as genai


# load_dotenv()
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# STEPS = {
#     "Clarify Task": clarify_task,
#     "Analyze Task": analyze_task,
#     "Decompose Task": decompose_task,
#     "Generate Code": generate_code,
#     # "Analyze Code Quality": analyze_code_quality,
#     "Write Docs": write_docs,
#     "Write PR": write_pr,
# }

# DEFAULT_ORDER = [
#     "Clarify Task",
#     "Analyze Task",
#     "Decompose Task",
#     "Generate Code",
#     # "Analyze Code Quality",
#     "Write Docs",
#     "Write PR"
# ]

# def get_user_steps():
#     print("🧩 Select which steps you want Project Buddy to perform (comma-separated numbers):")
#     for idx, step in enumerate(DEFAULT_ORDER, start=1):
#         print(f"{idx}. {step}")
#     user_input = input("👉 Enter numbers (e.g., 1,2,4,6) or press ENTER for all: ").strip()

#     if not user_input:
#         return DEFAULT_ORDER

#     selected_indices = [int(x.strip()) for x in user_input.split(",") if x.strip().isdigit()]
#     selected_steps = [DEFAULT_ORDER[i - 1] for i in selected_indices if 0 < i <= len(DEFAULT_ORDER)]

#     return selected_steps

# def build_graph(selected_steps):
#     builder = StateGraph(AgentState)

#     # Add nodes
#     for step in selected_steps:
#         builder.add_node(step, STEPS[step])

#     # Add edges
#     for i in range(len(selected_steps) - 1):
#         builder.add_edge(selected_steps[i], selected_steps[i + 1])

#     builder.set_entry_point(selected_steps[0])
#     builder.add_edge(selected_steps[-1], END)

#     return builder.compile()

# if __name__ == "__main__":
#     task = input("📝 Enter the task you want Project Buddy to work on: ").strip()
#     github_repo = input("🌐 Enter your GitHub repo (e.g., username/repo): ").strip()
#     local_path = input("📁 Enter the local path to your cloned repo (or leave blank to clone fresh): ").strip()

#     if not all([task, github_repo]):
#         print("❌ All inputs are required. Exiting.")
#         exit(1)
#     if not local_path:
#         local_path = f"./temp_repo_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

#     selected_steps = get_user_steps()
#     print(f"\n🚧 Starting Project Buddy with steps: {selected_steps}")
#     workflow = build_graph(selected_steps)

#     result = workflow.invoke({
#         "task": task,
#         "github_repo": github_repo,
#         "local_path": local_path
#     })

#     print("\n🎉 Workflow Complete!")
#     print("🔚 Final Agent State:\n")
#     for key, value in result.items():
#         print(f"{key.upper()}:\n{value}\n")


import os
import datetime
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END

from agents.state import AgentState
from agents.clarify_task import clarify_task
from agents.analyze_task import analyze_task
from agents.decompose_task import decompose_task
from agents.generate_code import generate_code
from agents.write_docs import write_docs
from agents.write_pr import write_pr
# from agents.analyzeCodeQuality import analyze_code_quality

import google.generativeai as genai

# === Setup ===
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)

# === Step Config ===
STEPS = {
    "Clarify Task": clarify_task,
    "Analyze Task": analyze_task,
    "Decompose Task": decompose_task,
    "Generate Code": generate_code,
    # "Analyze Code Quality": analyze_code_quality,
    "Write Docs": write_docs,
    "Write PR": write_pr,
}

DEFAULT_ORDER = [
    "Clarify Task",
    "Analyze Task",
    "Decompose Task",
    "Generate Code",
    # "Analyze Code Quality",
    "Write Docs",
    "Write PR"
]

# === Graph Builder ===
def build_graph(selected_steps):
    builder = StateGraph(AgentState)

    for step in selected_steps:
        builder.add_node(step, STEPS[step])
    invalid_steps = [step for step in selected_steps if step not in STEPS]
    if invalid_steps:
        raise ValueError(f"Invalid steps selected: {invalid_steps}")

    for i in range(len(selected_steps) - 1):
        builder.add_edge(selected_steps[i], selected_steps[i + 1])

    builder.set_entry_point(selected_steps[0])
    builder.add_edge(selected_steps[-1], END)

    return builder.compile()

# === Flask Endpoint ===
@app.route("/run", methods=["POST"])
def run_project_buddy():
    try:
        data = request.json
        task = data.get("task", "").strip()
        github_repo = data.get("github_repo", "").strip()
        
        if not task or not github_repo:
            return jsonify({"error": "Task and GitHub repository are required"}), 400

        # Initialize with defaults
        local_path = data.get("local_path", "").strip() or \
                    f"./temp_repo_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        branch_name = data.get("branch_name", "").strip() or \
                     f"feature-{task.lower()[:20].replace(' ', '-')}-{datetime.datetime.now().strftime('%Y%m%d')}"

        selected_steps = [step for step in data.get("steps", DEFAULT_ORDER) if step in STEPS]
        
        # Initialize state
        initial_state = {
            "task": task,
            "github_repo": github_repo,
            "local_path": local_path,
            "branch_name": branch_name,
            "logs": [],
            "current_step": None
        }

        workflow = build_graph(selected_steps)
        result = workflow.invoke(initial_state)

        response = {
            "status": "success",
            "logs": result.get("logs", []),
            "outputs": {
                "task": result.get("task"),
                "github_repo": result.get("github_repo"),
                "local_path": result.get("local_path"),
                "branch_name": result.get("branch_name", branch_name),
                "clarified_task": result.get("clarified_task", task),
                "status": result.get("status", "completed")
            }
        }

        if result.get("clarification_needed"):
            response.update({
                "clarification_needed": True,
                "clarification_question": result.get("question"),
                "clarification_response": result.get("clarification_response")
            })

        if "pr_url" in result:
            response["pr_url"] = result["pr_url"]

        return jsonify(response)

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "message": "An error occurred during processing"
        }), 500

# === Run Server ===
if __name__ == "__main__":
    app.run(debug=True)
