import os
import shutil
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
import google.generativeai as genai
from typing import TypedDict
from datetime import datetime
import git
import requests
import re
from typing import TypedDict
from langgraph.graph import StateGraph, END


class AgentState(TypedDict, total=False):
    task: str
    analysis: str
    code: str
    pr_status: str
    github_repo: str
    local_path: str
    documentation: str


load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def extract_text(response):
    try:
        return response.candidates[0].content.parts[0].text.strip()
    except Exception as e:
        return f"[ERROR extracting text] {e}"

def clarify_task(state: AgentState) -> AgentState:
    task = state["task"]
    model = genai.GenerativeModel("models/gemini-2.0-flash")
    response = model.generate_content(
        f"Is this task ambiguous? If yes, ask ONE specific clarifying question:\n\nTask: {task}\n\n"
        f"Reply with 'CLEAR' if the task is understandable."
    )
    question = response.text.strip()
    print("\n🤖 Clarifying Agent:", question)
    if "CLEAR" not in question.upper():
        user_input = input("\n🧑 Your Answer: ")
        state["clarification"] = user_input
        state["task"] = f"{task}\n\nAdditional context: {user_input}"

    return {"task": state["task"]}

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

    return {"analysis": analysis}

def detect_language_and_extension(code: str) -> tuple[str, str]:
    """Heuristically detect language and return (language, file extension)."""
    if re.search(r'^\s*import\s+\w+', code, re.MULTILINE) and 'def ' in code:
        return 'python', 'py'
    elif 'console.log' in code or 'function' in code:
        return 'javascript', 'js'
    elif re.search(r'#include\s+<\w+>', code) or 'int main' in code:
        return 'c++', 'cpp'
    elif 'public static void main' in code:
        return 'java', 'java'
    elif 'class' in code and 'self' in code:
        return 'python', 'py'
    elif 'print(' in code and not ';' in code:
        return 'python', 'py'
    elif '<?php' in code:
        return 'php', 'php'
    elif '<html>' in code or '</html>' in code:
        return 'html', 'html'
    elif 'SELECT' in code.upper() and 'FROM' in code.upper():
        return 'sql', 'sql'
    else:
        return 'text', 'txt'

def generate_code(state: AgentState) -> AgentState:
    analysis = state.get("analysis")
    if not analysis or analysis.startswith("[ERROR]"):
        state["code"] = "[ERROR] Cannot generate code without analysis."
        return state

    print("\n🧠 Generating code from analysis...")
    model = genai.GenerativeModel("models/gemini-1.5-flash")
    response = model.generate_content(f"Write the code based on the following analysis:\n{analysis}")
    code = extract_text(response).strip()

    if not code:
        print("❌ No code generated.")
        state["code"] = "[ERROR] No code generated."
        return state

    state["code"] = code

    # Detect language and assign file extension
    language, extension = detect_language_and_extension(code)
    if not extension:
        extension = "py"  # Fallback
        print("⚠️ Language detection failed. Defaulting to .py")

    filename = f"generated_code.{extension}"

    # Save to a file in the temp folder
    local_path = state.get("local_path") or f"./temp_repo_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    os.makedirs(local_path, exist_ok=True)
    file_path = os.path.join(local_path, filename)
    print(f"✅ Code saved to: {file_path} ({language})")
    print(f"📁 Folder now contains: {os.listdir(local_path)}")
    print(f"DEBUG: Does file exist? {os.path.exists(file_path)}")
    print(f"DEBUG: Listing files in {local_path}: {os.listdir(local_path)}")
    print(f"DEBUG: Full path: {file_path}")


    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)
        state["generated_file_name"] = filename
        state["local_path"] = local_path  # Ensure it's persisted
        print(f"✅ Code saved to: {file_path} ({language})")
    except Exception as e:
        print(f"❌ Failed to save code: {e}")
        state["code"] = f"[ERROR] Failed to save code: {e}"

    return {
        "code": code,
        "generated_file_name": filename,
        "local_path": local_path,
        "language": language
    }

