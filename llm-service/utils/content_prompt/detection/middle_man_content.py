from utils.helpers.class_extractor import extract_classes_from_code
from utils.rag.retrieval import retrieve_relevant_info_detection

def create_relevant_docs_for_middle_man(processed_data, knowledge_base_detection, nn_model):
    relevant_docs = []
    for file_path, classes in processed_data.items():
        for class_code in classes:
            relevant_docs.extend(retrieve_relevant_info_detection("Middle Man", class_code, knowledge_base_detection, nn_model))
    return relevant_docs

def create_middle_man_prompt(task_data, knowledge_base_detection, nn_model):
    processed_data = {}
    for file_path, content in task_data.items():
        processed_data[file_path] = extract_classes_from_code(content)
        
    relevant_docs = create_relevant_docs_for_middle_man(processed_data, knowledge_base_detection, nn_model)

    # Create the base content with the processed data
    content = (
        "I am providing you with files and classes structured as follows:\n\n"
    )
    
    # Add the files and their respective classes from the processed_data
    for file_path, classes in processed_data.items():
        for class_code in classes:
            content += f"File:{{{file_path}}}\nCode:{{\n{class_code}\n}}\n"

    # Append the instruction part of the prompt
    content += """
        Review all provided classes from each file and determine if they exhibit a Middle Man code smell.
        A class is said to exhibit the **Middle Man** code smell when:
        - It serves as an intermediary between other classes without adding meaningful functionality of its own.
        - Most of its methods are simple delegations to another class or set of classes.
        - It provides little to no additional logic, computation, or abstraction beyond forwarding calls.

        Characteristics of a Middle Man:
        - The class primarily exists to forward method calls or access methods in other classes.
        - It does not encapsulate meaningful behavior or responsibilities.

        If you find any classes that qualify as a Middle Man based on these criteria, respond with them in the following format:
        Your Answer Should only contain the following File Name and Detected Class in the exact format (including the braces):
        
        File:{file_name}.py
        Detected:{class_name}
        If there are multiple classes in the same file that qualify, list them separately under the same file heading.

        If no classes qualify as a Middle Man, respond with:
        None
    """

    # Add relevant documents to the prompt if available
    if relevant_docs:
        content += (
            "\nThe following documents are provided as references. These documents contain examples of "
            "Middle Man Code Smells. Use them as references when analyzing the above files and their classes:\n"
        )
        for documents in relevant_docs:
            for index, (key, doc) in enumerate(documents.items(), start=1):
                content += f"Reference {index}:\n{{\n{doc}\n}}\n"

    # Return the complete prompt as a dictionary
    return {
        "role": "user",
        "content": content.strip()
    }, processed_data
