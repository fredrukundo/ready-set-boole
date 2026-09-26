"""
Ready, Set, Boole! - Exercise 01: Multiplier

Return a * b using ONLY these operators:
    &  |  ^  <<  >>  =  ==  !=  <  >  <=  >=

Required complexity: O(1) time, O(1) space.
Full explanation: see README.md in this folder.

Usage:
    python3 multiplier.py              # short demo
    python3 multiplier.py 5 3          # multiply any two numbers
    python3 multiplier.py -t 13 11     # show the algorithm step by step
"""

import sys

# Python integers are unbounded, unlike Rust's u32. This mask keeps only the
# lowest 32 bits, reproducing real u32 wraparound. `&` is an allowed operator.
MASK_32 = 0xFFFFFFFF


def adder(a: int, b: int) -> int:
    """Return a + b using bitwise operators only. (Exercise 00.)

    A local copy is kept here on purpose, so this folder runs standalone
    without importing across directories. See README section 6.1.
    """
    a = a & MASK_32
    b = b & MASK_32

    while b != 0:
        carry = (a & b) << 1
        a = (a ^ b) & MASK_32
        b = carry & MASK_32

    return a


def multiplier(a: int, b: int) -> int:
    """Return a * b, computed with bitwise operators only.

    This is "shift and add", the binary version of the long multiplication
    you learned at school.

    Because b is written in base 2, it is a sum of powers of two:
        11 = 1011 = 8 + 2 + 1
    So a * b is the sum of a shifted by each of those powers:
        a * 11 = (a << 3) + (a << 1) + (a << 0)

    We walk the bits of b from right to left. Whenever a bit is 1, the
    matching shifted copy of a is added into the result.
    """
    a = a & MASK_32
    b = b & MASK_32
    result = 0

    while b != 0:
        # Is the lowest bit of b a 1? If so, this power of two is part of b,
        # so the matching shifted copy of a belongs in the result.
        if (b & 1) != 0:
            result = adder(result, a)

        a = (a << 1) & MASK_32      # next power of two: double a
        b = b >> 1                  # move to the next bit of b

    return result


def trace(a: int, b: int) -> int:
    """Same algorithm as multiplier(), but prints every iteration.

    Used for the defense ("show me how it works") and for checking work
    done on paper. Not part of the required function.
    """
    original_a = a & MASK_32
    original_b = b & MASK_32
    a = original_a
    b = original_b
    result = 0

    print(f"  multiplier({original_a}, {original_b})\n")
    print(f"  {'step':>4} | {'b in binary':>14} | {'bit':>3} | "
          f"{'a (shifted)':>13} | {'action':>22} | {'result':>12}")
    print("  " + "-" * 86)

    step = 0
    while b != 0:
        bit = b & 1
        if bit != 0:
            action = f"add {a}"
            result = adder(result, a)
        else:
            action = "bit is 0, skip"
        print(f"  {step:>4} | {b:>14b} | {bit:>3} | {a:>13} | "
              f"{action:>22} | {result:>12}")

        a = (a << 1) & MASK_32
        b = b >> 1
        step = step + 1             # loop counter only, allowed by the subject

    print(f"\n  b reached 0  ->  result = {result}")
    return result


def demo() -> None:
    """A handful of examples, shown when no arguments are given."""
    print("Exercise 01 - Multiplier   (pass two numbers as arguments to test your own)\n")
    print(f"  {'a':>12} {'b':>12} {'multiplier(a, b)':>18}")
    print("  " + "-" * 44)
    for a, b in [(0, 0), (0, 7), (1, 42), (3, 5), (13, 11),
                 (12, 12), (255, 255), (65536, 65536)]:
        print(f"  {a:>12} {b:>12} {multiplier(a, b):>18}")
    print("\n  Note: 65536 * 65536 gives 0 - the true result is 2^32, which")
    print("  does not fit in 32 bits, so it wraps around exactly like a real u32.")
    print("  Run  python3 multiplier.py -t 13 11   to see the algorithm step by step.")


def main() -> None:
    args = sys.argv[1:]

    show_trace = False
    if args and (args[0] == "-t" or args[0] == "--trace"):
        show_trace = True
        args = args[1:]

    if not args:
        demo()
        return

    if len(args) != 2:
        print("usage: python3 multiplier.py [-t] <a> <b>", file=sys.stderr)
        sys.exit(1)

    try:
        a = int(args[0])
        b = int(args[1])
    except ValueError:
        print("error: both arguments must be whole numbers", file=sys.stderr)
        sys.exit(1)

    if a < 0 or b < 0:
        print("error: this function takes natural numbers (>= 0)", file=sys.stderr)
        sys.exit(1)

    if a > MASK_32 or b > MASK_32:
        print(f"error: arguments must fit in 32 bits (max {MASK_32})", file=sys.stderr)
        sys.exit(1)

    if show_trace:
        trace(a, b)
    else:
        print(multiplier(a, b))


if __name__ == "__main__":
    main()