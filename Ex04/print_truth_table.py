"""
Ready, Set, Boole! - Exercise 04: Truth table

Print the truth table of a propositional formula given in Reverse Polish
Notation, where the operands are variables A..Z.

    A..Z  distinct variables     !  negation            ^  exclusive or
                                 &  conjunction         >  material condition
                                 |  disjunction         =  logical equivalence

Required complexity: O(2^n) time, N/A space.
Full explanation: see README.md in this folder.

The output format is specified exactly by the subject (Chapter VII):

    | A | B | C | = |
    |---|---|---|---|
    | 0 | 0 | 0 | 0 |
    ...

This file is standalone. The Node class and parser come from Exercise 03,
with one change: leaves may now be variables as well as constants.

Usage:
    python3 print_truth_table.py               # demo, incl. the subject example
    python3 print_truth_table.py "AB&C|"       # print one truth table
    python3 print_truth_table.py -t "AB&C|"    # also show the parsed tree
"""

import sys

# ---------------------------------------------------------------------------
# Symbols
# ---------------------------------------------------------------------------
VARIABLES = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
CONSTANTS = "01"
UNARY_OPERATORS = "!"
BINARY_OPERATORS = "&|^>="

# Above this many distinct variables the table stops being printable:
# 2^17 is 131072 rows. --force overrides it.
MAX_VARIABLES_WITHOUT_FORCE = 16

# Used only for the optional tree display.
PRETTY = {
    "0": "⊥", "1": "⊤",
    "!": "¬", "&": "∧", "|": "∨",
    "^": "⊕", ">": "⇒", "=": "⇔",
}


class Node:
    """One node of the Abstract Syntax Tree.

    A node is either:
      - a leaf     : symbol is a variable A..Z, or the constant '0'/'1'
      - a unary op : symbol is '!', only `left` is used
      - a binary op: symbol is one of &|^>=, both children are used
    """

    def __init__(self, symbol: str, left: "Node" = None, right: "Node" = None):
        self.symbol = symbol
        self.left = left
        self.right = right

    def is_leaf(self) -> bool:
        return self.left is None and self.right is None

    def __repr__(self) -> str:
        return f"Node({self.symbol!r})"


# ---------------------------------------------------------------------------
# Parsing: Reverse Polish Notation -> tree
# ---------------------------------------------------------------------------
def parse(formula: str) -> Node:
    """Turn an RPN string into an Abstract Syntax Tree.

    Identical to Exercise 03 except that a leaf may now be a variable.
    Constants 0 and 1 are still accepted; the subject's table for this
    exercise lists only A..Z, so accepting them is a harmless extension
    that keeps Exercise 03's formulas working here too.
    """
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
            # The SECOND operand was pushed last, so it comes off first.
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


# ---------------------------------------------------------------------------
# Evaluation under an assignment of values to variables
# ---------------------------------------------------------------------------
def evaluate(node: Node, values: dict) -> bool:
    """Evaluate the tree, looking variables up in `values`.

    `values` maps a variable letter to True or False. Exercise 03 had no
    variables, so this extra argument is the only change to the evaluator.
    """
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


def collect_variables(formula: str) -> list:
    """Return the distinct variables of a formula, in alphabetical order.

    Alphabetical order is what makes the columns come out as A, B, C -
    matching the subject's example - and it keeps the output deterministic
    regardless of the order the letters happen to appear in the formula.
    """
    found = []
    for char in formula:
        if char in VARIABLES and char not in found:
            found.append(char)
    found.sort()
    return found


# ---------------------------------------------------------------------------
# The required function
# ---------------------------------------------------------------------------
def print_truth_table(formula: str) -> None:
    """Write the truth table of `formula` to standard output.

    Output format is fixed by the subject:

        | A | B | C | = |
        |---|---|---|---|
        | 0 | 0 | 0 | 0 |

    Each line is "| " then the cells joined by " | " then " |", with no
    trailing whitespace. The last column, headed '=', is the result.
    """
    root = parse(formula)
    variables = collect_variables(formula)
    count = len(variables)

    # Header row: one column per variable, plus the result column '='.
    print("| " + " | ".join(variables + ["="]) + " |")

    # Separator row: '---' per column.
    print("|" + "---|" * (count + 1))

    # One row per combination: 2^n of them.
    # Bit (count - 1 - index) of `combination` is the value of variables[index],
    # so the first variable is the most significant bit and the rows come out
    # in the natural counting order 000, 001, 010, ...
    for combination in range(1 << count):
        values = {}
        for index, variable in enumerate(variables):
            values[variable] = (combination >> (count - 1 - index)) & 1 == 1

        cells = []
        for variable in variables:
            cells.append("1" if values[variable] else "0")
        cells.append("1" if evaluate(root, values) else "0")

        print("| " + " | ".join(cells) + " |")


