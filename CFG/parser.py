from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GrammarSpec:
    terminals: set[str]
    non_terminals: set[str]
    start_symbol: str
    productions: list[tuple[str, list[str]]]
    max_steps: int = 10
    max_words: int = 20
    check_word: str = ""


def parse_grammar_file(file_path: str | Path) -> GrammarSpec:
    path = Path(file_path)
    sections = _read_sections(path)

    grammar_section = sections.get("grammar", {})
    settings_section = sections.get("settings", {})
    production_lines = sections.get("productions", [])

    terminals = _parse_symbols(grammar_section.get("terminals", ""))
    non_terminals = _parse_symbols(grammar_section.get("non_terminals", ""))
    start_symbol = grammar_section.get("start", "").strip()
    productions = _parse_productions(production_lines)

    if not terminals:
        raise ValueError("Lipseste multimea terminalelor.")
    if not non_terminals:
        raise ValueError("Lipseste multimea neterminalelor.")
    if not start_symbol:
        raise ValueError("Lipseste simbolul de start.")
    if not productions:
        raise ValueError("Lipsesc productiile.")

    return GrammarSpec(
        terminals=terminals,
        non_terminals=non_terminals,
        start_symbol=start_symbol,
        productions=productions,
        max_steps=int(settings_section.get("max_steps", "10")),
        max_words=int(settings_section.get("max_words", "20")),
        check_word=settings_section.get("check", "").strip(),
    )


def _read_sections(path: Path) -> dict[str, dict[str, str] | list[str]]:
    sections: dict[str, dict[str, str] | list[str]] = {}
    current_section = ""

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue

        if line.startswith("[") and line.endswith("]"):
            current_section = line[1:-1].strip().lower()
            sections[current_section] = [] if current_section == "productions" else {}
            continue

        if not current_section:
            raise ValueError(f"Linie in afara unei sectiuni: {line}")

        section = sections[current_section]
        if current_section == "productions":
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


def _parse_productions(lines: list[str]) -> list[tuple[str, list[str]]]:
    productions: list[tuple[str, list[str]]] = []

    for line in lines:
        if "->" not in line:
            raise ValueError(f"Productie invalida: {line}")

        left, alternatives = line.split("->", 1)
        left = left.strip()
        for alternative in alternatives.split("|"):
            alternative = alternative.strip()
            right = [] if alternative == "epsilon" else alternative.split()
            productions.append((left, right))

    return productions
