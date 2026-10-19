# Exercise 06 — Conjunctive Normal Form

> **Goal:** write `conjunctive_normal_form(formula)` returning an equivalent
> formula where **every negation is on a variable** and **every conjunction is
> at the end of the formula**.
>
> **Allowed mathematical functions:** None
> **Required complexity:** N/A time, N/A space
> **Output constraint:** only variables and `!`, `&`, `|`

---

## 0. Before you start

The subject's lightbulb box says it plainly:

> *"You may use the function you wrote during the previous exercise to help
> you."*

That's not a hint, it's the design. **CNF = NNF + one more step.** This file
contains Exercise 05 verbatim (eliminate `>`/`=`/`^`, then push negations), and
adds distribution on top.

There is one requirement here that is easy to miss and that catches people out —
**"every conjunction must be located at the end of the formula"**. That is a
constraint on the *output string*, not just on the logic, and satisfying it
needs a deliberate serialisation step. Section 4 is the one to read carefully.

---

## 1. What is Conjunctive Normal Form?

A formula is in **CNF** when it is an **AND of ORs of literals**:

```
(literal ∨ literal ∨ …) ∧ (literal ∨ literal ∨ …) ∧ …
```

Recall from Exercise 05 that a **literal** is a variable or a negated variable
(`A` or `¬A`). Each bracketed group is called a **clause**.

So CNF has three layers, and they may never be out of order:

| Layer | Contains |
|---|---|
| top | `∧` only |
| middle | `∨` only |
| bottom | literals |

An `∧` is never allowed *inside* an `∨`. That's the whole restriction.

### 1.1 Examples

| Formula | CNF? | Why |
|---|---|---|
| `(A ∨ B) ∧ C` | ✔ | AND of two clauses |
| `A ∨ (B ∧ C)` | ✘ | an AND sits inside an OR |
| `¬A ∨ ¬B` | ✔ | a single clause is still CNF |
| `A` | ✔ | a single literal is a clause of one |
| `¬(A ∧ B)` | ✘ | not even NNF |

### 1.2 Why CNF matters

**It's the input format for SAT solvers.** Exercise 07 asks whether a formula
can be made true. In CNF that question becomes beautifully simple: the whole
formula is an AND, so **every clause must be satisfied**, and a clause is an OR,
so **at least one literal in it must be true**. Essentially every real SAT
solver in the world takes CNF as input for exactly this reason.

**It's how logic becomes circuits.** An AND of ORs maps directly onto a
two-layer gate network. The subject's info box mentions Karnaugh maps for
simplifying CNF — that's the electronics-design connection (see section 8.2).

### 1.3 Vocabulary

| Word | Meaning |
|---|---|
| **literal** | A variable or a negated variable: `A`, `¬A`. |
| **clause** | An OR of literals. |
| **CNF** | An AND of clauses. |
| **DNF** | The mirror image — an OR of ANDs. Not required here. |
| **associative** | `(a∧b)∧c` = `a∧(b∧c)`, so the bracketing carries no meaning. |
| **distribute** | Push an operator inside another, as in `a×(b+c) = a×b + a×c`. |

---

## 2. Distributivity — the one new rule

Everything else comes from Exercise 05. The new tool is Interlude 00, VIII.5:

```
A ∨ (B ∧ C)   ⇔   (A ∨ B) ∧ (A ∨ C)
A ∧ (B ∨ C)   ⇔   (A ∧ B) ∨ (A ∧ C)
```

For CNF we only need the **first** one — it is what moves an `∧` *upward* past
an `∨`, which is precisely the illegal arrangement from section 1.

### 2.1 The arithmetic analogy, and where it breaks

In ordinary arithmetic you know:

```
a × (b + c)  =  a×b + a×c
```

Logical distributivity works the same way with `∧` playing `×` and `∨` playing
`+`. But the subject's red warning box flags the crucial difference:

> *"Watch out, unlike the one-way distributivity for × over +, this one goes
> both ways!"*

In arithmetic, `a + (b × c)` is **not** `(a+b) × (a+c)`. In Boolean algebra the
matching law **does** hold:

