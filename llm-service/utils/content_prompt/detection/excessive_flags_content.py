from utils.content_prompt.detection.utils.process_data import process_data
from utils.content_prompt.detection.utils.retrieve_relevant_docs import retrieve_relevant_docs_for_


def create_excessive_flags_prompt(task_data, knowledge_base_detection, nn_model):
    processed_data = process_data(task_data, "functions", "Excessive Use of Flags")
    # for file_path, content in task_data.items():
    #     processed_data[file_path] = extract_functions_from_code(content)
        
    # relevant_docs = create_relevant_docs_for_excessive_flags(processed_data, knowledge_base_detection, nn_model)
    relevant_docs = retrieve_relevant_docs_for_("Excessive Use of Flags", processed_data, knowledge_base_detection, nn_model)

    # Create the base content with the processed data
    content = (
        "I am providing you with files and their functions as follows:\n\n"
    )
    
    # Add the files and their respective functions
    for file_path, functions in processed_data.items():
        for func_info in functions:
            class_part = f"{func_info['class_name']}." if func_info['class_name'] else ""
            content += (
                f"File:{{{file_path}}}\n"
                f"Function:{{{class_part}{func_info['function_name']}}}\n"
                f"Code:{{\n{func_info['function_code']}\n}}\n"
            )

    # Append the instruction part of the prompt
    content += """
        Review all provided functions from each file and determine if they exhibit an Excessive Use of Flags code smell.
        **Excessive Use of Flags** is characterized by:
        - The overuse of boolean or flag parameters in function calls to control execution paths.
        - Functions becoming difficult to understand because the behavior changes significantly depending on the flag's value.
        - Poor cohesion due to multiple unrelated tasks being handled within the same function, triggered by different flag values.

        Characteristics of Excessive Use of Flags:
        - The function accepts one or more boolean parameters that alter its behavior.
        - Code branches or paths (e.g., `if flag:` or `if not flag:`) exist in the function to handle different behaviors, leading to increased complexity.
        - The function can be split into smaller, focused functions instead of relying on flags to determine execution.

        If you find any functions that qualify as Excessive Use of Flags based on these criteria, respond with them in the following format:
        Your Answer Should only contain the following File Name and Detected Function in the exact format (including the braces):
        
        File:{file_name}.py
        Detected:{CLASSNAME.FUNCTIONNAME or FUNCTIONNAME}
        Issue:{brief description of how the flags are used excessively and why it is problematic}
        
        If there are multiple functions in the same file that qualify, list them separately under the same file heading.

        If no functions qualify as having Excessive Use of Flags, respond with:
        None
    """

    # Add relevant documents to the prompt if available
    if relevant_docs:
        content += (
            "\nThe following documents are provided as references. These documents contain examples of "
            "Excessive Use of Flags code smells. Use them as references when analyzing the above files and their functions:\n"
        )
        for documents in relevant_docs:
            for index, (key, doc) in enumerate(documents.items(), start=1):
                content += f"Reference {index}:\n{{\n{doc}\n}}\n"

    # Return the complete prompt as a dictionary
    return {
        "role": "user",
        "content": content.strip()
    }, processed_data
