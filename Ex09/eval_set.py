"""
Ready, Set, Boole! - Exercise 09: Set evaluation

Evaluate a propositional formula in Reverse Polish Notation where the
variables are SETS rather than booleans.

    A..Z  distinct sets          !  complement        ^  symmetric difference
                                 &  intersection      >  material condition
                                 |  union             =  logical equivalence

Required complexity: N/A time, N/A space.
Full explanation: see README.md in this folder.

This file REUSES the parser from Exercise 05, as the subject suggests. Only
the evaluator is new: the stack machine is identical to Exercise 03, but the
operations work on sets instead of booleans.

THE CRITICAL RULE (the subject's red warning box):

    "The globally encompassing set is considered to be the union of all
     the sets given as parameters."

So the complement of A is taken relative to the union of every input set,
not relative to some infinite universe. That is why

    eval_set("A!", [[0, 1, 2]])  ->  []

the universe is {0,1,2}, A is {0,1,2}, so nothing is left outside it.

Usage:
    python3 eval_set.py                            # demo, subject examples
    python3 eval_set.py "AB&" 0,1,2 0,3,4          # -> [0]
    python3 eval_set.py -t "AB&" 0,1,2 0,3,4       # show the stack machine
    python3 eval_set.py -v "AB|" 0,1,2 3,4,5       # verify against logic
"""

import os
import sys

# ---------------------------------------------------------------------------
# Reusing Exercise 05
# ---------------------------------------------------------------------------
# The exercise folders are siblings (ready-set-boole/Ex00 ... Ex09) and are
# not a Python package, so a plain `import` cannot see across them. The path
# is built from __file__ - this file's own location - and NOT from the
# current working directory, so it works from anywhere.
#
# Ex05 is the module imported because it is the lightest one that carries
# what this exercise needs: the Node class and the RPN parser (both from
# Ex03). Ex09 does no rewriting, so pulling in Ex06's CNF machinery would
# add nothing.
_HERE = os.path.dirname(os.path.abspath(__file__))
_EX05 = os.path.join(_HERE, os.pardir, "Ex05")

if _EX05 not in sys.path:
    sys.path.insert(0, _EX05)

try:
    from negation_normal_form import (
        Node,                 # Exercise 03: a tree node
        parse,                # Exercise 03: RPN string -> tree
        collect_variables,    # Exercise 04: distinct variables, sorted
        VARIABLES,
        CONSTANTS,
        PRETTY,
    )
except ImportError as error:      # pragma: no cover - setup problem, not logic
    raise SystemExit(
        f"error: cannot import from {_EX05}\n"
        f"       {error}\n"
        f"hint: Ex09 reuses Ex05; keep the exercise folders side by side "
        f"inside ready-set-boole/")


# ---------------------------------------------------------------------------
# The set operations
# ---------------------------------------------------------------------------
# Each one is the set-theory counterpart of a boolean operator, following
# the table in Interlude 02 (XIII.4):
#
#     negation     !   <->  complement
#     disjunction  |   <->  union
#     conjunction  &   <->  intersection
#
# The remaining three are built from those, exactly as in Exercise 05.
# ---------------------------------------------------------------------------
def complement(values: set, universe: set) -> set:
    """Everything in the universe that is NOT in `values`."""
    return universe - values


def union(left: set, right: set) -> set:
    """Everything in either set."""
    return left | right


def intersection(left: set, right: set) -> set:
    """Everything in both sets."""
    return left & right


def symmetric_difference(left: set, right: set) -> set:
    """Everything in exactly one of the two sets.

    The set counterpart of XOR: 'in one or the other, but not both'.
    """
    return left ^ right


def material_condition(left: set, right: set, universe: set) -> set:
    """The set version of  A => B,  which is  (not A) or B.

    Same identity as Exercise 03, with complement for 'not' and union
    for 'or'.
    """
    return complement(left, universe) | right


