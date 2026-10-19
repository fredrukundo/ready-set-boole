"""
Ready, Set, Boole! - Exercise 06: Conjunctive Normal Form

Rewrite a propositional formula as an AND of ORs of literals, serialised so
that every negation sits on a variable and every conjunction is at the end
of the formula.

    A..Z  distinct variables     !  negation            ^  exclusive or
                                 &  conjunction         >  material condition
                                 |  disjunction         =  logical equivalence

Required complexity: N/A time, N/A space.
Full explanation: see README.md in this folder.

This file is standalone. Everything from Exercise 05 (parser, NNF rewriters)
is reused here as the subject suggests; what is new is the distribution step
and the flattened serialiser.

Usage:
    python3 conjunctive_normal_form.py                # demo, subject examples
    python3 conjunctive_normal_form.py "ABCD&|&"      # convert one formula
    python3 conjunctive_normal_form.py -t "ABCD&|&"   # show every stage
    python3 conjunctive_normal_form.py -v "AB=C^"     # verify equivalence
"""

import sys
import os


# ---------------------------------------------------------------------------
# Symbols
# ---------------------------------------------------------------------------
VARIABLES = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
CONSTANTS = "01"
UNARY_OPERATORS = "!"
BINARY_OPERATORS = "&|^>="
CNF_OPERATORS = "!&|"

PRETTY = {
    "0": "⊥", "1": "T",
    "!": "¬", "&": "∧", "|": "V",
    "^": "⊕", ">": "⇒", "=": "⇔",
}


class Node:
    """One node of the Abstract Syntax Tree."""

    def __init__(self, symbol: str, left: "Node" = None, right: "Node" = None):
        self.symbol = symbol
        self.left = left
        self.right = right

    def is_leaf(self) -> bool:
        return self.left is None and self.right is None

    def __repr__(self) -> str:
        return f"Node({self.symbol!r})"


def copy_tree(node: Node) -> Node:
    """Return an independent copy of a subtree.

    Essential here: distribution duplicates whole sub-formulas, and the
    copies must not share nodes.
    """
    if node is None:
        return None
    return Node(node.symbol, copy_tree(node.left), copy_tree(node.right))


# ---------------------------------------------------------------------------
# Parsing (Exercise 03)
# ---------------------------------------------------------------------------
def parse(formula: str) -> Node:
    """Turn an RPN string into an Abstract Syntax Tree."""
    if formula is None or formula == "":
        raise ValueError("empty formula")

    stack = []

    for position, char in enumerate(formula):
        if char in VARIABLES or char in CONSTANTS:
            stack.append(Node(char))

        elif char in UNARY_OPERATORS:
            if len(stack) < 1:
                raise ValueError(
                    f"'{char}' at position {position} needs 1 operand, "
                    f"but the stack is empty")
            stack.append(Node(char, stack.pop()))

        elif char in BINARY_OPERATORS:
            if len(stack) < 2:
                raise ValueError(
                    f"'{char}' at position {position} needs 2 operands, "
                    f"but only {len(stack)} available")
            right = stack.pop()
            left = stack.pop()
            stack.append(Node(char, left, right))

        else:
            raise ValueError(
                f"invalid character '{char}' at position {position} "
                f"(allowed: A-Z 0 1 ! & | ^ > =)")

    if len(stack) > 1:
        raise ValueError(
            f"formula is incomplete: {len(stack)} values left on the stack, "
            f"expected exactly 1 (an operator is missing)")

    return stack[0]


def to_rpn(node: Node) -> str:
    """Serialise a tree to RPN (post-order), without recursion.

    Written iteratively on purpose. Distribution can produce a CNF with
    thousands of clauses hanging off one long chain of '&', and a recursive
    walk down that chain blows Python's default 1000-frame stack. The
    explicit stack has no such limit.

    The pairs on the stack are (node, children_done): the first visit
    schedules the children, the second emits the operator - which is
    exactly post-order, and post-order is RPN.
    """
    output = []
    stack = [(node, False)]

    while stack:
        current, children_done = stack.pop()

        if children_done:
            output.append(current.symbol)
            continue

        if current.is_leaf():
            output.append(current.symbol)
            continue

        stack.append((current, True))
        if current.right is not None:
            stack.append((current.right, False))
        stack.append((current.left, False))

    return "".join(output)


# ---------------------------------------------------------------------------
# Stage 1 and 2: Negation Normal Form (Exercise 05)
# ---------------------------------------------------------------------------
def eliminate_operators(node: Node) -> Node:
    """Rewrite >, = and ^ using only ! & | ."""
    if node.is_leaf():
        return Node(node.symbol)

    if node.symbol == "!":
        return Node("!", eliminate_operators(node.left))

    left = eliminate_operators(node.left)
    right = eliminate_operators(node.right)

    if node.symbol == ">":
        return Node("|", Node("!", left), right)

    if node.symbol == "=":
        return Node("|",
                    Node("&", left, right),
                    Node("&",
                         Node("!", copy_tree(left)),
                         Node("!", copy_tree(right))))

    if node.symbol == "^":
        return Node("|",
                    Node("&", left, Node("!", copy_tree(right))),
                    Node("&", Node("!", copy_tree(left)), right))

    return Node(node.symbol, left, right)


