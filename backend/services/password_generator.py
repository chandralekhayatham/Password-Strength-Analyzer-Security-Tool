import secrets
import string


def generate_password(length=20, uppercase=True, lowercase=True, numbers=True, symbols=True):
    length = max(12, min(int(length), 64))
    groups = []
    if lowercase: groups.append(string.ascii_lowercase)
    if uppercase: groups.append(string.ascii_uppercase)
    if numbers: groups.append(string.digits)
    if symbols: groups.append("!@#$%^&*()-_=+[]{};:,.?")
    if not groups:
        groups = [string.ascii_letters]

    chars = [secrets.choice(group) for group in groups]
    alphabet = "".join(groups)
    chars.extend(secrets.choice(alphabet) for _ in range(length - len(chars)))
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)


def generate_passphrase(words=4):
    # Small educational word pool; generated examples are not recommended for reuse.
    word_list = ["river", "candle", "photon", "saffron", "galaxy", "orchid", "drift", "ember", "velvet", "harbor", "turtle", "prairie"]
    return "-".join(secrets.choice(word_list) for _ in range(max(4, min(words, 8))))
