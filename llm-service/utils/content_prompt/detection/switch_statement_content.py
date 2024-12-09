from utils.content_prompt.detection.utils.process_data import process_data
from utils.content_prompt.detection.utils.retrieve_relevant_docs import retrieve_relevant_docs_for_


def create_switch_statement_abuser_prompt(task_data, knowledge_base_detection, nn_model):
    processed_data = process_data(task_data, "functions", "Switch Statement Abuser")
    # for file_path, content in task_data.items():
    #     processed_data[file_path] = extract_functions_from_code(content)
        
    # relevant_docs = create_relevant_docs_for_switch_statement_abuser(processed_data, knowledge_base_detection, nn_model)
    relevant_docs = retrieve_relevant_docs_for_("Switch Statement Abuser", processed_data, knowledge_base_detection, nn_model)

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
        Review all provided functions from each file and determine if they exhibit a Switch Statement Abuser code smell.
        A **Switch Statement Abuser** is identified by:
        - Overusing `if-elif` or `switch` constructs (or their functional equivalent in Python, such as chained conditionals).
        - Handling too many distinct cases within a single function or method.
        - Repeating similar patterns or logic across multiple cases, instead of delegating to smaller, more focused functions or using polymorphism.

        Characteristics of a Switch Statement Abuser:
        - The function relies heavily on conditional constructs to handle various cases.
        - Each case performs different tasks but is not modularized or encapsulated.
        - The overall function becomes hard to maintain, extend, or test due to tightly coupled logic.

        If you find any functions that qualify as a Switch Statement Abuser based on these criteria, respond with them in the following format:
        Your Answer Should only contain the following File Name and Detected Function in the exact format (including the braces):
        
        File:{file_name}.py
        Detected:{CLASSNAME.FUNCTIONNAME or FUNCTIONNAME}
        If there are multiple functions in the same file that qualify, list them separately under the same file heading.

        If no functions qualify as Switch Statement Abusers, respond with:
        None
    """

    # Add relevant documents to the prompt if available
    if relevant_docs:
        content += (
            "\nThe following documents are provided as references. These documents contain examples of "
            "Switch Statement Abuser Code Smells. Use them as references when analyzing the above files and their functions:\n"
        )
        for documents in relevant_docs:
            for index, (key, doc) in enumerate(documents.items(), start=1):
                content += f"Reference {index}:\n{{\n{doc}\n}}\n"

    # Return the complete prompt as a dictionary
    return {
        "role": "user",
        "content": content.strip()
    }, processed_data
