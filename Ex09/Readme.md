# Exercise 09 — Set evaluation

> **Goal:** write `eval_set(formula, sets)` that evaluates an RPN formula whose
> variables are **sets** instead of booleans, and returns the resulting set.
>
> **Allowed mathematical functions:** None
> **Required complexity:** N/A time, N/A space

---

## 0. Before you start — this is Exercise 03 again

This is the **last mandatory exercise**, and it is mostly a re-run of Exercise
03 with different operations plugged in. The stack machine is identical: push
operands, pop on an operator, one value left at the end. Only what the values
*are* has changed — sets instead of booleans.

The whole exercise rests on one table from Interlude 02 (XIII.4):

| Boolean algebra | Set theory |
|---|---|
| ¬A | complement |
| A ∨ B | union |
| A ∧ B | intersection |

**There is exactly one hard part**, and the subject puts it in a red warning
box: the complement is taken relative to a universe, and that universe is
**the union of all the input sets**. Section 2 is the one to read twice.

This file **imports** the parser from Ex05 rather than copying it, as the
subject's reuse hint suggests. Only the evaluator is new.

---

## 1. What the function does

You get a formula and a list of sets. Each letter names one set — *"The set A
is the first set, the set B is the second set, etc..."* — and the operators
become set operations.

```
eval_set("AB&", [[0,1,2], [0,3,4]])  ->  [0]
```

`A ∩ B`: the only element in both `{0,1,2}` and `{0,3,4}` is `0`. ✓

```
eval_set("AB|", [[0,1,2], [3,4,5]])  ->  [0,1,2,3,4,5]
```

`A ∪ B`: everything from either set. ✓

```
eval_set("A!", [[0,1,2]])  ->  []
```

This is the one that surprises people. See section 2.

### 1.1 The operators

| Symbol | Boolean meaning | Set operation | Definition |
|---|---|---|---|
| `!` | negation | **complement** | `U − A` |
| `&` | conjunction | **intersection** | in both |
| `\|` | disjunction | **union** | in either |
| `^` | exclusive or | **symmetric difference** | in exactly one |
| `>` | material condition | — | `Aᶜ ∪ B` |
| `=` | equivalence | — | `(A ∩ B) ∪ (Aᶜ ∩ Bᶜ)` |

The last three are built from the first three, using exactly the identities you
implemented in Exercise 05:

- `A ⇒ B` is `¬A ∨ B` → `complement(A) ∪ B`
- `A ⇔ B` is `(A ∧ B) ∨ (¬A ∧ ¬B)` → "in both, or in neither"
- `A ⊕ B` is "in exactly one" → symmetric difference

Note how `^` reappears here as the **symmetric difference** — which is also the
left-hand Venn diagram from Interlude 02 (XIII.5), the one where the overlap is
left uncoloured.

---

## 2. The universe — the one thing to get right

The subject's red box:

> **"The globally encompassing set is considered to be the union of all the sets
> given as parameters."**

This matters because **complement is meaningless without a universe**. If `A =
{0,1,2}`, what is "everything not in A"? All integers? All numbers? It has to be
bounded by something, and the subject says that something is the union of the
inputs.

### 2.1 Why `A!` gives `[]`

```
eval_set("A!", [[0,1,2]])
```

- The only set given is `{0,1,2}`.
- So the universe `U` = union of all inputs = `{0,1,2}`.
- `A!` = `U − A` = `{0,1,2} − {0,1,2}` = **`{}`**

There is nothing outside `A`, because `A` *is* the entire universe. The answer
`[]` is correct, and matches the subject's third example.

### 2.2 The universe depends on every set, not just the one being complemented

This is the subtle consequence worth understanding:

```
A = [0,1,2]              ->  U = [0,1,2]        ->  A! = []
A = [0,1,2], B = [3,4]   ->  U = [0,1,2,3,4]    ->  A! = [3,4]
```

**The same `A`, two different complements.** Adding an unrelated set `B` changed
what `A!` means, because it grew the universe. That's not a bug — it follows
directly from the subject's rule.

You can see it in the demo:

```
A = [0, 1, 2], B = [3, 4]  ->  U = [0, 1, 2, 3, 4]
A!, written AB|A!& to use both sets  ->  [3, 4]
```

