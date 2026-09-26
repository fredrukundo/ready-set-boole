"""
Ready, Set, Boole! - Exercise 02: Gray code

Return the Gray code equivalent of a natural number n.

Required complexity: N/A (the subject sets no bound; this runs in O(1)).
Full explanation: see README.md in this folder.

This file is fully standalone - Gray code needs nothing from Ex00 or Ex01.

Usage:
    python3 gray_code.py              # demo table for 0..15
    python3 gray_code.py 8            # convert a single number
    python3 gray_code.py -t 8         # show the conversion bit by bit
    python3 gray_code.py -r 0 31      # table for a range of values
"""

import sys

# Python integers are unbounded, unlike Rust's u32. This mask keeps only the
# lowest 32 bits, reproducing real u32 behaviour.
MASK_32 = 0xFFFFFFFF


def gray_code(n: int) -> int:
    """Return the Gray code of n.

    The defining property of Gray code is that consecutive values differ by
    exactly ONE bit. Ordinary binary does not have this property: going from
    7 (0111) to 8 (1000) flips all four bits at once.

    The conversion is a single expression:

        gray(n) = n XOR (n >> 1)

    Why it works, in one line: bit i of the Gray code is bit i of n XOR
    bit i+1 of n, and shifting n right by one lines bit i+1 up with bit i
    so a single XOR does all the positions at once. See README section 4.
    """
    n = n & MASK_32
    return (n ^ (n >> 1)) & MASK_32


def bits(value: int, width: int = 8) -> str:
    """Format a value as a zero-padded binary string. Display only."""
    return format(value & MASK_32, "0" + str(width) + "b")


def differing_bit(x: int, y: int) -> int:
    """Return how many bits differ between x and y.

    Used by the demo to show the one-bit-change property. XOR marks every
    position where the two values differ, so we just count the 1s.
    """
    diff = (x ^ y) & MASK_32
    count = 0
    while diff != 0:
        if (diff & 1) != 0:
            count = count + 1
        diff = diff >> 1
    return count


def trace(n: int) -> int:
    """Show the conversion of a single value, column by column."""
    n = n & MASK_32
    shifted = n >> 1
    result = n ^ shifted

    width = 8
    if n > 255:
        width = 32

    print(f"  gray_code({n})\n")
    print(f"    n        =  {bits(n, width)}   ({n})")
    print(f"    n >> 1   =  {bits(shifted, width)}   ({shifted})")
    print("                " + "-" * width)
    print(f"    XOR      =  {bits(result, width)}   ({result})")
    print("\n  Each output bit is 1 exactly where the two rows differ.")
    print(f"\n  result = {result}")
    return result


def table(start: int, end: int) -> None:
    """Print a table of Gray codes, highlighting the one-bit change."""
    width = 8
    if end > 255:
        width = 16

    # Columns must be at least as wide as their own headers, or the header
    # row overflows and stops lining up with the data underneath it.
    bin_w = width
    if bin_w < 14:
        bin_w = 14

    header = (f"  {'n':>6} | {'n in binary':>{bin_w}} | {'gray(n)':>8} | "
              f"{'gray in binary':>{bin_w}} | {'bits changed':>12}")
    print(header)
    print("  " + "-" * (len(header) - 2))

    previous = None
    value = start
    while value <= end:
        g = gray_code(value)
        if previous is None:
            changed = "-"
        else:
            changed = str(differing_bit(previous, g))
        print(f"  {value:>6} | {bits(value, width):>{bin_w}} | {g:>8} | "
              f"{bits(g, width):>{bin_w}} | {changed:>12}")
        previous = g
        value = value + 1


def demo() -> None:
    """Shown when no arguments are given."""
    print("Exercise 02 - Gray code   (pass a number as an argument to test your own)\n")
    table(0, 15)

    # The whole point of Gray code: verify the one-bit property holds.
    failures = 0
    previous = gray_code(0)
    n = 1
    while n <= 65535:
        current = gray_code(n)
        if differing_bit(previous, current) != 1:
            failures = failures + 1
        previous = current
        n = n + 1

    print()
    if failures == 0:
        print("  Property check: consecutive Gray codes differ by exactly one bit,")
        print("  verified for every n from 0 to 65535.")
    else:
        print(f"  Property check FAILED for {failures} values.")

    print("\n  Run  python3 gray_code.py -t 8      to see one conversion in detail.")
    print("  Run  python3 gray_code.py -r 0 31   for a table over a range.")


def main() -> None:
    args = sys.argv[1:]

    mode = "single"
    if args and (args[0] == "-t" or args[0] == "--trace"):
        mode = "trace"
        args = args[1:]
    elif args and (args[0] == "-r" or args[0] == "--range"):
        mode = "range"
        args = args[1:]

    if not args:
        if mode == "single":
            demo()
            return
        print("usage: python3 gray_code.py [-t <n> | -r <start> <end>] | <n>",
              file=sys.stderr)
        sys.exit(1)

    # Parse every argument as a natural number that fits in 32 bits.
    values = []
    for raw in args:
        try:
            value = int(raw)
        except ValueError:
            print(f"error: '{raw}' is not a whole number", file=sys.stderr)
            sys.exit(1)
        if value < 0:
            print("error: this function takes natural numbers (>= 0)",
                  file=sys.stderr)
            sys.exit(1)
        if value > MASK_32:
            print(f"error: values must fit in 32 bits (max {MASK_32})",
                  file=sys.stderr)
            sys.exit(1)
        values.append(value)

    if mode == "range":
        if len(values) != 2:
            print("usage: python3 gray_code.py -r <start> <end>", file=sys.stderr)
            sys.exit(1)
        if values[0] > values[1]:
            print("error: start must not be greater than end", file=sys.stderr)
            sys.exit(1)
        if values[1] > values[0] + 1000:
            print("error: range too large to display (limit 1000 rows)",
                  file=sys.stderr)
            sys.exit(1)
        table(values[0], values[1])
        return

    if len(values) != 1:
        print("usage: python3 gray_code.py [-t] <n>", file=sys.stderr)
        sys.exit(1)

    if mode == "trace":
        trace(values[0])
    else:
        print(gray_code(values[0]))


if __name__ == "__main__":
    main()