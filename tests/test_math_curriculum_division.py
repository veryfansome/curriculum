import pytest
from curriculum import math_curriculum

def test_a_b_division_examples_int_division_with_negative_divisor():
    stmts = set(math_curriculum.a_b_division_examples(10, -5))
    for expected in [
        {"10 ÷ (-5) = -10/5",
         "10 ÷ (-5) = -10⁄5"},
        {"10 ÷ (-5) = -2/1",
         "10 ÷ (-5) = -2⁄1"},
        {"10/-5 = -2/1",
         "10⁄-5 = -2⁄1"},
    ]:
        assert any(s in expected for s in stmts), str(expected)
    assert {
        "0 < 5",
        "0 is less than 5.",
        "5 > 0",
        "5 is greater than 0.",
        "The greatest common divisor of -5 and 10 is 5.",
        "The greatest common divisor of 0 and 5 is 5.",
        "The greatest common divisor of 10 and -5 is 5.",
        "The greatest common divisor of 5 and 0 is 5.",
        "The ratio of 10 to -5 is -2:1.",
    }.issubset(stmts)

    stmts = set(math_curriculum.a_b_division_examples(-10, -5))
    for expected in [
        {"(-10) ÷ (-5) = 10/5",
         "(-10) ÷ (-5) = 10⁄5"},
        {"(-10) ÷ (-5) = 2/1",
         "(-10) ÷ (-5) = 2⁄1"},
        {"-10/-5 = 2/1",
         "-10⁄-5 = 2⁄1"},
    ]:
        assert any(s in expected for s in stmts), str(expected)
    assert {
        "0 < 5",
        "0 is less than 5.",
        "5 > 0",
        "5 is greater than 0.",
        "The greatest common divisor of -10 and -5 is 5.",
        "The greatest common divisor of -5 and -10 is 5.",
        "The greatest common divisor of 0 and 5 is 5.",
        "The greatest common divisor of 5 and 0 is 5.",
        "The ratio of -10 to -5 is 2:1.",
    }.issubset(stmts)

def test_a_b_division_examples_int_division_with_positive_divisor():
    stmts = set(math_curriculum.a_b_division_examples(10, 5))
    for expected in [
        {"10 ÷ 5 = 10/5",
         "10 ÷ 5 = 10⁄5"},
        {"10 ÷ 5 = 2/1",
         "10 ÷ 5 = 2⁄1"},
        {"10/5 = 2/1",
         "10⁄5 = 2⁄1"},
    ]:
        assert any(s in expected for s in stmts), str(expected)
    assert {
        "0 < 5",
        "0 is less than 5.",
        "5 > 0",
        "5 is greater than 0.",
        "The greatest common divisor of 10 and 5 is 5.",
        "The greatest common divisor of 5 and 10 is 5.",
        "The greatest common divisor of 0 and 5 is 5.",
        "The greatest common divisor of 5 and 0 is 5.",
        "The ratio of 10 to 5 is 2:1.",
    }.issubset(stmts)

def test_a_b_division_examples_raises_on_zero_divisor():
    with pytest.raises(AssertionError):
        math_curriculum.a_b_division_examples(5, 0)

def test_normalize_fraction():
    """Standard positive fractions."""
    assert math_curriculum.normalize_fraction(4, 8) == (1, 2, 4)
    assert math_curriculum.normalize_fraction(5, 10) == (1, 2, 5)
    assert math_curriculum.normalize_fraction(10, 100) == (1, 10, 10)

def test_normalize_fraction_already_simplified():
    """Already simplified fractions."""
    assert math_curriculum.normalize_fraction(1, 2) == (1, 2, 1)
    assert math_curriculum.normalize_fraction(3, 4) == (3, 4, 1)
    assert math_curriculum.normalize_fraction(1, 1) == (1, 1, 1)

def test_normalize_fraction_negative_denominators():
    """Negative denominators should be standardized to positive denominators."""
    assert math_curriculum.normalize_fraction(4, -8) == (-1, 2, 4)
    assert math_curriculum.normalize_fraction(5, -10) == (-1, 2, 5)
    assert math_curriculum.normalize_fraction(-3, -9) == (1, 3, 3) # Both negative -> p

def test_normalize_fraction_negative_numerators():
    """Negative numerators."""
    assert math_curriculum.normalize_fraction(-4, 8) == (-1, 2, 4)
    assert math_curriculum.normalize_fraction(-5, 10) == (-1, 2, 5)

def test_normalize_fraction_prime_numbers():
    """Prime numbers."""
    assert math_curriculum.normalize_fraction(17, 31) == (17, 31, 1)
    assert math_curriculum.normalize_fraction(2, 3) == (2, 3, 1)

def test_normalize_fraction_zero_numerators():
    """Zero numerators."""
    assert math_curriculum.normalize_fraction(0, 5) == (0, 1, 5)
    assert math_curriculum.normalize_fraction(0, -10) == (0, 1, 10) # Denom becomes positive
