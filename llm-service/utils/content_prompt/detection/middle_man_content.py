from utils.content_prompt.detection.utils.process_data import process_data
from utils.content_prompt.detection.utils.retrieve_relevant_docs import retrieve_relevant_docs_for_

def create_middle_man_prompt(task_data, knowledge_base_detection, nn_model):
    processed_data = process_data(task_data, "classes", "Middle Man")
    relevant_docs = retrieve_relevant_docs_for_("Middle Man", processed_data, knowledge_base_detection, nn_model)

    # Base content for the prompt
    content = "I am providing you with files and their classes as follows:\n\n"

    # Add files and their respective classes
    for file_path, classes in processed_data.items():
        for class_code in classes:
            content += f"File:{{{file_path}}}\nCode:{{\n{class_code}\n}}\n"

    # Add detailed instructions for identifying Middle Man code smells
    content += """
        Analyze the provided classes and determine if any exhibit the Middle Man code smell.

        A **Middle Man** is a class that:
        - Acts primarily as an intermediary between other classes without adding significant functionality of its own.
        - Delegates most of its methods to other classes without introducing meaningful logic or abstraction.
        - Encapsulates little or no additional behavior or responsibilities beyond forwarding calls.

        Characteristics of a Middle Man:
        - The class contains a high number of methods that are simple pass-throughs to another class or set of classes.
        - It does not provide significant computation, logic, or domain-specific behavior.
        - It increases indirection without improving modularity or reducing complexity.

        Follow these response rules exactly:
        - If no Middle Man code smells are found, respond with 'None' only.
        - If any are found, respond only in this format, no extra commentary:
        
        File:{file_name}.py
        Detected:{class_name}
        Issue:{brief description of why it is considered a Middle Man (e.g., excessive delegation, no meaningful behavior)}

        If multiple Middle Man classes are found in the same file, list each under the same File heading with their Detected and Issue lines.

        Do not mention correlation IDs or processed data lines.
        Do not provide additional commentary beyond what is requested.
    """
    
    additonal_content = content

    # Include relevant reference documents if available
    if relevant_docs:
        content += (
            "\nThe following reference documents are provided for additional context on Middle Man code smells:\n"
        )
        for documents in relevant_docs:
            for index, (key, doc) in enumerate(documents.items(), start=1):
                content += f"Reference {index}:\n{{\n{doc}\n}}\n"

    # Return the prompt and processed data
    return {
        "role": "user",
        "content": content.strip()
    }, {
        "role": "user",
        "content": additonal_content.strip()    
    }, processed_data
