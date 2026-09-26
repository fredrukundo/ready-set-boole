# Exercise 02 — Gray code

> **Goal:** write `gray_code(n)` returning the Gray code equivalent of `n`.
>
> **Allowed mathematical functions:** None
> **Required complexity:** N/A (the subject sets no bound — ours is O(1))

---

## 0. Before you start

This is the **shortest exercise in the module**. The implementation is a single
expression:

```python
return n ^ (n >> 1)
```

That's it. But don't skip the reading — an evaluator will absolutely ask *why*
that works, and "I found it online" is a bad answer for a one-line function.
There is nowhere to hide in a one-liner, so this is the exercise where
understanding matters most relative to the amount of code.

The subject gives no complexity bound here, which means the defense will lean
almost entirely on **explanation** rather than demonstration. Sections 3 and 4
are the ones to know cold.

---

## 1. What is a Gray code, and why does it exist?

**Gray code is a way of ordering binary numbers so that any two consecutive
values differ by exactly one bit.**

Ordinary binary does not have this property. Watch what happens going from 7 to
8:

```
  7  =  0111
  8  =  1000
        ^^^^   all four bits change at once
```

Or 3 to 4:

```
  3  =  0011
  4  =  0100
         ^^^   three bits change
```

Gray code fixes this. Here is the same range in Gray code:

| n | binary | gray(n) | gray in binary | bits changed |
|---|---|---|---|---|
| 0 | `0000` | 0 | `0000` | — |
| 1 | `0001` | 1 | `0001` | 1 |
| 2 | `0010` | 3 | `0011` | 1 |
| 3 | `0011` | 2 | `0010` | 1 |
| 4 | `0100` | 6 | `0110` | 1 |
| 5 | `0101` | 7 | `0111` | 1 |
| 6 | `0110` | 5 | `0101` | 1 |
| 7 | `0111` | 4 | `0100` | 1 |
| 8 | `1000` | 12 | `1100` | 1 |

Every single step changes exactly one bit. Even the jump from 7 to 8, which was
a four-bit catastrophe in plain binary, is now a single flip.

### 1.1 Why anyone cares

This is not a mathematical curiosity — it solves a real physical problem.

Imagine a **rotary encoder**: a disc with contacts that reports its angular
position as a binary number. The bits are read by separate physical sensors,
and they never switch at *exactly* the same instant. If the disc moves from 7
(`0111`) to 8 (`1000`) and the sensors are slightly out of sync, you might
momentarily read `1111` (15) or `0000` (0) — a wildly wrong position, appearing
for just a moment. That glitch could make a machine lurch.

With Gray code only one sensor ever changes at a time, so the worst case during
a transition is that you read either the old value or the new one. Both are
adjacent to the truth. **The catastrophic misreading becomes impossible.**

Gray codes also show up in:

- **Karnaugh maps** — the row/column labels are in Gray code order so that
  neighbouring cells differ in one variable. That's exactly what makes adjacent
  cells groupable. The subject mentions K-maps in Exercise 06.
- **Error correction and digital communications**, for the same
  one-bit-of-difference reason.
- **Genetic algorithms**, where a small change to the encoding should mean a
  small change to the value.

The name comes from **Frank Gray**, a Bell Labs researcher who patented its use
in 1953. It is a person's name, not the colour — so it's capitalised.

---

## 2. Building a Gray code by hand: reflect and prefix

Before the formula, here's the construction that shows *why* such an ordering
exists at all. It's called the **reflect-and-prefix** method, and it's worth
doing on paper once.

**Start with 1 bit.** Two values, trivially one bit apart:

```
0
1
```

**To go from n bits to n+1 bits:**

1. Write your current list.
2. Write it again **upside down** (reflected) underneath.
3. Prefix `0` to every entry in the top half, `1` to every entry in the bottom half.

From 1 bit to 2 bits:

```
   0          0 0          00
   1          0 1          01
   -   ->     ----   ->    --
   1          1 1          11
   0          1 0          10
```

From 2 bits to 3 bits:

```
   00         0 00         000
   01         0 01         001
   11         0 11         011
   10         0 10         010
   --   ->    -----   ->   ---
   10         1 10         110
   11         1 11         111
   01         1 01         101
   00         1 00         100
```

**Why does this preserve the one-bit rule?**

- Inside the top half, nothing changed except a shared `0` prefix, so
  consecutive entries still differ by one bit. Same for the bottom half.
