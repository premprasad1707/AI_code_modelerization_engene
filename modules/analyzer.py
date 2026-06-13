import ast
import re
import pandas as pd

PYTHON2_PATTERNS = [
    {
        'name': 'Python 2 print statement',
        'pattern': r'(?m)^\s*print\s+[^\(\n].*',
        'severity': 'Medium',
        'suggestion': 'Convert print statement to print() function.'
    },
    {
        'name': 'xrange usage',
        'pattern': r'\bxrange\s*\(',
        'severity': 'Low',
        'suggestion': 'Replace xrange() with range().'
    },
    {
        'name': 'raw_input usage',
        'pattern': r'\braw_input\s*\(',
        'severity': 'Low',
        'suggestion': 'Replace raw_input() with input().'
    },
    {
        'name': 'Old exception syntax',
        'pattern': r'except\s+([A-Za-z_][\w.]*)\s*,\s*([A-Za-z_][\w]*)\s*:',
        'severity': 'High',
        'suggestion': 'Convert except Exception, e to except Exception as e.'
    },
    {
        'name': 'iteritems usage',
        'pattern': r'\.iteritems\s*\(',
        'severity': 'Medium',
        'suggestion': 'Replace .iteritems() with .items().'
    },
    {
        'name': 'itervalues usage',
        'pattern': r'\.itervalues\s*\(',
        'severity': 'Medium',
        'suggestion': 'Replace .itervalues() with .values().'
    },
]


def analyze_code(code: str):
    findings = []
    lines = code.splitlines()
    for rule in PYTHON2_PATTERNS:
        for match in re.finditer(rule['pattern'], code):
            line_number = code[:match.start()].count('\n') + 1
            findings.append({
                'Issue': rule['name'],
                'Line': line_number,
                'Severity': rule['severity'],
                'Matched Code': lines[line_number - 1].strip() if line_number <= len(lines) else '',
                'Suggestion': rule['suggestion']
            })
    return pd.DataFrame(findings)


def extract_basic_metrics(code: str):
    lines = code.splitlines()
    non_empty_lines = [line for line in lines if line.strip()]
    functions = len(re.findall(r'(?m)^\s*def\s+[A-Za-z_][\w]*\s*\(', code))
    classes = len(re.findall(r'(?m)^\s*class\s+[A-Za-z_][\w]*', code))
    imports = len(re.findall(r'(?m)^\s*(import|from)\s+', code))
    comments = len([line for line in lines if line.strip().startswith('#')])
    return {
        'total_lines': len(lines),
        'non_empty_lines': len(non_empty_lines),
        'functions': functions,
        'classes': classes,
        'imports': imports,
        'comments': comments
    }


def detect_code_smells(code: str):
    """Lightweight heuristic checks for code quality smells."""
    lines = code.splitlines()
    findings = []

    long_lines = [ln for ln in enumerate(lines, start=1) if len(ln[1]) > 100]
    if long_lines:
        findings.append({'Issue': 'Long lines detected', 'Severity': 'Low', 'Suggestion': 'Break long lines into smaller statements for readability and easier migration.'})

    if re.search(r'\b(eval|exec)\s*\(', code):
        findings.append({'Issue': 'Dynamic code execution', 'Severity': 'High', 'Suggestion': 'Replace eval/exec with explicit dispatch logic or safer parsing.'})

    if re.search(r'\b(os\.system|subprocess\.(Popen|call|run|check_output))\s*\(', code):
        findings.append({'Issue': 'Shell command execution', 'Severity': 'Medium', 'Suggestion': 'Use safer subprocess patterns and validate user-controlled inputs.'})

    return pd.DataFrame(findings)


def detect_unused_functions(code: str):
    """Approximate unused functions by comparing definitions against call sites."""
    defs = re.findall(r'(?m)^\s*def\s+([A-Za-z_][\w]*)\s*\(', code)
    calls = set(re.findall(r'\b([A-Za-z_][\w]*)\s*\(', code))
    unused = [name for name in defs if name not in calls and name not in {'main', '__init__'}]
    return unused


def detect_python_syntax_errors(code: str):
    """Return syntax error details if Python parsing fails."""
    try:
        ast.parse(code)
        return None
    except SyntaxError as exc:
        return {'line': exc.lineno, 'message': str(exc)}


def detect_runtime_risks(code: str):
    """Basic runtime-risk heuristics for beginner-friendly modernization guidance."""
    risks = []
    if re.search(r'\bpickle\.(loads|load)\s*\(', code):
        risks.append('Unsafe deserialization via pickle is risky in modern code.')
    if re.search(r'\brequests\.[A-Za-z_]+\s*\(', code) and 'timeout=' not in code:
        risks.append('HTTP calls should explicitly set timeouts to avoid hanging requests.')
    if re.search(r'\bpassword\s*=\s*[\'\"][^\'\"]+[\'\"]', code):
        risks.append('Hard-coded credentials were detected; move secrets to environment variables.')
    if re.search(r'\b(execute|commit|rollback)\s*\(', code) and not re.search(r'\b(transaction|with)\b', code):
        risks.append('Database operations detected without explicit transaction management or context managers.')
    return risks


def generate_suggestions(findings_df):
    suggestions = []
    if findings_df is not None and not findings_df.empty:
        suggestions.extend(findings_df['Suggestion'].drop_duplicates().tolist())
    suggestions.append('Modernize dependencies and add tests before deployment.')
    return '\n'.join(f'- {item}' for item in suggestions)


def generate_migration_roadmap(code: str):
    """Create a simple modernization roadmap for the current code."""
    unused = detect_unused_functions(code)
    roadmap = [
        '1. Replace deprecated Python 2 constructs with modern Python 3 syntax.',
        '2. Remove or refactor dynamic execution patterns such as eval/exec where possible.',
        '3. Update outdated libraries and dependency imports to maintained alternatives.',
        '4. Review runtime risks such as pickle usage, missing timeouts, and hard-coded secrets.',
    ]
    if unused:
        roadmap.append('5. Remove or verify unused helper functions: ' + ', '.join(unused))
    else:
        roadmap.append('5. Keep the current function set, but validate each helper with tests before deployment.')
    return '\n'.join(roadmap)
