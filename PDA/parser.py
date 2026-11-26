from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PDASpec:
    states: set[str]
    alphabet: set[str]
    stack_alphabet: set[str]
    start_state: str
    start_stack: str
    final_states: set[str]
    accept_by: str
    transitions: dict[tuple[str, str, str], set[tuple[str, tuple[str, ...]]]]
    check_words: list[str]


def parse_pda_file(file_path: str | Path) -> PDASpec:
    path = Path(file_path)
    sections = _read_sections(path)

    pda_section = sections.get("pda", {})
    transition_lines = sections.get("transitions", [])
    settings_section = sections.get("settings", {})

    states = _parse_symbols(pda_section.get("states", ""))
    alphabet = _parse_symbols(pda_section.get("alphabet", ""))
    stack_alphabet = _parse_symbols(pda_section.get("stack_alphabet", ""))
    start_state = pda_section.get("start", "").strip()
    start_stack = pda_section.get("start_stack", "").strip()
    final_states = _parse_symbols(pda_section.get("final", ""))
    accept_by = pda_section.get("accept_by", "final_state").strip().lower()
    transitions = _parse_transitions(transition_lines)
    check_words = _parse_words(settings_section.get("check", ""))

    if not states:
        raise ValueError("Lipseste multimea starilor.")
    if not alphabet:
        raise ValueError("Lipseste alfabetul de intrare.")
    if not stack_alphabet:
        raise ValueError("Lipseste alfabetul stivei.")
    if not start_state:
        raise ValueError("Lipseste starea initiala.")
    if not start_stack:
        raise ValueError("Lipseste simbolul initial al stivei.")
    if accept_by not in {"final_state", "empty_stack"}:
        raise ValueError("accept_by poate fi doar final_state sau empty_stack.")
    if accept_by == "final_state" and not final_states:
        raise ValueError("Lipseste multimea starilor finale.")
    if not transitions:
        raise ValueError("Lipsesc tranzitiile.")

    return PDASpec(
        states=states,
        alphabet=alphabet,
        stack_alphabet=stack_alphabet,
        start_state=start_state,
        start_stack=start_stack,
        final_states=final_states,
        accept_by=accept_by,
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


def _parse_stack_push(raw_value: str) -> tuple[str, ...]:
    symbols = raw_value.replace(",", " ").split()
    if len(symbols) == 1 and symbols[0].lower() in {"epsilon", "eps", "lambda", "$"}:
        return tuple()
    return tuple(symbols)


def _parse_transitions(lines: list[str]) -> dict[tuple[str, str, str], set[tuple[str, tuple[str, ...]]]]:
    transitions: dict[tuple[str, str, str], set[tuple[str, tuple[str, ...]]]] = {}

    for line in lines:
        if "->" not in line:
            raise ValueError(f"Tranzitie invalida: {line}")

        left, right = line.split("->", 1)
        left_parts = left.strip().replace(",", " ").split()
        right_parts = right.strip().split(",", 1)

        if len(left_parts) != 3 or len(right_parts) != 2:
            raise ValueError(f"Tranzitie invalida: {line}")

        state, input_symbol, stack_top = left_parts
        next_state = right_parts[0].strip()
        push_symbols = _parse_stack_push(right_parts[1].strip())

        key = (state, input_symbol, stack_top)
        value = (next_state, push_symbols)
        transitions.setdefault(key, set()).add(value)

    return transitions
