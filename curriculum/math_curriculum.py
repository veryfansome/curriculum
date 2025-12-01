"""
Generate a corpus of statements and expressions for pretraining.
Conceptually, this is like memorizing multiplication tables early in childhood education.
"""
import itertools
import math
import random
from locale import normalize

from num2words import num2words

SUBSCRIPT_MAP = {
    "0": "₀", "1": "₁", "2": "₂", "3": "₃", "4": "₄",
    "5": "₅", "6": "₆", "7": "₇", "8": "₈", "9": "₉",
    "-": "₋"
}
SUPERSCRIPT_MAP = {
    "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
    "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹",
    "-": "⁻"
}


def a_b_comparison_examples(_a, _b, a: str = None, b: str = None) -> list[str]:
    """Generate examples that must be true, given that a > b."""
    if _a == _b:
        return []
    a_is_greater = _a > _b
    if a is None:
        a = _a
    if b is None:
        b = _b
    return [
        f"{a} {'>' if a_is_greater else '<'} {b}",
        f"{a} {'is greater than' if a_is_greater else 'is less than'} {b}.",
        f"{b} {'<' if a_is_greater else '>'} {a}",
        f"{b} {'is less than' if a_is_greater else 'is greater than'} {a}.",
    ]


def a_b_division_examples(a, b) -> list[str]:
    """Generate examples that must be true, given that a / b = q + r/b, which has a float value of f."""
    assert b != 0, "Can't divide by zero"
    b_abs = abs(b)                      # Euclidean divisor (always positive)
    q_b_abs, r = divmod(a, b_abs)       # ensures 0 <= r < b_abs
    q = q_b_abs if b > 0 else -q_b_abs  # ensures a = (b * q) + r
    f = a / b                           # sign-correct numeric value

    # Simplify with positive denominator
    a_simplified, b_simplified, ab_gcd = normalize_fraction(a, b)
    r_simplified, b_abs_simplified, rb_gcd = normalize_fraction(r if b > 0 else -r, b_abs)

    # Always true
    stmts = [
        f"{a} = {parenthesize_if_negative(b)} {random_multiplication_sign()} {parenthesize_if_negative(q)} + {r}",
    ]
    stmts += a_b_comparison_examples(0, r)
    stmts += a_b_comparison_examples(0, b_abs)
    stmts += a_b_comparison_examples(r, b_abs)

    return stmts

