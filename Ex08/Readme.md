# Exercise 08 — Powerset

> **Goal:** write `powerset(set)` returning every subset of a set of integers.
>
> **Allowed mathematical functions:** None
> **Required complexity:** N/A time, **O(2ⁿ) space**

---

## 0. Before you start

This exercise opens the **set-theory block**, and it's a gentle one — the
algorithm is the same bit-mask enumeration you already used for truth-table rows
in Exercise 04. If that trick made sense there, this is twenty lines.

**Required reading first:** Interlude 02 (Chapter XIII) introduces sets, the
symbols, Russell's paradox, and — most importantly for Exercise 09 — the
correspondence between logic and set theory. Section 1 below summarises what you
need.

Two things to notice about the spec:

- **The subject gives no examples here.** Chapter XIV ends at the prototype. So
  unlike Exercise 04 (where the format was graded character by character), the
  output format is your choice. This implementation uses mathematical notation
  (`{}`, `{1}`, `{1, 2}`), which is the easiest to check by eye.
- **The complexity constraint is on *space*, not time** — the reverse of
  Exercise 04. Section 5 explains why.

---

## 1. Set theory, the parts you need

### 1.1 What is a set?

A **set** is a collection of objects where only two things matter:

- **No duplicates.** `{1, 2, 2}` isn't a set; it's just `{1, 2}`.
- **No order.** `{1, 2}` and `{2, 1}` are the *same set*.

That second point is the one that trips up programmers, because a list is
ordered and a set isn't. The subject puts it well: *"You can see a set as an
array that can be finite or infinite, and cannot be indexed."*

The subject also states the input assumption plainly: *"It is assumed that the
set passed as parameter is valid (no duplicate elements)."* This implementation
checks anyway and reports a duplicate rather than silently producing repeated
subsets.

### 1.2 Symbols from Interlude 02

| Symbol | Meaning |
|---|---|
| `∅` | the empty set — the set with no elements |
| `a ∈ B` | "a is an element of B" |
| `a ∉ B` | "a is not in B" |
| `A ⊆ B` | A is a **subset** of B — every element of A is in B, and A may equal B |
| `A ⊇ B` | A is a **superset** of B |
| `∀a ∈ B` | "for all a in B" |
| `∃a ∈ B` | "there exists an a in B" |
| `card(A)`, `\|A\|` | the **cardinal** — how many elements A has |
| `P(A)` | the **powerset** of A |

### 1.3 The link between logic and sets

This table from Interlude 02 (XIII.4) is the key to **Exercise 09**, so it's
worth learning now:

| Boolean algebra | Name | Set theory | Name |
|---|---|---|---|
| ¬A | negation | Aᶜ or Ā | complement |
| A ∨ B | disjunction | A ∪ B | union |
| A ∧ B | conjunction | A ∩ B | intersection |

The subject notes that the rewrite rules you implemented in Exercise 05 — double
negation, De Morgan — **work on sets too**. De Morgan for sets reads:

```
(A ∪ B)ᶜ  =  Aᶜ ∩ Bᶜ
(A ∩ B)ᶜ  =  Aᶜ ∪ Bᶜ
```

Exactly the same shape as the logical version, with the symbols swapped. That
correspondence is what makes Exercise 09 "Exercise 03 again, with sets".

### 1.4 The Venn diagram question

Interlude 02 (XIII.5) shows three Venn diagrams and asks *"Can you guess which
operations they are?"* Reading the coloured region in each:

| Diagram | Coloured | Operation |
|---|---|---|
| left | both circles **except** the overlap | **symmetric difference**, A △ B — the set version of XOR |
| middle | everything **except** the overlap, including outside the circles | **complement of the intersection**, (A ∩ B)ᶜ |
| right | both circles **including** the overlap | **union**, A ∪ B |

The left one is a nice link back to Exercise 03: symmetric difference is to sets
what `^` is to booleans — "in one or the other, but not both".

### 1.5 Russell's paradox (why "naive" set theory is naive)

Interlude 02 spends a section on this, and it's worth understanding because it
explains an odd rule: **a set cannot contain itself.**

Imagine the set `A` of all sets that do **not** contain themselves:

```
A = { x | x ∉ x }
```

Now ask: does `A` contain itself?

