"""
This module contains functions for checking the quality of microdata metadata.
"""


def is_valid_variable(var: dict) -> bool:
    """Check if a variable is valid.
    Args:
        var (dict): The variable.
    Returns:
        bool: True if the variable is valid.
    """
    label = (var.get("labl", var.get("label", "")) or "").strip()
    if not label:
        return False

    # Count the number of digits in the label.
    # If the ratio of digits to characters is greater than 0.5, then the variable is invalid.
    num_digits = sum(c.isdigit() for c in label)
    num_chars = len(label.replace(" ", ""))
    ratio = num_digits / num_chars

    if ratio > 0.5:
        return False

    # Remove variables that start with a parenthesis.
    # For example: (sum) cgrp05, (sum) health, (mean) internet
    if label.startswith("("):
        return False

    return True
