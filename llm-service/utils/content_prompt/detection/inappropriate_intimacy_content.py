from utils.content_prompt.detection.utils.process_data import process_data
from utils.content_prompt.detection.utils.retrieve_relevant_docs import retrieve_relevant_docs_for_

def create_inappropriate_intimacy_prompt(task_data, knowledge_base_detection, nn_model):
    processed_data = process_data(task_data, "classes", "Inappropriate Intimacy")
    relevant_docs = retrieve_relevant_docs_for_("Inappropriate Intimacy", processed_data, knowledge_base_detection, nn_model)

    # Base content for the prompt
    content = "I am providing you with files and their classes as follows:\n\n"

    # Add files and their respective classes
    for file_path, classes in processed_data.items():
        for class_code in classes:
            content += f"File:{{{file_path}}}\nCode:{{\n{class_code}\n}}\n"

    # Add detailed instructions for identifying Inappropriate Intimacy code smells
    content += """
        Analyze the provided classes and determine if any exhibit the Inappropriate Intimacy code smell.

        A class exhibits **Inappropriate Intimacy** if:
        - It knows too much about the internal details (e.g., private attributes or implementation specifics) of another class.
        - It directly accesses or modifies private attributes of another class.
        - It relies heavily on specific methods or implementation details of another class, instead of leveraging proper abstractions or interfaces.
        - It tightly couples its logic to another class, leading to a lack of modularity and making future changes difficult.

        Characteristics of Inappropriate Intimacy:
        - Directly accessing or modifying private variables of another class.
        - Dependency on specific methods or structures of another class that should ideally be encapsulated.
        - Excessive collaboration or reliance between two classes that go beyond typical interactions.

        Follow these response rules exactly:
        - If no Inappropriate Intimacy code smells are found, respond with 'None' only.
        - If any are found, respond only in this format, no extra commentary:

        File:{file_name}.py
        Detected:{class_name}
        Issue:{brief description of why it exhibits inappropriate intimacy (e.g., accesses private attributes, tightly coupled)}

        If multiple classes in the same file exhibit Inappropriate Intimacy, list each under the same File heading with their Detected and Issue lines.

        Do not mention correlation IDs or processed data lines.
        Do not provide additional commentary beyond what is requested.
    """

    # Include relevant reference documents if available
    if relevant_docs:
        content += (
            "\nThe following documents are provided for additional context on Inappropriate Intimacy code smells:\n"
        )
        for documents in relevant_docs:
            for index, (key, doc) in enumerate(documents.items(), start=1):
                content += f"Reference {index}:\n{{\n{doc}\n}}\n"

    # Return the prompt and processed data
    return {
        "role": "user",
        "content": content.strip()
    }, processed_data