#def a_b_division_examples(a, b) -> list[str]:
#    """Generate examples that must be true, given that a / b = q + r/b, which has a float value of f."""
#    assert b != 0, "Can't divide by zero"
#    #b_abs = abs(b)
#    #q, r = divmod(a, b_abs)
#    q, r = divmod(a, b)
#    f = a / b
#
#    stmts = []
#    if q == 0 and r > 0:
#        # Fraction
#        a_simplified, b_simplified, ab_gcd = simplify_fraction(a, b)
#        perc = f * 100
#        stmts += [
#            *commutative_statements(f"The greatest common divisor of %s and %s is {ab_gcd}.", a, b),
#            f"{a} % {b} = {r}",
#            f"{a} // {b} = 0",
#            f"{a} ÷ {b} = {a}{random_division_sign(exclude={'÷'})}{b}",
#        ]
#        if ab_gcd != 1:  # Can be reduced
#            stmts += [
#                f"The ratio of {a} to {b} is {a_simplified}:{b_simplified}.",
#                f"{a} / {b} = {a_simplified}/{b_simplified}".replace("/", random_division_sign(exclude={'÷'})),
#                f"{a}/{b} = {a_simplified}/{b_simplified}".replace("/", random_division_sign(exclude={'÷'})),
#                f"{a}/{b} {random.choice(['reduces', 'simplifies'])} to {a_simplified}/{b_simplified}.".replace("/", random_division_sign(exclude={'÷'})),
#                f"{to_superscript(a)}⁄{to_subscript(b)} = {to_superscript(a_simplified)}⁄{to_subscript(b_simplified)}",
#                f"{to_superscript(a)}⁄{to_subscript(b)} {random.choice(['reduces', 'simplifies'])} to {to_superscript(a_simplified)}⁄{to_subscript(b_simplified)}.",
#            ]
#        else:
#            stmts += [
#                f"{a} / {b} = {a}/{b}".replace("/", random_division_sign(exclude={'÷'})),
#                f"{a} ⁄ {b} = {to_superscript(a)}⁄{to_subscript(b)}",
#            ]
#
#        if is_denominator_of_terminating_decimal(b_simplified):
#            stmts += [
#                *a_b_comparison_examples(1, f, b=f"{a}/{b}"),
#                *a_b_comparison_examples(1, f, b=f"{to_superscript(a)}⁄{to_subscript(b)}"),
#                f"The ratio of {a} to {b} is {f}.",
#                f"{a_simplified}/{b_simplified} = {perc}%",
#                f"{a} divided by {b} {random.choice(['equals', 'is'])} {f}.",
#                f"{a} {random_division_sign()} {b} = {f}",
#                f"{a}/{b} = {perc}%",
#                f"{to_superscript(a)}⁄{to_subscript(b)} = {perc}%",
#                f"{to_superscript(a_simplified)}⁄{to_subscript(b_simplified)} = {perc}%",
#                f"{to_superscript(r)}⁄{to_subscript(b)} = {f}",
#            ]
#        else:
#            stmts += [
#                f"The ratio of {a} to {b} is {random.choice(['approximately', 'roughly'])} {f}.",
#                f"{a_simplified}/{b_simplified} ≈ {perc}%",
#                f"{a} divided by {b} {random.choice(['equals', 'is'])} {random.choice(['approximately', 'roughly'])} {f}.",
#                f"{a} {random_division_sign()} {b} ≈ {f}",
#                f"{a}/{b} ≈ {perc}%",
#                f"{to_superscript(a)}⁄{to_subscript(b)} ≈ {perc}%",
#                f"{to_superscript(a_simplified)}⁄{to_subscript(b_simplified)} ≈ {perc}%",
#                f"{to_superscript(r)}⁄{to_subscript(b)} ≈ {f}",
#            ]
#
#    elif r == 0:
#        # Perfect division
#        match q:
#            case 2:
#                stmts += [
#                    f"{a} is {random.choice(['double', 'twice', 'twice as much as'])} {b}.",
#                    f"{b} is {random.choice(['half', 'half as much as', 'half of'])} {a}.",
#                ]
#            case 3:
#                stmts.append(f"{a} is triple {b}.")
#            case 4:
#                stmts.append(f"{a} is quadruple {b}.")
#        q_word = num2words(q)
#        stmts += [
#            f"The quotient of {a} and {b} {random.choice(['equals', 'is'])} {q}.",
#            f"The ratio of {a} to {b} is {q}.",
#            f"{a} divided by {b} {random.choice(['equals', 'is'])} {q}.",
#            f"{a} {random.choice(['is divisible by', 'is a multiple of'])} {b}.",
#            f"{parenthesize_if_negative(a)} % {parenthesize_if_negative(b)} = 0",
#            f"{parenthesize_if_negative(a)} {random_division_sign()} {parenthesize_if_negative(b)} = {q}",
#        ]
#        if a != 0:
#            stmts += [
#                f"{a} is {q_word} {random.choice(['times', 'times as much as'])} {b}.",
#                f"{b} goes into {a}, {q} times.",
#                f"{b} {random.choice(['divides', 'is a divisor of', 'is a factor of'])} {a}.",
#                f"{q} {random.choice(['divides', 'is a divisor of', 'is a factor of'])} {a}.",
#            ]
#            if q > 2:
#                stmts.append(f"{b} is one-{num2words(q, to='ordinal')} of {a}.")
#        if q != 0:
#            stmts += [
#                f"{a} {random.choice(['is divisible by', 'is a multiple of'])} {q}.",
#            ]
#    else:
#        # Euclidean division
#        a_simplified, b_simplified, ab_gcd = simplify_fraction(a, b)
#        r_simplified, rb_simplified, rb_gcd = simplify_fraction(r, b)
#        stmts += [
#            *a_b_comparison_examples(b, r),
#            *a_b_comparison_examples(f, 1, a=f"{a}/{b}"),
#            *a_b_comparison_examples(f, 1, a=f"{to_superscript(a)}⁄{to_subscript(b)}"),
#            *a_b_comparison_examples(q, 0),
#            *commutative_statements(f"The greatest common divisor of %s and %s is {ab_gcd}.", a, b),
#            *commutative_statements(f"The greatest common divisor of %s and %s is {rb_gcd}.", r, b),
#            f"The ratio of {a} to {b} is {a_simplified}:{b_simplified}.",
#            f"{a} % {b} = {r}",
#            f"{a} // {b} = {q}",
#            f"{a} = {q} {random_multiplication_sign()} {b} + {r}",
#            f"{a} divided by {b} {random.choice(['equals', 'is'])} {q} with a remainder of {r}.",
#            f"{a} divided by {b} {random.choice(['equals', 'is'])} {q}{to_superscript(r_simplified)}⁄{to_subscript(rb_simplified)}.",
#            f"{a} ⁄ {b} = {q}{to_superscript(r_simplified)}⁄{to_subscript(rb_simplified)}",
#            f"{b} goes into {a}, {q} times with a remainder of {r}.",
#            f"{b} is not a factor of {a}.",
#        ]
#        if is_denominator_of_terminating_decimal(rb_simplified):
#            stmts += [
#                f"The ratio of {a} to {b} is {f}.",
#                f"{a} divided by {b} {random.choice(['equals', 'is'])} {f}.",
#                f"{a} {random_division_sign()} {b} = {f}",
#                f"{q}{to_superscript(r_simplified)}⁄{to_subscript(rb_simplified)} = {f}",
#            ]
#        else:
#            stmts += [
#                f"The ratio of {a} to {b} is {random.choice(['approximately', 'roughly'])} {f}.",
#                f"{a} divided by {b} is {random.choice(['approximately', 'roughly'])} {f}.",
#                f"{a} {random_division_sign()} {b} ≈ {f}",
#                f"{q}{to_superscript(r_simplified)}⁄{to_subscript(rb_simplified)} ≈ {f}",
#            ]
#    return stmts


