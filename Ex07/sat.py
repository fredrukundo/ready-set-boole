"""
Ready, Set, Boole! - Exercise 07: SAT

Decide whether a propositional formula is satisfiable: is there at least one
assignment of its variables that makes the whole formula true?

Required complexity: O(2^n) time, N/A space.
Full explanation: see README.md in this folder.

This file REUSES the previous exercises instead of copying them, as the
subject's hint suggests. The parser, the evaluator and the variable
collector are imported from Ex06; see the import block below.

Usage:
    python3 sat.py                  # demo, including the subject examples
    python3 sat.py "AB|"            # -> True
    python3 sat.py -m "AB>C&"       # also print a satisfying assignment
    python3 sat.py -t "AA!&"        # show the search, assignment by assignment
"""

import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Reusing the previous exercises
# ---------------------------------------------------------------------------
# The exercise folders are siblings (ready-set-boole/Ex00 ... Ex09) and are
# not a Python package, so a plain `import` cannot see across them. We add
# the sibling folder to the module search path.
#
# The path is built from __file__ - this file's own location - and NOT from
# the current working directory, so it works whether the program is started
# with `cd Ex07 && python3 sat.py` or `python3 Ex07/sat.py` from the repo
# root.
#
# Ex06 is the module imported because it already contains the whole stack:
# the parser from Ex03, the evaluator and variable collector from Ex04, and
# the normal-form rewriters from Ex05 and Ex06.

PROJECT_ROOT = Path(__file__).parent.parent
EX06_DIR = PROJECT_ROOT / "Ex06"

if not EX06_DIR.is_dir():
    raise SystemExit(
        f"error: Ex06 directory not found: {EX06_DIR}"
    )

sys.path.insert(0, str(EX06_DIR))

try:
    from conjunctive_normal_form import (
        parse,                      # Exercise 03: RPN string -> tree
        evaluate,                   # Exercise 04: tree + assignment -> bool
        collect_variables,          # Exercise 04: distinct variables, sorted
        conjunctive_normal_form,    # Exercise 06: CNF rewriting
        flatten,                    # Exercise 06: collapse an operator chain
        to_rpn,                     # Exercise 05: tree -> RPN string
    )
except ImportError as error:
    raise SystemExit(
        "error: could not import the required functions from "
        f"Ex06/conjunctive_normal_form.py\n{error}"
    ) from error


# Above this many distinct variables a full search is impractical to display.
# It does not limit `sat` itself, only the -t trace.
MAX_TRACE_VARIABLES = 10


# ---------------------------------------------------------------------------
# The required function
# ---------------------------------------------------------------------------
def sat(formula: str) -> bool:
    """True if some assignment of the variables makes `formula` true.

    Brute force: walk all 2^n assignments and stop at the first one that
    evaluates to true. The subject allows O(2^n), and stopping early means
    satisfiable formulas are usually settled long before the end.

    A formula with no variables (only constants) has exactly one
    assignment - the empty one - which this handles naturally, since
    2^0 is 1.
    """
    return find_model(formula) is not None


def find_model(formula: str):
    """Return a satisfying assignment, or None if the formula is unsatisfiable.

    A satisfying assignment is called a *model*. Returning it rather than a
    bare True is strictly more useful: the caller can check the answer, and
    `sat` is then a one-liner on top of it.
    """
    tree = parse(formula)
    variables = collect_variables(formula)
    count = len(variables)

    for combination in range(1 << count):
        values = {}
        for index, variable in enumerate(variables):
            values[variable] = (combination >> (count - 1 - index)) & 1 == 1
        if evaluate(tree, values):
            return values

    return None


# ---------------------------------------------------------------------------
# Related questions, answered with the same machinery
# ---------------------------------------------------------------------------
def is_tautology(formula: str) -> bool:
    """True if the formula holds under EVERY assignment.

    A formula is a tautology exactly when its negation is unsatisfiable -
    if nothing can make it false, it is always true. Negating in RPN is
    just appending '!'.
    """
    return not sat(formula + "!")


def is_contradiction(formula: str) -> bool:
    """True if no assignment satisfies the formula."""
    return not sat(formula)


def classify(formula: str) -> str:
    """Name the formula: tautology, contradiction, or contingent."""
    if is_contradiction(formula):
        return "contradiction (never true)"
    if is_tautology(formula):
        return "tautology (always true)"
    return "contingent (sometimes true)"


def format_model(values: dict) -> str:
    """Render an assignment as 'A=1, B=0'."""
    if not values:
        return "(no variables)"
    parts = []
    for variable in sorted(values):
        parts.append(f"{variable}={'1' if values[variable] else '0'}")
    return ", ".join(parts)


# ---------------------------------------------------------------------------
# The CNF view (why Exercise 06 comes first)
# ---------------------------------------------------------------------------
def explain_via_cnf(formula: str) -> None:
    """Show the formula as CNF clauses and check them against a model.

    Not used by `sat` - brute force is enough for the required complexity -
    but it shows the structure real SAT solvers exploit: a CNF formula is
    satisfied exactly when every clause has at least one true literal.
    """
    cnf = conjunctive_normal_form(formula)
    print(f"      CNF: {cnf}")

    clauses = flatten(parse(cnf), "&")
    model = find_model(formula)

    if model is None:
        print(f"      {len(clauses)} clause(s); no assignment satisfies them all")
        return

    print(f"      model: {format_model(model)}\n")
    for index, clause in enumerate(clauses):
        literals = flatten(clause, "|")
        shown = " | ".join(to_rpn(literal) for literal in literals)
        satisfied = [to_rpn(literal) for literal in literals
                     if evaluate(literal, model)]
        print(f"      clause {index + 1}: ({shown})"
              f"  satisfied by {', '.join(satisfied)}")


