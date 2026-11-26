from collections import deque
from dataclasses import dataclass
from typing import Iterable

from parser import NFASpec


EPSILON = "epsilon"
EPSILON_ALIASES = {EPSILON, "eps", "lambda", "$"}
EMPTY_SET = "{}"


@dataclass(frozen=True)
class Step:
    symbol: str
    before: frozenset[str]
    after_move: frozenset[str]
    after_closure: frozenset[str]


class NFA:
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
        self.transitions: dict[tuple[str, str], set[str]] = {}

        if self.start_state not in self.states:
            raise ValueError("Starea initiala trebuie sa apartina multimii starilor.")
        unknown_final_states = self.final_states - self.states
        if unknown_final_states:
            raise ValueError(f"Stari finale necunoscute: {', '.join(sorted(unknown_final_states))}")
        epsilon_in_alphabet = self.alphabet & EPSILON_ALIASES
        if epsilon_in_alphabet:
            raise ValueError("Epsilon nu trebuie pus in alfabet; se foloseste doar in tranzitii.")

    def add_transition(self, state: str, symbol: str, next_states: Iterable[str]) -> None:
        normalized_symbol = normalize_symbol(symbol)
        targets = set(next_states)

        if state not in self.states:
            raise ValueError(f"Stare necunoscuta in tranzitie: {state}")
        if normalized_symbol != EPSILON and normalized_symbol not in self.alphabet:
            raise ValueError(f"Simbol necunoscut in tranzitie: {symbol}")

        unknown_targets = targets - self.states
        if unknown_targets:
            raise ValueError(f"Stari destinatie necunoscute: {', '.join(sorted(unknown_targets))}")

        self.transitions.setdefault((state, normalized_symbol), set()).update(targets)

    def epsilon_closure(self, states: Iterable[str]) -> frozenset[str]:
        closure = set(states)
        stack = list(closure)

        while stack:
            state = stack.pop()
            for next_state in self.transitions.get((state, EPSILON), set()):
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)

        return frozenset(closure)

    def move(self, states: Iterable[str], symbol: str) -> frozenset[str]:
        reached: set[str] = set()
        for state in states:
            reached.update(self.transitions.get((state, symbol), set()))
        return frozenset(reached)

    def run(self, word: str) -> tuple[bool, list[Step], frozenset[str]]:
        symbols = self.split_word(word)
        current_states = self.epsilon_closure({self.start_state})
        steps: list[Step] = []

        for symbol in symbols:
            after_move = self.move(current_states, symbol)
            after_closure = self.epsilon_closure(after_move)
            steps.append(
                Step(
                    symbol=symbol,
                    before=current_states,
                    after_move=after_move,
                    after_closure=after_closure,
                )
            )
            current_states = after_closure

        return bool(current_states & self.final_states), steps, current_states

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
        if word == "" or normalize_symbol(word) == EPSILON:
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

    def nondeterminism_reasons(self) -> list[str]:
        reasons: list[str] = []
        for (state, symbol), targets in sorted(self.transitions.items()):
            if symbol == EPSILON:
                reasons.append(f"delta({state}, epsilon) exista")
            elif len(targets) > 1:
                reasons.append(
                    f"delta({state}, {symbol}) are mai multe destinatii: {format_states(targets)}"
                )
        return reasons

    def to_dfa(self) -> tuple[frozenset[str], set[frozenset[str]], set[frozenset[str]], dict[tuple[frozenset[str], str], frozenset[str]]]:
        dfa_start = self.epsilon_closure({self.start_state})
        dfa_states: set[frozenset[str]] = {dfa_start}
        dfa_final_states: set[frozenset[str]] = set()
        dfa_transitions: dict[tuple[frozenset[str], str], frozenset[str]] = {}
        queue = deque([dfa_start])

        while queue:
            current = queue.popleft()
            if current & self.final_states:
                dfa_final_states.add(current)

            for symbol in sorted(self.alphabet):
                target = self.epsilon_closure(self.move(current, symbol))
                dfa_transitions[(current, symbol)] = target
                if target not in dfa_states:
                    dfa_states.add(target)
                    queue.append(target)

        return dfa_start, dfa_states, dfa_final_states, dfa_transitions


def normalize_symbol(symbol: str) -> str:
    lowered = symbol.strip().lower()
    if lowered in EPSILON_ALIASES:
        return EPSILON
    return symbol.strip()


def build_nfa(spec: NFASpec) -> NFA:
    nfa = NFA(
        states=spec.states,
        alphabet=spec.alphabet,
        start_state=spec.start_state,
        final_states=spec.final_states,
    )
    for (state, symbol), next_states in spec.transitions.items():
        nfa.add_transition(state, symbol, next_states)
    return nfa


def format_states(states: Iterable[str]) -> str:
    ordered = sorted(states)
    if not ordered:
        return EMPTY_SET
    return "{" + ", ".join(ordered) + "}"


def format_trace(steps: list[Step], start_closure: frozenset[str], final_states: frozenset[str]) -> str:
    if not steps:
        return f"epsilon-inchidere(q0) = {format_states(start_closure)} => {format_states(final_states)}"

    parts = [f"start: {format_states(start_closure)}"]
    for step in steps:
        parts.append(
            f"dupa '{step.symbol}': move = {format_states(step.after_move)}, "
            f"epsilon-inchidere = {format_states(step.after_closure)}"
        )
    return " | ".join(parts)


def format_dfa_state(state_set: frozenset[str]) -> str:
    if not state_set:
        return EMPTY_SET
    return "{" + ",".join(sorted(state_set)) + "}"
