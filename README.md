# Ready, Set, Boole!

**An introduction to Boolean Algebra** — 42 / 1337 School.
Implemented in **Python 3**. Exercises **00 to 09** (the mandatory set).

---

## Contents

1. [What this project is](#1-what-this-project-is)
2. [Repository layout](#2-repository-layout)
3. [Quick start](#3-quick-start)
4. [The ten exercises](#4-the-ten-exercises)
5. [Complexity table](#5-complexity-table-graded-at-peer-review)
6. [How the code is organised](#6-how-the-code-is-organised)
7. [Ideas that recur across exercises](#7-ideas-that-recur-across-exercises)
8. [Testing and verification](#8-testing-and-verification)
9. [Defense preparation](#9-defense-preparation)
10. [Notes on Python](#10-notes-on-python)

---

## 1. What this project is

Ten exercises that build up from manipulating individual bits to evaluating
logical formulas and set expressions. The arc is:

```
Ex00 – Ex02   bit manipulation        add, multiply and re-encode numbers
                                      using only bitwise operators

Ex03 – Ex07   propositional logic     parse, evaluate, rewrite and solve
                                      boolean formulas

Ex08 – Ex09   set theory              the same logic, applied to sets
```

The connecting idea — stated in the subject's Interlude 02 — is that **Boolean
algebra and set theory are the same structure wearing different symbols**:

| Boolean | Set |
|---|---|
| ¬A | complement |
| A ∨ B | union |
| A ∧ B | intersection |

Exercise 09 is Exercise 03 with that table applied, which is the point the
whole module is building toward.

**Exercises 10 and 11 (Curve, Inverse function) are not implemented.** The
subject marks them as not mandatory; this repository covers the required
Ex00–Ex09.

---

## 2. Repository layout

```
ready-set-boole/
├── README.md                   ← you are here
├── Ex00/  adder.py                   + README.md
├── Ex01/  multiplier.py              + README.md
├── Ex02/  gray_code.py               + README.md
├── Ex03/  eval_formula.py            + README.md
├── Ex04/  print_truth_table.py       + README.md
├── Ex05/  negation_normal_form.py    + README.md
├── Ex06/  conjunctive_normal_form.py + README.md
├── Ex07/  sat.py                     + README.md
├── Ex08/  powerset.py                + README.md
└── Ex09/  eval_set.py                + README.md
```

**Every folder has its own README** with the full beginner-level explanation:
the concept, a worked example done by hand, the algorithm, the complexity
argument, common mistakes, paper exercises, and a defense cheat-sheet. This
file is the map; those are the territory.

---

## 3. Quick start

Each exercise runs from the command line and takes its input as arguments:

```bash
python3 Ex00/adder.py 5 3                        # 8
python3 Ex01/multiplier.py 13 11                 # 143
python3 Ex02/gray_code.py 8                      # 12
python3 Ex03/eval_formula.py "1011||="           # True
python3 Ex04/print_truth_table.py "AB&C|"        # the truth table
python3 Ex05/negation_normal_form.py "AB&!"      # A!B!|
python3 Ex06/conjunctive_normal_form.py "ABCD&|&" # ABC|BD|&&
python3 Ex07/sat.py "AB|"                        # True
python3 Ex08/powerset.py 1 2 3                   # all 8 subsets
python3 Ex09/eval_set.py "AB&" 0,1,2 0,3,4       # [0]
```

Run any file **with no arguments** to get a demonstration that includes the
subject's own examples with their expected values.

> ### Quote your formulas
>
> `|`, `>`, `&` and `^` are shell metacharacters. Unquoted,
> `python3 Ex03/eval_formula.py 10|` will hang or create a file instead of
> running. Always wrap formulas in `"..."`.
>
> This is the single most common confusion during a defense — mention it
> before handing over the keyboard.

### Common flags

Most exercises support:

| Flag | Meaning |
|---|---|
| `-t` | **trace** — show the algorithm step by step |
| `-v` | **verify** — print correctness checks alongside the result |

`-t` is the one to use during a defense when asked *"show me how it works"*.
For example:

```bash
python3 Ex00/adder.py -t 13 11          # the carry loop, iteration by iteration
python3 Ex03/eval_formula.py -t "101|&" # parsing, the AST, and evaluation
python3 Ex06/conjunctive_normal_form.py -t "ABCD&|&"  # all four rewrite stages
python3 Ex09/eval_set.py -t "AB&" 0,1,2 0,3,4         # the set stack machine
```

---

## 4. The ten exercises

### Ex00 — Adder

Add two numbers using only `&`, `|`, `^`, `<<`, `>>`.

School-style column addition, in binary. XOR gives the sum of each column
ignoring carries; AND marks where carries occur; shifting left by one puts each
carry in the right column. Repeat until no carry remains.

```
a ^ b          sum without carrying
(a & b) << 1   the carries, moved one column left
```

### Ex01 — Multiplier

Multiply using the same operator set, reusing the adder.

`b` written in binary is already a sum of powers of two (`11 = 1011 = 8+2+1`),
and shifting left multiplies by two. So walk the bits of `b` and add the
matching shifted copy of `a` wherever a bit is 1 — binary long multiplication.

### Ex02 — Gray code

Convert `n` to the ordering where consecutive values differ by exactly one bit.

```python
return n ^ (n >> 1)
```

One expression. Each Gray bit says whether two neighbouring bits of `n` differ;
shifting right lines each bit up with its neighbour, and XOR compares every
position at once.

### Ex03 — Boolean evaluation

Evaluate an RPN formula such as `"1011||="`.

**This is the architectural pivot of the module.** Rather than evaluating the
string directly, it builds a binary **Abstract Syntax Tree**, as the subject's
lightbulb box recommends. Ex04, Ex05, Ex06, Ex07 and Ex09 all depend on that
tree — Ex05 and Ex06 *rewrite* formulas, which is local surgery on a tree and
painful text-splicing on a string.

### Ex04 — Truth table

Print the result for every combination of the variables' values.

The output format is specified byte-exactly by the subject (shown through
`cat -e` to prove there is no trailing whitespace). This implementation matches
it **character for character** — same MD5 as the subject's text.

### Ex05 — Negation Normal Form

Rewrite so every `!` sits directly on a variable, using only `!`, `&`, `|`.

Two passes: eliminate `>`, `=`, `^` using their identities; then push negations
inward with De Morgan. The second pass carries a `negated` flag rather than
rewriting in place, which makes double negation cancel for free.

### Ex06 — Conjunctive Normal Form

Rewrite as an AND of ORs — NNF plus distributivity.

The subtle requirement is on the **output shape**: *"every conjunction must be
located at the end of the formula"*. So `AB&C&D&` must come back as `ABCD&&&`,
even though the input is already valid CNF. That needs a deliberate flattening
step, not just a tree walk.

### Ex07 — SAT

Decide whether any assignment makes the formula true.

Brute force over all 2ⁿ assignments, stopping at the first success. Built on a
`find_model` that returns the satisfying assignment, so `-m` gives a witness an
evaluator can check by hand instead of a bare `True`.

### Ex08 — Powerset

Return every subset of a set.

A subset is n independent in/out decisions, which is exactly what an n-bit
number encodes — so count from 0 to 2ⁿ−1 and read each number's bits.

### Ex09 — Set evaluation

Evaluate an RPN formula whose variables are **sets**.

Structurally identical to Ex03; only the operations change. The one thing to
get right is the subject's red box: **the universe is the union of all the
input sets**, which is why `eval_set("A!", [[0,1,2]])` correctly returns `[]`.

---

## 5. Complexity table (graded at peer review)

Taken from the subject's own boxes. The subject states these *"will be checked
during peer review"*, so they are the one criterion you can fail with otherwise
correct code.

| Ex | Name | Time | Space | Prototype |
|---|---|---|---|---|
| 00 | Adder | **O(log n)** | **O(log n)** | `adder(a: u32, b: u32) -> u32` |
| 01 | Multiplier | **O(1)** | **O(1)** | `multiplier(a: u32, b: u32) -> u32` |
| 02 | Gray code | N/A | N/A | `gray_code(n: u32) -> u32` |
| 03 | Boolean evaluation | **O(n)** | N/A | `eval_formula(formula) -> bool` |
| 04 | Truth table | **O(2ⁿ)** | N/A | `print_truth_table(formula)` |
| 05 | NNF | N/A | N/A | `negation_normal_form(formula) -> String` |
| 06 | CNF | N/A | N/A | `conjunctive_normal_form(formula) -> String` |
| 07 | SAT | **O(2ⁿ)** | N/A | `sat(formula) -> bool` |
| 08 | Powerset | N/A | **O(2ⁿ)** | `powerset(set) -> Vec<Vec<i32>>` |
| 09 | Set evaluation | N/A | N/A | `eval_set(formula, sets) -> Vec<i32>` |

### What "checked during peer review" actually means

There is **no automated tool**. The evaluator reads your code, counts the
loops, and asks you about them. Three things happen:

1. **They read the structure.** How many times can this loop run, as a function
   of the input? A loop driven by the input's *value* instead of its *bits* is
   the classic failure — it produces correct answers and still fails.
2. **They ask you to explain it out loud.**
3. **They may ask for a demonstration** — which is what `-t` is for.

### `n` means something different in almost every exercise

This is the most common source of a wrong justification:

| Exercise | `n` is |
|---|---|
| Ex00, Ex01 | the **value** of the number |
| Ex03 | the **length of the formula string** |
| Ex04, Ex07 | the **number of distinct variables** |
| Ex08 | the **number of elements in the set** |

Always check which one before quoting a bound.

### Why O(2ⁿ) is required in Ex04/Ex07/Ex08 but would fail Ex01

Because in those exercises the **output itself** has 2ⁿ parts — 2ⁿ truth-table
rows, 2ⁿ subsets. You cannot produce 2ⁿ things in fewer than 2ⁿ steps, so the
bound is forced by the problem, not chosen by the algorithm. It is a lower
bound as much as an upper one.

---

## 6. How the code is organised

### The shared AST

Exercises 03 through 09 all work on the same structure:

```python
class Node:
    def __init__(self, symbol, left=None, right=None):
        self.symbol = symbol
        self.left   = left
        self.right  = right
```

A node is a **leaf** (a variable or constant), a **unary** operator (`!`, using
`left` only), or a **binary** operator (`&|^>=`, using both children).

Parsing is one left-to-right pass with a stack: push operands, and on an
operator pop what it needs and push the resulting subtree. That is all RPN
requires — no parentheses, no precedence rules.

### Reuse between exercises

The subject repeatedly says *"you may use the functions you wrote during the
previous exercise"*. Where an exercise genuinely needs earlier code, it
**imports** rather than copies:

```
Ex05  ──▶  Ex06  ──▶  Ex07
  │
  └─────▶  Ex09
```

| Folder | Imports from | What it needs |
|---|---|---|
| Ex00, Ex01, Ex02 | — | nothing; pure bit manipulation |
| Ex03, Ex04 | — | they define the parser and evaluator |
| Ex05 | — | carries its own copy of the parser |
| **Ex06** | **Ex05** | parser + the NNF rewriters |
| **Ex07** | **Ex06** | parser + evaluator |
| **Ex09** | **Ex05** | parser only (no rewriting needed) |

The import resolves the sibling folder from `__file__`, not the working
directory, so every file runs correctly from the repo root, from inside its own
folder, or by absolute path:

```python
_HERE = os.path.dirname(os.path.abspath(__file__))
_EX05 = os.path.join(_HERE, os.pardir, "Ex05")
if _EX05 not in sys.path:
    sys.path.insert(0, _EX05)
```

**Trade-off:** Ex06, Ex07 and Ex09 need their sibling present and no longer run
in isolation. Each catches a missing sibling and says so plainly instead of
failing with a bare `ImportError`. Since the repository is submitted whole,
that is the right trade.

### One deliberate exception

`to_rpn`, `evaluate` and `flatten` exist in **both** Ex05 and Ex06, and this is
intentional rather than sloppy. Ex05's versions are recursive; Ex06's are
iterative, because distribution can produce a CNF with thousands of clauses on
one `&` chain and a recursive walk exceeds Python's 1000-frame limit. Measured:

```
AB&CD&|EF&|GH&|IJ&|KL&|MN&|OP&|QR&|ST&|     ← 39 characters
```

produces **1,024 clauses**, where the recursive version raises `RecursionError`
and the iterative one does not. The comment in `Ex06/conjunctive_normal_form.py`
says so; Ex06's README section 6.1 has the full table.

---

## 7. Ideas that recur across exercises

### The bit-mask enumeration, three times

The same trick enumerates "all combinations of n independent binary choices":

| Exercise | What the bits select |
|---|---|
| Ex01 Multiplier | which shifted copies of `a` to add |
| Ex04 Truth table | which variables are true in this row |
| Ex08 Powerset | which elements are in this subset |

### Rewrite rules (Interlude 00)

Implemented in Ex05 and Ex06, and verifiable with Ex04's truth tables:

```
¬¬A        ⇔  A                         double negation
A ⇒ B      ⇔  ¬A ∨ B                    material condition
A ⇔ B      ⇔  (A ⇒ B) ∧ (B ⇒ A)         equivalence
¬(A ∧ B)   ⇔  ¬A ∨ ¬B                   De Morgan
¬(A ∨ B)   ⇔  ¬A ∧ ¬B                   De Morgan
A ∨ (B ∧ C) ⇔ (A ∨ B) ∧ (A ∨ C)         distributivity
```

The subject's red box flags that **distributivity goes both ways here**, unlike
arithmetic where `a + (b × c) ≠ (a+b) × (a+c)`. Don't let arithmetic intuition
tell you the rule is invalid.

### Gray code reappears

Karnaugh maps — the optional CNF simplification mentioned in Ex06 — label their
rows and columns in **Gray code order**, so that adjacent cells differ in one
variable and can be merged. That is why Ex02 exists where it does.

### The logic ↔ set bridge

Ex09's correctness rests on one property, which is also the cleanest way to
explain the whole module's arc:

> An element `x` is in the resulting set **exactly when** the same formula is
> true with each variable replaced by *"is `x` a member of this set?"*

Every set formula is a boolean formula evaluated once per element.

---

## 8. Testing and verification

Every exercise was checked against the subject's own examples **and** against
an independent implementation or mathematical property — not just eyeballed.

| Ex | How it was verified |
|---|---|
| 00 | Exhaustive: all 65,536 pairs in 0..255; 100,000 random full-range u32 pairs |
| 01 | Exhaustive 0..255; 200,000 random u32 pairs; overflow cases |
| 02 | All 9 subject examples; one-bit property verified for all n in 0..65535; bijectivity |
| 03 | 5/5 subject examples; cross-checked against an independent stack evaluator on 19,114 formulas |
| 04 | Byte-exact format match (same MD5 as the subject); values cross-checked on 9,018 + 3,000 formulas |
| 05 | 5/5 subject examples; NNF + allowed-symbols + identical truth table on 9,018 + 4,000 formulas; idempotence |
| 06 | 7/7 subject examples + the worked one; five properties on 9,018 + 1,200 formulas; idempotence |
| 07 | 4/4 subject examples; cross-checked against truth tables on 9,018 + 2,000 formulas; every returned model re-verified |
| 08 | Cardinality, completeness vs `itertools`, distinctness, containment — sizes 0..12 and 400 random sets |
| 09 | 3/3 subject examples; membership property on 14,000 + 2,666 formula/set pairs; 10 classic set identities |

Where several answers are valid (Ex05, Ex06), correctness is checked by
**comparing truth tables**, not by string comparison — the subject explicitly
allows multiple valid outputs.

### Invalid input

The subject calls invalid input undefined behaviour but *encourages* an error
message. Every formula-based exercise names three distinct failure modes:

```
''      → empty formula
'1&'    → '&' at position 1 needs 2 operands, but only 1 available
'11'    → formula is incomplete: 2 values left on the stack
'1A&'   → invalid character 'A' at position 1
```

---

## 9. Defense preparation

### Run this first

```bash
cd ready-set-boole
python3 Ex00/adder.py 5 3 && python3 Ex01/multiplier.py 13 11 && \
python3 Ex02/gray_code.py 8 && python3 Ex03/eval_formula.py "1011||=" && \
python3 Ex05/negation_normal_form.py "AB&!" && \
python3 Ex06/conjunctive_normal_form.py "ABCD&|&" && \
python3 Ex07/sat.py "AB|" && python3 Ex09/eval_set.py "AB&" 0,1,2 0,3,4
```

Expected: `8`, `143`, `12`, `True`, `A!B!|`, `ABC|BD|&&`, `True`, `[0]`.

Do the same from **inside** each folder, to confirm the imports resolve both
ways.

### Questions that come up most

**"Why is `4294967295 + 1` zero?"**
Correct u32 wraparound. Python integers are unbounded, so `& 0xFFFFFFFF`
reproduces what the hardware does.

**"Why is Ex00 O(log n) but Ex01 O(1) with the same loop shape?"**
Two phrasings of one bound: in terms of the input *value* it is O(log n); for a
fixed-width 32-bit type it is O(1). What matters in both is that the loop is
driven by **bits**, never by the value.

**"Why is `⊥ ⇒ ⊤` true?"**
An implication is a promise, broken only when the premise holds and the
conclusion fails. Nothing on a sunny day can break a promise about rainy days.
Equivalently `A ⇒ B` is `¬A ∨ B`.

**"Show me operand order matters."**
`10>` is false, `01>` is true. The other operators are commutative, so a
reversed pop would hide the bug everywhere except `>`.

**"Why did you build a tree in Ex03?"**
The subject suggests it, and Ex05/Ex06 must *rewrite* formulas. De Morgan on a
tree is a local node swap; on a string it means scanning backwards counting
operands to find sub-formula boundaries.

**"Why doesn't `AB&C&D&` come back unchanged in Ex06?"**
It is already logically CNF, but the required *shape* puts every `&` at the
end, so it must be `ABCD&&&`. Associativity makes that legal.

**"Why does `A!` return an empty list in Ex09?"**
With one input set, that set *is* the universe, so nothing lies outside it. Add
a second set and the universe grows, and the answer changes.

**"How do you know the rewrites are correct?"**
Identical truth tables — Ex04 used as a verification tool, not just as an
exercise.

### Paper work

The subject recommends working on paper, and every per-exercise README ends
with a **"Do this on paper"** section. The two most worthwhile:

- **Ex00 §9** — trace `adder(13, 11)` by hand and check against `-t`.
- **Ex04 §9** — build the tables for `AB>` vs `A!B|`, and `AB&!` vs `A!B!|`.
  Identical result columns; those are the two rules Ex05 implements.

---

## 10. Notes on Python

### The 32-bit mask

Exercises 00–02 specify `u32`. Rust and C++ enforce that; **Python integers are
unbounded and never overflow**, so the limit is enforced manually:

```python
MASK_32 = 0xFFFFFFFF          # 32 ones
value & MASK_32               # keep only the lowest 32 bits
```

`&` is an allowed operator, so this is legal. Without it,
`adder(4294967295, 1)` would return `4294967296` — not a valid u32 at all.

### Operator precedence — Python is the safe one here

Worth knowing precisely, because it differs from C and it is easy to state
backwards.

In **Python**, bitwise `&` binds **tighter** than `==`:

```python
b & 1 == 1        # parses as  (b & 1) == 1     ← correct
```

In **C and C++** it is the reverse — `==` binds tighter than `&`:

```c
b & 1 == 1        /* parses as  b & (1 == 1)    ← the classic bug */
```

So this code is safe in Python but would be a bug in a C port of the same
exercise. The explicit form is unambiguous in both languages, which is what
this repository uses:

```python
(b & 1) != 0
```

### Recursion limit

Python's default is 1000 frames. Ex06 can build trees deeper than that, so its
tree walks are iterative (section 6).

### Broken pipe

Every executable catches `BrokenPipeError`, so piping into `head` exits cleanly
instead of printing a traceback that looks like a crash:

```bash
python3 Ex04/print_truth_table.py "ABCD^^^" | head -5
```

### Requirements

Python 3.6+ (f-strings). No third-party packages, no `import math` — the
subject allows no mathematical functions, and none are used.

---

## Status

**Ex00 – Ex09 complete.** Ex10 and Ex11 are marked not mandatory in the subject
and are not implemented.