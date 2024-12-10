import hashlib

def generate_unique_name(file_path, existing_keys, length=6):
    """
    Generate a unique name for a given file path using a hash function, limited to a specific length.
    
    Args:
        file_path (str): Original file path.
        existing_keys (set): Set of already generated keys to ensure uniqueness.
        length (int): Desired initial length of the unique name.

    Returns:
        str: Unique name with .py appended.
    """
    hash_value = hashlib.md5(file_path.encode()).hexdigest()
    unique_name = hash_value[:length] + ".py"
    index = length

    # Ensure the generated name is unique
    while unique_name in existing_keys:
        unique_name = hash_value[:index] + ".py"
        index += 1

    return unique_name

def create_mapped_task_data(task_data):
    """
    Generate updated task_data with unique file path keys and a mapping dictionary.

    Args:
        task_data (dict): Original task_data with file paths as keys and code as values.

    Returns:
        tuple: A tuple containing:
            - updated_task_data: Dictionary with unique file path keys and code as values.
            - name_to_path_mapping: Dictionary with unique names as keys and original file paths as values.
    """
    updated_task_data = {}
    name_to_path_mapping = {}
    existing_keys = set()

    for file_path, code in task_data.items():
        unique_name = generate_unique_name(file_path, existing_keys)
        existing_keys.add(unique_name)
        updated_task_data[unique_name] = code
        name_to_path_mapping[unique_name] = file_path

    return updated_task_data, name_to_path_mapping

def revert_task_data_keys(task_data, name_to_path_mapping):
    """
    Revert the keys in the updated_task_data back to their original file paths.

    Args:
        task_data (dict): Updated task_data with unique file path keys and code as values.
        name_to_path_mapping (dict): Dictionary with unique names as keys and original file paths as values.

    Returns:
        dict: Dictionary with original file paths as keys and the same code values.
    """
    reverted_task_data = {}

    for unique_name, code in task_data.items():
        original_file_path = name_to_path_mapping.get(unique_name, unique_name)
        reverted_task_data[original_file_path] = code

    return reverted_task_data