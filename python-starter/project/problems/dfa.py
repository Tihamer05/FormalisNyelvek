from project.problem import Problem
import argparse

class DfaProblem(Problem):

    def initialize_parser(self, parser):
        parser.add_argument('--check', type=str, help='Words to check')

    def is_chosen_problem(self, args):
        return bool(args.check)

    def run(self, args):
        input_file = args.input
        output_file = args.output
        words_to_check = args.check.split(',')

        with open(input_file, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]

            states = set(lines[0].split())
            alphabet = set(lines[1].split())
            start_state = lines[2].strip()
            accept_states = set(lines[3].split())

            transitions = {}
            for line in lines[4:]:
                parts = line.split()
                if len(parts) == 3:
                    src, symbol, dst = parts
                    transitions[(src, symbol)] = dst

        results = []
        for word in words_to_check:
            current_state = start_state
            accepted = True

            for symbol in word:
                if symbol not in alphabet or (current_state, symbol) not in transitions:
                    accepted = False
                    break
                current_state = transitions[(current_state, symbol)]

            if accepted and current_state in accept_states:
                results.append("IGEN")
            else:
                results.append("NEM")

        with open(output_file, 'w') as f:
            f.write('\n'.join(results) + '\n')               