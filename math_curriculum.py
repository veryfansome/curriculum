"""
Generate a corpus of short maxims and expressions for pretraining.
Conceptually, this is like memorizing multiplication tables early in childhood education.
"""
import math
import random

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

def addition_examples(a, b, c) -> list[str]:
    stmts = [
        f"Add {a} to {b} to get {c}.",
        f"Adding {a} and {b} {random.choice(['gets', 'results in', 'yields'])} {c}.",
        f"The {random.choice(['sum', 'total'])} of {a} and {b} {random.choice(['is', 'equals'])} {c}.",
        f"{a} {random.choice(['added to', 'plus'])} {b} {random.choice(['is', 'equals'])} {c}.",
        f"{c} equals {a} plus {b}.",
        f"{c} is the sum of {a} and {b}.",
    ]
    if a > 0 and b > 0:
        stmts += [
            f"{random_euclidean_qualifier(capitalize=True)}, a rectangle with a width of {a} and a height of {b} has a perimeter {random.choice(['of', 'equal to'])} {2 * c}.",
        ]
    if b > 0:
        stmts += [
            f"Increase {a} by {b} to get {c}",
            f"Increasing {a} by {b} {random.choice(['gets', 'results in', 'yields'])} {c}",
            f"{c} is {b} more than {a}",
        ]
    a, b = parenthesize_if_negative(a, b)
    stmts += [
        f"{a} + {b} = {c}",
    ]
    return stmts


def division_examples(a, b, q, r, f) -> list[str]:
    stmts = []
    if q == 0 and r > 0:
        # Fraction
        ab_gcd = math.gcd(a, b)
        a_simplified = a // ab_gcd
        b_simplified = b // ab_gcd
        stmts += [
            f"The greatest common denominator of {a} and {b} is {ab_gcd}",
            f"{a} % {b} = {r}",
            f"{a} // {b} = 0",
            f"{a} ÷ {b} = {a}{random_division_sign(exclude={'÷'})}{b}",
        ]
        if ab_gcd != 1:  # Can be reduced
            stmts += [
                f"The ratio of {a} to {b} is {random.choice([f, f'{a_simplified}:{b_simplified}'])}",
                f"{a} / {b} = {a_simplified}/{b_simplified}".replace("/", random_division_sign(exclude={'÷'})),
                f"{a}/{b} = {a_simplified}/{b_simplified}".replace("/", random_division_sign(exclude={'÷'})),
                f"{a}/{b} {random.choice(['reduces', 'simplifies'])} to {a_simplified}/{b_simplified}.".replace("/", random_division_sign(exclude={'÷'})),
                f"{to_superscript(a)}⁄{to_subscript(b)} = {to_superscript(a_simplified)}⁄{to_subscript(b_simplified)}",
                f"{to_superscript(a)}⁄{to_subscript(b)} {random.choice(['reduces', 'simplifies'])} to {to_superscript(a_simplified)}⁄{to_subscript(b_simplified)}.",
            ]
        else:
            stmts += [
                f"{a} / {b} = {a}/{b}".replace("/", random_division_sign(exclude={'÷'})),
                f"{a} ⁄ {b} = {to_superscript(a)}⁄{to_subscript(b)}",
            ]

        if is_denominator_of_terminating_decimal(b_simplified):
            stmts += [
                f"{a} divided by {b} {random.choice(['is', 'equals'])} {f}.",
                f"{a} {random_division_sign()} {b} = {f}",
            ]
        else:
            stmts += [
                f"{a} divided by {b} {random.choice(['is', 'equals'])} approximately {f}.",
                f"{a} {random_division_sign()} {b} ≈ {f}",
            ]

    elif r == 0:
        # Perfect division
        match q:
            case 2:
                stmts += [
                    f"{a} is {random.choice(['double', 'twice', 'twice as much as'])} {b}.",
                    f"{b} is {random.choice(['half', 'half as much as', 'half of'])} {a}.",
                ]
            case 3:
                stmts.append(f"{a} is triple {b}.")
            case 4:
                stmts.append(f"{a} is quadruple {b}.")
        q_word = num2words(q)
        q_ordinal = num2words(q, to='ordinal')
        stmts += [
            f"The ratio of {a} to {b} is {q}",
            f"the quotient of {a} and {b} {random.choice(['is', 'equals'])} {q}.",
            f"{a} divided by {b} {random.choice(['is', 'equals'])} {q}.",
            f"{a} {random.choice(['is divisible by', 'is a multiple of'])} {b}.",
            f"{a} {random.choice(['is divisible by', 'is a multiple of'])} {q}.",
            f"{a} {random_division_sign()} {b} = {q}",
            f"{b} {random.choice(['divides', 'is a divisor of', 'is a factor of'])} {a}.",
            f"{q} {random.choice(['divides', 'is a divisor of', 'is a factor of'])} {a}.",
        ]
        if a != 0:
            stmts += [
                f"{a} is {q_word} {random.choice(['times', 'times as much as'])} {b}.",
                f"{b} goes into {a}, {q} times.",
            ]
            if q > 2:
                stmts.append(f"{b} is one-{q_ordinal} of {a}.")
    else:
        # Euclidean division
        ab_gcd = math.gcd(a, b)
        a_simplified = a // ab_gcd
        b_simplified = b // ab_gcd
        stmts += [
            f"The greatest common denominator of {a} and {b} is {ab_gcd}",
            f"The ratio of {a} to {b} is {random.choice([f, f'{a_simplified}:{b_simplified}'])}",
            f"{a} % {b} = {r}",
            f"{a} // {b} = {q}",
            f"{a} divided by {b} {random.choice(['is', 'equals'])} {q} with a remainder of {r}.",
            f"{b} goes into {a}, {q} times with a remainder of {r}.",
            f"{b} is not a factor of {a}.",
        ]
        if is_denominator_of_terminating_decimal(b_simplified):
            stmts += [
                f"{a} divided by {b} {random.choice(['is', 'equals'])} {f}.",
                f"{a} {random_division_sign()} {b} = {f}",
            ]
        else:
            stmts += [
                f"{a} divided by {b} is approximately {f}.",
                f"{a} {random_division_sign()} {b} ≈ {f}",
            ]
    return stmts


