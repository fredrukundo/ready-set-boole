"""
Ready, Set, Boole! - Exercise 03: Boolean evaluation

Evaluate a propositional formula written in Reverse Polish Notation.

    0  false            !  negation            ^  exclusive or
    1  true             &  conjunction         >  material condition
                        |  disjunction         =  logical equivalence

Required complexity: O(n) time, N/A space.
Full explanation: see README.md in this folder.

This file is standalone. It builds a binary Abstract Syntax Tree, as the
subject suggests, because Exercises 05 and 06 must *rewrite* formulas and
not merely evaluate them - a tree is what makes that possible.

Usage:
    python3 eval_formula.py                 # demo, including subject examples
    python3 eval_formula.py "1011||="       # evaluate one formula
    python3 eval_formula.py -t "10|1&"      # show parsing, tree and evaluation
"""

import sys

# ---------------------------------------------------------------------------
# Symbols
# ---------------------------------------------------------------------------
CONSTANTS = "01"
UNARY_OPERATORS = "!"
BINARY_OPERATORS = "&|^>="

# Used only for display, so the tree reads like the maths in the subject.
PRETTY = {
    "0": "\u22a5",   # falsum
    "1": "\u22a4",   # verum
    "!": "\u00ac",   # not
    "&": "\u2227",   # and
    "|": "\u2228",   # or
    "^": "\u2295",   # xor
    ">": "\u21d2",   # implies
    "=": "\u21d4",   # equivalent
}


class Node:
    """One node of the Abstract Syntax Tree.

    A node is either:
      - a leaf     : symbol is '0' or '1', both children are None
      - a unary op : symbol is '!', only `left` is used
      - a binary op: symbol is one of &|^>=, both children are used

    For binary operators `left` is the FIRST operand and `right` the second.
    That order matters for '>' , which is not commutative: A > B is not the
    same as B > A.
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

    One left-to-right pass with a stack:
      - a constant becomes a leaf, pushed on the stack
      - an operator pops the operands it needs, becomes their parent,
        and the new subtree is pushed back

    At the end exactly one tree must remain: the root.

    Raises ValueError with a helpful message if the formula is malformed.
    The subject says the behaviour is undefined for invalid input, but
    encourages printing an error - so we raise instead of guessing.
    """
    if formula is None or formula == "":
        raise ValueError("empty formula")

    stack = []

    for position, char in enumerate(formula):
        if char in CONSTANTS:
            stack.append(Node(char))

        elif char in UNARY_OPERATORS:
            if len(stack) < 1:
                raise ValueError(
                    f"'{char}' at position {position} needs 1 operand, "
                    f"but the stack is empty")
            operand = stack.pop()
            stack.append(Node(char, operand))

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
                f"(allowed: 0 1 ! & | ^ > =)")

    if len(stack) == 0:
        raise ValueError("formula produced no result")
    if len(stack) > 1:
        raise ValueError(
            f"formula is incomplete: {len(stack)} values left on the stack, "
            f"expected exactly 1 (an operator is missing)")

    return stack[0]


# ---------------------------------------------------------------------------
# Evaluation: tree -> bool
# ---------------------------------------------------------------------------
def evaluate(node: Node) -> bool:
    """Evaluate a tree bottom-up, recursively.

    Each operator is applied to the already-evaluated values of its
    children, so the recursion does the ordering for us.
    """
    symbol = node.symbol

    if symbol == "0":
        return False
    if symbol == "1":
        return True

    if symbol == "!":
        return not evaluate(node.left)

    left = evaluate(node.left)
    right = evaluate(node.right)

    if symbol == "&":
        return left and right
    if symbol == "|":
        return left or right
    if symbol == "^":
        return left != right          # exclusive or: true when they differ
    if symbol == ">":
        return (not left) or right    # A => B  is  (not A) or B
    if symbol == "=":
        return left == right          # A <=> B is  A equals B

    raise ValueError(f"unknown operator '{symbol}'")


def eval_formula(formula: str) -> bool:
    """Evaluate a propositional formula given in Reverse Polish Notation."""
    return evaluate(parse(formula))


# ---------------------------------------------------------------------------
# Display helpers (not part of the required function)
# ---------------------------------------------------------------------------
def to_infix(node: Node) -> str:
    """Render a tree the way a human writes maths, for readability."""
    symbol = PRETTY[node.symbol]

    if node.is_leaf():
        return symbol
    if node.right is None:
        return f"{symbol}{to_infix(node.left)}"
    return f"({to_infix(node.left)} {symbol} {to_infix(node.right)})"


