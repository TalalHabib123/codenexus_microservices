from utils.helpers.function_extractor import extract_functions_from_code
from utils.rag.retrieval import retrieve_relevant_info_detection

def create_relevant_docs_for_long_functions(processed_data, knowledge_base_detection, nn_model):
    relevant_docs = []
    for file_path, functions in processed_data.items():
        for function_code in functions:
            relevant_docs.extend(retrieve_relevant_info_detection("Long Function", function_code, knowledge_base_detection, nn_model))
    return relevant_docs

def create_long_function_prompt(task_data, knowledge_base_detection, nn_model):
    processed_data = {}
    for file_path, content in task_data.items():
        processed_data[file_path] = extract_functions_from_code(content)

    relevant_docs = create_relevant_docs_for_long_functions(processed_data, knowledge_base_detection, nn_model)

    # Base content for the prompt
    content = "I am providing you with files and their functions as follows:\n\n"

    # Add files and their respective functions
    for file_path, functions in processed_data.items():
        for func_info in functions:
            class_part = f"{func_info['class_name']}." if func_info['class_name'] != "None" else ""
            # Include function details in the prompt
            content += (
                f"File:{{{file_path}}}\n"
                f"Function:{{{class_part}{func_info['function_name']}}}\n"
                f"Code:{{\n{func_info['function_code']}\n}}\n"
            )

    # Add detailed instructions for the LLM
    content += """
        Now, I want you to identify any functions that suffer from a "Long Function" code smell.

        A "Long Function" is characterized by:
        - Being excessively long or doing too many distinct tasks.
        - Lacking cohesion and performing multiple responsibilities that should be split into smaller, focused functions.
        - Having a large number of lines or complex logic beyond what is necessary for a single task.

        If the function is defined inside a class (Not None), you must return it in the format:
        CLASSNAME.FUNCTIONNAME

        If the function is defined at the top-level (not inside a class), just return FUNCTIONNAME as-is.

        If you find any functions that qualify as a long function, respond with them in the following format (and only this format, no extra commentary):

        File:{file_name}.py
        Detected:{CLASSNAME.FUNCTIONNAME or FUNCTIONNAME}

        If there are multiple long functions in the same file, list them each on a new line after the same File: line.

        If no functions qualify as long functions, respond with:
        None
    """

    # Include relevant reference documents if available
    if relevant_docs:
        content += (
            "\nThe following reference documents are provided. They contain examples or definitions related "
            "to long function code smells. Use them as references when analyzing the above files and their functions:\n"
        )
        for documents in relevant_docs:
            for index, (key, doc) in enumerate(documents.items(), start=1):
                content += f"Reference {index}:\n{{\n{doc}\n}}\n"

    # Return the prompt and processed data
    return {
        "role": "user",
        "content": content.strip()
    }, processed_data
