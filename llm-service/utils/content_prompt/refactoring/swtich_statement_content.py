from utils.content_prompt.detection.utils.retrieve_relevant_docs import retrieve_relevant_refactoring_docs_for_

def create_switch_statement_abuser_content(task_data, knowledge_base_refactoring, nn_model):
    # Extract the code snippet from the task data
    code_snippet = task_data.get("code_snippet", "")

    # Retrieve any relevant documentation for the "Switch Statement Abuser" code smell
    relevant_docs = retrieve_relevant_refactoring_docs_for_(
        "Switch Statement Abuser",
        code_snippet,
        knowledge_base_refactoring,
        nn_model
    )

    # Build the main content of the user prompt
    content = f"""
You will now refactor the following Python function or class to eliminate the "Switch Statement Abuser" code smell while adhering to the system's guidelines. The logic and functionality must remain unchanged, but you should ensure the refactored code employs polymorphism, strategy patterns, or dictionary-based dispatch where appropriate. Clearly document the changes you make as specified in the system prompt.

Here is the Python code that requires refactoring:

```python
{code_snippet}
```
Refactor this function or class by removing or reducing lengthy switch-like statements (such as if-elif-else or match-case) and replacing them with a more extensible and maintainable design. Your output should be clear, readable, and well-commented to explain your design choices. """.strip()

    if relevant_docs:
        content += "\n\n### Additional References:\n"
        content += "If applicable, use the following documents for guidance on refactoring 'Switch Statement Abuser':\n\n"
        for index, doc in enumerate(relevant_docs, start=1):
            for key, value in doc.items():
                content += (
                    f"Reference {index} - {key}:\n\n"
                    "```\n"
                    f"{value}\n"
                    "```\n\n"
                )

    return {
        "role": "user",
        "content": content
    }