import re

KEYBOARD_PATTERNS = (
    "qwerty", "asdf", "zxcv", "qaz", "wsx", "edc", "rfv", "tgb", "yhn", "ujm"
)


def detect_sequences(password: str):
    s = password.lower()
    found = []
    for i in range(len(s) - 3):
        chunk = s[i:i+4]
        if all(ord(chunk[j+1]) - ord(chunk[j]) == 1 for j in range(3)):
            found.append(f"ascending sequence: {chunk}")
        elif all(ord(chunk[j+1]) - ord(chunk[j]) == -1 for j in range(3)):
            found.append(f"descending sequence: {chunk}")
    return list(dict.fromkeys(found))


def detect_keyboard_patterns(password: str):
    s = password.lower()
    return [p for p in KEYBOARD_PATTERNS if p in s or p[::-1] in s]


def detect_repetition(password: str):
    findings = []
    repeated_chars = re.findall(r"(.)\1{2,}", password)
    if repeated_chars:
        findings.append("repeated characters")

    repeated_substrings = []
    for size in range(2, max(2, len(password) // 2 + 1)):
        for i in range(len(password) - 2 * size + 1):
            part = password[i:i+size]
            if part * 2 in password:
                repeated_substrings.append(part)
    if repeated_substrings:
        findings.append("repeated substring pattern")
    return list(dict.fromkeys(findings))


def detect_predictable_structure(password: str):
    s = password.lower()
    findings = []
    if re.search(r"[a-z]{3,}\d{2,}[!@#$%^&*()_+=\-]*$", s):
        findings.append("common word followed by predictable numbers/symbols")
    if re.search(r"(?:19|20)\d{2}", s):
        findings.append("year-like pattern")
    if re.search(r"(?:19|20)\d{2}[-/]?(?:0[1-9]|1[0-2])[-/]?(?:0[1-9]|[12]\d|3[01])", s):
        findings.append("date-like pattern")
    return list(dict.fromkeys(findings))