(The formula is written `AB|A!&` — "(A ∪ B) ∩ Aᶜ" — because a bare `A!` has only
one variable and would therefore need exactly one set; see section 4.)

### 2.3 In code

```python
def build_universe(sets):
    universe = set()
    for one in sets:
        universe = universe | set(one)
    return universe

def complement(values, universe):
    return universe - values
```

Two functions, four lines. The difficulty is conceptual, not technical.

---

## 3. The algorithm

Identical to Exercise 03's stack machine:

```
for each character, left to right:
    a letter        -> push its set
    !               -> pop 1, push its complement
    & | ^ > =       -> pop 2, push the combined set
one value remains: the answer
```

### 3.1 Worked example

```bash
python3 eval_set.py -t "AB&" 0,1,2 0,3,4
```

```
  sets:
      A = [0, 1, 2]
      B = [0, 3, 4]

  universe (the union of every input set):
      U = [0, 1, 2, 3, 4]

  evaluation, left to right:

      step | char | action       | stack
         0 |    A | push A       | [0, 1, 2]
         1 |    B | push B       | [0, 1, 2] , [0, 3, 4]
         2 |    & | intersection | [0]

  result: [0]
```

Compare that stack table with Exercise 03's — it is the same machine. Only the
`action` column changed.

### 3.2 Constants

The subject's symbol table for this exercise lists only `A`–`Z`, but the
imported parser also accepts `0` and `1`. They map naturally:

- `0` (false) → the **empty set**
- `1` (true) → the **universe**

A harmless extension. Mention it only if asked.

---

## 4. Variable-to-set mapping

The subject says *"The set A is the first set, the set B is the second set,
etc..."*, so this implementation maps **by position in the alphabet**: `A`→set 1,
`B`→set 2, `C`→set 3.

It also says:

> *"If the formula is invalid, or if the amount of sets provided in the list is
> not equal to the amount of variables in the formula, the behaviour is
> undefined (however, we encourage you to print an appropriate error message)."*

So two things are checked:

```
$ python3 eval_set.py "AB&" 0,1,2
error: the formula has 2 distinct variable(s) (A, B) but 1 set(s) were
       provided; they must match

$ python3 eval_set.py "A" 0,1 2,3
error: the formula has 1 distinct variable(s) (A) but 2 set(s) were
       provided; they must match
```

### 4.1 A corner case worth knowing

Strict alphabet mapping means a formula like `BC&` with two sets is rejected:
`C` is the third letter, so it would need a third set, even though the count
check passes. The error says so explicitly.

An alternative reading would map the *i*-th distinct variable to the *i*-th set,
so `BC&` would work with two sets. Both readings satisfy the subject's examples
(which all start from `A`). This implementation follows the literal wording —
*"the set A is the first set"* — and reports the mismatch clearly rather than
guessing. If an evaluator prefers the other reading, that's a one-line change,
and the reasoning is worth being able to state.

---

## 5. How to know it's correct

The subject gives three examples. That's not many, so the real test is the
property that *defines* this exercise:

> **An element `x` is in the result exactly when the formula is true with each
> variable replaced by "is `x` a member of this set?"**

That is the logic↔set correspondence, stated operationally. It means every set
formula is really 2 evaluations in disguise: for each element of the universe,
evaluate the *boolean* formula over membership facts.

```
A = {0,1,2}, B = {0,3,4}, formula "AB&"

x=0:  in A? yes.  in B? yes.   true & true  = true   -> 0 is in the result
x=1:  in A? yes.  in B? no.    true & false = false  -> 1 is not
x=3:  in A? no.   in B? yes.   false & true = false  -> 3 is not
```

Result: `{0}` ✓

`membership_check()` implements exactly this, and `-v` reports it:

```bash
$ python3 eval_set.py -v "AB>" 0,1,2 2,3
[2, 3]
  universe         : [0, 1, 2, 3]
  membership check : True
```

### Verification performed

- All **three subject examples** reproduced exactly.
- **The membership property** verified on **14,000 formula/set combinations** —
  every valid formula of length 1–6 over A and B, against seven set pairs
  including empty sets and identical sets — plus **2,666 random** formula/set
  pairs over up to 3 variables.
