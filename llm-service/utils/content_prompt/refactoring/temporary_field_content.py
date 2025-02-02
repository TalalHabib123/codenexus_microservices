from utils.content_prompt.detection.utils.retrieve_relevant_docs import retrieve_relevant_refactoring_docs_for_

def create_temporary_field_content(task_data, knowledge_base_refactoring, nn_model):
    code_snippet = task_data["code_snippet"]
    
    # Retrieve any relevant documents for "Temporary Field" refactoring
    relevant_docs = retrieve_relevant_refactoring_docs_for_(
        "Temporary Field", code_snippet, knowledge_base_refactoring, nn_model
    )

    content = f"""
You will now refactor the following Python class to eliminate the "Temporary Field" code smell while adhering to the system's guidelines. The logic and functionality must remain unchanged, but you should ensure the refactored code is modular and follows Pythonic best practices. Clearly document the changes you make.

Here is the Python code snippet that requires refactoring:

```python
{code_snippet}
```
Refactor this class by removing or relocating any attributes that are only occasionally used or remain uninitialized for most of the class's lifecycle. If an attribute is only used within a single method, consider converting it to a local variable. Ensure your output is clean, readable, and properly commented to explain your design choices. """
    if relevant_docs:
        content += """
        ### Additional References:
        If applicable, use the following documents for guidance. These documents provide examples of "Temporary Field" code smells and best practices for refactoring: """
        content += "\nThe following reference documents are available to assist in your refactoring:\n\n" 
        for index, doc in enumerate(relevant_docs, start=1): 
            for key, value in doc.items(): 
                content += ( f"Reference {index} - {key}:\n\n" f"\n{value}\n\n\n" )
    
    return {
        "role": "user",
        "content": content.strip()
    }