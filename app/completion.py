import re
import ast
from typing import Any, Dict, List


# --------------------
# Atomic validators
# --------------------

def contains_text(output: str, value: str) -> bool:
    return value.lower() in output.lower()


def matches_regex(output: str, pattern: str) -> bool:
    return re.search(pattern, output) is not None


def is_valid_python(output: str) -> bool:
    """
    Ensures output is syntactically valid Python.
    Very strong signal for code-generation steps.
    """
    try:
        ast.parse(output)
        return True
    except SyntaxError:
        return False


def has_required_sections(output: str, sections: List[str]) -> bool:
    """
    Ensures structured explanations.
    Example sections: ["install", "run", "example"]
    """
    text = output.lower()
    return all(section.lower() in text for section in sections)


def length_between(output: str, bounds: Dict[str, int]) -> bool:
    min_len = bounds.get("min", 0)
    max_len = bounds.get("max", float("inf"))
    return min_len <= len(output) <= max_len


# --------------------
# Composite validator
# --------------------

def validate_all(output: str, rules: List[Dict[str, Any]]) -> bool:
    """
    All rules must pass.
    """
    for rule in rules:
        rule_type = rule["type"]
        value = rule.get("value")

        if not check_completion(output, rule_type, value):
            return False

    return True


# --------------------
# Main entry point
# --------------------

def check_completion(
    output: str,
    criteria_type: str,
    criteria_value: Any = None
) -> bool:
    """
    Production-grade deterministic completion checker.
    """

    if not output or not isinstance(output, str):
        return False

    # ---- Simple rules ----
    if criteria_type == "contains":
        return contains_text(output, criteria_value)

    if criteria_type == "regex":
        return matches_regex(output, criteria_value)

    # ---- Strong rules ----
    if criteria_type == "valid_python":
        return is_valid_python(output)

    if criteria_type == "sections":
        return has_required_sections(output, criteria_value)

    if criteria_type == "length":
        return length_between(output, criteria_value)

    # ---- Composite rule ----
    if criteria_type == "all":
        return validate_all(output, criteria_value)

    # ---- Unknown criteria ----
    raise ValueError(f"Unknown criteria_type: {criteria_type}")
