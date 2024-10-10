import json
from collections import defaultdict



def get_duplicated_code( source_code):
        duplicates = []
        lines = source_code.split('\n')
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
        duplicates = unique_duplicates
        dupList = []
        for seq, positions in unique_duplicates:
            dupList.append([positions[0], positions[0] + len(seq) - 1])
        return json.dumps(dupList)