# ---------------------------------------------------------------------------
# Display helpers (not part of the required function)
# ---------------------------------------------------------------------------
def pretty(symbol: str) -> str:
    if symbol in PRETTY:
        return PRETTY[symbol]
    return symbol


def to_infix(node: Node) -> str:
    """Render a tree the way a human writes maths."""
    if node.is_leaf():
        return pretty(node.symbol)
    if node.right is None:
        return f"{pretty(node.symbol)}{to_infix(node.left)}"
    return (f"({to_infix(node.left)} {pretty(node.symbol)} "
            f"{to_infix(node.right)})")


def render_tree(node: Node, prefix: str = "", lines: list = None) -> list:
    """Draw the tree with box-drawing characters, root at the top."""
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


# ---------------------------------------------------------------------------
# Demo and CLI
# ---------------------------------------------------------------------------
def demo() -> None:
    print("Exercise 04 - Truth table"
          "   (pass a formula as an argument to test your own)\n")

    print('  The subject\'s example: "AB&C|"  ->  (A ∧ B) ∨ C\n')
    print_truth_table("AB&C|")

    print('\n  A single variable: "A"\n')
    print_truth_table("A")

    print('\n  Negation: "A!"\n')
    print_truth_table("A!")

    print('\n  Material condition: "AB>"   (false only when A holds '
          'and B fails)\n')
    print_truth_table("AB>")

    print('\n  A contradiction: "AA!&"   (never true)\n')
    print_truth_table("AA!&")

    print('\n  A tautology: "AA!|"   (always true)\n')
    print_truth_table("AA!|")

    print('\n  A variable used several times: "AAB&|"\n')
    print_truth_table("AAB&|")

    print("\n  Invalid formulas are reported rather than silently guessed:\n")
    for bad in ["", "A&", "AB", "Ab&", "&"]:
        try:
            print_truth_table(bad)
            print(f"      {bad!r:<8} -> no error (unexpected)")
        except ValueError as error:
            print(f"      {bad!r:<8} -> {error}")

    print('\n  Check the format against the subject with:'
          '  python3 print_truth_table.py "AB&C|" | cat -e')


def main() -> None:
    args = sys.argv[1:]

    show_tree = False
    force = False

    while args and args[0].startswith("-"):
        if args[0] == "-t" or args[0] == "--tree":
            show_tree = True
        elif args[0] == "-f" or args[0] == "--force":
            force = True
        else:
            print(f"unknown option '{args[0]}'", file=sys.stderr)
            print("usage: python3 print_truth_table.py [-t] [-f] \"<formula>\"",
                  file=sys.stderr)
            sys.exit(1)
        args = args[1:]

    if not args:
        if show_tree or force:
            print("usage: python3 print_truth_table.py [-t] [-f] \"<formula>\"",
                  file=sys.stderr)
            sys.exit(1)
        demo()
        return

    if len(args) != 1:
        print("usage: python3 print_truth_table.py [-t] [-f] \"<formula>\"",
              file=sys.stderr)
        print("hint: quote the formula, the shell treats | > & specially",
              file=sys.stderr)
        sys.exit(1)

    formula = args[0]

    try:
        count = len(collect_variables(formula))
        if count > MAX_VARIABLES_WITHOUT_FORCE and not force:
            print(f"error: {count} distinct variables would produce "
                  f"{1 << count} rows", file=sys.stderr)
            print("hint: pass -f to print it anyway", file=sys.stderr)
            sys.exit(1)

        if show_tree:
            root = parse(formula)
            print("  tree:\n")
            for line in render_tree(root):
                print("      " + line)
            print(f"\n  readable: {to_infix(root)}\n")

        print_truth_table(formula)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        # Raised when the reader closes early, e.g. `... | head -5`.
        # Without this, Python prints a traceback that looks like a crash.
        # Redirect stdout to devnull so the interpreter's shutdown flush
        # does not raise a second time, then exit quietly.
        import os
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.exit(0)