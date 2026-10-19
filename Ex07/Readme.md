# Exercise 07 — SAT

> **Goal:** write `sat(formula)` returning whether the formula is
> **satisfiable** — whether *some* assignment of its variables makes it true.
>
> **Allowed mathematical functions:** None
> **Required complexity:** O(2ⁿ) time, N/A space

---

## 0. Before you start

This is the **easiest exercise since Exercise 02**, and the one with the most
famous underlying problem. The code is short because everything it needs
already exists — the subject says so directly:

> *"You may use the functions you wrote from the previous exercises to help
> you."*

This file takes that literally. **Nothing is copied.** The parser, evaluator and
variable collector are *imported* from `../Ex06/`. See section 6 for how the
cross-folder import works.

The interesting part of this exercise isn't the algorithm — it's understanding
what satisfiability *is* and why it matters. Sections 1 and 7 are the ones worth
your attention.

---

## 1. What is satisfiability?

A formula is **satisfiable** if there is **at least one** assignment of its
variables that makes it true.

That's it. You are not asked whether it's *always* true, only whether it's
*ever* true.

| Formula | Satisfiable? | Why |
|---|---|---|
| `AB\|` | ✔ yes | A=0, B=1 makes it true |
| `AB&` | ✔ yes | A=1, B=1 makes it true |
| `AA!&` | ✘ no | A ∧ ¬A — nothing can make this true |
| `AA^` | ✘ no | A ⊕ A — a value can never differ from itself |

Those four are the subject's examples, and all four are reproduced by this
implementation.

### 1.1 The three categories

Satisfiability splits formulas into kinds you already met in Exercise 04:

| Kind | Truth table result column | Satisfiable? |
|---|---|---|
| **tautology** | all 1s | yes (every assignment works) |
| **contingent** | mixed | yes (some assignment works) |
| **contradiction** | all 0s | **no** |

So *unsatisfiable* and *contradiction* mean the same thing. A SAT solver that
says "no" has proved the formula is a contradiction.

### 1.2 The tautology trick

There's a neat relationship worth knowing, because an evaluator may ask:

> **A formula is a tautology exactly when its negation is unsatisfiable.**

If nothing can make `¬F` true, then nothing can make `F` false, so `F` is always
true. And negating a formula in RPN is trivial — just append `!`:

```python
def is_tautology(formula):
    return not sat(formula + "!")
```

One function gives you all three questions. That's implemented here and shown in
the demo.

### 1.3 Why SAT is famous

SAT is the problem of deciding satisfiability, and it has a special place in
computer science: it was the **first problem proved NP-complete** (Cook, 1971).
Informally, that means a fast general solution to SAT would give a fast solution
to an enormous family of problems — scheduling, routing, circuit verification,
puzzle solving — and nobody knows whether such a solution exists. That's the
P vs NP question.

In practice, modern SAT solvers routinely handle formulas with *millions* of
variables by being clever about which assignments they try. Brute force (what
this exercise asks for) tries them all.

**Where it's actually used:** hardware verification (does this circuit ever
produce a wrong output?), software dependency resolution (package managers
literally run SAT solvers to pick versions), scheduling, and automated theorem
proving.

### 1.4 Vocabulary

| Word | Meaning |
|---|---|
| **satisfiable** | True under at least one assignment. |
| **model** | A specific assignment that makes the formula true — the "witness". |
| **unsatisfiable** | True under no assignment; a contradiction. |
| **valid / tautology** | True under every assignment. |
| **NP-complete** | In the hardest class of problems whose answers are quick to *check*. |
| **decision problem** | A question with a yes/no answer — which is what SAT is. |

---

## 2. The algorithm

Brute force, which is exactly what the required O(2ⁿ) permits:

```
for each of the 2^n assignments:
    evaluate the formula
    if it is true:
        return True        <- stop immediately
return False               <- only after trying them all
```

This is the Exercise 04 loop with one change: instead of printing every row,
stop at the first row whose result is `1`.

### 2.1 Returning the witness, not just a bool

Rather than writing `sat` directly, this file builds it on `find_model`:

```python
def find_model(formula):
    """Return a satisfying assignment, or None."""
    ...
    return values   # or None

def sat(formula):
    return find_model(formula) is not None
```

Why bother? Because **a bare `True` is unverifiable**. If `find_model` returns
`A=0, B=0, C=1`, the claim can be checked instantly by plugging it in. During a
defense that's a much stronger demonstration than a lone `True`, and it costs
one extra line.

```bash
$ python3 sat.py -m "AB>C&"
True
  model: A=0, B=0, C=1
  contingent (sometimes true)
```

Verify by hand: `A ⇒ B` with A=0 is true (false premise), and C=1, so the
conjunction is true. ✓

### 2.2 Early exit

The `return` inside the loop matters. A satisfiable formula is often settled on
the very first assignment — `sat("AB|")` finds a model at `A=0, B=1`, the second
of four. Only **unsatisfiable** formulas pay the full 2ⁿ cost, because proving
"no" requires ruling out every possibility.

