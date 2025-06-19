# 🧠 Project Buddy — Your Autonomous AI Intern

**Project Buddy** is an autonomous AI-powered intern that streamlines software development workflows by clarifying vague tasks, generating code, writing documentation, and pushing GitHub pull requests — all through a simple web interface built with **Flask** and **Streamlit**.

---

## 🚀 Features

1. **Task Clarification** — Uses Gemini to detect vague tasks and auto-suggest clarifying questions.
2. **Task Analysis & Decomposition** — Breaks large tasks into manageable subtasks.
3. **Code Generation** — Generates backend/frontend code using AI based on the clarified task.
4. **Documentation** — Writes documentation for generated code automatically.
5. **PR Creation** — Commits code and creates pull requests on GitHub.
6. **Web Interface** — Run the entire workflow via a no-code UI built in Streamlit.
7. **Modular Workflow** — Select which steps (clarify, generate, doc, PR, etc.) to run.

---

## 🛠️ Tech Stack

- **LLM**: Google Gemini Pro (via `google.generativeai`)
- **Workflow Engine**: [LangGraph](https://github.com/langchain-ai/langgraph)
- **Backend**: Flask
- **Frontend**: Streamlit
- **Version Control**: Git + GitHub Integration


