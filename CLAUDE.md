# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Contents

- `kepler.c` — C99 program demonstrating Kepler's three laws of planetary motion.

## Build & Run

```sh
cc -std=c99 -Wall -Wextra -pedantic -O2 kepler.c -o kepler -lm
./kepler
```