That asymmetry is fundamental to SAT and worth stating: **"yes" has a short
proof (the model); "no" does not.**

### 2.3 Formulas with no variables

`sat("1")` has zero variables, so the loop runs `2⁰ = 1` time with an empty
assignment. No special case needed — it falls out of the arithmetic.

---

## 3. Worked example

```bash
python3 sat.py -t "AA!&"
```

```
  formula: AA!&
  variables: A   ->  2 assignment(s) to try

      A   | result
      -----------
      0   | 0
      1   | 0

  all 2 assignments give false
  satisfiable: False
  classification: contradiction (never true)
```

Only one variable, so only two assignments, and `A ∧ ¬A` fails both. Compare
with a satisfiable one, where the search stops early:

```bash
python3 sat.py -t "AB|"
```

The trace marks the stopping point with `<- satisfiable, stop here`.

---

## 4. Complexity

The subject requires **O(2ⁿ)** where `n` is the number of distinct variables.

- The loop runs at most `2ⁿ` times.
- Each iteration evaluates the tree once: O(size of formula).
- **Total: O(2ⁿ)** ✓

Same reasoning as Exercise 04, and the same caveat: `n` is the **variable
count**, not the string length.

### 4.1 Is exponential really acceptable?

Yes — and this is worth being precise about, because it sounds like a cop-out.

Nobody knows a general algorithm for SAT that is better than exponential in the
worst case. That is precisely what NP-completeness means: finding one would
settle P vs NP. So an exponential algorithm here is not a failure to optimise,
it's the state of the art for the general case.

What real solvers do is prune: unit propagation, clause learning, backtracking
(the DPLL algorithm and its descendants). They are still exponential in the
worst case, but dramatically faster on the formulas that arise in practice. The
subject doesn't ask for any of that — O(2ⁿ) is the stated bound.

---

## 5. The CNF connection — why Exercise 06 comes first

Brute force doesn't need CNF at all. So why does the subject put CNF
immediately before SAT?

Because **CNF is the input format of every real SAT solver**, and the reason is
visible once you look at the shape:

> A CNF formula is an **AND of clauses**, so *every* clause must be true.
> Each clause is an **OR of literals**, so each needs only *one* true literal.

That turns satisfiability into a concrete search: **pick one literal from every
clause, without picking both `A` and `¬A`.** That's the structure DPLL and
modern solvers exploit.

The demo shows this view:

```
  Why Exercise 06 comes first - the CNF view of "AB>C&":

      CNF: A!B|C&
      model: A=0, B=0, C=1

      clause 1: (A! | B)  satisfied by A!
      clause 2: (C)  satisfied by C
```

Both clauses have at least one satisfied literal, so the whole formula holds.
This file reuses `conjunctive_normal_form` from Ex06 for that explanation,
though `sat` itself doesn't need it.

---

## 6. Reusing the previous exercises

Unlike Ex00–Ex06, **this folder imports rather than copies**. The exercise
folders are siblings:

```
ready-set-boole/
├── Ex06/conjunctive_normal_form.py
└── Ex07/sat.py          <- imports from ../Ex06/
```

They are not a Python package, so a plain `import` can't see across them. The
import block adds the sibling folder to the module search path:

```python
_HERE = os.path.dirname(os.path.abspath(__file__))
_EX06 = os.path.join(_HERE, os.pardir, "Ex06")

if _EX06 not in sys.path:
    sys.path.insert(0, _EX06)

from conjunctive_normal_form import (
    parse,                    # Exercise 03
    evaluate,                 # Exercise 04
    collect_variables,        # Exercise 04
    conjunctive_normal_form,  # Exercise 06
    flatten, to_rpn,          # Exercises 05 and 06
)
```

### 6.1 Why `__file__` and not the working directory

The path is built from `__file__` — this file's own location — **not** from
wherever the program happens to be started. That matters because an evaluator
might run it any of these ways:

```bash
cd Ex07 && python3 sat.py "AB|"            # works
python3 Ex07/sat.py "AB|"                  # works
python3 /full/path/to/Ex07/sat.py "AB|"    # works
```

All three are verified. Using a relative path like `"../Ex06"` without
`__file__` would only work from inside `Ex07`.

### 6.2 Why Ex06 and not several folders

`Ex06/conjunctive_normal_form.py` already contains the entire stack: the Ex03
parser, the Ex04 evaluator and variable collector, and the Ex05/Ex06 rewriters.
Importing from one place keeps a single `Node` class in play — mixing classes
from two modules would work by duck typing but is the kind of thing that causes
confusing bugs later.

### 6.3 The trade-off, stated honestly

Importing removes duplication, which is what you asked for and is better
engineering. The cost is that **Ex07 no longer runs standalone** — it needs
`Ex06/` present beside it. If someone copies a single folder out of the repo, it
breaks. The import block catches that and says so rather than failing with a
bare `ImportError`:

```
error: cannot import from .../Ex06
hint: Ex07 reuses Ex06; keep the exercise folders side by side
      inside ready-set-boole/
```