def push_negations(node: Node, negated: bool = False) -> Node:
    """Move negations inward until they sit on leaves (De Morgan)."""
    symbol = node.symbol

    if node.is_leaf():
        if not negated:
            return Node(symbol)
        if symbol == "0":
            return Node("1")
        if symbol == "1":
            return Node("0")
        return Node("!", Node(symbol))

    if symbol == "!":
        return push_negations(node.left, not negated)

    if symbol == "&":
        return Node("|" if negated else "&",
                    push_negations(node.left, negated),
                    push_negations(node.right, negated))

    if symbol == "|":
        return Node("&" if negated else "|",
                    push_negations(node.left, negated),
                    push_negations(node.right, negated))

    raise ValueError(
        f"'{symbol}' should have been eliminated before pushing negations")


def negation_normal_form(formula: str) -> str:
    """Exercise 05, reused as the subject suggests."""
    tree = push_negations(eliminate_operators(parse(formula)))
    return to_rpn(tree)


# ---------------------------------------------------------------------------
# Stage 3: distribute OR over AND
# ---------------------------------------------------------------------------
def distribute(left: Node, right: Node) -> Node:
    """Build the CNF of (left | right), where both are already in CNF.

    Distributivity (Interlude 00, VIII.5):

        A | (B & C)   ->   (A | B) & (A | C)
        (A & B) | C   ->   (A | C) & (B | C)

    If either side is a conjunction, the OR must be pushed inside it. Note
    the non-conjunction side gets DUPLICATED - that is where the size
    growth the subject warns about comes from.
    """
    if left.symbol == "&":
        # (L1 & L2) | R   ->   (L1 | R) & (L2 | R)
        return Node("&",
                    distribute(left.left, right),
                    distribute(left.right, copy_tree(right)))

    if right.symbol == "&":
        # L | (R1 & R2)   ->   (L | R1) & (L | R2)
        return Node("&",
                    distribute(left, right.left),
                    distribute(copy_tree(left), right.right))

    # Neither side is a conjunction, so this OR is already a valid clause.
    return Node("|", left, right)


def to_cnf_tree(node: Node) -> Node:
    """Turn an NNF tree into a CNF tree.

    Children are converted first, so when an OR is reached both of its
    operands are already ANDs-of-ORs and `distribute` can do its job.
    """
    if node.is_leaf():
        return Node(node.symbol)

    if node.symbol == "!":
        # In NNF this is a literal: '!' with a leaf beneath it.
        return Node("!", Node(node.left.symbol))

    left = to_cnf_tree(node.left)
    right = to_cnf_tree(node.right)

    if node.symbol == "&":
        return Node("&", left, right)

    if node.symbol == "|":
        return distribute(left, right)

    raise ValueError(f"unexpected operator '{node.symbol}' in an NNF tree")


# ---------------------------------------------------------------------------
# Stage 4: flattened serialisation
# ---------------------------------------------------------------------------
def flatten(node: Node, operator: str) -> list:
    """Collapse a chain of one associative operator into a flat list.

    `flatten(tree, "&")` turns  ((P & Q) & R)  into  [P, Q, R].

    This is what makes the subject's output shape possible: AND and OR are
    associative, so a nested chain of them is really an n-ary operation and
    the bracketing carries no meaning.

    Iterative, for the same reason as `to_rpn`: these chains get long.
    Pushing right before left makes the list come out left to right.
    """
    result = []
    stack = [node]

    while stack:
        current = stack.pop()
        if current.symbol == operator and current.right is not None:
            stack.append(current.right)
            stack.append(current.left)
        else:
            result.append(current)

    return result


def serialise_cnf(root: Node) -> str:
    """Write a CNF tree as RPN with every conjunction at the end.

    The subject requires that shape:

        AB&C&D&   must come out as   ABCD&&&
        AB|C|D|   must come out as   ABCD|||

    A plain post-order traversal would interleave the operators
    (AB&C&D&), so instead we flatten each level and emit all operands
    first, then all the operators:

        clause1 clause2 ... clauseN & & ... &     (N-1 ampersands)

    and inside each clause the same trick with '|'.
    """
    clauses = flatten(root, "&")

    pieces = []
    for clause in clauses:
        literals = flatten(clause, "|")
        text = "".join(to_rpn(literal) for literal in literals)
        text = text + "|" * (len(literals) - 1)
        pieces.append(text)

    return "".join(pieces) + "&" * (len(clauses) - 1)