def write_pr(state: AgentState) -> AgentState:
    task = state.get("task")
    code = state.get("code")
    github_repo = state.get("github_repo")
    github_token = os.getenv("GITHUB_TOKEN")

    if not all([task, code, github_repo, github_token]):
        print("❌ Missing required inputs: task/code/github_repo/token")
        state["pr_status"] = "PR Failed: Missing input"
        return state

    local_path = state.get("local_path")
    backup_files = {}

    # Backup all files if path exists (before deleting non-git folder)
    if os.path.exists(local_path):
        try:
            _ = git.Repo(local_path)  # try to open as repo
        except git.exc.InvalidGitRepositoryError:
            print(f"📥 Cloning {github_repo} to {local_path} (folder is not a valid Git repo)...")

            for fname in os.listdir(local_path):
                fpath = os.path.join(local_path, fname)
                if os.path.isfile(fpath):
                    with open(fpath, "r", encoding="utf-8") as f:
                        backup_files[fname] = f.read()

            shutil.rmtree(local_path)  # remove non-git folder

    # Clone repo
    if not os.path.exists(local_path):
        repo_url = f"https://{github_token}@github.com/{github_repo}.git"
        repo = git.Repo.clone_from(repo_url, local_path)
    else:
        repo = git.Repo(local_path)

    # Restore backed-up files
    for fname, content in backup_files.items():
        with open(os.path.join(local_path, fname), "w", encoding="utf-8") as f:
            f.write(content)
        print(f"🔁 Restored file: {fname}")

    state["local_path"] = local_path

    branch_name = input("🔀 Enter a branch name: ").strip()
    if branch_name in repo.heads:
        print(f"♻️ Branch '{branch_name}' already exists. Reusing it.")
        new_branch = repo.heads[branch_name]
    else:
        new_branch = repo.create_head(branch_name)
    new_branch.checkout()

    print("\n📂 You can now upload files to push. Paste full file paths, one per line. Leave blank to skip.")
    file_paths = []
    while True:
        path = input("📎 File path (ENTER to stop): ").strip()
        if not path:
            break

        if os.path.exists(path):
            dest_path = os.path.join(local_path, os.path.basename(path))
            if os.path.abspath(path) == os.path.abspath(dest_path):
                print(f"⚠️ Skipped copying '{path}' (source and destination are the same).")
                continue

            if os.path.isdir(path):
                shutil.copytree(path, dest_path, dirs_exist_ok=True)
                print(f"📁 Copied folder: {path}")
            else:
                shutil.copy(path, dest_path)
                print(f"📄 Copied file: {path}")
            file_paths.append(os.path.basename(path))

        else:
            print("⚠️ File does not exist.")

    if not file_paths:
        generated_file_name = state.get("generated_file_name", "generated_code.py")
        fallback_path = os.path.join(local_path, generated_file_name)
        with open(fallback_path, "w", encoding="utf-8") as f:
            f.write(code)
        file_paths.append(generated_file_name)

    readme_path = os.path.join(local_path, "README.md")
    gitignore_path = os.path.join(local_path, ".gitignore")

    if not os.path.exists(readme_path):
        with open(readme_path, "w") as f:
            f.write(f"# Project for task: {task}\n\nAuto-generated by Project Buddy.\n")
        file_paths.append("README.md")

    if not os.path.exists(gitignore_path):
        with open(gitignore_path, "w") as f:
            f.write("__pycache__/\n*.pyc\n.env\n")
        file_paths.append(".gitignore")

    repo.git.add(A=True)
    if repo.is_dirty(untracked_files=True):
        print("📦 Files staged for commit:")
        print(repo.git.status('--short'))

        repo.index.commit(f"feat: add files for task - {task}")
        repo.remote(name="origin").push(refspec=f"{branch_name}:{branch_name}")
        print(f"✅ Code committed and pushed to `{branch_name}`")
    else:
        print("⚠️ No changes to commit.")
        state["pr_status"] = "PR Failed: No changes to commit."
        return state

    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json"
    }

    # Check if PR already exists
    pr_check_url = f"https://api.github.com/repos/{github_repo}/pulls?head={github_repo.split('/')[0]}:{branch_name}"
    check_response = requests.get(pr_check_url, headers=headers)
    pr_url = None

    if check_response.status_code == 200 and check_response.json():
        pr_url = check_response.json()[0]["html_url"]
        print("♻️ Pull Request already exists. Updating branch only.")
        state["pr_status"] = f"✅ Updated existing PR: {pr_url}"
    else:
        # Create PR
        payload = {
            "title": f"Auto PR: {task}",
            "body": "PR auto-generated by Project Buddy.",
            "head": branch_name,
            "base": "main"
        }
        pr_response = requests.post(
            f"https://api.github.com/repos/{github_repo}/pulls",
            headers=headers,
            json=payload
        )

        if pr_response.status_code == 201:
            pr_url = pr_response.json()["html_url"]
            print("🎉 Pull Request Created:", pr_url)
            state["pr_status"] = f"PR Created: {pr_url}"
        else:
            print("❌ PR Failed:", pr_response.status_code, pr_response.text)
            state["pr_status"] = f"PR Failed: {pr_response.status_code} - {pr_response.text}"

    return {
        "local_path": local_path,
        "pr_status": state["pr_status"]
    }

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

def build_graph():
    from langgraph.graph import StateGraph
    from langgraph.graph import END

    builder = StateGraph(AgentState)

    builder.add_node("Clarify Task", clarify_task)
    builder.add_node("Analyze Task", analyze_task)
    builder.add_node("Generate Code", generate_code)
    builder.add_node("Write Docs", write_docs)
    builder.add_node("Write PR", write_pr)

    builder.set_entry_point("Clarify Task")
    builder.add_edge("Clarify Task", "Analyze Task")
    builder.add_edge("Analyze Task", "Generate Code")
    builder.add_edge("Generate Code", "Write Docs")
    builder.add_edge("Write Docs", "Write PR")
    builder.add_edge("Write PR", END)

    return builder.compile()

if __name__ == "__main__":
    workflow = build_graph()

    task = input("📝 Enter the task you want Project Buddy to work on: ").strip()
    github_repo = input("🌐 Enter your GitHub repo (e.g., username/repo): ").strip()
    local_path = input("📁 Enter the local path to your cloned repo (or leave blank to clone fresh): ").strip()

    if not all([task, github_repo]):
        print("❌ All inputs are required. Exiting.")
        exit(1)
    if not local_path:
        local_path = f"./temp_repo_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    print("\n🚧 Starting Project Buddy for task:", task)
    result = workflow.invoke({
        "task": task,
        "github_repo": github_repo,
        "local_path": local_path
    })

    print("\n🎉 Workflow Complete!")
    print("🔚 Final Agent State:\n")
    for key, value in result.items():
        print(f"{key.upper()}:\n{value}\n")
