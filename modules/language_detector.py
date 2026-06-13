"""
modules/language_detector.py
Detects programming language from code content and file extension.
"""

import re
from pathlib import Path


# ── Extension map ──────────────────────────────────────────────────────────────
EXT_MAP = {
    ".py":    "Python",
    ".java":  "Java",
    ".js":    "JavaScript",
    ".ts":    "TypeScript",
    ".php":   "PHP",
    ".c":     "C",
    ".cpp":   "C++",
    ".cc":    "C++",
    ".cxx":   "C++",
    ".sql":   "SQL",
    ".sh":    "Shell",
    ".bash":  "Shell",
    ".bat":   "Batch",
    ".cmd":   "Batch",
    ".xml":   "XML",
    ".yaml":  "YAML",
    ".yml":   "YAML",
    ".json":  "JSON",
    ".html":  "HTML",
    ".css":   "CSS",
    ".rb":    "Ruby",
    ".go":    "Go",
    ".rs":    "Rust",
    ".kt":    "Kotlin",
    ".swift": "Swift",
    ".cs":    "C#",
}

# ── Content fingerprints ───────────────────────────────────────────────────────
PATTERNS = [
    ("Python",     [r"\bprint\s*\(", r"\bdef\s+\w+\s*\(", r"\bimport\s+\w+", r"#!.*python"]),
    ("Java",       [r"public\s+class\s+\w+", r"System\.out\.println", r"import\s+java\.", r"void\s+main\s*\("]),
    ("JavaScript", [r"\bfunction\s+\w+\s*\(", r"console\.log\s*\(", r"const\s+\w+\s*=", r"document\."]),
    ("TypeScript", [r":\s*(string|number|boolean|void)\b", r"interface\s+\w+", r"import.*from\s+['\"]"]),
    ("PHP",        [r"<\?php", r"\$\w+\s*=", r"echo\s+", r"function\s+\w+\s*\("]),
    ("C",          [r"#include\s*<stdio\.h>", r"int\s+main\s*\(", r"printf\s*\(", r"malloc\s*\("]),
    ("C++",        [r"#include\s*<iostream>", r"std::", r"cout\s*<<", r"class\s+\w+\s*\{"]),
    ("SQL",        [r"\bSELECT\b", r"\bFROM\b", r"\bWHERE\b", r"\bINSERT\s+INTO\b", r"\bCREATE\s+TABLE\b"]),
    ("Shell",      [r"#!/bin/bash", r"#!/bin/sh", r"\becho\b", r"\bfi\b", r"\bdo\b\s+\bfor\b"]),
    ("Batch",      [r"@echo off", r"SET\s+\w+", r"GOTO\s+\w+", r"IF\s+EXIST"]),
    ("YAML",       [r"^\s*\w+:\s", r"---\s*$"]),
    ("JSON",       [r'^\s*\{', r'":\s*(true|false|null|\d+|")']),
    ("XML",        [r"<\?xml", r"</\w+>", r"<\w+\s+\w+=", r"xmlns"]),
    ("HTML",       [r"<!DOCTYPE html>", r"<html", r"<body", r"<div"]),
]


def detect_language(code: str, filename: str = "") -> str:
    """
    Detect programming language from file extension first, then content patterns.
    Returns language name string (e.g. "Python", "Java", "Unknown").
    """
    # 1. Extension-based detection (fast path)
    if filename:
        ext = Path(filename).suffix.lower()
        if ext in EXT_MAP:
            return EXT_MAP[ext]

    # 2. Content-based detection (scoring)
    scores = {}
    for lang, patterns in PATTERNS:
        score = sum(1 for p in patterns if re.search(p, code, re.IGNORECASE | re.MULTILINE))
        if score > 0:
            scores[lang] = score

    if scores:
        return max(scores, key=scores.get)

    return "Unknown"


def get_migration_target(language: str) -> str:
    """Return the recommended migration target for a given source language."""
    targets = {
        "Python":     "Python 3.12+",
        "Java":       "Java 21 (LTS)",
        "JavaScript": "ES2022 / ES2023",
        "TypeScript": "TypeScript 5.x",
        "PHP":        "PHP 8.3",
        "C":          "ANSI C / C11",
        "C++":        "C++20 / C++23",
        "SQL":        "ANSI SQL / PostgreSQL 16",
        "Shell":      "POSIX sh / Bash 5",
    }
    return targets.get(language, "Modern equivalent")
