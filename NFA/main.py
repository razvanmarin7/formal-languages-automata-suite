from pathlib import Path
import sys

from emulator import EPSILON, build_nfa, format_dfa_state, format_states, format_trace
from parser import parse_nfa_file


NFA_FILES = [
    ("nfa_contains_ab.txt", "Cuvinte peste {a, b} care contin subcuvantul ab"),
    ("nfa_ends_with_01.txt", "Cuvinte binare care se termina cu 01"),
    ("nfa_third_from_end_a.txt", "Al treilea simbol de la final este a"),
    ("nfa_union_epsilon.txt", "Limbajul a*b reunit cu ab*, folosind epsilon"),
]


def choose_nfa_file() -> Path:
    base_dir = Path(__file__).parent

    if len(sys.argv) > 1:
        candidate = Path(sys.argv[1])
        return candidate if candidate.is_absolute() else base_dir / candidate

    print("Alege NFA-ul pe care vrei sa il emulezi:")
    for index, (file_name, description) in enumerate(NFA_FILES, start=1):
        print(f"{index}. {file_name} - {description}")

    while True:
        choice = input("Optiunea ta: ").strip()
        if choice.isdigit():
            index = int(choice)
            if 1 <= index <= len(NFA_FILES):
                return base_dir / NFA_FILES[index - 1][0]

        print(f"Alege un numar intre 1 si {len(NFA_FILES)}.")


def run_nfa(nfa_file: Path) -> None:
    spec = parse_nfa_file(nfa_file)
    nfa = build_nfa(spec)

    print("Proiect LFA: Emulator pentru NFA")
    print(f"Fisier citit: {nfa_file}")
    print()

    print("M = (Q, Sigma, delta, q0, F)")
    print(f"Q = {format_states(nfa.states)}")
    print(f"Sigma = {format_states(nfa.alphabet)}")
    print(f"q0 = {nfa.start_state}")
    print(f"F = {format_states(nfa.final_states)}")
    print("delta:")
    for (state, symbol), next_states in sorted(nfa.transitions.items()):
        print(f"  delta({state}, {symbol}) = {format_states(next_states)}")

    print()
    reasons = nfa.nondeterminism_reasons()
    if reasons:
        print("Automatul este NFA. Motive:")
        for reason in reasons:
            print(f"  - {reason}")
    else:
        print("Automatul este determinist: nu are epsilon-tranzitii si nu are alegeri multiple.")

    print()
    print("Cuvinte acceptate generate:")
    accepted_words = nfa.generate_accepted_words(max_length=5, max_words=20)
    if accepted_words:
        for word in accepted_words:
            print(f"  {word}")
    else:
        print("  Nu s-au gasit cuvinte acceptate pana la lungimea 5.")

    if spec.check_words:
        print()
        print("Cuvinte verificate:")
        for word in spec.check_words:
            accepted, steps, final_states = nfa.run(word)
            start_closure = nfa.epsilon_closure({nfa.start_state})
            display_word = word or EPSILON
            print(f"  {display_word}: {'acceptat' if accepted else 'respins'}")
            print(f"    stari active finale: {format_states(final_states)}")
            print(f"    traseu: {format_trace(steps, start_closure, final_states)}")

    print()
    print("DFA echivalent obtinut prin subset construction:")
    dfa_start, dfa_states, dfa_final_states, dfa_transitions = nfa.to_dfa()
    print(f"  Stare initiala DFA: {format_dfa_state(dfa_start)}")
    print("  Stari DFA:")
    for state in sorted(dfa_states, key=format_dfa_state):
        marker = " *finala" if state in dfa_final_states else ""
        print(f"    {format_dfa_state(state)}{marker}")
    print("  Tranzitii DFA:")
    for (state, symbol), target in sorted(
        dfa_transitions.items(),
        key=lambda item: (format_dfa_state(item[0][0]), item[0][1]),
    ):
        print(f"    delta({format_dfa_state(state)}, {symbol}) = {format_dfa_state(target)}")


def main() -> None:
    nfa_file = choose_nfa_file()
    run_nfa(nfa_file)


if __name__ == "__main__":
    main()
