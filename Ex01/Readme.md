# Exercise 01 — Multiplier

> **Goal:** write `multiplier(a, b)` that returns `a * b`, without using `*`.
>
> **Allowed operators:** `&` `|` `^` `<<` `>>` `=` and the comparisons `== != < > <= >=`
> **Required complexity:** O(1) time, O(1) space

---

## 0. Before you start

Same advice as Exercise 00: keep a pen nearby. Section 9 has paper exercises.

This exercise is much easier than the last one *if* you genuinely understood
Exercise 00, because the hard part — adding without `+` — is already solved. The
new idea here is small. The tricky part of this exercise is not the algorithm,
it's the **complexity requirement**, which changed from `O(log n)` to `O(1)`.
Section 5 deals with that carefully, because it is the most likely thing an
evaluator will probe.

---

## 1. New vocabulary

| Word | Meaning |
|---|---|
| **partial product** | In long multiplication, one of the intermediate rows you add up at the end. |
| **shift-and-add** | The standard name for the binary multiplication algorithm in this exercise. |
| **power of two** | 1, 2, 4, 8, 16, 32… i.e. `2⁰, 2¹, 2², 2³…`. Each binary column is worth one of these. |
| **decomposition** | Writing a number as a sum of other numbers. Here: writing `b` as a sum of powers of two. |

Everything else (bit, binary, u32, mask, carry) carries over from Exercise 00.

---

## 2. How do humans multiply? Steal their method again

Exercise 00 worked by copying school-style column addition. This exercise does
exactly the same thing with school-style long multiplication.

Take `13 × 11` in decimal:

```
      13
    × 11
    ----
      13     <- 13 × 1   (the units digit of 11)
   + 130     <- 13 × 10  (the tens digit of 11)
    ----
     143
```

What actually happened there? You **broke 11 into its digits by place value**:

```
11 = 1×10 + 1×1
```

then multiplied 13 by each piece and added the results. Those intermediate rows
(`13` and `130`) are the **partial products**.

### 2.1 The same thing in binary

Binary makes this dramatically simpler, because **every digit is either 0 or 1**.
There is no "multiply by 7" case — you either take the row, or you don't.

Write `11` in binary:

```
   8   4   2   1     <- what each column is worth
   1   0   1   1     <- the bits of 11
```

So `11 = 8 + 2 + 1`. Therefore:

```
13 × 11  =  13 × (8 + 2 + 1)
         =  13×8  +  13×2  +  13×1
         =  104   +   26   +   13
         =  143
```

### 2.2 The key realisation

Now recall from Exercise 00 that **shifting left by one multiplies by two**:

```
  13 << 0  =  13       (13 × 1)
  13 << 1  =  26       (13 × 2)
  13 << 2  =  52       (13 × 4)
  13 << 3  = 104       (13 × 8)
```

Multiplying by a power of two is *free* — it's just a shift. And any number `b`
is a sum of powers of two, which is precisely what its binary representation
tells you. Putting those two facts together:

> **To multiply `a` by `b`: look at each bit of `b`. Wherever the bit is 1, add
> the correspondingly shifted copy of `a` into the result.**

That's the entire algorithm. We already know how to add (Exercise 00) and how to
shift, so we're done.

---

## 3. The algorithm

```
result = 0
while b is not 0:
    if the lowest bit of b is 1:
        result = result + a        # using adder() from Exercise 00
    a = a << 1                     # a now represents the next power of two
    b = b >> 1                     # look at the next bit of b
return result
```

Two small tricks to notice:

- **`b & 1`** isolates the lowest bit of `b`. If that bit is 1, the result of
  `b & 1` is 1; otherwise 0. (Check it against the AND truth table: `&` with `1`
  keeps the last bit and zeroes everything else.)
- Instead of indexing into bit positions, we **shift `b` right** by one each
  round. That moves the next bit down into the lowest position, so `b & 1`
  always inspects the bit we care about. When `b` runs out of 1-bits it becomes
  0 and the loop ends.

### 3.1 Worked example: 13 × 11 = 143

