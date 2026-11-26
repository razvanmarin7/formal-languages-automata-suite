# Proiect LFA - Emulator DFA

Proiectul citeste un automat finit determinist dintr-un fisier text, valideaza tranzitiile si verifica daca anumite cuvinte sunt acceptate.

## Fisiere

- `dfa.txt` - exemplu principal: cuvinte binare cu numar par de simboluri `1`.
- `dfa_ends_with_01.txt` - cuvinte binare care se termina cu `01`.
- `dfa_contains_ab.txt` - cuvinte peste `{a, b}` care contin subcuvantul `ab`.
- `dfa_even_length.txt` - cuvinte binare de lungime para.
- `dfa_divisible_by_3.txt` - numere binare divizibile cu 3.
- `parser.py` - citeste fisierul text si extrage componentele DFA-ului.
- `emulator.py` - construieste DFA-ul, ruleaza cuvinte si genereaza exemple acceptate.
- `main.py` - porneste programul si leaga parserul de emulator.

## Format fisier DFA

```text
[dfa]
states = q0, q1
alphabet = 0, 1
start = q0
final = q0

[transitions]
q0, 0 -> q0
q0, 1 -> q1
q1, 0 -> q1
q1, 1 -> q0

[settings]
check = epsilon, 0, 1, 11, 101
```

`epsilon` reprezinta cuvantul vid.

## Rulare

```bash
python main.py
```

Pentru un anumit fisier DFA:

```bash
python main.py dfa_contains_ab.txt
```

Alte exemple:

```bash
python main.py dfa_ends_with_01.txt
python main.py dfa_even_length.txt
python main.py dfa_divisible_by_3.txt
```

## Ce face programul

1. Afiseaza componentele automatului `M = (Q, Sigma, delta, q0, F)`.
2. Verifica daca tranzitiile formeaza un DFA complet.
3. Genereaza cateva cuvinte acceptate de automat.
4. Verifica lista de cuvinte din sectiunea `[settings]`.
5. Afiseaza traseul prin stari pentru fiecare cuvant verificat.