def a_b_multiplication_examples(a, b) -> list[str]:
    """Generate examples that must be true, given that a * b = c."""
    c = a * b

    stmts = []
    stmts += commutative_statements(f"%s times %s {random.choice(['equals', 'is'])} {c}.", a, b)
    stmts += commutative_statements(f"Multiply %s {random.choice(['and', 'by'])} %s to get {c}.", a, b)
    stmts += commutative_statements(f"Multiplying %s and %s {random.choice(['gets', 'results in', 'yields'])} {c}.", a, b)
    stmts += commutative_statements(f"The product of %s and %s {random.choice(['equals', 'is'])} {c}.", a, b)
    stmts += commutative_statements(f"{c} {random.choice(['equals', 'is'])} %s {random.choice(['multiplied by', 'times'])} %s.", a, b)
    if a > 0:
        stmts += [
            f"Divide {c} by {a} to get {b}.",
            f"Dividing {c} by {a} {random.choice(['gets', 'results in', 'yields'])} {b}.",
            f"The quotient of {c} and {a} {random.choice(['equals', 'is'])} {b}.",
            f"{b} repeated {a} times {random.choice(['equals', 'is'])} {c}.",
            f"{c} divided by {a} {random.choice(['equals', 'is'])} {b}.",
            f"{parenthesize_if_negative(c)} {random_division_sign()} {parenthesize_if_negative(a)} = {b}",
        ]
    if b > 0:
        stmts += [
            f"Divide {c} by {b} to get {a}.",
            f"Dividing {c} by {b} {random.choice(['gets', 'results in', 'yields'])} {a}.",
            f"The quotient of {c} and {b} {random.choice(['equals', 'is'])} {a}.",
            f"{a} repeated {b} times {random.choice(['equals', 'is'])} {c}.",
            f"{c} divided by {b} {random.choice(['equals', 'is'])} {a}.",
            f"{parenthesize_if_negative(c)} {random_division_sign()} {parenthesize_if_negative(b)} = {a}",
        ]
    if a > 0 and b > 0:
        stmts += commutative_statements(f"%s and %s are factors of {c}.", a, b)
        stmts += commutative_statements(f"%s groups of %s {random.choice(['equals', 'is'])} {c}.", a, b)
        stmts += commutative_statements(f"Scale %s by a factor of %s to get {c}.", a, b)
        stmts += commutative_statements(f"Scaling %s by a factor of %s {random.choice(['gets', 'results in', 'yields'])} {c}.", a, b)
        stmts += commutative_statements(f"The least common multiple of %s and %s {random.choice(['equals', 'is'])} {math.lcm(a, b)}.", a, b)
        stmts += commutative_statements(f"{c} is %s scaled by %s.", a, b)
        stmts += commutative_statements(f"{c} is a multiple of %s and of %s.", a, b)
        stmts += [
            f"{random_euclidean_qualifier(capitalize=True)}, a rectangle with a width of {a} and a height of {b} has an area {random.choice(['of', 'equal to'])} {c}.",
            f"{random_euclidean_qualifier(capitalize=True)}, a triangle with a base of {a} and a height of {b} has an area {random.choice(['of', 'equal to'])} {c / 2 if c % 2 != 0 else c // 2}.",
        ]
    stmts += commutative_statements(f"%s {random_multiplication_sign()} %s = {c}", parenthesize_if_negative(a), parenthesize_if_negative(b))
    return stmts


