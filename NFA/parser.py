from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class NFASpec:
    states: set[str]
    alphabet: set[str]
    start_state: str
    final_states: set[str]
    transitions: dict[tuple[str, str], set[str]]
    check_words: list[str]


def parse_nfa_file(file_path: str | Path) -> NFASpec:
    path = Path(file_path)
    sections = _read_sections(path)

    nfa_section = sections.get("nfa", {})
    transition_lines = sections.get("transitions", [])
    settings_section = sections.get("settings", {})

    states = _parse_symbols(nfa_section.get("states", ""))
    alphabet = _parse_symbols(nfa_section.get("alphabet", ""))
    start_state = nfa_section.get("start", "").strip()
    final_states = _parse_symbols(nfa_section.get("final", ""))
    transitions = _parse_transitions(transition_lines)
    check_words = _parse_words(settings_section.get("check", ""))

    if not states:
        raise ValueError("Lipseste multimea starilor.")
    if not alphabet:
        raise ValueError("Lipseste alfabetul.")
    if not start_state:
        raise ValueError("Lipseste starea initiala.")
    if not final_states:
        raise ValueError("Lipseste multimea starilor finale.")
    if not transitions:
        raise ValueError("Lipsesc tranzitiile.")

    return NFASpec(
        states=states,
        alphabet=alphabet,
        start_state=start_state,
        final_states=final_states,
        transitions=transitions,
        check_words=check_words,
    )


def _read_sections(path: Path) -> dict[str, dict[str, str] | list[str]]:
    if not path.exists():
        raise ValueError(f"Fisierul nu exista: {path}")

    sections: dict[str, dict[str, str] | list[str]] = {}
    current_section = ""

    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue

        if line.startswith("[") and line.endswith("]"):
            current_section = line[1:-1].strip().lower()
            sections[current_section] = [] if current_section == "transitions" else {}
            continue

        if not current_section:
            raise ValueError(f"Linie in afara unei sectiuni: {line}")

        section = sections[current_section]
        if current_section == "transitions":
            assert isinstance(section, list)
            section.append(line)
        else:
            assert isinstance(section, dict)
            if "=" not in line:
                raise ValueError(f"Linie invalida in sectiunea [{current_section}]: {line}")
            key, value = line.split("=", 1)
            section[key.strip().lower()] = value.strip()

    return sections


def _parse_symbols(raw_value: str) -> set[str]:
    return set(raw_value.replace(",", " ").split())


def _parse_words(raw_value: str) -> list[str]:
    if not raw_value.strip():
        return []
    return [word.strip() for word in raw_value.split(",")]


def _parse_transitions(lines: list[str]) -> dict[tuple[str, str], set[str]]:
    transitions: dict[tuple[str, str], set[str]] = {}

    for line in lines:
        if "->" not in line:
            raise ValueError(f"Tranzitie invalida: {line}")

        left, right = line.split("->", 1)
        parts = left.strip().replace(",", " ").split()
        if len(parts) != 2:
            raise ValueError(f"Tranzitie invalida: {line}")

        state, symbol = parts
        next_states = _parse_symbols(right.strip())
        if not next_states:
            raise ValueError(f"Tranzitia nu are stare destinatie: {line}")

        transitions.setdefault((state, symbol), set()).update(next_states)

    return transitions

