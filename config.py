"""
Configuration loader.

Reads framework_path from config.json in the repo root. Falls back to
~/Developer/engineering-playbook if config.json is absent — works out of
the box for the local-developer setup, requires explicit config for any
other layout.

config.json is gitignored so each user's path stays local.
"""

import json, os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
CONFIG_FILE = REPO_ROOT / "config.json"
DEFAULT_FRAMEWORK_PATH = os.path.expanduser("~/Developer/engineering-playbook")


def get_framework_path():
    """Return absolute path to the engineering-playbook directory."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return os.path.expanduser(json.load(f).get("framework_path", DEFAULT_FRAMEWORK_PATH))
    return DEFAULT_FRAMEWORK_PATH