def a_b_subtraction_examples(a, b) -> list[str]:
    """Generate examples that must be true, given that a - b = c."""
    c = a - b

    stmts = [
        f"Subtract {b} from {a} to get {c}.",
        f"Subtracting {b} from {a} {random.choice(['gets', 'results in', 'yields'])} {c}.",
        f"The absolute difference between {a} and {b} {random.choice(['equals', 'is'])} {abs(c)}.",
        f"{a} minus {b} {random.choice(['equals', 'is'])} {c}.",
    ]
    if a > b:
        stmts.append(f"{a} exceeds {b} by {c}.")
    if b > 0:
        stmts += [
            f"Decrease {a} by {b} to get {c}.",
            f"Decreasing {a} by {b} {random.choice(['gets', 'results in', 'yields'])} {c}.",
            f"Take {b} away from {a} to get {c}.",
            f"Taking {b} away from {a} {random.choice(['gets', 'results in', 'yields'])} {c}.",
            f"{c} equals {a} minus {b}.",
            f"{c} is {b} less than {a}.",
        ]
    stmts += commutative_statements(f"%s + %s = {a}", parenthesize_if_negative(b), parenthesize_if_negative(c))
    stmts.append(f"{parenthesize_if_negative(a)} - {parenthesize_if_negative(b)} = {c}")
    return stmts


def a_b_sum_examples(a, b) -> list[str]:
    """Generate examples, given that a + b = c."""
    c = a + b

    stmts = []
    stmts += commutative_statements(f"%s {random.choice(['added to', 'plus'])} %s {random.choice(['equals', 'is', 'makes'])} {c}.", a, b)
    stmts += commutative_statements(f"Add %s to %s to get {c}.", a, b)
    stmts += commutative_statements(f"Adding %s and %s {random.choice(['gets', 'makes', 'results in', 'yields'])} {c}.", a, b)
    stmts += commutative_statements(f"Subtract %s from {c} to get %s.", a, b)
    stmts += commutative_statements(f"Subtracting %s from {c} {random.choice(['gets', 'makes', 'results in', 'yields'])} %s.", a, b)
    stmts += commutative_statements(f"The result of {random.choice(['adding', 'summing'])} %s and %s is {c}.", a, b)
    stmts += commutative_statements(f"The {random.choice(['sum', 'total'])} of %s and %s {random.choice(['equals', 'is'])} {c}.", a, b)
    stmts += commutative_statements(f"{c} is {random.choice(['obtained by', 'the result of'])} adding %s and %s.", a, b)
    stmts += commutative_statements(f"{c} {random.choice(['equals', 'is'])} the sum of %s and %s.", a, b)
    if a > 0:
        stmts += [
            f"Increase {b} by {a} to get {c}.",
            f"Increasing {b} by {a} {random.choice(['gets', 'results in', 'yields'])} {c}.",
            f"{c} is {a} more than {b}.",
            f"{c} {random.choice(['equals', 'is'])} {b} {random.choice(['increased by', 'plus'])} {a}.",
        ]
    if b > 0:
        stmts += [
            f"Increase {a} by {b} to get {c}.",
            f"Increasing {a} by {b} {random.choice(['gets', 'results in', 'yields'])} {c}.",
            f"{c} is {b} more than {a}.",
            f"{c} {random.choice(['equals', 'is'])} {a} {random.choice(['increased by', 'plus'])} {b}.",
        ]
    if a > 0 and b > 0:
        stmts += [
            *commutative_statements(f"{random_euclidean_qualifier(capitalize=True)}, a rectangle with a width of %s and a height of %s has a perimeter {random.choice(['of', 'equal to'])} {2 * c}.", a, b),
            *a_b_comparison_examples(c, a),
            *a_b_comparison_examples(c, b),
        ]
    stmts += commutative_statements(f"%s + %s = {c}", parenthesize_if_negative(a), parenthesize_if_negative(b))
    stmts += [
        f"{parenthesize_if_negative(c)} - {parenthesize_if_negative(a)} = {b}",
        f"{parenthesize_if_negative(c)} - {parenthesize_if_negative(b)} = {a}",
    ]
    return stmts