def logical_equivalence(left: set, right: set, universe: set) -> set:
    """The set version of  A <=> B:  elements in both, or in neither.

    Same identity used in Exercise 05: (A & B) | (!A & !B).
    """
    both = left & right
    neither = complement(left, universe) & complement(right, universe)
    return both | neither


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------
def evaluate_tree(node: Node, values: dict, universe: set) -> set:
    """Evaluate the tree, returning a set.

    Structurally identical to Exercise 03's evaluator - only the
    operations differ. Written iteratively (post-order with an explicit
    stack) for the same reason as Exercise 06: a deep tree would exceed
    Python's recursion limit.
    """
    results = []
    stack = [(node, False)]

    while stack:
        current, children_done = stack.pop()
        symbol = current.symbol

        if not children_done:
            if current.is_leaf():
                if symbol == "0":
                    # The empty set is the set-theory counterpart of false.
                    results.append(set())
                elif symbol == "1":
                    # The universe is the counterpart of true.
                    results.append(set(universe))
                else:
                    results.append(set(values[symbol]))
                continue

            stack.append((current, True))
            if current.right is not None:
                stack.append((current.right, False))
            stack.append((current.left, False))
            continue

        if symbol == "!":
            results.append(complement(results.pop(), universe))
            continue

        # The left child was pushed last, so it was evaluated first and its
        # value sits deeper in `results`.
        right = results.pop()
        left = results.pop()

        if symbol == "&":
            results.append(intersection(left, right))
        elif symbol == "|":
            results.append(union(left, right))
        elif symbol == "^":
            results.append(symmetric_difference(left, right))
        elif symbol == ">":
            results.append(material_condition(left, right, universe))
        elif symbol == "=":
            results.append(logical_equivalence(left, right, universe))
        else:
            raise ValueError(f"unknown operator '{symbol}'")

    return results[0]


def build_universe(sets: list) -> set:
    """The globally encompassing set: the union of every input set.

    This is the subject's red warning box, and it is the single most
    important detail of this exercise.
    """
    universe = set()
    for one in sets:
        universe = universe | set(one)
    return universe


def map_variables(formula: str, sets: list) -> dict:
    """Associate each variable letter with its set.

    The subject: "The set A is the first set, the set B is the second
    set, etc..." - so the mapping is by position in the alphabet, not by
    order of appearance in the formula.

    It also says the behaviour is undefined when "the amount of sets
    provided in the list is not equal to the amount of variables in the
    formula", and encourages an error message, so both that count and the
    index range are checked.
    """
    variables = collect_variables(formula)

    if len(variables) != len(sets):
        raise ValueError(
            f"the formula has {len(variables)} distinct variable(s) "
            f"({', '.join(variables) if variables else 'none'}) but "
            f"{len(sets)} set(s) were provided; they must match")

    values = {}
    for variable in variables:
        index = VARIABLES.index(variable)
        if index >= len(sets):
            raise ValueError(
                f"variable '{variable}' is letter {index + 1} of the "
                f"alphabet, so it needs set number {index + 1}, but only "
                f"{len(sets)} set(s) were given")
        values[variable] = set(sets[index])

    return values


def eval_set(formula: str, sets: list) -> list:
    """Evaluate `formula` with `sets` as its variables; return a list.

    The subject's prototype returns Vec<i32>, so a list is returned rather
    than a Python set. The result is sorted: the subject says the order
    does not matter, and sorting makes the output reproducible and easy to
    compare.
    """
    tree = parse(formula)
    values = map_variables(formula, sets)
    universe = build_universe(sets)
    return sorted(evaluate_tree(tree, values, universe))


# ---------------------------------------------------------------------------
# Verification: the bridge between logic and sets
# ---------------------------------------------------------------------------
def evaluate_boolean(node: Node, values: dict) -> bool:
    """Evaluate the same tree as BOOLEANS. Used only for checking.

    This is Exercise 03's evaluator, kept here so the property below can
    be tested without importing a second module.
    """
    results = []
    stack = [(node, False)]

    while stack:
        current, children_done = stack.pop()
        symbol = current.symbol

        if not children_done:
            if current.is_leaf():
                if symbol == "0":
                    results.append(False)
                elif symbol == "1":
                    results.append(True)
                else:
                    results.append(values[symbol])
                continue

            stack.append((current, True))
            if current.right is not None:
                stack.append((current.right, False))
            stack.append((current.left, False))
            continue

        if symbol == "!":
            results.append(not results.pop())
            continue

        right = results.pop()
        left = results.pop()

        if symbol == "&":
            results.append(left and right)
        elif symbol == "|":
            results.append(left or right)
        elif symbol == "^":
            results.append(left != right)
        elif symbol == ">":
            results.append((not left) or right)
        elif symbol == "=":
            results.append(left == right)
        else:
            raise ValueError(f"unknown operator '{symbol}'")

    return results[0]


def membership_check(formula: str, sets: list) -> bool:
    """Verify the result against the logic-to-set correspondence.

    The defining property of this exercise:

        an element x belongs to the resulting set
        EXACTLY WHEN
        the same formula is true with each variable replaced by
        "is x a member of this set?"

    So for every x in the universe we evaluate the formula twice - once
    over sets, once over booleans - and the two answers must agree. This
    is a far stronger test than checking a few examples.
    """
    tree = parse(formula)
    values = map_variables(formula, sets)
    universe = build_universe(sets)
    result = set(evaluate_tree(tree, values, universe))

    for element in universe:
        memberships = {}
        for variable in values:
            memberships[variable] = element in values[variable]
        if evaluate_boolean(tree, memberships) != (element in result):
            return False

    # Nothing outside the universe may appear in the result.
    return result <= universe


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------
def format_list(values) -> str:
    """Render a result the way the subject prints it: [0, 1, 2] or []."""
    return "[" + ", ".join(str(value) for value in sorted(values)) + "]"


