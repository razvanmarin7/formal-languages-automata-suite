from pathlib import Path
import sys

from emulator import (
    EPSILON,
    build_pda,
    format_push,
    format_symbols,
    format_trace,
)
from parser import parse_pda_file


PDA_FILES = [
    ("pda.txt", "Limbajul a^n b^n, n >= 0"),
    ("pda_anbn.txt", "Acelasi exemplu clasic a^n b^n"),
    ("pda_parentheses.txt", "Paranteze corect balansate"),
    ("pda_palindrome.txt", "Palindroame peste alfabetul {a, b}"),
]


def choose_pda_file() -> Path:
    base_dir = Path(__file__).parent

    if len(sys.argv) > 1:
        candidate = Path(sys.argv[1])
        return candidate if candidate.is_absolute() else base_dir / candidate

    print("Alege PDA-ul pe care vrei sa il emulezi:")
    for index, (file_name, description) in enumerate(PDA_FILES, start=1):
        print(f"{index}. {file_name} - {description}")

    while True:
        choice = input("Optiunea ta: ").strip()
        if choice.isdigit():
            index = int(choice)
            if 1 <= index <= len(PDA_FILES):
                return base_dir / PDA_FILES[index - 1][0]

        print(f"Alege un numar intre 1 si {len(PDA_FILES)}.")


def run_pda(pda_file: Path) -> None:
    spec = parse_pda_file(pda_file)
    pda = build_pda(spec)

    print("Proiect LFA: Emulator pentru PDA")
    print(f"Fisier citit: {pda_file}")
    print()

    print("M = (Q, Sigma, Gamma, delta, q0, Z0, F)")
    print(f"Q = {format_symbols(pda.states)}")
    print(f"Sigma = {format_symbols(pda.alphabet)}")
    print(f"Gamma = {format_symbols(pda.stack_alphabet)}")
    print(f"q0 = {pda.start_state}")
    print(f"Z0 = {pda.start_stack}")
    print(f"F = {format_symbols(pda.final_states)}")
    print(f"Acceptare = {'stare finala' if pda.accept_by == 'final_state' else 'stiva goala'}")
    print("delta:")
    for (state, input_symbol, stack_top), targets in sorted(pda.transitions.items()):
        for next_state, push_symbols in sorted(targets):
            print(
                f"  delta({state}, {input_symbol}, {stack_top}) = "
                f"({next_state}, {format_push(push_symbols)})"
            )

    print()
    reasons = pda.nondeterminism_reasons()
    if reasons:
        print("Automatul este nedeterminist. Motive:")
        for reason in reasons:
            print(f"  - {reason}")
    else:
        print("Automatul este determinist pentru configuratiile definite.")

    print()
    print("Cuvinte acceptate generate:")
    accepted_words = pda.generate_accepted_words(max_length=5, max_words=20)
    if accepted_words:
        for word in accepted_words:
            print(f"  {word}")
    else:
        print("  Nu s-au gasit cuvinte acceptate pana la lungimea 5.")

    if spec.check_words:
        print()
        print("Cuvinte verificate:")
        for word in spec.check_words:
            symbols = pda.split_word(word)
            result = pda.run(word)
            display_word = word or EPSILON
            print(f"  {display_word}: {'acceptat' if result.accepted else 'respins'}")
            print(f"    configuratii explorate: {result.explored_configurations}")
            print(f"    motiv: {result.reason}")
            print(f"    traseu: {format_trace(result.steps, symbols, result.final_configuration)}")


def main() -> None:
    pda_file = choose_pda_file()
    run_pda(pda_file)


if __name__ == "__main__":
    main()