- At the **seam** in the middle, the two entries either side of the mirror line
  are *identical copies* of each other (that's what reflecting means). The only
  difference between them is the prefix: `0` on one, `1` on the other. That's
  exactly one bit. ✓

That seam is the clever part, and it's the thing to point at if an evaluator
asks you to justify the construction.

Read down the final column and convert to decimal: `000, 001, 011, 010, 110,
111, 101, 100` = `0, 1, 3, 2, 6, 7, 5, 4`. Compare with the table in section 1 —
identical. ✓

---

## 3. The formula

You don't need to build tables at runtime. There's a direct conversion:

```
gray(n) = n XOR (n >> 1)
```

### 3.1 Worked example: gray_code(8)

```
    n        =  00001000   (8)
    n >> 1   =  00000100   (4)
                --------
    XOR      =  00001100   (12)
```

Result: **12** ✓ (matches the subject's example)

Run it yourself:

```bash
python3 gray_code.py -t 8
```

### 3.2 A second one: gray_code(6)

```
    n        =  00000110   (6)
    n >> 1   =  00000011   (3)
                --------
    XOR      =  00000101   (5)
```

Result: **5** ✓

---

## 4. Why does `n ^ (n >> 1)` work?

This is the question you will be asked. Here is the reasoning, built up in three
small steps.

### 4.1 What we need each output bit to be

Look back at the reflect-and-prefix construction. A bit in the Gray code flips
exactly when we cross a mirror line, and the mirror lines are precisely where
the *next higher* bit of `n` changes. Working that through gives the rule:

> **Gray bit at position `i` = (bit `i` of n) XOR (bit `i+1` of n)**

Each Gray bit answers the question *"do these two neighbouring bits of n
differ?"* The topmost bit has no neighbour above it, so it's treated as XOR with
0 — meaning it just copies through unchanged.

Check it on `n = 6 = 0110`:

| position i | bit i | bit i+1 | XOR | gray bit |
|---|---|---|---|---|
| 0 | 0 | 1 | 0 ⊕ 1 | **1** |
| 1 | 1 | 1 | 1 ⊕ 1 | **0** |
| 2 | 1 | 0 | 1 ⊕ 0 | **1** |
| 3 | 0 | 0 | 0 ⊕ 0 | **0** |

Reading positions 3→0: `0101` = 5. ✓ Matches section 3.2.

### 4.2 Lining the bits up

We now need, at every position, bit `i` next to bit `i+1`. That's exactly what a
right shift does: `n >> 1` slides every bit down one place, so the value sitting
at position `i` of `n >> 1` is the bit that was at position `i+1` of `n`.

```
   n       =  0 1 1 0        position 3 2 1 0
   n >> 1  =  0 0 1 1        now position i holds n's old bit i+1
```

Column `i` of the two rows now holds exactly the pair we want to compare.

### 4.3 Comparing all positions at once

"Do these two bits differ?" is the definition of XOR — that's the truth table
from Exercise 00:

| a | b | a ⊕ b |
|---|---|---|
| 0 | 0 | 0 |
| 0 | 1 | **1** |
| 1 | 0 | **1** |
| 1 | 1 | 0 |

And bitwise operators work on every column independently, **in parallel**. So a
single `^` answers the question for all 32 positions simultaneously:

```
gray(n) = n ^ (n >> 1)
```

The shift with zero-fill also handles the topmost bit correctly for free: the
new leading bit of `n >> 1` is 0, and `x ⊕ 0 = x`, so the highest bit copies
through unchanged, exactly as section 4.1 requires.

**The one-sentence version for your defense:**

> *"Each Gray bit says whether two neighbouring bits of n differ. Shifting right
> by one lines each bit up with its neighbour, and XOR compares all positions at
> once."*

---

## 5. Properties worth knowing

### 5.1 It is a bijection

Every input maps to a different output, and every possible output is reachable.
This matters because Gray code is an *ordering* of the same set of values — it
doesn't lose or duplicate anything. The demo verifies it implicitly: 65,536
distinct inputs give 65,536 distinct outputs.

This also means the conversion is **reversible**, which leads to the next point.

### 5.2 The inverse (not required, but often asked)

The subject only asks for the forward direction, so this file doesn't implement
it. But an evaluator may ask "can you go back?", so know the answer.

Decoding is *not* symmetric — `g ^ (g >> 1)` does **not** undo the encoding. You
have to XOR in every shift:

```
binary(g) = g ^ (g>>1) ^ (g>>2) ^ (g>>4) ^ (g>>8) ^ (g>>16)
```

The reason: encoding compared each bit with its immediate neighbour, so
recovering bit `i` requires XOR-ing together *every* Gray bit above it. Doubling
the shift each round accumulates all of them in log₂(32) = 5 steps.

If you'd like this added as a bonus function, say so — but it isn't required and
adding unrequested code can invite questions you don't need.

### 5.3 The complexity

The subject says N/A, so nothing is being checked. For completeness: one shift,
one XOR, no loop → **O(1) time and O(1) space**, trivially.

If asked, note the contrast with Exercises 00 and 01: those needed loops over
bit positions, whereas here the bitwise operators do all 32 positions in one
instruction. That's the payoff of thinking in parallel across bits.

---

## 6. The code

```python
MASK_32 = 0xFFFFFFFF

def gray_code(n: int) -> int:
    n = n & MASK_32
    return (n ^ (n >> 1)) & MASK_32
```

**Operator check:**

| Used | Allowed? |
|---|---|
| `^` | ✔ bitwise XOR |
| `>>` | ✔ right shift |
| `&` | ✔ bitwise AND (the 32-bit mask) |

No arithmetic, no library, no loop. ✓

The mask serves the same purpose as in Exercises 00 and 01 — Python integers are
unbounded, so we clamp to 32 bits to match `u32`. Here it's mostly belt and
braces: `n ^ (n >> 1)` can never produce more bits than `n` already had, so the
output mask never actually changes anything for valid input. It's there for
consistency and to make the `u32` contract explicit.

---

## 7. How to run it

```bash
cd Ex02

python3 gray_code.py 8         # -> 12
python3 gray_code.py 0         # -> 0
python3 gray_code.py 7         # -> 4
```

**No arguments** — a table for 0..15 plus a verification that the one-bit
property holds for every value from 0 to 65535:

```bash
python3 gray_code.py
```

**`-t`** — the bit-by-bit conversion from section 3.1:

```bash
python3 gray_code.py -t 8
```

**`-r`** — a table over any range (up to 1000 rows), with a column counting how
many bits changed from the previous row. Every entry should read `1`:

```bash
python3 gray_code.py -r 0 31
python3 gray_code.py -r 254 258     # watch the 8-bit boundary stay smooth
```

### The subject's examples, all verified

| Command | Expected | Got |
|---|---|---|
| `gray_code(0)` | 0 | 0 ✓ |
| `gray_code(1)` | 1 | 1 ✓ |
| `gray_code(2)` | 3 | 3 ✓ |
| `gray_code(3)` | 2 | 2 ✓ |
| `gray_code(4)` | 6 | 6 ✓ |
| `gray_code(5)` | 7 | 7 ✓ |
| `gray_code(6)` | 5 | 5 ✓ |
| `gray_code(7)` | 4 | 4 ✓ |
| `gray_code(8)` | 12 | 12 ✓ |

All nine match the values printed in the subject.

---

## 8. Common mistakes to avoid

| Mistake | What happens | Fix |
|---|---|---|
| Using `<<` instead of `>>` | Compares each bit with the one *below* it; wrong answers and the value grows | `n >> 1` |
| Using `\|` or `&` instead of `^` | Those don't answer "do these differ?" — only XOR does | `^` |
| Shifting by more than 1 | Compares non-adjacent bits; the one-bit property breaks | Shift by exactly 1 |
| Assuming `g ^ (g >> 1)` decodes | It doesn't — decoding needs all the shifts (section 5.2) | Don't claim it does |
| Building a lookup table of all values | Wasteful and O(2ⁿ) space for no benefit | One expression is enough |
| Writing the colour "grey code" | It's a surname — Frank Gray | Capital G, spelled "Gray" |

---

## 9. Do this on paper

1. **Build the 4-bit Gray code** with reflect-and-prefix, starting from the
   3-bit list in section 2. You should get 16 entries. Check a few against
   `python3 gray_code.py -r 0 15`.

2. **Convert by hand:** compute `gray_code(10)` and `gray_code(11)` using the
   two-row XOR layout from section 3.1. Verify the two results differ by exactly
   one bit, then check with the program.

3. **Verify the neighbour rule:** take `n = 12` (`1100`) and fill in the
   position table from section 4.1. Confirm it gives the same answer as the
   formula.

4. **Answer in writing:** why does the *highest* bit of the Gray code always
   equal the highest bit of `n`? (Hint: what does `>>` put in the vacated top
   position, and what is `x ⊕ 0`?)

5. **Think it through:** why is the transition from 7 to 8 the worst case in
   plain binary, and what does Gray code do about it? Relate your answer to the
   rotary-encoder story in section 1.1.

---

## 10. Peer-review preparation

- **"What is a Gray code?"** → An ordering of binary values where consecutive
  values differ by exactly one bit.
- **"Why does that matter?"** → Physical sensors don't switch simultaneously.
  With plain binary, 7→8 flips four bits and a mid-transition read can return a
  wildly wrong value. With Gray code only one bit ever changes, so the worst
  case is reading the old or the new value.
- **"Explain your one-line formula."** → Each Gray bit says whether two
  neighbouring bits of `n` differ. `>> 1` lines each bit up with its neighbour;
  XOR compares all positions at once.
- **"Why does the top bit come out right?"** → `>>` fills with 0, and `x ⊕ 0 =
  x`, so the highest bit passes through unchanged.
- **"Can you decode it?"** → Yes, but not symmetrically: you XOR in every shift,
  `g ^ (g>>1) ^ (g>>2) ^ (g>>4) ^ (g>>8) ^ (g>>16)`.
- **"Show me it works."** → `python3 gray_code.py` prints the 0..15 table and
  verifies the one-bit property for all 65,536 values. Then `-r` on any range
  they pick.
- **"Where else is this used?"** → Karnaugh maps (Exercise 06 mentions them),
  error correction, rotary encoders.

---

## 11. What's next

This closes the pure bit-manipulation block. **Exercise 03 changes gear
completely**: you'll parse and evaluate logical formulas written in Reverse
Polish Notation.

It's worth knowing in advance that Ex03 is the most important architectural
decision in the module. The subject suggests building a binary **Abstract Syntax
Tree** there rather than evaluating the string directly — and Exercises 04, 05,
06, 07 and 09 all build on that structure. Getting it right once saves a lot of
work five times over.