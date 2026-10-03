import math
import string


def estimate_theoretical_entropy(password: str) -> float:
    """Educational entropy-style estimate; assumes random character selection."""
    if not password:
        return 0.0
    pool = 0
    if any(c.islower() for c in password): pool += 26
    if any(c.isupper() for c in password): pool += 26
    if any(c.isdigit() for c in password): pool += 10
    if any(c in string.punctuation for c in password): pool += len(string.punctuation)
    if any(c.isspace() for c in password): pool += 1
    pool = max(pool, 1)
    return round(len(password) * math.log2(pool), 1)
