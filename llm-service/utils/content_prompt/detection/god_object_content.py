from utils.content_prompt.detection.utils.process_data import process_data
from utils.content_prompt.detection.utils.retrieve_relevant_docs import retrieve_relevant_docs_for_



def create_god_object_prompt(task_data, knowledge_base_detection, nn_model):
    processed_data = process_data(task_data, "classes", "God Object")
    # for file_path, content in task_data.items():
    #     processed_data[file_path] = extract_classes_from_code(content)
        
    # relevant_docs = create_relevant_docs(processed_data, knowledge_base_detection, nn_model)
    relevant_docs = retrieve_relevant_docs_for_("God Object", processed_data, knowledge_base_detection, nn_model)
    
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
        Review all provided classes from each file and determine if they exhibit a large class (God Object) code smell.
        A large class or 'God Object' is one that:
        - Takes on multiple unrelated responsibilities (e.g., configuration, database, logging, UI input, data processing) all in a single class.
        - Is far from cohesive and handles more than one clear domain concern.
        In contrast, smaller utility classes that focus on a single task or domain-specific classes that are large but cohesive should not be considered large classes. For example, a class like 'StringUtils' that just manipulates strings is cohesive and single-purpose, and should NOT be flagged as a large class code smell.
        If you find any classes that qualify as a large (God Object) class based on these criteria, respond with them in the following format:
        Your Answer Should only contain the following File Name and Detected Class in the exact format (including the braces):
        
        File:{file_name}.py
        Detected:{class_name}
        Issue:{brief description of why this class is considered large}
        
        If there are multiple classes in the same file that qualify, list them separately under the same file heading.
        
        If no classes qualify as large classes, respond with:
        None
    """

    additonal_content = content
    
    # Add relevant documents to the prompt if available
    if relevant_docs:
        content += (
            "\nThe following documents are provided as references. These documents contain examples of "
            "God Object Code Smells. Use them as references when analyzing the above files and their classes:\n"
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

