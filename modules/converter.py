import re


def convert_print_statements(code: str) -> str:
    converted_lines = []
    for line in code.splitlines():
        stripped = line.lstrip()
        indent = line[:len(line) - len(stripped)]
        # Handle 'print ' and 'print"' or "print'" edge cases
        if (stripped.startswith('print ') or stripped.startswith('print"') or stripped.startswith("print'")) \
           and not stripped.startswith('print('):
            # Find where the content starts (after 'print')
            content = stripped[5:].strip()
            converted_lines.append(f'{indent}print({content})')
        else:
            converted_lines.append(line)
    return '\n'.join(converted_lines)


def convert_python2_to_python3(code: str) -> str:
    migrated = code
    migrated = convert_print_statements(migrated)
    migrated = re.sub(r'\bimport\s+urllib2\b', 'import urllib.request as urllib2', migrated)
    migrated = re.sub(r'\bfrom\s+urllib2\s+import\b', 'from urllib.request import', migrated)
    migrated = re.sub(r'\bimport\s+httplib\b', 'import http.client', migrated)
    migrated = re.sub(r'\bimport\s+cookielib\b', 'import http.cookiejar', migrated)
    migrated = re.sub(r'\bimport\s+cPickle\b', 'import pickle', migrated)
    migrated = re.sub(r'\bxrange\s*\(', 'range(', migrated)
    migrated = re.sub(r'\braw_input\s*\(', 'input(', migrated)
    migrated = re.sub(r'\.iteritems\s*\(', '.items(', migrated)
    migrated = re.sub(r'\.itervalues\s*\(', '.values(', migrated)
    migrated = re.sub(r'\.iterkeys\s*\(', '.keys(', migrated)
    migrated = re.sub(r'except\s+([A-Za-z_][\w.]*)\s*,\s*([A-Za-z_][\w]*)\s*:', r'except \1 as \2:', migrated)
    return migrated


def create_diff_summary(original: str, migrated: str):
    original_lines = original.splitlines()
    migrated_lines = migrated.splitlines()
    changed = 0
    for old, new in zip(original_lines, migrated_lines):
        if old != new:
            changed += 1
    changed += abs(len(original_lines) - len(migrated_lines))
    return {
        'original_lines': len(original_lines),
        'migrated_lines': len(migrated_lines),
        'changed_lines': changed
    }
