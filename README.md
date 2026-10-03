# Password Strength Analyzer & Security Suggestion Tool

A beginner-friendly defensive cybersecurity project that evaluates password strength using length, character diversity, common-password checks, sequence detection, keyboard-pattern detection, repetition analysis, optional personal-context overlap, and an educational entropy-style estimate.

## Privacy design

- Passwords are analyzed transiently in application memory.
- Passwords are never inserted into SQLite.
- Passwords are not written to localStorage or sessionStorage.
- Passwords are not included in API responses.
- The dashboard stores only safe aggregate metadata.
- Demonstrations should use synthetic passwords, never real account passwords.

## Features

- Real-time strength meter
- 0–100 project-defined score
- VERY WEAK / WEAK / MODERATE / STRONG / VERY STRONG classifications
- Length analysis
- Character diversity and unique-character ratio
- Common-password detection
- Sequential-number/letter detection
- Keyboard-pattern detection
- Repeated-character and repeated-substring detection
- Predictable word + number/year detection
- Optional personal-context warning
- Entropy-style educational estimate
- Specific security recommendations
- Secure password generator using Python `secrets`
- Privacy-safe SQLite analytics dashboard
- Policy checker module
- Automated tests

## Architecture

User → Web UI → `/api/analyze` → In-memory analyzer → scoring engine → findings/suggestions → UI

Optional safe metadata → SQLite → dashboard

The password itself does not enter analytics storage.

## Technology stack

- Python
- Flask
- HTML/CSS/JavaScript
- SQLite
- pytest

## Run locally

### Windows PowerShell

```powershell
cd Password-Strength-Analyzer
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python backend/app.py
```

Open `http://127.0.0.1:5000`.

### Windows CMD

```bat
cd Password-Strength-Analyzer
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python backend\app.py
```

## Tests

```bash
pytest -q
```

## Demo cases

Use only synthetic values:

- `123456` → expected very weak
- `Password123!` → predictable despite character diversity
- `aaaaaaaaaaaaaaaa` → long but repetitive
- `qwerty2026!` → keyboard pattern + year-like pattern
- Generate a fresh 20-character value in the application → demonstrate secure generation

Do not reuse demonstration passwords for real accounts.

## Scoring note

The 0–100 score and classification bands are project-defined educational heuristics, not universal security standards. The project deliberately does not treat uppercase + lowercase + digit + symbol as sufficient evidence of strength.

The entropy-style calculation assumes random character selection, so it can be optimistic for human-created passwords. Pattern and common-password checks are therefore combined with it.

## Database

`analytics.db` is generated locally and ignored by Git. Its schema intentionally has no password column.

### ANALYSES

- analysis_id
- score
- classification
- password_length
- unique_character_ratio
- weakness_count
- created_at

### FINDINGS

- finding_id
- analysis_id
- finding_type
- severity
- description

## Security testing checklist

Verify that:

1. Passwords are not stored in SQLite.
2. Passwords are not logged by application code.
3. Passwords are not returned by `/api/analyze`.
4. Passwords are not placed in URL parameters.
5. The UI uses an HTML password field by default.
6. Browser storage is not used for passwords.
7. Dashboard data contains only metadata.
8. Production deployment uses HTTPS and appropriate rate limiting.

## GitHub

Suggested repository name: `Password-Strength-Analyzer-Security-Tool`

Suggested topics: `cybersecurity`, `password-security`, `application-security`, `python`, `flask`, `secure-coding`, `iam`, `defensive-security`

Example commits:

- `Initialize password strength analyzer`
- `Implement password pattern detection`
- `Build real-time password strength meter`
- `Add secure password generator`
- `Add privacy-safe analytics dashboard`
- `Add automated security tests`
- `Complete README and documentation`

## Limitations and future improvements

- Replace the small educational common-password list with an appropriately licensed dataset.
- Add a privacy-preserving breached-password check using a k-anonymity design when a suitable production requirement exists.
- Consider a mature password-strength estimation library.
- Add configurable organizational policy settings.
- Add MFA, password-manager, SSO and passkey/WebAuthn educational material.
- Add accessibility and localization improvements.

## Disclaimer

This is a defensive educational project. It does not crack passwords, attempt credentials against accounts, or collect real user passwords.
