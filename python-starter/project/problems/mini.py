import argparse
from collections import deque
import re
from project.problem import Problem


def state_sort_key(s: str):
    match = re.match(r'^([a-zA-Z]+)(\d+)$', s)
    if match:
        return (0, match.group(1), int(match.group(2)))
    return (1, s)


def rename_state(state: str) -> str:
    if state.startswith('q'):
        return 's' + state[1:]
    elif state.startswith('s'):
        return state
    else:
        return 's' + state


class MiniProblem(Problem):

    def initialize_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('--mini', action='store_true', help='Minimize the given automaton')

    def is_chosen_problem(self, args):
        return bool(args.mini)

    def run(self, args):
        input_file = args.input
        output_file = args.output

        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()

        lines = [line.strip() for line in lines]

        if len(lines) < 4:
            raise ValueError("Input file must contain at least 4 lines for automaton definition.")

        states = lines[0].split()
        alphabet = lines[1].split()
        start_state = lines[2].strip()
        accept_states = lines[3].split() if lines[3] else []

        states_set = set(states)
        alphabet_set = set(alphabet)

        if start_state not in states_set:
            raise ValueError(f"Start state '{start_state}' is not among defined states.")

        for acc in accept_states:
            if acc not in states_set:
                raise ValueError(f"Accept state '{acc}' is not among defined states.")

        transitions = {}
        for line in lines[4:]:
            if not line:
                continue
            parts = line.split()
            if len(parts) != 3:
                raise ValueError(f"Invalid transition format: '{line}'")
            src, sym, dst = parts
            if src not in states_set:
                raise ValueError(f"Transition source state '{src}' is not among defined states.")
            if sym not in alphabet_set:
                raise ValueError(f"Transition symbol '{sym}' is not in alphabet.")
            if dst not in states_set:
                raise ValueError(f"Transition destination state '{dst}' is not among defined states.")

            transitions[(src, sym)] = dst

        # 1. Eliminate unreachable states from start_state
        reachable = set()
        queue = deque([start_state])
        reachable.add(start_state)

        while queue:
            curr = queue.popleft()
            for sym in alphabet:
                if (curr, sym) in transitions:
                    nxt = transitions[(curr, sym)]
                    if nxt not in reachable:
                        reachable.add(nxt)
                        queue.append(nxt)

        reachable_states = [s for s in states if s in reachable]
        reachable_accept_states = set(s for s in accept_states if s in reachable)
        reachable_transitions = {
            (src, sym): dst
            for (src, sym), dst in transitions.items()
            if src in reachable and dst in reachable
        }

        # 2. Partition refinement (Moore's algorithm)
        F = set(s for s in reachable_states if s in reachable_accept_states)
        NF = set(s for s in reachable_states if s not in reachable_accept_states)

        partitions = []
        if F:
            partitions.append(F)
        if NF:
            partitions.append(NF)

        while True:
            state_to_partition = {}
            for idx, part in enumerate(partitions):
                for s in part:
                    state_to_partition[s] = idx

            new_partitions = []
            split_occurred = False

            for part in partitions:
                signatures = {}
                for s in part:
                    sig = []
                    for sym in alphabet:
                        target = reachable_transitions.get((s, sym))
                        if target is not None:
                            sig.append(state_to_partition[target])
                        else:
                            sig.append(-1)
                    sig = tuple(sig)
                    if sig not in signatures:
                        signatures[sig] = set()
                    signatures[sig].add(s)

                if len(signatures) > 1:
                    split_occurred = True

                for split_part in signatures.values():
                    new_partitions.append(split_part)

            partitions = new_partitions
            if not split_occurred:
                break

        # 3. Form new state names from equivalence classes
        state_to_new = {}
        for part in partitions:
            representative = min(part, key=state_sort_key)
            new_name = rename_state(representative)
            for s in part:
                state_to_new[s] = new_name

        new_states = sorted(list(set(state_to_new.values())), key=state_sort_key)
        new_start_state = state_to_new[start_state]
        new_accept_states = [
            st for st in new_states
            if any(q in reachable_accept_states for q in reachable_states if state_to_new[q] == st)
        ]

        # 4. Form transitions
        new_transitions = set()
        for (src, sym), dst in reachable_transitions.items():
            new_src = state_to_new[src]
            new_dst = state_to_new[dst]
            new_transitions.add((new_src, sym, new_dst))

        sorted_transitions = sorted(
            new_transitions,
            key=lambda t: (state_sort_key(t[0]), t[1], state_sort_key(t[2]))
        )

        output_lines = [
            ' '.join(new_states),
            ' '.join(alphabet),
            new_start_state,
            ' '.join(new_accept_states)
        ] + [f"{src} {sym} {dst}" for src, sym, dst in sorted_transitions]

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines) + '\n')

