# Formal Languages & Automata Emulator Suite

A modular Python CLI suite for simulating, validating, and analyzing core formal language models (**DFA**, **ε-NFA**, **CFG**, and **PDA**), validated across 21 formal language benchmarks.

## Modules
- `DFA/` — Deterministic Finite Automaton parser & emulator
- `NFA/` — ε-Nondeterministic Finite Automaton emulator & ε-NFA to DFA subset construction
- `CFG/` — Context-Free Grammar BFS derivation engine with pruning
- `PDA/` — Dual-mode Pushdown Automaton simulator using immutable `frozen dataclasses` and `collections.deque`

## Usage
Run any module from its directory, for example:
- `cd DFA && python3 main.py`

## Author
- **Răzvan Marin** — https://github.com/razvanmarin7
