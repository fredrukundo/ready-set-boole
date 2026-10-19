# Exercise 05 — Negation Normal Form

> **Goal:** write `negation_normal_form(formula)` returning an equivalent
> formula where **every negation sits directly on a variable**.
>
> **Allowed mathematical functions:** None
> **Required complexity:** N/A time, N/A space
> **Output constraint:** the result may contain only variables and `!`, `&`, `|`

---

## 0. Before you start — the tree pays off here

Up to now you have been *computing* with formulas. This exercise is the first
one where you **transform** a formula into a different formula that means the
same thing.

This is exactly the moment the Exercise 03 decision pays off. Every rewrite rule
below is a small, local change to a tree node — "find this shape, replace it
with that shape". On a flat string you would be hunting for sub-formula
boundaries by counting operands backwards through the text. On a tree it's a
dozen lines of recursion.

**Required reading first:** Interlude 00 (Chapter VIII) lists the rewrite rules.
This exercise implements four of them.

You should also have Exercise 04 to hand, not just as a past exercise but as a
**tool**: a rewrite is correct exactly when the original and the result have
identical truth tables. This implementation reuses that to check itself.

---

## 1. What is Negation Normal Form?

A formula is in **Negation Normal Form (NNF)** when:

1. Every `!` is applied **directly to a variable** — never to a bracketed
   sub-formula.
2. The only operators present are `!`, `&` and `|`.

The subject states both conditions: *"every negation operators must be located
right after a variable"*, and *"The result must only contain variables and the
following symbols: !, & and | (even if the input contains other operations)."*

### 1.1 Examples

| Formula | In NNF? | Why |
|---|---|---|
| `A!B!\|` | ✔ yes | ¬A ∨ ¬B — each `!` is on a variable |
| `AB&!` | ✘ no | ¬(A ∧ B) — the `!` negates a whole sub-formula |
| `AB>` | ✘ no | contains `>` |
| `A!!` | ✘ no | the outer `!` applies to `¬A`, not to a variable |
| `AB&CD\|&` | ✔ yes | no negation at all, only `&` and `\|` — that's fine |

That last row is worth noting: NNF doesn't *require* negations, it only
restricts where they may appear.

### 1.2 Why does this form matter?

Two reasons.

**It's a stepping stone.** Exercise 06 (CNF) needs a formula built only from
`&`, `|` and negated variables before distributivity can be applied. NNF is
precisely that precondition. The subject's hint in Chapter X — *"You may use the
function you wrote during the previous exercise"* — is pointing straight at this.

**It makes structure visible.** Once negations are pushed down to the leaves,
the shape of the formula is carried entirely by `&` and `|`. Nothing is hidden
inside a negated bracket. That's what makes the next transformation mechanical.

### 1.3 Vocabulary

| Word | Meaning |
|---|---|
| **normal form** | A standardised shape that every formula can be rewritten into. |
| **literal** | A variable or a negated variable: `A` or `¬A`. The leaves of an NNF formula are exactly the literals. |
| **rewrite rule** | An equivalence used left-to-right to transform a formula. |
| **equivalent** | Two formulas with identical truth tables. |
| **idempotent** | Applying the operation twice changes nothing after the first time. |

---

## 2. The rewrite rules

