# Emulator PDA

Proiect LFA pentru emularea unui Pushdown Automaton.

Un PDA este un automat finit care are in plus o stiva. Din acest motiv poate recunoaste limbaje care nu sunt regulate, de exemplu `a^n b^n`.

## Structura proiectului

```text
PDA/
  main.py
  parser.py
  emulator.py
  pda.txt
  pda_anbn.txt
  pda_parentheses.txt
  pda_palindrome.txt
```

## Rulare

Din folderul proiectului:

```bash
python main.py
```

Sau direct cu un fisier:

```bash
python main.py pda_palindrome.txt
```

## Formatul unui fisier PDA

```text
[pda]
states = q_push, q_pop, qf
alphabet = a, b
stack_alphabet = Z, A
start = q_push
start_stack = Z
final = qf
accept_by = final_state

[transitions]
q_push, a, Z -> q_push, A Z
q_push, b, A -> q_pop, epsilon

[settings]
check = epsilon, ab, aabb, aab
```

O tranzitie are forma:

```text
stare_curenta, simbol_intrare, varf_stiva -> stare_urmatoare, simboluri_puse_pe_stiva
```

`epsilon` inseamna ca nu se consuma simbol de intrare sau ca nu se pune nimic pe stiva.

## Ce aduce in plus

- afiseaza definitia formala `M = (Q, Sigma, Gamma, delta, q0, Z0, F)`
- simuleaza pas cu pas configuratiile `(stare, input ramas, stiva)`
- suporta acceptare prin stare finala si prin stiva goala
- detecteaza motive simple de nedeterminism
- genereaza automat cuvinte acceptate pana la o lungime data
- include exemple pentru `a^n b^n`, paranteze balansate si palindroame