def pretty(symbol: str) -> str:
    return PRETTY.get(symbol, symbol)


def trace(formula: str, sets: list) -> list:
    """Show the stack machine running over sets, step by step."""
    values = map_variables(formula, sets)
    universe = build_universe(sets)

    print(f"  formula: {formula}\n")
    print("  sets:\n")
    for variable in sorted(values):
        print(f"      {variable} = {format_list(values[variable])}")

    print(f"\n  universe (the union of every input set):\n")
    print(f"      U = {format_list(universe)}")
    print("\n  this is what '!' complements against - see README section 2.\n")

    print("  evaluation, left to right:\n")
    print(f"      {'step':>4} | {'char':>4} | {'action':<22} | stack")
    print("      " + "-" * 72)

    stack = []
    for position, char in enumerate(formula):
        if char in VARIABLES:
            stack.append(set(values[char]))
            action = f"push {char}"
        elif char == "0":
            stack.append(set())
            action = "push empty set"
        elif char == "1":
            stack.append(set(universe))
            action = "push universe"
        elif char == "!":
            operand = stack.pop()
            stack.append(complement(operand, universe))
            action = "complement"
        else:
            right = stack.pop()
            left = stack.pop()
            if char == "&":
                stack.append(intersection(left, right))
                action = "intersection"
            elif char == "|":
                stack.append(union(left, right))
                action = "union"
            elif char == "^":
                stack.append(symmetric_difference(left, right))
                action = "symmetric difference"
            elif char == ">":
                stack.append(material_condition(left, right, universe))
                action = "material condition"
            elif char == "=":
                stack.append(logical_equivalence(left, right, universe))
                action = "equivalence"
            else:
                raise ValueError(f"invalid character '{char}'")

        shown = " , ".join(format_list(item) for item in stack)
        print(f"      {position:>4} | {char:>4} | {action:<22} | {shown}")

    result = sorted(stack[0])
    print(f"\n  result: {format_list(result)}")
    print(f"\n  membership check against logic: "
          f"{membership_check(formula, sets)}")
    return result


# ---------------------------------------------------------------------------
# Demo and CLI
# ---------------------------------------------------------------------------
SUBJECT_EXAMPLES = [
    ("AB&", [[0, 1, 2], [0, 3, 4]], [0]),
    ("AB|", [[0, 1, 2], [3, 4, 5]], [0, 1, 2, 3, 4, 5]),
    ("A!", [[0, 1, 2]], []),
]