```
A ∨ (B ∧ C)  =  (A ∨ B) ∧ (A ∨ C)       ← no arithmetic equivalent
```

So don't let arithmetic intuition tell you this rule is invalid. Check it with a
truth table if it feels wrong — that's paper exercise 1.

### 2.2 Both sides

The rule also applies when the AND is on the left:

```
(A ∧ B) ∨ C   ⇔   (A ∨ C) ∧ (B ∨ C)
```

An implementation must handle both, since an OR can meet an AND from either
direction.

### 2.3 Where the size growth comes from

Look closely at what distribution does to the *other* operand:

```
A ∨ (B ∧ C)   ->   (A ∨ B) ∧ (A ∨ C)
^                    ^        ^
A appears once       A now appears twice
```

`A` is **duplicated**. If `A` is a large sub-formula, the whole thing is copied.
Do this repeatedly and the formula explodes — which is exactly what the subject
warns about:

> *"The size of the output formula may grow exponentially with the size of the
> input. There exist an algorithm to avoid this but it isn't required to use
> it."*

Section 6 has measurements. (The algorithm being alluded to is the **Tseytin
transformation**, which keeps the size linear by inventing new variables — but
it produces a formula that is only *equisatisfiable*, not equivalent, so it
would break the truth-table test. Not required, and not used here.)

---

## 3. The algorithm — four stages

```
stage 1   eliminate  >  =  ^              (Exercise 05, pass 1)
stage 2   push negations onto variables   (Exercise 05, pass 2)  -> NNF
stage 3   distribute | over &                                    -> CNF tree
stage 4   flatten and serialise                                  -> output string
```

Stages 1 and 2 are Exercise 05 unchanged. Stage 3 is distribution. **Stage 4 is
the part people forget** — see section 4.

### 3.1 Stage 3 in code

```python
def distribute(left, right):           # builds the CNF of (left | right)
    if left.symbol == "&":             # (L1 & L2) | R  ->  (L1|R) & (L2|R)
        return Node("&", distribute(left.left,  right),
                         distribute(left.right, copy_tree(right)))
    if right.symbol == "&":            # L | (R1 & R2)  ->  (L|R1) & (L|R2)
        return Node("&", distribute(left,            right.left),
                         distribute(copy_tree(left), right.right))
    return Node("|", left, right)      # neither side is an AND: a valid clause

def to_cnf_tree(node):
    if leaf or literal:  return a copy
    left  = to_cnf_tree(node.left)     # convert children FIRST
    right = to_cnf_tree(node.right)
    if node.symbol == "&":  return Node("&", left, right)
    if node.symbol == "|":  return distribute(left, right)
```

**Why children first?** By the time `distribute` is called, both operands are
already ANDs-of-ORs. That means `distribute` only ever has to handle one shape —
an `&` at the top of one side or the other — and it recurses until neither side
has one. Converting bottom-up is what keeps the function short.

Note `copy_tree` on the duplicated side. The two copies must be independent
objects; sharing would be a latent bug the moment anything edits a node.

---

## 4. Stage 4 — the output shape (don't skip this)

The subject requires that **every conjunction be at the end of the formula**.
Look at what that demands:

```
conjunctive_normal_form("AB&C&D&")   ->   ABCD&&&
```

The input `AB&C&D&` is *already* a perfectly good CNF — it's `A ∧ B ∧ C ∧ D`,
three clauses of one literal each. But the expected output is **not** the input.
The `&` symbols have been gathered to the end.

A plain post-order traversal of that tree produces `AB&C&D&` — operators
interleaved with operands. **That fails the requirement.** Same for OR:

```
conjunctive_normal_form("AB|C|D|")   ->   ABCD|||
```

### 4.1 Why this is allowed

AND and OR are **associative**: `(A ∧ B) ∧ C` and `A ∧ (B ∧ C)` are the same
formula, so the tree's bracketing carries no real information. A chain of `&` is
really one n-ary AND over a flat list of clauses, and we are free to print it
whichever way we like.

### 4.2 How to do it

**Flatten, then emit all operands before all operators:**

```
clause₁ clause₂ … clauseₙ & & … &          (n−1 ampersands)
```

