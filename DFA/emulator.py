from collections import deque
from dataclasses import dataclass
from typing import Iterable

from parser import DFASpec


EPSILON = "epsilon"


@dataclass(frozen=True)
class Step:
    current_state: str
    symbol: str
    next_state: str

    def __str__(self) -> str:
        return f"{self.current_state} --{self.symbol}--> {self.next_state}"


class DFA:
    def __init__(
        self,
        states: Iterable[str],
        alphabet: Iterable[str],
        start_state: str,
        final_states: Iterable[str],
    ) -> None:
        self.states = set(states)
        self.alphabet = set(alphabet)
        self.start_state = start_state
        self.final_states = set(final_states)
        self.transitions: dict[tuple[str, str], str] = {}

        if self.start_state not in self.states:
            raise ValueError("Starea initiala trebuie sa apartina multimii starilor.")
        unknown_final_states = self.final_states - self.states
        if unknown_final_states:
            raise ValueError(f"Stari finale necunoscute: {', '.join(unknown_final_states)}")

    def add_transition(self, state: str, symbol: str, next_state: str) -> None:
        if state not in self.states:
            raise ValueError(f"Stare necunoscuta in tranzitie: {state}")
        if symbol not in self.alphabet:
            raise ValueError(f"Simbol necunoscut in tranzitie: {symbol}")
        if next_state not in self.states:
            raise ValueError(f"Stare destinatie necunoscuta: {next_state}")
        if (state, symbol) in self.transitions:
            raise ValueError(f"Tranzitie duplicata pentru ({state}, {symbol})")

        self.transitions[(state, symbol)] = next_state

    def validate_complete(self) -> None:
        missing = []
        for state in sorted(self.states):
            for symbol in sorted(self.alphabet):
                if (state, symbol) not in self.transitions:
                    missing.append(f"delta({state}, {symbol})")

        if missing:
            raise ValueError("DFA incomplet. Lipsesc: " + ", ".join(missing))

    def run(self, word: str) -> tuple[bool, list[Step], str]:
        symbols = self.split_word(word)
        current_state = self.start_state
        steps: list[Step] = []

        for symbol in symbols:
            next_state = self.transitions[(current_state, symbol)]
            steps.append(Step(current_state, symbol, next_state))
            current_state = next_state

        return current_state in self.final_states, steps, current_state

    def accepts(self, word: str) -> bool:
        accepted, _, _ = self.run(word)
        return accepted

    def generate_accepted_words(
        self,
        max_length: int = 5,
        max_words: int = 20,
    ) -> list[str]:
        words: list[str] = []
        queue = deque([("", 0)])
        alphabet = sorted(self.alphabet)

        while queue and len(words) < max_words:
            current_word, length = queue.popleft()
            if self.accepts(current_word):
                words.append(current_word or EPSILON)

            if length >= max_length:
                continue

            for symbol in alphabet:
                queue.append((current_word + symbol, length + 1))

        return words

    def split_word(self, word: str) -> list[str]:
        if word == "" or word == EPSILON:
            return []
        if " " in word:
            symbols = word.split()
        else:
            alphabet = sorted(self.alphabet, key=len, reverse=True)
            symbols = []
            index = 0
            while index < len(word):
                match = next(
                    (symbol for symbol in alphabet if word.startswith(symbol, index)),
                    None,
                )
                if match is None:
                    raise ValueError(f"Nu pot interpreta cuvantul la pozitia {index}.")
                symbols.append(match)
                index += len(match)

        for symbol in symbols:
            if symbol not in self.alphabet:
                raise ValueError(f"Simbolul '{symbol}' nu apartine alfabetului.")
        return symbols


def build_dfa(spec: DFASpec) -> DFA:
    dfa = DFA(
        states=spec.states,
        alphabet=spec.alphabet,
        start_state=spec.start_state,
        final_states=spec.final_states,
    )
    for (state, symbol), next_state in spec.transitions.items():
        dfa.add_transition(state, symbol, next_state)
    dfa.validate_complete()
    return dfa


def format_trace(steps: list[Step], start_state: str, final_state: str) -> str:
    if not steps:
        return f"{start_state} (cuvant vid) => {final_state}"
    return " | ".join(str(step) for step in steps)