def commutative_statements(stmt: str, a, b) -> list[str]:
    return [stmt % (a, b), stmt % (b, a)]


def examples_from_natural_int_pair(a: int, b: int) -> list[str]:
    a_neg = -a
    b_neg = -b

    stmts = []
    stmts += examples_from_natural_number(a)
    stmts += examples_from_natural_number(b)

    for e1, e2 in itertools.product((a, a_neg), (b, b_neg)):
        stmts += a_b_comparison_examples(e1, e2)
        stmts += a_b_multiplication_examples(e1, e2)
        stmts += a_b_subtraction_examples(e1, e2)
        stmts += a_b_sum_examples(e1, e2)
        if e2 != 0:
            stmts += a_b_division_examples(e1, e2)
    if a != b:
        for e1, e2 in itertools.product((b, b_neg), (a, a_neg)):
            stmts += a_b_subtraction_examples(e1, e2)
            if e2 != 0:
                stmts += a_b_division_examples(e1, e2)

    # TODO: Euclidean geometry and more advanced math
    #   - Triangles: area, hypotenuse, etc.
    return stmts


def examples_from_natural_number(n: int) -> list[str]:
    word = num2words(n)
    stmts = [
        f"{n} = {n}",
        f"{n} equals {n}.",
        f"{n} is numerically equivalent to {word}.",
        f"{word.capitalize()} is numerically equivalent to {n}.",
    ]
    is_zero = n == 0
    if not is_zero:
        stmts += [
            *a_b_comparison_examples(0, -n),
            *a_b_comparison_examples(n, -n),
            *a_b_comparison_examples(n, 0),
            f"{n} {random_multiplication_sign()} 1/{n} = 1",
            f"{n} {random_multiplication_sign()} {1 / n} ≈ 1",
            f"{n} {random_multiplication_sign()} {to_superscript(1)}⁄{to_subscript(n)} = 1",
            f"{random_euclidean_qualifier(capitalize=True)}, a circle with a radius of {n} has a circumference {random.choice(['approximately', 'roughly'])} equal to {2 * n * math.pi}.",
            f"{random_euclidean_qualifier(capitalize=True)}, a circle with a radius of {n} has a circumference {random.choice(['of', 'equal to'])} {2 * n} {random_multiplication_sign()} π.",
            f"{random_euclidean_qualifier(capitalize=True)}, a circle with a radius of {n} has a diameter {random.choice(['of', 'equal to'])} {2 * n}.",
            f"{random_euclidean_qualifier(capitalize=True)}, a circle with a radius of {n} has an area {random.choice(['of', 'equal to'])} {random_exponent_expr(n, 2)} {random_multiplication_sign()} π.",
            f"{random_euclidean_qualifier(capitalize=True)}, a square with an area {random.choice(['of', 'equal to'])} {random_exponent_expr(n, 2)} has an edge length of {n}.",
            f"{random_euclidean_qualifier(capitalize=True)}, a square with an edge length of {n} has an area {random.choice(['of', 'equal to'])} {random_exponent_expr(n, 2)}.",
            f"|{-n}| = {n}",
            f"|{n}| = {n}",
        ]
        if is_prime(n):
            stmts.append(f"1 and {n} are the only divisors of {n}.")
            stmts.append(f"{n} is a prime number.")
    for power in range(1 if is_zero else 0, 21):
        n_to_power = 0 if is_zero else n ** power
        match power:
            case 2:
                if not is_zero:
                    stmts += [
                        f"{random_euclidean_qualifier(capitalize=True)}, a circle with a radius of {n} has an area {random.choice(['approximately', 'roughly'])} equal to {n_to_power * math.pi}.",
                        f"{random_euclidean_qualifier(capitalize=True)}, a circle with a radius of {n} has an area {random.choice(['of', 'equal to'])} {n_to_power}π.",
                        f"{random_euclidean_qualifier(capitalize=True)}, a square with a side length of {n} has an area {random.choice(['of', 'equal to'])} {n_to_power}.",
                        f"{random_euclidean_qualifier(capitalize=True)}, a square with an area {random.choice(['of', 'equal to'])} {n_to_power} has a side length of {n}.",
                        f"{random_euclidean_qualifier(d=3, capitalize=True)}, a sphere with a radius of {n} has a surface area {random.choice(['approximately', 'roughly'])} equal to {4  * n_to_power * math.pi}.",
                        f"{random_euclidean_qualifier(d=3, capitalize=True)}, a sphere with a radius of {n} has a surface area {random.choice(['of', 'equal to'])} {4 * n_to_power}π.",
                    ]
                stmts += [
                    f"The principal square root of {n_to_power} {random.choice(['equals', 'is'])} {n}.",
                    f"{n} is the principal square root of {n_to_power}.",
                    f"{n} raised to the 2nd power {random.choice(['equals', 'is'])} {n_to_power}.",
                    f"{n} squared is {n_to_power}.",
                ]
            case 3:
                if not is_zero:
                    stmts += [
                        f"{random_euclidean_qualifier(d=3, capitalize=True)}, a cube with an edge length of {n} has a volume {random.choice(['of', 'equal to'])} {n_to_power}.",
                        f"{random_euclidean_qualifier(d=3, capitalize=True)}, a cube with an edge length of {n} has {random.choice(['6', 'six'])} faces, each with an area {random.choice(['of', 'equal to'])} {n ** 2}.",
                        f"{random_euclidean_qualifier(d=3, capitalize=True)}, a sphere with a radius of {n} has a volume {random.choice(['approximately', 'roughly'])} equal to {(4/3) * n_to_power * math.pi}.",
                        f"{random_euclidean_qualifier(d=3, capitalize=True)}, a sphere with a radius of {n} has a volume {random.choice(['of', 'equal to'])} {(4/3) * n_to_power}π.",
                    ]
                stmts += [
                    f"The cube root of {n_to_power} {random.choice(['equals', 'is'])} {n}.",
                    f"{n} cubed {random.choice(['equals', 'is'])} {n_to_power}.",
                    f"{n} is the cube root of {n_to_power}.",
                    f"{n} raised to the 3rd power {random.choice(['equals', 'is'])} {n_to_power}.",
                ]
        if power > 1:
            power_ordinal = num2words(power, to='ordinal')
            stmts += [
                f"The {power_ordinal} root of {n_to_power} {random.choice(['equals', 'is'])} {n}.",
                f"{n} is the {power_ordinal} root of {n_to_power}.",
                f"{n} raised to the {power_ordinal} power {random.choice(['equals', 'is'])} {n_to_power}.",
                f"{n} to the power of {power} {random.choice(['equals', 'is'])} {n_to_power}.",
            ]
            if power > 3:
                stmts.append(f"{n} raised to the {power}th power {random.choice(['equals', 'is'])} {n_to_power}.")
        stmts += [
            f"{random_exponent_expr(n, power)} = {n_to_power}",
            f"{random_exponent_expr(n, power)} {random.choice(['equals', 'is'])} {n_to_power}.",
        ]
    return stmts