and inside each clause, the same trick with `|`:

```
literal₁ literal₂ … literalₖ | | … |       (k−1 pipes)
```

```python
def serialise_cnf(root):
    clauses = flatten(root, "&")              # [c1, c2, ...]
    pieces = []
    for clause in clauses:
        literals = flatten(clause, "|")       # [l1, l2, ...]
        pieces.append("".join(to_rpn(l) for l in literals)
                      + "|" * (len(literals) - 1))
    return "".join(pieces) + "&" * (len(clauses) - 1)
```

Check it against the subject's example `ABCD&|&` → `ABC|BD|&&`:

- clauses: `A`, `(B∨C)`, `(B∨D)`
- serialised: `A` + `BC|` + `BD|` + `&&` = **`ABC|BD|&&`** ✓

Verify the RPN actually parses back to the right thing: `A`, `BC|`, `BD|` are
pushed, then the first `&` combines the last two into `(B∨C)∧(B∨D)`, and the
second `&` combines that with `A`. Correct.

---

## 5. Worked example: `ABCD&|&`

This is the example from the subject's instructions: `A ∧ (B ∨ (C ∧ D))`.

**Stages 1 and 2:** nothing to do — no `>`, `=`, `^`, no negations.

**Stage 3:** the `∨` has an `∧` on its right, so distribute:

```
B ∨ (C ∧ D)   ->   (B ∨ C) ∧ (B ∨ D)
```

giving `A ∧ ((B ∨ C) ∧ (B ∨ D))`.

**Stage 4:** flatten the `&` chain into three clauses, then serialise.

```bash
python3 conjunctive_normal_form.py -t "ABCD&|&"
```

```
  [3] After distributing  |  over  &
      (A ∧ ((B ∨ C) ∧ (B ∨ D)))

  [4] Clauses
      clause 1: (A)
      clause 2: (B ∨ C)
      clause 3: (B ∨ D)

  [5] Flattened output   (operands first, then all the operators)
      ABC|BD|&&

  [6] Checks
      is CNF                  : True
      negations on variables  : True
      conjunctions at end     : True
      only ! & | used         : True
      same truth table        : True
```

Result `ABC|BD|&&` — exactly the subject's expected output. ✓

---

## 6. The size explosion, measured

Distribution duplicates operands, and eliminating `=`/`^` already duplicated
them once in Exercise 05. Together the growth is dramatic:

| input | length | output length | clauses |
|---|---|---|---|
| `AB&C\|` | 5 | 7 | 2 |
| `AB&CD&\|` | 7 | 15 | 4 |
| `AB&CD&\|EF&\|` | 11 | 47 | 8 |
| `AB=` | 3 | 19 | 4 |
| `AB=C=` | 5 | 130 | 15 |
| `AB=C=D=` | 7 | **1,682** | **112** |

Seven characters in, 1,682 out. Add one more `E=` and it runs to hundreds of
thousands. This is why the subject sets complexity to **N/A** and says an
avoidance algorithm exists but isn't required.

### 6.1 A consequence worth knowing about

With 112 clauses, the output tree has a chain of 111 `&` nodes. A **recursive**
walk down that chain uses 111 stack frames — fine. But nest one level deeper and
the chain runs to thousands, and Python's default limit is **1000 frames**. A
recursive tree walk raises `RecursionError` and the program appears to crash.

I hit this while testing, so the functions that walk the *output* tree —
`to_rpn`, `flatten`, `evaluate`, and the structural checkers — are written
**iteratively**, with an explicit stack instead of recursion:

```python
def to_rpn(node):
    output, stack = [], [(node, False)]
    while stack:
        current, children_done = stack.pop()
        if children_done or current.is_leaf():
            output.append(current.symbol)
            continue
        stack.append((current, True))          # emit the operator later
        if current.right is not None:
            stack.append((current.right, False))
        stack.append((current.left, False))
    return "".join(output)
```

The `(node, children_done)` pair is the standard trick: the first visit
schedules the children, the second emits the operator. That *is* post-order, and
post-order is RPN.

This matters in practice: `AB=C=D=` is only seven characters, and an evaluator
could plausibly type something like it.