def examples_from_natural_number_pair(pair: tuple[int, int]) -> list[str]:
    stmts = []
    a, b = pair

    ab_sum = a + b
    ab_product = a * b

    # Addition
    stmts += addition_examples(a, b, ab_sum)
    stmts += addition_examples(-a, b, (-a) + b)
    stmts += addition_examples(a, -b, a + (-b))
    stmts += addition_examples(-a, -b, (-a) + (-b))

    # Subtraction
    stmts += subtraction_examples(a, b, a - b)
    stmts += subtraction_examples(-a, b, (-a) - b)
    stmts += subtraction_examples(a, -b, a - (-b))
    stmts += subtraction_examples(-a, -b, (-a) - (-b))

    # Multiplication
    stmts += multiplication_examples(a, b, ab_product)
    stmts += multiplication_examples(-a, b, (-a) * b)
    stmts += multiplication_examples(a, -b, a * (-b))
    stmts += multiplication_examples(-a, -b, (-a) * (-b))

    if a != b:
        stmts += subtraction_examples(b, a, b - a)

        # Commutativity
        stmts += addition_examples(b, a, ab_sum)
        stmts += multiplication_examples(b, a, ab_product)

    # Division
    if b != 0:
        ab_quotient, ab_remainder = divmod(a, b)
        stmts += division_examples(a, b, ab_quotient, ab_remainder, a / b)
    if a != 0:
        ba_quotient, ba_remainder = divmod(b, a)
        stmts += division_examples(b, a, ba_quotient, ba_remainder, b / a)

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
            f"{random_euclidean_qualifier(capitalize=True)}, a circle with a radius of {n} has a circumference {random.choice(['approximately', 'roughly'])} equal to {2 * n * math.pi}.",
            f"{random_euclidean_qualifier(capitalize=True)}, a circle with a radius of {n} has a circumference {random.choice(['of', 'equal to'])} {2 * n} {random_multiplication_sign()} π.",
            f"{random_euclidean_qualifier(capitalize=True)}, a circle with a radius of {n} has a diameter {random.choice(['of', 'equal to'])} {2 * n}.",
            f"{random_euclidean_qualifier(capitalize=True)}, a circle with a radius of {n} has an area {random.choice(['of', 'equal to'])} {random_exponent_expr(n, 2)} {random_multiplication_sign()} π.",
            f"{random_euclidean_qualifier(capitalize=True)}, a square with an area {random.choice(['of', 'equal to'])} {random_exponent_expr(n, 2)} has an edge length of {n}.",
            f"{random_euclidean_qualifier(capitalize=True)}, a square with an edge length of {n} has an area {random.choice(['of', 'equal to'])} {random_exponent_expr(n, 2)}.",
            f"{n} {random_multiplication_sign()} {1 / n} = 1",
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
                        f"{random_euclidean_qualifier(capitalize=True)}, a circle with a radius of {n} has an area roughly equal to {n_to_power * math.pi}.",
                        f"{random_euclidean_qualifier(capitalize=True)}, a circle with a radius of {n} has an area {random.choice(['of', 'equal to'])} {n_to_power}π.",
                        f"{random_euclidean_qualifier(capitalize=True)}, a square with a side length of {n} has an area {random.choice(['of', 'equal to'])} {n_to_power}.",
                        f"{random_euclidean_qualifier(capitalize=True)}, a square with an area {random.choice(['of', 'equal to'])} {n_to_power} has a side length of {n}.",
                    ]
                stmts += [
                    f"The principal square root of {n_to_power} {random.choice(['is', 'equals'])} {n}.",
                    f"{n} is the principal square root of {n_to_power}.",
                    f"{n} raised to the 2nd power {random.choice(['is', 'equals'])} {n_to_power}.",
                    f"{n} squared is {n_to_power}.",
                ]
            case 3:
                if not is_zero:
                    stmts += [
                        f"{random_euclidean_qualifier(d=3, capitalize=True)}, a cube with an edge length of {n} has a volume {random.choice(['of', 'equal to'])} {n_to_power}.",
                        f"{random_euclidean_qualifier(d=3, capitalize=True)}, a cube with an edge length of {n} has {random.choice(['6', 'six'])} faces, each with an area {random.choice(['of', 'equal to'])} {n ** 2}.",
                    ]
                stmts += [
                    f"The cube root of {n_to_power} {random.choice(['is', 'equals'])} {n}.",
                    f"{n} cubed {random.choice(['is', 'equals'])} {n_to_power}.",
                    f"{n} is the cube root of {n_to_power}.",
                    f"{n} raised to the 3rd power {random.choice(['is', 'equals'])} {n_to_power}.",
                ]
        if power > 1:
            power_ordinal = num2words(power, to='ordinal')
            stmts += [
                f"The {power_ordinal} root of {n_to_power} {random.choice(['is', 'equals'])} {n}.",
                f"{n} is the {power_ordinal} root of {n_to_power}.",
                f"{n} raised to the {power_ordinal} power {random.choice(['is', 'equals'])} {n_to_power}.",
                f"{n} to the power of {power} {random.choice(['is', 'equals'])} {n_to_power}.",
            ]
            if power > 3:
                stmts.append(f"{n} raised to the {power}th power {random.choice(['is', 'equals'])} {n_to_power}.")
        stmts += [
            f"{random_exponent_expr(n, power)} = {n_to_power}",
            f"{random_exponent_expr(n, power)} {random.choice(['is', 'equals'])} {n_to_power}.",
        ]
    return stmts