Do this on paper before reading the table. `a` starts at 13, `b` at 11 (`1011`).

| step | `b` in binary | lowest bit | `a` (shifted) | action | result |
|---|---|---|---|---|---|
| 0 | `1011` | **1** | 13 | add 13 | 13 |
| 1 | `101` | **1** | 26 | add 26 | 39 |
| 2 | `10` | 0 | 52 | bit is 0, skip | 39 |
| 3 | `1` | **1** | 104 | add 104 | **143** |

`b` is now 0, so we stop. **Answer: 143.** ✓

Notice the result column: `13 + 26 + 104 = 143`, exactly the three partial
products from section 2.1. The step where the bit was 0 contributed nothing —
that's the `4` column, and `11` has no `4` in it.

The program prints this exact table:

```bash
python3 multiplier.py -t 13 11
```

### 3.2 Why does the loop always stop?

`b = b >> 1` throws away one bit of `b` on every single iteration, and never
adds any. A 32-bit number has 32 bits, so after at most 32 iterations `b` has
been emptied and equals 0. There is no input that can make this loop run
forever.

This is worth stating clearly at a defense, because it's also the basis of the
complexity argument in section 5.

---

## 4. The 32-bit mask (same as Exercise 00)

Python integers grow without limit, so we enforce `u32` behaviour ourselves with
`& MASK_32` where `MASK_32 = 0xFFFFFFFF`. See Exercise 00's README section 4 for
the full explanation.

Multiplication overflows much faster than addition, so you'll see wraparound
often here:

```bash
$ python3 multiplier.py 65536 65536
0
```

That's correct. The true answer is `65536 × 65536 = 4294967296 = 2³²`, which
needs 33 bits. The lowest 32 bits of `2³²` are all zero, so a real `u32` also
gives 0. Another one worth knowing:

```bash
$ python3 multiplier.py 4294967295 4294967295
1
```

Surprising but correct — `(2³²−1)² = 2⁶⁴ − 2³³ + 1`, and both of the first two
terms vanish when truncated to 32 bits, leaving exactly 1.

Note **where** the mask is applied in the code: on `a` after each shift, and
inside `adder`. Masking `a` matters — without it, `a` would keep doubling into a
huge Python integer for all 32 rounds even after it stopped being relevant.

---

## 5. Complexity — read this section twice

The subject asks for **O(1) time and O(1) space** here, where Exercise 00 asked
for **O(log n)**. Both exercises have one loop bounded by the bit-width, so this
looks like a contradiction. It isn't, and being able to explain why is worth
real points.

### 5.1 What O(1) means here

`u32` is a **fixed-size** type. It is always exactly 32 bits, no matter what
value it holds. Since `b >> 1` discards one bit per iteration, the loop runs **at
most 32 times — for every possible input**. Not "32 times for big inputs and
fewer for small ones" in an asymptotic sense; 32 is a hard ceiling that does not
grow with anything, because there is no input large enough to make it grow.

A bound that does not grow with the input is, by definition, constant:

- **Time:** ≤ 32 iterations, each doing a bounded amount of work (one AND, one
  comparison, one `adder` call which is itself ≤ 32 bounded steps, two shifts) →
  **O(1)** ✓
- **Space:** three integer variables (`a`, `b`, `result`), each 32 bits. No list,
  no recursion, nothing that grows → **O(1)** ✓

### 5.2 So why was Exercise 00 called O(log n)?

Because you can describe the same loop from two angles, and the subject picks a
different one in each exercise:

| Point of view | Adder | Multiplier |
|---|---|---|
| Counting in terms of the input **value** `n` | O(log n) | O(log n) |
| Counting for a **fixed 32-bit type** | O(1) | O(1) |

Both rows are internally consistent. The subject simply states Exercise 00's
bound in the first style and Exercise 01's in the second. **Neither phrasing
changes what code you should write.**

What actually matters — and what the evaluator is really checking — is the same
in both exercises:

> **Your loop must be driven by the *bits* of the input, never by its *value*.**