- If `A ∉ A`, then by its own definition it qualifies for membership — so
  `A ∈ A`. Contradiction.
- If `A ∈ A`, then it fails its own definition — so `A ∉ A`. Contradiction.

Either way you get a contradiction. Bertrand Russell found this in 1901, and it
broke naive set theory. The repair was more careful systems — **Zermelo-Fraenkel
(ZF) set theory**, category theory, and **type theory** (which, as the subject
notes, is very useful in computer science: it's why your compiler can reason
about types at all).

None of this affects your code. It's the reason the ground rules are what they
are.

---

## 2. What is a powerset?

The **powerset** of `A`, written `P(A)`, is **the set of all subsets of `A`** —
including the empty set and `A` itself.

```
A = {1, 2, 3}

P(A) = { {}, {1}, {2}, {3}, {1,2}, {1,3}, {2,3}, {1,2,3} }
```

Eight subsets. Note that `P(A)` is a **set of sets** — its elements are
themselves sets.

> **On ordering.** Listed above grouped by size, which reads naturally. The
> program emits them in *mask order* (`{}, {1}, {2}, {1,2}, {3}, …`, see
> section 3). Both are the same powerset — a set has no order, so any listing
> of the same eight subsets is correct. Don't let the difference worry you.

Two elements people forget:

- **`∅` is always in there.** The empty set is a subset of every set (vacuously:
  it has no element that could fail to be in `A`).
- **`A` itself is always in there.** `A ⊆ A` is true — subset allows equality.

So even `P(∅) = {∅}` — the powerset of the empty set has **one** element, not
zero. That's a good edge case to be asked about.

### 2.1 Why 2ⁿ subsets?

Here's the argument, and it's the one to give at a defense.

To build a subset, you walk through the elements and make **one yes/no decision
each**: is this element in, or out?

```
element 1:  in or out?   2 choices
element 2:  in or out?   2 choices
element 3:  in or out?   2 choices
```

The decisions are independent, so the total number of distinct subsets is

```
2 × 2 × 2 = 2³ = 8
```

and in general **2ⁿ** for `n` elements. Every different combination of decisions
gives a different subset, and every subset arises from exactly one combination —
so the count is exact, not an estimate.

### 2.2 Cantor's theorem (optional, but a nice fact)

`P(A)` is always **strictly larger** than `A` — `2ⁿ > n` for every `n`. This
holds even for infinite sets, which is how Georg Cantor proved there are
**different sizes of infinity**. The subject's info box hints at this: *"Note
that there are multiple, distinct, infinite cardinals."*

Not required. Worth knowing if an evaluator is curious.

---

## 3. The algorithm

Section 2.1 said a subset is **n independent yes/no decisions**. And `n` yes/no
decisions is *exactly* what an n-bit binary number encodes.

So: **count from 0 to 2ⁿ − 1, and read each number's bits as the decisions.**

```
n = 3, elements a, b, c

mask  binary   subset
  0     000    {}
  1     001    {a}
  2     010    {b}
  3     011    {a, b}
  4     100    {c}
  5     101    {a, c}
  6     110    {b, c}
  7     111    {a, b, c}
```

Bit `j` set means "element `j` is in this subset". Because every number from 0 to
2ⁿ−1 appears exactly once, **every subset appears exactly once** — no
duplicates, nothing missed. The counting does the bookkeeping for you.

```python
def powerset(elements):
    count = len(elements)
    result = []
    for mask in range(1 << count):          # 0 .. 2^n - 1
        subset = []
        for index in range(count):
            if (mask >> index) & 1 == 1:    # is bit `index` set?
                subset.append(elements[index])
        result.append(subset)
    return result
```

`1 << count` is `2^count` — the shift from Exercise 01. `(mask >> index) & 1`
tests one bit — the same test used in Exercise 01's multiplier and Exercise 04's
truth-table rows.

### 3.1 You've done this before

This is the **third** appearance of the same trick:

| Exercise | What the bits selected |
|---|---|
| 01 Multiplier | which shifted copies of `a` to add |
| 04 Truth table | which variables are true in this row |
| **08 Powerset** | **which elements are in this subset** |

If an evaluator asks where the idea came from, that's a good answer — it's the
standard way to enumerate "all combinations of n independent binary choices".

### 3.2 Worked example

