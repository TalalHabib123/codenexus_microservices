import json
from collections import defaultdict
from app.models.ast_models import Duplicates, DuplicateCodeDetails


def get_duplicated_code(source_code: str) -> str:
    duplicates = []
    lines = source_code.split('\n')
    print(lines)
    normalized_lines = [line.strip() for line in lines]
    line_count = len(normalized_lines)
    min_sequence_length = 2  
    max_sequence_length = 10  

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
    duplicate_code_details_list = []
    for seq, positions in unique_duplicates:
        original_code = "\n".join(seq)
        start_line = positions[0]
        end_line = positions[0] + len(seq) - 1
        duplicates = [{"code":"\n".join(seq), "start_line":pos, "end_line":pos + len(seq) - 1}for pos in positions[1:]]
        duplicate_code_details = {
            "original_code":original_code,
            "start_line":start_line,
            "end_line":end_line,
            "duplicates":duplicates,
            "duplicate_count":len(duplicates)
        }
        duplicate_code_details_list.append(duplicate_code_details)
    return duplicate_code_details_list