If you can say that sentence and mean it, you have satisfied both requirements
at once, and you can handle the question whichever way it's asked.

### 5.3 The failure this requirement exists to catch

There's a much simpler way to multiply, and it's the wrong one:

```python
# DO NOT DO THIS
result = 0
for _ in range(b):          # loop runs b times!
    result = adder(result, a)
```

This produces correct answers. It would pass every output test you throw at it.
And it **fails the exercise**, because the loop runs `b` times. With
`b = 4294967295` that's over four billion iterations — your evaluator would be
waiting for minutes instead of microseconds. That is O(n), not O(1).

This is the single thing the complexity requirement is designed to catch. The
whole point of shift-and-add is turning four billion steps into 32.

### 5.4 Demonstrating it live

`-t` numbers every iteration, so you can show the bound directly:

```bash
python3 multiplier.py -t 9 1            # 1 iteration
python3 multiplier.py -t 9 255          # 8 iterations
python3 multiplier.py -t 9 65535        # 16 iterations
python3 multiplier.py -t 9 4294967295   # 32 iterations  <- the ceiling
```

The second operand grows from 1 to four billion; the work goes from 1 step to
32 and then stops. It cannot exceed 32 no matter what you type. That ceiling is
the O(1) claim, made visible.

Note that only the **bits of `b`** drive the loop count — `a`'s value is
irrelevant. `multiplier(4294967295, 1)` runs a single iteration.

---

## 6. The code, line by line

```python
def multiplier(a: int, b: int) -> int:
    a = a & MASK_32
    b = b & MASK_32
    result = 0

    while b != 0:                       # while b still has 1-bits left
        if (b & 1) != 0:                # is the lowest bit of b a 1?
            result = adder(result, a)   # yes -> this power of two counts

        a = (a << 1) & MASK_32          # next power of two: double a
        b = b >> 1                      # move to the next bit of b

    return result
```

**Operator check** — every operator used is on the allowed list:

| Used | Allowed? |
|---|---|
| `&` | ✔ bitwise AND |
| `^` | ✔ bitwise XOR (inside `adder`) |
| `<<` | ✔ left shift |
| `>>` | ✔ right shift |
| `=` | ✔ assignment |
| `!=` | ✔ comparison |

No `*`, no `+`, no `range(b)`, no library function. ✓

`if` and `while` are control flow, not operators, so they are not restricted.

### 6.1 Why `adder` is duplicated in this file

`multiplier.py` contains its own copy of `adder` from Exercise 00, rather than
importing it from `../ex00/`. Two reasons:

1. **The folder runs standalone.** An evaluator can `cd ex01` and run it without
   the rest of the repo being present or importable.
2. **Cross-folder imports in Python are awkward** — `ex00` is not a package, so
   importing from a sibling directory needs `sys.path` manipulation, which is
   ugly and fragile.

The subject explicitly permits reusing your earlier functions, and duplication
is the normal approach in 42 repos. If you'd rather have a single shared module,
the alternative is a `utils/` package at the repo root imported by every
exercise — say the word and I'll restructure.

---

## 7. How to run it

```bash
cd ex01

python3 multiplier.py 5 3           # -> 15
python3 multiplier.py 13 11         # -> 143
python3 multiplier.py 65536 65536   # -> 0   (correct u32 wraparound)
```

With no arguments, a short demo table. With `-t`, the step-by-step table from
section 3.1. Bad input (missing args, non-numbers, negatives, values over 32
bits) is rejected with a clear message.

### Useful values to try during a defense

| Command | Result | What it shows |
|---|---|---|
| `python3 multiplier.py 3 5` | `15` | The basic case |
| `python3 multiplier.py 0 7` | `0` | Zero on the left |
| `python3 multiplier.py 7 0` | `0` | Zero on the right — loop never runs |
| `python3 multiplier.py 1 42` | `42` | Multiplying by one |
| `python3 multiplier.py 42 1` | `42` | Commutativity check |
| `python3 multiplier.py 255 255` | `65025` | Larger values |
| `python3 multiplier.py 65536 65536` | `0` | Overflow wraps to zero |
| `python3 multiplier.py 4294967295 4294967295` | `1` | The surprising max × max |

