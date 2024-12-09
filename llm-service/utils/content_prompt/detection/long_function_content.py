from utils.content_prompt.detection.utils.process_data import process_data
from utils.content_prompt.detection.utils.retrieve_relevant_docs import retrieve_relevant_docs_for_


def create_long_function_prompt(task_data, knowledge_base_detection, nn_model):
    processed_data = process_data(task_data, "functions", "Long Function")
    # for file_path, content in task_data.items():
    #     processed_data[file_path] = extract_functions_from_code(content)

    # relevant_docs = create_relevant_docs_for_long_functions(processed_data, knowledge_base_detection, nn_model)
    relevant_docs = retrieve_relevant_docs_for_("Long Function", processed_data, knowledge_base_detection, nn_model)
    
    # Base content for the prompt
    content = "I am providing you with files and their functions as follows:\n\n"

    # Add files and their respective functions
    for file_path, functions in processed_data.items():
        for func_info in functions:
            # If class_name is None or empty, just use the function name; otherwise format CLASSNAME.FUNCTIONNAME
            class_name = func_info['class_name']+"." if func_info['class_name'] else ""
            content += (
                f"File:{{{file_path}}}\n"
                f"Function:{{{func_info['function_name']}}}\n"
                f"Code:{{\n{func_info['function_code']}\n}}\n"
            )

    # Add instructions for identifying long functions
    content += """
        Now, identify any functions that qualify as a "Long Function" code smell based on the definition:
        - Exceeds a reasonable line threshold (~100 lines of substantive code).
        - Performs multiple unrelated tasks.
        - Is excessively complex or deeply nested.

        Follow these response rules exactly:
        - If no long functions are found, respond with 'None' only.
        - If any are found, respond only in this format, no extra commentary:
        - If it a function contains multiple Issues, list them in one response under one issue and separate them with "."
        
        File:{file_name}.py
        Detected:{CLASSNAME.FUNCTIONNAME or FUNCTIONNAME}
        Issue:{brief description of why it is long, e.g. multiple tasks or excessive lines}
        
        Multiple detections in the same file should be listed under the same File line, each Detected and Issue on new lines.

        Do not mention correlation IDs or processed data lines.
        Do not provide additional commentary beyond what is requested.
    """

    # Include relevant docs if available
    if relevant_docs:
        content += (
            "\nThe following reference documents are provided for additional context on long functions:\n"
        )
        for documents in relevant_docs:
            for index, (key, doc) in enumerate(documents.items(), start=1):
                content += f"Reference {index}:\n{{\n{doc}\n}}\n"

    return {
        "role": "user",
        "content": content.strip()
    }, processed_data

