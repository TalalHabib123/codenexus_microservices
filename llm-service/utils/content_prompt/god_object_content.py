from utils.helpers.class_extractor import extract_classes_from_code
from utils.rag.retrieval import retrieve_relevant_info_detection

def create_relevant_docs(processed_data, knowledge_base_detection, nn_model):
    relevant_docs = []
    for file_path, classes in processed_data.items():
        for class_code in classes:
            relevant_docs.extend(retrieve_relevant_info_detection("God Object", class_code, knowledge_base_detection, nn_model))
        
    return relevant_docs


def create_god_object_prompt(task_data, knowledge_base_detection, nn_model):
    processed_data = [{key: extract_classes_from_code(value)} for key, value in task_data.items()]
    relevant_docs = create_relevant_docs(processed_data, knowledge_base_detection, nn_model)
    # Create the base content with the processed data
    content = "I am providing you with files and classes structured as follows:\n\n"
    
    # Add the files and their respective classes from the processed_data
    for file_path, classes in processed_data.items():
        for class_code in classes:
            content += f"File:{{{file_path}}}\nCode:{{\n{class_code}\n}}\n"

    # Append the instruction part of the prompt
    content += """
        I want you to detect and respond back with only those files that contain a Large Class code smell.
        Each code block contains exactly one class, so multiple classes in a file are provided separately.
        Your response should be either 'None' or formatted like this including the {} brackets as well:
        Your Answer Should only contain the following File Name and Detected Class, all unnecessary content shouldn't be added.
        File:{file_name}.py
        Detected:{class_name}
        """

    # Add relevant documents to the prompt
    if relevant_docs:
        content += (
            "\nThe following documents are provided as references. These documents contain examples of "
            "God Object Code Smells. Use them as references when analyzing the above files and their classes:\n"
        )
        for index, doc in enumerate(relevant_docs, start=1):
            content += f"Reference {index}:\n{{\n{doc}\n}}\n"


    # Return the complete prompt as a dictionary
    return {
        "role": "user",
        "content": content.strip()
    }
