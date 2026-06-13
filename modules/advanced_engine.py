from typing import Any, Dict

import pandas as pd

from modules.analyzer import (
    analyze_code,
    detect_code_smells,
    detect_python_syntax_errors,
    detect_runtime_risks,
    detect_unused_functions,
    extract_basic_metrics,
    generate_migration_roadmap,
    generate_suggestions,
)
from modules.converter import convert_python2_to_python3, create_diff_summary
from modules.dependency_analyzer import analyze_dependencies
from modules.language_detector import detect_language, get_migration_target
from modules.risk_model import predict_risk
from modules.security_scanner import scan_security, summarize_security


def run_migration_workflow(code: str, *, filename: str | None = None) -> Dict[str, Any]:
    """Reusable orchestrator for the migration workflow.

    For now, it delegates to the existing regex-based Python2 analyzer/converter.
    This creates a stable interface so the platform can grow (multi-language,
    LLM agents, dependency analysis, etc.) without rewriting the UI.
    """

    # 1) Analysis (deprecated syntax)
    findings_df: pd.DataFrame = analyze_code(code)
    metrics: Dict[str, Any] = extract_basic_metrics(code)

    # 2) Migration (basic rule conversions)
    migrated_code: str = convert_python2_to_python3(code)
    diff_summary: Dict[str, Any] = create_diff_summary(code, migrated_code)

    # 3) Suggestions (from analyzer + dependency hints)
    code_smells_df = detect_code_smells(code)
    unused_functions = detect_unused_functions(code)
    syntax_error = detect_python_syntax_errors(code)
    runtime_risks = detect_runtime_risks(code)
    suggestions_text: str = generate_suggestions(findings_df)
    roadmap_text = generate_migration_roadmap(code)
    dependency_findings = analyze_dependencies(code, filename or "")
    if dependency_findings:
        dependency_hints = "\n".join(
            f"- {item['library']}: {item['replacement']} ({item['status']})" for item in dependency_findings[:8]
        )
        suggestions_text = "\n\n".join([suggestions_text, "Dependency recommendations:", dependency_hints])
    issue_count: int = len(findings_df) if findings_df is not None else 0

    # 4) Language + target modernization path
    language = detect_language(code, filename or "")
    migration_target = get_migration_target(language)

    # 5) Risk (existing ML/rule model)
    risk_level: str
    risk_score: float
    probabilities: list
    risk_level, risk_score, probabilities = predict_risk(metrics, issue_count)

    # 5) Security scan (basic static heuristics)
    security_findings_df: pd.DataFrame = scan_security(code)
    security_summary: str = summarize_security(security_findings_df)

    return {
        "filename": filename,
        "findings_df": findings_df,
        "metrics": metrics,
        "migrated_code": migrated_code,
        "diff_summary": diff_summary,
        "issue_count": issue_count,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "probabilities": probabilities,
        "suggestions_text": suggestions_text,
        "roadmap_text": roadmap_text,
        "code_smells_df": code_smells_df,
        "unused_functions": unused_functions,
        "syntax_error": syntax_error,
        "runtime_risks": runtime_risks,
        "security_findings_df": security_findings_df,
        "security_summary": security_summary,
        "language": language,
        "migration_target": migration_target,
        "dependency_findings": dependency_findings,
    }


def build_dashboard_metrics(result: Dict[str, Any]) -> pd.DataFrame:
    metrics = result.get("metrics", {})
    issue_count = result.get("issue_count", 0)
    return pd.DataFrame(
        {
            "Metric": ["Lines", "Functions", "Classes", "Imports", "Issues", "Security Issues"],
            "Count": [
                metrics.get("total_lines", 0),
                metrics.get("functions", 0),
                metrics.get("classes", 0),
                metrics.get("imports", 0),
                issue_count,
                int(len(result.get("security_findings_df", pd.DataFrame())))
                if result.get("security_findings_df") is not None
                else 0,
            ],
        }
    )

