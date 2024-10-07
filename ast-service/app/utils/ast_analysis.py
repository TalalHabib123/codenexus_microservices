import json
from app.utils.visitors import (
    FunctionVisitor,
    GlobalVisitor
)
from collections import defaultdict

# extract magic numbers from the ast 
def get_magic_numbers(parsed_ast: str):
    visitor = GlobalVisitor()
    # visitor.visit(parsed_ast)
    return json.dumps(dict(visitor.get_magic_numbers(parsed_ast)))

# extract number of paramenters
def get_parameter_list(parsed_ast:str):
    visitor = FunctionVisitor()
    visitor.visit(parsed_ast)
    param_list = visitor.get_function_arguments()
    res = {key: True if value > 3 else False for key, value in param_list.items()} # long param iff num of params is more than 3
    return json.dumps(dict(res))

# function to extract duplicate code snippets 
def get_duplicated_code( source_code):
        duplicates = []
        lines = source_code.split('\n')
        normalized_lines = [line.strip() for line in lines]
        line_count = len(normalized_lines)
        min_sequence_length = 2  # Minimum number of consecutive lines for a duplicate snippet
        max_sequence_length = 10  # Maximum length of sequence to check

        # Map from sequence representation to list of starting line numbers
        sequence_map = defaultdict(list)

        # Build sequences
        for seq_length in range(min_sequence_length, max_sequence_length + 1):
            for i in range(line_count - seq_length + 1):
                seq = normalized_lines[i:i+seq_length]
                seq_repr = tuple(seq)
                sequence_map[seq_repr].append(i + 1)  # Line numbers are 1-based

        # Find sequences that occur more than once
        duplicated_sequences = {seq: positions for seq, positions in sequence_map.items() if len(positions) > 1}

        # Filter out overlapping sequences
        sorted_sequences = sorted(duplicated_sequences.items(), key=lambda x: -len(x[0]))

        covered_positions = set()
        unique_duplicates = []

        for seq, positions in sorted_sequences:
            new_positions = []
            for pos in positions:
                overlapping = any((pos + offset) in covered_positions for offset in range(len(seq)))
                if not overlapping:
                    new_positions.append(pos)
                    covered_positions.update(pos + offset for offset in range(len(seq)))

            if len(new_positions) > 1:
                unique_duplicates.append((seq, new_positions))

        # Store the duplicates
        duplicates = unique_duplicates
        dupList = []
        for seq, positions in unique_duplicates:
            dupList.append([positions[0], positions[0] + len(seq) - 1])
        return json.dumps(dupList)

# Extract unused variables
def get_unused_variables(parsed_ast:str):
    visitor = FunctionVisitor()
    visitor.visit(parsed_ast)
    return json.dumps(visitor.get_unused_variables())

# naming convention
def get_naming_convention(parsed_ast:str):
    visitor = GlobalVisitor()
    conventions = visitor.get_naming_convention(parsed_ast)
    total = 0
    snake_case = conventions['snake_case']
    camel_case = conventions['camel_case']
    pascal_case = conventions['pascal_case']
    for key in conventions:
        total += len(conventions[key])
    snake_percent = (len(snake_case)/total) * 100
    camel_percent = (len(camel_case)/total) * 100
    pascal_percent = (len(pascal_case)/total) * 100
    unknown = 100 - (snake_percent + camel_percent + pascal_percent)
    return json.dumps({
        'snake_case': len(snake_case),
        'camel_case': len(camel_case),
        'pascal_case': len(pascal_case),
        'unknown': total - (snake_percent + camel_percent + pascal_percent)
    })