Since the whole repo is submitted together, this is the right trade.

---

## 7. How to run it

```bash
cd Ex07

python3 sat.py "AB|"      # -> True
python3 sat.py "AA!&"     # -> False
python3 sat.py "AA^"      # -> False
```

> **Quote your formulas** — `|`, `>`, `&` and `^` are shell metacharacters.

**No arguments** — the demo: the four subject examples, satisfiable formulas
with witness models, contradictions with explanations, the three-way
classification, the CNF view, and error cases.

**`-m`** — print a satisfying assignment and the classification alongside the
answer (on stderr, so piping still gives you just `True`/`False`).

**`-t`** — show the search assignment by assignment, with the early-exit point
marked.

### The subject's examples, all verified

| Call | Expected | Got |
|---|---|---|
| `sat("AB\|")` | true | True ✓ |
| `sat("AB&")` | true | True ✓ |
| `sat("AA!&")` | false | False ✓ |
| `sat("AA^")` | false | False ✓ |

### Verification performed

- All four subject examples match.
- Cross-checked against an independent full-truth-table reference on **9,018
  formulas** (every valid formula of length 1–6 over A, B, C) plus **2,000
  random formulas**.
- **Every returned model was plugged back in** and confirmed to satisfy its
  formula — a stronger check than comparing booleans.
- **SAT agrees on the CNF** of each formula, confirming the Ex06 rewriting
  preserves satisfiability.
- No formula was classified as both a tautology and a contradiction.

---

## 8. Common mistakes to avoid

| Mistake | What happens | Fix |
|---|---|---|
| Returning true only if **all** assignments work | That's validity, not satisfiability | **At least one** is enough |
| Forgetting to stop at the first success | Still correct, just wasteful | `return` inside the loop |
| Treating a contradiction as an error | `AA!&` is a perfectly valid formula | Return `False` |
| Counting duplicate variables twice | `AA!&` has **one** variable, 2 rows | Use distinct variables |
| Assuming CNF is required | Brute force is fine at O(2ⁿ) | CNF is the solver's shape, not a requirement |
| Building `is_tautology` as a separate search | Unnecessary | It's `not sat(formula + "!")` |
| Copying Ex04's code in again | Duplication | Import it (section 6) |

---

## 9. Do this on paper

1. **Decide by hand:** is `AB>A&B!&` satisfiable? Write the truth table and look
   for a single `1`. Check with `-t`.

2. **Explain the subject's examples:** why is `AA^` unsatisfiable? Say it in one
   sentence without using a truth table.

3. **Use the tautology trick:** take `AA!|` (A ∨ ¬A). Append `!` and convince
   yourself the result is unsatisfiable. What does that prove about the
   original?

4. **Find a model by hand** for `AB>C&`, then check it against the program's
   `-m` output. Yours may differ — any valid model is correct.

5. **Count the work:** for a formula with 5 distinct variables, how many
   assignments must be checked to prove it *unsatisfiable*? How many might be
   enough to prove it *satisfiable*? Explain the asymmetry.

6. **Clause view:** take the CNF `A!B|C&` and find an assignment satisfying both
   clauses by picking one literal from each. Confirm it matches section 5.

---

## 10. Peer-review preparation

- **"What does satisfiable mean?"** → At least one assignment makes the formula
  true. Not *all* — that's a tautology.
- **"How does your algorithm work?"** → Try all 2ⁿ assignments, return true at
  the first success; false only after exhausting them.
- **"Justify O(2ⁿ)."** → One iteration per assignment, 2ⁿ assignments, constant
  work per evaluation relative to the variable count.
- **"Isn't exponential bad?"** → For SAT it's the state of the art. SAT was the
  first NP-complete problem; a sub-exponential general algorithm would settle
  P vs NP.
- **"Show me it works."** → `-m` prints a witness assignment, which they can
  verify by hand. That's stronger than a bare `True`.
- **"Why is proving `False` more expensive?"** → "Yes" needs one example; "no"
  needs every possibility ruled out.
- **"How would you check for a tautology?"** → `not sat(formula + "!")`.
- **"Why did Exercise 06 come before this one?"** → CNF is the input format for
  real solvers: every clause must have a true literal, which turns SAT into a
  concrete search. Demo shows the clause view.
- **"Where did your parser come from?"** → Imported from Ex06, not copied — the
  subject says to reuse earlier functions.

---

## 11. What's next

**Exercise 08 (Powerset)** starts the set-theory block, and **Interlude 02
(Chapter XIII) comes first** — it covers naive set theory, Russell's paradox,
and the correspondence between logic and sets:

| Boolean algebra | Set theory |
|---|---|
| ¬A | complement |
| A ∨ B | union |
| A ∧ B | intersection |

That table is the key to Exercise 09, which is Exercise 03 again with sets
instead of booleans.

Exercise 08 itself is short and returns to bit manipulation: a set of `n`
elements has `2ⁿ` subsets, and you enumerate them with the same
integer-and-bitmask trick used for truth-table rows in Exercise 04.