- **Result containment**: no output ever contains an element outside the
  universe.
- **Classic set identities** all hold:

| Identity | Verified |
|---|---|
| De Morgan: `(A∪B)ᶜ = Aᶜ∩Bᶜ` | ✓ |
| De Morgan: `(A∩B)ᶜ = Aᶜ∪Bᶜ` | ✓ |
| Double complement: `Aᶜᶜ = A` | ✓ |
| Idempotence: `A∪A = A`, `A∩A = A` | ✓ |
| Commutativity of ∪ and ∩ | ✓ |
| Associativity of ∪ and ∩ | ✓ |
| Distributivity: `A∪(B∩C) = (A∪B)∩(A∪C)` | ✓ |
| Absorption: `A∩(A∪B) = A`, `A∪(A∩B) = A` | ✓ |
| Complement laws: `A∪Aᶜ = U`, `A∩Aᶜ = ∅` | ✓ |
| Material condition: `A⇒B = Aᶜ∪B` | ✓ |

Those are the set-theory versions of the rewrite rules from Interlude 00 — which
is the subject's point that *"the rewrite rules that we mentioned earlier also
work on sets."*

---

## 6. How to run it

```bash
cd Ex09

python3 eval_set.py "AB&" 0,1,2 0,3,4     # -> [0]
python3 eval_set.py "AB|" 0,1,2 3,4,5     # -> [0, 1, 2, 3, 4, 5]
python3 eval_set.py "A!" 0,1,2            # -> []
```

Sets are comma-separated. Brackets are optional and an empty argument is the
empty set:

```bash
python3 eval_set.py "AB|" "[1,2]" "[3]"   # -> [1, 2, 3]
python3 eval_set.py "A!" ""               # -> []
python3 eval_set.py "AB|" -2,-1 0,1       # negatives work
```

> **Quote your formulas** — `|`, `>`, `&` and `^` are shell metacharacters.

**No arguments** — the demo: the three subject examples, an explanation of the
universe, every operator on a worked pair, De Morgan verified on sets, edge
cases, and the error messages.

**`-t`** — show the sets, the computed universe, and the stack machine step by
step.

**`-v`** — print the result, with the universe and membership check on stderr.

### The subject's examples, all verified

| Call | Expected | Got |
|---|---|---|
| `eval_set("AB&", [[0,1,2],[0,3,4]])` | `[0]` | `[0]` ✓ |
| `eval_set("AB\|", [[0,1,2],[3,4,5]])` | `[0,1,2,3,4,5]` | `[0,1,2,3,4,5]` ✓ |
| `eval_set("A!", [[0,1,2]])` | `[]` | `[]` ✓ |

### On output order

The subject's second red box: *"Remember: The order of the elements in the
resulting set doesn't matter."* A set has no order. This implementation sorts
the result anyway, because sorted output is reproducible and easy to compare by
eye — but any permutation would be equally correct.

---

## 7. Reusing Exercise 05

Same mechanism as Ex06 and Ex07 — the sibling folder is added to the module
search path, resolved from `__file__` so it works from any working directory:

```python
_HERE = os.path.dirname(os.path.abspath(__file__))
_EX05 = os.path.join(_HERE, os.pardir, "Ex05")
if _EX05 not in sys.path:
    sys.path.insert(0, _EX05)

from negation_normal_form import (
    Node, parse,            # Exercise 03
    collect_variables,      # Exercise 04
    VARIABLES, CONSTANTS, PRETTY,
)
```

**Why Ex05 and not Ex06?** Ex09 needs only the parser and the `Node` class. It
does no rewriting, so importing Ex06 would drag in the CNF machinery for
nothing. Ex05 is the lightest module that carries what's needed.

A `boolean_evaluate` is defined locally — not imported — because it is used only
by `membership_check`, and keeping it beside the set evaluator makes the
side-by-side comparison in section 5 easy to read.

As with Ex06 and Ex07, this folder no longer runs standalone: it needs `Ex05/`
beside it, and says so clearly if it's missing.

---

## 8. Common mistakes to avoid

