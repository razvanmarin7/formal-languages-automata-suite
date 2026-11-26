from pathlib import Path
import sys

from emulator import EPSILON, build_dfa, format_trace
from parser import parse_dfa_file


DFA_FILES = [
    ("dfa.txt", "Numar par de simboluri 1"),
    ("dfa_ends_with_01.txt", "Cuvinte binare care se termina cu 01"),
    ("dfa_contains_ab.txt", "Cuvinte peste {a, b} care contin subcuvantul ab"),
    ("dfa_even_length.txt", "Cuvinte binare de lungime para"),
    ("dfa_divisible_by_3.txt", "Numere binare divizibile cu 3"),
]


def choose_dfa_file() -> Path:
    base_dir = Path(__file__).parent

    if len(sys.argv) > 1:
        return Path(sys.argv[1])

    print("Alege DFA-ul pe care vrei sa il emulezi:")
    for index, (file_name, description) in enumerate(DFA_FILES, start=1):
        print(f"{index}. {file_name} - {description}")

    while True:
        choice = input("Optiunea ta: ").strip()
        if choice.isdigit():
            index = int(choice)
            if 1 <= index <= len(DFA_FILES):
                return base_dir / DFA_FILES[index - 1][0]

        print(f"Alege un numar intre 1 si {len(DFA_FILES)}.")


def run_dfa(dfa_file: Path) -> None:
    spec = parse_dfa_file(dfa_file)
    dfa = build_dfa(spec)

    print("Proiect LFA: Emulator pentru DFA")
    print(f"Fisier citit: {dfa_file}")
    print()

    print("M = (Q, Sigma, delta, q0, F)")
    print(f"Q = {{{', '.join(sorted(dfa.states))}}}")
    print(f"Sigma = {{{', '.join(sorted(dfa.alphabet))}}}")
    print(f"q0 = {dfa.start_state}")
    print(f"F = {{{', '.join(sorted(dfa.final_states))}}}")
    print("delta:")
    for (state, symbol), next_state in sorted(dfa.transitions.items()):
        print(f"  delta({state}, {symbol}) = {next_state}")

    print()
    print("Cuvinte acceptate generate:")
    for word in dfa.generate_accepted_words(max_length=5, max_words=20):
        print(f"  {word}")

    if spec.check_words:
        print()
        print("Cuvinte verificate:")
        for word in spec.check_words:
            accepted, steps, final_state = dfa.run(word)
            display_word = word or EPSILON
            print(f"  {display_word}: {'acceptat' if accepted else 'respins'}")
            print(f"    stare finala: {final_state}")
            print(f"    traseu: {format_trace(steps, dfa.start_state, final_state)}")


def main() -> None:
    dfa_file = choose_dfa_file()
    run_dfa(dfa_file)


if __name__ == "__main__":
    main()
