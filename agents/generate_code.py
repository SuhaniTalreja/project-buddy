import os
import re
from datetime import datetime
from agents.state import AgentState
from agents.utils import extract_text
import google.generativeai as genai

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

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)
        state["generated_file_name"] = filename
        state["local_path"] = local_path 
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

