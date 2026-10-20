"""
Ready, Set, Boole! - Exercise 08: Powerset

Return the powerset of a set of integers: every subset it has, including the
empty set and the set itself.

Required complexity: N/A time, O(2^n) space.
Full explanation: see README.md in this folder.

This file is standalone. Unlike Ex06 and Ex07 there is nothing to import -
a powerset needs no formula parsing, only the bit-mask enumeration trick
first used for truth-table rows in Exercise 04.

The subject assumes the input set is valid (no duplicate elements); this
implementation checks anyway and says so rather than returning nonsense.

Usage:
    python3 powerset.py                # demo
    python3 powerset.py 1 2 3          # powerset of {1, 2, 3}
    python3 powerset.py -t 1 2 3       # show how each subset is built
    python3 powerset.py -c 1 2 3 4 5   # count only, no listing
"""

import sys

# A powerset has 2^n subsets, so n is small before the output is unusable.
# 2^20 is over a million subsets; --force overrides the guard.
MAX_ELEMENTS_WITHOUT_FORCE = 20


def powerset(elements: list) -> list:
    """Return every subset of `elements`, as a list of lists.

    The idea (explained fully in README.md):

    A subset is built by making one yes/no decision per element: is this
    element in, or out? With n elements that is n independent decisions,
    so there are 2^n possible subsets.

    n yes/no decisions is exactly what an n-bit number encodes. So we
    count from 0 to 2^n - 1, and read each number's bits as the decisions:
    bit j set means "element j is in this subset".

        n = 3, counting 0..7

        0 = 000 -> {}            4 = 100 -> {c}
        1 = 001 -> {a}           5 = 101 -> {a, c}
        2 = 010 -> {b}           6 = 110 -> {b, c}
        3 = 011 -> {a, b}        7 = 111 -> {a, b, c}

    Every subset appears exactly once, because every number from 0 to
    2^n - 1 appears exactly once.
    """
    count = len(elements)
    result = []

    for mask in range(1 << count):
        subset = []
        for index in range(count):
            # Is bit `index` of `mask` set? If so, element `index` is in.
            if (mask >> index) & 1 == 1:
                subset.append(elements[index])
        result.append(subset)

    return result


def has_duplicates(elements: list) -> bool:
    """True if any value appears more than once.

    The subject says the input is assumed valid, but a duplicate would
    silently produce repeated subsets, so it is worth reporting.
    """
    seen = []
    for value in elements:
        if value in seen:
            return True
        seen.append(value)
    return False


# ---------------------------------------------------------------------------
# Display helpers (not part of the required function)
# ---------------------------------------------------------------------------
def format_set(elements: list) -> str:
    """Render a subset in mathematical notation: {}, {1}, {1, 2}."""
    if not elements:
        return "{}"
    return "{" + ", ".join(str(value) for value in elements) + "}"


def format_powerset(subsets: list) -> str:
    """Render a whole powerset as a set of sets."""
    return "{" + ", ".join(format_set(subset) for subset in subsets) + "}"


def bits(value: int, width: int) -> str:
    """Binary string, padded to `width`. Display only."""
    return format(value, "0" + str(width) + "b")


def trace(elements: list) -> list:
    """Show how each subset is derived from its bit mask."""
    count = len(elements)
    total = 1 << count

    print(f"  set: {format_set(elements)}   ({count} element"
          f"{'' if count == 1 else 's'})")
    print(f"  the powerset has 2^{count} = {total} subset"
          f"{'' if total == 1 else 's'}\n")

    if count > 0:
        print("  each bit position decides one element:\n")
        for index in range(count):
            print(f"      bit {index}  ->  {elements[index]}")
        print()
        print("  note the bits are read right to left, so bit 0 is the")
        print("  rightmost digit of the mask.\n")

    width = count
    if width < 1:
        width = 1

    print(f"      {'mask':>{width + 2}} | {'binary':>{width}} | subset")
    print("      " + "-" * (width * 2 + 24))

    result = []
    for mask in range(total):
        subset = []
        for index in range(count):
            if (mask >> index) & 1 == 1:
                subset.append(elements[index])
        result.append(subset)
        print(f"      {mask:>{width + 2}} | {bits(mask, width):>{width}} | "
              f"{format_set(subset)}")

    print(f"\n  {total} subsets, as expected.")
    return result