Four rules, all from Interlude 00 except xor (which the subject's table includes
as an operator but doesn't give a rule for).

### 2.1 Material condition — eliminating `>`

```
A ⇒ B   ⇔   ¬A ∨ B
```

This is the identity from Exercise 03, section 2.2: *"either the premise fails,
or the conclusion holds"*. Verify it with Exercise 04 if you haven't:
`AB>` and `A!B|` have identical result columns.

```
AB>   ->   A!B|          ✓ matches the subject's third example
```

### 2.2 Equivalence — eliminating `=`

The subject's example tells us which form they want:

```
negation_normal_form("AB=")   ->   AB&A!B!&|
```

Read that back: `(A ∧ B) ∨ (¬A ∧ ¬B)` — **"both true, or both false"**. Which is
exactly what "A if and only if B" means.

```
A ⇔ B   ⇔   (A ∧ B) ∨ (¬A ∧ ¬B)
```

**A note on Interlude 00.** The subject's interlude gives a *different*
equivalence rule:

```
A ⇔ B   ⇔   (A ⇒ B) ∧ (B ⇒ A)
```

Follow that one instead and you'd get `A!B|B!A|&` — also perfectly valid NNF,
also correct. The subject says *"There may be several valid results, only one is
required."* This implementation uses the both-true-or-both-false form **because
it reproduces the subject's printed example exactly**, which is one less thing
for an evaluator to query. Either answer passes; matching the example is just
tidier.

### 2.3 Exclusive or — eliminating `^`

Not in Interlude 00, but `^` is in the symbol table and the output may not
contain it, so it needs a rule. XOR is the mirror image of equivalence:

```
A ⊕ B   ⇔   (A ∧ ¬B) ∨ (¬A ∧ B)
```

**"Exactly one of them is true."**

```
AB^   ->   AB!&A!B&|
```

### 2.4 De Morgan's laws — pushing `!` inward

These are the heart of the exercise:

```
¬(A ∧ B)   ⇔   ¬A ∨ ¬B
¬(A ∨ B)   ⇔   ¬A ∧ ¬B
```

**The operator flips.** Negating an AND gives an OR, and vice versa. That flip
is the thing to remember — forgetting it is the single most common bug here.

The plain-English reading helps:

- *"Not both of them"* = *"at least one of them is missing"* → ¬A ∨ ¬B
- *"Neither of them"* = *"this one is missing AND that one is missing"* → ¬A ∧ ¬B

```
AB&!   ->   A!B!|          ✓ the subject's first example
AB|!   ->   A!B!&          ✓ the subject's second example
```

### 2.5 Double negation

```
¬¬A   ⇔   A
```

Two negations cancel. `A!!` becomes just `A`.

---

## 3. The algorithm — two passes

The transformation is done in two separate recursive passes. Keeping them
separate is what makes each one simple.

### Pass 1 — eliminate `>`, `=` and `^`

Walk the tree. Rewrite children first, then apply the rule for this node:

```
>  ->  !A | B
=  ->  (A & B) | (!A & !B)
^  ->  (A & !B) | (!A & B)
&, |, !, leaves  ->  unchanged (but children still rewritten)
```

After this pass, only `!`, `&`, `|` and leaves remain — but negations may still
sit on whole sub-formulas.

### Pass 2 — push negations down to the leaves

This pass carries a **flag** rather than rewriting in place:

```
push(node, negated):
    leaf      ->  negated ? !leaf : leaf
    !         ->  push(child, NOT negated)      # absorb the ! into the flag
    &         ->  negated ? OR of push(both, True) : AND of push(both, False)
    |         ->  negated ? AND of push(both, True) : OR of push(both, False)
```

**Why the flag is elegant.** It handles double negation for free. Two `!` nodes
flip the flag twice, returning it to `False` — no special case needed, no
separate rule to apply. `A!!!!` collapses to `A` without any code that mentions
double negation at all.

And De Morgan becomes a single line: *when `negated` is true, swap the operator
and pass the flag down to both children*.

### 3.1 Worked example: `AB|C&!`

That's `¬((A ∨ B) ∧ C)` — the subject's fifth example.

**Pass 1:** no `>`, `=` or `^` present → unchanged.

**Pass 2**, starting at the root with `negated = False`:

| node | negated in | what happens |
|---|---|---|
| `!` | False | absorb it → recurse on child with `negated = True` |
| `&` | True | flip to `\|`, pass True to both children |
| `\|` (left child) | True | flip to `&`, pass True to both children |
| `A` | True | leaf → `A!` |
| `B` | True | leaf → `B!` |
| `C` (right child) | True | leaf → `C!` |

Reassembled: `(¬A ∧ ¬B) ∨ ¬C` → RPN **`A!B!&C!|`** ✓ matches the subject.

See it yourself:

```bash
python3 negation_normal_form.py -t "AB|C&!"
```

```
  [2] After pushing negations onto the variables

      A!B!&C!|
      ((¬A ∧ ¬B) ∨ ¬C)

  [3] Result tree

      ∨
      ├── ∧
      │   ├── ¬
      │   │   └── A
      │   └── ¬
      │       └── B
      └── ¬
          └── C
```

Every `¬` in that tree has a bare variable underneath it. That's NNF, visually.

---

## 4. Serialising back to RPN

The function must return a **string**, so the tree has to be written back out.
This is the easiest part:

```python
def to_rpn(node):
    if leaf:        return symbol
    if unary:       return to_rpn(child) + symbol
    else:           return to_rpn(left) + to_rpn(right) + symbol
```

Children first, then the operator — which is the definition of RPN. The
traversal order *is* the output order, so no stack and no parentheses are
needed. (This is called a **post-order traversal**.)

---

## 5. Checking your own work

The subject gives five examples. That's not many, and "there may be several
valid results" means you can't simply string-compare against expected output in
general. So how do you know a rewrite is right?

**Three properties must hold for every input:**

1. **It is NNF** — every `!` has a leaf directly beneath it.
2. **Only `!`, `&`, `|`** appear in the output.
3. **It is equivalent** — identical truth table to the input.

Property 3 is the important one, and Exercise 04 already gives it to you. Build
both truth tables, compare the result columns. That's what `equivalent()` does
in this file, and it's what `-v` reports:

```bash
$ python3 negation_normal_form.py -v "AB=C^"
AB&A!B!&|C!&A!B!|AB|&C&|
  is NNF           : True
  same truth table : True
```

### Verification performed

- All **five subject examples** reproduced character for character.
- All three properties verified on **9,018 formulas** — every valid formula of
  length 1–6 over A, B, C — plus **4,000 random deeper formulas** with up to 4
  variables.
- **Idempotence** checked on 610 formulas: running NNF on an already-NNF formula
  returns it unchanged. (A good sanity property — if the second pass changed
  something, the first pass hadn't finished the job.)

---

## 6. The size problem

The subject warns about this in Exercise 06, but it starts here. Eliminating `=`
and `^` **duplicates both operands**:

```
A = B   ->   (A & B) | (!A & !B)
             ^   ^       ^    ^
             A and B each appear twice
```

If `A` is itself a big sub-formula, it gets copied. Nest these and the growth is
exponential:

| input | length | output length |
|---|---|---|
| `AB=` | 3 | 9 |
| `AB=C=` | 5 | 24 |
| `AB=C=D=` | 7 | 54 |
| `AB=C=D=E=` | 9 | 114 |
| `AB=C=D=E=F=` | 11 | 234 |

Roughly doubling each time. This is why the subject sets the complexity to
**N/A** for this exercise — there is no reasonable bound to require.

It's also why `copy_tree` exists in the code. The two copies of `A` must be
**independent objects**. Sharing one object would work for this exercise (nothing
mutates), but Exercise 06 rewrites trees further, and a shared node edited in one
place would silently change the other. Copying keeps every node owned by exactly
one parent.

---

## 7. The code

### 7.1 What's new compared to Exercise 04

| Piece | Status |
|---|---|
| `Node`, `parse`, `evaluate`, `collect_variables` | unchanged from Ex03/Ex04 |
| `to_rpn` | **new** — serialise a tree back to a string |
| `copy_tree` | **new** — independent subtree copies |
| `eliminate_operators` | **new** — pass 1 |
| `push_negations` | **new** — pass 2 |
| `is_nnf` | **new** — verify property 1 |
| `equivalent` | **new** — verify property 3, built on Ex04's table loop |

### 7.2 The two passes, in full

```python
def eliminate_operators(node):
    if node.is_leaf():      return Node(node.symbol)
    if node.symbol == "!":  return Node("!", eliminate_operators(node.left))

    left  = eliminate_operators(node.left)
    right = eliminate_operators(node.right)

    if node.symbol == ">":
        return Node("|", Node("!", left), right)
    if node.symbol == "=":
        return Node("|", Node("&", left, right),
                         Node("&", Node("!", copy_tree(left)),
                                   Node("!", copy_tree(right))))
    if node.symbol == "^":
        return Node("|", Node("&", left, Node("!", copy_tree(right))),
                         Node("&", Node("!", copy_tree(left)), right))
    return Node(node.symbol, left, right)
```

```python
def push_negations(node, negated=False):
    if node.is_leaf():
        if not negated:         return Node(node.symbol)
        if node.symbol == "0":  return Node("1")
        if node.symbol == "1":  return Node("0")
        return Node("!", Node(node.symbol))

    if node.symbol == "!":
        return push_negations(node.left, not negated)

    if node.symbol == "&":
        return Node("|" if negated else "&",
                    push_negations(node.left, negated),
                    push_negations(node.right, negated))

    if node.symbol == "|":
        return Node("&" if negated else "|",
                    push_negations(node.left, negated),
                    push_negations(node.right, negated))
```

Note the symmetry in pass 2 — `&` and `|` are the same four lines with the
symbols swapped. That symmetry *is* De Morgan's law, expressed as code.

### 7.3 Constants

The subject's symbol table for this exercise lists only `A`–`Z`, but this parser
still accepts `0` and `1` (as in Exercise 03). A negated constant is simply the
other constant — `¬⊥` becomes `1` — rather than emitting `0!`, which wouldn't
satisfy "negation right after a **variable**". A harmless extension; mention it
only if asked.

---

## 8. How to run it

```bash
cd Ex05

python3 negation_normal_form.py "AB&!"      # -> A!B!|
python3 negation_normal_form.py "AB="       # -> AB&A!B!&|
python3 negation_normal_form.py "AB|C&!"    # -> A!B!&C!|
```

> **Quote your formulas** — `|`, `>`, `&` and `^` are shell metacharacters.

**No arguments** — the demo: the five subject examples with expected values,
each rewrite rule in isolation, nested/mixed formulas with their NNF and
equivalence checks, and the error cases.

**`-t`** — show each stage: after eliminating `>`/`=`/`^`, after pushing
negations, the result tree, and all three checks.

**`-v`** — print the result, plus the NNF and equivalence checks on stderr (so
piping the output still gives you just the formula).

### The subject's examples, all verified

| Input | Subject's output | Got |
|---|---|---|
| `AB&!` | `A!B!\|` | `A!B!\|` ✓ |
| `AB\|!` | `A!B!&` | `A!B!&` ✓ |
| `AB>` | `A!B\|` | `A!B\|` ✓ |
| `AB=` | `AB&A!B!&\|` | `AB&A!B!&\|` ✓ |
| `AB\|C&!` | `A!B!&C!\|` | `A!B!&C!\|` ✓ |

All five identical.

---

## 9. Common mistakes to avoid

| Mistake | What happens | Fix |
|---|---|---|
| Forgetting the operator flip in De Morgan | `¬(A∧B)` → `¬A ∧ ¬B` — wrong truth table | `∧` becomes `∨` and vice versa |
| Leaving `^`, `>` or `=` in the output | Violates the stated output constraint | Pass 1 must eliminate all three |
| Pushing negations before eliminating `>`/`=`/`^` | Pass 2 hits an operator it has no rule for | Eliminate first, then push |
| Negating only one side in De Morgan | `¬(A∧B)` → `¬A ∨ B` | Both children get negated |
| Sharing subtree objects when duplicating | Works now, breaks in Ex06 when trees get edited | `copy_tree` |
| Handling double negation as a special case | Extra code, easy to get wrong | The `negated` flag does it for free |
| Comparing output to the subject's string | Several valid answers exist | Compare **truth tables** |
| Writing RPN with the operator first | That's Polish notation, not *Reverse* Polish | Children first, operator last |

---

## 10. Do this on paper

1. **Verify De Morgan** with truth tables: build the tables for `AB&!` and
   `A!B!|` using your Exercise 04 program. Identical result columns.

2. **Convert by hand:** `AB>!` — that's ¬(A ⇒ B). Eliminate `>` first, then push
   the negation. You should get `AB!&` (A ∧ ¬B). Does that make sense in words?
   *The only way to break a promise is for the premise to hold and the
   conclusion to fail.*

3. **Trace `ABC&|!`** through both passes by hand, writing the tree at each
   stage. Check with `-t`.

4. **Compare the two equivalence rules:** convert `AB=` by hand using Interlude
   00's rule `(A⇒B) ∧ (B⇒A)` instead. You should get `A!B|B!A|&`. Build its
   truth table and confirm it matches `AB&A!B!&|`. Both are valid NNF.

5. **Watch the blowup:** convert `AB=C=` by hand. Count the characters. Now
   predict `AB=C=D=` before running it.

6. **Answer in writing:** why does the `negated` flag handle `A!!!!` correctly
   without any rule for double negation?

---

## 11. Peer-review preparation

- **"What is NNF?"** → Every negation sits directly on a variable, and only
  `!`, `&`, `|` remain.
- **"Walk me through your algorithm."** → Two passes: eliminate `>`, `=`, `^`
  using their identities; then push negations down with De Morgan, carrying a
  flag.
- **"State De Morgan."** → ¬(A∧B) ⇔ ¬A∨¬B and ¬(A∨B) ⇔ ¬A∧¬B. **The operator
  flips.**
- **"How do you handle double negation?"** → The `negated` flag flips twice and
  cancels — no special case.
- **"Why two passes instead of one?"** → Pass 2 only knows `!`, `&`, `|`.
  Eliminating the other operators first keeps each pass simple.
- **"Your `AB=` doesn't match Interlude 00's rule."** → Interlude 00 gives
  `(A⇒B)∧(B⇒A)`; I use `(A∧B)∨(¬A∧¬B)` because that reproduces the subject's
  printed example. Both are valid — the subject says several results are
  acceptable.
- **"How do you know it's correct?"** → Three properties: it's NNF, it uses only
  the allowed symbols, and it has the same truth table. Verified on 9,018
  exhaustive plus 4,000 random formulas. Show `-v`.
- **"Why can the output get so big?"** → `=` and `^` duplicate both operands;
  nesting them doubles the size each time. That's why complexity is N/A.
- **"Why `copy_tree`?"** → The duplicated operands must be independent objects,
  or a later in-place edit would change both.

---

## 12. What's next

**Exercise 06 (CNF)** continues directly from here. Conjunctive Normal Form
requires NNF *plus* one more property: all the `&` operators pulled to the
outside, so the formula becomes a big AND of ORs. The tool is distributivity
(Interlude 00, section VIII.5):

```
A ∨ (B ∧ C)   ⇔   (A ∨ B) ∧ (A ∨ C)
```

The subject's hint — *"You may use the function you wrote during the previous
exercise"* — means literally this: run `negation_normal_form` first, then
distribute. The size-growth problem from section 6 gets worse there, and the
subject acknowledges it: *"The size of the output formula may grow exponentially
with the size of the input."*