def generate_corpus() -> set[str]:
    docs = set()
    for pair in gen_uniq_int_grps(2, 121, 0, 10):
        a, b = pair
        docs.update(examples_from_natural_int_pair(a, b))
    return docs


def gen_uniq_int_grps(grp_size: int, num_to_gen: int, lb: int, ub: int) -> set[tuple[int, ...]]:
    assert lb < ub, "Lower bound can't be greater than upper bound"
    assert grp_size > 1, "Group size should be greater than 1"
    # Calculate the total possible unique pairs
    range_size = ub - lb + 1
    max_grps_possible = range_size ** grp_size
    assert num_to_gen <= max_grps_possible, (
        f"Cannot generate {num_to_gen} unique groups. "
        f"Only {max_grps_possible} possible groups of size {grp_size} exist in the range {lb} to {ub}."
    )
    uniq_grps = set()
    while len(uniq_grps) < num_to_gen:
        uniq_grps.add(tuple(random.randint(lb, ub) for _ in range(grp_size)))
    return uniq_grps


def is_denominator_of_terminating_decimal(simplified_denominator):
    """Check prime factors of the simplified denominator"""
    assert simplified_denominator != 0, "Can't divide by zero"
    simplified_denominator = abs(simplified_denominator)
    # Repeatedly divide out factors of 2 and 5
    while simplified_denominator % 2 == 0:
        simplified_denominator //= 2
    while simplified_denominator % 5 == 0:
        simplified_denominator //= 5
    # If the remaining denominator is 1, only 2 and 5 were factors.
    return simplified_denominator == 1


