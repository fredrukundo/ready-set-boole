# Exercise 00 — Adder

> **Goal:** write `adder(a, b)` that returns `a + b`, without ever using `+`.
>
> **Allowed operators:** `&` `|` `^` `<<` `>>` `=` and the comparisons `== != < > <= >=`
> **Required complexity:** O(log n) time, O(log n) space

---

## 0. Before you read any code: get a pen

The subject explicitly recommends paper, and this exercise is the single best
one to start that habit. At the end of this file there is a section called
**"Do this on paper"** with three exercises. Do them *before* you read the
solution code if you can — the algorithm is much easier to believe once your
own hand has produced it.

---

## 1. Vocabulary you need

These are the words peer evaluators will use. Learn them now; they come back in
every exercise of this module.

| Word | Meaning |
|---|---|
| **bit** | A single 0 or 1. The smallest piece of information a computer has. |
| **binary** | Base 2. We write numbers using only the digits 0 and 1. |
| **natural number** | A whole number ≥ 0 (0, 1, 2, 3, …). Written `ℕ`. |
| **u32** | "Unsigned 32-bit integer". A natural number stored in exactly 32 bits. Range: `0` to `4294967295` (= 2³² − 1). |
| **bitwise operator** | An operator that works on each bit position independently, not on the number as a whole. |
| **carry** | In addition, the digit you "carry over" to the next column on the left when a column overflows. |
| **overflow / wraparound** | What happens when a result is too big for its number of bits: the extra bits are thrown away. |
| **invariant** | A statement that stays true at every step of a loop. Very useful to prove a loop is correct. |

### 1.1 Counting in binary

In decimal (base 10), each column is worth ten times the column to its right:

```
   thousands  hundreds  tens  units
      1000       100     10     1
```

In binary (base 2), each column is worth **two** times the column to its right:

```
   128   64   32   16   8   4   2   1
```

So the binary number `1101` means:

```
   8   4   2   1     <- what each column is worth
   1   1   0   1     <- the bits
   = 8 + 4 + 0 + 1
   = 13
```

Write this out by hand a few times for 0 through 16. It will pay off for the
next twelve exercises.

### 1.2 The bitwise operators, with truth tables

A **truth table** lists every possible input combination and the output. You will
build these by hand constantly in this module (Exercise 04 is literally about
printing them), so get comfortable now.

**AND (`&`)** — result bit is 1 only if **both** input bits are 1:

| a | b | a & b |
|---|---|---|
| 0 | 0 | 0 |
| 0 | 1 | 0 |
| 1 | 0 | 0 |
| 1 | 1 | **1** |

**OR (`|`)** — result bit is 1 if **at least one** input bit is 1:

| a | b | a \| b |
|---|---|---|
| 0 | 0 | 0 |
| 0 | 1 | 1 |
| 1 | 0 | 1 |
| 1 | 1 | 1 |

**XOR (`^`)**, "exclusive or" — result bit is 1 if the inputs are **different**:

| a | b | a ^ b |
|---|---|---|
| 0 | 0 | 0 |
| 0 | 1 | 1 |
| 1 | 0 | 1 |
| 1 | 1 | **0** |

Applied to whole numbers, these work column by column:

```
    a = 1101   (13)
    b = 1011   (11)
        ----
a & b = 1001   ( 9)    1 only where BOTH have 1
a | b = 1111   (15)    1 where AT LEAST ONE has 1
a ^ b = 0110   ( 6)    1 where they DIFFER
```

**Left shift (`<<`)** — move all bits one position to the left, put a 0 on the
right. This multiplies by 2:

```
  5 << 1   ->   0101 becomes 1010   ->  10
  3 << 2   ->   0011 becomes 1100   ->  12
```

**Right shift (`>>`)** — move all bits to the right, dropping the rightmost one.
This divides by 2 (throwing away any remainder):

```
  10 >> 1  ->   1010 becomes 0101   ->  5
   7 >> 1  ->   0111 becomes 0011   ->  3   (the .5 is lost)
```

---

## 2. How do humans add? Let's steal their method

Take `47 + 25` in decimal, the way you learned in primary school:

```
      1          <- the carry
     47
   + 25
   ----
     72
```

Two things happened in each column:

1. A **sum digit** was written down.
2. Sometimes a **carry** was pushed to the next column on the left.

Binary addition works exactly the same way, but with only four possible column
cases:

| bit of a | bit of b | sum bit written | carry produced |
|---|---|---|---|
| 0 | 0 | 0 | 0 |
| 0 | 1 | 1 | 0 |
| 1 | 0 | 1 | 0 |
| 1 | 1 | **0** | **1** |

That last row is the interesting one: `1 + 1 = 2`, and 2 in binary is `10`. So we
write down a `0` and carry a `1`.

### 2.1 The key realisation