---

## 7. Checking your own work

As in Exercise 05, several valid answers exist, so string comparison isn't a
general test. **Five properties** must hold:

1. **It is CNF** — an AND of ORs of literals, no AND inside an OR.
2. **Negations are on variables** — inherited from NNF.
3. **Conjunctions are at the end** — every `&` forms one unbroken suffix.
4. **Only `!`, `&`, `|`** appear.
5. **Same truth table** as the input.

`-v` reports all five:

```bash
$ python3 conjunctive_normal_form.py -v "AB>C&"
A!B|C&
  is CNF                  : True
  negations on variables  : True
  conjunctions at end     : True
  only ! & | used         : True
  same truth table        : True
```

### Verification performed

- All **seven subject examples** reproduced character for character.
- The **worked example** from the instructions (`ABCD&|&` → `ABC|BD|&&`) matches.
- All five properties verified on **9,018 formulas** (every valid formula of
  length 1–6 over A, B, C) plus **1,200 random deeper formulas**.
- **Idempotence** on 610 formulas: CNF of a CNF is unchanged.

---

## 8. Notes on the output quality

### 8.1 Redundant clauses

This implementation does no simplification, so some outputs contain obviously
useless clauses:

```
$ python3 conjunctive_normal_form.py "AB="
AA!|AB!|BA!|BB!|&&&
```

That reads `(A ∨ ¬A) ∧ (A ∨ ¬B) ∧ (B ∨ ¬A) ∧ (B ∨ ¬B)`. The first and last
clauses are **tautologies** — always true — so they contribute nothing. The
formula is still *correct*: dropping them leaves `(A ∨ ¬B) ∧ (¬A ∨ B)`, which is
exactly `A ⇔ B`.

The subject permits this: *"There may be several valid results, only one is
required."* Be ready to explain why a clause like `A ∨ ¬A` is harmless.

### 8.2 Karnaugh maps (optional)

The subject's blue box notes that CNF can be simplified using a **Karnaugh
map**, and that this is "noteworthy for those interested in the design of
logical electronic circuits" — fewer clauses means fewer gates.

A K-map is a grid of a formula's truth table whose rows and columns are labelled
in **Gray code order** — which is exactly why Exercise 02 exists. Adjacent cells
differ in one variable, so a block of adjacent true cells can be merged into a
single simpler term.

Implementing it is explicitly optional (*"If you wish"*) and this file does not.
Mention the Gray code connection if it comes up — it's a nice thread between
exercises.

---

## 9. How to run it

```bash
cd Ex06

python3 conjunctive_normal_form.py "ABCD&|&"    # -> ABC|BD|&&
python3 conjunctive_normal_form.py "AB&C&D&"    # -> ABCD&&&
python3 conjunctive_normal_form.py "AB|!C!&"    # -> A!B!C!&&
```

> **Quote your formulas** — `|`, `>`, `&` and `^` are shell metacharacters.

**No arguments** — the demo: all seven subject examples with expected values,
the worked instruction example, distributivity cases, other operators converted
end to end, and the error cases.

**`-t`** — every stage: after eliminating `>`/`=`/`^`, after NNF, after
distribution, the clause list, the flattened output, and all five checks.

**`-v`** — the result on stdout, the five checks on stderr.

### The subject's examples, all verified

| Input | Subject's output | Got |
|---|---|---|
| `AB&!` | `A!B!\|` | `A!B!\|` ✓ |
| `AB\|!` | `A!B!&` | `A!B!&` ✓ |
| `AB\|C&` | `AB\|C&` | `AB\|C&` ✓ |
| `AB\|C\|D\|` | `ABCD\|\|\|` | `ABCD\|\|\|` ✓ |
| `AB&C&D&` | `ABCD&&&` | `ABCD&&&` ✓ |
| `AB&!C!\|` | `A!B!C!\|\|` | `A!B!C!\|\|` ✓ |
| `AB\|!C!&` | `A!B!C!&&` | `A!B!C!&&` ✓ |
| `ABCD&\|&` | `ABC\|BD\|&&` | `ABC\|BD\|&&` ✓ |