# ---------------------------------------------------------------------------
# Demo and CLI
# ---------------------------------------------------------------------------
def demo() -> None:
    print("Exercise 08 - Powerset"
          "   (pass numbers as arguments to test your own set)\n")

    print("  Small sets, written out in full:\n")
    for elements in [[], [1], [1, 2], [1, 2, 3]]:
        subsets = powerset(elements)
        plural = "" if len(subsets) == 1 else "s"
        print(f"      P({format_set(elements)})")
        print(f"        = {format_powerset(subsets)}")
        print(f"        {len(subsets)} subset{plural}\n")

    print("  The count doubles with each added element:\n")
    print(f"      {'n':>3} | {'set':<26} | {'2^n':>8} | subsets found")
    print("      " + "-" * 60)
    elements = []
    for n in range(9):
        subsets = powerset(elements)
        print(f"      {n:>3} | {format_set(elements):<26} | "
              f"{1 << n:>8} | {len(subsets)}")
        elements = elements + [n + 1]

    print("\n  Properties that must always hold:\n")
    for elements in [[], [7], [1, 2], [4, 8, 15, 16]]:
        subsets = powerset(elements)
        has_empty = [] in subsets
        has_full = sorted(elements) in [sorted(s) for s in subsets]
        unique = len({tuple(sorted(s)) for s in subsets}) == len(subsets)
        print(f"      {format_set(elements):<22} "
              f"size={len(subsets):<4} "
              f"contains empty set={str(has_empty):<5} "
              f"contains itself={str(has_full):<5} "
              f"all distinct={unique}")

    print("\n  Negative numbers and zero are fine:\n")
    print(f"      P({format_set([-1, 0, 5])})")
    print(f"        = {format_powerset(powerset([-1, 0, 5]))}")

    print("\n  Duplicates are reported rather than silently accepted:\n")
    for bad in [[1, 1], [3, 7, 3]]:
        print(f"      {bad} -> duplicate elements: "
              f"{has_duplicates(bad)}")

    print("\n  Run  python3 powerset.py -t 1 2 3   to see how each")
    print("  subset is built from its bit mask.")


def main() -> None:
    args = sys.argv[1:]

    show_trace = False
    count_only = False
    force = False

    while args and args[0].startswith("-") and not _is_number(args[0]):
        if args[0] == "-t" or args[0] == "--trace":
            show_trace = True
        elif args[0] == "-c" or args[0] == "--count":
            count_only = True
        elif args[0] == "-f" or args[0] == "--force":
            force = True
        else:
            print(f"unknown option '{args[0]}'", file=sys.stderr)
            print("usage: python3 powerset.py [-t] [-c] [-f] <n1> <n2> ...",
                  file=sys.stderr)
            sys.exit(1)
        args = args[1:]

    if not args:
        if show_trace or count_only or force:
            # An explicit empty set: the powerset is {{}}.
            elements = []
        else:
            demo()
            return
    else:
        elements = []
        for raw in args:
            try:
                elements.append(int(raw))
            except ValueError:
                print(f"error: '{raw}' is not a whole number", file=sys.stderr)
                sys.exit(1)

    if has_duplicates(elements):
        print("error: the set contains duplicate elements", file=sys.stderr)
        print("hint: a set has no repeated values", file=sys.stderr)
        sys.exit(1)

    if len(elements) > MAX_ELEMENTS_WITHOUT_FORCE and not force:
        print(f"error: {len(elements)} elements would produce "
              f"{1 << len(elements)} subsets", file=sys.stderr)
        print("hint: pass -f to build it anyway, or -c to count only",
              file=sys.stderr)
        sys.exit(1)

    if show_trace:
        trace(elements)
        return

    if count_only:
        print(1 << len(elements))
        return

    for subset in powerset(elements):
        print(format_set(subset))


def _is_number(text: str) -> bool:
    """True if `text` parses as an integer.

    Needed so a negative number like -3 is treated as an element and not
    mistaken for an option.
    """
    try:
        int(text)
        return True
    except ValueError:
        return False


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        import os
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.exit(0)