Now look very carefully at the two rightmost columns of that table and compare
them with the truth tables from section 1.2:

- The **"sum bit written"** column is `0, 1, 1, 0` — **that is exactly XOR.**
- The **"carry produced"** column is `0, 0, 0, 1` — **that is exactly AND.**

This is the whole exercise. Everything else is bookkeeping.

```
sum without carrying   =   a ^ b
where carries happen   =   a & b
```

And because a carry belongs to the *next column to the left*, we shift it:

```
the carries, placed correctly   =   (a & b) << 1
```

---

## 3. The algorithm

We now have two numbers instead of one:

- `a ^ b` — the partial sum, ignoring all carries
- `(a & b) << 1` — all the carries, waiting to be added in

Their total is still exactly `a + b`. Nothing was lost, nothing was invented.
So we can just **repeat the same trick** on those two new numbers:

```
while there are still carries to add:
    carry = (a & b) << 1     # find the carries
    a     = a ^ b            # add without carrying
    b     = carry            # the carries become the new number to add
return a
```

### 3.1 Worked example: 13 + 11 = 24

Do this one on paper before reading the table.

```
Start:   a = 1101 (13)      b = 1011 (11)
```

**Step 1**

```
  a & b  = 1101 & 1011 = 1001  (9)        -> carries are in positions 0 and 3
  <<1                  = 10010 (18)       -> shift them one column left
  a ^ b  = 1101 ^ 1011 = 0110  (6)        -> sum without carrying

  new a = 6,  new b = 18       (check: 6 + 18 = 24 ✓ still the same total)
```

**Step 2**

```
  a & b  = 00110 & 10010 = 00010 (2)
  <<1                    = 00100 (4)
  a ^ b  = 00110 ^ 10010 = 10100 (20)

  new a = 20,  new b = 4       (check: 20 + 4 = 24 ✓)
```

**Step 3**

```
  a & b  = 10100 & 00100 = 00100 (4)
  <<1                    = 01000 (8)
  a ^ b  = 10100 ^ 00100 = 10000 (16)

  new a = 16,  new b = 8       (check: 16 + 8 = 24 ✓)
```

**Step 4**

```
  a & b  = 10000 & 01000 = 00000 (0)
  <<1                    = 00000 (0)
  a ^ b  = 10000 ^ 01000 = 11000 (24)

  new a = 24,  new b = 0       <- b is 0, we stop
```

**Answer: 24.** ✓

The program prints exactly this trace when you run it (section `[5]` of the
output), so you can check your paper work against it.

### 3.2 Why does the loop always stop?

This is a question a peer evaluator may well ask, so here is the answer.

Look at the carry: `(a & b) << 1`. The `<< 1` means every carry moves **one
position to the left**, and it can never move right. The rightmost 1-bit of `b`
therefore moves strictly leftward on every iteration. Since we only have 32 bit
positions, after at most 32 iterations every carry has been pushed off the left
edge of the number, and `b` becomes 0.

**The loop invariant:** at the start of every iteration, `a + b` (mathematically)
equals the original `a + b`. Step 1 of the loop moves some information from `b`
into `a` without changing the total; when `b` finally reaches 0, `a` alone holds
the whole total. That is why returning `a` is correct.

---

## 4. The Python-specific trap: `MASK_32`

This is the one thing that trips people up when they do this module in Python
instead of Rust or C++.

In Rust, `u32` is enforced by the language: if a value exceeds 32 bits, the
extra bits are physically gone. **Python integers have no size limit** — they
grow as large as you want. So if you don't do anything, `adder` in Python will
happily return a 33-bit number where a real `u32` would have wrapped around to 0.

The fix is a **mask**:

```python
MASK_32 = 0xFFFFFFFF
```

`0xFFFFFFFF` is hexadecimal for a number whose lowest 32 bits are all 1:

```
0xFFFFFFFF = 11111111111111111111111111111111  (32 ones)
           = 4294967295
```

`x & MASK_32` keeps only the lowest 32 bits of `x` and discards everything
above, which is precisely what a hardware `u32` does. And since `&` is one of
the allowed operators, this is completely legal for the exercise.

You can see the effect by running it:

```
$ python3 adder.py 4294967295 1
0                     <- correct u32 behaviour: it wraps around
```

Without the mask, Python would have printed `4294967296`, which is not a valid
`u32` value at all.

---

## 5. Complexity analysis

The subject requires **O(log n)** time and space, and says these "will be checked
during peer review". Section 5.3 explains what that check actually consists of.

### 5.1 The reasoning

**Why O(log n) and not O(n)?** Because "n" here means the *value* of the input,
and the number of bits needed to write a number `n` in binary is about `log₂(n)`.
For example 1,000,000 needs only 20 bits. Our loop runs at most once per bit
position, so:

- **Time:** at most `log₂(n)` ≈ 32 iterations, each doing a constant amount of
  work (one AND, one shift, one XOR, one comparison) → **O(log n)** ✓
- **Space:** we store three numbers (`a`, `b`, `carry`), each of `log₂(n)` bits.
  We never allocate a list, and we never recurse, so nothing grows with the
  input → **O(log n)** ✓

> **A note on the convention.** In this module, `n` is the *value* of the
> number, not the number of bits. That is why adding is O(log n) rather than
> O(n): the work is proportional to the number of *digits*, and a number of
> value `n` has about `log₂(n)` binary digits. Keep this straight — it is the
> single most common confusion in this exercise.

### 5.2 Showing it empirically

You don't have to take the argument on faith. The `-t` flag numbers each
iteration, so you can watch the count grow with the number of **bits**, not
with the value:

```bash
python3 adder.py -t 1 1              # 2 iterations   (1 is 1 bit)
python3 adder.py -t 255 1            # 9 iterations   (255 is 8 bits)
python3 adder.py -t 65535 1          # 17 iterations  (65535 is 16 bits)
python3 adder.py -t 4294967295 1     # 32 iterations  (the 32-bit maximum)
```

Look at what that sequence means. The input value grows from 1 to about four
billion — a factor of four *billion* — while the work grows from 2 steps to 32
steps, a factor of 16. Multiplying the input by 256 adds only 8 iterations.
That is precisely the signature of logarithmic growth, and it is a far more
convincing demonstration than any verbal argument.

Two useful measured facts to have in your pocket:

- Worst case over **every** pair in `0..1023`: **11 iterations**
- Worst case over 200,000 random full-range u32 pairs: **21 iterations**

The absolute worst case is 32, reached by `adder(4294967295, 1)` — a carry that
has to ripple through all 32 positions. It can never exceed 32, because there
are only 32 bit positions for a carry to travel through.

### 5.3 How complexity is *actually* "checked during peer review"

This confuses nearly everyone the first time. There is **no automated tool** and
no profiler. The evaluation is a conversation. Concretely, the evaluator will do
some mix of these three things:

**1. Read your code and count the loops.** This is the main check. They look at
the structure and ask: how many times can this loop run, as a function of the
input? One loop bounded by the bit-width is O(log n). A loop that runs `b` times
(e.g. "add 1 to `a`, `b` times") would be O(n) and would **fail** this exercise,
even though it produces the correct answer. Correct output is not enough here —
the *shape* of the algorithm is part of the requirement.

**2. Ask you to explain it out loud.** Something like "why is this O(log n)?"
You answer with section 5.1: one iteration per bit position, and a number of
value `n` has `log₂(n)` bits.

**3. Possibly ask for a demonstration.** That's what section 5.2 is for. Run the
four `-t` commands and let them watch the iteration count barely move while the
input explodes.

**The red flags they're looking for** — these are what "failing the complexity
check" actually looks like:

| Red flag | Why it fails |
|---|---|
| A loop that runs `b` times (repeated increment) | O(n), not O(log n) — far too slow |
| Nested loops over bit positions | O(log² n) instead of O(log n) |
| Building a list/array of bits | Allocates memory proportional to input → space too high |
| Deep recursion without justification | The call stack is memory; must still be O(log n) |
| Converting to a string of digits and back | Usually hides an allocation and an extra pass |

Our implementation has one loop, three integer variables, no allocation and no
recursion — so all five red flags are absent. That is the whole argument, and
you should be able to say it in one sentence:

> *"One loop, bounded by the number of bits; three scalar variables, no
> allocation, no recursion."*

---

## 6. The code, line by line

```python
MASK_32 = 0xFFFFFFFF

def adder(a: int, b: int) -> int:
    a = a & MASK_32          # behave like u32: keep only 32 bits
    b = b & MASK_32

    while b != 0:            # while there are still carries to add
        carry = (a & b) << 1 # find carries, move them one column left
        a = (a ^ b) & MASK_32# add without carrying
        b = carry & MASK_32  # the carries become the next thing to add

    return a                 # no carries left -> a holds the full sum
```

**Operator check** — every operator used is on the allowed list:

| Used | Allowed? |
|---|---|
| `&` | ✔ bitwise AND |
| `^` | ✔ bitwise XOR |
| `<<` | ✔ left shift |
| `=` | ✔ assignment |
| `!=` | ✔ comparison |

No `+`, no `-`, no `*`, no `sum()`, no library function. ✓

> **Note on the tests:** inside `main()` the tests *do* use Python's `+` to
> compute the expected value. That is fine and expected — the restriction
> applies to how `adder()` computes its result, not to how we check it. Using
> the real `+` in the test is exactly how we prove `adder()` is correct.

---

## 7. How to run it

