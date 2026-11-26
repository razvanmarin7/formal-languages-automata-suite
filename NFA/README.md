# Proiect LFA - Emulator NFA

Proiectul citeste un automat finit nedeterminist dintr-un fisier text, valideaza tranzitiile si verifica daca anumite cuvinte sunt acceptate.

Emulatorul suporta si epsilon-tranzitii. Un cuvant este acceptat daca, dupa consumarea lui, cel putin una dintre starile active este stare finala.

## Fisiere

- `nfa_contains_ab.txt` - cuvinte peste `{a, b}` care contin subcuvantul `ab`.
- `nfa_ends_with_01.txt` - cuvinte binare care se termina cu `01`.
- `nfa_third_from_end_a.txt` - cuvinte peste `{a, b}` unde al treilea simbol de la final este `a`.
- `nfa_union_epsilon.txt` - limbajul `a*b` reunit cu `ab*`, construit cu epsilon-tranzitii.
- `parser.py` - citeste fisierul text si extrage componentele NFA-ului.
- `emulator.py` - construieste NFA-ul, ruleaza cuvinte, calculeaza epsilon-closure si genereaza DFA-ul echivalent.
- `main.py` - porneste programul si leaga parserul de emulator.

## Format fisier NFA

```text
[nfa]
states = q0, q1, q2
alphabet = a, b
start = q0
final = q2

[transitions]
q0, a -> q0, q1
q0, b -> q0
q1, b -> q2
q2, a -> q2
q2, b -> q2

[settings]
check = epsilon, a, ab, baba
```

`epsilon`, `eps`, `lambda` si `$` pot fi folosite pentru tranzitii epsilon. Epsilon nu se trece in alfabet.

## Rulare

```bash
python main.py
```

Pentru un anumit fisier NFA:

```bash
python main.py nfa_union_epsilon.txt
```

Alte exemple:

```bash
python main.py nfa_contains_ab.txt
python main.py nfa_ends_with_01.txt
python main.py nfa_third_from_end_a.txt
```

## Ce face programul

1. Afiseaza componentele automatului `M = (Q, Sigma, delta, q0, F)`.
2. Arata daca automatul este nedeterminist si de ce.
3. Genereaza cateva cuvinte acceptate de automat.
4. Verifica lista de cuvinte din sectiunea `[settings]`.
5. Afiseaza starile active dupa fiecare simbol citit.
6. Construieste si afiseaza DFA-ul echivalent prin subset construction.
