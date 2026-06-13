"""
modules/github_integration.py
Fetch single files and shallow-clone public GitHub repositories for analysis.
"""

import os
import re
import logging
import tempfile
import shutil
from typing import Dict, Tuple, Optional

import requests

logger = logging.getLogger(__name__)

# Supported code file extensions for repository scanning
SUPPORTED_EXTENSIONS = {
    ".py", ".java", ".js", ".ts", ".php", ".c", ".cpp", ".cc",
    ".sql", ".sh", ".bash", ".rb", ".go", ".rs", ".kt", ".cs",
    ".html", ".css", ".xml", ".yaml", ".yml", ".json", ".txt",
    ".ipynb", ".md", ".tsx", ".jsx", ".pyw"
}


def _raw_url_from_github(url: str) -> str:
    """Convert a github.com blob URL to its raw equivalent."""
    # https://github.com/user/repo/blob/main/file.py
    # → https://raw.githubusercontent.com/user/repo/main/file.py
    url = url.strip()
    if "raw.githubusercontent.com" in url:
        return url
    url = re.sub(r"github\.com/([^/]+)/([^/]+)/blob/", r"raw.githubusercontent.com/\1/\2/", url)
    return url


def fetch_github_file(url: str) -> Tuple[str, Optional[str]]:
    """
    Fetch a single file from GitHub (raw URL or blob URL).

    Returns:
        (code_text, None)  on success
        ("", error_message) on failure
    """
    raw_url = _raw_url_from_github(url)
    try:
        r = requests.get(raw_url, timeout=20)
        r.raise_for_status()
        logger.info(f"Fetched GitHub file: {raw_url}")
        return r.text, None
    except requests.exceptions.HTTPError as e:
        return "", f"HTTP {r.status_code}: {e}"
    except requests.exceptions.RequestException as e:
        return "", str(e)


def clone_github_repo(repo_url: str, branch: str = "main") -> Tuple[Dict[str, str], Optional[str]]:
    """
    Attempt to list and read files from a public GitHub repo via the API.
    Does NOT require git to be installed.

    Returns:
        (files_dict, None)      on success — {relative_path: code_text}
        ({}, error_message)     on failure
    """
    # Parse owner/repo from URL
    match = re.search(r"github\.com[/:]([^/]+)/([^/]+?)(?:\.git)?/?$", repo_url.strip())
    if not match:
        return {}, "Could not parse GitHub repository URL. Expected: https://github.com/owner/repo"

    owner, repo = match.group(1), match.group(2)
    api_base = f"https://api.github.com/repos/{owner}/{repo}"

    try:
        # First, fetch repository metadata to find its actual default branch
        repo_meta_r = requests.get(api_base, timeout=10, headers={"Accept": "application/vnd.github.v3+json"})
        repo_meta_r.raise_for_status()
        repo_meta = repo_meta_r.json()
        actual_branch = repo_meta.get("default_branch", branch)
        branch = actual_branch  # update for raw url usage later

        # Get the default branch tree recursively
        tree_url = f"{api_base}/git/trees/{actual_branch}?recursive=1"
        r = requests.get(tree_url, timeout=20, headers={"Accept": "application/vnd.github.v3+json"})
        r.raise_for_status()
        data = r.json()
    except requests.exceptions.HTTPError as e:
        return {}, f"Could not access repository tree. Make sure the repo is public. ({e})"
    except requests.exceptions.RequestException as e:
        return {}, str(e)

    files = {}
    blob_items = [item for item in data.get("tree", [])
                  if item["type"] == "blob"
                  and any(item["path"].endswith(ext) for ext in SUPPORTED_EXTENSIONS)
                  and item.get("size", 0) < 100_000]  # skip files > 100 KB

    # Limit to first 30 files to avoid rate limits
    for item in blob_items[:30]:
        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{item['path']}"
        try:
            rr = requests.get(raw_url, timeout=10)
            if rr.status_code == 200:
                files[item["path"]] = rr.text
        except Exception:
            continue

    if not files:
        return {}, "No supported code files found in the repository (or all files exceeded size limit)."

    logger.info(f"Cloned {len(files)} files from {owner}/{repo}@{branch}")
    return files, None
