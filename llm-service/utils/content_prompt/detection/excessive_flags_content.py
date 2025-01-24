from utils.content_prompt.detection.utils.process_data import process_data
from utils.content_prompt.detection.utils.retrieve_relevant_docs import retrieve_relevant_docs_for_


def create_excessive_flags_prompt(task_data, knowledge_base_detection, nn_model):
    processed_data = process_data(task_data, "functions", "Excessive Use of Flags")
    relevant_docs = retrieve_relevant_docs_for_("Excessive Use of Flags", processed_data, knowledge_base_detection, nn_model)

    # Base content for the prompt
    content = "I am providing you with files and their functions as follows:\n\n"

    # Add files and their respective functions
    for file_path, functions in processed_data.items():
        for func_info in functions:
            class_part = f"{func_info['class_name']}." if func_info['class_name'] else ""
            content += (
                f"File:{{{file_path}}}\n"
                f"Function:{{{func_info['function_name']}}}\n"
                f"Code:{{\n{func_info['function_code']}\n}}\n"
            )

    # Add detailed instructions for identifying excessive flags
    content += """
        Review all provided functions from each file and determine if they exhibit the Excessive Use of Flags code smell.

        A **function exhibits Excessive Use of Flags** if:
        - It relies on one or more boolean or flag parameters to alter its behavior, leading to multiple execution paths.
        - Different tasks or behaviors are handled within the same function based on the flag's value, resulting in poor cohesion.
        - The function becomes harder to understand, maintain, or extend due to the branching logic triggered by flags.

        Characteristics of Excessive Use of Flags:
        - Functions accept boolean parameters and use conditionals (e.g., `if flag:` or `if not flag:`) to differentiate logic.
        - Multiple distinct tasks are embedded in the same function instead of being split into smaller, dedicated functions.
        - The behavior of the function changes significantly depending on the flags passed.

        Follow these response rules exactly:
        - If no excessive flag usage is found, respond with 'None' only.
        - If any functions exhibit excessive flag usage, respond in this format (no additional commentary):

        File:{file_name}.py
        Detected:{CLASSNAME.FUNCTIONNAME or FUNCTIONNAME}
        Issue:{brief description of how the flags are used excessively and why it is problematic}

        If multiple functions in the same file exhibit excessive flag usage, list each Detected and Issue under the same File heading.

        Do not include correlation IDs or extraneous details. Only provide the specified response format.
    """

    additonal_content = content

    # Include relevant reference documents if available
    if relevant_docs:
        content += (
            "\nThe following reference documents are provided for additional context on Excessive Use of Flags code smells:\n"
        )
        for documents in relevant_docs:
            for index, (key, doc) in enumerate(documents.items(), start=1):
                content += f"Reference {index}:\n{{\n{doc}\n}}\n"

    # Return the complete prompt as a dictionary
    return {
        "role": "user",
        "content": content.strip()
    },{
        "role": "user",
        "content": additonal_content.strip()    
    }, processed_data
