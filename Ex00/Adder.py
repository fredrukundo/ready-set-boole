"""
Ready, Set, Boole! - Exercise 00: Adder

Return a + b using ONLY these operators:
    &  |  ^  <<  >>  =  ==  !=  <  >  <=  >=

Required complexity: O(log n) time, O(log n) space.
Full explanation: see README.md in this folder.

Usage:
    python3 adder.py 5 3          # add any two numbers
    python3 adder.py -t 13 11     # show the algorithm step by step
"""

import sys

# Python integers are unbounded, unlike Rust's u32. This mask keeps only the
# lowest 32 bits, reproducing real u32 wraparound. `&` is an allowed operator.
MASK_32 = 0xFFFFFFFF


def adder(a: int, b: int) -> int:
    """Return a + b, computed with bitwise operators only.

    XOR gives the sum of each column while ignoring carries.
    AND marks the columns that produce a carry; shifting it left by one
    puts that carry in the column it belongs to. Repeat until no carry
    is left, at which point the partial sum is the full answer.
    """
    a = a & MASK_32
    b = b & MASK_32

    while b != 0:
        carry = (a & b) << 1        # where carries happen, moved one column left
        a = (a ^ b) & MASK_32       # add without carrying
        b = carry & MASK_32         # the carries are what remains to be added

    return a


def trace(a: int, b: int) -> int:
    """Same algorithm as adder(), but prints every iteration.

    Used for the defense ("show me how it works") and for checking work
    done on paper. Not part of the required function.
    """
    a = a & MASK_32
    b = b & MASK_32

    print(f"  adder({a}, {b})\n")
    print(f"  {'step':>4} | {'a  (sum so far)':>26} | {'b  (carry left to add)':>26}")
    print("  " + "-" * 62)

    step = 0
    print(f"  {step:>4} | {a:>16b} ({a:>7}) | {b:>16b} ({b:>7})")
    while b != 0:
        carry = (a & b) << 1
        a = (a ^ b) & MASK_32
        b = carry & MASK_32
        step = step + 1             # loop counter only, allowed by the subject
        print(f"  {step:>4} | {a:>16b} ({a:>7}) | {b:>16b} ({b:>7})")

    print(f"\n  b reached 0  ->  result = {a}")
    return a


def main() -> None:
    args = sys.argv[1:]

    show_trace = False
    if args and (args[0] == "-t" or args[0] == "--trace"):
        show_trace = True
        args = args[1:]

    if not args:
        print("Exercise 00 - Adder (pass two numbers as arguments to test your own)\n")
        return

    if len(args) != 2:
        print("usage: python3 adder.py [-t] <a> <b>", file=sys.stderr)
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
        print(adder(a, b))


if __name__ == "__main__":
    main()