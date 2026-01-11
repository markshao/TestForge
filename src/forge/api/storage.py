import os
import yaml
from typing import List, Dict, Optional

STORAGE_DIR = os.path.join(os.path.dirname(__file__), "../../../storage/testcases")

def list_testcases() -> List[str]:
    """List all available testcase files."""
    if not os.path.exists(STORAGE_DIR):
        return []
    return [f for f in os.listdir(STORAGE_DIR) if f.endswith('.yaml') or f.endswith('.yml')]

def get_testcase_content(filename: str) -> Optional[str]:
    """Read content of a testcase file."""
    path = os.path.join(STORAGE_DIR, filename)
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return f.read()

def save_testcase(filename: str, content: str) -> None:
    """Save a testcase file."""
    if not os.path.exists(STORAGE_DIR):
        os.makedirs(STORAGE_DIR)
    path = os.path.join(STORAGE_DIR, filename)
    with open(path, "w") as f:
        f.write(content)
