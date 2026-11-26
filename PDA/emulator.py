from collections import deque
from dataclasses import dataclass
from typing import Iterable

from parser import PDASpec


EPSILON = "epsilon"
EPSILON_ALIASES = {EPSILON, "eps", "lambda", "$"}
EMPTY_SET = "{}"
MAX_CONFIGURATIONS = 5000


@dataclass(frozen=True)
class Configuration:
    state: str
    position: int
    stack: tuple[str, ...]


@dataclass(frozen=True)
class Step:
    before: Configuration
    input_symbol: str
    stack_top: str
    next_state: str
    push_symbols: tuple[str, ...]
    after: Configuration


@dataclass(frozen=True)
class RunResult:
    accepted: bool
    steps: list[Step]
    final_configuration: Configuration
    reason: str
    explored_configurations: int


class PDA:
    def __init__(
        self,
        states: Iterable[str],
        alphabet: Iterable[str],
        stack_alphabet: Iterable[str],
        start_state: str,
        start_stack: str,
        final_states: Iterable[str],
        accept_by: str = "final_state",
    ) -> None:
        self.states = set(states)
        self.alphabet = set(alphabet)
        self.stack_alphabet = set(stack_alphabet)
        self.start_state = start_state
        self.start_stack = start_stack
        self.final_states = set(final_states)
        self.accept_by = accept_by
        self.transitions: dict[tuple[str, str, str], set[tuple[str, tuple[str, ...]]]] = {}

        if self.start_state not in self.states:
            raise ValueError("Starea initiala trebuie sa apartina multimii starilor.")
        if self.start_stack not in self.stack_alphabet:
            raise ValueError("Simbolul initial al stivei trebuie sa apartina alfabetului stivei.")
        unknown_final_states = self.final_states - self.states
        if unknown_final_states:
            raise ValueError(f"Stari finale necunoscute: {', '.join(sorted(unknown_final_states))}")
        epsilon_in_alphabet = self.alphabet & EPSILON_ALIASES
        if epsilon_in_alphabet:
            raise ValueError("Epsilon nu trebuie pus in alfabet; se foloseste doar in tranzitii.")
        if self.accept_by not in {"final_state", "empty_stack"}:
            raise ValueError("accept_by poate fi doar final_state sau empty_stack.")

    def add_transition(
        self,
        state: str,
        input_symbol: str,
        stack_top: str,
        next_state: str,
        push_symbols: Iterable[str],
    ) -> None:
        normalized_input = normalize_symbol(input_symbol)
        push_tuple = tuple(push_symbols)

        if state not in self.states:
            raise ValueError(f"Stare necunoscuta in tranzitie: {state}")
        if next_state not in self.states:
            raise ValueError(f"Stare destinatie necunoscuta: {next_state}")
        if normalized_input != EPSILON and normalized_input not in self.alphabet:
            raise ValueError(f"Simbol de intrare necunoscut in tranzitie: {input_symbol}")
        if stack_top not in self.stack_alphabet:
            raise ValueError(f"Simbol necunoscut in varful stivei: {stack_top}")

        unknown_stack_symbols = set(push_tuple) - self.stack_alphabet
        if unknown_stack_symbols:
            raise ValueError(
                "Simboluri necunoscute puse pe stiva: "
                + ", ".join(sorted(unknown_stack_symbols))
            )

        key = (state, normalized_input, stack_top)
        self.transitions.setdefault(key, set()).add((next_state, push_tuple))

    def run(self, word: str) -> RunResult:
        symbols = self.split_word(word)
        start = Configuration(
            state=self.start_state,
            position=0,
            stack=(self.start_stack,),
        )

        queue = deque([(start, [])])
        visited = {start}
        best_rejected = start
        best_rejected_path: list[Step] = []
        explored = 0

        while queue and explored < MAX_CONFIGURATIONS:
            configuration, path = queue.popleft()
            explored += 1
            best_rejected = configuration
            best_rejected_path = path

            if self.is_accepting(configuration, len(symbols)):
                return RunResult(
                    accepted=True,
                    steps=path,
                    final_configuration=configuration,
                    reason=self.acceptance_reason(configuration),
                    explored_configurations=explored,
                )

            for step in self.next_steps(configuration, symbols):
                if step.after in visited:
                    continue
                visited.add(step.after)
                queue.append((step.after, path + [step]))

        if explored >= MAX_CONFIGURATIONS:
            reason = "S-a atins limita de configuratii explorate; posibil exista o bucla epsilon."
        else:
            reason = self.rejection_reason(best_rejected, symbols)

        return RunResult(
            accepted=False,
            steps=best_rejected_path,
            final_configuration=best_rejected,
            reason=reason,
            explored_configurations=explored,
        )

    def accepts(self, word: str) -> bool:
        return self.run(word).accepted

    def next_steps(self, configuration: Configuration, symbols: list[str]) -> list[Step]:
        if not configuration.stack:
            return []

        stack_top = configuration.stack[0]
        available_inputs = [EPSILON]
        if configuration.position < len(symbols):
            available_inputs.insert(0, symbols[configuration.position])

        steps: list[Step] = []
        for input_symbol in available_inputs:
            key = (configuration.state, input_symbol, stack_top)
            for next_state, push_symbols in sorted(self.transitions.get(key, set())):
                next_position = configuration.position
                if input_symbol != EPSILON:
                    next_position += 1

                next_stack = push_symbols + configuration.stack[1:]
                after = Configuration(
                    state=next_state,
                    position=next_position,
                    stack=next_stack,
                )
                steps.append(
                    Step(
                        before=configuration,
                        input_symbol=input_symbol,
                        stack_top=stack_top,
                        next_state=next_state,
                        push_symbols=push_symbols,
                        after=after,
                    )
                )

        return steps

    def is_accepting(self, configuration: Configuration, word_length: int) -> bool:
        if configuration.position != word_length:
            return False
        if self.accept_by == "final_state":
            return configuration.state in self.final_states
        return not configuration.stack

    def acceptance_reason(self, configuration: Configuration) -> str:
        if self.accept_by == "final_state":
            return (
                "inputul a fost consumat complet si starea finala este "
                f"{configuration.state}."
            )
        return "inputul a fost consumat complet si stiva este goala."

    def rejection_reason(self, configuration: Configuration, symbols: list[str]) -> str:
        remaining = remaining_input(symbols, configuration.position)
        if configuration.stack:
            top = configuration.stack[0]
            current_symbol = symbols[configuration.position] if configuration.position < len(symbols) else EPSILON
            return (
                "nu exista tranzitie valida pentru "
                f"delta({configuration.state}, {current_symbol}, {top}); "
                f"input ramas: {remaining}."
            )
        return f"stiva este goala, dar configuratia nu este acceptata; input ramas: {remaining}."

    def nondeterminism_reasons(self) -> list[str]:
        reasons: list[str] = []

        for (state, input_symbol, stack_top), targets in sorted(self.transitions.items()):
            if len(targets) > 1:
                reasons.append(
                    f"delta({state}, {input_symbol}, {stack_top}) are mai multe destinatii"
                )

        keys = set(self.transitions)
        for state, input_symbol, stack_top in sorted(keys):
            if input_symbol == EPSILON:
                continue
            if (state, EPSILON, stack_top) in keys:
                reasons.append(
                    f"delta({state}, {input_symbol}, {stack_top}) concureaza cu "
                    f"delta({state}, epsilon, {stack_top})"
                )

        return reasons

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