| Mistake | What happens | Fix |
|---|---|---|
| Complementing against an infinite universe | `A!` returns garbage, or never terminates | The universe is the **union of the inputs** |
| Building the universe from one set only | `A!` wrong whenever another set adds elements | Union **all** the parameter sets |
| Expecting `A!` to be non-empty | With one set, the complement is always `[]` | That's correct (section 2.1) |
| Returning duplicates | A set has no repeats | Use a set type internally |
| Forgetting `>` is not commutative | `AB>` ≠ `BA>` | Pop right before left (Exercise 03's trap) |
| Hard-coding the variable order | `B` must map to the **second** set | Map by alphabet position |
| Not checking the set count | Undefined behaviour per the subject | Compare counts, report a mismatch |
| Worrying about output order | Order is explicitly irrelevant | Sort it for convenience |

---

## 9. Do this on paper

1. **The three examples by hand.** For each, write the universe first, then
   evaluate. The third one is the important one — convince yourself why `[]` is
   right.

2. **Compute `A!` twice:** with `A = {1,2}` alone, then with `A = {1,2}` and
   `B = {3}`. Explain in one sentence why the answers differ.

3. **Build a membership table.** For `A = {0,1,2}`, `B = {0,3,4}` and formula
   `AB^`, make a row per element of the universe with columns "in A?", "in B?",
   "A ⊕ B?". Read off the result set and check with the program.

4. **De Morgan on sets:** evaluate `AB|!` and `A!B!&` by hand with
   `A = {0,1,2}`, `B = {2,3,4}`. They should match — and both give `[]`. Why?

5. **Material condition:** evaluate `AB>` with `A = {0,1,2}`, `B = {2,3}`.
   Predict the answer from `Aᶜ ∪ B` before running it.

6. **Translate back:** take the formula `AB&!` and say what it means in plain
   English, both as logic ("not both…") and as sets ("everything except…").

---

## 10. Peer-review preparation

- **"What does your function do?"** → Evaluates an RPN formula where the
  variables are sets, using the logic↔set correspondence: `!`→complement,
  `&`→intersection, `|`→union.
- **"What is the universe?"** → The union of all the sets passed in. The
  subject states it in a red box, and complement is meaningless without it.
- **"Why does `A!` return an empty list?"** → With one set, that set *is* the
  universe, so nothing lies outside it. Add a second set and the answer changes.
- **"How is this different from Exercise 03?"** → It isn't, structurally. Same
  stack machine; only the operations on the popped values differ.
- **"How do `>` and `=` work on sets?"** → Same identities as Exercise 05:
  `A⇒B` is `Aᶜ ∪ B`; `A⇔B` is "in both, or in neither".
- **"How do you know it's correct?"** → The membership property: `x` is in the
  result exactly when the boolean formula is true over "is `x` in each set?".
  Verified on 14,000 formula/set combinations. Show `-v`.
- **"What if the counts don't match?"** → The subject calls it undefined and
  invites an error message, so both the count and the alphabet index are
  checked.
- **"Does output order matter?"** → No — the subject says so explicitly. Sorted
  for convenience.
- **"Where's your parser from?"** → Imported from Ex05, not copied.

---

## 11. What's next — the mandatory part is done

**Ex00 through Ex09 are complete.** Exercises 10 and 11 (Curve and Inverse
function) are marked **not mandatory** in the subject, so the required work
finishes here.

If you want to continue, **Interlude 03 (Chapter XVI)** introduces them: common
number sets (ℕ, ℤ, ℚ, ℝ, ℂ) and their relationship to C types, then space-filling
curves. Exercise 10 maps a pair `(x, y)` of `u16`s to a single `f64` in `[0,1]`
bijectively — the standard approach is the **Z-order (Morton) curve**, which
interleaves the bits of `x` and `y`. Exercise 11 inverts it by de-interleaving.

That would be a fourth outing for the bit manipulation from Ex00–Ex02, which is
a satisfying way to close the module — but it is optional, and a complete Ex00–
Ex09 is a complete submission.

Before the defense, two things worth doing:

1. **Run every exercise once from a clean checkout**, from the repo root and
   from inside each folder, to confirm the Ex05→Ex06→Ex07 and Ex05→Ex09 imports
   resolve.
2. **Re-read the complexity sections.** They're the one criterion the subject
   says is checked at peer review, and `n` means something different in almost
   every exercise.