def generate_corpus() -> set[str]:
    docs = set()
    for i in range(10):
        docs.update(examples_from_natural_number(i))
    for pair in generate_unique_number_pairs(121, 0, 10):
        docs.update(examples_from_natural_number_pair(pair))
    # General facts and maxims
    docs.update([
        "A positive number has a value greater than zero.",
        "A negative number has a value less than zero.",

        "An even number is divisible by two.",
        "An odd number is not divisible by two.",
        "Adding two even number always results in an even number.",
        "Adding two odd number always results in an even number.",
        "The sum of two even numbers is always an even number.",
        "The sum of two odd numbers is always an even number.",
        "Multiplying by an even number always results in an even number.",
        "Multiplying two odd number always results in an odd number.",
        "The product of two odd numbers is always an odd number.",

        "With whole numbers, multiplication is adding the same number together multiple times.",
        "With multiplication, the numbers being multiplied are called factors or the multiplicand and multiplier and the resulting number is called the product.",
        "Multiplying by a number greater than 1 is thought of as scaling up.",
        "Multiplying by 1 leaves numbers unchanged.",
        "Multiplying by a positive number less than 1 is thought of as scaling down.",
        "Multiplying by 0 reduces numbers to 0.",
        "Multiplying by a negative number causes non-zero numbers to change their sign or polarity.",

        "Exponentiation is repeated multiplication.",
        "To square a number is to multiply it by itself.",
        "To square a number is to raise it to the second power.",
        "To cube a number is to multiply it by itself twice.",
        "To cube a number is to multiply it by its square.",
        "To cube a number is to raise it to the third power.",

        # TODO: division
        "A number is prime if its only positive divisors are 1 and itself.",
        "A fractional number is used to represent parts of a whole.",
    ])
    return docs