# ---------------------------------------------------------------------------
# Trace
# ---------------------------------------------------------------------------
def trace(formula: str) -> bool:
    """Show the search: every assignment tried, and where it stopped."""
    tree = parse(formula)
    variables = collect_variables(formula)
    count = len(variables)

    print(f"  formula: {formula}")
    print(f"  variables: {', '.join(variables) if variables else '(none)'}"
          f"   ->  {1 << count} assignment(s) to try\n")

    if count > MAX_TRACE_VARIABLES:
        print(f"  too many variables to list ({count}); "
              f"running without the table\n")
        result = sat(formula)
        print(f"  satisfiable: {result}")
        return result

    header = "      " + "  ".join(f"{v}" for v in variables)
    print(header + "   | result")
    print("      " + "-" * (len(header) + 4))

    answer = False
    for combination in range(1 << count):
        values = {}
        for index, variable in enumerate(variables):
            values[variable] = (combination >> (count - 1 - index)) & 1 == 1

        outcome = evaluate(tree, values)
        cells = "  ".join("1" if values[v] else "0" for v in variables)
        marker = "  <- satisfiable, stop here" if outcome else ""
        print(f"      {cells}   | {'1' if outcome else '0'}{marker}")

        if outcome:
            answer = True
            break

    print()
    if answer:
        print(f"  satisfiable: True")
    else:
        print(f"  all {1 << count} assignments give false")
        print(f"  satisfiable: False")

    print(f"  classification: {classify(formula)}")
    return answer


# ---------------------------------------------------------------------------
# Demo and CLI
# ---------------------------------------------------------------------------
SUBJECT_EXAMPLES = [
    ("AB|", True),
    ("AB&", True),
    ("AA!&", False),
    ("AA^", False),
]


def demo() -> None:
    print("Exercise 07 - SAT"
          "   (pass a formula as an argument to test your own)\n")

    print("  The four examples from the subject:\n")
    print(f"      {'formula':<10} | {'sat':<6} | {'expected':<8} | match")
    print("      " + "-" * 46)
    for formula, expected in SUBJECT_EXAMPLES:
        result = sat(formula)
        mark = "ok" if result == expected else "MISMATCH"
        print(f"      {formula:<10} | {str(result):<6} | "
              f"{str(expected):<8} | {mark}")

    print("\n  Satisfiable formulas, with a witness assignment:\n")
    print(f"      {'formula':<12} | {'sat':<6} | model")
    print("      " + "-" * 52)
    for formula in ["A", "AB&", "AB|", "AB>", "AB=", "AB^", "ABC&&", "AB>C&"]:
        model = find_model(formula)
        print(f"      {formula:<12} | {str(model is not None):<6} | "
              f"{format_model(model) if model is not None else '-'}")

    print("\n  Unsatisfiable formulas (contradictions):\n")
    print(f"      {'formula':<14} | {'sat':<6} | meaning")
    print("      " + "-" * 56)
    for formula, meaning in [
        ("AA!&", "A and not A"),
        ("AA^", "A differs from itself"),
        ("AA!&B|B!&", "a contradiction, and not B"),
        ("AB&A!&", "A and B, and not A"),
    ]:
        print(f"      {formula:<14} | {str(sat(formula)):<6} | {meaning}")

    print("\n  Classification (satisfiability answers three questions):\n")
    print(f"      {'formula':<12} | classification")
    print("      " + "-" * 52)
    for formula in ["AA!|", "AA!&", "A", "AB|", "AB>B>A>"]:
        print(f"      {formula:<12} | {classify(formula)}")

    print("\n  Why Exercise 06 comes first - the CNF view of \"AB>C&\":\n")
    explain_via_cnf("AB>C&")

    print("\n  Invalid formulas are reported rather than silently guessed:\n")
    for bad in ["", "A&", "AB", "Ab&"]:
        try:
            sat(bad)
            print(f"      {bad!r:<8} -> no error (unexpected)")
        except ValueError as error:
            print(f"      {bad!r:<8} -> {error}")

    print('\n  Run  python3 sat.py -t "AA!&"   to watch the search.')


def main() -> None:
    args = sys.argv[1:]

    show_trace = False
    show_model = False

    while args and args[0].startswith("-"):
        if args[0] == "-t" or args[0] == "--trace":
            show_trace = True
        elif args[0] == "-m" or args[0] == "--model":
            show_model = True
        else:
            print(f"unknown option '{args[0]}'", file=sys.stderr)
            print('usage: python3 sat.py [-t] [-m] "<formula>"', file=sys.stderr)
            sys.exit(1)
        args = args[1:]

    if not args:
        if show_trace or show_model:
            print('usage: python3 sat.py [-t] [-m] "<formula>"', file=sys.stderr)
            sys.exit(1)
        demo()
        return

    if len(args) != 1:
        print('usage: python3 sat.py [-t] [-m] "<formula>"', file=sys.stderr)
        print("hint: quote the formula, the shell treats | > & specially",
              file=sys.stderr)
        sys.exit(1)

    formula = args[0]

    try:
        if show_trace:
            trace(formula)
            return

        model = find_model(formula)
        print(model is not None)

        if show_model:
            if model is None:
                print("  no satisfying assignment exists", file=sys.stderr)
            else:
                print(f"  model: {format_model(model)}", file=sys.stderr)
            print(f"  {classify(formula)}", file=sys.stderr)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.exit(0)