from utils.content_prompt.detection.utils.process_data import process_data
from utils.content_prompt.detection.utils.retrieve_relevant_docs import retrieve_relevant_docs_for_


def create_switch_statement_abuser_prompt(task_data, knowledge_base_detection, nn_model):
    processed_data = process_data(task_data, "functions", "Switch Statement Abuser")
    relevant_docs = retrieve_relevant_docs_for_("Switch Statement Abuser", processed_data, knowledge_base_detection, nn_model)

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

    # Add detailed instructions for identifying Switch Statement Abusers
    content += """
        Analyze the provided functions and determine if any exhibit the Switch Statement Abuser code smell.

        A **Switch Statement Abuser** is characterized by:
        - Overuse of `if-elif` constructs or Python's functional equivalent of a switch statement.
        - Handling too many distinct cases within a single function or method.
        - Repeated patterns or logic across cases that could be modularized using smaller functions or object-oriented principles like polymorphism.

        Key indicators of a Switch Statement Abuser include:
        - Heavy reliance on conditionals to differentiate between cases.
        - Each case performing distinct but non-encapsulated tasks, leading to tightly coupled logic.
        - Difficulties in extending, maintaining, or testing the function due to its size or complexity.

        Follow these response rules exactly:
        - If no Switch Statement Abusers are found, respond with 'None' only.
        - If any are found, respond only in this format, no extra commentary:
        
        File:{file_name}.py
        Detected:{CLASSNAME.FUNCTIONNAME or FUNCTIONNAME}
        Issue:{brief description of why it is a Switch Statement Abuser (e.g., tightly coupled logic, excessive cases, lack of modularization)}

        If multiple functions are found in the same file, list each under the same File heading with their Detected and Issue lines.

        Do not mention correlation IDs or processed data lines.
        Do not provide additional commentary beyond what is requested.
    """
    
    additonal_content = content

    # Include relevant reference documents if available
    if relevant_docs:
        content += (
            "\nThe following reference documents are provided for additional context on Switch Statement Abusers:\n"
        )
        for documents in relevant_docs:
            for index, (key, doc) in enumerate(documents.items(), start=1):
                content += f"Reference {index}:\n{{\n{doc}\n}}\n"

    # Return the prompt and processed data
    return {
        "role": "user",
        "content": content.strip()
    },{
        "role": "user",
        "content": additonal_content.strip()    
    }, processed_data