def is_prime(number: int):
    """Check if a given integer is a prime number using trial division."""
    # 2, 3, and 5 are the first primes
    if number in {2, 3, 5}:
        return True
    elif number < 5:
        return False

    # Check if the number is divisible by 2 or 3. # This optimization allows us to step by 6 later.
    if number % 2 == 0 or number % 3 == 0:
        return False

    # Check for divisors from 5 up to the square root of the number. We only need to check up to the square root
    # of the number because if n has a divisor greater than its square root, it must also have a divisor less than
    # its square root.
    i = 5
    while i * i <= number:
        # Check divisibility by i and i + 2 (e.g., 5 and 7, 11 and 13, etc.). This skips multiples of 2 and 3,
        # making it more efficient.
        if number % i == 0 or number % (i + 2) == 0:
            return False
        i += 6

    # If no divisors were found, the number is prime.
    return True


def parenthesize_if_negative(n: int) -> str:
    return f"({n})" if n < 0 else str(n)


def random_division_sign(exclude: set[str] = None):
    default = ["/", "⁄", "÷"]
    return random.choice(default if exclude is None else [s for s in default if s not in exclude])


def random_euclidean_qualifier(d: int = 2, capitalize: bool = False) -> str:
    choice = random.choice(["in Euclidean space", f"in {d}-dimensional Euclidean space"])
    if capitalize:
        choice = choice[0].upper() + choice[1:]
    return choice


def random_exponent_expr(n, power):
    return f"{n}{random.choice([f'^{power}', f'**{power}', to_superscript(power)])}"


def random_multiplication_sign(exclude: set[str] = None):
    default = ["*", "×", "x", "·"]
    return random.choice(default if exclude is None else [s for s in default if s not in exclude])


def normalize_fraction(n: int, d: int) -> tuple[int, int, int]:
    gcd = math.gcd(n, d)
    n_simplified, d_simplified = n // gcd, d // gcd
    if d_simplified < 0:
        n_simplified, d_simplified = -n_simplified, -d_simplified
    return n_simplified, d_simplified, gcd


def to_subscript(val):
    return "".join(SUBSCRIPT_MAP.get(char, char) for char in str(val))


def to_superscript(val):
    return "".join(SUPERSCRIPT_MAP.get(char, char) for char in str(val))


if __name__ == "__main__":
    #corpus = generate_corpus()
    #print(corpus)
    #print(f"corpus length: {len(corpus)}")
    print(a_b_division_examples(10, -5))
