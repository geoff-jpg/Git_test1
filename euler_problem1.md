# Project Euler — Problem 1: Multiples of 3 or 5

## Puzzle

If we list all the natural numbers below 10 that are multiples of 3 or 5, we get 3, 5, 6, 9. Their sum is 23.

Find the sum of all the multiples of 3 or 5 below 1000.

---

## Solution Approaches

### Brute Force

Loop through every number from 1 to 999, check if it is divisible by 3 or 5, and add it to a running total:

```python
total = sum(n for n in range(1, 1000) if n % 3 == 0 or n % 5 == 0)
print(total)  # 233168
```

### Mathematical (Arithmetic Series)

Use the formula for the sum of an arithmetic series: `S(n, limit) = n * k*(k+1) / 2`  
where `k = floor((limit - 1) / n)`

- Sum of multiples of 3 below 1000
- Plus sum of multiples of 5 below 1000
- Minus sum of multiples of 15 below 1000 (to avoid double-counting)

```python
def S(n, limit):
    k = (limit - 1) // n
    return n * k * (k + 1) // 2

answer = S(3, 1000) + S(5, 1000) - S(15, 1000)
print(answer)  # 233168
```

This approach scales instantly to any limit, unlike the brute-force loop.

---

## Answer

**233168**
