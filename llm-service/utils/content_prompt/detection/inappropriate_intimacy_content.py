from utils.content_prompt.detection.utils.process_data import process_data
from utils.content_prompt.detection.utils.retrieve_relevant_docs import retrieve_relevant_docs_for_


def create_inappropriate_intimacy_prompt(task_data, knowledge_base_detection, nn_model):
    processed_data = process_data(task_data, "classes", "Inappropriate Intimacy")
    # for file_path, content in task_data.items():
    #     processed_data[file_path] = extract_classes_from_code(content)
        
    # relevant_docs = create_relevant_docs_for_inappropriate_intimacy(processed_data, knowledge_base_detection, nn_model)
    relevant_docs = retrieve_relevant_docs_for_("Inappropriate Intimacy", processed_data, knowledge_base_detection, nn_model)

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
        Review all provided classes from each file and determine if they exhibit an Inappropriate Intimacy code smell.
        A class is said to exhibit **Inappropriate Intimacy** when:
        - It knows too much about the internal details of another class, creating tight coupling.
        - It accesses or manipulates the private attributes or implementation details of another class directly.
        - It has methods that rely heavily on specific details of another class, indicating a lack of proper abstraction.

        Classes with Inappropriate Intimacy often result in poor modularity and make future changes difficult. Examples include:
        - A class directly modifying private attributes of another class.
        - A class being overly dependent on specific methods of another class, rather than using an interface or abstraction.

        If you find any classes that qualify as exhibiting inappropriate intimacy based on these criteria, respond with them in the following format:
        Your Answer Should only contain the following File Name and Detected Class in the exact format (including the braces):
        
        File:{file_name}.py
        Detected:{class_name}
        If there are multiple classes in the same file that qualify, list them separately under the same file heading.

        If no classes qualify as exhibiting inappropriate intimacy, respond with:
        None
    """

    # Add relevant documents to the prompt if available
    if relevant_docs:
        content += (
            "\nThe following documents are provided as references. These documents contain examples of "
            "Inappropriate Intimacy Code Smells. Use them as references when analyzing the above files and their classes:\n"
        )
        for documents in relevant_docs:
            for index, (key, doc) in enumerate(documents.items(), start=1):
                content += f"Reference {index}:\n{{\n{doc}\n}}\n"

    # Return the complete prompt as a dictionary
    return {
        "role": "user",
        "content": content.strip()
    }, processed_data
