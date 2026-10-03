def check_policy(password: str, min_length=12, reject_common=True, personal_overlap=False, common=False):
    checks = {
        "minimum_length": len(password) >= min_length,
        "common_password": not common if reject_common else True,
        "personal_information": not personal_overlap,
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "message": "POLICY PASS" if all(checks.values()) else "POLICY FAIL",
        "note": "Policy compliance and strength score are separate concepts."
    }