# ---------------------------------------------------------------------------
# The required function
# ---------------------------------------------------------------------------
def conjunctive_normal_form(formula: str) -> str:
    """Return an equivalent formula in Conjunctive Normal Form, as RPN."""
    tree = parse(formula)
    tree = eliminate_operators(tree)      # stage 1: drop > = ^
    tree = push_negations(tree)           # stage 2: NNF (Exercise 05)
    tree = to_cnf_tree(tree)              # stage 3: distribute | over &
    return serialise_cnf(tree)            # stage 4: flattened output


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------
def is_literal(node: Node) -> bool:
    """A variable, a constant, or a negated one of those."""
    if node.is_leaf():
        return True
    return node.symbol == "!" and node.left is not None and node.left.is_leaf()


def is_clause(node: Node) -> bool:
    """A literal, or an OR of literals - no AND allowed inside."""
    stack = [node]

    while stack:
        current = stack.pop()
        if is_literal(current):
            continue
        if current.symbol == "|" and current.right is not None:
            stack.append(current.left)
            stack.append(current.right)
            continue
        return False

    return True


def is_cnf(node: Node) -> bool:
    """A clause, or an AND of clauses.

    Split on '&' first (iteratively), then check each piece is a clause.
    """
    for clause in flatten(node, "&"):
        if not is_clause(clause):
            return False
    return True


def conjunctions_at_end(formula: str) -> bool:
    """True if every '&' in the string forms one unbroken suffix.

    This is the subject's literal requirement: "every conjunction must be
    located at the end of the formula".
    """
    index = len(formula)
    while index > 0 and formula[index - 1] == "&":
        index = index - 1
    return "&" not in formula[:index]


