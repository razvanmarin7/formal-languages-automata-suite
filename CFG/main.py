from pathlib import Path
import sys

from emulator import build_grammar, format_derivation
from parser import parse_grammar_file


GRAMMAR_FILES = [
    ("grammar.txt", "Limbajul (01)^n 1"),
    ("grammar_regular.txt", "Gramatica regulata: 0^n 1"),
    ("grammar_anbn.txt", "Gramatica independenta de context: a^n b^n"),
    ("grammar_palindrome.txt", "Palindroame peste alfabetul {a, b}"),
    ("grammar_parentheses.txt", "Paranteze corect balansate"),
    ("grammar_expression.txt", "Expresii aritmetice simple"),
    ("grammar_sentence.txt", "Propozitii simple: dog/cat/eat/chase"),
    ("grammar_sentence_extended.txt", "Propozitii extinse cu articole"),
]


def choose_grammar_file() -> Path:
    # Daca programul este rulat din terminal cu un argument, folosim direct acel fisier.
    # Exemplu: python main.py grammar_anbn.txt
    if len(sys.argv) > 1:
        return Path(sys.argv[1])

    # afisam un meniu interactiv.
    print("Alege gramatica pe care vrei sa o parsezi:")
    for index, (file_name, description) in enumerate(GRAMMAR_FILES, start=1):
        print(f"{index}. {file_name} - {description}")

    while True:
        choice = input("Optiunea ta: ").strip()
        if choice.isdigit():
            index = int(choice)
            if 1 <= index <= len(GRAMMAR_FILES):
                return Path(GRAMMAR_FILES[index - 1][0])

        print(f"Alege un numar intre 1 si {len(GRAMMAR_FILES)}.")


def run_grammar(grammar_file: Path) -> None:
    spec = parse_grammar_file(grammar_file)
    grammar = build_grammar(spec)

    print("Proiect LFA: Emulator pentru gramatici formale")
    print(f"Fisier citit: {grammar_file}")
    print()

    print("G = (V, Sigma, P, S)")
    print(f"V = {{{', '.join(sorted(grammar.non_terminals))}}}")
    print(f"Sigma = {{{', '.join(sorted(grammar.terminals))}}}")
    print(f"S = {grammar.start_symbol}")
    print("P:")
    for production in grammar.productions:
        print(f"  {production}")

    print()
    words = grammar.generate_words(
        max_steps=spec.max_steps,
        max_words=spec.max_words,
    )
    print("Cuvinte generate:")
    for word in words:
        print(f"  {word}")

    if spec.check_word:
        print()
        print(f"Cuvant verificat: {spec.check_word}")
        print(f"Acceptat: {grammar.accepts(spec.check_word, max_steps=spec.max_steps)}")
        derivation = grammar.find_derivation(spec.check_word, max_steps=spec.max_steps)
        print("Derivare:")
        print(f"  {format_derivation(grammar, derivation)}")


def main() -> None:
    grammar_file = choose_grammar_file()
    run_grammar(grammar_file)


if __name__ == "__main__":
    main()