---

## 8. Common mistakes to avoid

| Mistake | What happens | Fix |
|---|---|---|
| Looping `b` times instead of over b's bits | Correct answers, but O(n) — **fails the exercise** | Shift-and-add (section 5.3) |
| Shifting `b` left instead of right | The loop never terminates, or reads the wrong bits | `b = b >> 1` |
| Forgetting to double `a` each round | Every partial product uses the same `a`; you compute a bit-count, not a product | `a = (a << 1)` every iteration |
| Doubling `a` only when the bit is 1 | The powers of two fall out of sync with b's columns | Shift `a` on **every** iteration, inside or outside the `if` |
| Using `b & 1 == 1` without parentheses | In Python, `==` binds tighter than `&`, so this parses as `b & (1 == 1)` | Write `(b & 1) != 0` |
| Not masking `a` after shifting | `a` grows into a huge Python integer over 32 rounds | `a = (a << 1) & MASK_32` |
| Using `+` to accumulate the result | Breaks the rules | Call your `adder` |

That parenthesis one is a genuine Python trap and worth remembering — the
operator precedence differs from C here.

---

## 9. Do this on paper

1. **Decompose into powers of two:** write 5, 12, 25 and 100 as sums of powers
   of two. Check each against its binary representation.

2. **Trace `multiplier(5, 3)` by hand** using the table format from section 3.1.
   You should need 2 iterations and land on 15. Write down `b`'s binary form,
   the lowest bit, `a`, and the result at every step.

3. **Trace `multiplier(7, 4)` by hand.** This one is interesting: `4` is `100`,
   so the first two iterations both skip. Convince yourself why the answer is
   still 28 and why the loop still runs 3 times.

4. **Answer in writing:** why must `a` be shifted on *every* iteration, and not
   only when the current bit of `b` is 1? Trace `multiplier(3, 5)` both ways and
   compare the results — the wrong version gives 9 instead of 15.

5. **Predict, then check:** how many iterations does `multiplier(4294967295, 1)`
   take? What about `multiplier(1, 4294967295)`? Explain the difference, then
   verify with `-t`.

---

## 10. Peer-review preparation

- **"Explain your algorithm."** → `b` in binary is a sum of powers of two. For
  each 1-bit of `b`, add the matching shifted copy of `a`. Shifting left is
  multiplying by two, so each shifted copy is one partial product.
- **"Why is it O(1)?"** → The loop discards one bit of `b` per iteration, and
  `b` is a fixed 32-bit type, so it runs at most 32 times for any input. A bound
  that never grows is constant.
- **"But Exercise 00 was O(log n) with the same loop shape…"** → Same loop, two
  ways of phrasing the bound: in terms of the input value it's O(log n), for a
  fixed-width type it's O(1). What matters in both is that the loop is driven by
  bits, never by the value. (Section 5.2.)
- **"Why not just add `a` to itself `b` times?"** → That's O(n); four billion
  iterations in the worst case. Shift-and-add does it in 32.
- **"Why does it terminate?"** → `b >> 1` removes a bit every iteration and
  never adds one, so `b` reaches 0 within 32 rounds.
- **"Why is `multiplier(65536, 65536)` zero?"** → The true product is `2³²`,
  whose lowest 32 bits are all zero. Correct `u32` wraparound.
- **"Show me it works."** → Ask them for any two numbers and run it. The table
  in section 7 has good values if they want suggestions.
- **"Show me it respects the complexity."** → Run the four `-t` commands from
  section 5.4 and point at the 32-iteration ceiling.

---

## 11. What's next

Exercise 02 (Gray code) is the shortest exercise in the whole module — the
implementation is a single expression. It closes out the "pure bit manipulation"
block. After that, Exercise 03 changes gear completely: parsing and evaluating
logical formulas, where you'll build the tree structure that exercises 04
through 09 all depend on.