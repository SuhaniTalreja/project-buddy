import streamlit as st
import requests
import datetime

st.set_page_config(page_title="Project Buddy", layout="centered")

st.title("🧠 Project Buddy")
st.markdown("Build, clarify, document, and push code automatically.")

# Task Input
task = st.text_area("📝 Task", placeholder="e.g., Add a login API with JWT auth")

# GitHub Repo Input
repo = st.text_input("🔗 GitHub Repo (username/repo)", placeholder="e.g., suhani/project-buddy")

# Local Path (optional)
path = st.text_input("📁 Local Clone Path (leave empty to auto-clone)")

# Branch Name Input (optional)
branch_name = st.text_input("🔀 Branch Name (optional)", placeholder="e.g., feature-login-api")

# Step selection
all_steps = [
    "Clarify Task",
    "Analyze Task",
    "Decompose Task",
    "Generate Code",
    # "Analyze Code Quality",  # Uncomment if supported
    "Write Docs",
    "Write PR"
]

st.markdown("### 📦 Select Steps")
selected_steps = st.multiselect("Choose which steps to run", all_steps, default=all_steps)

# Submit button
if st.button("🚀 Run Project Buddy"):
    if not task or not repo:
        st.warning("❗ Please enter both task and GitHub repo.")
    else:
        with st.spinner("Running Project Buddy..."):
            try:
                response = requests.post("http://localhost:5000/run", json={
                    "task": task,
                    "github_repo": repo,
                    "local_path": path,
                    "branch_name": branch_name,
                    "steps": selected_steps
                })
                res = response.json()

                if response.status_code != 200:
                    st.error(f"❌ Server error: {res.get('error', 'Unknown error')}")
                else:
                    st.success("✅ Project Buddy completed successfully!")

                    st.markdown("### 🧾 Logs")
                    st.code("\n".join(res.get("logs", ["No logs available."])))

                    st.markdown("### 📬 Result")
                    st.json(res.get("outputs", {}))

                    # Store the clarification result
                    clarified_task = res.get("outputs", {}).get("clarified_task")

                    if res.get("clarification_needed") and clarified_task:
                        st.warning("❓ Clarification Needed")
                        st.markdown("**Suggested Interpretation:**")
                        st.info(clarified_task)

                        if st.button("✅ Yes, proceed with this clarified task"):
                            # Re-trigger the run with the clarified task instead of asking again
                            with st.spinner("Re-running with clarified task..."):
                                response = requests.post("http://localhost:5000/run", json={
                                    "task": clarified_task,  # 👈 use the clarified version
                                    "github_repo": repo,
                                    "local_path": path,
                                    "branch_name": branch_name,
                                    "steps": [s for s in selected_steps if s != "Clarify Task"]  # skip clarify on second run
                                })
                                res2 = response.json()
                                st.success("✅ Task clarified and re-run successfully!")
                                st.markdown("### 🧾 Logs")
                                st.code("\n".join(res2.get("logs", ["No logs available."])))
                                st.markdown("### 📬 Final Result")
                                st.json(res2.get("outputs", {}))
                                if "pr_url" in res2:
                                    st.markdown(f"[🔗 View Pull Request]({res2['pr_url']})")
            except Exception as e:
                st.error(f"❌ Something went wrong: {e}")