def demo() -> None:
    print("Exercise 09 - Set evaluation"
          "   (pass a formula and sets as arguments)\n")

    print("  The three examples from the subject:\n")
    print(f"      {'formula':<8} | {'sets':<26} | {'result':<22} | expected")
    print("      " + "-" * 78)
    for formula, sets, expected in SUBJECT_EXAMPLES:
        result = eval_set(formula, sets)
        shown_sets = " ".join(format_list(one) for one in sets)
        mark = "ok" if result == expected else "MISMATCH"
        print(f"      {formula:<8} | {shown_sets:<26} | "
              f"{format_list(result):<22} | {format_list(expected)} {mark}")

    print("\n  Why \"A!\" gives [] - the universe is the union of the inputs:\n")
    print("      sets given:  A = [0, 1, 2]")
    print("      universe  :  U = [0, 1, 2]   (the union of everything given)")
    print("      A! = U - A = []              (nothing is outside A)\n")
    print("      The universe depends on ALL the sets, so adding a second")
    print("      one changes what the complement means:\n")
    print("      A = [0, 1, 2], B = [3, 4]  ->  U = "
          f"{format_list(build_universe([[0,1,2],[3,4]]))}")
    print(f"      A!, written AB|A!& to use both sets  ->  "
          f"{format_list(eval_set('AB|A!&', [[0,1,2],[3,4]]))}")
    print("      which is exactly the part of U that is outside A.")

    print("\n  Every operator, on A = [0, 1, 2], B = [2, 3, 4]:\n")
    sets = [[0, 1, 2], [2, 3, 4]]
    print(f"      universe = {format_list(build_universe(sets))}\n")
    print(f"      {'formula':<10} | {'operation':<26} | result")
    print("      " + "-" * 62)
    for formula, label in [
        ("AB&", "intersection"),
        ("AB|", "union"),
        ("AB^", "symmetric difference"),
        ("AB>", "material condition"),
        ("AB=", "equivalence"),
        ("AB|A!&", "complement of A, inside U"),
        ("AB|B!&", "complement of B, inside U"),
    ]:
        print(f"      {formula:<10} | {label:<26} | "
              f"{format_list(eval_set(formula, sets))}")

    print("\n  De Morgan holds for sets too (Interlude 02):\n")
    print(f"      {'formula':<12} | {'result':<22} | reads as")
    print("      " + "-" * 62)
    for formula, reads in [
        ("AB|!", "complement of the union"),
        ("A!B!&", "intersection of the complements"),
        ("AB&!", "complement of the intersection"),
        ("A!B!|", "union of the complements"),
    ]:
        print(f"      {formula:<12} | "
              f"{format_list(eval_set(formula, sets)):<22} | {reads}")
    same_one = eval_set("AB|!", sets) == eval_set("A!B!&", sets)
    same_two = eval_set("AB&!", sets) == eval_set("A!B!|", sets)
    print(f"\n      (A | B)! == A!&B! : {same_one}")
    print(f"      (A & B)! == A!|B! : {same_two}")

    print("\n  Edge cases:\n")
    print(f"      {'case':<34} | result")
    print("      " + "-" * 54)
    for label, formula, sets_in in [
        ("empty set as input", "A", [[]]),
        ("complement of an empty set", "A!", [[]]),
        ("disjoint sets intersected", "AB&", [[1, 2], [3, 4]]),
        ("a set with itself", "AA&", [[1, 2]]),
        ("three sets", "ABC&&", [[1, 2, 3], [2, 3, 4], [3, 4, 5]]),
        ("negative numbers", "AB|", [[-2, -1], [0, 1]]),
    ]:
        print(f"      {label:<34} | "
              f"{format_list(eval_set(formula, sets_in))}")

    print("\n  Invalid input is reported rather than silently guessed:\n")
    for formula, sets_in in [
        ("", [[1]]),
        ("AB&", [[1, 2]]),
        ("A", [[1], [2]]),
        ("Ab&", [[1], [2]]),
        ("AB", [[1], [2]]),
    ]:
        try:
            eval_set(formula, sets_in)
            print(f"      {formula!r:<8} -> no error (unexpected)")
        except ValueError as error:
            print(f"      {formula!r:<8} -> {error}")

    print('\n  Run  python3 eval_set.py -t "AB&" 0,1,2 0,3,4'
          '   to see the stack machine.')


def parse_set_argument(text: str) -> list:
    """Parse one command-line set: "0,1,2", "[0,1,2]" or "" for empty."""
    cleaned = text.strip()
    if cleaned.startswith("[") and cleaned.endswith("]"):
        cleaned = cleaned[1:-1]
    cleaned = cleaned.strip()

    if cleaned == "":
        return []

    values = []
    for piece in cleaned.split(","):
        piece = piece.strip()
        if piece == "":
            continue
        try:
            values.append(int(piece))
        except ValueError:
            raise ValueError(f"'{piece}' is not a whole number")
    return values


def main() -> None:
    args = sys.argv[1:]

    show_trace = False
    verify = False

    while args and args[0].startswith("-") and len(args[0]) > 1 \
            and not args[0][1].isdigit():
        if args[0] == "-t" or args[0] == "--trace":
            show_trace = True
        elif args[0] == "-v" or args[0] == "--verify":
            verify = True
        else:
            print(f"unknown option '{args[0]}'", file=sys.stderr)
            print('usage: python3 eval_set.py [-t] [-v] "<formula>" '
                  '<set1> <set2> ...', file=sys.stderr)
            sys.exit(1)
        args = args[1:]

    if not args:
        if show_trace or verify:
            print('usage: python3 eval_set.py [-t] [-v] "<formula>" '
                  '<set1> <set2> ...', file=sys.stderr)
            sys.exit(1)
        demo()
        return

    formula = args[0]
    raw_sets = args[1:]

    try:
        sets = [parse_set_argument(text) for text in raw_sets]

        for index, one in enumerate(sets):
            if len(set(one)) != len(one):
                raise ValueError(
                    f"set number {index + 1} contains duplicate elements")

        if show_trace:
            trace(formula, sets)
            return

        result = eval_set(formula, sets)
        print(format_list(result))

        if verify:
            universe = build_universe(sets)
            print(f"  universe         : {format_list(universe)}",
                  file=sys.stderr)
            print(f"  membership check : {membership_check(formula, sets)}",
                  file=sys.stderr)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.exit(0)