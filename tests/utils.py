"""
Utility functions for tests.
"""

def includes_any(expected_sets: list[set[str]], generated: set[str]):
    for expected in expected_sets:
        assert any(stmt in expected for stmt in generated), f"Expected any of: {expected}, got: {generated}"


def includes_all(expected: set[str], generated: set[str]):
    assert expected.issubset(generated), f"Expected: {expected - generated}, got {generated}"
