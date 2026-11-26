# Proiect LFA - Gramatici formale

Proiectul citeste o gramatica dintr-un fisier text, construieste regulile de productie si emuleaza derivari.

## Fisiere

- `grammar.txt` - fisier text de intrare cu gramatica principala.
- `grammar_sentence.txt` - exemplu suplimentar cu propozitii simple.
- `grammar_regular.txt` - exemplu de gramatica regulata.
- `grammar_anbn.txt` - exemplu pentru limbajul `a^n b^n`.
- `grammar_palindrome.txt` - exemplu pentru palindroame.
- `grammar_parentheses.txt` - exemplu pentru paranteze balansate.
- `grammar_expression.txt` - exemplu pentru expresii aritmetice simple.
- `grammar_sentence_extended.txt` - exemplu extins pentru propozitii.
- `parser.py` - citeste fisierul text si extrage componentele gramaticii.
- `emulator.py` - genereaza cuvinte, verifica apartenenta unui cuvant si cauta derivarea.
- `main.py` - porneste programul si leaga parserul de emulator.

## Format fisier gramatica

```text
[grammar]
non_terminals = S
terminals = 0, 1
start = S

[productions]
S -> 0 1 S | 1

[settings]
max_steps = 10
max_words = 20
check = 01011
```

## Rulare

```bash
python main.py
```

Pentru alt fisier de gramatica:

```bash
python main.py grammar_sentence.txt
```

Alte exemple:

```bash
python main.py grammar_regular.txt
python main.py grammar_anbn.txt
python main.py grammar_palindrome.txt
python main.py grammar_parentheses.txt
python main.py grammar_expression.txt
python main.py grammar_sentence_extended.txt
```

## Ce face programul

1. Afiseaza componentele gramaticii `G = (V, Sigma, P, S)`.
2. Genereaza cuvinte obtinute prin aplicarea productiilor.
3. Verifica daca un cuvant apartine limbajului.
4. Afiseaza o derivare pentru cuvantul verificat, daca exista.
