import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))

from services.password_analyzer import analyze_password, is_common_password
from services.password_generator import generate_password
from services.policy_checker import check_policy


def test_empty_password():
    assert analyze_password("")["classification"] == "VERY WEAK"


def test_common_password():
    result = analyze_password("123456")
    assert result["metrics"]["common_password"] is True
    assert result["score"] <= 40


def test_sequence_detection():
    result = analyze_password("abcd1234")
    assert result["metrics"]["sequence_count"] > 0


def test_keyboard_detection():
    result = analyze_password("qwerty2026!")
    assert result["metrics"]["keyboard_pattern_count"] > 0


def test_repetition_detection():
    result = analyze_password("aaaaaaaaaaaaaaaa")
    assert result["metrics"]["repetition_count"] > 0


def test_personal_context():
    result = analyze_password("Rahul@2026", {"first_name": "Rahul"})
    assert result["metrics"]["personal_context_overlap"] is True


def test_generated_password_length():
    password = generate_password(20)
    assert len(password) == 20


def test_policy():
    assert check_policy("short", min_length=12)["passed"] is False


def test_common_helper():
    assert is_common_password("password") is True
