"""
modules/dependency_analyzer.py
Detects outdated, deprecated, or risky library imports and suggests replacements.
"""

import re
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

# ── Deprecated / outdated library rules ───────────────────────────────────────
# Format: (import_pattern, library_name, status, replacement, notes)
DEPRECATED_LIBRARIES = [
    # Python
    (r"\bimport\s+urllib2\b",              "urllib2",          "Removed in Python 3",
     "urllib.request / urllib.error",      "Standard in Python 3"),
    (r"\bimport\s+httplib\b",              "httplib",          "Removed in Python 3",
     "http.client",                        "Standard in Python 3"),
    (r"\bimport\s+cookielib\b",            "cookielib",        "Removed in Python 3",
     "http.cookiejar",                     "Standard in Python 3"),
    (r"\bimport\s+cPickle\b",              "cPickle",          "Removed in Python 3",
     "pickle",                             "cPickle merged into pickle in Python 3"),
    (r"\bimport\s+MySQLdb\b",              "MySQLdb",          "Largely unmaintained",
     "mysql-connector-python or PyMySQL",  "Better Python 3 support"),
    (r"\bimport\s+pycrypto\b|from\s+Crypto\b", "PyCrypto",     "Unmaintained, security issues",
     "cryptography or PyCryptodome",       "PyCrypto has known vulnerabilities"),
    (r"\bimport\s+nose\b",                 "nose",             "Maintenance mode",
     "pytest",                             "pytest is the modern standard"),
    (r"\bfrom\s+sklearn\s+import\s+cross_validation\b", "sklearn.cross_validation",
     "Removed in sklearn 0.20",
     "sklearn.model_selection",            "Renamed in scikit-learn 0.20"),
    (r"\bimport\s+imp\b",                  "imp",              "Deprecated since Python 3.4",
     "importlib",                          "Use importlib.import_module()"),
    (r"\bimport\s+distutils\b",            "distutils",        "Removed in Python 3.12",
     "setuptools",                         "Use setuptools for packaging"),
    (r"\bfrom\s+distutils\b",              "distutils",        "Removed in Python 3.12",
     "setuptools",                         "Use setuptools for packaging"),
    (r"\bimport\s+optparse\b",             "optparse",         "Deprecated since Python 3.2",
     "argparse",                           "argparse is the modern CLI parser"),
    (r"\bimport\s+md5\b|\bimport\s+sha\b", "md5/sha modules",  "Removed in Python 3",
     "hashlib",                            "Use hashlib.md5() / hashlib.sha256()"),
    (r"\bimport\s+sets\b",                 "sets module",      "Removed in Python 3",
     "set() built-in",                     "Python 3 set() replaces the sets module"),
    (r"\bimport\s+string\b.*maketrans|string\.maketrans\b", "string.maketrans",
     "Removed in Python 3",
     "str.maketrans()",                    "Use str.maketrans() instead"),

    # Python web frameworks (older versions)
    (r"\bfrom\s+flask\s+import\b",         "Flask",            "Check version for security patches",
     "Flask ≥ 3.x",                        "Ensure you're on a maintained version"),
    (r"\bfrom\s+django\b|\bimport\s+django\b", "Django",       "Check version for security patches",
     "Django ≥ 4.2 LTS",                   "LTS versions receive security updates"),

    # JavaScript / Node
    (r'"request"\s*:',                     "request (npm)",    "Deprecated",
     "axios or node-fetch",                "request is unmaintained since 2020"),
    (r'"gulp"\s*:',                        "gulp",             "Declining usage",
     "Vite or esbuild",                    "Modern build tools are faster"),
    (r'"bower"\s*:',                       "bower",            "Deprecated",
     "npm or yarn workspaces",             "bower is unmaintained"),
    (r'"moment"\s*:',                      "moment.js",        "Legacy mode (no new features)",
     "dayjs or date-fns or Temporal API",  "moment.js is very large; modern alternatives are better"),
    (r'"lodash"\s*:',                      "lodash",           "Often unnecessary",
     "Native ES6+ methods",                "Many lodash functions are now native JS"),

    # Java
    (r"import\s+com\.sun\.\w+",            "com.sun.*",        "Internal JDK API (unsupported)",
     "Standard java.* APIs",               "Internal APIs may be removed without notice"),
    (r"import\s+javax\.xml\.bind",         "javax.xml.bind (JAXB)", "Removed from JDK 11+",
     "jakarta.xml.bind",                   "Add jakarta.xml.bind-api dependency"),
    (r"import\s+sun\.\w+",                 "sun.*",            "Unsupported internal API",
     "Standard java.* or open-source libs", "sun.* APIs are implementation details"),

    # PHP
    (r"\bmysql_connect\s*\(",              "mysql_* functions", "Removed in PHP 7",
     "PDO or mysqli",                      "mysql_* was removed; use PDO for security"),
    (r"\bereg\s*\(",                       "ereg/eregi",       "Removed in PHP 7",
     "preg_match()",                       "POSIX regex removed; use PCRE"),
    (r"\bsplit\s*\(",                      "split()",          "Removed in PHP 7",
     "explode() or preg_split()",          "split() was removed in PHP 7"),
    (r"\bmagic_quotes",                    "magic_quotes",     "Removed in PHP 5.4",
     "addslashes() or PDO params",         "Magic quotes was a misguided feature"),
]


def analyze_dependencies(code: str, filename: str = "") -> List[Dict]:
    """
    Scan code/requirements for deprecated or risky dependencies.

    Returns list of dicts with: library, status, replacement, notes, line
    """
    findings = []
    lines = code.splitlines()

    for pattern, lib, status, replacement, notes in DEPRECATED_LIBRARIES:
        try:
            for match in re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE):
                line_no = code[:match.start()].count("\n") + 1
                snippet = lines[line_no - 1].strip()[:100] if line_no <= len(lines) else ""
                findings.append({
                    "library":     lib,
                    "status":      status,
                    "replacement": replacement,
                    "notes":       notes,
                    "line":        line_no,
                    "snippet":     snippet,
                })
        except re.error:
            continue

    # Deduplicate by library + line
    seen = set()
    unique = []
    for f in findings:
        key = (f["library"], f["line"])
        if key not in seen:
            seen.add(key)
            unique.append(f)

    logger.info(f"Dependency analysis: {len(unique)} issues found in {filename}")
    return unique
