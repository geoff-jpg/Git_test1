# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Contents

- `kepler.c` — C99 program demonstrating Kepler's three laws of planetary motion.
- `keplar_newton.c` — the same demonstrations plus a Newtonian gravity simulation
  showing the three laws emerge from the inverse-square force.

## Build & Run

```sh
cc -std=c99 -Wall -Wextra -pedantic -O2 kepler.c -o kepler -lm
./kepler

cc -std=c99 -Wall -Wextra -pedantic -O2 keplar_newton.c -o keplar_newton -lm
./keplar_newton
```
