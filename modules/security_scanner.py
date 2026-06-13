import re
import pandas as pd

# Very lightweight static security heuristics.
# NOTE: This is NOT a complete vulnerability scanner.
# It provides beginner-friendly, reusable building blocks for the platform.

SECURITY_PATTERNS = [
    {
        "name": "Use of eval()",
        "pattern": r"\beval\s*\(",
        "severity": "High",
        "suggestion": "Avoid eval(). Use a safer parser or mapping-based dispatch."
    },
    {
        "name": "Use of exec()",
        "pattern": r"\bexec\s*\(",
        "severity": "High",
        "suggestion": "Avoid exec(). Use explicit functions/classes or restricted execution environments."
    },
    {
        "name": "Potential command execution (os.system)",
        "pattern": r"\bos\.system\s*\(",
        "severity": "High",
        "suggestion": "Avoid os.system(). Use subprocess with argument lists and proper validation, or safer libraries."
    },
    {
        "name": "Potential command execution (subprocess)",
        "pattern": r"\bsubprocess\.(Popen|call|check_output|run)\s*\(",
        "severity": "Medium",
        "suggestion": "Review subprocess usage. Ensure commands are not built from untrusted input."
    },
    {
        "name": "Insecure deserialization (pickle.loads)",
        "pattern": r"\bpickle\.(loads|load)\s*\(",
        "severity": "High",
        "suggestion": "Avoid untrusted pickle.loads(). Use safer serialization formats (json, msgpack) or strict allowlists."
    },
    {
        "name": "Hard-coded secrets (basic patterns)",
        "pattern": r"\b(AKIA[0-9A-Z]{16})\b|\b(AIza[0-9A-Za-z\-_]{35})\b|\b(SECRET_KEY\s*=)|\b(password\s*=\s*['\"][^'\"]+['\"])",
        "severity": "Medium",
        "suggestion": "Remove hard-coded secrets. Use environment variables or a secret manager."
    },
]


def scan_security(code: str) -> pd.DataFrame:
    findings = []
    lines = code.splitlines() or [""]

    for rule in SECURITY_PATTERNS:
        for match in re.finditer(rule["pattern"], code, flags=re.IGNORECASE):
            line_number = code[:match.start()].count("\n") + 1
            findings.append(
                {
                    "Issue": rule["name"],
                    "Line": line_number,
                    "Severity": rule["severity"],
                    "Matched Code": lines[line_number - 1].strip() if 1 <= line_number <= len(lines) else "",
                    "Suggestion": rule["suggestion"],
                }
            )

    return pd.DataFrame(findings)


def summarize_security(findings_df: pd.DataFrame):
    if findings_df is None or findings_df.empty:
        return "No high-confidence security issues found by basic static checks."

    # Beginner-friendly: just list unique suggestions
    unique = findings_df["Suggestion"].drop_duplicates().tolist() if "Suggestion" in findings_df.columns else []
    return "\n".join(f"- {s}" for s in unique)
