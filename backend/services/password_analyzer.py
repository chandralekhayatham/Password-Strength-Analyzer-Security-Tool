import re
import string
from pathlib import Path
from .entropy_estimator import estimate_theoretical_entropy
from .pattern_detector import (
    detect_sequences, detect_keyboard_patterns, detect_repetition,
    detect_predictable_structure,
)

DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "common_passwords.txt"
COMMON_PASSWORDS = {
    line.strip().lower() for line in DATA_FILE.read_text(encoding="utf-8").splitlines()
    if line.strip() and not line.startswith("#")
}


def is_common_password(password: str) -> bool:
    s = password.lower()
    if s in COMMON_PASSWORDS:
        return True
    parts = re.split(r"[\W_]+", s)
    return any(len(p) >= 4 and p in COMMON_PASSWORDS for p in parts)


def analyze_length(password: str):
    n = len(password)
    if n < 8: band = "Very short"
    elif n <= 11: band = "Short"
    elif n <= 15: band = "Better length"
    else: band = "Strong length contribution"
    return {"length": n, "band": band}


def analyze_characters(password: str):
    categories = {
        "lowercase": any(c.islower() for c in password),
        "uppercase": any(c.isupper() for c in password),
        "digits": any(c.isdigit() for c in password),
        "symbols": any(c in string.punctuation for c in password),
        "spaces": any(c.isspace() for c in password),
    }
    unique = len(set(password))
    return {
        **categories,
        "character_type_count": sum(categories.values()),
        "unique_character_count": unique,
        "unique_character_ratio": round(unique / len(password), 2) if password else 0,
    }


def _context_findings(password: str, context: dict | None):
    if not context:
        return []
    lowered = password.lower()
    findings = []
    for key in ("first_name", "birth_year", "college_company"):
        value = str(context.get(key, "")).strip().lower()
        if value and len(value) >= 3 and value in lowered:
            findings.append(key.replace("_", " "))
    return findings


def analyze_password(password: str, context: dict | None = None):
    password = password or ""
    findings = []
    suggestions = []
    length = analyze_length(password)
    chars = analyze_characters(password)

    if not password:
        return {
            "score": 0, "classification": "VERY WEAK", "findings": ["Password is empty"],
            "suggestions": ["Enter a password or use the generator."],
            "metrics": {**length, **chars, "entropy_bits": 0.0}
        }

    sequences = detect_sequences(password)
    keyboards = detect_keyboard_patterns(password)
    repetitions = detect_repetition(password)
    predictable = detect_predictable_structure(password)
    common = is_common_password(password)
    context_hits = _context_findings(password, context)

    if len(password) < 8:
        findings.append("Password is very short")
        suggestions.append("Use a longer password or passphrase; aim for at least 12–16 characters.")
    if chars["character_type_count"] < 3:
        findings.append("Limited character diversity")
        suggestions.append("Increase variety where appropriate, but do not rely on composition alone.")
    if common:
        findings.append("Common password or common word detected")
        suggestions.append("Avoid commonly used passwords and predictable words.")
    if sequences:
        findings.append("Sequential characters detected")
        suggestions.append("Avoid predictable ascending or descending sequences such as 1234 or abcd.")
    if keyboards:
        findings.append("Keyboard pattern detected")
        suggestions.append("Avoid predictable keyboard walks such as qwerty or asdf.")
    if repetitions:
        findings.extend(repetitions)
        suggestions.append("Avoid repeated characters or repeated substrings.")
    if predictable:
        findings.extend(predictable)
        suggestions.append("Avoid common word + number, year, or date patterns.")
    if context_hits:
        findings.append("Password appears to contain personal information")
        suggestions.append("Avoid names, birth years, college/company names, or other predictable personal context.")

    entropy = estimate_theoretical_entropy(password)
    score = 0
    # Project-defined 0–100 rubric from the uploaded specification.
    score += min(35, round((min(len(password), 20) / 20) * 35))
    score += min(15, chars["character_type_count"] * 3)
    score += min(10, round(chars["unique_character_ratio"] * 10))
    pattern_penalty = min(20, len(sequences) * 8 + len(keyboards) * 8 + len(repetitions) * 6 + len(predictable) * 5)
    score += max(0, 20 - pattern_penalty)
    score += 0 if common else 10
    score += min(10, max(0, round(entropy / 10)))
    score -= 25 if common else 0
    score -= 10 if sequences else 0
    score -= 10 if keyboards else 0
    score -= 10 if repetitions else 0
    score -= 10 if context_hits else 0

    # Strongly cap obvious predictable structures so length does not hide weakness.
    if common:
        score = min(score, 25)
    if repetitions:
        score = min(score, 40)
    if keyboards:
        score = min(score, 40)
    if sequences:
        score = min(score, 40)
    if predictable:
        score = min(score, 45)
    if context_hits:
        score = min(score, 45)
    score = max(0, min(100, score))

    if score <= 20: classification = "VERY WEAK"
    elif score <= 40: classification = "WEAK"
    elif score <= 60: classification = "MODERATE"
    elif score <= 80: classification = "STRONG"
    else: classification = "VERY STRONG"

    if not suggestions:
        suggestions.extend([
            "Keep the password unique to this account.",
            "Consider using a password manager to generate and store unique passwords.",
            "Enable MFA where available.",
        ])
    else:
        suggestions.append("Avoid reusing this password across different accounts.")
        suggestions.append("Use a password manager and enable MFA where available.")

    return {
        "score": score,
        "classification": classification,
        "findings": list(dict.fromkeys(findings)),
        "suggestions": list(dict.fromkeys(suggestions)),
        "metrics": {
            **length,
            **chars,
            "entropy_bits": entropy,
            "common_password": common,
            "sequence_count": len(sequences),
            "keyboard_pattern_count": len(keyboards),
            "repetition_count": len(repetitions),
            "predictable_pattern_count": len(predictable),
            "personal_context_overlap": bool(context_hits),
        },
    }