def evaluate(node: Node, values: dict) -> bool:
    """Evaluate a tree under an assignment, without recursion.

    Post-order again: children are computed first and their results wait on
    `results`, then the operator consumes them. Iterative because a CNF tree
    can be thousands of nodes deep (see README section 6).
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

        # The left child was pushed last, so it was evaluated first and its
        # value sits deeper in `results`.
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


def collect_variables(*formulas: str) -> list:
    found = []
    for formula in formulas:
        for char in formula:
            if char in VARIABLES and char not in found:
                found.append(char)
    found.sort()
    return found


def equivalent(first: str, second: str) -> bool:
    """True if two formulas agree on every possible assignment."""
    variables = collect_variables(first, second)
    count = len(variables)
    left_tree = parse(first)
    right_tree = parse(second)

    for combination in range(1 << count):
        values = {}
        for index, variable in enumerate(variables):
            values[variable] = (combination >> (count - 1 - index)) & 1 == 1
        if evaluate(left_tree, values) != evaluate(right_tree, values):
            return False
    return True


def check_all(formula: str, result: str) -> dict:
    """Run every correctness property and report them together."""
    tree = parse(result)
    allowed = all(c in VARIABLES or c in CONSTANTS or c in CNF_OPERATORS
                  for c in result)
    return {
        "is CNF": is_cnf(tree),
        "negations on variables": all_negations_on_variables(tree),
        "conjunctions at end": conjunctions_at_end(result),
        "only ! & | used": allowed,
        "same truth table": equivalent(formula, result),
    }


def all_negations_on_variables(node: Node) -> bool:
    """True if every '!' in the tree has a bare leaf beneath it."""
    stack = [node]

    while stack:
        current = stack.pop()

        if current.is_leaf():
            continue

        if current.symbol == "!":
            if current.left is None or not current.left.is_leaf():
                return False
            continue

        stack.append(current.left)
        if current.right is not None:
            stack.append(current.right)

    return True


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------
def pretty(symbol: str) -> str:
    return PRETTY.get(symbol, symbol)


def to_infix(node: Node) -> str:
    if node.is_leaf():
        return pretty(node.symbol)
    if node.right is None:
        return f"{pretty(node.symbol)}{to_infix(node.left)}"
    return (f"({to_infix(node.left)} {pretty(node.symbol)} "
            f"{to_infix(node.right)})")


def trace(formula: str) -> str:
    """Show the formula at each stage of the conversion."""
    original = parse(formula)
    print(f"  input:  {formula}")
    print(f"          {to_infix(original)}\n")

    print("  [1] After eliminating  >  =  ^\n")
    stage_one = eliminate_operators(original)
    print(f"      {to_rpn(stage_one)}")
    print(f"      {to_infix(stage_one)}\n")

    print("  [2] After pushing negations  (this is NNF, Exercise 05)\n")
    stage_two = push_negations(stage_one)
    print(f"      {to_rpn(stage_two)}")
    print(f"      {to_infix(stage_two)}\n")

    print("  [3] After distributing  |  over  &\n")
    stage_three = to_cnf_tree(stage_two)
    print(f"      {to_infix(stage_three)}\n")

    print("  [4] Clauses\n")
    clauses = flatten(stage_three, "&")
    for index, clause in enumerate(clauses):
        literals = flatten(clause, "|")
        shown = " ∨ ".join(to_infix(literal) for literal in literals)
        print(f"      clause {index + 1}: ({shown})")

    result = serialise_cnf(stage_three)

    print("\n  [5] Flattened output"
          "   (operands first, then all the operators)\n")
    print(f"      {result}\n")

    print("  [6] Checks\n")
    for label, value in check_all(formula, result).items():
        print(f"      {label:<24}: {value}")

    print(f"\n  output: {result}")
    return result


# ---------------------------------------------------------------------------
# Demo and CLI
# ---------------------------------------------------------------------------
SUBJECT_EXAMPLES = [
    ("AB&!", "A!B!|"),
    ("AB|!", "A!B!&"),
    ("AB|C&", "AB|C&"),
    ("AB|C|D|", "ABCD|||"),
    ("AB&C&D&", "ABCD&&&"),
    ("AB&!C!|", "A!B!C!||"),
    ("AB|!C!&", "A!B!C!&&"),
]


def demo() -> None:
    print("Exercise 06 - Conjunctive Normal Form"
          "   (pass a formula as an argument to test your own)\n")

    print("  The seven examples from the subject:\n")
    print(f"      {'input':<12} | {'output':<14} | {'expected':<14} | match")
    print("      " + "-" * 64)
    for formula, expected in SUBJECT_EXAMPLES:
        result = conjunctive_normal_form(formula)
        mark = "ok" if result == expected else "DIFFERENT"
        print(f"      {formula:<12} | {result:<14} | {expected:<14} | {mark}")

    print("\n  The worked example from the instructions:\n")
    result = conjunctive_normal_form("ABCD&|&")
    print(f"      ABCD&|&  ->  {result}   (expected ABC|BD|&&, "
          f"{'ok' if result == 'ABC|BD|&&' else 'DIFFERENT'})")
    print("      A ∧ (B ∨ (C ∧ D))  becomes  "
          "A ∧ (B ∨ C) ∧ (B ∨ D)")

    print("\n  Distributivity at work:\n")
    print(f"      {'input':<14} | {'output':<26} | equivalent")
    print("      " + "-" * 60)
    for formula in ["ABC&|", "AB&C|", "AB&CD&|", "ABC|&", "AB|CD|&"]:
        result = conjunctive_normal_form(formula)
        print(f"      {formula:<14} | {result:<26} | "
              f"{equivalent(formula, result)}")

    print("\n  Other operators, converted end to end:\n")
    print(f"      {'input':<12} | {'output':<34} | equivalent")
    print("      " + "-" * 64)
    for formula in ["AB>", "AB=", "AB^", "AB>C&", "AB=C|"]:
        result = conjunctive_normal_form(formula)
        print(f"      {formula:<12} | {result:<34} | "
              f"{equivalent(formula, result)}")

    print("\n  Invalid formulas are reported rather than silently guessed:\n")
    for bad in ["", "A&", "AB", "Ab&"]:
        try:
            conjunctive_normal_form(bad)
            print(f"      {bad!r:<8} -> no error (unexpected)")
        except ValueError as error:
            print(f"      {bad!r:<8} -> {error}")

    print('\n  Run  python3 conjunctive_normal_form.py -t "ABCD&|&"'
          '   to see each stage.')


def main() -> None:
    args = sys.argv[1:]

    show_trace = False
    verify = False

    while args and args[0].startswith("-"):
        if args[0] == "-t" or args[0] == "--trace":
            show_trace = True
        elif args[0] == "-v" or args[0] == "--verify":
            verify = True
        else:
            print(f"unknown option '{args[0]}'", file=sys.stderr)
            print('usage: python3 conjunctive_normal_form.py [-t] [-v] '
                  '"<formula>"', file=sys.stderr)
            sys.exit(1)
        args = args[1:]

    if not args:
        if show_trace or verify:
            print('usage: python3 conjunctive_normal_form.py [-t] [-v] '
                  '"<formula>"', file=sys.stderr)
            sys.exit(1)
        demo()
        return

    if len(args) != 1:
        print('usage: python3 conjunctive_normal_form.py [-t] [-v] "<formula>"',
              file=sys.stderr)
        print("hint: quote the formula, the shell treats | > & specially",
              file=sys.stderr)
        sys.exit(1)

    formula = args[0]

    try:
        if show_trace:
            trace(formula)
            return

        result = conjunctive_normal_form(formula)
        print(result)

        if verify:
            for label, value in check_all(formula, result).items():
                print(f"  {label:<24}: {value}", file=sys.stderr)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        import os
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.exit(0)