import subprocess
import json
from agents.state import AgentState
from agents.utils import extract_text
import google.generativeai as genai
def analyze_code_quality(state: AgentState) -> AgentState:
    files_to_analyze = state.get("modified_files", [])
    import os

    def find_files_in_repo(path):
        """Generator that finds all Python files in the repository"""
        for root, _, files in os.walk(path):
            for f in files:
                if f.endswith(".py"):
                    yield os.path.join(root, f)

    # Get files to analyze
    if not files_to_analyze:
        print("⚠️ No modified files listed. Falling back to scanning repo.")
        repo_path = state.get("repo_path", ".")
        print(f"🔎 Scanning repository at: {repo_path}")
        files_to_analyze = list(find_files_in_repo(repo_path))

        if not files_to_analyze:
            print("⚠️ No Python files found to analyze.")
            return state

    print(f"\n🔍 Analyzing {len(files_to_analyze)} files for code quality...")
    print("Files to analyze:", ", ".join(files_to_analyze))

    analysis_results = []

    for file in files_to_analyze:
        if not os.path.exists(file):
            print(f"⚠️ File not found: {file}")
            continue

        print(f"\n📄 Analyzing {file}...")
        result = {
            "file": file,
            "radon": "",
            "pylint": "",
            "file_size": os.path.getsize(file)
        }

        # Run radon for cyclomatic complexity
        try:
            print("  Running radon...")
            radon_out = subprocess.check_output(
                ["radon", "cc", "-s", file],
                stderr=subprocess.PIPE,
                text=True
            )
            result["radon"] = radon_out
            print("  Radon completed successfully")
        except subprocess.CalledProcessError as e:
            error_msg = f"[Radon Error] {e.stderr.strip() if e.stderr else str(e)}"
            result["radon"] = error_msg
            print(f"  Radon failed: {error_msg}")
        except Exception as e:
            error_msg = f"[Radon Unexpected Error] {str(e)}"
            result["radon"] = error_msg
            print(f"  Radon failed: {error_msg}")

        # Run pylint for style and errors
        try:
            print("  Running pylint...")
            pylint_out = subprocess.check_output(
                ["pylint", file, "--disable=all", "--enable=C,R,W,E"],
                stderr=subprocess.PIPE,
                text=True
            )
            result["pylint"] = pylint_out
            print("  Pylint completed successfully")
        except subprocess.CalledProcessError as e:
            # Pylint returns non-zero exit code even when it finds issues
            if e.returncode in (1, 2, 4, 8, 16, 32):
                result["pylint"] = e.output
                print("  Pylint completed with findings")
            else:
                error_msg = f"[Pylint Error] {e.stderr.strip() if e.stderr else str(e)}"
                result["pylint"] = error_msg
                print(f"  Pylint failed: {error_msg}")
        except Exception as e:
            error_msg = f"[Pylint Unexpected Error] {str(e)}"
            result["pylint"] = error_msg
            print(f"  Pylint failed: {error_msg}")

        analysis_results.append(result)

    # Generate suggestions if we got any results
    if not analysis_results:
        print("⚠️ No analysis results to process")
        return state

    print("\n📊 Analysis results collected. Generating suggestions...")
    model = genai.GenerativeModel("models/gemini-1.5-flash")
    prompt = f"""
You're an AI intern reviewing Python code. Here are static analysis results:

{json.dumps(analysis_results, indent=2)}

Based on these, suggest:
- Refactor opportunities (with specific code examples)
- Complexity reduction tips
- Code quality improvements (naming, structure, readability)
- Any potential bugs found

Give actionable suggestions per file, focusing on the most critical issues first.
"""

    try:
        response = model.generate_content(prompt)
        suggestions = extract_text(response)
        print("\n🛠️ Refactor suggestions generated successfully")
        state["refactor_suggestions"] = suggestions
    except Exception as e:
        print(f"⚠️ Failed to generate suggestions: {str(e)}")
        state["refactor_suggestions"] = f"Error generating suggestions: {str(e)}"

    return state