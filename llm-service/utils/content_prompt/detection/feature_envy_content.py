from utils.helpers.function_extractor import extract_functions_from_code
from utils.rag.retrieval import retrieve_relevant_info_detection

def create_relevant_docs_for_feature_envy(processed_data, knowledge_base_detection, nn_model):
    relevant_docs = []
    for file_path, functions in processed_data.items():
        for function_code in functions:
            relevant_docs.extend(retrieve_relevant_info_detection("Feature Envy", function_code, knowledge_base_detection, nn_model))
    return relevant_docs

def create_feature_envy_prompt(task_data, knowledge_base_detection, nn_model):
    processed_data = {}
    for file_path, content in task_data.items():
        processed_data[file_path] = extract_functions_from_code(content)

    relevant_docs = create_relevant_docs_for_feature_envy(processed_data, knowledge_base_detection, nn_model)

    # Base content for the prompt
    content = "I am providing you with files and their functions as follows:\n\n"

    # Add files and their respective functions
    for file_path, functions in processed_data.items():
        for func_info in functions:
            # If class_name is None or empty, just use the function name; otherwise format CLASSNAME.FUNCTIONNAME
            class_name = func_info['class_name']+"." if func_info['class_name'] else ""
            content += (
                f"File:{{{file_path}}}\n"
                f"Function:{{{class_name}{func_info['function_name']}}}\n"
                f"Code:{{\n{func_info['function_code']}\n}}\n"
            )

    # Add instructions for identifying feature envy
    content += """
        Now, identify any functions that qualify as a "Feature Envy" code smell based on the definition:
        - The function relies heavily on accessing data or methods from another class, indicating it might be more appropriate as part of that class.
        - Most of the function's logic involves interacting with another class's fields or methods instead of its own.

        Follow these response rules exactly:
        - If no feature envy is found, respond with 'None' only.
        - If any are found, respond only in this format, no extra commentary:
        
        File:{file_name}.py
        Detected:{CLASSNAME.FUNCTIONNAME or FUNCTIONNAME}
        Issue:{brief description of why it exhibits feature envy, e.g. relies heavily on methods from another class}

        Multiple detections in the same file should be listed under the same File line, each Detected and Issue on new lines.

        Do not mention correlation IDs or processed data lines.
        Do not provide additional commentary beyond what is requested.
    """

    # Include relevant docs if available
    if relevant_docs:
        content += (
            "\nThe following reference documents are provided for additional context on feature envy:\n"
        )
        for documents in relevant_docs:
            for index, (key, doc) in enumerate(documents.items(), start=1):
                content += f"Reference {index}:\n{{\n{doc}\n}}\n"

    return {
        "role": "user",
        "content": content.strip()
    }, processed_data