def generate_unique_number_pairs(num_pairs, lower_bound, upper_bound) -> set[tuple[int, int]]:
    assert lower_bound < upper_bound, "Lower bound can't be greater than upper bound"
    # Calculate the total possible unique pairs
    range_size = upper_bound - lower_bound + 1
    max_possible_pairs = range_size * range_size
    assert num_pairs <= max_possible_pairs, (
        f"Cannot generate {num_pairs} unique pairs. "
        f"Only {max_possible_pairs} possible pairs exist in the range {lower_bound} to {upper_bound}."
    )
    unique_pairs = set()
    while len(unique_pairs) < num_pairs:
        x = random.randint(lower_bound, upper_bound)
        y = random.randint(lower_bound, upper_bound)
        # Adding to a set automatically handles the uniqueness check
        unique_pairs.add((x, y))
    return unique_pairs


def is_denominator_of_terminating_decimal(simplified_denominator):
    """Check prime factors of the simplified denominator"""
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


def multiplication_examples(a, b, c) -> list[str]:
    ab_lcm = math.lcm(a, b)
    stmts = [
        f"Multiply {a} {random.choice(['and', 'by'])} {b} to get {c}.",
        f"Multiplying {a} and {b} {random.choice(['gets', 'results in', 'yields'])} {c}.",
        f"The product of {a} and {b} {random.choice(['is', 'equals'])} {c}.",
        f"{a} repeated {b} times {random.choice(['is', 'equals'])} {c}.",
        f"{a} {random.choice(['groups of', 'times'])} {b} {random.choice(['is', 'equals'])} {c}.",
        f"{c} {random.choice(['is', 'equals'])} {a} {random.choice(['multiplied by', 'times'])} {b}.",
    ]
    if a > 0 and b > 0:
        stmts += [
            f"Scale {a} by a factor of {b} to get {c}.",
            f"The least common multiple of {a} and {b} {random.choice(['is', 'equals'])} {ab_lcm}.",
            f"{random_euclidean_qualifier(capitalize=True)}, a rectangle with a width of {a} and a height of {b} has an area {random.choice(['of', 'equal to'])} {c}.",
            f"{random_euclidean_qualifier(capitalize=True)}, a triangle with a base of {a} and a height of {b} has an area {random.choice(['of', 'equal to'])} {c / 2 if c % 2 != 0 else c // 2}.",
        ]
    a, b = parenthesize_if_negative(a, b)
    stmts.append(f"{a} {random_multiplication_sign()} {b} = {c}")
    return stmts


def parenthesize_if_negative(a: int, b: int) -> tuple[str, str]:
    return f"({a})" if a < 0 else str(a), f"({b})" if b < 0 else str(b)


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


def subtraction_examples(a, b, c) -> list[str]:
    stmts = [
        f"Subtract {b} from {a} to get {c}.",
        f"Subtracting {b} from {a} {random.choice(['gets', 'results in', 'yields'])} {c}.",
        f"{a} minus {b} {random.choice(['is', 'equals'])} {c}.",
    ]
    if a > b:
        stmts.append(f"The difference between {a} and {b} {random.choice(['is', 'equals'])} {c}.")
    if b > 0:
        stmts += [
            f"Decrease {a} by {b} to get {c}.",
            f"Decreasing {a} by {b} {random.choice(['gets', 'results in', 'yields'])} {c}.",
            f"Take {b} away from {a} to get {c}.",
            f"Taking {b} away from {a} {random.choice(['gets', 'results in', 'yields'])} {c}.",
            f"{c} equals {a} minus {b}.",
            f"{c} is {b} less than {a}.",
        ]
    a, b = parenthesize_if_negative(a, b)
    stmts.append(f"{a} - {b} = {c}")
    return stmts


def to_subscript(val):
    return "".join(SUBSCRIPT_MAP.get(char, char) for char in str(val))


def to_superscript(val):
    return "".join(SUPERSCRIPT_MAP.get(char, char) for char in str(val))


if __name__ == "__main__":
    corpus = generate_corpus()
    print(corpus)
    print(f"corpus length: {len(corpus)}")
