"""
Ready, Set, Boole! - Exercise 05: Negation Normal Form

Rewrite a propositional formula so that every negation sits directly on a
variable, and the only operators left are ! & | .

    A..Z  distinct variables     !  negation            ^  exclusive or
                                 &  conjunction         >  material condition
                                 |  disjunction         =  logical equivalence

Required complexity: N/A time, N/A space.
Full explanation: see README.md in this folder.

This file is standalone. The Node class, parser and evaluator come from
Exercises 03 and 04; what is new is the pair of tree rewriters.

Usage:
    python3 negation_normal_form.py                # demo, incl. subject examples
    python3 negation_normal_form.py "AB&!"         # convert one formula
    python3 negation_normal_form.py -t "AB|C&!"    # show each rewriting stage
    python3 negation_normal_form.py -v "AB="       # verify equivalence by table
"""

import sys

# ---------------------------------------------------------------------------
# Symbols
# ---------------------------------------------------------------------------
VARIABLES = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
CONSTANTS = "01"
UNARY_OPERATORS = "!"
BINARY_OPERATORS = "&|^>="

# Operators allowed in the OUTPUT, per the subject.
NNF_OPERATORS = "!&|"

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

    Needed because eliminating '=' and '^' uses each operand TWICE. Sharing
    one object between two places in the tree would work today, but a later
    rewrite that modified a node in place would silently change both copies.
    Copying keeps every node owned by exactly one parent.
    """
    if node is None:
        return None
    return Node(node.symbol, copy_tree(node.left), copy_tree(node.right))


# ---------------------------------------------------------------------------
# Parsing and serialising
# ---------------------------------------------------------------------------
def parse(formula: str) -> Node:
    """Turn an RPN string into an Abstract Syntax Tree. (From Exercise 03.)"""
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
    """Serialise a tree back to Reverse Polish Notation.

    Post-order: children first, then the operator. That is exactly what RPN
    is, so the traversal order IS the output order.
    """
    if node.is_leaf():
        return node.symbol
    if node.right is None:
        return to_rpn(node.left) + node.symbol
    return to_rpn(node.left) + to_rpn(node.right) + node.symbol


# ---------------------------------------------------------------------------
# Stage 1: eliminate > , = and ^
# ---------------------------------------------------------------------------
def eliminate_operators(node: Node) -> Node:
    """Rewrite >, = and ^ using only ! & |.

    The rules (Interlude 00, plus the standard one for xor):

        A > B   ->   !A | B                          material condition
        A = B   ->   (A & B) | (!A & !B)             equivalence
        A ^ B   ->   (A & !B) | (!A & B)             exclusive or

    Children are rewritten first, so nested operators are handled too.
    """
    if node.is_leaf():
        return Node(node.symbol)

    if node.symbol == "!":
        return Node("!", eliminate_operators(node.left))

    left = eliminate_operators(node.left)
    right = eliminate_operators(node.right)

    if node.symbol == ">":
        # A => B  becomes  (not A) or B
        return Node("|", Node("!", left), right)

    if node.symbol == "=":
        # A <=> B  becomes  (A and B) or (not A and not B)
        # i.e. "they are both true, or both false"
        both_true = Node("&", left, right)
        both_false = Node("&",
                          Node("!", copy_tree(left)),
                          Node("!", copy_tree(right)))
        return Node("|", both_true, both_false)

    if node.symbol == "^":
        # A xor B  becomes  (A and not B) or (not A and B)
        # i.e. "exactly one of them is true"
        only_left = Node("&", left, Node("!", copy_tree(right)))
        only_right = Node("&", Node("!", copy_tree(left)), right)
        return Node("|", only_left, only_right)

    # & and | pass through unchanged.
    return Node(node.symbol, left, right)


# ---------------------------------------------------------------------------
# Stage 2: push every negation down onto the variables
# ---------------------------------------------------------------------------
def push_negations(node: Node, negated: bool = False) -> Node:
    """Move negations inward until they sit on leaves.

    `negated` records whether an odd number of '!' has been seen on the way
    down from the root. Carrying a flag instead of rewriting in place handles
    double negation for free: two '!' flip the flag twice, back to False.

    The rules applied:

        !!A         ->  A                    double negation
        !(A & B)    ->  !A | !B              De Morgan
        !(A | B)    ->  !A & !B              De Morgan

    Expects a tree that `eliminate_operators` has already cleaned, so only
    ! & | and leaves remain.
    """
    symbol = node.symbol

    if node.is_leaf():
        if not negated:
            return Node(symbol)
        # A negated constant is simply the other constant; a negated
        # variable keeps its '!', which is where NNF wants it.
        if symbol == "0":
            return Node("1")
        if symbol == "1":
            return Node("0")
        return Node("!", Node(symbol))

    if symbol == "!":
        # Absorb this '!' into the flag rather than emitting it.
        return push_negations(node.left, not negated)

    if symbol == "&":
        # Negating an AND turns it into an OR, with both sides negated.
        new_symbol = "|" if negated else "&"
        return Node(new_symbol,
                    push_negations(node.left, negated),
                    push_negations(node.right, negated))

    if symbol == "|":
        # Negating an OR turns it into an AND, with both sides negated.
        new_symbol = "&" if negated else "|"
        return Node(new_symbol,
                    push_negations(node.left, negated),
                    push_negations(node.right, negated))

    raise ValueError(
        f"'{symbol}' should have been eliminated before pushing negations")


# ---------------------------------------------------------------------------
# The required function
# ---------------------------------------------------------------------------
def negation_normal_form(formula: str) -> str:
    """Return an equivalent formula in Negation Normal Form, as RPN."""
    tree = parse(formula)
    tree = eliminate_operators(tree)
    tree = push_negations(tree)
    return to_rpn(tree)


# ---------------------------------------------------------------------------
# Checking the result really is NNF
# ---------------------------------------------------------------------------
def is_nnf(node: Node) -> bool:
    """True if every '!' sits directly on a leaf and only ! & | are used."""
    if node.is_leaf():
        return True

    if node.symbol == "!":
        # The single child must be a leaf - that is the whole definition.
        return node.left is not None and node.left.is_leaf()

    if node.symbol == "&" or node.symbol == "|":
        return is_nnf(node.left) and is_nnf(node.right)

    return False


# ---------------------------------------------------------------------------
# Equivalence checking, reused from Exercise 04's truth table
# ---------------------------------------------------------------------------
def evaluate(node: Node, values: dict) -> bool:
    symbol = node.symbol

    if symbol == "0":
        return False
    if symbol == "1":
        return True
    if symbol in VARIABLES:
        return values[symbol]

    if symbol == "!":
        return not evaluate(node.left, values)

    left = evaluate(node.left, values)
    right = evaluate(node.right, values)

    if symbol == "&":
        return left and right
    if symbol == "|":
        return left or right
    if symbol == "^":
        return left != right
    if symbol == ">":
        return (not left) or right
    if symbol == "=":
        return left == right

    raise ValueError(f"unknown operator '{symbol}'")


def collect_variables(*formulas: str) -> list:
    """Distinct variables across one or more formulas, alphabetically."""
    found = []
    for formula in formulas:
        for char in formula:
            if char in VARIABLES and char not in found:
                found.append(char)
    found.sort()
    return found


def equivalent(first: str, second: str) -> bool:
    """True if two formulas agree on every possible assignment.

    This is the real correctness test for this exercise: a rewrite is valid
    exactly when the truth tables match. It is Exercise 04 used as a tool.
    """
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


def render_tree(node: Node, prefix: str = "", lines: list = None) -> list:
    if lines is None:
        lines = [pretty(node.symbol)]

    children = []
    if node.left is not None:
        children.append(node.left)
    if node.right is not None:
        children.append(node.right)

    for index, child in enumerate(children):
        last = index == len(children) - 1
        branch = "└── " if last else "├── "
        lines.append(f"{prefix}{branch}{pretty(child.symbol)}")
        extension = "    " if last else "│   "
        render_tree(child, prefix + extension, lines)

    return lines


def trace(formula: str) -> str:
    """Show the formula at each stage of the rewriting."""
    original = parse(formula)
    print(f"  input:  {formula}")
    print(f"          {to_infix(original)}\n")

    print("  [1] After eliminating  >  =  ^\n")
    stage_one = eliminate_operators(original)
    print(f"      {to_rpn(stage_one)}")
    print(f"      {to_infix(stage_one)}\n")

    print("  [2] After pushing negations onto the variables\n")
    stage_two = push_negations(stage_one)
    print(f"      {to_rpn(stage_two)}")
    print(f"      {to_infix(stage_two)}\n")

    print("  [3] Result tree\n")
    for line in render_tree(stage_two):
        print("      " + line)

    result = to_rpn(stage_two)
    print("\n  [4] Checks\n")
    print(f"      is NNF            : {is_nnf(stage_two)}")
    print(f"      only ! & | used   : "
          f"{all(c in VARIABLES or c in CONSTANTS or c in NNF_OPERATORS for c in result)}")
    print(f"      same truth table  : {equivalent(formula, result)}")
    print(f"\n  output: {result}")
    return result


# ---------------------------------------------------------------------------
# Demo and CLI
# ---------------------------------------------------------------------------
SUBJECT_EXAMPLES = [
    ("AB&!", "A!B!|"),
    ("AB|!", "A!B!&"),
    ("AB>", "A!B|"),
    ("AB=", "AB&A!B!&|"),
    ("AB|C&!", "A!B!&C!|"),
]


def demo() -> None:
    print("Exercise 05 - Negation Normal Form"
          "   (pass a formula as an argument to test your own)\n")

    print("  The five examples from the subject:\n")
    print(f"      {'input':<10} | {'output':<14} | {'expected':<14} | match")
    print("      " + "-" * 60)
    for formula, expected in SUBJECT_EXAMPLES:
        result = negation_normal_form(formula)
        mark = "ok" if result == expected else "DIFFERENT"
        print(f"      {formula:<10} | {result:<14} | {expected:<14} | {mark}")

    print("\n  Each rewrite rule on its own:\n")
    print(f"      {'rule':<22} | {'input':<10} | {'output':<18} | equivalent")
    print("      " + "-" * 72)
    rules = [
        ("double negation", "A!!"),
        ("material condition", "AB>"),
        ("equivalence", "AB="),
        ("exclusive or", "AB^"),
        ("De Morgan (and)", "AB&!"),
        ("De Morgan (or)", "AB|!"),
    ]
    for label, formula in rules:
        result = negation_normal_form(formula)
        print(f"      {label:<22} | {formula:<10} | {result:<18} | "
              f"{equivalent(formula, result)}")

    print("\n  Nested and mixed formulas:\n")
    print(f"      {'input':<14} | {'output':<30} | NNF | equivalent")
    print("      " + "-" * 72)
    for formula in ["AB|C&!", "AB>C>", "AB=C=", "AB^C^", "ABC&|!",
                    "AB&CD&|!", "A!!!!", "AB>!"]:
        result = negation_normal_form(formula)
        print(f"      {formula:<14} | {result:<30} | "
              f"{str(is_nnf(parse(result))):<5} | {equivalent(formula, result)}")

    print("\n  Invalid formulas are reported rather than silently guessed:\n")
    for bad in ["", "A&", "AB", "Ab&"]:
        try:
            negation_normal_form(bad)
            print(f"      {bad!r:<8} -> no error (unexpected)")
        except ValueError as error:
            print(f"      {bad!r:<8} -> {error}")

    print('\n  Run  python3 negation_normal_form.py -t "AB|C&!"'
          '   to see each stage.')


def main() -> None:
    print("{}", negation_normal_form("AB|!"))

if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        import os
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.exit(0)