def normalize_symbol(symbol: str) -> str:
    lowered = symbol.strip().lower()
    if lowered in EPSILON_ALIASES:
        return EPSILON
    return symbol.strip()


def build_pda(spec: PDASpec) -> PDA:
    pda = PDA(
        states=spec.states,
        alphabet=spec.alphabet,
        stack_alphabet=spec.stack_alphabet,
        start_state=spec.start_state,
        start_stack=spec.start_stack,
        final_states=spec.final_states,
        accept_by=spec.accept_by,
    )
    for (state, input_symbol, stack_top), targets in spec.transitions.items():
        for next_state, push_symbols in targets:
            pda.add_transition(state, input_symbol, stack_top, next_state, push_symbols)
    return pda


def format_symbols(symbols: Iterable[str]) -> str:
    ordered = sorted(symbols)
    if not ordered:
        return EMPTY_SET
    return "{" + ", ".join(ordered) + "}"


def format_stack(stack: tuple[str, ...]) -> str:
    if not stack:
        return EPSILON
    return "".join(stack)


def format_push(push_symbols: tuple[str, ...]) -> str:
    if not push_symbols:
        return EPSILON
    return " ".join(push_symbols)


def remaining_input(symbols: list[str], position: int) -> str:
    remaining = symbols[position:]
    if not remaining:
        return EPSILON
    return "".join(remaining)


def format_configuration(configuration: Configuration, symbols: list[str]) -> str:
    return (
        f"({configuration.state}, "
        f"{remaining_input(symbols, configuration.position)}, "
        f"{format_stack(configuration.stack)})"
    )


def format_trace(steps: list[Step], symbols: list[str], final_configuration: Configuration) -> str:
    if not steps:
        return format_configuration(final_configuration, symbols)

    parts = [format_configuration(steps[0].before, symbols)]
    for step in steps:
        transition = (
            f"delta({step.before.state}, {step.input_symbol}, {step.stack_top}) = "
            f"({step.next_state}, {format_push(step.push_symbols)})"
        )
        parts.append(f"{transition} => {format_configuration(step.after, symbols)}")
    return " | ".join(parts)


