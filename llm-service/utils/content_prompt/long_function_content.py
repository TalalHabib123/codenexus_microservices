from utils.helpers.function_extractor import extract_functions_from_code
from utils.rag.retrieval import retrieve_relevant_info_detection

def create_relevant_docs_for_long_functions(processed_data, knowledge_base_detection, nn_model):
    relevant_docs = []
    for file_path, functions in processed_data.items():
        for function_code in functions:
            relevant_docs.extend(retrieve_relevant_info_detection("Long Function", function_code, knowledge_base_detection, nn_model))
    return relevant_docs

def create_long_function_prompt(task_data, knowledge_base_detection, nn_model):
    # Process the task data to extract functions
    processed_data = [{key: extract_functions_from_code(value)} for key, value in task_data.items()]
    relevant_docs = create_relevant_docs_for_long_functions(processed_data, knowledge_base_detection, nn_model)

    # Create the base content with the processed data
    content = "I am providing you with files and functions structured as follows:\n\n"

    # Add the files and their respective functions from the processed_data
    for file_path, functions in processed_data.items():
        for function_code in functions:
            content += f"File:{{{file_path}}}\nCode:{{\n{function_code}\n}}\n"

    # Append the instruction part of the prompt
    content += """
        I want you to detect and respond back with only those files that contain a Long Function code smell.
        Each code block contains exactly one function, so multiple functions in a file are provided separately.
        Your response should be either 'None' or formatted like this including the {} brackets as well:
        Your Answer Should only contain the following File Name and Detected Function, all unnecessary content shouldn't be added.
        File:{file_name}.py
        Detected:{function_name}
        """

    # Add relevant documents to the prompt
    if relevant_docs:
        content += (
            "\nThe following documents are provided as references. These documents contain examples of "
            "Long Function Code Smells. Use them as references when analyzing the above files and their functions:\n"
        )
        for index, (key, doc) in enumerate(relevant_docs.items(), start=1):
            if key != "smell":
                content += f"Reference {index}:\n{{\n{doc}\n}}\n"

    # Return the complete prompt as a dictionary
    return {
        "role": "user",
        "content": content.strip()
    }

