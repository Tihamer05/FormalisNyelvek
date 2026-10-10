from project.problem import Problem
import argparse
from collections import deque

class DetProblem(Problem): 
    def initialize_parser(self, parser):
        parser.add_argument('--det', action='store_true')

    def is_chosen_problem(self, args):
        return bool(args.det)

    def run(self, args):
        input_file = args.input
        output_file = args.output

        with open(input_file, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]

        states = lines[0].split()
        alphabet = lines[1].split()
        start_state = lines[2].strip()
        accept_states = set(lines[3].split())

        transactions = {}
        for line in lines[4:]:
            parts = line.split()
            if len(parts) == 3:
                src, sym, dst = parts
                if(src, sym) not in transactions:
                    transactions[(src, sym)] = set()
                transactions[(src, sym)].add(dst)

        initial_subset = frozenset([start_state])

        subset_to_name = {initial_subset: "s0"}
        name_to_subset = {"s0": initial_subset}
        queue = deque([initial_subset])
        state_counter = 1

        dfa_transactions = []

        while queue:
            current_subset = queue.popleft()
            current_name = subset_to_name[current_subset]

            for sym in alphabet:
                next_subset_set = set()
                for st in current_subset:
                    if (st, sym) in transactions:
                        next_subset_set.update(transactions[(st, sym)])

                if next_subset_set:
                    next_subset = frozenset(next_subset_set)
                    if next_subset not in subset_to_name:
                        new_name = f"s{state_counter}"
                        state_counter += 1
                        subset_to_name[next_subset] = new_name
                        name_to_subset[new_name] = next_subset
                        queue.append(next_subset)

                    target_name = subset_to_name[next_subset]
                    dfa_transactions.append(f"{current_name} {sym} {target_name}")

        dfa_states = [f"s{i}" for i in range(state_counter)]

        dfa_accept_states = [
            name for name in dfa_states
            if any(q in accept_states for q in name_to_subset[name])
        ]

        output_lines = [
            ' '.join(dfa_states),
            ' '.join(alphabet),
            "s0",
            ' '.join(dfa_accept_states)
        ] + dfa_transactions

        with open(output_file, 'w') as f:
            f.write('\n'.join(output_lines) + '\n')