```bash
python3 powerset.py -t 1 2 3
```

```
  set: {1, 2, 3}   (3 elements)
  the powerset has 2^3 = 8 subsets

  each bit position decides one element:

      bit 0  ->  1
      bit 1  ->  2
      bit 2  ->  3

       mask | binary | subset
      ------------------------------
          0 | 000 | {}
          1 | 001 | {1}
          2 | 010 | {2}
          3 | 011 | {1, 2}
          4 | 100 | {3}
          5 | 101 | {1, 3}
          6 | 110 | {2, 3}
          7 | 111 | {1, 2, 3}

  8 subsets, as expected.
```

Note the bits are read **right to left** — bit 0 is the rightmost digit. That's
why mask `011` gives `{1, 2}` and not `{2, 3}`.

---

## 4. An alternative: recursive construction

Worth knowing, because an evaluator may ask "is there another way?"

```
P({}) = { {} }
P(A ∪ {x}) = P(A)  ∪  { S ∪ {x} : S ∈ P(A) }
```

In words: take the powerset of everything except the last element, then output
it **twice** — once as-is, once with the last element added to every subset.

That doubling is the 2ⁿ growth made visible, and it's the same reflect-and-extend
shape as the Gray code construction in Exercise 02. This implementation uses the
iterative bit-mask version because it needs no recursion and no stack — which
matters given how fast the output grows.

---

## 5. Complexity

The subject requires **O(2ⁿ) space** and sets time to **N/A**. That's the
reverse emphasis of Exercise 04, and it's worth understanding why.

**Why space is the binding constraint:** the function must *return* all 2ⁿ
subsets, so they all exist in memory at once. That's unavoidable — it's the
output itself, not a choice of algorithm.

- **Space:** 2ⁿ subsets, of n elements each in the worst case → O(2ⁿ) at minimum,
  and O(n·2ⁿ) counting the elements inside them. The subject's bound is on the
  number of subsets. ✓
- **Time:** the loop runs 2ⁿ times with O(n) work each, so O(n·2ⁿ). Marked N/A
  because, as with space, you cannot produce 2ⁿ things faster than 2ⁿ.

Note `n` has changed meaning *again* — here it's the **number of elements in the
input set**. Across the module it has been a numeric value (Ex00/01), a string
length (Ex03), a variable count (Ex04/07), and now a set size.

### 5.1 A practical guard

2²⁶ subsets would be 67 million. This implementation refuses to build more than
2²⁰ unless you pass `-f`:

```
$ python3 powerset.py 1 2 3 ... 21
error: 21 elements would produce 2097152 subsets
hint: pass -f to build it anyway, or -c to count only
```

`-c` reports the count without building anything, which is instant for any size.
This is an engineering choice, not a subject requirement.

---

## 6. How to run it

```bash
cd Ex08

python3 powerset.py 1 2 3        # the powerset of {1, 2, 3}
python3 powerset.py 7            # -> {} and {7}
python3 powerset.py              # (no arguments) runs the demo
```

Output is one subset per line, in mathematical notation:

```
{}
{1}
{2}
{1, 2}
{3}
{1, 3}
{2, 3}
{1, 2, 3}
```

**`-t`** — show how each subset is derived from its bit mask (section 3.2).

**`-c`** — print only the count, `2ⁿ`, without building the subsets.

**`-f`** — build a powerset with more than 20 elements anyway.

**Negative numbers work**: `python3 powerset.py -1 -2` treats them as elements,
not options. Worth demonstrating, since it's a plausible thing for an evaluator
to try.

**The empty set**: `python3 powerset.py -t` with no numbers gives `P(∅) = {{}}`
— one subset, not zero.

### Verification performed

The subject gives no examples, so correctness was checked against the
mathematical definition and an independent reference (`itertools.combinations`):

- **Cardinality** `|P(A)| = 2ⁿ` for n = 0..12.
- **Completeness** — identical to `itertools.combinations` over all sizes, for
  n = 0..12 and **400 random sets** including negatives and zero.
- **All subsets distinct** — no duplicates.
- **Contains `∅` and `A` itself** in every case.
- **Every output really is a subset** of the input.
- **Deterministic** — repeated calls give identical output.
- Two classic identities: each element appears in exactly **2ⁿ⁻¹** subsets, and
  the sizes of all subsets sum to **n·2ⁿ⁻¹**.