def render_tree(node: Node, prefix: str = "", is_last: bool = True,
                lines: list = None) -> list:
    """Draw the tree with box-drawing characters, root at the top."""
    if lines is None:
        lines = []
        lines.append(PRETTY[node.symbol])
    children = []
    if node.left is not None:
        children.append(node.left)
    if node.right is not None:
        children.append(node.right)

    for index, child in enumerate(children):
        last = index == len(children) - 1
        branch = "\u2514\u2500\u2500 " if last else "\u251c\u2500\u2500 "
        lines.append(f"{prefix}{branch}{PRETTY[child.symbol]}")
        extension = "    " if last else "\u2502   "
        render_tree(child, prefix + extension, last, lines)

    return lines


def trace(formula: str) -> bool:
    """Show parsing step by step, then the tree, then the evaluation."""
    print(f"  formula: {formula}\n")
    print("  [1] Parsing - one pass, left to right\n")
    print(f"      {'step':>4} | {'char':>4} | {'action':<28} | stack")
    print("      " + "-" * 74)

    stack = []
    for position, char in enumerate(formula):
        if char in CONSTANTS:
            stack.append(Node(char))
            action = f"push {PRETTY[char]}"
        elif char in UNARY_OPERATORS:
            operand = stack.pop()
            stack.append(Node(char, operand))
            action = "pop 1, push subtree"
        elif char in BINARY_OPERATORS:
            right = stack.pop()
            left = stack.pop()
            stack.append(Node(char, left, right))
            action = "pop 2, push subtree"
        else:
            raise ValueError(f"invalid character '{char}'")

        shown = " , ".join(to_infix(item) for item in stack)
        print(f"      {position:>4} | {char:>4} | {action:<28} | {shown}")

    root = stack[0]

    print("\n  [2] The tree\n")
    for line in render_tree(root):
        print("      " + line)

    print("\n  [3] Readable form\n")
    print("      " + to_infix(root))

    result = evaluate(root)
    print("\n  [4] Result\n")
    print(f"      {result}")
    return result


# ---------------------------------------------------------------------------
# Demo and CLI
# ---------------------------------------------------------------------------
def demo() -> None:
    print("Exercise 03 - Boolean evaluation"
          "   (pass a formula as an argument to test your own)\n")

    print("  The five examples from the subject:\n")
    print(f"      {'formula':<12} | {'readable':<22} | {'result':<6} | expected")
    print("      " + "-" * 62)
    subject_examples = [
        ("10&", False),
        ("10|", True),
        ("11>", True),
        ("10=", False),
        ("1011||=", True),
    ]
    for formula, expected in subject_examples:
        result = eval_formula(formula)
        mark = "ok" if result == expected else "MISMATCH"
        print(f"      {formula:<12} | {to_infix(parse(formula)):<22} | "
              f"{str(result):<6} | {str(expected):<5} {mark}")

    print("\n  Every operator, on every input combination:\n")
    print(f"      {'formula':<10} | {'readable':<18} | result")
    print("      " + "-" * 48)
    for op in "&|^>=":
        for a in "01":
            for b in "01":
                formula = a + b + op
                print(f"      {formula:<10} | "
                      f"{to_infix(parse(formula)):<18} | "
                      f"{eval_formula(formula)}")
        print()
    for a in "01":
        formula = a + "!"
        print(f"      {formula:<10} | {to_infix(parse(formula)):<18} | "
              f"{eval_formula(formula)}")

    print("\n  Invalid formulas are reported rather than silently guessed:\n")
    for bad in ["", "1&", "11", "1A&", "&"]:
        try:
            eval_formula(bad)
            print(f"      {bad!r:<10} -> no error (unexpected)")
        except ValueError as error:
            print(f"      {bad!r:<10} -> {error}")

    print("\n  Run  python3 eval_formula.py -t \"10|1&\"   to see the tree.")


def main() -> None:
    args = sys.argv[1:]

    show_trace = False
    if args and (args[0] == "-t" or args[0] == "--trace"):
        show_trace = True
        args = args[1:]

    if not args:
        if show_trace:
            print("usage: python3 eval_formula.py [-t] \"<formula>\"",
                  file=sys.stderr)
            sys.exit(1)
        demo()
        return

    if len(args) != 1:
        print("usage: python3 eval_formula.py [-t] \"<formula>\"",
              file=sys.stderr)
        print("hint: quote the formula, the shell treats | > & specially",
              file=sys.stderr)
        sys.exit(1)

    try:
        if show_trace:
            trace(args[0])
        else:
            print(eval_formula(args[0]))
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()