There is a single file, `adder.py`. It takes numbers **from the command line**,
so an evaluator can type whatever they like instead of you having to edit the
file:

```bash
cd ex00

python3 adder.py 5 3           # -> 8
python3 adder.py 42 58         # -> 100
python3 adder.py 4294967295 1  # -> 0   (correct u32 wraparound)
```

With no arguments, it prints a short demo table of eight examples:

```bash
python3 adder.py
```

With `-t` (or `--trace`), it prints the algorithm step by step — useful when
an evaluator asks "show me how it works", and for checking your paper work
against section 3.1 above:

```bash
python3 adder.py -t 13 11
```

```
  adder(13, 11)

  step |            a  (sum so far) |     b  (carry left to add)
  --------------------------------------------------------------
     0 |             1101 (     13) |             1011 (     11)
     1 |              110 (      6) |            10010 (     18)
     2 |            10100 (     20) |              100 (      4)
     3 |            10000 (     16) |             1000 (      8)
     4 |            11000 (     24) |                0 (      0)

  b reached 0  ->  result = 24
```

Bad input is rejected with a clear message: missing arguments, non-numbers,
negative values, and values that don't fit in 32 bits.

### Useful values to try during a defense

| Command | Result | What it shows |
|---|---|---|
| `python3 adder.py 5 3` | `8` | The basic case |
| `python3 adder.py 0 0` | `0` | Both zero |
| `python3 adder.py 7 1` | `8` | A carry rippling through every bit |
| `python3 adder.py 2147483647 1` | `2147483648` | Crossing the signed 32-bit boundary |
| `python3 adder.py 4294967295 1` | `0` | Correct u32 wraparound |
| `python3 adder.py 4294967295 4294967295` | `4294967294` | Max + max |

---

## 8. Common mistakes to avoid

| Mistake | What happens | Fix |
|---|---|---|
| Forgetting `<< 1` on the carry | Carries get added to the wrong column; results are wrong | The carry belongs to the **next column left** |
| Updating `a` before computing `carry` | `carry` is computed from the already-changed `a`, giving garbage | Compute `carry` **first**, or use simultaneous assignment |
| Forgetting the mask in Python | Results exceed 32 bits and don't match real `u32` behaviour | Mask with `& MASK_32` after every operation |
| Using `while b > 0` with signed thinking | Fine here (inputs are natural numbers), but `!= 0` is clearer and safer | Use `while b != 0` |
| Using `+=` to build the result | Breaks the rules — the subject only allows `++`/`+=` for **loop counters** | Use only the allowed operators |

---

## 9. Do this on paper

Before moving to Exercise 01, do these by hand. Check yourself by running the
program afterwards.

1. **Convert to binary and back:** write 0 through 20 in binary. Then convert
   `10110`, `11111`, `100000` back to decimal.

2. **Trace `adder(5, 3)` by hand** using the table format from section 3.1. You
   should need 3 iterations and land on 8. Write down `a`, `b`, `a & b`,
   `(a & b) << 1` and `a ^ b` at every step.

3. **Trace `adder(7, 1)` by hand.** This one is interesting: it produces a chain
   of carries that ripples all the way up (`0111 + 0001 = 1000`). Count how many
   iterations it takes and convince yourself why it's more than for `5 + 3`.

4. **Answer this in writing:** why is `(a & b) << 1` and not `(a | b) << 1`?
   Use the truth table from section 2 to explain it in one sentence.

---

## 10. Peer-review preparation

Questions an evaluator is likely to ask, with short answers you should be able
to give without notes:

- **"Explain your algorithm."** → XOR gives the sum without carries, AND gives
  where carries occur, shift left by 1 places them in the right column, repeat
  until no carries remain.
- **"Why does it terminate?"** → The carry shifts strictly leftward each
  iteration, so after at most 32 steps it falls off the end and `b` becomes 0.
- **"Justify O(log n)."** → One iteration per bit; a number `n` has ~`log₂(n)`
  bits.
- **"What is `MASK_32` for?"** → Python has unbounded integers; the mask
  reproduces `u32` wraparound behaviour.
- **"What happens on overflow?"** → It wraps around, exactly like a real `u32`.
  `4294967295 + 1` gives `0`. Run `python3 adder.py 4294967295 1`.
- **"Show me it works."** → Ask them for any two numbers and run
  `python3 adder.py <a> <b>`. Offer the table in section 7 if they want ideas.
- **"Show me it respects the complexity."** → Run the four `-t` commands from
  section 5.2 and point out that the input grows by a factor of four billion
  while the iteration count goes from 2 to 32.

---

## 11. What's next

Exercise 01 (Multiplier) **reuses this `adder` function directly** — binary
multiplication is "shift and add", where the "add" is exactly what you just
built. Make sure you are genuinely comfortable with sections 2 and 3 before
moving on, because a misunderstanding here will resurface immediately.