---

## 7. Common mistakes to avoid

| Mistake | What happens | Fix |
|---|---|---|
| Forgetting the empty set | 2ⁿ−1 subsets instead of 2ⁿ | Start the loop at mask `0` |
| Forgetting the full set | Missing the last subset | Loop **through** `2ⁿ − 1` inclusive |
| Looping to `2ⁿ` inclusive | One subset too many, and a stray duplicate | `range(1 << n)` stops correctly |
| Reading bits left to right | Subsets are correct as a set, but the order looks scrambled | Bit 0 is the rightmost |
| Returning `P(∅) = {}` | The powerset of the empty set has **one** element, `∅` | `2⁰ = 1` |
| Mutating one shared list | Every subset ends up identical | Build a fresh list per mask |
| Accepting duplicate input | Produces repeated subsets | Check, or trust the subject's assumption |
| Treating `-3` as an option | Crash or wrong parse | Check whether the argument parses as a number |

---

## 8. Do this on paper

1. **Write out `P({a, b})`** by hand — all four subsets. Then `P({a, b, c})` —
   all eight. Check against `python3 powerset.py -t 1 2 3`.

2. **Predict the count** for a set of 6 elements, then 10. Verify with `-c`.

3. **Build the mask table** for `{x, y}` by hand: write masks 0–3 in binary and
   read off each subset. Confirm the right-to-left bit order.

4. **Answer in writing:** why is `P(∅)` not empty? How many elements does it
   have?

5. **Count a specific element:** in `P({1,2,3,4})`, how many subsets contain the
   element `3`? Predict first, then count. (The answer is 2ⁿ⁻¹ — can you say
   why, in one sentence?)

6. **Recursive view:** starting from `P({1}) = {{}, {1}}`, apply the doubling
   rule from section 4 twice by hand to reach `P({1,2,3})`. Compare with the
   mask table.

7. **Set theory check:** using the table in section 1.3, translate
   `¬(A ∨ B) ⇔ ¬A ∧ ¬B` into set notation. You should get De Morgan for sets.

---

## 9. Peer-review preparation

- **"What is a powerset?"** → The set of all subsets, including the empty set
  and the original set itself.
- **"Why 2ⁿ?"** → Each element is independently in or out — n binary choices, so
  2ⁿ combinations, each giving a distinct subset.
- **"How does your algorithm work?"** → Count from 0 to 2ⁿ−1 and read each
  number's bits as the in/out decisions. Every number appears once, so every
  subset appears once.
- **"What is `P(∅)`?"** → `{∅}` — one element, not zero. `2⁰ = 1`.
- **"Is `A` a subset of itself?"** → Yes, `⊆` allows equality, which is why the
  full set is in the powerset.
- **"Justify the O(2ⁿ) space."** → The function returns 2ⁿ subsets, so they all
  exist at once. It's the output, not the algorithm.
- **"Why is time N/A?"** → Same reason — you can't produce 2ⁿ things in less
  than 2ⁿ steps, so there's nothing meaningful to constrain.
- **"Have you used this bit trick before?"** → Yes: Exercise 01 (which shifted
  copies to add) and Exercise 04 (which variables are true in a row).
- **"Any other way to do it?"** → Recursively: `P(A ∪ {x})` is `P(A)` plus every
  member of `P(A)` with `x` added. The doubling is the 2ⁿ growth made visible.
- **"What if the input has duplicates?"** → The subject assumes it doesn't; this
  implementation reports it rather than producing repeated subsets.

---

## 10. What's next

**Exercise 09 (Set evaluation)** closes the mandatory block, and it's
**Exercise 03 with sets instead of booleans**. You take an RPN formula and a
list of sets, and evaluate it using the correspondence from section 1.3:

| Operator | Boolean | Set |
|---|---|---|
| `!` | negation | complement |
| `&` | conjunction | intersection |
| `\|` | disjunction | union |

The RPN stack machine is identical — only the operations on the popped values
change. The one detail that needs care is the **complement**: complement
relative to *what*? The subject calls this out explicitly, and it's the main
thing to get right.

Since Ex09 needs the parser, that's a case where importing from an earlier
exercise applies — unlike this one, which needed nothing.