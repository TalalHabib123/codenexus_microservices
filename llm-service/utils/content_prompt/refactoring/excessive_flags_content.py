from utils.content_prompt.detection.utils.retrieve_relevant_docs import retrieve_relevant_refactoring_docs_for_

def create_excessive_flags_content(task_data, knowledge_base_refactoring, nn_model):
    # Extract the code snippet to be refactored from the task data
    code_snippet = task_data.get("code_snippet", "")

    relevant_docs = retrieve_relevant_refactoring_docs_for_(
        "Excessive Flags",
        code_snippet,
        knowledge_base_refactoring,
        nn_model
    )

    # Construct the user prompt content
    content = f"""
You will now refactor the following Python function or method to eliminate the "Excessive Use of Flags" code smell while adhering to the system's guidelines. The logic and functionality must remain unchanged, but you should ensure the refactored code is more modular, avoids flag parameters, and follows Pythonic best practices. Clearly document the changes you make as described in the system prompt.

Here is the Python code that requires refactoring:

```python
{code_snippet}
```
Refactor this function/method by removing or reducing flag parameters and splitting out distinct behaviors into separate functions, while preserving the original logic. Ensure your output is clear, readable, and well-commented to explain your design choices. """.strip()

    # If we have references, append them to the content
    if relevant_docs:
        content += "\n\n### Additional References:\n"
        content += "If applicable, use the following documents for guidance on refactoring 'Excessive Flags':\n\n"
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