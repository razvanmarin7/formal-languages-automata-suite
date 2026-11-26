from collections import deque
from dataclasses import dataclass
from typing import Iterable

from parser import GrammarSpec


EPSILON = "epsilon"


@dataclass(frozen=True)
class Production:
    left: str
    right: tuple[str, ...]

    def __str__(self) -> str:
        right = " ".join(self.right) if self.right else EPSILON
        return f"{self.left} -> {right}"


class Grammar:
    def __init__(
        self,
        terminals: Iterable[str],
        non_terminals: Iterable[str],
        start_symbol: str,
    ) -> None:
        self.terminals = set(terminals)
        self.non_terminals = set(non_terminals)
        self.start_symbol = start_symbol
        self.productions: list[Production] = []

        if start_symbol not in self.non_terminals:
            raise ValueError("Simbolul de start trebuie sa fie neterminal.")

    def add_production(self, left: str, right: Iterable[str]) -> None:
        if left not in self.non_terminals:
            raise ValueError(f"Partea stanga '{left}' nu este neterminal.")

        right_symbols = list(right)
        for symbol in right_symbols:
            if symbol not in self.terminals and symbol not in self.non_terminals:
                raise ValueError(f"Simbol necunoscut in productie: {symbol}")

        self.productions.append(Production(left, tuple(right_symbols)))

    def generate_words(self, max_steps: int = 6, max_words: int = 20) -> list[str]:
        words: list[str] = []
        queue = deque([((self.start_symbol,), 0)])
        visited = set()

        while queue and len(words) < max_words:
            current_form, steps = queue.popleft()
            state = (current_form, steps)
            if state in visited:
                continue
            visited.add(state)

            if self.is_final_word(current_form):
                words.append(self.format_form(current_form))
                continue

            if steps >= max_steps:
                continue

            for next_form in self.derive_once(current_form):
                queue.append((next_form, steps + 1))

        return words

    def find_derivation(
        self,
        target: str,
        max_steps: int = 10,
    ) -> list[tuple[str, ...]] | None:
        target_form = tuple(self.split_word(target))
        queue = deque([((self.start_symbol,), [(self.start_symbol,)])])
        visited = {(self.start_symbol,)}

        while queue:
            current_form, path = queue.popleft()

            if current_form == target_form:
                return path

            if len(path) - 1 >= max_steps:
                continue

            for next_form in self.derive_once(current_form):
                if next_form in visited:
                    continue
                if self.has_too_many_terminals(next_form, target_form):
                    continue
                visited.add(next_form)
                queue.append((next_form, path + [next_form]))

        return None

    def accepts(self, target: str, max_steps: int = 10) -> bool:
        return self.find_derivation(target, max_steps=max_steps) is not None

    def derive_once(self, form: tuple[str, ...]) -> list[tuple[str, ...]]:
        results = []

        for index, symbol in enumerate(form):
            if symbol not in self.non_terminals:
                continue

            for production in self.productions:
                if production.left == symbol:
                    new_form = form[:index] + production.right + form[index + 1 :]
                    results.append(new_form)

        return results

    def is_final_word(self, form: tuple[str, ...]) -> bool:
        return all(symbol in self.terminals for symbol in form)

    def has_too_many_terminals(
        self,
        form: tuple[str, ...],
        target: tuple[str, ...],
    ) -> bool:
        terminal_count = sum(symbol in self.terminals for symbol in form)
        return terminal_count > len(target)

    def split_word(self, word: str) -> list[str]:
        if " " in word:
            return word.split()

        symbols = sorted(self.terminals | self.non_terminals, key=len, reverse=True)
        result = []
        index = 0

        while index < len(word):
            match = next(
                (symbol for symbol in symbols if word.startswith(symbol, index)),
                None,
            )
            if match is None:
                raise ValueError(f"Nu pot interpreta cuvantul la pozitia {index}.")
            result.append(match)
            index += len(match)

        return result

    def format_form(self, form: tuple[str, ...]) -> str:
        if not form:
            return EPSILON
        if any(len(symbol) > 1 for symbol in form):
            return " ".join(form)
        return "".join(form)


def build_grammar(spec: GrammarSpec) -> Grammar:
    grammar = Grammar(spec.terminals, spec.non_terminals, spec.start_symbol)
    for left, right in spec.productions:
        grammar.add_production(left, right)
    return grammar


def format_derivation(grammar: Grammar, path: list[tuple[str, ...]] | None) -> str:
    if path is None:
        return "Nu exista derivare gasita."
    return " => ".join(grammar.format_form(step) for step in path)
