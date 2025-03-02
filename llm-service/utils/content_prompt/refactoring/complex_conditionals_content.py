from utils.content_prompt.detection.utils.retrieve_relevant_docs import retrieve_relevant_refactoring_docs_for_

def create_overly_complex_conditionals_content(task_data, knowledge_base_refactoring, nn_model):
    """
    Creates the content prompt for refactoring a Python codebase to address
    the 'Overly Complex Conditionals' code smell. This function retrieves relevant
    documentation and crafts a user-facing message instructing them to refactor
    the code while preserving its logic and functionality, following best
    practices outlined in the system prompts.
    """
    code_snippet = task_data["code_snippet"]

    # Retrieve any relevant docs that could help guide the refactoring
    relevant_docs = retrieve_relevant_refactoring_docs_for_(
        "Overly Complex Conditionals",
        code_snippet,
        knowledge_base_refactoring,
        nn_model
    )

    # Construct the main content prompt
    content = f"""
You will now refactor the following Python code to eliminate the 'Overly Complex Conditionals' code smell while adhering to the system's guidelines. The logic and functionality must remain unchanged, but you should ensure the refactored code simplifies complex conditionals. Clearly document the changes you make.

Here is the Python code that requires refactoring:

```python
{code_snippet}
```
Refactor this code by reducing nested conditionals and improving readability, while preserving its logic. Ensure your output is contained within a single code block, is clear, and includes comments explaining your refactoring choices. 
"""

    if relevant_docs: 
        content += """
        ### Additional References:
        If applicable, use the following documents for guidance. These documents provide examples of "Overly Complex Conditionals" code smells and best practices for refactoring:
        """
        content += "\nThe following reference documents are available to assist in your refactoring:\n\n"
        for index, doc in enumerate(relevant_docs, start=1):
            for key, value in doc.items():
                content += f"Reference {index} - {key}:\n\n" + """```\n{value}\n```\n\n"""
    return {
        "role": "user",
        "content": content.strip()
    }