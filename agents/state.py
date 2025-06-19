from typing import TypedDict,List

class AgentState(TypedDict, total=False):
    logs: List[str]
    task: str
    analysis: str
    code: str
    pr_status: str
    github_repo: str
    local_path: str
    documentation: str