All eight identical.

---

## 10. Common mistakes to avoid

| Mistake | What happens | Fix |
|---|---|---|
| Returning the tree with a plain post-order walk | `AB&C&D&` instead of `ABCD&&&` — fails the stated shape | Flatten and emit operators last (section 4) |
| Distributing before reaching NNF | A `¬` over a bracket blocks the rule | NNF first, always |
| Only handling `A ∨ (B ∧ C)` | `(A ∧ B) ∨ C` is left un-distributed | Handle the AND on either side |
| Distributing top-down | Children may still contain ANDs | Convert children first, then distribute |
| Sharing the duplicated operand | Latent aliasing bug | `copy_tree` |
| Recursive walks over the output | `RecursionError` on deep chains | Iterate with an explicit stack (section 6.1) |
| Expecting a unique answer | Several valid CNFs exist | Compare **truth tables** |
| Assuming `∨` doesn't distribute over `∧` | Arithmetic intuition misleads here | It does — see the subject's red box |

---

## 11. Do this on paper

1. **Verify the surprising law:** build truth tables for `A ∨ (B ∧ C)` and
   `(A ∨ B) ∧ (A ∨ C)` with your Exercise 04 program (`ABC&|` and `AB|AC|&`).
   Identical result columns — the law arithmetic doesn't have.

2. **Distribute by hand:** convert `AB&C|` — that's `(A ∧ B) ∨ C`. The AND is on
   the *left*, so use the section 2.2 form. You should get `(A∨C) ∧ (B∨C)` →
   `AC|BC|&`.

3. **Trace `ABCD&|&`** through all four stages before running `-t`.

4. **Flatten by hand:** take `AB&C&D&`, draw its tree, list the clauses, and
   write the flattened RPN. Confirm you get `ABCD&&&` and that re-parsing it
   gives back the same formula.

5. **Count the blowup:** convert `AB&CD&|` by hand. How many clauses? Now
   predict `AB&CD&|EF&|` before checking the table in section 6.

6. **Simplify by hand:** take the `AB=` output `AA!|AB!|BA!|BB!|&&&`, cross out
   the tautological clauses, and confirm what remains really is `A ⇔ B`.

---

## 12. Peer-review preparation

- **"What is CNF?"** → An AND of ORs of literals. No AND may appear inside an OR.
- **"How does it relate to Exercise 05?"** → CNF = NNF plus distribution. The
  subject says to reuse the previous function, and this file does.
- **"State distributivity."** → `A ∨ (B ∧ C) ⇔ (A ∨ B) ∧ (A ∨ C)`, and it works
  from either side. Unlike arithmetic, it goes both ways — the subject's red box.
- **"Why is `AB&C&D&` not returned unchanged?"** → It's already logically CNF,
  but the required *shape* puts every `&` at the end, so it must come out as
  `ABCD&&&`. Associativity is what makes that legal.
- **"How do you produce that shape?"** → Flatten each operator chain into a list,
  emit all operands, then all the operators.
- **"Why does the output get so big?"** → Distribution duplicates the other
  operand. `AB=C=D=` goes from 7 characters to 1,682.
- **"Why are some of your loops iterative?"** → Deep CNF trees exceed Python's
  1000-frame recursion limit; an explicit stack has no such limit.
- **"Is `A ∨ ¬A` in your output a bug?"** → No, it's a tautology that is simply
  redundant. Simplification is optional per the subject.
- **"How do you know it's correct?"** → Five properties including an identical
  truth table, verified on 9,018 exhaustive plus 1,200 random formulas.

---

## 13. What's next

**Exercise 07 (SAT)** asks whether a formula can be made true by some
assignment. The subject again says you may reuse earlier functions, and you have
two routes:

- **Brute force** — loop over all 2ⁿ assignments with your Exercise 04
  machinery and stop at the first `true`. Simple, and within the required
  O(2ⁿ).
- **Via CNF** — a CNF formula is satisfiable when you can pick one true literal
  from every clause. This is the shape real solvers exploit.

The required complexity is O(2ⁿ), so brute force is acceptable — but the CNF
route is why this exercise comes first.